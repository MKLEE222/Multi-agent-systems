"""Independent, page-level verifier for OACR-WACT-R v1 artifacts.

This verifier intentionally does not import producer-side graph helpers.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
import sys
from pathlib import Path
from typing import List, Tuple

import networkx as nx

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "common"))

from operational_partition import directional_information_gap, partition_from_signatures

PROTOCOL = "OACR_WACT_R_WRITE_ACTIVATION_FLIP_V1"
TOL = 1e-12


def qid(uri: str) -> str:
    return uri.rsplit("/", 1)[-1].strip()


def parse_edges(raw: bytes) -> Tuple[List[Tuple[str, str]], int]:
    obj = json.loads(raw.decode("utf-8"))
    bindings = obj["results"]["bindings"]
    edges = set()
    for row in bindings:
        if "child" not in row or "parent" not in row:
            continue
        child = qid(row["child"]["value"])
        parent = qid(row["parent"]["value"])
        if (
            child
            and parent
            and child != parent
            and child.startswith("Q")
            and parent.startswith("Q")
        ):
            edges.add((child, parent))
    return sorted(edges), len(bindings)


def prepare_graph(edges, root):
    g = nx.DiGraph()
    g.add_edges_from(edges)
    if not g.nodes:
        return g, [], {}
    if root in g:
        nodes = nx.node_connected_component(g.to_undirected(), root)
    else:
        nodes = max(nx.weakly_connected_components(g), key=len)
    g = g.subgraph(nodes).copy()
    sccs = list(nx.strongly_connected_components(g))
    cyclic = [sorted(c) for c in sccs if len(c) > 1]
    if cyclic:
        c = nx.condensation(g, sccs)
        members = {int(n): sorted(c.nodes[n]["members"]) for n in c.nodes}
        cg = nx.DiGraph((int(a), int(b)) for a, b in c.edges if a != b)
        labels = {
            int(n): (
                members[int(n)][0]
                if len(members[int(n)]) == 1
                else "SCC[" + ",".join(members[int(n)]) + "]"
            )
            for n in cg.nodes
        }
        return cg, cyclic, labels
    return g, [], {n: n for n in g.nodes}


def closure_edges(g):
    if not nx.is_directed_acyclic_graph(g):
        raise RuntimeError("prepared graph must be DAG")
    return set(nx.transitive_closure_dag(g).edges())


def closure_hash(edges):
    payload = "\n".join(
        f"{a}\t{b}"
        for a, b in sorted(edges, key=lambda x: (str(x[0]), str(x[1])))
    )
    return hashlib.sha256(payload.encode()).hexdigest()


def evenly_spaced(items, k):
    if k >= len(items):
        return list(items)
    idxs = []
    for i in range(k):
        idx = round(i * (len(items) - 1) / (k - 1))
        if idx not in idxs:
            idxs.append(idx)
    if len(idxs) != k:
        for i in range(len(items)):
            if i not in idxs:
                idxs.append(i)
            if len(idxs) == k:
                break
        idxs = sorted(idxs)
    return [items[i] for i in idxs]


def sha_obj(x):
    return hashlib.sha256(
        json.dumps(
            x, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode()
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
    den = math.sqrt(sum(x * x for x in dx) * sum(y * y for y in dy))
    if den == 0:
        return None
    return sum(a * b for a, b in zip(dx, dy)) / den


def close(a, b, tol=TOL):
    if a is None or b is None:
        return a is None and b is None
    return abs(float(a) - float(b)) <= tol


def two_state_gap(op_equal: bool, rep_equal: bool):
    ids = ["base", "aug"]
    op = partition_from_signatures(ids, lambda s: "same" if op_equal else s)
    rep = partition_from_signatures(ids, lambda s: "same" if rep_equal else s)
    return directional_information_gap(rep, op)


def verify_pages(raw_dir: Path, combined_raw: bytes, retrieval: dict):
    page_manifest = retrieval["page_manifest"]
    concatenated = []
    last_pair = None
    seen_hashes = set()

    for page in page_manifest:
        page_path = raw_dir / page["file"]
        raw = page_path.read_bytes()
        raw_sha = hashlib.sha256(raw).hexdigest()
        if raw_sha != page["raw_sha256"]:
            raise RuntimeError(f"page SHA mismatch {page['page_index']}")
        if raw_sha in seen_hashes and page["binding_count"] > 0:
            raise RuntimeError("repeated nonempty page hash")
        seen_hashes.add(raw_sha)

        obj = json.loads(raw.decode("utf-8"))
        bindings = obj["results"]["bindings"]
        if len(bindings) != page["binding_count"]:
            raise RuntimeError("page binding count mismatch")

        pairs = []
        for row in bindings:
            if "child" not in row or "parent" not in row:
                continue
            child = qid(row["child"]["value"])
            parent = qid(row["parent"]["value"])
            if (
                child
                and parent
                and child != parent
                and child.startswith("Q")
                and parent.startswith("Q")
            ):
                pairs.append((child, parent))

        if pairs != sorted(pairs):
            raise RuntimeError("page ordering violation")
        if last_pair is not None and pairs and pairs[0] < last_pair:
            raise RuntimeError("cross-page ordering inversion")
        if pairs:
            if page["first_edge"] != list(pairs[0]):
                raise RuntimeError("page first-edge manifest mismatch")
            if page["last_edge"] != list(pairs[-1]):
                raise RuntimeError("page last-edge manifest mismatch")
            last_pair = pairs[-1]
        else:
            if page["first_edge"] is not None or page["last_edge"] is not None:
                raise RuntimeError("empty-page boundary manifest mismatch")
        concatenated.extend(bindings)

    if retrieval["pages_retrieved"] != len(page_manifest):
        raise RuntimeError("pages_retrieved mismatch")

    combined_obj = {
        "head": {"vars": ["child", "parent"]},
        "results": {"bindings": concatenated},
    }
    expected = json.dumps(
        combined_obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    if combined_raw != expected:
        raise RuntimeError("combined JSON is not exact raw-page concatenation")
    if hashlib.sha256(combined_raw).hexdigest() != retrieval["combined_json_sha256"]:
        raise RuntimeError("combined JSON SHA mismatch")

    edges, binding_count = parse_edges(combined_raw)
    edge_payload = "\n".join(f"{u}\t{v}" for u, v in edges).encode("utf-8")
    if hashlib.sha256(edge_payload).hexdigest() != retrieval["combined_edge_sha256"]:
        raise RuntimeError("combined edge SHA mismatch")
    if binding_count != retrieval["concatenated_binding_count"]:
        raise RuntimeError("binding count mismatch")
    if len(edges) != retrieval["deduplicated_edge_count"]:
        raise RuntimeError("deduplicated edge count mismatch")
    return edges, binding_count


def structural_reasons(g, candidates_all):
    reasons = []
    if g.number_of_nodes() < 100:
        reasons.append("prepared_nodes_lt_100")
    if g.number_of_edges() < 128:
        reasons.append("prepared_edges_lt_128")
    if len(candidates_all) < 64:
        reasons.append("redundant_candidates_lt_64")
    if g.number_of_edges() < 64:
        reasons.append("asserted_edges_lt_64")
    return reasons


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw_dir", required=True)
    ap.add_argument("--combined_json", required=True)
    ap.add_argument("--result_json", required=True)
    args = ap.parse_args()

    x = json.loads(Path(args.result_json).read_text())
    if x.get("protocol") != PROTOCOL:
        raise RuntimeError(f"unexpected protocol: {x.get('protocol')}")

    combined_raw = Path(args.combined_json).read_bytes()
    edges, binding_count = verify_pages(
        Path(args.raw_dir), combined_raw, x["retrieval"]
    )
    retrieval = x["retrieval"]

    if x["status"] == "PAGINATION_TRUNCATED":
        if retrieval["complete"] is not False:
            raise RuntimeError("truncated result marked complete")
        if x.get("exclusion_reasons") != ["pagination_truncated"]:
            raise RuntimeError("truncation reason mismatch")
        print(json.dumps({
            "protocol": PROTOCOL,
            "root": x["root"],
            "status": "PASS_PAGINATION_TRUNCATED",
            "pages_verified": retrieval["pages_retrieved"],
        }, indent=2))
        return

    if retrieval["complete"] is not True:
        raise RuntimeError("non-truncated result lacks complete retrieval")

    g, cyclic, labels = prepare_graph(edges, x["root"]["qid"])
    if g.number_of_nodes() == 0:
        expected = ["empty_prepared_graph"]
        if x["status"] != "STRUCTURAL_EXCLUSION":
            raise RuntimeError("empty prepared graph not structurally excluded")
        if x.get("exclusion_reasons") != expected:
            raise RuntimeError("empty-graph exclusion reason mismatch")
        print(json.dumps({
            "protocol": PROTOCOL,
            "root": x["root"],
            "status": "PASS_STRUCTURAL_EXCLUSION",
            "exclusion_reasons": expected,
        }, indent=2))
        return

    base_edges = set(g.edges())
    base_closure = closure_edges(g)
    candidates_all = sorted(
        base_closure - base_edges, key=lambda z: (str(z[0]), str(z[1]))
    )

    structural = {
        "raw_unique_edges": len(edges),
        "prepared_nodes": g.number_of_nodes(),
        "prepared_asserted_edges": g.number_of_edges(),
        "cyclic_scc_count": len(cyclic),
        "closure_size": len(base_closure),
        "redundant_candidate_count": len(candidates_all),
    }
    if x.get("structural") != structural:
        raise RuntimeError("structural summary mismatch")

    exclusions = structural_reasons(g, candidates_all)
    if x["status"] == "STRUCTURAL_EXCLUSION":
        if x.get("exclusion_reasons") != exclusions:
            raise RuntimeError("structural exclusion reasons mismatch")
        if not exclusions:
            raise RuntimeError("structural exclusion without a failing gate")
        print(json.dumps({
            "protocol": PROTOCOL,
            "root": x["root"],
            "status": "PASS_STRUCTURAL_EXCLUSION",
            "binding_count": binding_count,
            "exclusion_reasons": exclusions,
        }, indent=2))
        return

    if x["status"] != "INCLUDED":
        raise RuntimeError(f"unexpected status: {x['status']}")
    if exclusions:
        raise RuntimeError(f"INCLUDED carrier violates gates: {exclusions}")

    candidates = (
        candidates_all
        if len(candidates_all) <= 271
        else evenly_spaced(candidates_all, 271)
    )
    if x["state_bank"]["registered_redundant_candidates"] != len(candidates):
        raise RuntimeError("registered candidate count mismatch")

    ranked = []
    base_after = {}
    for edge in sorted(base_edges, key=lambda z: (str(z[0]), str(z[1]))):
        h = g.copy()
        h.remove_edge(*edge)
        post = closure_edges(h)
        impact = len(base_closure ^ post)
        ranked.append((impact, str(edge[0]), str(edge[1]), edge, post))
    ranked.sort(key=lambda z: (z[0], z[1], z[2]))
    selected_idx = evenly_spaced(list(range(len(ranked))), 64)
    selected = [ranked[i] for i in selected_idx]

    action_manifest = []
    action_by_id = {}
    impacts = {}
    for i, (impact, _, _, edge, post) in enumerate(selected):
        u, v = edge
        aid = f"del:{labels[u]}>{labels[v]}"
        action_manifest.append({
            "action_index": i,
            "action_id": aid,
            "edge": [labels[u], labels[v]],
            "base_deletion_impact": impact,
        })
        action_by_id[aid] = edge
        impacts[aid] = impact
        base_after[aid] = post

    if x["action_manifest"] != action_manifest:
        raise RuntimeError("action manifest mismatch")
    if sha_obj(action_manifest) != x["manifest_hashes"]["action_manifest_sha256"]:
        raise RuntimeError("action manifest hash mismatch")

    candidate_ids = {
        edge: f"add:{labels[edge[0]]}>{labels[edge[1]]}"
        for edge in candidates
    }
    activation = {}
    k_rows = []
    g_load = {a["action_id"]: 0 for a in action_manifest}
    for edge in candidates:
        cid = candidate_ids[edge]
        row = {}
        for action in action_manifest:
            aid = action["action_id"]
            active = edge not in base_after[aid]
            row[aid] = bool(active)
            g_load[aid] += int(active)
        activation[cid] = row
        k_rows.append((sum(row.values()), cid, edge))

    if x["activation_matrix"] != activation:
        raise RuntimeError("activation matrix mismatch")
    if sha_obj(activation) != x["manifest_hashes"]["activation_matrix_sha256"]:
        raise RuntimeError("activation matrix hash mismatch")

    eligible = [z for z in k_rows if 0 < z[0] < 64]
    eligible.sort(key=lambda z: (z[0], z[1]))
    witnesses = (
        eligible if len(eligible) <= 16 else evenly_spaced(eligible, 16)
    )
    if x["eligible_distinctions"] != len(eligible):
        raise RuntimeError("eligible distinction count mismatch")
    if x["witness_selection"]["selected_count"] != len(witnesses):
        raise RuntimeError("witness selection count mismatch")
    if len(x["witnesses"]) != len(witnesses):
        raise RuntimeError("stored witness count mismatch")

    witness_manifest = []
    causal_failures = []
    exact_flips = 0

    for wi, ((degree, cid, edge), stored) in enumerate(
        zip(witnesses, x["witnesses"])
    ):
        if stored["witness_index"] != wi:
            raise RuntimeError(f"witness index mismatch {wi}")
        if stored["state_pair"] != ["base", cid]:
            raise RuntimeError(f"witness state pair mismatch {wi}")
        if stored["added_edge"] != [labels[edge[0]], labels[edge[1]]]:
            raise RuntimeError(f"witness added edge mismatch {wi}")
        if stored["activation_degree"] != degree:
            raise RuntimeError(f"witness activation degree mismatch {wi}")

        row = activation[cid]
        inert_action = next(
            a for a in action_manifest if not row[a["action_id"]]
        )
        active_action = next(
            a for a in action_manifest if row[a["action_id"]]
        )
        if stored["inert_action"] != inert_action:
            raise RuntimeError(f"inert action mismatch {wi}")
        if stored["activating_action"] != active_action:
            raise RuntimeError(f"activating action mismatch {wi}")

        aug = g.copy()
        aug.add_edge(*edge)

        hm = aug.copy()
        hm.remove_edge(*action_by_id[inert_action["action_id"]])
        aug_minus = closure_edges(hm)

        hp = aug.copy()
        hp.remove_edge(*action_by_id[active_action["action_id"]])
        aug_plus = closure_edges(hp)

        base_minus = base_after[inert_action["action_id"]]
        base_plus = base_after[active_action["action_id"]]

        inert_equal = aug_minus == base_minus
        active_distinct = aug_plus != base_plus

        expected_inert = {
            "base_post_closure_sha256": closure_hash(base_minus),
            "aug_post_closure_sha256": closure_hash(aug_minus),
            "base_post_closure_size": len(base_minus),
            "aug_post_closure_size": len(aug_minus),
            "operationally_equal": inert_equal,
        }
        expected_active = {
            "base_post_closure_sha256": closure_hash(base_plus),
            "aug_post_closure_sha256": closure_hash(aug_plus),
            "base_post_closure_size": len(base_plus),
            "aug_post_closure_size": len(aug_plus),
            "operationally_distinct": active_distinct,
        }
        if stored["inert_native"] != expected_inert:
            raise RuntimeError(f"inert native replay mismatch {wi}")
        if stored["active_native"] != expected_active:
            raise RuntimeError(f"active native replay mismatch {wi}")

        inert_gap = two_state_gap(op_equal=inert_equal, rep_equal=True)
        active_gap = two_state_gap(op_equal=not active_distinct, rep_equal=False)

        rf = stored["representation_flip"]
        if rf["under_inert_contract_representation_equal"] is not True:
            raise RuntimeError(f"inert representation bit mismatch {wi}")
        if rf["under_activated_contract_representation_distinct"] is not True:
            raise RuntimeError(f"active representation bit mismatch {wi}")
        expected_metrics = {
            "inert_contract_U_bits": inert_gap["omission_U_bits"],
            "inert_contract_E_bits": inert_gap["excess_E_bits"],
            "activated_contract_U_bits": active_gap["omission_U_bits"],
            "activated_contract_E_bits": active_gap["excess_E_bits"],
        }
        for key, value in expected_metrics.items():
            if not close(rf[key], value):
                raise RuntimeError(f"representation metric mismatch {wi} {key}")

        if not inert_equal or not active_distinct:
            causal_failures.append(wi)
        if (
            inert_equal
            and active_distinct
            and all(close(rf[k], 0.0) for k in expected_metrics)
        ):
            exact_flips += 1

        witness_manifest.append({
            "state_pair": ["base", cid],
            "inert_action": inert_action["action_id"],
            "activating_action": active_action["action_id"],
        })

    if sha_obj(witness_manifest) != x["manifest_hashes"]["witness_manifest_sha256"]:
        raise RuntimeError("witness manifest hash mismatch")

    if x.get("causal_prediction_failures") != []:
        raise RuntimeError("producer recorded causal prediction failures")
    if causal_failures:
        raise RuntimeError(f"independent causal failures: {causal_failures}")

    loads = [g_load[a["action_id"]] for a in action_manifest]
    total_events = sum(loads)
    desc = sorted(loads, reverse=True)
    n10 = max(1, math.ceil(0.10 * len(desc)))
    n25 = max(1, math.ceil(0.25 * len(desc)))
    k_values = [z[0] for z in k_rows]

    spectrum = x["activation_spectrum"]
    expected_degree = {
        "min": min(k_values),
        "max": max(k_values),
        "median": statistics.median(k_values),
        "zero_count": sum(k == 0 for k in k_values),
        "full_count": sum(k == 64 for k in k_values),
    }
    if spectrum["distinction_activation_degree"] != expected_degree:
        raise RuntimeError("distinction activation degree summary mismatch")

    expected_load_rows = [
        {
            "action_id": a["action_id"],
            "action_index": a["action_index"],
            "base_deletion_impact": a["base_deletion_impact"],
            "activated_distinctions": g_load[a["action_id"]],
        }
        for a in action_manifest
    ]
    if spectrum["write_activation_load"] != expected_load_rows:
        raise RuntimeError("write activation load rows mismatch")
    if spectrum["candidate_count"] != len(candidates):
        raise RuntimeError("spectrum candidate count mismatch")
    if spectrum["action_count"] != 64:
        raise RuntimeError("spectrum action count mismatch")
    if spectrum["activation_events"] != total_events:
        raise RuntimeError("activation event total mismatch")
    if spectrum["zero_load_write_count"] != sum(v == 0 for v in loads):
        raise RuntimeError("zero-load count mismatch")
    if spectrum["max_write_activation_load"] != max(loads):
        raise RuntimeError("max activation load mismatch")
    if not close(spectrum["gini_write_activation_load"], gini(loads)):
        raise RuntimeError("gini mismatch")

    share10 = sum(desc[:n10]) / total_events if total_events else 0.0
    share25 = sum(desc[:n25]) / total_events if total_events else 0.0
    if not close(spectrum["top_10pct_activation_event_share"], share10):
        raise RuntimeError("top-10 activation share mismatch")
    if not close(spectrum["top_25pct_activation_event_share"], share25):
        raise RuntimeError("top-25 activation share mismatch")

    impact_corr = pearson(
        [float(a["base_deletion_impact"]) for a in action_manifest],
        [float(g_load[a["action_id"]]) for a in action_manifest],
    )
    if not close(spectrum["impact_activation_pearson"], impact_corr):
        raise RuntimeError("impact/activation correlation mismatch")

    activated = set()
    expected_prefix = [{
        "k": 0,
        "active_distinctions": 0,
        "retention_fraction": 0.0,
    }]
    for i, action in enumerate(action_manifest, start=1):
        aid = action["action_id"]
        for cid, row in activation.items():
            if row[aid]:
                activated.add(cid)
        expected_prefix.append({
            "k": i,
            "action_id_added": aid,
            "active_distinctions": len(activated),
            "retention_fraction": len(activated) / len(candidates),
        })
    if spectrum["prefix_retention_curve"] != expected_prefix:
        raise RuntimeError("prefix retention curve mismatch")

    summary = x["summary"]
    expected_summary = {
        "candidates": len(candidates),
        "actions": 64,
        "eligible_distinctions": len(eligible),
        "prospective_witnesses": len(witnesses),
        "inert_prediction_failures": 0,
        "activation_prediction_failures": 0,
        "exact_representation_flips": exact_flips,
    }
    if summary != expected_summary:
        raise RuntimeError(
            f"summary mismatch: stored={summary} expected={expected_summary}"
        )

    print(json.dumps({
        "protocol": PROTOCOL,
        "root": x["root"],
        "status": "PASS_STRICT",
        "pages_verified": retrieval["pages_retrieved"],
        "candidates": len(candidates),
        "eligible_distinctions": len(eligible),
        "witnesses": len(witnesses),
        "native_causal_failures": 0,
        "exact_representation_flips": exact_flips,
        "activation_events": total_events,
        "gini_write_activation_load": gini(loads),
        "top_10pct_activation_event_share": share10,
        "top_25pct_activation_event_share": share25,
    }, indent=2))


if __name__ == "__main__":
    main()
