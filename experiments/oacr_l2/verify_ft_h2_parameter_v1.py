"""Structural/recomputation verifier for OACR-L2 parameter-state H2 artifacts."""
from __future__ import annotations

import argparse
import json
import math
import sys
from itertools import combinations
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "common"))

from operational_partition import (
    directional_information_gap,
    partition_from_signatures,
    refinement_relation,
)

PROTOCOL = "OACR_L2_PARAMETER_FT_H2_V1"
TOL = 1e-10
ALLOWED_NONCOMPLETE = {
    "SEED_CONSTRUCTION_FAILURE",
    "UNDERPOWERED_ANCHOR_CANDIDATES",
    "UNDERPOWERED_FUTURE_ACTIONS",
    "UNDERPOWERED_STATE_CONSTRUCTION",
}


def native_meta(x):
    return (
        x["status"],
        bool(x["target_realized"]),
        bool(x["fixed_all_satisfied"]),
    )


def logit_equal(a, b, atol, rtol):
    if len(a) != len(b):
        return False
    for x, y in zip(a, b):
        if x["pred"] != y["pred"] or x["target"] != y["target"]:
            return False
        if not np.allclose(
            np.asarray(x["logits"], dtype=float),
            np.asarray(y["logits"], dtype=float),
            atol=atol,
            rtol=rtol,
        ):
            return False
    return True


def task_pair(a, b, action_ids):
    h0 = a["root_reads"]["task"] == b["root_reads"]["task"]
    h1 = h0 and all(
        native_meta(a["tree"]["h1"][aid]) == native_meta(b["tree"]["h1"][aid])
        and a["tree"]["h1"][aid]["post_reads"]["task"]
        == b["tree"]["h1"][aid]["post_reads"]["task"]
        for aid in action_ids
    )
    h2 = h1 and all(
        native_meta(a["tree"]["h2"][f"{aid}>{bid}"])
        == native_meta(b["tree"]["h2"][f"{aid}>{bid}"])
        and a["tree"]["h2"][f"{aid}>{bid}"]["post_reads"]["task"]
        == b["tree"]["h2"][f"{aid}>{bid}"]["post_reads"]["task"]
        for aid in action_ids
        for bid in action_ids
    )
    return h0, h1, h2


def logit_pair(a, b, action_ids, atol, rtol):
    h0 = logit_equal(
        a["root_reads"]["logit"], b["root_reads"]["logit"], atol, rtol
    )
    h1 = h0 and all(
        native_meta(a["tree"]["h1"][aid]) == native_meta(b["tree"]["h1"][aid])
        and logit_equal(
            a["tree"]["h1"][aid]["post_reads"]["logit"],
            b["tree"]["h1"][aid]["post_reads"]["logit"],
            atol,
            rtol,
        )
        for aid in action_ids
    )
    h2 = h1 and all(
        native_meta(a["tree"]["h2"][f"{aid}>{bid}"])
        == native_meta(b["tree"]["h2"][f"{aid}>{bid}"])
        and logit_equal(
            a["tree"]["h2"][f"{aid}>{bid}"]["post_reads"]["logit"],
            b["tree"]["h2"][f"{aid}>{bid}"]["post_reads"]["logit"],
            atol,
            rtol,
        )
        for aid in action_ids
        for bid in action_ids
    )
    return h0, h1, h2


def canonical_json(x):
    return json.dumps(x, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def op_signature(s, action_ids):
    return {
        "h0": s["root_reads"]["task"],
        "h1": {
            aid: {
                "meta": native_meta(s["tree"]["h1"][aid]),
                "reads": s["tree"]["h1"][aid]["post_reads"]["task"],
            }
            for aid in action_ids
        },
        "h2": {
            f"{aid}>{bid}": {
                "meta": native_meta(s["tree"]["h2"][f"{aid}>{bid}"]),
                "reads": s["tree"]["h2"][f"{aid}>{bid}"]["post_reads"]["task"],
            }
            for aid in action_ids
            for bid in action_ids
        },
    }


def close(a, b):
    return abs(float(a) - float(b)) <= TOL


def verify_metric(stored, info, pair):
    numeric = [
        "representation_entropy_bits",
        "operational_entropy_bits",
        "joint_entropy_bits",
        "mutual_information_bits",
        "omission_U_bits",
        "excess_E_bits",
        "variation_of_information_bits",
    ]
    for k in numeric:
        if not close(stored[k], info[k]):
            raise RuntimeError(f"metric mismatch {k}: {stored[k]} vs {info[k]}")
    for k in ["adequate_almost_surely", "partition_match_almost_surely"]:
        if bool(stored[k]) != bool(info[k]):
            raise RuntimeError(f"boolean metric mismatch {k}")
    if stored["under_refinement_count"] != pair["under_refinement_count"]:
        raise RuntimeError("under-refinement count mismatch")
    if stored["over_refinement_count"] != pair["over_refinement_count"]:
        raise RuntimeError("over-refinement count mismatch")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--artifact", required=True)
    args = ap.parse_args()

    x = json.loads(Path(args.artifact).read_text())
    if x.get("protocol") != PROTOCOL:
        raise RuntimeError(f"unexpected protocol {x.get('protocol')}")

    status = x.get("status")
    if status != "COMPLETE":
        if status not in ALLOWED_NONCOMPLETE:
            raise RuntimeError(f"unknown non-complete status {status}")
        if x.get("future_outcomes_executed") is not False:
            raise RuntimeError("non-complete artifact must not execute future outcomes")
        print(json.dumps({
            "protocol": PROTOCOL,
            "seed": x.get("seed"),
            "status": f"PASS_{status}",
        }, indent=2))
        return

    if x["editor"]["name"] != "official_finetune":
        raise RuntimeError("wrong editor")
    if x["editor"]["target_parameter"] != "bert.encoder.layer.10.output.dense.weight":
        raise RuntimeError("wrong target parameter")
    if not close(x["editor"]["edit_lr"], 1e-2) or int(x["editor"]["n_iter"]) != 100:
        raise RuntimeError("wrong FT budget")
    if x["non_target_parameter_hash_before"] != x["non_target_parameter_hash_after"]:
        raise RuntimeError("non-target parameter hash changed")

    anchors = [int(i) for i in x["anchor_ids"]]
    futures = [int(i) for i in x["future_ids"]]
    if len(anchors) != 24 or len(set(anchors)) != 24:
        raise RuntimeError("anchor IDs not exactly 24 unique")
    if len(futures) != 3 or len(set(futures)) != 3:
        raise RuntimeError("future IDs not exactly 3 unique")
    if set(anchors) & set(futures):
        raise RuntimeError("anchor/future overlap")

    panel = x["panel_manifest"]
    counts = {
        k: sum(1 for r in panel if r["kind"] == k)
        for k in ["seed", "future", "sentinel"]
    }
    if counts != {"seed": 4, "future": 3, "sentinel": 24}:
        raise RuntimeError(f"panel counts mismatch: {counts}")

    states = x["states"]
    if not (2 <= len(states) <= 6):
        raise RuntimeError(f"invalid state count {len(states)}")
    ids = [s["state_id"] for s in states]
    if len(set(ids)) != len(ids) or "base" not in ids:
        raise RuntimeError("invalid state IDs")
    if len(set(s["parameter_hash"] for s in states)) != len(states):
        raise RuntimeError("retained states do not have unique parameter identities")

    action_ids = [str(i) for i in futures]
    h2_keys = {f"{a}>{b}" for a in action_ids for b in action_ids}
    for s in states:
        if set(s["tree"]["h1"]) != set(action_ids):
            raise RuntimeError(f"incomplete H1 for {s['state_id']}")
        if set(s["tree"]["h2"]) != h2_keys:
            raise RuntimeError(f"incomplete H2 for {s['state_id']}")

    stored_pairs = {
        tuple(sorted((p["state_a"], p["state_b"]))): p for p in x["pairs"]
    }
    expected_pair_keys = {
        tuple(sorted((a, b))) for a, b in combinations(ids, 2)
    }
    if set(stored_pairs) != expected_pair_keys:
        raise RuntimeError("pair set mismatch")

    atol = float(x["registered_read"]["atol"])
    rtol = float(x["registered_read"]["rtol"])

    h1_sep = 0
    h2_sep = 0
    logit_h0 = 0
    logit_h1 = 0
    logit_h2 = 0

    byid = {s["state_id"]: s for s in states}
    eq_task = {0: {}, 1: {}, 2: {}}
    for sid in ids:
        for h in range(3):
            eq_task[h][(sid, sid)] = True

    for a, b in combinations(ids, 2):
        p = stored_pairs[tuple(sorted((a, b)))]
        t = task_pair(byid[a], byid[b], action_ids)
        l = logit_pair(byid[a], byid[b], action_ids, atol, rtol)
        if [p["task_equivalent"][f"H{i}"] for i in range(3)] != list(t):
            raise RuntimeError(f"task pair mismatch {a},{b}")
        if [p["logit_equivalent"][f"H{i}"] for i in range(3)] != list(l):
            raise RuntimeError(f"logit pair mismatch {a},{b}")

        for h, v in enumerate(t):
            eq_task[h][(a, b)] = v
            eq_task[h][(b, a)] = v

        h1_sep += int(t[0] and not t[1])
        h2_sep += int(t[1] and not t[2])
        logit_h0 += int(l[0])
        logit_h1 += int(l[1])
        logit_h2 += int(l[2])

    # Exact task relation must be transitive.
    for h in range(3):
        for a in ids:
            for b in ids:
                for c in ids:
                    if (
                        eq_task[h].get((a, b), False)
                        and eq_task[h].get((b, c), False)
                        and not eq_task[h].get((a, c), False)
                    ):
                        raise RuntimeError(f"task transitivity failure H{h}: {a},{b},{c}")

    if any(x["task_transitivity"][f"H{h}"] for h in range(3)):
        raise RuntimeError("stored task transitivity violations non-empty")

    if not all(bool(v) for v in x["duplicate_replay"].values() if v is not None):
        raise RuntimeError("duplicate replay control failed")

    op = partition_from_signatures(
        ids, lambda sid: canonical_json(op_signature(byid[sid], action_ids))
    )
    reps = {
        "P0_task_read": partition_from_signatures(
            ids, lambda sid: canonical_json(byid[sid]["root_reads"]["task"])
        ),
        "Pfull_target_parameter_hash": partition_from_signatures(
            ids, lambda sid: byid[sid]["parameter_hash"]
        ),
        "Pdelta_norm": partition_from_signatures(
            ids, lambda sid: byid[sid]["delta_stats"]["l2_hex"]
        ),
    }
    for name, rep in reps.items():
        info = directional_information_gap(rep, op)
        pair = refinement_relation(rep, op)
        verify_metric(x["representation_audit_h2_task"][name], info, pair)

    s = x["summary"]
    if s["states"] != len(states):
        raise RuntimeError("summary state count mismatch")
    if s["h0_task_collision_pairs"] != len(stored_pairs):
        raise RuntimeError("summary pair count mismatch")
    if s["h1_task_separations_from_h0"] != h1_sep:
        raise RuntimeError("summary H1 separation mismatch")
    if s["h2_task_separations_from_h1"] != h2_sep:
        raise RuntimeError("summary H2 separation mismatch")
    if s["h2_task_operational_classes"] != len(op):
        raise RuntimeError("summary operational class mismatch")
    if s["logit_h0_equivalent_pairs"] != logit_h0:
        raise RuntimeError("logit H0 summary mismatch")
    if s["logit_h1_equivalent_pairs"] != logit_h1:
        raise RuntimeError("logit H1 summary mismatch")
    if s["logit_h2_equivalent_pairs"] != logit_h2:
        raise RuntimeError("logit H2 summary mismatch")

    print(json.dumps({
        "protocol": PROTOCOL,
        "seed": x["seed"],
        "status": "PASS",
        "states": len(states),
        "h0_task_collision_pairs": len(stored_pairs),
        "h1_task_separations": h1_sep,
        "h2_task_separations": h2_sep,
        "h2_operational_classes": len(op),
        "parameter_identity_blocks": len(reps["Pfull_target_parameter_hash"]),
        "parameter_identity_over_refinement_pairs":
            x["representation_audit_h2_task"]["Pfull_target_parameter_hash"]["over_refinement_count"],
    }, indent=2))


if __name__ == "__main__":
    main()
