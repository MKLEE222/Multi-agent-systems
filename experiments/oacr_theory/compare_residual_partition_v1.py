"""Same-input finite-state partition baseline for the budgeted DAG contract.

The baseline observes native outcomes and is explicitly a retrospective semantic
oracle. It is not a predictive constructor. It charges the explicit residual
state expansion rather than giving the baseline outcome functions for free.
All graphs respect the fixed vertex order; this is exhaustive proof debugging
over that bank, not statistical evidence or a novelty certificate.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path

from contract_budget_audit_v1 import compile_rep, step_rep


def subsets(items):
    seq = tuple(sorted(items))
    for k in range(len(seq) + 1):
        for part in itertools.combinations(seq, k):
            yield frozenset(part)


def warshall(n, edges):
    """Independent native observation oracle, not the inherited BFS or flow."""
    rows = [0] * n
    for u, v in edges:
        rows[u] |= 1 << v
    for k in range(n):
        for u in range(n):
            if rows[u] & (1 << k):
                rows[u] |= rows[k]
    return tuple(rows)


def number_blocks(signatures):
    ids = {}
    return [ids.setdefault(sig, len(ids)) for sig in signatures]


def check_contract(n, graph, actions, budget, candidates, counts):
    prefixes = tuple(f for f in subsets(actions) if len(f) <= budget)
    states = tuple((f, e) for f in prefixes for e in candidates)
    index = {state: i for i, state in enumerate(states)}
    alphabet = tuple(sorted(actions))
    # Shared residual context is observable. Illegal actions use a common
    # explicit undefined marker; context observability prevents legal-mask
    # differences from accidentally merging states from different prefixes.
    observations = [(f, warshall(n, (graph - f) | (frozenset({e}) if e else frozenset())))
                    for f, e in states]
    transitions = [tuple(index[(f | {a}, e)] if a not in f and len(f) < budget else None
                         for a in alphabet) for f, e in states]
    labels = number_blocks(observations)
    rounds = 0
    while True:
        refined = number_blocks([(labels[i], tuple(None if dest is None else labels[dest]
                                                   for dest in transitions[i]))
                                 for i in range(len(states))])
        rounds += 1
        if refined == labels:
            break
        labels = refined
    # The classical quotient update table is derived from the final partition.
    quotient_updates = {}
    for i, dests in enumerate(transitions):
        for a, dest in zip(alphabet, dests):
            key = (labels[i], a)
            value = None if dest is None else labels[dest]
            assert key not in quotient_updates or quotient_updates[key] == value
            quotient_updates[key] = value
            if dest is not None:
                counts['baseline_commuting_transitions'] += 1

    compiled = [compile_rep(n, graph - f, actions - f, budget - len(f), e)
                for f, e in states]
    for f in prefixes:
        ids = [index[(f, e)] for e in candidates]
        for i, j in itertools.combinations_with_replacement(ids, 2):
            assert (labels[i] == labels[j]) == (compiled[i] == compiled[j]), (n, graph, actions, budget, f)
            counts['same_context_partition_pairs'] += 1
    for i, (f, e) in enumerate(states):
        for a, dest in zip(alphabet, transitions[i]):
            if dest is None:
                continue
            ge, aa, hh, rep = step_rep(n, graph - f, actions - f, budget - len(f), compiled[i], a)
            assert ge == graph - (f | {a}) and aa == actions - (f | {a})
            assert hh == budget - len(f) - 1 and rep == compiled[dest]
            counts['compiler_commuting_transitions'] += 1
    counts['contracts'] += 1
    counts['expanded_states'] += len(states)
    counts['native_observation_calls'] += len(states)
    counts['residual_contexts'] += len(prefixes)
    counts['quotient_blocks'] += len(set(labels))
    counts['refinement_rounds_including_stability_check'] += rounds
    counts['max_expanded_states_per_contract'] = max(counts['max_expanded_states_per_contract'], len(states))
    counts['max_refinement_rounds'] = max(counts['max_refinement_rounds'], rounds)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--max-n', type=int, default=4, choices=range(2, 6))
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    counts = Counter()
    for n in range(2, args.max_n + 1):
        possible = frozenset((u, v) for u in range(n) for v in range(u + 1, n))
        for graph in subsets(possible):
            counts['order_respecting_dags'] += 1
            current = warshall(n, graph)
            counts['candidate_bank_preparation_closures'] += 1
            deltas = tuple(sorted(e for e in possible - graph if current[e[0]] & (1 << e[1])))
            if not deltas:
                continue
            counts['graphs_with_candidates'] += 1
            candidates = (None,) + deltas
            for actions in subsets(graph):
                counts['graph_action_banks'] += 1
                for budget in range(len(actions) + 1):
                    check_contract(n, graph, actions, budget, candidates, counts)
    report = {
        'protocol': 'OACR_SAME_INPUT_RESIDUAL_PARTITION_BASELINE_V1',
        'verified': True, 'max_nodes': args.max_n,
        'input': '(ordered DAG G, redundant single-edge candidates D=TC(G)-G plus no-addition, deletable A, budget h)',
        'scope': 'synthetic exhaustive semantic comparison; no held-out or natural evidence',
        'baseline': 'native observations + deterministic Moore partition refinement + quotient update table',
        'compiler': 'unchanged restricted-mincut compiler and stored-representation updater',
        'baseline_authority': 'retrospective observation oracle, not a predictive constructor',
        'conclusion': 'same residual partition and executable commuting updates on every enumerated contract',
        'novelty_status': 'semantic object and quotient updates are realized by a standard finite-state baseline; succinct implementation novelty remains unproved',
        'counts': dict(counts),
        'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'inherited_compiler_sha256': hashlib.sha256(Path(__file__).with_name('contract_budget_audit_v1.py').read_bytes()).hexdigest(),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
