"""OACR D1/D2-R v1: contract-gated delta representation on frozen R3 carrier."""
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


def state_id_for(labels, added):
    if added is None:
        return "base"
    return f"add:{labels[added[0]]}>{labels[added[1]]}"


def load_expected_m2(path: Path):
    x = json.loads(path.read_text())
    if x.get("protocol") != "OACR_M2_R_NESTED_CONTRACT_V2":
        raise RuntimeError(f"unexpected M2 protocol: {x.get('protocol')}")
    return x


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw_json", required=True)
    ap.add_argument("--m2_json", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    raw = Path(args.raw_json).read_bytes()
    raw_sha = hashlib.sha256(raw).hexdigest()
    if raw_sha != EXPECTED_RAW_SHA256:
        raise RuntimeError(f"raw carrier hash mismatch: {raw_sha}")

    m2 = load_expected_m2(Path(args.m2_json))
    g, labels = prepare_graph(parse_edges(raw))
    base_edges = set(g.edges())
    base_closure = closure_edges(g)
    candidates = sorted(base_closure - base_edges, key=lambda x: (str(x[0]), str(x[1])))

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
    action_ids = [f"del:{labels[u]}>{labels[v]}" for u, v in actions]

    m2_action_ids = [a["action_id"] for a in m2["action_manifest"]]
    if set(action_ids) != set(m2_action_ids):
        raise RuntimeError("reconstructed action set does not match M2 action manifest")

    action_by_id = {f"del:{labels[u]}>{labels[v]}": (u, v) for u, v in actions}

    # Precompute base post-deletion closures once. This is the only action-conditioned
    # information used by the encoder.
    base_after = {}
    for aid in m2_action_ids:
        f = action_by_id[aid]
        h = g.copy()
        h.remove_edge(*f)
        post = closure_edges(h)
        base_after[aid] = post

    state_specs = [("base", None)] + [
        (state_id_for(labels, e), e) for e in candidates
    ]
    state_ids = [s for s, _ in state_specs]
    if state_ids != [s["state_id"] for s in m2["state_manifest"]]:
        raise RuntimeError("state manifest mismatch against accepted M2-R artifact")

    expected_outcomes = {
        s: {r["action_id"]: r for r in rows}
        for s, rows in m2["state_action_outcomes"].items()
    }

    active_matrix = {}
    encoding = {}
    active_edges = []
    inactive_edges = []

    for sid, added in state_specs:
        if added is None:
            active_matrix[sid] = {aid: False for aid in m2_action_ids}
            encoding[sid] = {"kind": "shared_base", "retained_delta": None}
            continue

        u, v = added
        per_action = {
            aid: ((u, v) not in base_after[aid])
            for aid in m2_action_ids
        }
        active = any(per_action.values())
        active_matrix[sid] = per_action
        if active:
            active_edges.append(sid)
            encoding[sid] = {
                "kind": "shared_base_plus_active_delta",
                "retained_delta": [labels[u], labels[v]],
            }
        else:
            inactive_edges.append(sid)
            encoding[sid] = {"kind": "shared_base", "retained_delta": None}

    # Representation partition induced by the physical encoding.
    rep_partition = partition_from_signatures(
        state_ids,
        lambda s: encoding[s],
    )

    # Frozen operational partition from accepted M2 raw matrix.
    op_partition = partition_from_signatures(
        state_ids,
        lambda s: tuple(
            (
                r["action_id"],
                r["post_closure_sha256"],
                r["post_closure_size"],
            )
            for r in expected_outcomes[s].values()
        ),
    )

    info = directional_information_gap(rep_partition, op_partition)
    pair = refinement_relation(rep_partition, op_partition)

    # Full exact replay from compressed representation.
    replay_mismatches = []
    replay_records = 0
    replay_matrix = {}
    for sid, added in state_specs:
        enc = encoding[sid]
        if enc["retained_delta"] is None:
            retained_internal = None
        else:
            retained_internal = added
            if retained_internal is None:
                raise RuntimeError("active encoding missing original added edge")

        st = g.copy()
        if retained_internal is not None:
            st.add_edge(*retained_internal)

        rows = []
        for aid in m2_action_ids:
            f = action_by_id[aid]
            if not st.has_edge(*f):
                raise RuntimeError(f"registered action absent after decode: {sid} {aid}")
            h = st.copy()
            h.remove_edge(*f)
            post = closure_edges(h)
            got = {
                "action_id": aid,
                "post_closure_sha256": closure_hash(post),
                "post_closure_size": len(post),
            }
            exp = expected_outcomes[sid][aid]
            if (
                got["post_closure_sha256"] != exp["post_closure_sha256"]
                or got["post_closure_size"] != exp["post_closure_size"]
            ):
                replay_mismatches.append({
                    "state_id": sid,
                    "action_id": aid,
                    "expected": {
                        "post_closure_sha256": exp["post_closure_sha256"],
                        "post_closure_size": exp["post_closure_size"],
                    },
                    "got": got,
                })
            rows.append(got)
            replay_records += 1
        replay_matrix[sid] = rows

    if replay_mismatches:
        raise RuntimeError(f"compressed replay mismatches: {len(replay_mismatches)}")

    # Verify the theorem implementation directly for every inactive edge/action:
    # inactive means its endpoints remain reachable in every base post-deletion graph.
    theorem_violations = []
    for sid, added in state_specs:
        if added is None or sid not in inactive_edges:
            continue
        u, v = added
        for aid in m2_action_ids:
            if (u, v) not in base_after[aid]:
                theorem_violations.append((sid, aid))
    if theorem_violations:
        raise RuntimeError(f"inactive-edge theorem violations: {theorem_violations[:5]}")

    augmented_states = len(candidates)
    before_total_delta_records = augmented_states
    after_total_delta_records = len(active_edges)
    before_mean = before_total_delta_records / len(state_ids)
    after_mean = after_total_delta_records / len(state_ids)
    reduction = (
        (before_total_delta_records - after_total_delta_records)
        / before_total_delta_records
        if before_total_delta_records else 0.0
    )

    out = {
        "protocol": "OACR_D1D2_R_CONTRACT_GATED_DELTA_V1",
        "protocol_commit": "77eb6c4653d23f0e3e538e261086a82f50544410",
        "source": {
            "raw_sha256": raw_sha,
            "accepted_m2_r_run": 36425222754,
            "accepted_m2_r_outcome_matrix_sha256": m2["manifest_hashes"]["outcome_matrix_sha256"],
        },
        "summary": {
            "states": len(state_ids),
            "redundant_augmented_states": augmented_states,
            "registered_actions": len(m2_action_ids),
            "contract_active_augmented_states": len(active_edges),
            "contract_inactive_augmented_states": len(inactive_edges),
            "representation_blocks": len(rep_partition),
            "operational_blocks": len(op_partition),
            "omission_U_bits": info["omission_U_bits"],
            "excess_E_bits": info["excess_E_bits"],
            "under_refinement_count": pair["under_refinement_count"],
            "over_refinement_count": pair["over_refinement_count"],
            "exact_partition_match": info["partition_match_almost_surely"],
            "replay_records": replay_records,
            "replay_mismatches": len(replay_mismatches),
            "before_total_delta_edge_records": before_total_delta_records,
            "after_total_delta_edge_records": after_total_delta_records,
            "before_mean_delta_edge_records_per_state": before_mean,
            "after_mean_delta_edge_records_per_state": after_mean,
            "delta_edge_record_reduction_fraction": reduction,
        },
        "action_manifest": m2["action_manifest"],
        "encoding": encoding,
        "active_by_action": active_matrix,
        "active_state_ids": active_edges,
        "inactive_state_ids": inactive_edges,
        "representation_information": info,
        "pairwise_relation": pair,
        "replay_matrix": replay_matrix,
        "checks": {
            "theorem_implementation_violations": theorem_violations,
            "native_replay_mismatch_count": len(replay_mismatches),
            "native_replay_passed": len(replay_mismatches) == 0,
            "adequacy_U_zero": abs(info["omission_U_bits"]) < 1e-12,
        },
    }

    p = Path(args.out)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(out, indent=2))
    print(json.dumps(out["summary"], indent=2))


if __name__ == "__main__":
    main()
