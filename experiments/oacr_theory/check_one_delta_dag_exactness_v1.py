"""Exhaustive finite sanity check for the OACR one-delta DAG exactness theorem.

Enumerates all topologically labelled DAGs through n=5, all nonempty singleton-
deletion action panels over each graph's base edges, and all currently redundant
one-edge delta states. It checks the theorem-predicted operational partition:
base + inactive deltas form one class; every active delta is a singleton class.

This is proof debugging, not a substitute for the theorem proof.
"""

from __future__ import annotations

import itertools
import json
from pathlib import Path

import networkx as nx


def tc(g: nx.DiGraph):
    return set(nx.transitive_closure_dag(g).edges())


def verify_n(n: int):
    possible = [(i, j) for i in range(n) for j in range(i + 1, n)]
    checked_contracts = 0
    dags_with_candidates = 0

    for mask in range(1 << len(possible)):
        g = nx.DiGraph()
        g.add_nodes_from(range(n))
        edges = [
            possible[k]
            for k in range(len(possible))
            if (mask >> k) & 1
        ]
        g.add_edges_from(edges)

        closure = tc(g)
        candidates = sorted(closure - set(edges))
        if not candidates or not edges:
            continue

        dags_with_candidates += 1

        for action_mask in range(1, 1 << len(edges)):
            actions = [
                edges[k]
                for k in range(len(edges))
                if (action_mask >> k) & 1
            ]
            checked_contracts += 1

            base_after = {}
            for f in actions:
                h = g.copy()
                h.remove_edge(*f)
                base_after[f] = tc(h)

            active = {
                e
                for e in candidates
                if any(e not in base_after[f] for f in actions)
            }

            signatures = [
                tuple(frozenset(base_after[f]) for f in actions)
            ]
            for e in candidates:
                rows = []
                for f in actions:
                    h = g.copy()
                    h.add_edge(*e)
                    h.remove_edge(*f)
                    rows.append(frozenset(tc(h)))
                signatures.append(tuple(rows))

            base_sig = signatures[0]

            for idx, e in enumerate(candidates, start=1):
                if e in active:
                    if signatures[idx] == base_sig:
                        return {
                            "ok": False,
                            "n": n,
                            "reason": "active_equals_base",
                            "edges": edges,
                            "actions": actions,
                            "candidate": e,
                        }
                else:
                    if signatures[idx] != base_sig:
                        return {
                            "ok": False,
                            "n": n,
                            "reason": "inactive_differs_from_base",
                            "edges": edges,
                            "actions": actions,
                            "candidate": e,
                        }

            active_rows = [
                (idx, e)
                for idx, e in enumerate(candidates, start=1)
                if e in active
            ]
            for (i, e), (j, e2) in itertools.combinations(active_rows, 2):
                if signatures[i] == signatures[j]:
                    return {
                        "ok": False,
                        "n": n,
                        "reason": "active_collision",
                        "edges": edges,
                        "actions": actions,
                        "candidate_a": e,
                        "candidate_b": e2,
                    }

    return {
        "ok": True,
        "n": n,
        "checked_contracts": checked_contracts,
        "dags_with_redundant_candidates": dags_with_candidates,
    }


def main():
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    rows = [verify_n(n) for n in range(2, 6)]
    ok = all(row["ok"] for row in rows)
    total = sum(row.get("checked_contracts", 0) for row in rows)

    report = {
        "protocol": "OACR_ONE_DELTA_DAG_EXHAUSTIVE_SANITY_V1",
        "max_n": 5,
        "verified": ok,
        "total_contract_instances": total,
        "rows": rows,
        "interpretation":
            "Proof-debugging finite enumeration only; not a substitute for proof.",
    }

    p = Path(args.out)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))

    if not ok:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
