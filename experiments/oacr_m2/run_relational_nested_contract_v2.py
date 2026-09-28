"""OACR-M2-R v2: reproducible, order-robust nested-contract analysis."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import sys
from collections import defaultdict
from pathlib import Path
from statistics import median
from typing import Dict, List, Tuple

import networkx as nx

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "common"))

from operational_partition import (  # noqa: E402
    block_index,
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
TOL = 1e-12


def canonical_json(x) -> str:
    return json.dumps(x, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha_obj(x) -> str:
    return hashlib.sha256(canonical_json(x).encode("utf-8")).hexdigest()


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
    remaining = list(selected)
    med = sorted(x["base_rank"] for x in remaining)[(len(remaining) - 1) // 2]
    first = min(
        remaining,
        key=lambda x: (
            abs(x["base_rank"] - med),
            x["base_rank"],
            x["action_id"],
        ),
    )
    order = [first]
    remaining.remove(first)
    while remaining:
        def key(x):
            mind = min(abs(x["base_rank"] - y["base_rank"]) for y in order)
            return (-mind, x["base_rank"], x["action_id"])
        nxt = min(remaining, key=key)
        order.append(nxt)
        remaining.remove(nxt)
    return order


def permutation_order(actions, seed: int):
    prefix = f"OACR-M2-R-V2|{seed}|"
    return sorted(
        actions,
        key=lambda x: (
            hashlib.sha256((prefix + x["action_id"]).encode()).hexdigest(),
            x["action_id"],
        ),
    )


def block_sizes(partition):
    return sorted((len(x) for x in partition), reverse=True)


def partition_assignment(partition, state_ids):
    bi = block_index(partition)
    canonical_blocks = sorted(
        [sorted(block, key=str) for block in partition],
        key=lambda block: [str(x) for x in block],
    )
    ci = {}
    for i, block in enumerate(canonical_blocks):
        for x in block:
            ci[x] = i
    return [ci[s] for s in state_ids]


def is_refinement(fine, coarse) -> bool:
    ci = {}
    for i, block in enumerate(coarse):
        for x in block:
            ci[x] = i
    return all(len({ci[x] for x in block}) == 1 for block in fine)


def approx(a, b, tol=1e-10):
    return abs(float(a) - float(b)) <= tol


def quantiles(values):
    xs = sorted(float(x) for x in values)
    if not xs:
        return {}
    def pick(q):
        if len(xs) == 1:
            return xs[0]
        pos = q * (len(xs) - 1)
        lo = math.floor(pos)
        hi = math.ceil(pos)
        if lo == hi:
            return xs[lo]
        return xs[lo] * (hi - pos) + xs[hi] * (pos - lo)
    return {
        "n": len(xs),
        "min": xs[0],
        "q25": pick(0.25),
        "median": pick(0.5),
        "q75": pick(0.75),
        "max": xs[-1],
    }


def diagnostics(rep_partition, op_partition):
    info = directional_information_gap(rep_partition, op_partition)
    pair = refinement_relation(rep_partition, op_partition)
    h_o = info["operational_entropy_bits"]
    h_r = info["representation_entropy_bits"]
    return {
        **info,
        "representation_blocks": len(rep_partition),
        "under_refinement_count": pair["under_refinement_count"],
        "over_refinement_count": pair["over_refinement_count"],
        "normalized_U_by_HO": (info["omission_U_bits"] / h_o) if h_o > TOL else 0.0,
        "normalized_E_by_HR": (info["excess_E_bits"] / h_r) if h_r > TOL else 0.0,
    }


def transition_summary(chain_rows, rep_names):
    out = {}
    for name in rep_names:
        adequate = [r["k"] for r in chain_rows if r["diagnostics"][name]["omission_U_bits"] <= TOL]
        inadequate = [r["k"] for r in chain_rows if r["diagnostics"][name]["omission_U_bits"] > TOL]
        zero_e = [r["k"] for r in chain_rows if r["diagnostics"][name]["excess_E_bits"] <= TOL]
        exact = [
            r["k"] for r in chain_rows
            if r["diagnostics"][name]["omission_U_bits"] <= TOL
            and r["diagnostics"][name]["excess_E_bits"] <= TOL
        ]
        interval = None
        if exact:
            contiguous = exact == list(range(min(exact), max(exact) + 1))
            interval = [min(exact), max(exact)] if contiguous else None
        out[name] = {
            "first_inadequate_prefix": min(inadequate) if inadequate else None,
            "last_adequate_prefix": max(adequate) if adequate else None,
            "first_zero_excess_prefix": min(zero_e) if zero_e else None,
            "exact_match_prefixes": exact,
            "exact_match_interval": interval,
        }
    return out


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
    for f in sorted(base_edges, key=lambda x: (str(x[0]), str(x[1]))):
        h = g.copy()
        h.remove_edge(*f)
        post = closure_edges(h)
        impact = len(base_closure ^ post)
        ranked.append((impact, str(f[0]), str(f[1]), f))
    ranked.sort()
    selected_tuples = evenly_spaced(ranked, 64)
    actions = []
    for selected_index, t in enumerate(selected_tuples):
        base_rank = ranked.index(t)
        u, v = t[3]
        aid = f"del:{labels[u]}>{labels[v]}"
        actions.append({
            "action_index": selected_index,
            "action_id": aid,
            "base_rank": base_rank,
            "base_deletion_impact": t[0],
            "edge_internal": [str(u), str(v)],
            "edge_label": [labels[u], labels[v]],
            "_edge": (u, v),
        })

    state_specs = [("base", None)] + [
        (f"add:{labels[u]}>{labels[v]}", (u, v)) for u, v in candidates
    ]
    state_ids = [x[0] for x in state_specs]
    state_manifest = [
        {
            "state_index": i,
            "state_id": sid,
            "added_edge": None if added is None else [labels[added[0]], labels[added[1]]],
        }
        for i, (sid, added) in enumerate(state_specs)
    ]

    current_closure_sig = {}
    full_asserted_sig = {}
    support64_sig = {}
    outcome_matrix = {}

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
            str(path_count_dag(st, *a["_edge"])) for a in actions
        )
        rows = []
        for a in actions:
            f = a["_edge"]
            if not st.has_edge(*f):
                raise RuntimeError(f"shared action missing in {state_id}: {f}")
            h = st.copy()
            h.remove_edge(*f)
            post = closure_edges(h)
            rows.append({
                "action_id": a["action_id"],
                "post_closure_sha256": closure_hash(post),
                "post_closure_size": len(post),
            })
        outcome_matrix[state_id] = rows

    rep_signatures = {
        "R0_fixed_current_closure": current_closure_sig,
        "Rfull_fixed_asserted_identity": full_asserted_sig,
        "Rsupport64_fixed_path_counts": {
            s: list(support64_sig[s]) for s in state_ids
        },
    }
    reps = {
        name: partition_from_signatures(state_ids, lambda s, sigs=sigs: sigs[s])
        for name, sigs in rep_signatures.items()
    }

    action_index = {a["action_id"]: a["action_index"] for a in actions}
    action_manifest_public = [
        {k: v for k, v in a.items() if not k.startswith("_")}
        for a in actions
    ]

    def op_partition_for(action_ids):
        idxs = sorted(action_index[a] for a in action_ids)
        return partition_from_signatures(
            state_ids,
            lambda s: (
                current_closure_sig[s],
                tuple(
                    (
                        outcome_matrix[s][i]["action_id"],
                        outcome_matrix[s][i]["post_closure_sha256"],
                        outcome_matrix[s][i]["post_closure_size"],
                    )
                    for i in idxs
                ),
            ),
        )

    canonical_actions = maximin_rank_order(actions)
    canonical_ids = [a["action_id"] for a in canonical_actions]

    ensemble_contracts = {}
    for k in range(65):
        subsets = set()
        for seed in range(64):
            perm = permutation_order(actions, seed)
            subset = tuple(sorted(a["action_id"] for a in perm[:k]))
            subsets.add(subset)
        ensemble_contracts[k] = sorted(subsets)

    analysis_cache = {}

    def analyze_subset(action_ids):
        key = tuple(sorted(action_ids))
        if key in analysis_cache:
            return analysis_cache[key]
        op = op_partition_for(key)
        diag = {name: diagnostics(rep, op) for name, rep in reps.items()}
        row = {
            "contract_id": sha_obj(list(key)),
            "k": len(key),
            "action_ids": list(key),
            "operational_blocks": len(op),
            "operational_block_sizes": block_sizes(op),
            "operational_partition_assignment": partition_assignment(op, state_ids),
            "diagnostics": diag,
        }
        analysis_cache[key] = row
        return row

    canonical_rows = []
    previous_op = None
    refinement_failures = []
    previous_row = None
    for k in range(65):
        row = analyze_subset(canonical_ids[:k])
        op = op_partition_for(canonical_ids[:k])
        if previous_op is not None and not is_refinement(op, previous_op):
            refinement_failures.append(k)
        row = dict(row)
        row["canonical_prefix"] = True
        row["delta_operational_blocks"] = (
            row["operational_blocks"] - previous_row["operational_blocks"]
            if previous_row is not None else 0
        )
        h_o = next(iter(row["diagnostics"].values()))["operational_entropy_bits"]
        prev_h_o = (
            next(iter(previous_row["diagnostics"].values()))["operational_entropy_bits"]
            if previous_row is not None else h_o
        )
        row["delta_operational_entropy_bits"] = h_o - prev_h_o
        for name in reps:
            d = row["diagnostics"][name]
            pd = previous_row["diagnostics"][name] if previous_row is not None else d
            d["delta_U_bits"] = d["omission_U_bits"] - pd["omission_U_bits"]
            d["delta_E_bits"] = d["excess_E_bits"] - pd["excess_E_bits"]
        canonical_rows.append(row)
        previous_op = op
        previous_row = row

    if refinement_failures:
        raise RuntimeError(f"canonical nested refinement failed: {refinement_failures}")

    ensemble_rows = []
    by_k = defaultdict(list)
    for k in range(65):
        for subset in ensemble_contracts[k]:
            row = analyze_subset(subset)
            ensemble_rows.append(row)
            by_k[k].append(row)

    ensemble_summary = []
    for k in range(65):
        rows = by_k[k]
        summary = {
            "k": k,
            "unique_contracts": len(rows),
            "operational_blocks": quantiles([r["operational_blocks"] for r in rows]),
            "operational_entropy_bits": quantiles([
                next(iter(r["diagnostics"].values()))["operational_entropy_bits"]
                for r in rows
            ]),
            "representations": {},
        }
        for name in reps:
            ds = [r["diagnostics"][name] for r in rows]
            summary["representations"][name] = {
                "U_bits": quantiles([d["omission_U_bits"] for d in ds]),
                "E_bits": quantiles([d["excess_E_bits"] for d in ds]),
                "under_refinement_count": quantiles([d["under_refinement_count"] for d in ds]),
                "over_refinement_count": quantiles([d["over_refinement_count"] for d in ds]),
                "adequate_ensemble_fraction": sum(
                    d["omission_U_bits"] <= TOL for d in ds
                ) / len(ds),
                "exact_match_ensemble_fraction": sum(
                    d["omission_U_bits"] <= TOL and d["excess_E_bits"] <= TOL
                    for d in ds
                ) / len(ds),
            }
        ensemble_summary.append(summary)

    end = canonical_rows[-1]
    d0 = end["diagnostics"]["R0_fixed_current_closure"]
    df = end["diagnostics"]["Rfull_fixed_asserted_identity"]
    ds = end["diagnostics"]["Rsupport64_fixed_path_counts"]
    endpoint_ok = (
        end["operational_blocks"] == ENDPOINT["operational_blocks"]
        and approx(d0["omission_U_bits"], ENDPOINT["R0_U"])
        and approx(d0["excess_E_bits"], ENDPOINT["R0_E"])
        and approx(df["omission_U_bits"], ENDPOINT["Rfull_U"])
        and approx(df["excess_E_bits"], ENDPOINT["Rfull_E"])
        and approx(ds["omission_U_bits"], ENDPOINT["Rsupport_U"])
        and approx(ds["excess_E_bits"], ENDPOINT["Rsupport_E"])
    )
    if not endpoint_ok:
        raise RuntimeError("R3 endpoint regression failed")

    weights = {s: 1.0 / len(state_ids) for s in state_ids}
    manifest_hashes = {
        "state_manifest_sha256": sha_obj(state_manifest),
        "action_manifest_sha256": sha_obj(action_manifest_public),
        "representation_signatures_sha256": sha_obj(rep_signatures),
        "outcome_matrix_sha256": sha_obj(outcome_matrix),
        "weights_sha256": sha_obj(weights),
    }

    out = {
        "protocol": "OACR_M2_R_NESTED_CONTRACT_V2",
        "amendment_commit": "6c0e174df46f2a2b9796493a4798e895f649e3f3",
        "source": {
            "raw_sha256": raw_sha,
            "r3_run": 36385544527,
            "r3_checkpoint_commit": "5cc8baf1db8b66061032da6c99723a2956f98121",
        },
        "runtime_manifest": {
            "python": sys.version,
            "platform": platform.platform(),
            "networkx": nx.__version__,
            "github_sha": os.environ.get("GITHUB_SHA"),
        },
        "state_manifest": state_manifest,
        "action_manifest": action_manifest_public,
        "weights": weights,
        "fixed_representation_signatures": rep_signatures,
        "state_action_outcomes": outcome_matrix,
        "manifest_hashes": manifest_hashes,
        "canonical_chain": {
            "rule": "outcome-blind maximin spacing over R3 base deletion-impact ranks",
            "action_order": canonical_ids,
            "trajectory": canonical_rows,
            "transition_summary": transition_summary(canonical_rows, list(reps)),
        },
        "deterministic_permutation_ensemble": {
            "rule": "64 SHA256 action-ID permutations; unique prefix subsets by k",
            "seed_count": 64,
            "summary_by_k": ensemble_summary,
            "contracts": ensemble_rows,
            "interpretation": "deterministic sensitivity ensemble, not a probability sample over all subsets",
        },
        "checks": {
            "canonical_nested_refinement_failures": refinement_failures,
            "endpoint_regression_passed": endpoint_ok,
            "full_contract_operational_blocks": end["operational_blocks"],
        },
    }

    p = Path(args.out)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(out, indent=2))
    print(json.dumps({
        "protocol": out["protocol"],
        "manifest_hashes": manifest_hashes,
        "endpoint_regression_passed": endpoint_ok,
        "transition_summary": out["canonical_chain"]["transition_summary"],
        "ensemble_contract_count": len(ensemble_rows),
    }, indent=2))


if __name__ == "__main__":
    main()
