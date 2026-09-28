"""Structural verifier for OACR-L1b learned horizon artifacts."""
from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path


def fail(msg: str):
    raise RuntimeError(msg)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--artifact", required=True)
    a=ap.parse_args()
    x=json.loads(Path(a.artifact).read_text())

    if x.get("protocol")!="OACR_L1B_COLLISION_DENSE_GRACE_H2_V1":
        fail("unexpected protocol")
    status=x.get("status")

    if status in {
        "SEED_CONSTRUCTION_FAILURE",
        "UNDERPOWERED_FUTURE_ACTIONS",
        "UNDERPOWERED_STATE_CONSTRUCTION",
    }:
        if x.get("summary",{}).get("future_outcomes_executed") is not False:
            fail("underpowered/failure artifact must state future_outcomes_executed=false")
        print(json.dumps({
            "status":"PASS_"+status,
            "seed":x.get("seed"),
            "scientific_status":status,
        },indent=2))
        return

    if status!="COMPLETE":
        fail(f"unknown status {status}")

    anchors=x["anchor_selection"]["selected_ids"]
    futures=x["future_selection"]["selected_ids"]
    if len(anchors)!=len(set(anchors)):
        fail("duplicate anchor candidate IDs")
    if len(futures)!=4 or len(futures)!=len(set(futures)):
        fail("future action IDs must be four unique IDs")
    if set(anchors)&set(futures):
        fail("anchor/future selection overlap")

    if len(x["anchor_attempts"])!=len(anchors):
        fail("anchor attempt ledger does not cover frozen anchor candidates")

    states=[s["state_id"] for s in x["states"]]
    if not (2<=len(states)<=8):
        fail("complete run must contain 2..8 states")
    if len(states)!=len(set(states)):
        fail("duplicate state IDs")

    pairs=x["pairs"]
    expected_pairs=len(states)*(len(states)-1)//2
    if len(pairs)!=expected_pairs:
        fail(f"pair count mismatch {len(pairs)} != {expected_pairs}")
    pair_keys={tuple(sorted((r["state_a"],r["state_b"]))) for r in pairs}
    if len(pair_keys)!=expected_pairs:
        fail("duplicate/missing pair identities")
    if not all(r["equiv_h0"] for r in pairs):
        fail("retained state bank is not an H0 collision clique")

    tree=x["behavior_tree"]
    if set(tree)!=set(states):
        fail("behavior tree state set mismatch")
    action_ids=[str(int(v)) for v in x["action_ids"]]
    if len(action_ids)!=4 or len(set(action_ids))!=4:
        fail("action manifest mismatch")
    expected_h2={f"{a}>{b}" for a in action_ids for b in action_ids}
    for sid in states:
        if set(tree[sid]["h1"])!=set(action_ids):
            fail(f"incomplete H1 tree for {sid}")
        if set(tree[sid]["h2"])!=expected_h2:
            fail(f"incomplete H2 tree for {sid}")

    summary=x["summary"]
    if summary["states"]!=len(states):
        fail("summary state count mismatch")
    if summary["actions"]!=4:
        fail("summary action count mismatch")
    if summary["h0_collision_pairs"]!=expected_pairs:
        fail("summary H0 pair count mismatch")
    if summary["branch_trajectories_per_state"]!=20:
        fail("branch trajectory count mismatch")
    if summary["total_branch_trajectories"]!=20*len(states):
        fail("total branch trajectory count mismatch")
    if summary["anchor_attempts"]!=len(anchors):
        fail("summary anchor attempts mismatch")
    if summary["anchor_retained"]!=len(states)-1:
        fail("summary retained-anchor count mismatch")

    for h in ("0","1","2"):
        hz=summary["horizon"][h]
        if not hz["transitivity"]["transitive"]:
            fail(f"horizon {h} relation is non-transitive")
    if summary["horizon"]["0"]["N_h"]!=1:
        fail("H0 partition must be one class")

    det=summary["determinism"]
    if det["base_h1"] is not True or det["nonbase_h1"] is not True or det["base_h2"] is not True:
        fail("determinism control failed")

    # Recompute first-separation counts from pair ledger.
    h1=sum(int(r["equiv_h0"] and not r["equiv_h1"]) for r in pairs)
    h2=sum(int(r["equiv_h1"] and not r["equiv_h2"]) for r in pairs)
    if h1!=summary["h1_separations_from_h0"]:
        fail("H1 separation summary mismatch")
    if h2!=summary["h2_separations_from_h1"]:
        fail("H2 separation summary mismatch")

    print(json.dumps({
        "status":"PASS",
        "seed":x["seed"],
        "states":len(states),
        "h0_collision_pairs":expected_pairs,
        "actions":4,
        "branch_trajectories":20*len(states),
        "h1_separations":h1,
        "h2_separations":h2,
    },indent=2))


if __name__=="__main__":
    main()
