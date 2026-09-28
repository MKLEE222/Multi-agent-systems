"""Independent verifier for OACR-R4 fresh relational redesign artifacts."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import List, Tuple

import networkx as nx

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "common"))

from operational_partition import (
    directional_information_gap,
    partition_from_signatures,
    refinement_relation,
)


def qid(uri: str) -> str:
    return uri.rsplit("/", 1)[-1].strip()


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


def partition_identity(partition):
    blocks = sorted(
        [sorted(str(x) for x in block) for block in partition],
        key=lambda block: (len(block), block),
    )
    payload = json.dumps(blocks, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def analyze_subset(state_ids, current_sig, outcomes, action_ids):
    p = partition_from_signatures(
        state_ids,
        lambda s: (
            current_sig[s],
            tuple(
                (
                    aid,
                    outcomes[s][aid]["post_closure_sha256"],
                    outcomes[s][aid]["post_closure_size"],
                )
                for aid in sorted(action_ids)
            ),
        ),
    )
    return len(p), partition_identity(p)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw_json", required=True)
    ap.add_argument("--result_json", required=True)
    args = ap.parse_args()

    raw = Path(args.raw_json).read_bytes()
    x = json.loads(Path(args.result_json).read_text())

    if hashlib.sha256(raw).hexdigest() != x["raw_sha256"]:
        raise RuntimeError("raw SHA mismatch")

    root = x["root"]["qid"]
    edges, binding_count = parse_edges(raw)
    g, cyclic, labels = prepare_graph(edges, root)

    if binding_count != x["binding_count"]:
        raise RuntimeError("binding count mismatch")

    if x["status"] == "STRUCTURAL_EXCLUSION":
        print(json.dumps({
            "protocol": x["protocol"],
            "root": x["root"],
            "status": "PASS_STRUCTURAL_EXCLUSION",
            "binding_count": binding_count,
            "exclusion_reasons": x.get("exclusion_reasons", []),
        }, indent=2))
        return

    base_edges = set(g.edges())
    base_closure = closure_edges(g)
    candidates_all = sorted(base_closure - base_edges, key=lambda e: (str(e[0]), str(e[1])))
    candidates = candidates_all if len(candidates_all) <= 271 else evenly_spaced(candidates_all, 271)

    ranked = []
    for f in sorted(base_edges, key=lambda e: (str(e[0]), str(e[1]))):
        h = g.copy()
        h.remove_edge(*f)
        post = closure_edges(h)
        ranked.append((len(base_closure ^ post), str(f[0]), str(f[1]), f))
    ranked.sort()
    selected = evenly_spaced(ranked, 64)
    actions = [r[3] for r in selected]
    action_ids = [f"del:{labels[u]}>{labels[v]}" for u, v in actions]
    action_by_id = dict(zip(action_ids, actions))

    stored_action_ids = [a["action_id"] for a in x["action_manifest"]]
    if stored_action_ids != action_ids:
        raise RuntimeError("action manifest mismatch")

    state_specs = [("base", None)] + [
        (f"add:{labels[u]}>{labels[v]}", (u, v))
        for u, v in candidates
    ]
    state_ids = [s for s, _ in state_specs]
    if state_ids != [s["state_id"] for s in x["state_manifest"]]:
        raise RuntimeError("state manifest mismatch")

    base_after = {}
    for aid, f in action_by_id.items():
        h = g.copy()
        h.remove_edge(*f)
        base_after[aid] = closure_edges(h)

    current_sig = {}
    full_sig = {}
    gate_sig = {}
    active_matrix = {}
    original_outcomes = {}
    compressed_outcomes = {}
    replay_mismatch = 0

    for sid, added in state_specs:
        st = g.copy()
        if added is not None:
            st.add_edge(*added)
        current_sig[sid] = closure_hash(closure_edges(st))
        full_sig[sid] = closure_hash(set(st.edges()))

        if added is None:
            active_matrix[sid] = {aid: False for aid in action_ids}
            gate_sig[sid] = ["shared_base", None]
            active = False
        else:
            active_matrix[sid] = {
                aid: (added not in base_after[aid])
                for aid in action_ids
            }
            active = any(active_matrix[sid].values())
            gate_sig[sid] = (
                ["shared_base_plus_active_delta", [labels[added[0]], labels[added[1]]]]
                if active else ["shared_base", None]
            )

        compressed = g.copy()
        if active and added is not None:
            compressed.add_edge(*added)

        oo = {}
        co = {}
        for aid, f in action_by_id.items():
            o = st.copy()
            o.remove_edge(*f)
            oc = closure_edges(o)
            oo[aid] = {
                "post_closure_sha256": closure_hash(oc),
                "post_closure_size": len(oc),
            }

            c = compressed.copy()
            c.remove_edge(*f)
            cc = closure_edges(c)
            co[aid] = {
                "post_closure_sha256": closure_hash(cc),
                "post_closure_size": len(cc),
            }
            if oo[aid] != co[aid]:
                replay_mismatch += 1

        original_outcomes[sid] = oo
        compressed_outcomes[sid] = co

    if replay_mismatch:
        raise RuntimeError(f"independent replay mismatch: {replay_mismatch}")

    if active_matrix != x["active_by_action"]:
        raise RuntimeError("active matrix mismatch")
    if original_outcomes != x["original_state_action_outcomes"]:
        raise RuntimeError("original outcome matrix mismatch")
    if compressed_outcomes != x["compressed_state_action_outcomes"]:
        raise RuntimeError("compressed outcome matrix mismatch")

    op = partition_from_signatures(
        state_ids,
        lambda s: tuple(
            (
                aid,
                original_outcomes[s][aid]["post_closure_sha256"],
                original_outcomes[s][aid]["post_closure_size"],
            )
            for aid in sorted(action_ids)
        ),
    )

    reps = {
        "R0_current_closure": partition_from_signatures(state_ids, lambda s: current_sig[s]),
        "Rfull_asserted_identity": partition_from_signatures(state_ids, lambda s: full_sig[s]),
        "Rgate_contract_gated_delta": partition_from_signatures(state_ids, lambda s: gate_sig[s]),
    }

    metric_mismatches = []
    for name, rp in reps.items():
        info = directional_information_gap(rp, op)
        pair = refinement_relation(rp, op)
        st = x["diagnostics"][name]
        for key in [
            "representation_entropy_bits",
            "operational_entropy_bits",
            "joint_entropy_bits",
            "mutual_information_bits",
            "omission_U_bits",
            "excess_E_bits",
            "variation_of_information_bits",
        ]:
            if abs(float(info[key]) - float(st[key])) > 1e-10:
                metric_mismatches.append((name, key))
        if pair["under_refinement_count"] != st["under_refinement_count"]:
            metric_mismatches.append((name, "under_refinement_count"))
        if pair["over_refinement_count"] != st["over_refinement_count"]:
            metric_mismatches.append((name, "over_refinement_count"))

    if metric_mismatches:
        raise RuntimeError(f"metric mismatches: {metric_mismatches[:10]}")

    # Verify frozen secondary singleton/pair/leave-one-out summaries.
    singleton_stored = {r["action_id"]: r for r in x["secondary_action_content"]["singletons"]}
    for aid in action_ids:
        blocks, psha = analyze_subset(state_ids, current_sig, original_outcomes, [aid])
        if singleton_stored[aid]["operational_blocks"] != blocks:
            raise RuntimeError(f"singleton blocks mismatch {aid}")
        if singleton_stored[aid]["operational_partition_sha256"] != psha:
            raise RuntimeError(f"singleton partition mismatch {aid}")

    pair_stored = {
        tuple(r["actions"]): r
        for r in x["secondary_action_content"]["pairs"]
    }
    sorted_aids = sorted(action_ids)
    pair_count = 0
    for i, a in enumerate(sorted_aids):
        for b in sorted_aids[i + 1:]:
            blocks, psha = analyze_subset(state_ids, current_sig, original_outcomes, [a, b])
            st = pair_stored[(a, b)]
            if st["operational_blocks"] != blocks or st["operational_partition_sha256"] != psha:
                raise RuntimeError(f"pair mismatch {(a,b)}")
            pair_count += 1

    full_sha = partition_identity(op)
    loo_stored = {r["omitted_action"]: r for r in x["secondary_action_content"]["leave_one_out"]}
    for omitted in sorted_aids:
        subset = [a for a in sorted_aids if a != omitted]
        _, psha = analyze_subset(state_ids, current_sig, original_outcomes, subset)
        if loo_stored[omitted]["operational_partition_sha256"] != psha:
            raise RuntimeError(f"leave-one-out partition mismatch {omitted}")
        if loo_stored[omitted]["full_partition_preserved_by_omission"] != (psha == full_sha):
            raise RuntimeError(f"leave-one-out preservation mismatch {omitted}")

    print(json.dumps({
        "protocol": x["protocol"],
        "root": x["root"],
        "status": "PASS",
        "states": len(state_ids),
        "actions": len(action_ids),
        "native_replay_cells_verified": len(state_ids) * len(action_ids),
        "singleton_contracts_verified": len(action_ids),
        "pair_contracts_verified": pair_count,
        "leave_one_out_verified": len(action_ids),
        "metric_mismatches": 0,
    }, indent=2))


if __name__ == "__main__":
    main()
