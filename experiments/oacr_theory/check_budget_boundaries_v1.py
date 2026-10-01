"""Small scope regressions for the budgeted deletion theorem.

Constructor uses the inherited flow code; native comparison uses a bitset
Warshall implementation here. This is same-author proof debugging, not an
independent review or a natural-data experiment.
"""
from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

from contract_budget_audit_v1 import compile_rep, restricted_cut, step_rep


def closure(n, edges):
    rows = [0] * n
    for u, v in edges:
        rows[u] |= 1 << v
    for k in range(n):
        for u in range(n):
            if rows[u] & (1 << k):
                rows[u] |= rows[k]
    return tuple(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    graph = frozenset({(0, 1), (1, 2), (2, 3)})
    action = (1, 2)
    actions = frozenset({action})
    first, second = (0, 2), (0, 3)
    assert restricted_cut(4, graph, actions, first) == 1
    assert restricted_cut(4, graph, actions, second) == 1
    full = [tuple(closure(4, (graph - failure) | {e})
                  for failure in (frozenset(), actions)) for e in (first, second)]
    assert full[0] != full[1]
    partial = [tuple(bool(rows[0] & (1 << 3)) for rows in signature) for signature in full]
    assert partial[0] == partial[1] == (True, True)
    # Full-observation exactness does not persist when output is restricted.
    assert compile_rep(4, graph, actions, 1, first) != compile_rep(4, graph, actions, 1, second)

    # Independent delta identities over-refine the existing multi-delta witness.
    for failure in (frozenset(), actions):
        assert closure(4, (graph - failure) | {first}) == closure(4, (graph - failure) | {first, second})

    diamond = frozenset({(0, 1), (1, 3), (0, 2), (2, 3)})
    delta = (0, 3)
    assert compile_rep(4, diamond, diamond, 1, delta) is None
    assert compile_rep(4, diamond, diamond, 2, delta) == delta
    order_checks = 0
    # Enumerate complete legal two-deletion histories. Initial active identity
    # may be dropped as the budget is consumed; updater only sees stored state.
    for history in itertools.permutations(sorted(diamond), 2):
        g, a, h = diamond, diamond, 2
        stored = compile_rep(4, g, a, h, delta)
        for action in history:
            g, a, h, stored = step_rep(4, g, a, h, stored, action)
            assert stored == compile_rep(4, g, a, h, delta)
            assert closure(4, g | ({stored} if stored else set())) == closure(4, g | {delta})
            order_checks += 1
    report = {
        "protocol": "OACR_BUDGET_SCOPE_REGRESSIONS_V1",
        "scope": "synthetic same-author proof debugging; existing boundaries, no new empirical authority",
        "verified": True,
        "partial_output": {"observed_pair": [0, 3], "two_distinct_full_classes_merge": True},
        "multi_delta": {"independent_activity_overrefines": True, "existing_witness_regression": True},
        "contract_expansion": {"H1_erases_delta": True, "H2_requires_source_witness": True},
        "ordered_history_step_checks": order_checks,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
