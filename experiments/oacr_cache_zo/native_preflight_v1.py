"""Execute the pinned official MobiEdit cache branch on declared tiny fixtures.

No benchmark or evaluation manifest is read. This is a causal dependency
preflight, not reproduction of the paper's trained-model or mobile results.
Source code is loaded unmodified under its matching Transformers package.
"""
from __future__ import annotations

import argparse
import contextlib
import copy
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import platform
import sys
import time

import numpy as np
import torch
import transformers
from transformers import Qwen2Config


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_source(path: Path, expected: str):
    data = path.read_bytes()
    blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
    if blob != expected:
        raise ValueError(f"official source blob mismatch: {blob}")
    # Relative imports resolve against Transformers 4.44.2, not a reimplemented
    # attention. The imported file keeps all its original code and defaults.
    name = "transformers.models.qwen2.oacr_mobiedit_pinned"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module, blob


def cache_state(model):
    hashes, shapes, total = [], [], 0
    for layer in model.model.layers:
        records = getattr(layer.self_attn, "cached_prefixes", {})
        entry = []
        for key, tensors in sorted(records.items()):
            hs = []
            for tensor in tensors:
                arr = tensor.detach().cpu().contiguous().numpy()
                hs.append(digest(arr.tobytes()))
                total += tensor.numel() * tensor.element_size()
            entry.append({"key": key, "shapes": [list(t.shape) for t in tensors], "hashes": hs})
        shapes.append(entry)
        hashes.append(digest(json.dumps(entry, sort_keys=True).encode()))
    return {"layer_hashes": hashes, "records": shapes, "bytes": total}


def clear_cache(model):
    for layer in model.model.layers:
        if hasattr(layer.self_attn, "cached_prefixes"):
            layer.self_attn.cached_prefixes.clear()


def native_forward(model, ids, delta, layer_index, position, prefix, causal=False):
    handles = []
    def inject(_module, _args, output):
        modified = output.clone()
        modified[:, position, :] += delta
        return modified
    handles.append(model.model.layers[layer_index].mlp.register_forward_hook(inject))
    if causal:
        for index, layer in enumerate(model.model.layers):
            boundary = prefix if index <= layer_index else min(prefix, position)
            def adjust(_module, args, kwargs, boundary=boundary):
                kwargs["prefix"] = boundary
                return args, kwargs
            handles.append(layer.self_attn.register_forward_pre_hook(adjust, with_kwargs=True))
    try:
        with torch.no_grad(), contextlib.redirect_stdout(io.StringIO()):
            output = model(input_ids=ids, attention_mask=torch.ones_like(ids),
                           use_cache=False, prefix=prefix).logits.detach().clone()
        return output
    finally:
        for handle in handles:
            handle.remove()


def loss(logits):
    # Stable scalar arithmetic while leaving the original model's float logits
    # cast intact. Fixed labels measure dependence, not task correctness.
    labels = torch.tensor([7, 11])
    return float(torch.nn.functional.cross_entropy(logits[:, -1, :].double(), labels))


def run_variant(base, ids, direction, layer, position, p, epsilon, variant):
    model = copy.deepcopy(base)
    clear_cache(model)
    prefix = 0 if variant == "fresh" else p
    causal = variant == "exact_causal_reuse"
    zero = torch.zeros_like(direction)
    center = native_forward(model, ids, zero, layer, position, prefix, causal)
    anchor = cache_state(model)
    minus = native_forward(model, ids, -epsilon * direction, layer, position, prefix, causal)
    after_minus = cache_state(model)
    plus = native_forward(model, ids, epsilon * direction, layer, position, prefix, causal)
    after_plus = cache_state(model)
    values = {"center": loss(center), "minus": loss(minus), "plus": loss(plus)}
    result = {
        "losses": values,
        "secant": (values["plus"] - values["minus"]) / (2 * epsilon),
        "cache_bytes": anchor["bytes"],
        "cache_unchanged_after_pair": anchor == after_minus == after_plus,
        "cache_shapes": [[e["shapes"] for e in layer_entries] for layer_entries in anchor["records"]],
        "center_fingerprint": digest(center.numpy().tobytes()),
        "suffix_perturbation_max_abs": float((plus[:, -1] - minus[:, -1]).abs().max()),
    }
    # Reverse pair from the exact same anchor, on a separate model instance.
    reverse = copy.deepcopy(base)
    clear_cache(reverse)
    native_forward(reverse, ids, zero, layer, position, prefix, causal)
    plus_reverse = native_forward(reverse, ids, epsilon * direction, layer, position, prefix, causal)
    minus_reverse = native_forward(reverse, ids, -epsilon * direction, layer, position, prefix, causal)
    result["pair_order_max_abs"] = max(float((plus - plus_reverse).abs().max()),
                                     float((minus - minus_reverse).abs().max()))
    result["reverse_secant"] = (loss(plus_reverse) - loss(minus_reverse)) / (2 * epsilon)
    return result, {"center": center, "minus": minus, "plus": plus}


def interface_check(module, config_args, ids, operation):
    torch.manual_seed(1729)
    config = Qwen2Config(**config_args)
    config._attn_implementation = "sdpa" if operation == "sdpa" else "eager"
    model = module.Qwen2ForCausalLM(config).eval()
    try:
        with torch.no_grad(), contextlib.redirect_stdout(io.StringIO()):
            if operation == "prefix_zero_then_ten":
                model(input_ids=ids, use_cache=False, prefix=0)
                state = cache_state(model)
                model(input_ids=ids, use_cache=False, prefix=10)
            elif operation == "update_prefix":
                model(input_ids=ids, use_cache=False, update_prefix=True)
            else:
                model(input_ids=ids, use_cache=False, prefix=10)
        return {"status": "COMPLETED"}
    except Exception as error:
        result = {"status": "INTERFACE_ERROR", "type": type(error).__name__, "message": str(error)}
        if operation == "prefix_zero_then_ten":
            result["after_prefix_zero"] = state
        return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-file", required=True, type=Path)
    parser.add_argument("--protocol", type=Path, default=Path(__file__).with_suffix(".json"))
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    p = json.loads(args.protocol.read_text())
    actual_runtime = {"torch": torch.__version__, "transformers": transformers.__version__, "numpy": np.__version__}
    if actual_runtime != p["runtime"]:
        raise ValueError(f"runtime differs from declared fixture runtime: {actual_runtime}")
    module, blob = load_source(args.source_file, p["source_blob"])
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)
    generator = torch.Generator().manual_seed(p["input_seed"])
    ids = torch.randint(1, p["model"]["vocab_size"], (p["batch_size"], p["sequence_length"]), generator=generator)
    identity = {"protocol_sha256": digest(args.protocol.read_bytes()),
                "script_sha256": digest(Path(__file__).read_bytes()), "source_blob": blob}
    print(json.dumps({"pre_execution_identity": identity}), flush=True)
    rows, t0 = [], time.monotonic()
    for seed in p["model_seeds"]:
        torch.manual_seed(seed)
        config = Qwen2Config(**p["model"])
        config._attn_implementation = "eager"
        base = module.Qwen2ForCausalLM(config).eval()
        for layer in p["edit_layers"]:
            for position in p["edit_positions"]:
                for direction_seed in p["direction_seeds"]:
                    gen = torch.Generator().manual_seed(direction_seed)
                    direction = torch.randn(p["model"]["hidden_size"], generator=gen)
                    direction /= direction.norm()
                    variants, outputs = {}, {}
                    for variant in p["variants"]:
                        variants[variant], outputs[variant] = run_variant(
                            base, ids, direction, layer, position, p["prefix"], p["epsilon"], variant)
                    row = {"model_seed": seed, "edit_layer": layer, "edit_position": position,
                           "direction_seed": direction_seed, "variants": variants}
                    for variant in ["official_cache", "exact_causal_reuse"]:
                        row[variant + "_max_logit_error"] = max(float(
                            (outputs[variant][side] - outputs["fresh"][side]).abs().max())
                            for side in ["center", "minus", "plus"])
                        row[variant + "_secant_error"] = abs(variants[variant]["secant"] - variants["fresh"]["secant"])
                    rows.append(row)
    summary = {}
    for region in ["inside_earlier", "outside", "last_layer"]:
        selected = [r for r in rows if (
            (region == "inside_earlier" and r["edit_position"] < p["prefix"] and r["edit_layer"] < 2)
            or (region == "outside" and r["edit_position"] >= p["prefix"])
            or (region == "last_layer" and r["edit_layer"] == 2))]
        summary[region] = {
            "fixtures": len(selected),
            "official_max_logit_error": max(r["official_cache_max_logit_error"] for r in selected),
            "exact_max_logit_error": max(r["exact_causal_reuse_max_logit_error"] for r in selected),
            "official_zero_secants": sum(r["variants"]["official_cache"]["secant"] == 0 for r in selected),
            "fresh_nonzero_secants": sum(r["variants"]["fresh"]["secant"] != 0 for r in selected),
            "max_secant_error": max(r["official_cache_secant_error"] for r in selected),
        }
    report = {
        "protocol": p, "identity": identity, "runtime": actual_runtime,
        "python": platform.python_version(), "input_token_ids": ids.tolist(),
        "authority": p["authority"], "evaluation_units_loaded": 0,
        "summary": summary, "rows": rows,
        "interfaces": {k: interface_check(module, p["model"], ids, k)
                       for k in ["prefix_zero_then_ten", "update_prefix", "sdpa"]},
        "total_wall_seconds": time.monotonic() - t0,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({"summary": summary, "interfaces": report["interfaces"],
                      "wall_seconds": report["total_wall_seconds"]}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
