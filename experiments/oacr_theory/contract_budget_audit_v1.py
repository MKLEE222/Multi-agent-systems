"""OACR core audit: repairability, native replay, and budgeted deletion contracts.

Reference constructor: restricted min-cut using Edmonds-Karp.
Independent verification: enumerate legal failure sets and execute BFS reachability.
No model, benchmark, evaluation data, or third-party package is imported.
This is proof debugging, not a claim of new graph theory or empirical replication.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from collections import Counter, deque
from functools import lru_cache
from pathlib import Path
from typing import Hashable, Iterable

Edge = tuple[int, int]
Edges = frozenset[Edge]


def powerset(items: Iterable[Edge]):
    seq = tuple(sorted(items))
    for k in range(len(seq) + 1):
        for combo in itertools.combinations(seq, k):
            yield frozenset(combo)


@lru_cache(maxsize=200000)
def native_closure(n: int, edges: Edges) -> Edges:
    """Independent native oracle: BFS from each vertex, not flow code."""
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
    out = set()
    for source in range(n):
        seen = {source}
        queue = deque([source])
        while queue:
            u = queue.popleft()
            for v in adj[u]:
                if v not in seen:
                    seen.add(v)
                    queue.append(v)
        out.update((source, v) for v in seen if v != source)
    return frozenset(out)


def validate(n: int, edges: Edges, deletable: Edges, delta: Edge) -> None:
    if n < 2 or not deletable <= edges or delta in edges:
        raise ValueError('invalid base/deletion/delta specification')
    if any(not (0 <= u < n and 0 <= v < n and u != v) for u, v in edges | {delta}):
        raise ValueError('invalid vertex or self loop')
    # Both the base and its possible augmentation must remain DAGs.
    deg = [0] * n
    adj = [[] for _ in range(n)]
    for u, v in edges | {delta}:
        deg[v] += 1
        adj[u].append(v)
    queue = deque(i for i in range(n) if deg[i] == 0)
    visited = 0
    while queue:
        u = queue.popleft()
        visited += 1
        for v in adj[u]:
            deg[v] -= 1
            if deg[v] == 0:
                queue.append(v)
    if visited != n:
        raise ValueError('augmentation must preserve acyclicity')


@lru_cache(maxsize=200000)
def restricted_cut(n: int, edges: Edges, deletable: Edges, delta: Edge) -> float:
    """Minimum allowed base-edge deletions disconnecting delta endpoints.

    Returns infinity if no subset of deletable can disconnect them, and zero
    if they are already disconnected. No augmented-state outcome is queried.
    Nondeletable edges get capacity |A|+1, strictly above any legal cut budget.
    """
    validate(n, edges, deletable, delta)
    source, target = delta
    cap = [[0] * n for _ in range(n)]
    sentinel = len(deletable) + 1
    for u, v in edges:
        cap[u][v] = 1 if (u, v) in deletable else sentinel
    value = 0
    while True:
        parent = [-1] * n
        parent[source] = source
        queue = deque([source])
        while queue and parent[target] < 0:
            u = queue.popleft()
            for v in range(n):
                if parent[v] < 0 and cap[u][v] > 0:
                    parent[v] = u
                    queue.append(v)
                    if v == target:
                        break
        if parent[target] < 0:
            return float(value)
        add = sentinel
        v = target
        while v != source:
            u = parent[v]
            add = min(add, cap[u][v])
            v = u
        v = target
        while v != source:
            u = parent[v]
            cap[u][v] -= add
            cap[v][u] += add
            v = u
        value += add
        if value >= sentinel:
            return math.inf


def compile_rep(n: int, edges: Edges, deletable: Edges, budget: int,
                delta: Edge | None) -> Edge | None:
    """Compile from an available per-state delta witness, not from lost data."""
    if not 0 <= budget <= len(deletable):
        raise ValueError('budget outside the residual contract')
    if delta is None:
        return None
    return delta if restricted_cut(n, edges, deletable, delta) <= budget else None


def step_rep(n: int, edges: Edges, deletable: Edges, budget: int,
             stored: Edge | None, action: Edge):
    """Execute one legal deletion using ONLY stored representation + shared base.

    There is no access to a forgotten delta in this updater.
    """
    if budget <= 0 or action not in deletable:
        raise ValueError('action not legal under the residual contract')
    post_edges = edges - {action}
    post_actions = deletable - {action}
    post_budget = budget - 1
    post_rep = compile_rep(n, post_edges, post_actions, post_budget, stored)
    return post_edges, post_actions, post_budget, post_rep


def labels_equal(a: list[Hashable], b: list[Hashable]) -> bool:
    return all((a[i] == a[j]) == (b[i] == b[j])
               for i in range(len(a)) for j in range(len(a)))


def conditional_entropy(a, b) -> float:
    joint = Counter(zip(a, b))
    counts = Counter(b)
    n = len(a)
    return sum(-(c / n) * math.log2(c / counts[y]) for (_, y), c in joint.items())


def factorable(view, target) -> bool:
    seen = {}
    for v, t in zip(view, target):
        if v in seen and seen[v] != t:
            return False
        seen[v] = t
    return True


def attacks():
    rows = []
    coarse, target = [0, 0], [0, 1]
    repairs = list(itertools.product(range(2), repeat=1))
    assert not any(labels_equal([r[0], r[0]], target) for r in repairs)
    assert factorable([(0, 0), (0, 1)], target)
    rows.append({'id': 'A1_LOST_DISTINCTION', 'counterexample_verified': True,
                 'result': 'coarse-only repair impossible; statewise witness restores feasibility'})

    # U=E=0 is a partition statement, not validation of a chosen decoder.
    rep, outcome, swapped_decode_outcome = [0, 1], [0, 1], [1, 0]
    assert conditional_entropy(outcome, rep) == conditional_entropy(rep, outcome) == 0
    assert all(x != y for x, y in zip(outcome, swapped_decode_outcome))
    rows.append({'id': 'A2_DECODER_NOT_CERTIFIED_BY_PARTITION', 'counterexample_verified': True,
                 'partition_U_E': [0, 0], 'native_replay_mismatches': 2})

    # Two crossing partitions can have under- and over-refinement simultaneously.
    rep, outcome = [0, 0, 1, 1], [0, 1, 0, 1]
    assert conditional_entropy(outcome, rep) == conditional_entropy(rep, outcome) == 1
    rows.append({'id': 'A3_INCOMPARABLE_PARTITIONS', 'counterexample_verified': True,
                 'U_bits': 1, 'E_bits': 1})

    # An H=1 equivalence is not necessarily congruent under reusing H=1.
    transition = [1, 2, 2, 4, 5, 5]
    obs = [0, 0, 0, 0, 0, 1]
    sig = lambda x, h: tuple(obs[iterate(transition, x, k)] for k in range(h + 1))
    assert sig(0, 1) == sig(3, 1)
    assert sig(transition[0], 1) != sig(transition[3], 1)
    assert sig(transition[0], 0) == sig(transition[3], 0)
    rows.append({'id': 'A4_HORIZON_RESET', 'counterexample_verified': True,
                 'result': 'H equivalence maps to residual H-1, not automatically to H'})

    # Identical perfect predictions can still merge different output behaviors.
    gold = ['yes', 'yes']
    states = [['yes', 'no'], ['no', 'yes']]
    acc = [sum(a == b for a, b in zip(gold, s)) / 2 for s in states]
    assert acc == [0.5, 0.5] and states[0] != states[1]
    rows.append({'id': 'A5_ACCURACY_IS_NOT_BEHAVIOR_QUOTIENT', 'counterexample_verified': True,
                 'accuracy': acc})

    # A perfect non-adaptive simulator can reconstruct Q, without reading stored Y.
    frozen_simulator = lambda x: (x * x + 1) % 2
    inputs = list(range(4))
    simulated = [frozen_simulator(x) for x in inputs]
    labels = [1, 0, 1, 0]
    assert simulated == labels
    rows.append({'id': 'A6_FREEZE_IS_NOT_ALGORITHM_NOVELTY', 'counterexample_verified': True,
                 'result': 'no stored-outcome access alone does not rule out full simulation'})

    # A contract extension can require information safely discarded earlier.
    n = 4
    graph = frozenset({(0, 1), (1, 3), (0, 2), (2, 3)})
    delta = (0, 3)
    assert restricted_cut(n, graph, graph, delta) == 2
    assert compile_rep(n, graph, graph, 1, delta) is None
    assert compile_rep(n, graph, graph, 2, delta) == delta
    assert native_closure(n, (graph - {(0, 1), (0, 2)}) | {delta}) != native_closure(n, graph - {(0, 1), (0, 2)})
    rows.append({'id': 'A7_CONTRACT_EXPANSION_NEEDS_REACQUISITION', 'counterexample_verified': True,
                 'lambda': 2, 'stored_at_H1': None, 'required_at_H2': list(delta)})
    return rows


def iterate(transition, x, k):
    for _ in range(k):
        x = transition[x]
    return x


def check_graph(n: int, edges: Edges, counts: Counter):
    deltas = sorted(native_closure(n, edges) - edges)
    if not deltas:
        return
    counts['graphs_with_candidates'] += 1
    states = [None] + deltas
    for actions in powerset(edges):
        counts['graph_action_banks'] += 1
        failures = list(powerset(actions))
        cuts = {e: restricted_cut(n, edges, actions, e) for e in deltas}
        # Independent oracle for each lambda: enumerate deletions and BFS.
        for e in deltas:
            brute = min((len(f) for f in failures if e not in native_closure(n, edges - f)), default=math.inf)
            assert cuts[e] == brute, ('cut', n, edges, actions, e, cuts[e], brute)
            counts['mincut_vs_bruteforce_pairs'] += 1
        for h in range(len(actions) + 1):
            counts['budgeted_contracts'] += 1
            panel = [f for f in failures if len(f) <= h]
            sigs = [tuple(native_closure(n, (edges - f) | ({e} if e else set())) for f in panel) for e in states]
            reps = [compile_rep(n, edges, actions, h, e) for e in states]
            assert labels_equal(reps, sigs), ('quotient', n, edges, actions, h)
            counts['exact_quotients'] += 1
            for e, r in zip(states, reps):
                for f in panel:
                    native = native_closure(n, (edges - f) | ({e} if e else set()))
                    decoded = native_closure(n, (edges - f) | ({r} if r else set()))
                    assert native == decoded
                    counts['native_decode_replays'] += 1
                # Every one-step square on every bank, including nonredundant
                # residual candidates, is checked below through each prefix F.
                for f in panel:
                    residual_edges, residual_actions = edges - f, actions - f
                    residual_h = h - len(f)
                    actual = compile_rep(n, residual_edges, residual_actions, residual_h, e)
                    from_stored = compile_rep(n, residual_edges, residual_actions, residual_h, r)
                    assert actual == from_stored, ('no resurrection', e, r, f, h)
                    counts['residual_no_resurrection_checks'] += 1
                if h:
                    for action in actions:
                        ge, aa, hh, updated = step_rep(n, edges, actions, h, r, action)
                        actual = compile_rep(n, ge, aa, hh, e)
                        assert updated == actual
                        counts['commuting_update_squares'] += 1


def partition_exhaustive():
    checked = 0
    for view in itertools.product(range(2), repeat=4):
        for target in itertools.product(range(2), repeat=4):
            existence = any(labels_equal([mapping[v] for v in view], list(target))
                            for mapping in itertools.product(range(2), repeat=2))
            assert existence == factorable(view, target)
            checked += 1
    return checked


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--max-n', type=int, default=4, choices=range(2, 6))
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    counts = Counter()
    for n in range(2, args.max_n + 1):
        possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
        for graph in powerset(possible):
            counts['labelled_dags_enumerated'] += 1
            check_graph(n, graph, counts)
    report = {
        'protocol': 'OACR_CORE_BUDGET_AND_REPAIRABILITY_AUDIT_V1',
        'scope': 'synthetic exhaustive proof debugging, NOT natural or held-out evidence',
        'max_nodes': args.max_n,
        'verified': True,
        'counterexamples': attacks(),
        'factorization_cases': partition_exhaustive(),
        'checks': dict(counts),
        'constructor': 'restricted min-cut, classical max-flow; no augmented native outcome input',
        'verifier': 'failure-set enumeration + independent BFS reachability',
        'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
