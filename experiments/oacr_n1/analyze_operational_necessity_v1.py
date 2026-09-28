"""OACR-N1 v1: retrospective operational-necessity audit.

Consumes the frozen first OACR-W1 and audit-complete OACR-R1 JSON artifacts.
It does not rerun either carrier and does not create new scientific outcomes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--w1", required=True)
    p.add_argument("--r1", required=True)
    p.add_argument("--out", required=True)
    return p.parse_args()


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def audit_w1(x: Dict[str, Any]) -> Dict[str, Any]:
    pairs = [p for p in x["pairs"] if p["pre_read_strict_match"]]
    required = [p for p in pairs if p["primary_congruence_violation"]]

    levels = {}
    for level in ("A1", "A2", "A3"):
        under = [
            p for p in pairs
            if p["abstraction_equal"][level] and p["primary_congruence_violation"]
        ]
        over = [
            p for p in pairs
            if (not p["abstraction_equal"][level])
            and (not p["primary_congruence_violation"])
        ]
        separated_required = [
            p for p in required if not p["abstraction_equal"][level]
        ]
        levels[level] = {
            "evaluated_current_read_collision_pairs": len(pairs),
            "required_operational_separations": len(required),
            "under_refinement": len(under),
            "over_refinement": len(over),
            "required_pairs_separated": len(separated_required),
            "required_pair_capture_rate": (
                len(separated_required) / len(required) if required else None
            ),
            "finite_bank_contract_sufficient": len(under) == 0,
            "over_refinement_evaluable": True,
        }

    first = Counter(
        p["first_separating_refinement"]
        for p in required
        if p["first_separating_refinement"] is not None
    )
    return {
        "carrier": "OACR-W1 official GRACE + SCOTUS/BERT",
        "current_observation_collision_pairs": len(pairs),
        "required_operational_pair_separations": len(required),
        "no_necessity_witness_in_registered_bank": len(required) == 0,
        "candidate_levels": levels,
        "first_separating_refinement_distribution": dict(first),
        "interpretation": (
            "No registered pair required separation after the eight frozen future writes. "
            "A2/A3 distinctions therefore over-refined the observed one-step behavioral "
            "partition in this finite bank; they were real internal differences but were not "
            "shown operationally necessary by this contract."
        ),
    }


def audit_r1(x: Dict[str, Any]) -> Dict[str, Any]:
    ws = [w for w in x["witnesses"] if w["pre_full_closure_equal"]]
    required = [w for w in ws if not w["post_full_closure_equal"]]

    level_key = {
        "A1": "A1_separates",
        "A2": "A2_separates",
        "A3": "A3_separates",
    }
    levels = {}
    for level, key in level_key.items():
        under = [w for w in required if not w[key]]
        separated = [w for w in required if w[key]]
        levels[level] = {
            "evaluated_current_read_collision_pairs": len(ws),
            "required_operational_separations": len(required),
            "under_refinement": len(under),
            "over_refinement": None,
            "required_pairs_separated": len(separated),
            "required_pair_capture_rate": (
                len(separated) / len(required) if required else None
            ),
            "finite_bank_contract_sufficient_on_required_pairs": len(under) == 0,
            "over_refinement_evaluable": False,
            "over_refinement_note": (
                "R1 v1 is a positive-control witness set and contains no matched non-violation "
                "pairs for testing whether this feature splits behaviorally equivalent states."
            ),
        }

    first = Counter(w["first_separating_refinement"] for w in required)
    return {
        "carrier": "OACR-R1 registered Wikidata-derived P279 graph",
        "current_observation_collision_pairs": len(ws),
        "required_operational_pair_separations": len(required),
        "candidate_levels": levels,
        "first_separating_refinement_distribution": dict(first),
        "interpretation": (
            "Every frozen witness required a one-step operational separation despite exact "
            "pre-write closure equality. A1/A2/A3 each separate all required pairs, but this "
            "does not establish any one of those feature encodings as uniquely necessary."
        ),
    }


def main():
    args = parse_args()
    w1p, r1p = Path(args.w1), Path(args.r1)
    w1, r1 = json.loads(w1p.read_text()), json.loads(r1p.read_text())

    expected_w1 = "60b3e4c4b3ca20134a242b21fc7b31cea46e88e076c3fa314b8f54fbedf2ab6b"
    expected_r1 = "e6aedbc7772e6b097c0ebc773dd628aea9285f146148bfad609f7aca776203af"
    actual_w1, actual_r1 = sha256(w1p), sha256(r1p)
    if actual_w1 != expected_w1:
        raise RuntimeError(f"W1 artifact hash mismatch: {actual_w1}")
    if actual_r1 != expected_r1:
        raise RuntimeError(f"R1 artifact hash mismatch: {actual_r1}")

    result = {
        "protocol": "OACR_N1_OPERATIONAL_NECESSITY_RETROSPECTIVE_V1",
        "status": "retrospective_cross_carrier_audit",
        "source_hashes": {
            "w1_result_sha256": actual_w1,
            "r1_result_sha256": actual_r1,
            "r1_raw_carrier_sha256": r1["raw_response_sha256"],
        },
        "w1": audit_w1(w1),
        "r1": audit_r1(r1),
        "cross_carrier_conclusion": {
            "supported": [
                "Internal state difference is not sufficient evidence of operational necessity.",
                "A registered operational necessity witness requires a current-observation collision plus future registered behavioral divergence.",
                "R1 supplies exact pairwise separation requirements under its registered graph contract.",
            ],
            "not_supported": [
                "No specific R1 feature encoding is shown universally or uniquely necessary.",
                "W1 does not show that routing state is unnecessary outside the frozen one-step action/read contract.",
                "The two carriers do not yet establish a universal cross-system adequacy hierarchy.",
            ],
        },
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2))
    print(json.dumps({
        "w1_required_separations": result["w1"]["required_operational_pair_separations"],
        "w1_A2_over_refinement": result["w1"]["candidate_levels"]["A2"]["over_refinement"],
        "r1_required_separations": result["r1"]["required_operational_pair_separations"],
        "r1_A1_capture_rate": result["r1"]["candidate_levels"]["A1"]["required_pair_capture_rate"],
    }, indent=2))


if __name__ == "__main__":
    main()
