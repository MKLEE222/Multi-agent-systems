"""Aggregate auditor for accepted OACR-R4 fresh relational redesign artifacts."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def load(path):
    x=json.loads(Path(path).read_text())
    if x.get("status") != "INCLUDED":
        raise RuntimeError(f"{path}: status={x.get('status')} not INCLUDED")
    if x.get("protocol") not in {
        "OACR_R4_PAGINATED_REDESIGN_V2",
        "OACR_R4_FRESH_RELATIONAL_REDESIGN_V1",
    }:
        raise RuntimeError(f"{path}: unexpected protocol {x.get('protocol')}")
    return x


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--result", action="append", required=True)
    ap.add_argument("--out", required=True)
    args=ap.parse_args()

    rows=[]
    for p in args.result:
        x=load(p)
        s=x["summary"]
        d=x["diagnostics"]
        sec=x["secondary_action_content"]
        row={
            "root_qid":x["root"]["qid"],
            "root_label":x["root"]["label"],
            "states":s["states"],
            "actions":s["registered_actions"],
            "operational_blocks":s["operational_blocks"],
            "conditional_demand_bits":s["conditional_demand_bits"],
            "active_augmented_states":s["active_augmented_states"],
            "inactive_augmented_states":s["inactive_augmented_states"],
            "active_fraction":s["active_fraction"],
            "delta_record_reduction_fraction":s["delta_record_reduction_fraction"],
            "native_replay_mismatches":s["native_replay_mismatches"],
            "Rgate_exact_partition_match":bool(s["Rgate_exact_partition_match"]),
            "R0_U_bits":d["R0_current_closure"]["omission_U_bits"],
            "R0_E_bits":d["R0_current_closure"]["excess_E_bits"],
            "Rfull_U_bits":d["Rfull_asserted_identity"]["omission_U_bits"],
            "Rfull_E_bits":d["Rfull_asserted_identity"]["excess_E_bits"],
            "Rgate_U_bits":d["Rgate_contract_gated_delta"]["omission_U_bits"],
            "Rgate_E_bits":d["Rgate_contract_gated_delta"]["excess_E_bits"],
            "singleton_no_refinement":sum(r["operational_blocks"]==1 for r in sec["singletons"]),
            "singleton_max_blocks":max(r["operational_blocks"] for r in sec["singletons"]),
            "pair_min_blocks":min(r["operational_blocks"] for r in sec["pairs"]),
            "pair_max_blocks":max(r["operational_blocks"] for r in sec["pairs"]),
            "pair_median_blocks":sorted(r["operational_blocks"] for r in sec["pairs"])[len(sec["pairs"])//2],
            "leave_one_out_indispensable":sum(
                not r["full_partition_preserved_by_omission"]
                for r in sec["leave_one_out"]
            ),
        }
        rows.append(row)

    accepted=len(rows)
    aggregate={
        "accepted_roots":accepted,
        "minimum_two_roots_gate":accepted >= 2,
        "all_native_replay_exact":all(r["native_replay_mismatches"]==0 for r in rows),
        "all_Rgate_U_zero":all(abs(float(r["Rgate_U_bits"])) < 1e-12 for r in rows),
        "all_Rgate_exact_match":all(r["Rgate_exact_partition_match"] for r in rows),
        "all_show_directional_mismatch":all(
            float(r["R0_U_bits"]) > 1e-12
            and abs(float(r["R0_E_bits"])) < 1e-12
            and abs(float(r["Rfull_U_bits"])) < 1e-12
            and float(r["Rfull_E_bits"]) > 1e-12
            for r in rows
        ),
        "all_singleton_action_content_anisotropic":all(
            r["singleton_no_refinement"] > 0 and r["singleton_max_blocks"] > 1
            for r in rows
        ),
        "roots":rows,
    }

    if accepted >= 2:
        aggregate["promotion_gate_passed"] = bool(
            aggregate["all_native_replay_exact"]
            and aggregate["all_Rgate_U_zero"]
        )
    else:
        aggregate["promotion_gate_passed"] = False

    out=Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(aggregate, indent=2))
    print(json.dumps(aggregate, indent=2))


if __name__=="__main__":
    main()
