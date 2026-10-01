"""Exact tiny-bank query-policy control from permitted public native semantics."""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, deque
from fractions import Fraction
from functools import lru_cache
from pathlib import Path

from adaptive_source_compile_v1 import construct, hidden_candidates, port
from available_source_repair_v1 import Contract, failures
from contract_budget_audit_v1 import restricted_cut
from multi_delta_budget_audit_v1 import compile_multi, subsets


def simulate(c, additions, counts, phase="verification"):
    """Baseline simulator: BFS, no verifier outcomes or Warshall implementation."""
    result = []
    for failed in failures(c):
        counts[phase + "_simulated_native_calls"] += 1
        graph = (c.graph - failed) | additions
        adjacency = [[] for _ in range(c.n)]
        for u, v in graph:
            adjacency[u].append(v)
        relation = []
        for u in range(c.n):
            seen, queue = {u}, deque([u])
            while queue:
                for v in adjacency[queue.popleft()]:
                    if v not in seen:
                        seen.add(v)
                        queue.append(v)
            relation.append(tuple(sorted(seen - {u})))
        result.append(tuple(relation))
    return tuple(result)


def optimal_tree(stored, lost, new, counts):
    candidates = tuple(sorted(lost))
    worlds = tuple(stored | u for u in subsets(lost))
    counts["optimal_policy_hypothesis_states"] += len(worlds)
    # These are computed by the baseline from the same authorized semantics;
    # they are not read from the adaptive experiment's verifier or report.
    targets = [simulate(new, b, counts, phase="policy_compile") for b in worlds]
    positive_masks = [sum(1 << i for i, b in enumerate(worlds) if e in b)
                      for e in candidates]
    choices = {}

    @lru_cache(None)
    def solve(mask):
        counts["optimal_policy_dp_states"] += 1
        labels = {targets[i] for i in range(len(worlds)) if mask & (1 << i)}
        if len(labels) == 1:
            choices[mask] = None
            return Fraction(0)
        best = None
        for j, positive in enumerate(positive_masks):
            yes, no = mask & positive, mask & ~positive
            if not yes or not no:
                continue
            cost = 1 + (yes.bit_count() * solve(yes) + no.bit_count() * solve(no)) / mask.bit_count()
            item = cost, j
            if best is None or item < best:
                best = item
        assert best is not None
        choices[mask] = best[1]
        return best[0]

    initial = (1 << len(worlds)) - 1
    expectation = solve(initial)

    def execute(source):
        mask, queries = initial, 0
        known = stored
        while choices[mask] is not None:
            j = choices[mask]
            answer = source.membership(candidates[j], "v1")
            if answer:
                known = known | {candidates[j]}
            queries += 1
            mask &= positive_masks[j] if answer else ~positive_masks[j]
        labels = {targets[i] for i in range(len(worlds)) if mask & (1 << i)}
        assert len(labels) == 1
        rep = compile_multi(new.n, new.graph, new.actions, new.budget, known)
        return queries, next(iter(labels)), rep

    return worlds, expectation, execute


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, default=Path(__file__).with_suffix(".json"))
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    protocol = json.loads(args.protocol.read_text())
    fixture_path = args.protocol.with_name(protocol["fixture_protocol"])
    original = json.loads(fixture_path.read_text())
    pin_paths = [args.protocol, fixture_path, Path(__file__),
                 Path(__file__).with_name("adaptive_source_compile_v1.py"),
                 Path(__file__).with_name("available_source_repair_v1.py"),
                 Path(__file__).with_name("contract_budget_audit_v1.py"),
                 Path(__file__).with_name("multi_delta_budget_audit_v1.py")]
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in pin_paths}
    counts, output, total = Counter(), [], Counter()
    for f in original["fixtures"]:
        graph, candidates = frozenset(map(tuple, f["graph"])), frozenset(map(tuple, f["candidates"]))
        old = Contract(f["n"], graph, frozenset(map(tuple, f["old_actions"])), f["old_budget"])
        new = Contract(f["n"], graph, frozenset(map(tuple, f["new_actions"])), f["new_budget"])
        actuals = tuple(subsets(candidates))
        old_labels = {b: compile_multi(old.n, old.graph, old.actions, old.budget, b) for b in actuals}
        policies = {}
        local = Counter()
        for r in set(old_labels.values()):
            lost = hidden_candidates(old, candidates, r, counts)
            restricted_cut.cache_clear()
            worlds, expectation, execute = optimal_tree(r, lost, new, counts)
            assert set(worlds) == {b for b in actuals if old_labels[b] == r}
            counts["optimal_source_fibers"] += 1
            total_realized = 0
            for actual in worlds:
                observations = []
                source = port(actual, candidates, len(candidates), observations)
                queries, target, rep = execute(source)
                assert queries == len(observations)
                assert target == simulate(new, actual, counts)
                assert target == simulate(new, rep, counts)
                total_realized += queries
                counts["optimal_native_decode_checks"] += 1
                local["optimal_queries"] += queries
            assert Fraction(total_realized, len(worlds)) == expectation
            policies[r] = lost
        for actual in actuals:
            r = old_labels[actual]
            for order in protocol["greedy_orders"]:
                observed = []
                restricted_cut.cache_clear()
                source = port(actual, candidates, len(candidates), observed)
                decision = construct(r, policies[r], new, source, order, "adaptive_cut", counts)
                assert decision.exact
                assert simulate(new, decision.stored, counts) == simulate(new, actual, counts)
                local[order + "_queries"] += len(observed)
                counts["adaptive_native_decode_checks"] += 1
        local["worlds"] = len(actuals)
        for order in protocol["greedy_orders"]:
            assert local["optimal_queries"] <= local[order + "_queries"]
        total.update(local)
        output.append({"fixture": f["id"], **dict(local)})
    assert hashes == {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in pin_paths}
    report = {"protocol_id": protocol["protocol_id"], "fixtures": output,
              "totals": dict(total), "counts": dict(counts), "input_sha256": hashes,
              "source_worlds_are_dependent_development_cases": True,
              "simulation_is_permitted_computation": True,
              "cost_reporting_correction": "After the first control run, separated policy-compilation simulation calls from replay calls and checked the controller's physical stored subset. Fixtures, prior, DP objective, greedy policies and query choices unchanged; rerun is development verification, not independent confirmation.",
              "optimality_scope": "expected singleton membership queries under the declared artificial uniform fiber prior; excludes policy compilation cost",
              "conclusion": "greedy structural acquisition is correct but has no query-optimality or total-cost advantage established; full simulation is a valid charged same-information control"}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"out": str(args.out), "fixtures": output, "totals": dict(total),
                      "counts": dict(counts)}, indent=2))


if __name__ == "__main__":
    main()
