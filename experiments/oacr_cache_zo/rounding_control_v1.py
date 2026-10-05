"""Resolve the small numeric discrepancy with a fresh split-projection control.

Defined after the pretrained development probe exposed rounding differences.
This is a diagnostic on the same twelve probes, not independent confirmation.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch
from transformers import AutoTokenizer, Qwen2Config

from native_preflight_v1 import clear_cache, digest, load_source, native_forward
from pretrained_probe_v1 import nll


def split_fresh(model, ids, delta, layer_index, position, prefix):
    original = []
    try:
        for index, layer in enumerate(model.model.layers):
            boundary = prefix if index <= layer_index else min(prefix, position)
            for name in ["q_proj", "k_proj", "v_proj"]:
                projection = getattr(layer.self_attn, name)
                method = projection.forward
                original.append((projection, method))
                def forward(x, method=method, boundary=boundary):
                    return torch.cat([method(x[:, :boundary, :]),
                                      method(x[:, boundary:, :])], dim=1)
                projection.forward = forward
        # Prefix zero disables native cached-value replacement. The QKV
        # projections are recomputed on both pieces at every call.
        return native_forward(model, ids, delta, layer_index, position, 0)
    finally:
        for projection, method in original:
            projection.forward = method


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-file", required=True, type=Path)
    parser.add_argument("--model-dir", required=True, type=Path)
    parser.add_argument("--previous-report", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    previous = json.loads(args.previous_report.read_text())
    p = previous["protocol"]
    module, _ = load_source(args.source_file, p["source_blob"])
    identity = {"script_sha256": digest(Path(__file__).read_bytes()),
                "previous_report_sha256": digest(args.previous_report.read_bytes()),
                "protocol": "same pretrained probes; fresh split QKV control"}
    print(json.dumps({"pre_execution_identity": identity}), flush=True)
    torch.set_num_threads(2)
    torch.use_deterministic_algorithms(True)
    config = Qwen2Config.from_pretrained(args.model_dir, local_files_only=True)
    config._attn_implementation = "eager"
    model = module.Qwen2ForCausalLM.from_pretrained(
        args.model_dir, config=config, torch_dtype=torch.float32,
        local_files_only=True, attn_implementation="eager").eval()
    tokenizer = AutoTokenizer.from_pretrained(args.model_dir, local_files_only=True)
    target = tokenizer.encode(p["target_string"], add_special_tokens=False)[0]
    rows = []
    for prior in previous["rows"]:
        ids = torch.tensor([prior["token_ids"]])
        layer, position = prior["edit_layer"], prior["subject_position"]
        direction = torch.randn(config.hidden_size,
                                generator=torch.Generator().manual_seed(prior["direction_seed"]))
        direction /= direction.norm()
        outputs = {}
        for mode in ["fresh_split", "exact_causal_reuse"]:
            clear_cache(model)
            values = {}
            for side, delta in [("center", torch.zeros_like(direction)),
                                ("minus", -p["epsilon"]*direction),
                                ("plus", p["epsilon"]*direction)]:
                if mode == "fresh_split":
                    values[side] = split_fresh(model, ids, delta, layer, position, p["prefix"])
                else:
                    values[side] = native_forward(model, ids, delta, layer, position,
                                                 p["prefix"], causal=True)
            outputs[mode] = values
        row = {key: prior[key] for key in ["prompt_index", "edit_layer", "subject_position", "direction_seed"]}
        row["max_split_vs_exact_logit_error"] = max(float(
            (outputs["fresh_split"][side]-outputs["exact_causal_reuse"][side]).abs().max())
            for side in ["center", "minus", "plus"])
        values = outputs["fresh_split"]
        row["split_secant"] = (nll(values["plus"],target)-nll(values["minus"],target))/(2*p["epsilon"])
        row["prior_exact_secant"] = prior["variants"]["exact_causal_reuse"]["secant"]
        row["split_vs_prior_exact_secant_error"] = abs(row["split_secant"]-row["prior_exact_secant"])
        rows.append(row)
        print(json.dumps({"completed_control":len(rows), **row}), flush=True)
    report = {"identity":identity, "authority":"post-outcome numerical diagnosis, same probes",
              "rows":rows, "evaluation_units_loaded":0,
              "max_split_vs_exact_error":max(r["max_split_vs_exact_logit_error"] for r in rows)}
    args.out.write_text(json.dumps(report,indent=2)+"\n")


if __name__ == "__main__":
    main()
