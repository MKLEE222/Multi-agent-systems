"""OACR-R3 v1: shared-contract exact relational adequacy matrix."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import networkx as nx

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "common"))

from operational_partition import (  # noqa: E402
    directional_information_gap,
    partition_from_signatures,
    refinement_relation,
)

ROOT = "Q12136"
EXPECTED_RAW_SHA256 = "3d3852ff72382c171e3a5496336767809b9455541fa2604f7b6857a8e69457df"


def qid(uri: str) -> str:
    return uri.rsplit("/", 1)[-1].strip()


def parse_edges(raw: bytes) -> List[Tuple[str, str]]:
    obj = json.loads(raw.decode("utf-8"))
    edges = set()
    for row in obj["results"]["bindings"]:
        if "child" not in row or "parent" not in row:
            continue
        c = qid(row["child"]["value"])
        p = qid(row["parent"]["value"])
        if c and p and c != p and c.startswith("Q") and p.startswith("Q"):
            edges.add((c, p))
    return sorted(edges)


def prepare_graph(edges):
    g = nx.DiGraph()
    g.add_edges_from(edges)
    if ROOT in g:
        nodes = nx.node_connected_component(g.to_undirected(), ROOT)
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
            int(n): members[int(n)][0] if len(members[int(n)]) == 1
            else "SCC[" + ",".join(members[int(n)]) + "]"
            for n in cg.nodes
        }
        return cg, cyclic, labels
    return g, [], {n: n for n in g.nodes}


def closure_edges(g: nx.DiGraph):
    if not nx.is_directed_acyclic_graph(g):
        raise RuntimeError("prepared graph must be DAG")
    return set(nx.transitive_closure_dag(g).edges())


def closure_hash(edges) -> str:
    payload = "\n".join(f"{a}\t{b}" for a, b in sorted(edges, key=lambda x: (str(x[0]), str(x[1]))))
    return hashlib.sha256(payload.encode()).hexdigest()


def path_count_dag(g: nx.DiGraph, source, target) -> int:
    topo = list(nx.topological_sort(g))
    pos = {n: i for i, n in enumerate(topo)}
    if source not in pos or target not in pos or pos[source] >= pos[target]:
        return 0
    ways: Dict[object, int] = {source: 1}
    for n in topo[pos[source] : pos[target] + 1]:
        w = ways.get(n, 0)
        if not w:
            continue
        for nxt in g.successors(n):
            if pos[nxt] <= pos[target]:
                ways[nxt] = ways.get(nxt, 0) + w
    return int(ways.get(target, 0))


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


def block_sizes(partition):
    return sorted((len(x) for x in partition), reverse=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw_json", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--actions", type=int, default=64)
    args = ap.parse_args()

    raw = Path(args.raw_json).read_bytes()
    raw_sha = hashlib.sha256(raw).hexdigest()
    if raw_sha != EXPECTED_RAW_SHA256:
        raise RuntimeError(f"raw carrier hash mismatch: {raw_sha}")

    g, cyclic, labels = prepare_graph(parse_edges(raw))
    base_edges = set(g.edges())
    base_closure = closure_edges(g)
    candidates = sorted(base_closure - base_edges, key=lambda x: (str(x[0]), str(x[1])))

    # Freeze action alphabet using only base-graph deletion impact.
    ranked = []
    for f in sorted(base_edges, key=lambda x: (str(x[0]), str(x[1]))):
        h = g.copy()
        h.remove_edge(*f)
        post = closure_edges(h)
        impact = len(base_closure ^ post)
        ranked.append((impact, str(f[0]), str(f[1]), f))
    ranked.sort()
    selected = evenly_spaced(ranked, args.actions)
    actions = [x[3] for x in selected]

    state_specs = [("base", None)] + [
        (f"add:{labels[u]}>{labels[v]}", (u, v)) for u, v in candidates
    ]

    current_closure_sig = {}
    full_asserted_sig = {}
    support_sig = {}
    operational_sig = {}

    for state_id, added in state_specs:
        st = g.copy()
        if added is not None:
            st.add_edge(*added)
        cur = closure_edges(st)
        if cur != base_closure:
            raise RuntimeError(f"current closure changed for {state_id}")

        current_closure_sig[state_id] = closure_hash(cur)
        full_asserted_sig[state_id] = closure_hash(set(st.edges()))
        support_sig[state_id] = tuple(
            str(path_count_dag(st, u, v)) for u, v in actions
        )

        outcomes = []
        for f in actions:
            if not st.has_edge(*f):
                raise RuntimeError(f"shared action missing in state {state_id}: {f}")
            h = st.copy()
            h.remove_edge(*f)
            post = closure_edges(h)
            outcomes.append((str(f[0]), str(f[1]), closure_hash(post), len(post)))
        operational_sig[state_id] = tuple(outcomes)

    state_ids = [x[0] for x in state_specs]
    op_partition = partition_from_signatures(state_ids, lambda s: operational_sig[s])

    reps = {
        "R0_current_closure": partition_from_signatures(
            state_ids, lambda s: current_closure_sig[s]
        ),
        "Rfull_asserted_identity": partition_from_signatures(
            state_ids, lambda s: full_asserted_sig[s]
        ),
        "Rsupport_action_endpoint_path_counts": partition_from_signatures(
            state_ids, lambda s: support_sig[s]
        ),
    }

    diagnostics = {}
    for name, part in reps.items():
        diagnostics[name] = {
            "pairwise": refinement_relation(part, op_partition),
            "information": directional_information_gap(part, op_partition),
            "representation_blocks": len(part),
            "representation_block_sizes": block_sizes(part)[:30],
        }

    summary = {
        "raw_sha256": raw_sha,
        "prepared_nodes": g.number_of_nodes(),
        "prepared_edges": g.number_of_edges(),
        "cyclic_scc_count": len(cyclic),
        "states": len(state_ids),
        "redundant_augmented_states": len(candidates),
        "shared_actions": len(actions),
        "operational_blocks_H1": len(op_partition),
        "operational_block_sizes": block_sizes(op_partition)[:50],
        "action_impact_min": min(x[0] for x in selected),
        "action_impact_max": max(x[0] for x in selected),
        "diagnostics": diagnostics,
    }

    out = {
        "protocol": "OACR_R3_SHARED_CONTRACT_RELATIONAL_V1",
        "source": {"raw_sha256": raw_sha, "r1_run": 36378905855},
        "state_bank_rule": "base plus every single entailed-but-unasserted redundant edge augmentation",
        "action_selection_rule": "64 evenly spaced asserted edges after sorting by base deletion closure impact then lexical identity",
        "actions": [
            {
                "edge": [labels[u], labels[v]],
                "base_deletion_impact": impact,
            }
            for impact, _, _, (u, v) in selected
        ],
        "summary": summary,
    }
    p = Path(args.out)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(out, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
