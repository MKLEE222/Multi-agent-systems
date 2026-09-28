"""Independent verifier for OACR D1/D2-R contract-gated delta representation."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import List, Tuple

import networkx as nx

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
            int(n): members[int(n)][0]
            if len(members[int(n)]) == 1
            else "SCC[" + ",".join(members[int(n)]) + "]"
            for n in cg.nodes
        }
        return cg, labels
    return g, {n: n for n in g.nodes}


def closure_edges(g: nx.DiGraph):
    if not nx.is_directed_acyclic_graph(g):
        raise RuntimeError("prepared graph must be DAG")
    return set(nx.transitive_closure_dag(g).edges())


def closure_hash(edges) -> str:
    payload = "\n".join(
        f"{a}\t{b}" for a, b in sorted(edges, key=lambda x: (str(x[0]), str(x[1])))
    )
    return hashlib.sha256(payload.encode()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw_json", required=True)
    ap.add_argument("--m2_json", required=True)
    ap.add_argument("--redesign_json", required=True)
    args = ap.parse_args()

    raw = Path(args.raw_json).read_bytes()
    raw_sha = hashlib.sha256(raw).hexdigest()
    if raw_sha != EXPECTED_RAW_SHA256:
        raise RuntimeError(f"raw carrier hash mismatch: {raw_sha}")

    m2 = json.loads(Path(args.m2_json).read_text())
    d = json.loads(Path(args.redesign_json).read_text())
    if d.get("protocol") != "OACR_D1D2_R_CONTRACT_GATED_DELTA_V1":
        raise RuntimeError("unexpected redesign protocol")

    g, labels = prepare_graph(parse_edges(raw))
    base_edges = set(g.edges())
    base_closure = closure_edges(g)
    candidates = sorted(base_closure - base_edges, key=lambda x: (str(x[0]), str(x[1])))

    # Recover action edges directly from frozen action labels.
    label_to_node = {str(v): k for k, v in labels.items()}
    action_edges = {}
    for a in d["action_manifest"]:
        aid = a["action_id"]
        if not aid.startswith("del:"):
            raise RuntimeError(f"bad action id: {aid}")
        lhs = aid[4:]
        ulabel, vlabel = lhs.split(">", 1)
        if ulabel not in label_to_node or vlabel not in label_to_node:
            raise RuntimeError(f"cannot resolve action labels: {aid}")
        action_edges[aid] = (label_to_node[ulabel], label_to_node[vlabel])

    # Independent base-deletion reachability table.
    base_after = {}
    for aid, f in action_edges.items():
        h = g.copy()
        h.remove_edge(*f)
        base_after[aid] = closure_edges(h)

    # Rebuild state IDs and map labels back to candidate edges.
    state_to_edge = {"base": None}
    for e in candidates:
        sid = f"add:{labels[e[0]]}>{labels[e[1]]}"
        state_to_edge[sid] = e

    if set(state_to_edge) != set(d["encoding"]):
        raise RuntimeError("redesign state set mismatch")

    expected_outcomes = {
        s: {r["action_id"]: r for r in rows}
        for s, rows in m2["state_action_outcomes"].items()
    }

    active_count = 0
    inactive_count = 0
    replay_mismatches = 0
    classification_mismatches = 0
    replay_records = 0

    for sid, original_edge in state_to_edge.items():
        if original_edge is None:
            independently_active = False
        else:
            u, v = original_edge
            independently_active = any(
                (u, v) not in base_after[aid]
                for aid in action_edges
            )

        stored_active = d["encoding"][sid]["retained_delta"] is not None
        if stored_active != independently_active:
            classification_mismatches += 1

        if sid != "base":
            if independently_active:
                active_count += 1
            else:
                inactive_count += 1

        # Decode independently: retain original redundant edge iff structurally active.
        st = g.copy()
        if independently_active and original_edge is not None:
            st.add_edge(*original_edge)

        for aid, f in action_edges.items():
            h = st.copy()
            h.remove_edge(*f)
            post = closure_edges(h)
            exp = expected_outcomes[sid][aid]
            if closure_hash(post) != exp["post_closure_sha256"] or len(post) != exp["post_closure_size"]:
                replay_mismatches += 1
            replay_records += 1

    if classification_mismatches:
        raise RuntimeError(f"classification mismatches: {classification_mismatches}")
    if replay_mismatches:
        raise RuntimeError(f"native replay mismatches: {replay_mismatches}")

    s = d["summary"]
    if s["contract_active_augmented_states"] != active_count:
        raise RuntimeError("active-count mismatch")
    if s["contract_inactive_augmented_states"] != inactive_count:
        raise RuntimeError("inactive-count mismatch")
    if s["replay_records"] != replay_records:
        raise RuntimeError("replay-record mismatch")
    if abs(float(s["omission_U_bits"])) > 1e-12:
        raise RuntimeError("stored redesign is not adequate")

    print(json.dumps({
        "protocol": d["protocol"],
        "status": "PASS",
        "independent_active_augmented_states": active_count,
        "independent_inactive_augmented_states": inactive_count,
        "classification_mismatches": classification_mismatches,
        "native_replay_records": replay_records,
        "native_replay_mismatches": replay_mismatches,
    }, indent=2))


if __name__ == "__main__":
    main()
