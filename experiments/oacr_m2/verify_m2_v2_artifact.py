"""Independent verifier for OACR-M2 v2 artifacts.

Reads only the produced JSON artifact. It does not access the original carrier
or execute native operations. All partitions and directional gaps are rebuilt
from the frozen raw manifests/signatures/outcome matrix contained in the artifact.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "common"))

from operational_partition import (
    directional_information_gap,
    partition_from_signatures,
    refinement_relation,
)


TOL = 1e-10


def canonical_json(x):
    return json.dumps(x, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha_obj(x):
    return hashlib.sha256(canonical_json(x).encode("utf-8")).hexdigest()


def partition_assignment(partition, state_ids):
    canonical_blocks = sorted(
        [sorted(block, key=str) for block in partition],
        key=lambda block: [str(x) for x in block],
    )
    ci = {}
    for i, block in enumerate(canonical_blocks):
        for x in block:
            ci[x] = i
    return [ci[s] for s in state_ids]


def close(a, b):
    return abs(float(a) - float(b)) <= TOL


def verify_numeric_dict(stored, recomputed):
    keys = [
        "representation_entropy_bits",
        "operational_entropy_bits",
        "joint_entropy_bits",
        "mutual_information_bits",
        "omission_U_bits",
        "excess_E_bits",
        "variation_of_information_bits",
    ]
    for k in keys:
        if not close(stored[k], recomputed[k]):
            raise RuntimeError(f"metric mismatch {k}: {stored[k]} != {recomputed[k]}")
    for k in ["adequate_almost_surely", "partition_match_almost_surely"]:
        if bool(stored[k]) != bool(recomputed[k]):
            raise RuntimeError(f"boolean metric mismatch {k}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--artifact", required=True)
    args = ap.parse_args()

    x = json.loads(Path(args.artifact).read_text())
    protocol = x["protocol"]
    if protocol.startswith("OACR_M2_R_"):
        state_ids = [s["state_id"] for s in x["state_manifest"]]
        contracts = x["deterministic_permutation_ensemble"]["contracts"]
        rep0 = x["fixed_representation_signatures"]["R0_fixed_current_closure"]
        outcome_by_state = {
            s: {r["action_id"]: r for r in rows}
            for s, rows in x["state_action_outcomes"].items()
        }

        def op_signature(state, action_ids):
            return (
                rep0[state],
                tuple(
                    (
                        aid,
                        outcome_by_state[state][aid]["post_closure_sha256"],
                        outcome_by_state[state][aid]["post_closure_size"],
                    )
                    for aid in sorted(action_ids)
                ),
            )

    elif protocol.startswith("OACR_M2_G_"):
        state_ids = [s["commit"] for s in x["state_manifest"]]
        contracts = x["exact_contract_lattice"]["contracts"]
        rep0 = x["fixed_representation_signatures"]["R0_fixed_current_tree"]
        action_index = {a["action_id"]: a["action_index"] for a in x["action_manifest"]}

        def op_signature(state, action_ids):
            idxs = sorted(action_index[a] for a in action_ids)
            return (
                rep0[state],
                tuple(x["state_action_outcomes"][state][i]["signature"] for i in idxs),
            )
    else:
        raise RuntimeError(f"unsupported protocol: {protocol}")

    expected_hash_fields = {
        "state_manifest_sha256": x["state_manifest"],
        "action_manifest_sha256": x["action_manifest"],
        "representation_signatures_sha256": x["fixed_representation_signatures"],
        "outcome_matrix_sha256": x["state_action_outcomes"],
        "weights_sha256": x["weights"],
    }
    if "pair_manifest_sha256" in x["manifest_hashes"]:
        expected_hash_fields["pair_manifest_sha256"] = x["pair_manifest"]

    for key, value in expected_hash_fields.items():
        got = sha_obj(value)
        expected = x["manifest_hashes"][key]
        if got != expected:
            raise RuntimeError(f"manifest hash mismatch {key}: {got} != {expected}")

    rep_parts = {
        name: partition_from_signatures(state_ids, lambda s, sigs=sigs: sigs[s])
        for name, sigs in x["fixed_representation_signatures"].items()
    }

    verified = 0
    for row in contracts:
        action_ids = row["action_ids"]
        op = partition_from_signatures(
            state_ids,
            lambda s, action_ids=action_ids: op_signature(s, action_ids),
        )
        assignment = partition_assignment(op, state_ids)
        if assignment != row["operational_partition_assignment"]:
            raise RuntimeError(f"partition assignment mismatch in {row['contract_id']}")
        if len(op) != row["operational_blocks"]:
            raise RuntimeError(f"block-count mismatch in {row['contract_id']}")

        for name, rep in rep_parts.items():
            info = directional_information_gap(rep, op, weights=x["weights"])
            pair = refinement_relation(rep, op)
            stored = row["diagnostics"][name]
            verify_numeric_dict(stored, info)
            if pair["under_refinement_count"] != stored["under_refinement_count"]:
                raise RuntimeError(f"under-refinement mismatch {row['contract_id']} {name}")
            if pair["over_refinement_count"] != stored["over_refinement_count"]:
                raise RuntimeError(f"over-refinement mismatch {row['contract_id']} {name}")
        verified += 1

    result = {
        "artifact": str(args.artifact),
        "protocol": protocol,
        "verified_contracts": verified,
        "manifest_hashes_verified": sorted(expected_hash_fields),
        "status": "PASS",
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
