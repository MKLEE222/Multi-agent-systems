"""Verify the saved report bytes and derive non-overlapping mechanism counts.

This reads only the explicitly named cache reports. It does not run a model,
read task evaluation data, or reinterpret development fixtures as natural tasks.
"""
import gzip
import hashlib
import json
from pathlib import Path


def main():
    repo = Path(__file__).resolve().parents[2]
    folder = repo / "results/oacr_cache_zo"
    manifest = json.loads((folder / "manifest.json").read_text())
    if hashlib.sha256((folder / "runtime-freeze.txt").read_bytes()).hexdigest() != manifest["runtime_freeze_sha256"]:
        raise ValueError("runtime package snapshot mismatch")
    reports = {}
    for record in manifest["reports"]:
        packed = (repo / record["path"]).read_bytes()
        raw = gzip.decompress(packed)
        if hashlib.sha256(packed).hexdigest() != record["gzip_sha256"]:
            raise ValueError(f"compressed report mismatch: {record['path']}")
        if hashlib.sha256(raw).hexdigest() != record["raw_sha256"]:
            raise ValueError(f"raw report mismatch: {record['path']}")
        report = json.loads(raw)
        if report["evaluation_units_loaded"] != 0:
            raise ValueError("report unexpectedly declares evaluation access")
        for identity_key, source_path in record["identity_files"].items():
            actual = hashlib.sha256((repo / source_path).read_bytes()).hexdigest()
            if actual != report["identity"][identity_key]:
                raise ValueError(f"run input mismatch: {source_path}")
        reports[record["name"]] = report
    tiny = reports["native_preflight_v1"]
    p = tiny["protocol"]
    last = p["model"]["num_hidden_layers"] - 1
    groups = {
        "inside_earlier": [r for r in tiny["rows"] if r["edit_layer"] < last and r["edit_position"] < p["prefix"]],
        "outside_earlier": [r for r in tiny["rows"] if r["edit_layer"] < last and r["edit_position"] >= p["prefix"]],
        "last_layer": [r for r in tiny["rows"] if r["edit_layer"] == last],
    }
    summary = {
        "authority": "development mechanism probes, not independent natural tasks",
        "tiny": {
            "rows": len(tiny["rows"]),
            "regions": {
                name: {
                    "rows": len(rows),
                    "fresh_nonzero_secants": sum(r["variants"]["fresh"]["secant"] != 0 for r in rows),
                    "cached_zero_secants": sum(r["variants"]["official_cache"]["secant"] == 0 for r in rows),
                    "max_exact_logit_error": max(r["exact_causal_reuse_max_logit_error"] for r in rows),
                } for name, rows in groups.items()
            },
            "center_fingerprints_equal": sum(r["variants"]["fresh"]["center_fingerprint"] == r["variants"]["official_cache"]["center_fingerprint"] for r in tiny["rows"]),
            "max_pair_order_error": max(v["pair_order_max_abs"] for r in tiny["rows"] for v in r["variants"].values()),
        },
        "pretrained": {
            "rows": len(reports["pretrained_probe_v1"]["rows"]),
            "max_exact_vs_unsplit_fresh_logit_error": max(r["variants"]["exact_causal_reuse"]["max_logit_error"] for r in reports["pretrained_probe_v1"]["rows"]),
        },
        "rounding_control": {
            "rows": len(reports["rounding_control_v1"]["rows"]),
            "max_split_fresh_vs_exact_logit_error": reports["rounding_control_v1"]["max_split_vs_exact_error"],
            "max_split_secant_vs_previous_exact_error": max(r["split_vs_prior_exact_secant_error"] for r in reports["rounding_control_v1"]["rows"]),
        },
        "evaluation_units_loaded": 0,
    }
    if summary != manifest["derived_summary"]:
        raise ValueError("derived summary does not match manifest")
    previous_hash = next(r["raw_sha256"] for r in manifest["reports"] if r["name"] == "pretrained_probe_v1")
    if reports["rounding_control_v1"]["identity"]["previous_report_sha256"] != previous_hash:
        raise ValueError("rounding control is not linked to the saved pretrained report")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
