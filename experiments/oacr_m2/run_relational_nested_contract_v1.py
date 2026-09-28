"""OACR-M2-R v1: exact nested-contract adequacy trajectories on the frozen R3 carrier."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
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
ENDPOINT = {
    "operational_blocks": 101,
    "R0_U": 3.391442481659308,
    "R0_E": 0.0,
    "Rfull_U": 0.0,
    "Rfull_E": 4.69602035959104,
    "Rsupport_U": 3.391442481659308,
    "Rsupport_E": 0.0,
}
ANCHORS = {0, 1, 2, 4, 8, 16, 32, 64}


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
            int(n): members[int(n)][0]
            if len(members[int(n)]) == 1
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
    payload = "\n".join(
        f"{a}\t{b}" for a, b in sorted(edges, key=lambda x: (str(x[0]), str(x[1])))
    )
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


def maximin_rank_order(selected):
    """Outcome-blind space-filling order over selected base-rank positions."""
    remaining = list(selected)
    median = sorted(x["rank"] for x in remaining)[(len(remaining) - 1) // 2]
    first = min(
        remaining,
        key=lambda x: (
            abs(x["rank"] - median),
            x["rank"],
            str(x["edge"][0]),
            str(x["edge"][1]),
        ),
    )
    order = [first]
    remaining.remove(first)
    while remaining:
        def key(x):
            mind = min(abs(x["rank"] - y["rank"]) for y in order)
            return (-mind, x["rank"], str(x["edge"][0]), str(x["edge"][1]))
        nxt = min(remaining, key=key)
        order.append(nxt)
        remaining.remove(nxt)
    return order


def block_sizes(partition):
    return sorted((len(x) for x in partition), reverse=True)


def is_refinement(fine, coarse) -> bool:
    coarse_index = {}
    for i, block in enumerate(coarse):
        for x in block:
            coarse_index[x] = i
    for block in fine:
        if len({coarse_index[x] for x in block}) != 1:
            return False
    return True


def approx(a, b, tol=1e-10):
    return abs(float(a) - float(b)) <= tol


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw_json", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    raw = Path(args.raw_json).read_bytes()
    raw_sha = hashlib.sha256(raw).hexdigest()
    if raw_sha != EXPECTED_RAW_SHA256:
        raise RuntimeError(f"raw carrier hash mismatch: {raw_sha}")

    g, cyclic, labels = prepare_graph(parse_edges(raw))
    base_edges = set(g.edges())
    base_closure = closure_edges(g)
    candidates = sorted(base_closure - base_edges, key=lambda x: (str(x[0]), str(x[1])))

    ranked = []
    for rank_seed, f in enumerate(sorted(base_edges, key=lambda x: (str(x[0]), str(x[1])))):
        h = g.copy()
        h.remove_edge(*f)
        post = closure_edges(h)
        impact = len(base_closure ^ post)
        ranked.append((impact, str(f[0]), str(f[1]), f))
    ranked.sort()
    selected_tuples = evenly_spaced(ranked, 64)
    selected = []
    for t in selected_tuples:
        rank = ranked.index(t)
        selected.append({"rank": rank, "impact": t[0], "edge": t[3]})
    ordered = maximin_rank_order(selected)
    actions = [x["edge"] for x in ordered]

    state_specs = [("base", None)] + [
        (f"add:{labels[u]}>{labels[v]}", (u, v)) for u, v in candidates
    ]
    state_ids = [x[0] for x in state_specs]

    current_closure_sig = {}
    full_asserted_sig = {}
    support64_sig = {}
    all_outcomes = {}

    for state_id, added in state_specs:
        st = g.copy()
        if added is not None:
            st.add_edge(*added)
        cur = closure_edges(st)
        if cur != base_closure:
            raise RuntimeError(f"current closure changed for {state_id}")
        current_closure_sig[state_id] = closure_hash(cur)
        full_asserted_sig[state_id] = closure_hash(set(st.edges()))
        support64_sig[state_id] = tuple(
            str(path_count_dag(st, u, v)) for u, v in actions
        )
        out = []
        for f in actions:
            if not st.has_edge(*f):
                raise RuntimeError(f"shared action missing in {state_id}: {f}")
            h = st.copy()
            h.remove_edge(*f)
            post = closure_edges(h)
            out.append((str(f[0]), str(f[1]), closure_hash(post), len(post)))
        all_outcomes[state_id] = tuple(out)

    reps = {
        "R0_fixed_current_closure": partition_from_signatures(
            state_ids, lambda s: current_closure_sig[s]
        ),
        "Rfull_fixed_asserted_identity": partition_from_signatures(
            state_ids, lambda s: full_asserted_sig[s]
        ),
        "Rsupport64_fixed_path_counts": partition_from_signatures(
            state_ids, lambda s: support64_sig[s]
        ),
    }

    rows = []
    previous_op = None
    refinement_failures = []
    for k in range(65):
        op_partition = partition_from_signatures(
            state_ids,
            lambda s, k=k: (current_closure_sig[s], all_outcomes[s][:k]),
        )
        if previous_op is not None and not is_refinement(op_partition, previous_op):
            refinement_failures.append(k)

        diag = {}
        for name, rep in reps.items():
            info = directional_information_gap(rep, op_partition)
            pair = refinement_relation(rep, op_partition)
            diag[name] = {
                "representation_blocks": len(rep),
                "under_refinement_count": pair["under_refinement_count"],
                "over_refinement_count": pair["over_refinement_count"],
                "U_bits": info["omission_U_bits"],
                "E_bits": info["excess_E_bits"],
                "adequate": info["adequate_almost_surely"],
                "partition_match": info["partition_match_almost_surely"],
            }
        changed = previous_op is None or len(op_partition) != len(previous_op) or not (
            is_refinement(previous_op, op_partition) and is_refinement(op_partition, previous_op)
        )
        rows.append(
            {
                "k": k,
                "anchor": k in ANCHORS,
                "operational_blocks": len(op_partition),
                "operational_block_sizes": block_sizes(op_partition)[:50],
                "changed_from_previous": bool(changed),
                "diagnostics": diag,
            }
        )
        previous_op = op_partition

    if refinement_failures:
        raise RuntimeError(f"nested operational refinement failed at prefixes: {refinement_failures}")

    end = rows[-1]
    d0 = end["diagnostics"]["R0_fixed_current_closure"]
    df = end["diagnostics"]["Rfull_fixed_asserted_identity"]
    ds = end["diagnostics"]["Rsupport64_fixed_path_counts"]
    endpoint_ok = (
        end["operational_blocks"] == ENDPOINT["operational_blocks"]
        and approx(d0["U_bits"], ENDPOINT["R0_U"])
        and approx(d0["E_bits"], ENDPOINT["R0_E"])
        and approx(df["U_bits"], ENDPOINT["Rfull_U"])
        and approx(df["E_bits"], ENDPOINT["Rfull_E"])
        and approx(ds["U_bits"], ENDPOINT["Rsupport_U"])
        and approx(ds["E_bits"], ENDPOINT["Rsupport_E"])
    )
    if not endpoint_ok:
        raise RuntimeError(f"R3 endpoint regression failed: {json.dumps(end, indent=2)}")

    out = {
        "protocol": "OACR_M2_R_NESTED_CONTRACT_V1",
        "source": {
            "raw_sha256": raw_sha,
            "r3_run": 36385544527,
            "r3_checkpoint_commit": "5cc8baf1db8b66061032da6c99723a2956f98121",
        },
        "state_bank": {
            "states": len(state_ids),
            "redundant_augmented_states": len(candidates),
            "current_closure_identical": len(set(current_closure_sig.values())) == 1,
        },
        "action_order_rule": "maximin spacing over the exact R3 selected actions by base deletion-impact rank; no augmented-state outcomes used",
        "actions": [
            {
                "prefix_position": i + 1,
                "base_rank": x["rank"],
                "base_deletion_impact": x["impact"],
                "edge": [labels[x["edge"][0]], labels[x["edge"][1]]],
            }
            for i, x in enumerate(ordered)
        ],
        "fixed_representations": list(reps),
        "trajectory": rows,
        "checks": {
            "nested_refinement_failures": refinement_failures,
            "endpoint_regression_passed": endpoint_ok,
            "full_contract_operational_blocks": end["operational_blocks"],
        },
    }

    p = Path(args.out)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(out, indent=2))
    print(json.dumps({
        "protocol": out["protocol"],
        "states": len(state_ids),
        "prefixes": len(rows),
        "refinement_failures": refinement_failures,
        "endpoint_regression_passed": endpoint_ok,
        "anchors": [
            {
                "k": r["k"],
                "O": r["operational_blocks"],
                "R0_U": r["diagnostics"]["R0_fixed_current_closure"]["U_bits"],
                "Rfull_E": r["diagnostics"]["Rfull_fixed_asserted_identity"]["E_bits"],
                "Rsupport_U": r["diagnostics"]["Rsupport64_fixed_path_counts"]["U_bits"],
                "Rsupport_E": r["diagnostics"]["Rsupport64_fixed_path_counts"]["E_bits"],
            }
            for r in rows if r["anchor"]
        ],
    }, indent=2))


if __name__ == "__main__":
    main()
