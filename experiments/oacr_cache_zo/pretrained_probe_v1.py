"""Small pretrained language probes using the same pinned native cache code."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import time

import numpy as np
import torch
import transformers
from transformers import AutoTokenizer, Qwen2Config

from native_preflight_v1 import cache_state, clear_cache, digest, load_source, native_forward


def nll(logits, token):
    return -float(torch.log_softmax(logits[0, -1].double(), dim=-1)[token])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-file", required=True, type=Path)
    parser.add_argument("--model-dir", required=True, type=Path)
    parser.add_argument("--protocol", type=Path, default=Path(__file__).with_suffix(".json"))
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    p = json.loads(args.protocol.read_text())
    runtime = {"torch": torch.__version__, "transformers": transformers.__version__, "numpy": np.__version__}
    if runtime != p["runtime"]:
        raise ValueError("runtime mismatch")
    module, blob = load_source(args.source_file, p["source_blob"])
    files = {name: digest((args.model_dir / name).read_bytes()) for name in [
        "config.json", "model.safetensors", "tokenizer.json", "tokenizer_config.json", "vocab.json", "merges.txt"]}
    identity = {"source_blob": blob, "script_sha256": digest(Path(__file__).read_bytes()),
                "helper_sha256": digest(Path(__file__).with_name("native_preflight_v1.py").read_bytes()),
                "protocol_sha256": digest(args.protocol.read_bytes()), "model_file_sha256": files}
    print(json.dumps({"pre_execution_identity": identity}), flush=True)
    torch.set_num_threads(2)
    torch.use_deterministic_algorithms(True)
    config = Qwen2Config.from_pretrained(args.model_dir, local_files_only=True)
    config._attn_implementation = "eager"
    model = module.Qwen2ForCausalLM.from_pretrained(
        args.model_dir, config=config, torch_dtype=torch.float32, local_files_only=True,
        attn_implementation="eager").eval()
    tokenizer = AutoTokenizer.from_pretrained(args.model_dir, local_files_only=True)
    target = tokenizer.encode(p["target_string"], add_special_tokens=False)[0]
    rows = []
    start = time.monotonic()
    for prompt_index, prompt in enumerate(p["prompts"]):
        encoded = tokenizer(prompt, return_tensors="pt", return_offsets_mapping=True, add_special_tokens=False)
        ids = encoded["input_ids"]
        offsets = encoded["offset_mapping"][0].tolist()
        beginning = prompt.index(p["subject"])
        ending = beginning + len(p["subject"])
        position = max(index for index, (lo, hi) in enumerate(offsets)
                       if lo < ending and hi > beginning)
        if ids.shape[1] <= p["prefix"]:
            raise ValueError("fixture must include a suffix outside cached prefix")
        for layer in p["edit_layers"]:
            for seed in p["direction_seeds"]:
                generator = torch.Generator().manual_seed(seed)
                direction = torch.randn(config.hidden_size, generator=generator)
                direction /= direction.norm()
                variants, reference = {}, None
                for variant in p["variants"]:
                    clear_cache(model)
                    boundary = 0 if variant == "fresh" else p["prefix"]
                    exact = variant == "exact_causal_reuse"
                    zero = torch.zeros_like(direction)
                    center = native_forward(model, ids, zero, layer, position, boundary, exact)
                    anchor = cache_state(model)
                    minus = native_forward(model, ids, -p["epsilon"] * direction,
                                           layer, position, boundary, exact)
                    plus = native_forward(model, ids, p["epsilon"] * direction,
                                          layer, position, boundary, exact)
                    losses = {"center": nll(center, target), "minus": nll(minus, target),
                              "plus": nll(plus, target)}
                    variants[variant] = {
                        "losses": losses, "secant": (losses["plus"] - losses["minus"]) / (2*p["epsilon"]),
                        "cache_bytes": anchor["bytes"], "cache_unchanged": anchor == cache_state(model),
                        "suffix_response_max_abs": float((plus[:, -1]-minus[:, -1]).abs().max())}
                    if variant == "fresh":
                        reference = {"center": center, "minus": minus, "plus": plus}
                    else:
                        variants[variant]["center_max_logit_error"] = float((center-reference["center"]).abs().max())
                        variants[variant]["max_logit_error"] = max(float(
                            (value-reference[key]).abs().max())
                            for key,value in [("center",center),("minus",minus),("plus",plus)])
                row = {"prompt_index": prompt_index, "token_ids": ids[0].tolist(),
                       "subject_position": position, "sequence_length": ids.shape[1],
                       "edit_layer": layer, "direction_seed": seed, "variants": variants}
                rows.append(row)
                print(json.dumps({"completed_probe": len(rows), "prompt": prompt_index,
                                  "layer": layer, "subject_position": position,
                                  "fresh_secant": variants["fresh"]["secant"],
                                  "cached_secant": variants["official_cache"]["secant"],
                                  "exact_max_error": variants["exact_causal_reuse"]["max_logit_error"]}), flush=True)
                # Checkpoint complete records, retaining a visible incomplete
                # status until every declared probe has finished.
                args.out.parent.mkdir(parents=True, exist_ok=True)
                args.out.write_text(json.dumps({
                    "status": "RUNNING", "protocol": p, "identity": identity,
                    "runtime": runtime, "rows": rows}, indent=2) + "\n")
    report = {"status": "COMPLETE", "protocol": p, "identity": identity, "runtime": runtime,
              "target_token_id": target, "rows": rows, "wall_seconds": time.monotonic()-start,
              "evaluation_units_loaded": 0}
    args.out.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"status": "COMPLETE", "probes": len(rows), "wall_seconds": report["wall_seconds"]}), flush=True)


if __name__ == "__main__":
    main()
