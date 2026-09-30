"""Executable anti-circularity demonstration on the frozen OACR R4 building artifact.

Inputs expected under --artifact-dir:
  combined.json
  result.json

The script compares three same-cost representation constructors:
  A0 outcome oracle: reads realized evaluation outcomes.
  A2 contract predictive: reads only the base graph, candidate deltas, frozen deletion
      contract, and native reachability semantics.
  A2 matched inactive sham: retains the same number of structurally inactive deltas
      and never reads evaluation outcome labels.

The substantive claim is not that oracle repair cannot be exact. It can be exact
trivially. The claim is that exactness has confirmatory force only when constructor
choices were frozen without adaptive use of realized evaluation outcomes.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import networkx as nx


def qid(uri: str) -> str:
    return uri.rsplit("/", 1)[-1]


def closure_edges(g: nx.DiGraph):
    if not nx.is_directed_acyclic_graph(g):
        raise RuntimeError("expected DAG")
    return set(nx.transitive_closure_dag(g).edges())


def partition_from_labels(items, label_fn):
    blocks = {}
    for item in items:
        blocks.setdefault(label_fn(item), []).append(item)
    return list(blocks.values())


def op_signature(result, state_id):
    rows = result["original_state_action_outcomes"][state_id]
    return tuple(
        (
            action_id,
            rows[action_id]["post_closure_sha256"],
            rows[action_id]["post_closure_size"],
        )
        for action_id in sorted(rows)
    )


def conditional_entropy(a_part, b_part, items):
    """H(A | B) for finite uniform items."""
    a_index = {x: i for i, block in enumerate(a_part) for x in block}
    b_index = {x: i for i, block in enumerate(b_part) for x in block}
    n = len(items)
    joint = {}
    b_count = {}
    for x in items:
        joint[(a_index[x], b_index[x])] = joint.get((a_index[x], b_index[x]), 0) + 1
        b_count[b_index[x]] = b_count.get(b_index[x], 0) + 1
    h = 0.0
    for (_, b), count in joint.items():
        p = count / n
        h -= p * math.log2(count / b_count[b])
    return h


def rep_partition(state_ids, retained):
    retained = set(retained)
    return partition_from_labels(
        state_ids,
        lambda s: ("delta", s) if s in retained else ("base",),
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--artifact-dir", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    root = Path(args.artifact_dir)
    result = json.loads((root / "result.json").read_text(encoding="utf-8"))
    combined = json.loads((root / "combined.json").read_text(encoding="utf-8"))

    state_ids = [x["state_id"] for x in result["state_manifest"]]
    augmented = [s for s in state_ids if s != "base"]
    actions = result["action_manifest"]

    # Verification-only target.
    op_part = partition_from_labels(
        state_ids, lambda s: op_signature(result, s)
    )
    base_sig = op_signature(result, "base")

    # A0: direct use of realized evaluation outcomes.
    oracle = {
        s for s in augmented
        if op_signature(result, s) != base_sig
    }

    # A2: reconstruct active deltas using only base graph + frozen contract.
    edges = set()
    for row in combined["results"]["bindings"]:
        if "child" in row and "parent" in row:
            child = qid(row["child"]["value"])
            parent = qid(row["parent"]["value"])
            if child != parent:
                edges.add((child, parent))

    graph = nx.DiGraph()
    graph.add_edges_from(edges)
    root_qid = result["root"]["qid"]
    if root_qid in graph:
        nodes = nx.node_connected_component(graph.to_undirected(), root_qid)
        graph = graph.subgraph(nodes).copy()

    if not nx.is_directed_acyclic_graph(graph):
        raise RuntimeError(
            "artifact unexpectedly cyclic; accepted building carrier should be a DAG"
        )

    base_after = {}
    for action in actions:
        edge = tuple(action["edge"])
        h = graph.copy()
        h.remove_edge(*edge)
        base_after[action["action_id"]] = closure_edges(h)

    state_edge = {
        row["state_id"]: (
            tuple(row["added_edge"]) if row["added_edge"] is not None else None
        )
        for row in result["state_manifest"]
    }

    predictive = set()
    structurally_inactive = []
    for state_id in augmented:
        edge = state_edge[state_id]
        active = any(
            edge not in base_after[action["action_id"]]
            for action in actions
        )
        if active:
            predictive.add(state_id)
        else:
            structurally_inactive.append(state_id)

    # Matched-cost sham chosen only from contract-inactive structural candidates.
    sham = set(sorted(structurally_inactive)[: len(predictive)])

    constructors = {
        "A0_outcome_oracle": oracle,
        "A2_contract_predictive": predictive,
        "A2_matched_inactive_sham": sham,
    }

    rows = {}
    for name, retained in constructors.items():
        rep_part = rep_partition(state_ids, retained)
        u_bits = conditional_entropy(op_part, rep_part, state_ids)
        e_bits = conditional_entropy(rep_part, op_part, state_ids)
        rows[name] = {
            "retained_records": len(retained),
            "retained_state_ids": sorted(retained),
            "representation_blocks": len(rep_part),
            "U_bits": u_bits,
            "E_bits": e_bits,
            "exact": abs(u_bits) < 1e-12 and abs(e_bits) < 1e-12,
        }

    payload = {
        "protocol": "OACR_R4_NONCIRCULAR_LEAKAGE_DEMO_V1",
        "source_artifact_id": 11003190307,
        "source_workflow_run": 36438278451,
        "states": len(state_ids),
        "actions": len(actions),
        "operational_blocks": len(op_part),
        "constructors": rows,
        "oracle_equals_predictive": oracle == predictive,
        "predictive_equals_frozen_active_ids":
            predictive == set(result["active_state_ids"]),
        "sham_overlap_with_predictive": len(sham & predictive),
        "authority_interpretation": {
            "A0_outcome_oracle":
                "Reads realized evaluation outcomes; exactness demonstrates only ex-post encodability.",
            "A2_contract_predictive":
                "Uses base graph, candidate deltas, frozen deletion contract, and native reachability semantics; no augmented-state outcome labels.",
            "A2_matched_inactive_sham":
                "Same retained-record cost as predictive constructor; selects structurally contract-inactive deltas and uses no evaluation outcome labels.",
        },
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    print(json.dumps(
        {
            name: {
                key: row[key]
                for key in (
                    "retained_records",
                    "representation_blocks",
                    "U_bits",
                    "E_bits",
                    "exact",
                )
            }
            for name, row in rows.items()
        },
        indent=2,
    ))


if __name__ == "__main__":
    main()
