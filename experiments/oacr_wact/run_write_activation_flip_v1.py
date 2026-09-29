"""OACR-WACT-R v1: prospective causal WRITE-activation flip experiment."""
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
sys.path.insert(0, str(HERE.parent / "common"))

from run_paginated_relational_redesign_v2 import (  # noqa: E402
    query_for,
    fetch_json,
    parse_edges,
    prepare_graph,
    closure_edges,
    closure_hash,
    evenly_spaced,
    qid,
)
from operational_partition import (  # noqa: E402
    directional_information_gap,
    partition_from_signatures,
)

PROTOCOL = "OACR_WACT_R_WRITE_ACTIVATION_FLIP_V1"
PROTOCOL_COMMIT = "6a616ae39ac065908d6a650869eb20f38ff335ff"


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


def pearson(xs, ys):
    if len(xs) != len(ys) or not xs:
        return None
    mx = statistics.mean(xs)
    my = statistics.mean(ys)
    dx = [x - mx for x in xs]
    dy = [y - my for y in ys]
    den = math.sqrt(sum(x*x for x in dx) * sum(y*y for y in dy))
    if den == 0:
        return None
    return sum(a*b for a, b in zip(dx, dy)) / den


def two_state_gap(op_equal: bool, rep_equal: bool):
    ids = ["base", "aug"]
    op = partition_from_signatures(ids, lambda s: "same" if op_equal else s)
    rep = partition_from_signatures(ids, lambda s: "same" if rep_equal else s)
    return directional_information_gap(rep, op)


def write_json(path, obj):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2))
    print(json.dumps({
        "protocol": obj.get("protocol"),
        "root": obj.get("root"),
        "status": obj.get("status"),
        "summary": obj.get("summary"),
    }, indent=2))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--raw_dir", required=True)
    ap.add_argument("--combined_json", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--page_size", type=int, default=2000)
    ap.add_argument("--max_pages", type=int, default=20)
    ap.add_argument("--timeout", type=int, default=120)
    ap.add_argument("--retries", type=int, default=4)
    args = ap.parse_args()

    raw_dir = Path(args.raw_dir)
    raw_dir.mkdir(parents=True, exist_ok=True)
    all_bindings = []
    ordered_pairs = []
    page_manifest = []
    page_hashes = set()
    complete = False
    completion_page = None

    for page_index in range(args.max_pages):
        offset = page_index * args.page_size
        raw = fetch_json(query_for(args.root, args.page_size, offset), args.timeout, args.retries)
        raw_sha = hashlib.sha256(raw).hexdigest()
        page_path = raw_dir / f"page_{page_index:02d}.json"
        page_path.write_bytes(raw)

        obj = json.loads(raw.decode("utf-8"))
        bindings = obj["results"]["bindings"]
        page_pairs = []
        for row in bindings:
            if "child" not in row or "parent" not in row:
                continue
            child = qid(row["child"]["value"])
            parent = qid(row["parent"]["value"])
            if child and parent and child != parent and child.startswith("Q") and parent.startswith("Q"):
                page_pairs.append((child, parent))

        if page_pairs != sorted(page_pairs):
            raise RuntimeError(f"page ordering violation at page {page_index}")
        if ordered_pairs and page_pairs and page_pairs[0] < ordered_pairs[-1]:
            raise RuntimeError(f"cross-page ordering inversion at page {page_index}")
        if raw_sha in page_hashes and bindings:
            raise RuntimeError(f"identical raw page repeated: {page_index}")
        page_hashes.add(raw_sha)

        page_manifest.append({
            "page_index": page_index,
            "offset": offset,
            "binding_count": len(bindings),
            "raw_sha256": raw_sha,
            "first_edge": list(page_pairs[0]) if page_pairs else None,
            "last_edge": list(page_pairs[-1]) if page_pairs else None,
            "file": page_path.name,
        })
        all_bindings.extend(bindings)
        ordered_pairs.extend(page_pairs)
        if len(bindings) < args.page_size:
            complete = True
            completion_page = page_index
            break

    combined_obj = {"head": {"vars": ["child", "parent"]}, "results": {"bindings": all_bindings}}
    combined_raw = json.dumps(
        combined_obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    cp = Path(args.combined_json)
    cp.parent.mkdir(parents=True, exist_ok=True)
    cp.write_bytes(combined_raw)

    edges, binding_count = parse_edges(combined_raw)
    edge_payload = "\n".join(f"{u}\t{v}" for u, v in edges).encode()
    result = {
        "protocol": PROTOCOL,
        "protocol_commit": PROTOCOL_COMMIT,
        "root": {"qid": args.root, "label": args.label},
        "retrieval": {
            "page_size": args.page_size,
            "max_pages": args.max_pages,
            "complete": complete,
            "completion_page": completion_page,
            "pages_retrieved": len(page_manifest),
            "concatenated_binding_count": binding_count,
            "deduplicated_edge_count": len(edges),
            "combined_json_sha256": hashlib.sha256(combined_raw).hexdigest(),
            "combined_edge_sha256": hashlib.sha256(edge_payload).hexdigest(),
            "page_manifest": page_manifest,
            "transactional_snapshot": False,
        },
    }

    if not complete:
        result["status"] = "PAGINATION_TRUNCATED"
        result["exclusion_reasons"] = ["pagination_truncated"]
        write_json(args.out, result)
        return

    g, cyclic, labels = prepare_graph(edges, args.root)
    if g.number_of_nodes() == 0:
        result["status"] = "STRUCTURAL_EXCLUSION"
        result["exclusion_reasons"] = ["empty_prepared_graph"]
        write_json(args.out, result)
        return

    base_edges = set(g.edges())
    base_closure = closure_edges(g)
    candidates_all = sorted(base_closure - base_edges, key=lambda x: (str(x[0]), str(x[1])))
    structural = {
        "raw_unique_edges": len(edges),
        "prepared_nodes": g.number_of_nodes(),
        "prepared_asserted_edges": g.number_of_edges(),
        "cyclic_scc_count": len(cyclic),
        "closure_size": len(base_closure),
        "redundant_candidate_count": len(candidates_all),
    }
    result["structural"] = structural

    exclusions = []
    if g.number_of_nodes() < 100:
        exclusions.append("prepared_nodes_lt_100")
    if g.number_of_edges() < 128:
        exclusions.append("prepared_edges_lt_128")
    if len(candidates_all) < 64:
        exclusions.append("redundant_candidates_lt_64")
    if g.number_of_edges() < 64:
        exclusions.append("asserted_edges_lt_64")
    if exclusions:
        result["status"] = "STRUCTURAL_EXCLUSION"
        result["exclusion_reasons"] = exclusions
        write_json(args.out, result)
        return

    candidates = candidates_all if len(candidates_all) <= 271 else evenly_spaced(candidates_all, 271)

    ranked = []
    base_after = {}
    for f in sorted(base_edges, key=lambda x: (str(x[0]), str(x[1]))):
        h = g.copy()
        h.remove_edge(*f)
        post = closure_edges(h)
        impact = len(base_closure ^ post)
        ranked.append((impact, str(f[0]), str(f[1]), f, post))
    ranked.sort(key=lambda x: (x[0], x[1], x[2]))
    selected_idx = evenly_spaced(list(range(len(ranked))), 64)
    selected = [ranked[i] for i in selected_idx]

    action_manifest = []
    action_by_id = {}
    impacts = {}
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
        impacts[aid] = impact
        base_after[aid] = post

    candidate_ids = {
        e: f"add:{labels[e[0]]}>{labels[e[1]]}" for e in candidates
    }

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
        k = sum(row.values())
        k_rows.append((k, cid, e))

    eligible = [(k, cid, e) for k, cid, e in k_rows if 0 < k < 64]
    eligible.sort(key=lambda z: (z[0], z[1]))
    witnesses = eligible if len(eligible) <= 16 else evenly_spaced(eligible, 16)

    witness_rows = []
    failures = []
    for wi, (k, cid, e) in enumerate(witnesses):
        row = activation[cid]
        minus_a = next(a for a in action_manifest if not row[a["action_id"]])
        plus_a = next(a for a in action_manifest if row[a["action_id"]])
        minus_id = minus_a["action_id"]
        plus_id = plus_a["action_id"]

        aug = g.copy()
        aug.add_edge(*e)

        hm = aug.copy()
        hm.remove_edge(*action_by_id[minus_id])
        aug_minus = closure_edges(hm)
        hp = aug.copy()
        hp.remove_edge(*action_by_id[plus_id])
        aug_plus = closure_edges(hp)

        base_minus = base_after[minus_id]
        base_plus = base_after[plus_id]

        inert_equal = aug_minus == base_minus
        active_distinct = aug_plus != base_plus

        minus_gap = two_state_gap(op_equal=inert_equal, rep_equal=True)
        plus_gap = two_state_gap(op_equal=not active_distinct, rep_equal=False)

        row_out = {
            "witness_index": wi,
            "state_pair": ["base", cid],
            "added_edge": [labels[e[0]], labels[e[1]]],
            "activation_degree": k,
            "inert_action": minus_a,
            "activating_action": plus_a,
            "inert_native": {
                "base_post_closure_sha256": closure_hash(base_minus),
                "aug_post_closure_sha256": closure_hash(aug_minus),
                "base_post_closure_size": len(base_minus),
                "aug_post_closure_size": len(aug_minus),
                "operationally_equal": inert_equal,
            },
            "active_native": {
                "base_post_closure_sha256": closure_hash(base_plus),
                "aug_post_closure_sha256": closure_hash(aug_plus),
                "base_post_closure_size": len(base_plus),
                "aug_post_closure_size": len(aug_plus),
                "operationally_distinct": active_distinct,
            },
            "representation_flip": {
                "under_inert_contract_representation_equal": True,
                "under_activated_contract_representation_distinct": True,
                "inert_contract_U_bits": minus_gap["omission_U_bits"],
                "inert_contract_E_bits": minus_gap["excess_E_bits"],
                "activated_contract_U_bits": plus_gap["omission_U_bits"],
                "activated_contract_E_bits": plus_gap["excess_E_bits"],
            },
        }
        if not inert_equal or not active_distinct:
            failures.append({
                "witness_index": wi,
                "candidate_id": cid,
                "inert_equal": inert_equal,
                "active_distinct": active_distinct,
            })
        witness_rows.append(row_out)

    loads = [g_load[a["action_id"]] for a in action_manifest]
    total_events = sum(loads)
    desc_loads = sorted(loads, reverse=True)
    n10 = max(1, math.ceil(0.10 * len(desc_loads)))
    n25 = max(1, math.ceil(0.25 * len(desc_loads)))

    activated_prefix = set()
    prefix = [{"k": 0, "active_distinctions": 0, "retention_fraction": 0.0}]
    by_cid_to_e = {candidate_ids[e]: e for e in candidates}
    for i, a in enumerate(action_manifest, start=1):
        aid = a["action_id"]
        for cid, row in activation.items():
            if row[aid]:
                activated_prefix.add(cid)
        prefix.append({
            "k": i,
            "action_id_added": aid,
            "active_distinctions": len(activated_prefix),
            "retention_fraction": len(activated_prefix) / len(candidates),
        })

    k_values = [k for k, _, _ in k_rows]
    spectrum = {
        "candidate_count": len(candidates),
        "action_count": 64,
        "activation_events": total_events,
        "distinction_activation_degree": {
            "min": min(k_values),
            "max": max(k_values),
            "median": statistics.median(k_values),
            "zero_count": sum(k == 0 for k in k_values),
            "full_count": sum(k == 64 for k in k_values),
        },
        "write_activation_load": [
            {
                "action_id": a["action_id"],
                "action_index": a["action_index"],
                "base_deletion_impact": a["base_deletion_impact"],
                "activated_distinctions": g_load[a["action_id"]],
            }
            for a in action_manifest
        ],
        "zero_load_write_count": sum(x == 0 for x in loads),
        "max_write_activation_load": max(loads),
        "gini_write_activation_load": gini(loads),
        "top_10pct_activation_event_share":
            (sum(desc_loads[:n10]) / total_events if total_events else 0.0),
        "top_25pct_activation_event_share":
            (sum(desc_loads[:n25]) / total_events if total_events else 0.0),
        "impact_activation_pearson": pearson(
            [float(a["base_deletion_impact"]) for a in action_manifest],
            [float(g_load[a["action_id"]]) for a in action_manifest],
        ),
        "prefix_retention_curve": prefix,
    }

    result.update({
        "status": "INCLUDED",
        "state_bank": {
            "registered_redundant_candidates": len(candidates),
            "candidate_selection": "all if <=271 else 271 evenly spaced lexical",
        },
        "action_manifest": action_manifest,
        "activation_matrix": activation,
        "eligible_distinctions": len(eligible),
        "witness_selection": {
            "eligible_rule": "0 < activation_degree < 64",
            "selected_count": len(witnesses),
            "selection": "all if <=16 else 16 evenly spaced after activation-degree+lexical sort",
        },
        "witnesses": witness_rows,
        "causal_prediction_failures": failures,
        "activation_spectrum": spectrum,
        "manifest_hashes": {
            "action_manifest_sha256": sha_obj(action_manifest),
            "activation_matrix_sha256": sha_obj(activation),
            "witness_manifest_sha256": sha_obj([
                {
                    "state_pair": w["state_pair"],
                    "inert_action": w["inert_action"]["action_id"],
                    "activating_action": w["activating_action"]["action_id"],
                }
                for w in witness_rows
            ]),
        },
        "summary": {
            "candidates": len(candidates),
            "actions": 64,
            "eligible_distinctions": len(eligible),
            "prospective_witnesses": len(witness_rows),
            "inert_prediction_failures": sum(
                not w["inert_native"]["operationally_equal"] for w in witness_rows
            ),
            "activation_prediction_failures": sum(
                not w["active_native"]["operationally_distinct"] for w in witness_rows
            ),
            "exact_representation_flips": sum(
                w["inert_native"]["operationally_equal"]
                and w["active_native"]["operationally_distinct"]
                and abs(w["representation_flip"]["inert_contract_U_bits"]) < 1e-12
                and abs(w["representation_flip"]["inert_contract_E_bits"]) < 1e-12
                and abs(w["representation_flip"]["activated_contract_U_bits"]) < 1e-12
                and abs(w["representation_flip"]["activated_contract_E_bits"]) < 1e-12
                for w in witness_rows
            ),
        },
    })
    write_json(args.out, result)


if __name__ == "__main__":
    main()
