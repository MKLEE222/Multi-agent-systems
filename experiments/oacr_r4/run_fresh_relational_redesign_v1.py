"""OACR-R4 v1: fresh relational contract-gated redesign replication."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import time
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

import networkx as nx
import requests

from experiments.common.operational_partition import (
    directional_information_gap,
    partition_from_signatures,
    refinement_relation,
)

WDQS = "https://query.wikidata.org/sparql"


def canonical_json(x):
    return json.dumps(x, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha_obj(x):
    return hashlib.sha256(canonical_json(x).encode("utf-8")).hexdigest()


def qid(uri: str) -> str:
    return uri.rsplit("/", 1)[-1].strip()


def query_for(root: str, limit: int) -> str:
    return f"""SELECT DISTINCT ?child ?parent WHERE {{
  {{
    ?child wdt:P279 wd:{root} .
    BIND(wd:{root} AS ?parent)
  }}
  UNION
  {{
    ?mid wdt:P279 wd:{root} .
    ?child wdt:P279 ?mid .
    BIND(?mid AS ?parent)
  }}
  UNION
  {{
    ?top wdt:P279 wd:{root} .
    ?mid wdt:P279 ?top .
    ?child wdt:P279 ?mid .
    BIND(?mid AS ?parent)
  }}
}}
ORDER BY ?child ?parent
LIMIT {limit}
"""


def fetch_json(query: str, timeout: int, retries: int) -> bytes:
    headers = {
        "Accept": "application/sparql-results+json",
        "User-Agent": "OACR-research/1.0 (GitHub Actions; R4 confirmatory replication)",
    }
    last = None
    for attempt in range(retries):
        try:
            r = requests.get(
                WDQS,
                params={"query": query, "format": "json"},
                headers=headers,
                timeout=timeout,
            )
            r.raise_for_status()
            if len(r.content) < 100:
                raise RuntimeError("WDQS response unexpectedly small")
            return r.content
        except Exception as exc:
            last = exc
            if attempt + 1 < retries:
                time.sleep(4 * (attempt + 1))
    raise RuntimeError(f"WDQS fetch failed: {last}")


def parse_edges(raw: bytes) -> Tuple[List[Tuple[str, str]], int]:
    obj = json.loads(raw.decode("utf-8"))
    bindings = obj["results"]["bindings"]
    edges = set()
    for row in bindings:
        if "child" not in row or "parent" not in row:
            continue
        c = qid(row["child"]["value"])
        p = qid(row["parent"]["value"])
        if c and p and c != p and c.startswith("Q") and p.startswith("Q"):
            edges.add((c, p))
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
            int(n): members[int(n)][0]
            if len(members[int(n)]) == 1
            else "SCC[" + ",".join(members[int(n)]) + "]"
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
        f"{a}\t{b}" for a, b in sorted(edges, key=lambda x: (str(x[0]), str(x[1])))
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


def entropy_probs(ps):
    return -sum(p * math.log2(p) for p in ps if p > 0)


def operational_entropy(partition, n):
    return entropy_probs(len(b) / n for b in partition)


def analyze_contract_subset(state_ids, current_sig, outcome_matrix, action_ids):
    part = partition_from_signatures(
        state_ids,
        lambda s: (
            current_sig[s],
            tuple(
                (
                    aid,
                    outcome_matrix[s][aid]["post_closure_sha256"],
                    outcome_matrix[s][aid]["post_closure_size"],
                )
                for aid in sorted(action_ids)
            ),
        ),
    )
    return {
        "operational_blocks": len(part),
        "operational_entropy_bits": operational_entropy(part, len(state_ids)),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--raw_json", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--limit", type=int, default=2500)
    ap.add_argument("--timeout", type=int, default=120)
    ap.add_argument("--retries", type=int, default=4)
    args = ap.parse_args()

    query = query_for(args.root, args.limit)
    raw = fetch_json(query, args.timeout, args.retries)
    Path(args.raw_json).parent.mkdir(parents=True, exist_ok=True)
    Path(args.raw_json).write_bytes(raw)
    raw_sha = hashlib.sha256(raw).hexdigest()

    edges, binding_count = parse_edges(raw)
    g, cyclic, labels = prepare_graph(edges, args.root)

    result = {
        "protocol": "OACR_R4_FRESH_RELATIONAL_REDESIGN_V1",
        "protocol_commit": "8af77e7fa2d31f0b1b8ee2b5bcebded98b56a237",
        "root": {"qid": args.root, "label": args.label},
        "query": query,
        "raw_sha256": raw_sha,
        "binding_count": binding_count,
        "row_limit": args.limit,
        "truncated": binding_count == args.limit,
    }

    if g.number_of_nodes() == 0:
        result["status"] = "STRUCTURAL_EXCLUSION"
        result["exclusion_reasons"] = ["empty_prepared_graph"]
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(json.dumps(result, indent=2))
        print(json.dumps(result, indent=2))
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

    exclusion = []
    if binding_count == args.limit:
        exclusion.append("query_truncated")
    if g.number_of_nodes() < 100:
        exclusion.append("prepared_nodes_lt_100")
    if g.number_of_edges() < 128:
        exclusion.append("prepared_edges_lt_128")
    if len(candidates_all) < 64:
        exclusion.append("redundant_candidates_lt_64")
    if g.number_of_edges() < 64:
        exclusion.append("asserted_edges_lt_64")

    if exclusion:
        result["status"] = "STRUCTURAL_EXCLUSION"
        result["exclusion_reasons"] = exclusion
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(json.dumps(result, indent=2))
        print(json.dumps(result, indent=2))
        return

    # Freeze state bank outcome-blind.
    candidates = (
        candidates_all
        if len(candidates_all) <= 271
        else evenly_spaced(candidates_all, 271)
    )

    # Freeze action panel from base deletion impact only.
    ranked = []
    for f in sorted(base_edges, key=lambda x: (str(x[0]), str(x[1]))):
        h = g.copy()
        h.remove_edge(*f)
        post = closure_edges(h)
        impact = len(base_closure ^ post)
        ranked.append((impact, str(f[0]), str(f[1]), f))
    ranked.sort()
    selected = evenly_spaced(ranked, 64)
    actions = [x[3] for x in selected]
    action_manifest = [
        {
            "action_index": i,
            "action_id": f"del:{labels[u]}>{labels[v]}",
            "edge": [labels[u], labels[v]],
            "base_deletion_impact": impact,
        }
        for i, (impact, _, _, (u, v)) in enumerate(selected)
    ]
    action_by_id = {
        a["action_id"]: actions[a["action_index"]]
        for a in action_manifest
    }

    base_after = {}
    for aid, f in action_by_id.items():
        h = g.copy()
        h.remove_edge(*f)
        base_after[aid] = closure_edges(h)

    state_specs = [("base", None)] + [
        (f"add:{labels[u]}>{labels[v]}", (u, v))
        for u, v in candidates
    ]
    state_ids = [s for s, _ in state_specs]

    current_sig = {s: closure_hash(base_closure) for s in state_ids}
    full_sig = {}
    gate_sig = {}
    active_by_action = {}
    active_states = []
    inactive_states = []

    for sid, added in state_specs:
        st = g.copy()
        if added is not None:
            st.add_edge(*added)
        full_sig[sid] = closure_hash(set(st.edges()))

        if added is None:
            active_by_action[sid] = {aid: False for aid in action_by_id}
            gate_sig[sid] = ["shared_base", None]
            continue

        per_action = {
            aid: (added not in base_after[aid])
            for aid in action_by_id
        }
        active_by_action[sid] = per_action
        if any(per_action.values()):
            active_states.append(sid)
            gate_sig[sid] = ["shared_base_plus_active_delta", [labels[added[0]], labels[added[1]]]]
        else:
            inactive_states.append(sid)
            gate_sig[sid] = ["shared_base", None]

    original_outcomes = {}
    compressed_outcomes = {}
    replay_mismatches = []

    for sid, added in state_specs:
        original = g.copy()
        if added is not None:
            original.add_edge(*added)

        compressed = g.copy()
        if gate_sig[sid][1] is not None and added is not None:
            compressed.add_edge(*added)

        original_rows = {}
        compressed_rows = {}
        for aid, f in action_by_id.items():
            o = original.copy()
            o.remove_edge(*f)
            oc = closure_edges(o)
            osig = {"post_closure_sha256": closure_hash(oc), "post_closure_size": len(oc)}
            original_rows[aid] = osig

            c = compressed.copy()
            c.remove_edge(*f)
            cc = closure_edges(c)
            csig = {"post_closure_sha256": closure_hash(cc), "post_closure_size": len(cc)}
            compressed_rows[aid] = csig

            if osig != csig:
                replay_mismatches.append({"state_id": sid, "action_id": aid})

        original_outcomes[sid] = original_rows
        compressed_outcomes[sid] = compressed_rows

    if replay_mismatches:
        raise RuntimeError(f"compressed replay mismatches: {len(replay_mismatches)}")

    op_partition = partition_from_signatures(
        state_ids,
        lambda s: tuple(
            (
                aid,
                original_outcomes[s][aid]["post_closure_sha256"],
                original_outcomes[s][aid]["post_closure_size"],
            )
            for aid in sorted(action_by_id)
        ),
    )

    reps = {
        "R0_current_closure": partition_from_signatures(state_ids, lambda s: current_sig[s]),
        "Rfull_asserted_identity": partition_from_signatures(state_ids, lambda s: full_sig[s]),
        "Rgate_contract_gated_delta": partition_from_signatures(state_ids, lambda s: gate_sig[s]),
    }

    diagnostics = {}
    for name, part in reps.items():
        info = directional_information_gap(part, op_partition)
        pair = refinement_relation(part, op_partition)
        diagnostics[name] = {
            **info,
            "representation_blocks": len(part),
            "under_refinement_count": pair["under_refinement_count"],
            "over_refinement_count": pair["over_refinement_count"],
        }

    # Conditional future demand beyond current observation.
    demand_bits = diagnostics["R0_current_closure"]["omission_U_bits"]

    # Frozen secondary subset analysis.
    singleton_rows = []
    for aid in sorted(action_by_id):
        a = analyze_contract_subset(state_ids, current_sig, original_outcomes, [aid])
        singleton_rows.append({"action_id": aid, **a})

    pair_rows = []
    aids = sorted(action_by_id)
    for i, a in enumerate(aids):
        for b in aids[i + 1 :]:
            z = analyze_contract_subset(state_ids, current_sig, original_outcomes, [a, b])
            pair_rows.append({"actions": [a, b], **z})

    loo_rows = []
    full_blocks = len(op_partition)
    full_entropy = operational_entropy(op_partition, len(state_ids))
    for omitted in aids:
        subset = [a for a in aids if a != omitted]
        z = analyze_contract_subset(state_ids, current_sig, original_outcomes, subset)
        loo_rows.append({
            "omitted_action": omitted,
            "operational_blocks": z["operational_blocks"],
            "operational_entropy_bits": z["operational_entropy_bits"],
            "full_partition_preserved_by_omission": z["operational_blocks"] == full_blocks
            and abs(z["operational_entropy_bits"] - full_entropy) < 1e-12,
        })

    before_records = len(candidates)
    after_records = len(active_states)
    reduction_fraction = (
        (before_records - after_records) / before_records if before_records else 0.0
    )

    result.update({
        "status": "INCLUDED",
        "state_bank": {
            "registered_redundant_candidates": len(candidates),
            "states": len(state_ids),
            "candidate_selection": "all if <=271 else 271 evenly spaced lexical candidates",
        },
        "action_manifest": action_manifest,
        "state_manifest": [
            {
                "state_id": sid,
                "added_edge": None if e is None else [labels[e[0]], labels[e[1]]],
            }
            for sid, e in state_specs
        ],
        "active_state_ids": active_states,
        "inactive_state_ids": inactive_states,
        "active_by_action": active_by_action,
        "fixed_representation_signatures": {
            "R0_current_closure": current_sig,
            "Rfull_asserted_identity": full_sig,
            "Rgate_contract_gated_delta": gate_sig,
        },
        "original_state_action_outcomes": original_outcomes,
        "compressed_state_action_outcomes": compressed_outcomes,
        "summary": {
            "states": len(state_ids),
            "registered_actions": len(action_manifest),
            "operational_blocks": len(op_partition),
            "operational_entropy_bits": full_entropy,
            "conditional_demand_bits": demand_bits,
            "active_augmented_states": len(active_states),
            "inactive_augmented_states": len(inactive_states),
            "active_fraction": len(active_states) / len(candidates) if candidates else 0.0,
            "delta_records_before": before_records,
            "delta_records_after": after_records,
            "delta_record_reduction_fraction": reduction_fraction,
            "native_replay_mismatches": len(replay_mismatches),
            "Rgate_exact_partition_match": diagnostics["Rgate_contract_gated_delta"]["partition_match_almost_surely"],
        },
        "diagnostics": diagnostics,
        "secondary_action_content": {
            "singletons": singleton_rows,
            "pairs": pair_rows,
            "leave_one_out": loo_rows,
        },
        "manifest_hashes": {
            "state_manifest_sha256": sha_obj([
                {
                    "state_id": sid,
                    "added_edge": None if e is None else [labels[e[0]], labels[e[1]]],
                }
                for sid, e in state_specs
            ]),
            "action_manifest_sha256": sha_obj(action_manifest),
            "active_matrix_sha256": sha_obj(active_by_action),
            "original_outcome_matrix_sha256": sha_obj(original_outcomes),
            "compressed_outcome_matrix_sha256": sha_obj(compressed_outcomes),
        },
    })

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(result, indent=2))
    print(json.dumps({
        "root": result["root"],
        "status": result["status"],
        "structural": structural,
        "summary": result["summary"],
        "diagnostics": {
            k: {
                "U": v["omission_U_bits"],
                "E": v["excess_E_bits"],
                "blocks": v["representation_blocks"],
            }
            for k, v in diagnostics.items()
        },
    }, indent=2))


if __name__ == "__main__":
    main()
