"""Joint authorized source acquisition and conditional-cut compilation candidate.

No native outcomes, hidden source set, or world enumeration in construct().
The verifier separately enumerates source worlds and native failure behavior.
Classical cut/TR tools are inherited; algorithm novelty is not established here.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import itertools
import json
import time
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from available_source_repair_v1 import Contract, SourcePort, behavior, permission_set
from contract_budget_audit_v1 import restricted_cut
from multi_delta_budget_audit_v1 import compile_multi, step_multi, subsets

Edge = tuple[int, int]
Edges = frozenset[Edge]


@dataclass(frozen=True)
class Decision:
    exact: bool
    stored: Edges
    known: Edges
    transcript: tuple[tuple[Edge, bool], ...]
    remaining: Edges


def port(world: Edges, permissions: Edges, budget: int, observer: list) -> SourcePort:
    def membership(edge: Edge, epoch: str) -> bool:
        if epoch != "v1":
            raise ValueError("snapshot mismatch")
        if edge not in permissions:
            raise PermissionError("unauthorized source query")
        if len(observer) >= budget:
            raise RuntimeError("source budget exhausted")
        answer = edge in world
        observer.append((edge, answer))
        return answer
    return SourcePort("v1", permissions, budget, membership)


def demand(c: Contract, present: Edges, unknown: Edges, counts: Counter) -> Edges:
    counts["demand_cut_requests"] += len(unknown)
    return frozenset(e for e in unknown
                     if restricted_cut(c.n, c.graph | present, c.actions, e) <= c.budget)


def hidden_candidates(old: Contract, candidates: Edges, stored: Edges,
                      counts: Counter) -> Edges:
    counts["old_fiber_cut_requests"] += len(candidates - stored)
    return frozenset(e for e in candidates - stored
                     if restricted_cut(old.n, old.graph | stored, old.actions, e) > old.budget)


def construct(stored: Edges, lost: Edges, new: Contract, source: SourcePort,
              order: str, method: str, counts: Counter) -> Decision:
    """Visible inputs contain no hidden world or native behavior vectors."""
    present, unknown = stored, lost
    transcript = []
    need = demand(new, present, unknown, counts)
    while need:
        allowed = need & source.permissions
        if not allowed or len(transcript) >= source.budget:
            return Decision(False, frozenset(), present, tuple(transcript), need)
        candidate = sorted(allowed, reverse=order == "reverse_lexicographic")[0]
        answer = source.membership(candidate, "v1")
        transcript.append((candidate, answer))
        unknown = unknown - {candidate}
        if answer:
            present = present | {candidate}
        if method == "adaptive_cut":
            need = demand(new, present, unknown, counts)
        elif method == "static_initial_demand":
            need = need - {candidate}
        else:
            raise ValueError(method)
    counts["final_compile_input_edges"] += len(present)
    counts["final_compile_calls"] += 1
    result = compile_multi(new.n, new.graph, new.actions, new.budget, present)
    return Decision(True, result, present, tuple(transcript), frozenset())


def native_behavior(c: Contract, additions: Edges, counts: Counter):
    # Reuse independent bitset verifier with additions baked into its graph;
    # failures are still restricted to named base edges.
    augmented = Contract(c.n, c.graph | additions, c.actions, c.budget)
    return behavior(augmented, None, counts)


def residual_verify(c: Contract, stored: Edges, actual: Edges, counts: Counter):
    stack = [(c, stored)]
    seen = set()
    while stack:
        state, rep = stack.pop()
        if (state, rep) in seen:
            continue
        seen.add((state, rep))
        assert native_behavior(state, rep, counts) == native_behavior(state, actual, counts)
        counts["residual_state_checks"] += 1
        if state.budget:
            for action in sorted(state.actions):
                graph, actions, budget, post = step_multi(
                    state.n, state.graph, state.actions, state.budget, rep, action)
                successor = Contract(state.n, graph, actions, budget)
                assert native_behavior(successor, post, counts) == native_behavior(successor, actual, counts)
                assert post <= rep
                counts["residual_transition_checks"] += 1
                stack.append((successor, post))


def run(protocol: dict):
    counts, summaries, rows, comparisons = Counter(), [], [], Counter()
    started = time.perf_counter()
    for fixture in protocol["fixtures"]:
        graph = frozenset(map(tuple, fixture["graph"]))
        candidates = frozenset(map(tuple, fixture["candidates"]))
        old = Contract(fixture["n"], graph, frozenset(map(tuple, fixture["old_actions"])), fixture["old_budget"])
        new = Contract(fixture["n"], graph, frozenset(map(tuple, fixture["new_actions"])), fixture["new_budget"])
        worlds = tuple(subsets(candidates))
        counts["source_backed_initializations"] += len(worlds)
        old_reps = {b: compile_multi(old.n, old.graph, old.actions, old.budget, b) for b in worlds}
        old_sigs = {b: native_behavior(old, b, counts) for b in worlds}
        new_sigs = {b: native_behavior(new, b, counts) for b in worlds}
        fibers, native_fibers = {}, {}
        for b in worlds:
            fibers.setdefault(old_reps[b], set()).add(b)
            native_fibers.setdefault(old_sigs[b], set()).add(b)
        assert set(map(frozenset, fibers.values())) == set(map(frozenset, native_fibers.values()))
        counts["old_partition_bank_checks"] += 1
        lost_by_rep = {}
        for r, fiber in fibers.items():
            lost = hidden_candidates(old, candidates, r, counts)
            assert {r | u for u in subsets(lost)} == fiber
            lost_by_rep[r] = lost
            counts["old_fiber_characterization_checks"] += 1
        local = {method: Counter() for method in protocol["comparators"]}
        verified_worlds = set()
        for actual, permissions, budget, order in itertools.product(
                worlds, protocol["permissions"], range(len(candidates) + 1), protocol["orders"]):
            r = old_reps[actual]
            permission = permission_set(permissions, candidates)
            decisions = {}
            for method in protocol["comparators"]:
                observed = []
                source = port(actual, permission, budget, observed)
                # Initial source-backed/verifier work must not supply free cached
                # cuts to the producer. Keep only memoization within this call.
                restricted_cut.cache_clear()
                before = restricted_cut.cache_info()
                before_requests = counts["demand_cut_requests"]
                decision = construct(r, lost_by_rep[r], new, source, order, method, counts)
                after = restricted_cut.cache_info()
                assert decision.transcript == tuple(observed)
                assert len(observed) <= budget
                assert all(e in permission for e, _ in observed)
                compatible = [b for b in fibers[r]
                              if all((e in b) == answer for e, answer in observed)]
                classes = len({new_sigs[b] for b in compatible})
                assert actual in compatible
                if decision.exact:
                    assert classes == 1
                    assert native_behavior(new, decision.stored, counts) == new_sigs[actual]
                    assert decision.stored <= actual
                    # Least stored subset verified by native outputs, not cut labels.
                    if actual not in verified_worlds:
                        for alternate in subsets(actual):
                            sufficient = native_behavior(new, alternate, counts) == new_sigs[actual]
                            assert sufficient == (decision.stored <= alternate)
                            counts["native_least_subset_checks"] += 1
                        residual_verify(new, decision.stored, actual, counts)
                        verified_worlds.add(actual)
                        counts["distinct_repaired_world_checks"] += 1
                    counts["exact_native_checks"] += 1
                elif method == "adaptive_cut":
                    assert classes > 1
                    counts["adaptive_genuine_ambiguity_checks"] += 1
                else:
                    counts["static_avoidable_abstentions"] += classes == 1
                if permissions == "all" and budget == len(candidates):
                    assert decision.exact
                    counts["full_permission_budget_completion_checks"] += 1
                if fixture["id"] == "contract_contraction":
                    assert decision.exact and not observed
                    counts["contraction_source_free_checks"] += 1
                local[method]["cases"] += 1
                local[method]["exact" if decision.exact else "unresolved"] += 1
                local[method]["membership_queries"] += len(observed)
                local[method]["demand_cut_requests"] += counts["demand_cut_requests"] - before_requests
                local[method]["cut_cache_misses"] += after.misses - before.misses
                local[method]["cut_cache_hits"] += after.hits - before.hits
                decisions[method] = decision
                rows.append({"fixture": fixture["id"], "actual": sorted(actual),
                             "old_rep": sorted(r), "permissions": permissions, "budget": budget,
                             "order": order, "method": method,
                             "status": "EXACT" if decision.exact else "UNRESOLVED",
                             "stored": sorted(decision.stored), "known_present": sorted(decision.known),
                             "transcript": [[list(e), answer] for e, answer in observed],
                             "compatible_behavior_classes": classes})
            adaptive, static = decisions["adaptive_cut"], decisions["static_initial_demand"]
            comparisons["paired_cases"] += 1
            assert not static.exact or adaptive.exact
            comparisons["adaptive_only_exact"] += adaptive.exact and not static.exact
            if adaptive.exact and static.exact:
                assert adaptive.stored == static.stored
                comparisons["both_exact"] += 1
                comparisons["both_exact_adaptive_queries"] += len(adaptive.transcript)
                comparisons["both_exact_static_queries"] += len(static.transcript)
            if permissions == "all" and budget == len(candidates):
                comparisons["full_budget_pairs"] += 1
                comparisons["full_budget_adaptive_queries"] += len(adaptive.transcript)
                comparisons["full_budget_static_queries"] += len(static.transcript)
        summaries.append({"fixture": fixture["id"], "source_worlds": len(worlds),
                          "old_classes": len(fibers),
                          "methods": {method: dict(sorted(c.items())) for method, c in local.items()}})
    return {"protocol_id": protocol["protocol_id"], "counts": dict(sorted(counts.items())),
            "comparisons": dict(sorted(comparisons.items())), "fixtures": summaries,
            "rows": rows, "wall_seconds": time.perf_counter() - started,
            "producer_native_outcome_calls": 0, "native_or_false_exact_mismatches": 0,
            "unauthorized_or_overbudget_source_calls": 0,
            "cost_scope": protocol["costs"],
            "novelty_status": "working structural specialization; no optimal query policy, total cost superiority, independent review or T2/T5 closure"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, default=Path(__file__).with_suffix(".json"))
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    inputs = [args.protocol, Path(__file__), Path(__file__).with_name("available_source_repair_v1.py"),
              Path(__file__).with_name("contract_budget_audit_v1.py"),
              Path(__file__).with_name("multi_delta_budget_audit_v1.py")]
    pinned = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
    report = run(json.loads(args.protocol.read_text()))
    assert pinned == {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
    ledger_path = args.out.with_suffix(".cases.json.gz")
    ledger_bytes = gzip.compress(json.dumps(report.pop("rows"), sort_keys=True,
                                          separators=(",", ":")).encode(), mtime=0)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    ledger_path.write_bytes(ledger_bytes)
    report["case_ledger"] = {"file": ledger_path.name, "sha256": hashlib.sha256(ledger_bytes).hexdigest()}
    report["input_sha256"] = pinned
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"counts": report["counts"], "comparisons": report["comparisons"],
                      "wall_seconds": report["wall_seconds"], "out": str(args.out)}, indent=2))


if __name__ == "__main__":
    main()
