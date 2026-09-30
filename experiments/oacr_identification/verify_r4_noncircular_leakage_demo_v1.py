"""Independent verifier for OACR R4 non-circular leakage demonstration."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import networkx as nx


def qid(uri: str) -> str:
    return uri.rsplit("/", 1)[-1]


def tc(g: nx.DiGraph):
    if not nx.is_directed_acyclic_graph(g):
        raise RuntimeError("expected DAG")
    return set(nx.transitive_closure_dag(g).edges())


def make_partition(items, key):
    buckets = {}
    for item in items:
        buckets.setdefault(key(item), []).append(item)
    return list(buckets.values())


def h_cond(a_part, b_part, items):
    ai = {x: i for i, block in enumerate(a_part) for x in block}
    bi = {x: i for i, block in enumerate(b_part) for x in block}
    n = len(items)
    joint = {}
    btot = {}
    for x in items:
        j = (ai[x], bi[x])
        joint[j] = joint.get(j, 0) + 1
        btot[bi[x]] = btot.get(bi[x], 0) + 1
    value = 0.0
    for (_, b), count in joint.items():
        p = count / n
        value -= p * math.log2(count / btot[b])
    return value


def op_key(result, state):
    rows = result["original_state_action_outcomes"][state]
    return tuple(
        (a, rows[a]["post_closure_sha256"], rows[a]["post_closure_size"])
        for a in sorted(rows)
    )


def rep_partition(states, retained):
    keep = set(retained)
    return make_partition(
        states,
        lambda s: ("keep", s) if s in keep else ("base",),
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--artifact-dir", required=True)
    ap.add_argument("--producer-result", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    root = Path(args.artifact_dir)
    native = json.loads((root / "result.json").read_text(encoding="utf-8"))
    combined = json.loads((root / "combined.json").read_text(encoding="utf-8"))
    producer = json.loads(Path(args.producer_result).read_text(encoding="utf-8"))

    errors = []

    def require(cond, msg):
        if not cond:
            errors.append(msg)

    states = [x["state_id"] for x in native["state_manifest"]]
    aug = [s for s in states if s != "base"]

    # Verification-only operational partition and oracle.
    op = make_partition(states, lambda s: op_key(native, s))
    base_key = op_key(native, "base")
    oracle = {s for s in aug if op_key(native, s) != base_key}

    # Reconstruct predictive set independently from raw base graph and action manifest.
    edges = set()
    for row in combined["results"]["bindings"]:
        if "child" not in row or "parent" not in row:
            continue
        c = qid(row["child"]["value"])
        p = qid(row["parent"]["value"])
        if c != p:
            edges.add((c, p))

    g = nx.DiGraph()
    g.add_edges_from(edges)
    root_qid = native["root"]["qid"]
    if root_qid in g:
        component = nx.node_connected_component(g.to_undirected(), root_qid)
        g = g.subgraph(component).copy()

    require(nx.is_directed_acyclic_graph(g), "base graph not DAG")

    base_after = {}
    if nx.is_directed_acyclic_graph(g):
        for action in native["action_manifest"]:
            edge = tuple(action["edge"])
            h = g.copy()
            h.remove_edge(*edge)
            base_after[action["action_id"]] = tc(h)

    state_edge = {
        row["state_id"]: (
            None if row["added_edge"] is None else tuple(row["added_edge"])
        )
        for row in native["state_manifest"]
    }

    predictive = set()
    inactive = []
    if base_after:
        for s in aug:
            e = state_edge[s]
            active = any(
                e not in base_after[a["action_id"]]
                for a in native["action_manifest"]
            )
            if active:
                predictive.add(s)
            else:
                inactive.append(s)

    sham = set(sorted(inactive)[: len(predictive)])

    expected_sets = {
        "A0_outcome_oracle": oracle,
        "A2_contract_predictive": predictive,
        "A2_matched_inactive_sham": sham,
    }

    recomputed = {}
    for name, retained in expected_sets.items():
        part = rep_partition(states, retained)
        u = h_cond(op, part, states)
        e = h_cond(part, op, states)
        recomputed[name] = {
            "retained_records": len(retained),
            "retained_state_ids": sorted(retained),
            "representation_blocks": len(part),
            "U_bits": u,
            "E_bits": e,
            "exact": abs(u) < 1e-12 and abs(e) < 1e-12,
        }

    require(producer.get("source_artifact_id") == 11003190307, "artifact id")
    require(producer.get("states") == 272, "state count")
    require(producer.get("actions") == 64, "action count")
    require(producer.get("operational_blocks") == 23, "operational blocks")
    require(producer.get("oracle_equals_predictive") is True, "oracle/predictive flag")
    require(producer.get("predictive_equals_frozen_active_ids") is True, "predictive/frozen flag")
    require(producer.get("sham_overlap_with_predictive") == 0, "sham overlap")
    require(oracle == predictive, "oracle and predictive sets differ")
    require(predictive == set(native["active_state_ids"]), "predictive set differs from frozen active set")
    require(len(sham & predictive) == 0, "sham overlaps predictive")

    stored = producer["constructors"]
    for name, row in recomputed.items():
        got = stored.get(name)
        require(got is not None, f"missing constructor {name}")
        if got is None:
            continue
        require(got["retained_records"] == row["retained_records"], f"{name} retained count")
        require(got["retained_state_ids"] == row["retained_state_ids"], f"{name} retained set")
        require(got["representation_blocks"] == row["representation_blocks"], f"{name} blocks")
        require(abs(got["U_bits"] - row["U_bits"]) < 1e-12, f"{name} U")
        require(abs(got["E_bits"] - row["E_bits"]) < 1e-12, f"{name} E")
        require(got["exact"] == row["exact"], f"{name} exact")

    require(recomputed["A0_outcome_oracle"]["exact"], "oracle not exact")
    require(recomputed["A2_contract_predictive"]["exact"], "predictive not exact")
    require(not recomputed["A2_matched_inactive_sham"]["exact"], "sham unexpectedly exact")
    require(
        recomputed["A2_contract_predictive"]["retained_records"]
        == recomputed["A2_matched_inactive_sham"]["retained_records"],
        "predictive/sham cost mismatch",
    )
    require(
        recomputed["A2_contract_predictive"]["representation_blocks"]
        == recomputed["A2_matched_inactive_sham"]["representation_blocks"],
        "predictive/sham block-count mismatch",
    )

    report = {
        "protocol": "OACR_R4_NONCIRCULAR_LEAKAGE_VERIFY_V1",
        "verified": not errors,
        "error_count": len(errors),
        "errors": errors[:40],
        "oracle_equals_predictive": oracle == predictive,
        "predictive_equals_frozen_active_ids":
            predictive == set(native["active_state_ids"]),
        "sham_overlap_with_predictive": len(sham & predictive),
        "recomputed": recomputed,
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))

    if errors:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
