"""Conditional mincuts for multiple persistent additions in an acyclic carrier.

This candidate is a direct specialization of classical transitive reduction and
restricted mincut. It closes a naive componentwise boundary, not the novelty
gate. Independent Warshall outcomes and subset enumeration verify the compiler.
Only base edges fail; additions persist; the output is the full reachability
relation. The graph, action bank, budget and per-state addition witness are inputs.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path

from contract_budget_audit_v1 import restricted_cut


def subsets(items):
    seq = tuple(sorted(items))
    for k in range(len(seq) + 1):
        for part in itertools.combinations(seq, k):
            yield frozenset(part)


def closure(n, edges):
    rows = [0] * n
    for u, v in edges:
        rows[u] |= 1 << v
    for k in range(n):
        for u in range(n):
            if rows[u] & (1 << k):
                rows[u] |= rows[k]
    return tuple(rows)


def compile_multi(n, graph, actions, budget, additions):
    if not actions <= graph or not 0 <= budget <= len(actions) or additions & graph:
        raise ValueError('invalid multi-addition contract')
    edges = graph | additions
    if n < 2 or any(not (0 <= u < n and 0 <= v < n and u != v) for u, v in edges):
        raise ValueError('invalid vertices')
    degree, successors = [0] * n, [[] for _ in range(n)]
    for u, v in edges:
        degree[v] += 1
        successors[u].append(v)
    ready = [u for u in range(n) if degree[u] == 0]
    visited = 0
    while ready:
        u = ready.pop()
        visited += 1
        for v in successors[u]:
            degree[v] -= 1
            if degree[v] == 0:
                ready.append(v)
    if visited != n:
        raise ValueError('augmented graph must remain acyclic')
    # The inherited restricted_cut validates acyclicity of each augmentation.
    # Every other persistent addition has nondeletable capacity. Unlike the
    # failed independent gate, it is present when testing the necessity of e.
    return frozenset(e for e in additions
                     if restricted_cut(n, graph | (additions - {e}), actions, e) <= budget)


def step_multi(n, graph, actions, budget, stored, action):
    if budget <= 0 or action not in actions:
        raise ValueError('illegal residual action')
    g, a, h = graph - {action}, actions - {action}, budget - 1
    return g, a, h, compile_multi(n, g, a, h, stored)


def check_bank(n, graph, candidates, counts):
    states = tuple(subsets(candidates))
    for actions in subsets(graph):
        failures = tuple(subsets(actions))
        for budget in range(len(actions) + 1):
            counts['contracts'] += 1
            panel = tuple(f for f in failures if len(f) <= budget)
            reps = [compile_multi(n, graph, actions, budget, b) for b in states]
            signatures = [tuple(closure(n, (graph - f) | b) for f in panel) for b in states]
            rep_to_sig, sig_to_rep = {}, {}
            for b, r, sig in zip(states, reps, signatures):
                assert r not in rep_to_sig or rep_to_sig[r] == sig
                assert sig not in sig_to_rep or sig_to_rep[sig] == r
                rep_to_sig[r], sig_to_rep[sig] = sig, r
                counts['state_partition_checks'] += 1
                assert compile_multi(n, graph, actions, budget, r) == r
                counts['compiler_idempotence_checks'] += 1
                # Exact subset minimality is independently checked against
                # native outcomes, including all alternative stored subsets.
                for c in subsets(b):
                    sufficient = tuple(closure(n, (graph - f) | c) for f in panel) == sig
                    assert sufficient == (r <= c), ('least generator', n, graph, actions, budget, b, r, c)
                    counts['subset_minimality_checks'] += 1
                for f in panel:
                    assert closure(n, (graph - f) | r) == closure(n, (graph - f) | b)
                    actual = compile_multi(n, graph - f, actions - f, budget - len(f), b)
                    maintained = compile_multi(n, graph - f, actions - f, budget - len(f), r)
                    assert actual == maintained and actual <= r
                    counts['native_decoder_checks'] += 1
                    counts['residual_no_resurrection_checks'] += 1
                    if len(f) < budget:
                        for action in actions - f:
                            g, a, h, next_rep = step_multi(n, graph - f, actions - f, budget - len(f), maintained, action)
                            assert next_rep == compile_multi(n, g, a, h, b)
                            counts['commuting_residual_updates'] += 1
            counts['exact_partitions'] += 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--max-n', type=int, default=4, choices=range(2, 5))
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    counts = Counter()
    for n in range(2, args.max_n + 1):
        possible = frozenset((u, v) for u in range(n) for v in range(u + 1, n))
        for graph in subsets(possible):
            counts['order_respecting_dags'] += 1
            current = closure(n, graph)
            candidates = frozenset(e for e in possible - graph if current[e[0]] & (1 << e[1]))
            if not candidates:
                continue
            counts['graphs_with_candidates'] += 1
            check_bank(n, graph, candidates, counts)
    graph = frozenset({(0, 1), (1, 2), (2, 3)})
    actions = frozenset({(1, 2)})
    first, second = (0, 2), (0, 3)
    assert compile_multi(4, graph, actions, 1, frozenset({first})) == frozenset({first})
    assert compile_multi(4, graph, actions, 1, frozenset({first, second})) == frozenset({first})
    try:
        compile_multi(3, frozenset(), frozenset(), 0,
                      frozenset((u, v) for u in range(3) for v in range(3) if u != v))
    except ValueError:
        pass
    else:
        raise AssertionError('cyclic simultaneous redundancy must be rejected')
    report = {
        'protocol': 'OACR_MULTI_DELTA_CONDITIONAL_CUT_AUDIT_V1',
        'verified': True, 'max_nodes': args.max_n,
        'assumptions': ['acyclic augmented graph', 'only base edges are deletable',
                        'all subsets of deletable base edges up to h are legal',
                        'persistent additions', 'full reachability observation',
                        'statewise addition witness available at initial compilation'],
        'scope': 'same-author synthetic proof debugging, not independent or natural confirmation',
        'constructor': 'per-addition restricted mincut conditioned on every other persistent addition',
        'verifier': 'Warshall reachability + every legal failure set + every stored subset',
        'counts': dict(counts),
        'existing_interaction_witness_resolved': True,
        'cyclic_input_rejected': True,
        'novelty_status': 'classical transitive-reduction/mincut specialization; T2/T5 remain open',
        'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'inherited_flow_source_sha256': hashlib.sha256(Path(__file__).with_name('contract_budget_audit_v1.py').read_bytes()).hexdigest(),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
