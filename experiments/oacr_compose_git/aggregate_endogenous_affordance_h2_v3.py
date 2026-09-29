"""Aggregate developmental OACR-COMPOSE-G v3 H2 shards."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

PROTOCOL = "OACR_COMPOSE_G_V3_ENDOGENOUS_AFFORDANCE_DEVELOPMENT_H2"
PROTOCOL_COMMIT = "93dfec441e1cf7927aa22771988c284d68b2ff26"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input_dir", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    files = sorted(Path(args.input_dir).glob("**/h2_shard_*.json"))
    if len(files) != 8:
        raise RuntimeError(f"expected 8 H2 shards, found {len(files)}")

    payloads = [json.loads(p.read_text()) for p in files]
    failures = []
    targets = payloads[0]["ambient_targets"]
    seen_pairs = set()
    results = []
    for p in payloads:
        if p.get("protocol") != PROTOCOL:
            failures.append("protocol_mismatch")
        if p.get("protocol_commit") != PROTOCOL_COMMIT:
            failures.append("protocol_commit_mismatch")
        if p.get("ambient_targets") != targets:
            failures.append("ambient_target_manifest_mismatch")
        if p.get("claim_status") != "DEVELOPMENTAL_ONLY":
            failures.append("claim_status_mismatch")
        for row in p["results"]:
            idx = row["pair_index"]
            if idx in seen_pairs:
                failures.append(f"duplicate_pair_index:{idx}")
            seen_pairs.add(idx)
            results.append(row)

    results.sort(key=lambda r: r["pair_index"])
    t1_rows = [x for r in results for x in r["t1_results"]]
    positives = [x for x in t1_rows if x["status"] == "H2_SEPARATED"]
    qualification_positives = [x for x in positives if x.get("qualification_set_diverges")]
    outcome_only_positives = [
        x for x in positives
        if not x.get("qualification_set_diverges")
        and x.get("outcome_divergence_targets")
    ]
    positive_pairs = [r for r in results if r["has_H2_separation"]]

    summary = {
        "eligible_H1_pairs_processed": len(results),
        "t1_attempts": len(t1_rows),
        "H2_interfaces_scanned": sum(bool(x.get("H2_interface_scanned")) for x in t1_rows),
        "H2_separated_t1": len(positives),
        "pairs_with_H2_separation": len(positive_pairs),
        "qualification_divergence_t1": len(qualification_positives),
        "outcome_only_divergence_t1": len(outcome_only_positives),
        "integrity_failure_count": len(failures),
    }
    out = {
        "protocol": "OACR_COMPOSE_G_V3_ENDOGENOUS_AFFORDANCE_DEVELOPMENT_H2_AGGREGATE",
        "protocol_commit": PROTOCOL_COMMIT,
        "claim_status": "DEVELOPMENTAL_ONLY",
        "summary": summary,
        "positive_pair_indices": [r["pair_index"] for r in positive_pairs],
        "positive_pairs": positive_pairs,
        "failures": failures,
        "pass": not failures,
    }
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(out, indent=2))
    print(json.dumps(summary, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
