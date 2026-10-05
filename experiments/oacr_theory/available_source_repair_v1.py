"""Execute repair from an old exact label and an authorized source interface.

Producer: existing restricted-cut helper and singleton source membership calls.
Verifier: failure enumeration and independent bitset transitive closure.
Toy interface validation, not new graph theory, natural evidence, or a benchmark.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import itertools
import json
import platform
import time
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import contract_budget_audit_v1 as core

Edge = tuple[int, int]
Edges = frozenset[Edge]


@dataclass(frozen=True)
class Contract:
    n: int
    graph: Edges
    actions: Edges
    budget: int


@dataclass(frozen=True)
class SourcePort:
    epoch: str
    permissions: Edges
    budget: int
    membership: Callable[[Edge, str], bool]


@dataclass(frozen=True)
class Decision:
    exact: bool
    label: Edge | None
    queries: tuple[tuple[Edge, bool], ...]
    unresolved: Edges
    reason: str


def source_port(world: Edge | None, permissions: Edges, budget: int,
                epoch: str, observer: list[tuple[Edge, bool]]) -> SourcePort:
    """World is held only in the provider closure, never passed to repair()."""
    def membership(candidate: Edge, requested_epoch: str) -> bool:
        if requested_epoch != epoch:
            raise ValueError("stale source snapshot")
        if candidate not in permissions:
            raise PermissionError("source membership not authorized")
        if len(observer) >= budget:
            raise RuntimeError("source query budget exhausted")
        answer = candidate == world
        observer.append((candidate, answer))
        return answer
    return SourcePort(epoch, permissions, budget, membership)


def active(c: Contract, candidates: Edges) -> Edges:
    return frozenset(e for e in candidates
                     if core.restricted_cut(c.n, c.graph, c.actions, e) <= c.budget)


def repair(stored: Edge | None, old_active: Edges, new_active: Edges,
           source: SourcePort, snapshot: str) -> Decision:
    """Only public compiled metadata, stored label and SourcePort are visible.

    Promise: old exact label and source refer to the same frozen state, which
    contains at most one addition from the declared public candidate universe.
    """
    if stored is not None:
        if stored not in old_active:
            raise ValueError("invalid old exact-label promise")
        return Decision(True, stored if stored in new_active else None,
                        (), frozenset(), "known_state")
    unresolved = set(new_active - old_active)
    if not unresolved:
        return Decision(True, None, (), frozenset(), "no_new_hidden_demand")
    if source.epoch != snapshot:
        return Decision(False, None, (), frozenset(unresolved), "stale_source")
    answers: list[tuple[Edge, bool]] = []
    for candidate in sorted(unresolved):
        if candidate not in source.permissions:
            continue
        if len(answers) >= source.budget:
            break
        answer = source.membership(candidate, snapshot)
        answers.append((candidate, answer))
        unresolved.remove(candidate)
        if answer:
            return Decision(True, candidate, tuple(answers), frozenset(),
                            "positive_unique_addition")
    if unresolved:
        return Decision(False, None, tuple(answers), frozenset(unresolved),
                        "permission_or_budget")
    return Decision(True, None, tuple(answers), frozenset(), "all_demand_negative")


def closure(n: int, edges: Edges) -> tuple[int, ...]:
    """Verifier only: bitset Floyd-Warshall, distinct from producer min-cut."""
    rows = [0] * n
    for u, v in edges:
        rows[u] |= 1 << v
    for k in range(n):
        for u in range(n):
            if rows[u] & (1 << k):
                rows[u] |= rows[k]
    return tuple(rows)


def failures(c: Contract):
    ordered = sorted(c.actions)
    for size in range(c.budget + 1):
        for subset in itertools.combinations(ordered, size):
            yield frozenset(subset)


def behavior(c: Contract, world: Edge | None, counts: Counter):
    augmentation = frozenset() if world is None else frozenset({world})
    result = []
    for failed in failures(c):
        counts["verifier_native_closure_calls"] += 1
        result.append(closure(c.n, (c.graph - failed) | augmentation))
    return tuple(result)


def residual_check(c: Contract, label: Edge | None, world: Edge | None,
                   counts: Counter) -> None:
    """Verify every reachable residual state, without original delta in updater."""
    stack = [(c, label)]
    seen = set()
    while stack:
        state, stored = stack.pop()
        key = (state, stored)
        if key in seen:
            continue
        seen.add(key)
        assert behavior(state, stored, counts) == behavior(state, world, counts)
        counts["residual_state_checks"] += 1
        if state.budget:
            for action in sorted(state.actions):
                graph, actions, budget, post = core.step_rep(
                    state.n, state.graph, state.actions, state.budget, stored, action)
                successor = Contract(state.n, graph, actions, budget)
                # Check against native behavior, not equality to compile_rep(world).
                assert behavior(successor, post, counts) == behavior(successor, world, counts)
                counts["residual_transition_checks"] += 1
                stack.append((successor, post))


def edge_json(e: Edge | None):
    return None if e is None else list(e)


def permission_set(mode: str, candidates: Edges) -> Edges:
    ordered = sorted(candidates)
    if mode == "all":
        return candidates
    if mode == "none":
        return frozenset()
    if mode == "omit_first":
        return frozenset(ordered[1:])
    if mode == "alternating":
        return frozenset(ordered[::2])
    raise ValueError(mode)


def port_enforcement_checks(counts: Counter) -> None:
    tests = [
        (frozenset(), 1, "v1", "v1", PermissionError),
        (frozenset({(0, 2)}), 0, "v1", "v1", RuntimeError),
        (frozenset({(0, 2)}), 1, "v0", "v1", ValueError),
    ]
    for permissions, budget, epoch, requested, error in tests:
        observed = []
        port = source_port((0, 2), permissions, budget, epoch, observed)
        try:
            port.membership((0, 2), requested)
        except error:
            assert not observed
            counts["source_api_enforcement_checks"] += 1
        else:
            raise AssertionError("API failed to enforce capability")
    observed = []
    port = source_port((0, 2), frozenset({(0, 2)}), 1, "v1", observed)
    assert port.membership((0, 2), "v1")
    try:
        port.membership((0, 2), "v1")
    except RuntimeError:
        assert len(observed) == 1
        counts["source_api_enforcement_checks"] += 1
    else:
        raise AssertionError("API failed to enforce depleted budget")


def run(protocol: dict) -> dict:
    counts: Counter = Counter()
    fixture_results = []
    case_rows = []
    wall_start = time.perf_counter()
    phase_seconds = Counter()
    port_enforcement_checks(counts)
    for spec in protocol["fixtures"]:
        graph = frozenset(map(tuple, spec["edges"]))
        candidates = frozenset(map(tuple, spec["candidates"]))
        old = Contract(spec["n"], graph, frozenset(map(tuple, spec["old_actions"])), spec["old_budget"])
        new = Contract(spec["n"], graph, frozenset(map(tuple, spec["new_actions"])), spec["new_budget"])
        assert 0 <= old.budget <= len(old.actions)
        assert 0 <= new.budget <= len(new.actions)
        before_cache = core.restricted_cut.cache_info()
        start = time.perf_counter()
        old_active, new_active = active(old, candidates), active(new, candidates)
        phase_seconds["public_cut_compilation"] += time.perf_counter() - start
        after_cache = core.restricted_cut.cache_info()
        counts["public_cut_requests"] += 2 * len(candidates)
        counts["public_cut_cache_hits"] += after_cache.hits - before_cache.hits
        counts["public_cut_cache_misses"] += after_cache.misses - before_cache.misses
        worlds = [None, *sorted(candidates)]
        # Initial source-backed encoding is outside the repair invocation.
        start = time.perf_counter()
        old_labels = {world: core.compile_rep(old.n, old.graph, old.actions, old.budget, world)
                      for world in worlds}
        counts["initial_source_backed_encodings"] += len(worlds)
        counts["initial_source_delta_reads"] += len(worlds)
        phase_seconds["initial_source_backed_encoding"] += time.perf_counter() - start
        start = time.perf_counter()
        old_behaviors = {world: behavior(old, world, counts) for world in worlds}
        new_behaviors = {world: behavior(new, world, counts) for world in worlds}
        for x, y in itertools.product(worlds, repeat=2):
            assert (old_labels[x] == old_labels[y]) == (old_behaviors[x] == old_behaviors[y])
            counts["old_exact_promise_pair_checks"] += 1
        phase_seconds["native_verification"] += time.perf_counter() - start
        local = Counter()
        residual_verified = set()
        for world, mode, budget, epoch_mode in itertools.product(
                worlds, protocol["permission_modes"], range(len(candidates) + 1),
                protocol["source_epochs"]):
            permission = permission_set(mode, candidates)
            snapshot = "v1"
            epoch = snapshot if epoch_mode == "matching" else "v0"
            observed = []
            port = source_port(world, permission, budget, epoch, observed)
            start = time.perf_counter()
            decision = repair(old_labels[world], old_active, new_active, port, snapshot)
            phase_seconds["online_repair"] += time.perf_counter() - start
            assert tuple(observed) == decision.queries
            assert len(observed) <= budget
            assert all(e in permission for e, _ in observed)
            assert not observed or epoch == snapshot
            assert len({e for e, _ in observed}) == len(observed)
            start = time.perf_counter()
            compatible = [w for w in worlds if old_labels[w] == old_labels[world]
                          and all((w == e) == answer for e, answer in observed)]
            assert world in compatible
            behavior_count = len({new_behaviors[w] for w in compatible})
            if decision.exact:
                assert behavior_count == 1
                assert behavior(new, decision.label, counts) == new_behaviors[world]
                counts["successful_decode_checks"] += 1
                if world not in residual_verified:
                    residual_check(new, decision.label, world, counts)
                    residual_verified.add(world)
                    counts["repaired_world_residual_checks"] += 1
            else:
                assert behavior_count > 1
                assert decision.unresolved
                counts["genuine_ambiguity_checks"] += 1
            if old_labels[world] is not None or not (new_active - old_active):
                assert decision.exact and not observed
                counts["source_free_known_or_no_demand_checks"] += 1
            if (world is None and mode == "all" and epoch_mode == "matching"
                    and budget >= len(new_active - old_active)):
                assert decision.exact
                assert len(observed) == len(new_active - old_active)
                counts["negative_branch_query_bound_checks"] += 1
            phase_seconds["native_verification"] += time.perf_counter() - start
            counts["cases"] += 1
            counts["source_membership_queries"] += len(observed)
            counts["exact" if decision.exact else "unresolved"] += 1
            counts["reason_" + decision.reason] += 1
            local["cases"] += 1
            local["exact" if decision.exact else "unresolved"] += 1
            local["queries"] += len(observed)
            case_rows.append({"fixture": spec["id"], "world": edge_json(world),
                              "stored": edge_json(old_labels[world]), "permissions": mode,
                              "query_budget": budget, "source_epoch": epoch_mode,
                              "status": "EXACT" if decision.exact else "UNRESOLVED",
                              "output_label": edge_json(decision.label), "reason": decision.reason,
                              "queries": [[list(e), answer] for e, answer in observed],
                              "remaining_demand": [list(e) for e in sorted(decision.unresolved)],
                              "compatible_behavior_classes": behavior_count})
        fixture_results.append({"fixture": spec["id"], "old_active": sorted(old_active),
                                "new_active": sorted(new_active),
                                "new_hidden_demand": sorted(new_active - old_active),
                                "counts": dict(sorted(local.items()))})
    return {"protocol_id": protocol["protocol_id"], "counts": dict(sorted(counts.items())),
            "fixture_results": fixture_results, "cases": case_rows,
            "phase_seconds": dict(phase_seconds),
            "wall_seconds": time.perf_counter() - wall_start,
            "producer_native_oracle_calls": 0,
            "unauthorized_stale_or_overbudget_producer_queries": 0,
            "false_exact_or_native_mismatches": 0,
            "initial_source_retention": "not measured; explicit external prerequisite, not free storage",
            "shared_context_storage": "public graph, action banks, candidate universe and two active sets",
            "online_working_storage": "query transcript plus unresolved demand set; linear in candidate count",
            "timing_scope": "single local process; verifier and initial encoding excluded from online phase; no comparative speed claim",
            "claim_boundary": protocol["claim_boundary"]}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, default=Path(__file__).with_suffix(".json"))
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    protocol = json.loads(args.protocol.read_text())
    paths = [args.protocol, Path(__file__), Path(core.__file__)]
    hashes = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}
    result = run(protocol)
    assert hashes == {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}
    result["input_sha256"] = hashes
    result["python"] = platform.python_version()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    ledger = args.out.with_suffix(".cases.json.gz")
    ledger_bytes = gzip.compress(json.dumps(result.pop("cases"), sort_keys=True,
                                             separators=(",", ":")).encode(), mtime=0)
    ledger.write_bytes(ledger_bytes)
    result["case_ledger"] = {"file": ledger.name,
                             "sha256": hashlib.sha256(ledger_bytes).hexdigest(),
                             "rows": result["counts"]["cases"]}
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"out": str(args.out), "counts": result["counts"],
                      "input_sha256": hashes, "wall_seconds": result["wall_seconds"]}, indent=2))


if __name__ == "__main__":
    main()
