"""Independent verifier for OACR-WACT-R v1 artifacts."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "oacr_r4"))

from run_paginated_relational_redesign_v2 import (  # noqa: E402
    parse_edges,
    prepare_graph,
    closure_edges,
    closure_hash,
    evenly_spaced,
)

PROTOCOL = "OACR_WACT_R_WRITE_ACTIVATION_FLIP_V1"


def sha_obj(x):
    return hashlib.sha256(
        json.dumps(x, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def gini(values):
    xs = sorted(float(x) for x in values)
    n = len(xs)
    if n == 0 or sum(xs) == 0:
        return 0.0
    weighted = sum((i + 1) * x for i, x in enumerate(xs))
    return (2.0 * weighted) / (n * sum(xs)) - (n + 1.0) / n


def close(a, b, tol=1e-12):
    if a is None or b is None:
        return a is None and b is None
    return abs(float(a) - float(b)) <= tol


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--combined_json", required=True)
    ap.add_argument("--result_json", required=True)
    args = ap.parse_args()

    x = json.loads(Path(args.result_json).read_text())
    if x.get("protocol") != PROTOCOL:
        raise RuntimeError(f"unexpected protocol: {x.get('protocol')}")

    raw = Path(args.combined_json).read_bytes()
    if hashlib.sha256(raw).hexdigest() != x["retrieval"]["combined_json_sha256"]:
        raise RuntimeError("combined JSON hash mismatch")

    if x["status"] != "INCLUDED":
        if x["status"] not in {"PAGINATION_TRUNCATED", "STRUCTURAL_EXCLUSION"}:
            raise RuntimeError(f"unknown non-included status: {x['status']}")
        print(json.dumps({
            "protocol": PROTOCOL,
            "root": x["root"],
            "status": f"PASS_{x['status']}",
        }, indent=2))
        return

    edges, _ = parse_edges(raw)
    g, cyclic, labels = prepare_graph(edges, x["root"]["qid"])
    base_edges = set(g.edges())
    base_closure = closure_edges(g)
    candidates_all = sorted(base_closure - base_edges, key=lambda z: (str(z[0]), str(z[1])))
    candidates = candidates_all if len(candidates_all) <= 271 else evenly_spaced(candidates_all, 271)

    if len(candidates) != x["summary"]["candidates"]:
        raise RuntimeError("candidate count mismatch")

    ranked = []
    for f in sorted(base_edges, key=lambda z: (str(z[0]), str(z[1]))):
        h = g.copy()
        h.remove_edge(*f)
        post = closure_edges(h)
        impact = len(base_closure ^ post)
        ranked.append((impact, str(f[0]), str(f[1]), f, post))
    ranked.sort(key=lambda z: (z[0], z[1], z[2]))
    selected_indices = evenly_spaced(list(range(len(ranked))), 64)
    selected = [ranked[i] for i in selected_indices]

    action_manifest = []
    action_by_id = {}
    base_after = {}
    for i, (impact, _, _, f, post) in enumerate(selected):
        u, v = f
        aid = f"del:{labels[u]}>{labels[v]}"
        action_manifest.append({
            "action_index": i,
            "action_id": aid,
            "edge": [labels[u], labels[v]],
            "base_deletion_impact": impact,
        })
        action_by_id[aid] = f
        base_after[aid] = post

    if action_manifest != x["action_manifest"]:
        raise RuntimeError("action manifest mismatch")
    if sha_obj(action_manifest) != x["manifest_hashes"]["action_manifest_sha256"]:
        raise RuntimeError("action manifest hash mismatch")

    candidate_ids = {e: f"add:{labels[e[0]]}>{labels[e[1]]}" for e in candidates}
    activation = {}
    k_rows = []
    g_load = {a["action_id"]: 0 for a in action_manifest}
    for e in candidates:
        cid = candidate_ids[e]
        row = {}
        for a in action_manifest:
            aid = a["action_id"]
            active = e not in base_after[aid]
            row[aid] = bool(active)
            g_load[aid] += int(active)
        activation[cid] = row
        k_rows.append((sum(row.values()), cid, e))

    if activation != x["activation_matrix"]:
        raise RuntimeError("activation matrix mismatch")
    if sha_obj(activation) != x["manifest_hashes"]["activation_matrix_sha256"]:
        raise RuntimeError("activation matrix hash mismatch")

    eligible = [(k, cid, e) for k, cid, e in k_rows if 0 < k < 64]
    eligible.sort(key=lambda z: (z[0], z[1]))
    witnesses = eligible if len(eligible) <= 16 else evenly_spaced(eligible, 16)

    if len(witnesses) != len(x["witnesses"]):
        raise RuntimeError("witness count mismatch")

    failures = []
    manifest = []
    for i, ((k, cid, e), stored) in enumerate(zip(witnesses, x["witnesses"])):
        if stored["witness_index"] != i or stored["state_pair"] != ["base", cid]:
            raise RuntimeError(f"witness identity mismatch at {i}")
        row = activation[cid]
        minus_a = next(a for a in action_manifest if not row[a["action_id"]])
        plus_a = next(a for a in action_manifest if row[a["action_id"]])

        if stored["inert_action"] != minus_a:
            raise RuntimeError(f"inert action mismatch at witness {i}")
        if stored["activating_action"] != plus_a:
            raise RuntimeError(f"activating action mismatch at witness {i}")

        aug = g.copy()
        aug.add_edge(*e)

        hm = aug.copy()
        hm.remove_edge(*action_by_id[minus_a["action_id"]])
        aug_minus = closure_edges(hm)
        hp = aug.copy()
        hp.remove_edge(*action_by_id[plus_a["action_id"]])
        aug_plus = closure_edges(hp)

        base_minus = base_after[minus_a["action_id"]]
        base_plus = base_after[plus_a["action_id"]]

        inert_equal = aug_minus == base_minus
        active_distinct = aug_plus != base_plus

        if not inert_equal or not active_distinct:
            failures.append({
                "witness_index": i,
                "inert_equal": inert_equal,
                "active_distinct": active_distinct,
            })

        if stored["inert_native"]["operationally_equal"] != inert_equal:
            raise RuntimeError(f"stored inert equality mismatch {i}")
        if stored["active_native"]["operationally_distinct"] != active_distinct:
            raise RuntimeError(f"stored active distinction mismatch {i}")
        if stored["inert_native"]["base_post_closure_sha256"] != closure_hash(base_minus):
            raise RuntimeError(f"base inert hash mismatch {i}")
        if stored["inert_native"]["aug_post_closure_sha256"] != closure_hash(aug_minus):
            raise RuntimeError(f"aug inert hash mismatch {i}")
        if stored["active_native"]["base_post_closure_sha256"] != closure_hash(base_plus):
            raise RuntimeError(f"base active hash mismatch {i}")
        if stored["active_native"]["aug_post_closure_sha256"] != closure_hash(aug_plus):
            raise RuntimeError(f"aug active hash mismatch {i}")

        rf = stored["representation_flip"]
        for key in [
            "inert_contract_U_bits",
            "inert_contract_E_bits",
            "activated_contract_U_bits",
            "activated_contract_E_bits",
        ]:
            if not close(rf[key], 0.0):
                raise RuntimeError(f"nonzero exact representation gap {key} at {i}")

        manifest.append({
            "state_pair": ["base", cid],
            "inert_action": minus_a["action_id"],
            "activating_action": plus_a["action_id"],
        })

    if sha_obj(manifest) != x["manifest_hashes"]["witness_manifest_sha256"]:
        raise RuntimeError("witness manifest hash mismatch")

    loads = [g_load[a["action_id"]] for a in action_manifest]
    total = sum(loads)
    desc = sorted(loads, reverse=True)
    n10 = max(1, math.ceil(0.10 * len(desc)))
    n25 = max(1, math.ceil(0.25 * len(desc)))
    s = x["activation_spectrum"]
    if s["activation_events"] != total:
        raise RuntimeError("activation event total mismatch")
    if s["zero_load_write_count"] != sum(v == 0 for v in loads):
        raise RuntimeError("zero-load write count mismatch")
    if s["max_write_activation_load"] != max(loads):
        raise RuntimeError("max write activation load mismatch")
    if not close(s["gini_write_activation_load"], gini(loads)):
        raise RuntimeError("gini mismatch")
    expected10 = sum(desc[:n10]) / total if total else 0.0
    expected25 = sum(desc[:n25]) / total if total else 0.0
    if not close(s["top_10pct_activation_event_share"], expected10):
        raise RuntimeError("top10 share mismatch")
    if not close(s["top_25pct_activation_event_share"], expected25):
        raise RuntimeError("top25 share mismatch")

    summary = x["summary"]
    if summary["eligible_distinctions"] != len(eligible):
        raise RuntimeError("eligible count mismatch")
    if summary["prospective_witnesses"] != len(witnesses):
        raise RuntimeError("prospective witness count mismatch")
    if summary["inert_prediction_failures"] != 0 or summary["activation_prediction_failures"] != 0:
        raise RuntimeError("producer recorded causal prediction failures")
    if summary["exact_representation_flips"] != len(witnesses):
        raise RuntimeError("representation flip count mismatch")
    if failures:
        raise RuntimeError(f"independent native causal replay failures: {failures}")

    print(json.dumps({
        "protocol": PROTOCOL,
        "root": x["root"],
        "status": "PASS",
        "candidates": len(candidates),
        "eligible_distinctions": len(eligible),
        "witnesses": len(witnesses),
        "native_causal_failures": len(failures),
        "activation_events": total,
        "gini_write_activation_load": gini(loads),
        "top_10pct_activation_event_share": expected10,
        "top_25pct_activation_event_share": expected25,
    }, indent=2))


if __name__ == "__main__":
    main()
