"""Aggregate OACR-COMPOSE-G v3 developmental H1 preflight shards."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

PROTOCOL = "OACR_COMPOSE_G_V3_ENDOGENOUS_AFFORDANCE_DEVELOPMENT_H1_PREFLIGHT"
PROTOCOL_COMMIT = "93dfec441e1cf7927aa22771988c284d68b2ff26"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input_dir", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    files = sorted(Path(args.input_dir).glob("**/shard_*.json"))
    if len(files) != 8:
        raise RuntimeError(f"expected 8 shard JSONs, found {len(files)}")

    payloads = [json.loads(p.read_text()) for p in files]
    failures = []
    reference_targets = payloads[0]["ambient_targets"]
    seen_indices = set()
    rows = []

    for payload in payloads:
        if payload.get("protocol") != PROTOCOL:
            failures.append("protocol_mismatch")
        if payload.get("protocol_commit") != PROTOCOL_COMMIT:
            failures.append("protocol_commit_mismatch")
        if payload.get("ambient_targets") != reference_targets:
            failures.append("ambient_target_manifest_mismatch")
        if payload["summary"].get("H2_outcomes_executed") != 0:
            failures.append("H2_outcome_claim_nonzero")
        for row in payload["pairs"]:
            idx = row["pair_index"]
            if idx in seen_indices:
                failures.append(f"duplicate_pair_index:{idx}")
            seen_indices.add(idx)
            rows.append(row)

    rows.sort(key=lambda r: r["pair_index"])
    if seen_indices != set(range(48)):
        failures.append("development_pair_coverage_mismatch")

    h1 = [r for r in rows if r["v3_H1_equivalent"]]
    h1_nonempty = [r for r in h1 if r["nonempty_common_action_set"]]

    summary = {
        "development_bank_total": len(rows),
        "ambient_targets": len(reference_targets),
        "pairs_qualified_set_equal": sum(r["qualified_set_equal"] for r in rows),
        "pairs_v3_H1_equivalent": len(h1),
        "pairs_v3_H1_equivalent_nonempty": len(h1_nonempty),
        "common_qualified_count_min_nonempty": (
            min(r["common_qualified_count"] for r in h1_nonempty)
            if h1_nonempty else 0
        ),
        "common_qualified_count_max": (
            max((r["common_qualified_count"] for r in h1), default=0)
        ),
        "H2_outcomes_executed": 0,
        "integrity_failure_count": len(failures),
    }

    out = {
        "protocol": "OACR_COMPOSE_G_V3_ENDOGENOUS_AFFORDANCE_DEVELOPMENT_H1_AGGREGATE",
        "protocol_commit": PROTOCOL_COMMIT,
        "ambient_targets": reference_targets,
        "summary": summary,
        "eligible_pair_indices": [r["pair_index"] for r in h1_nonempty],
        "eligible_pairs": [
            {
                "pair_index": r["pair_index"],
                "tree": r["tree"],
                "A": r["A"],
                "B": r["B"],
                "common_qualified_count": r["common_qualified_count"],
                "common_qualified_targets": r["A_qualified_targets"],
            }
            for r in h1_nonempty
        ],
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
