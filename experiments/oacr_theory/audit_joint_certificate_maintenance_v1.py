"""Fixed development audit. Hidden additions appear only in this verifier.

No sealed natural evaluation and no model/API calls. Literal BFS and failure
enumeration independently check native behavior and every proof conclusion.
"""
from __future__ import annotations

import argparse
from collections import Counter, deque
from dataclasses import replace
import hashlib
import itertools
import json
from pathlib import Path
import random

from available_source_repair_v1 import SourcePort
from ordered_source_compile_v1 import Proof, support_proof
from joint_certificate_maintenance_v1 import (
    METHODS, bundle_sizes, check_dag, contract_token, counted_flow, initialize, update,
)


def subsets(edges, cap=None):
    edges = sorted(edges)
    for size in range(len(edges)+1 if cap is None else min(cap, len(edges))+1):
        for chosen in itertools.combinations(edges, size):
            yield frozenset(chosen)


def literal_bfs(n, edges):
    adjacency = [[] for _ in range(n)]
    for u, v in edges:
        adjacency[u].append(v)
    relation = set()
    for start in range(n):
        queue, seen = deque([start]), {start}
        while queue:
            u = queue.popleft()
            for v in adjacency[u]:
                if v not in seen:
                    seen.add(v)
                    queue.append(v)
        relation.update((start, v) for v in seen if v != start)
    return frozenset(relation)


def native_check(state, actual, counts, canonical):
    panel = list(subsets(state.actions, state.budget))
    output = {}
    for failed in panel:
        observed = literal_bfs(state.n, state.graph-failed | state.stored)
        reference = literal_bfs(state.n, state.graph-failed | actual)
        assert observed == reference
        assert set(state.nodes) <= observed
        output[failed] = observed
        counts["native_failure_pairs"] += 1
        counts["native_virtual_edge_checks"] += len(state.nodes)
    assert check_dag(state)
    counts["standalone_certificate_states"] += 1
    if canonical:
        for edge in state.stored:
            witnesses = [failed for failed in panel
                         if literal_bfs(state.n, state.graph-failed | (state.stored-{edge})) != output[failed]]
            assert witnesses
            counts["native_retained_necessity_witnesses"] += 1


def initial(n, graph, actions, h, known, unknown, actual, counts):
    observed = []
    def membership(edge, epoch):
        assert epoch == "joint_v1" and edge in unknown
        assert edge not in [e for e, _ in observed]
        answer = edge in actual
        observed.append((edge, answer))
        return answer
    state, transcript = initialize(n, graph, actions, h, known, unknown,
                                  SourcePort("joint_v1", unknown, len(unknown), membership),
                                  "joint_v1", counts)
    assert transcript == tuple(observed)
    return state


def bank(seed):
    # Exact inherited bank-generation rule, including RNG call order.
    rng = random.Random(seed)
    for case in range(60):
        n = 5 + case % 4
        edges = [(u, v) for u in range(n) for v in range(u+1, n)]
        rng.shuffle(edges)
        unknown = frozenset(edges[:1+case % 5])
        rest = edges[len(unknown):]
        graph = frozenset(e for e in rest if rng.randrange(3))
        known = frozenset(e for e in rest if e not in graph and rng.randrange(2))
        deletable = sorted(graph)
        rng.shuffle(deletable)
        actions = frozenset(deletable[:min(5, len(graph))])
        h = min(case % 3, len(actions))
        for extra in subsets(unknown):
            yield case, n, graph, actions, h, known, unknown, known | extra


def trajectories(initial_state):
    stack = [(initial_state, (), {method: initial_state for method in METHODS},
              {method: bundle_sizes(initial_state)["bundle_bytes"] for method in METHODS})]
    return stack


def process(state, actual, audit_counts, method_counts, comparisons, digest, case_id):
    stack = trajectories(state)
    while stack:
        anchor, history, states, peaks = stack.pop()
        canonical_outputs = [states[m].stored for m in METHODS if m != "persistent_flat"]
        assert all(rep == canonical_outputs[0] for rep in canonical_outputs)
        a, b = states["substitution_dag"], states["generic_dependency_dag"]
        assert a.nodes == b.nodes and a.stored == b.stored
        comparisons["candidate_generic_identical_proof_states"] += 1
        for method, current in states.items():
            native_check(current, actual, audit_counts, method != "persistent_flat")
            sizes = bundle_sizes(current)
            for name, value in sizes.items():
                method_counts[method]["state_sum_"+name] += value
                method_counts[method]["state_max_"+name] = max(method_counts[method]["state_max_"+name], value)
            method_counts[method]["state_observations"] += 1
        if not anchor.budget:
            for method in METHODS:
                method_counts[method]["terminal_peak_sum_bundle_bytes"] += peaks[method]
                method_counts[method]["terminal_trajectories"] += 1
        digest.update(json.dumps([case_id, history, sorted(a.stored),
                                 [[e, p.paths] for e, p in sorted(a.nodes.items())]],
                                separators=(",", ":")).encode()+b"\n")
        audit_counts["history_states"] += 1
        for action in sorted(anchor.actions) if anchor.budget else []:
            new_states, new_peaks, transition_cost = {}, {}, {}
            for method in METHODS:
                local = Counter()
                successor, sizes = update(states[method], action, method, "joint_v1",
                                          contract_token(states[method]), local)
                method_counts[method].update(local)
                new_states[method] = successor
                new_peaks[method] = max(peaks[method], sizes["bundle_bytes"])
                transition_cost[method] = local["bounded_flow_requests"]
            comparisons["transitions"] += 1
            comparisons["candidate_generic_flow_ties"] += int(
                transition_cost["substitution_dag"] == transition_cost["generic_dependency_dag"])
            comparisons["candidate_dependency_flat_flow_savings"] += (
                transition_cost["dependency_flat"]-transition_cost["substitution_dag"])
            comparisons["candidate_cold_flat_flow_savings"] += (
                transition_cost["cold_flat"]-transition_cost["substitution_dag"])
            stack.append((new_states["substitution_dag"], history+(action,), new_states, new_peaks))


def mechanism_cases():
    for length in (4, 6, 8, 12):
        n = length+2
        graph = frozenset({(i, i+1) for i in range(length-1)} | {(length, length+1)})
        actions = frozenset({(0, 1), (length, length+1)})
        known = frozenset({(0, j) for j in range(2, length-1)})
        unknown = frozenset({(0, length-1)})
        for extra in (frozenset(), unknown):
            yield length, n, graph, actions, known, unknown, known | extra, (length, length+1)


def attacks():
    state = initial(6, frozenset({(0,1),(1,2),(2,3),(4,5)}),
                    frozenset({(0,1),(4,5)}), 1, frozenset({(0,2)}),
                    frozenset({(0,3)}), frozenset({(0,2)}), Counter())
    new, _ = update(state, (4,5), "substitution_dag", "joint_v1", contract_token(state), Counter())
    assert not new.stored and check_dag(new)
    reject = {}
    def invalid(name, nodes):
        assert not check_dag(replace(new, nodes=nodes))
        reject[name] = True
    invalid("dangling_literal", {(0,3): new.nodes[(0,3)]})
    invalid("missing_dependency", {(0,2): new.nodes[(0,2)]})
    invalid("self_reference", {**new.nodes, (0,2): Proof("paths", paths=((0,2),))})
    invalid("two_node_cycle", {**new.nodes, (0,2): Proof("paths", paths=((0,3,2),))})
    invalid("under_supported", {**new.nodes, (0,2): Proof("paths", paths=())})
    # At h=1 duplicating the base chain illegally shares the deletable 0->1.
    invalid_initial = replace(state, stored=frozenset(),
                              nodes={(0,2): Proof("paths", paths=((0,1,2),(0,1,2))),
                                     (0,3): Proof("paths", paths=((0,2,3),(0,2,3)))})
    assert not check_dag(invalid_initial)
    reject["shared_deletable_edge"] = True
    for name, action, epoch, token, start in (
        ("stale_epoch", (4,5), "different", contract_token(state), state),
        ("wrong_predecessor", (4,5), "joint_v1", "bad", state),
        ("illegal_action", (1,2), "joint_v1", contract_token(state), state),
        ("exhausted_budget", (0,1), "joint_v1", contract_token(new), new),
    ):
        try:
            update(start, action, "substitution_dag", epoch, token, Counter())
        except ValueError:
            reject[name] = True
        else:
            raise AssertionError(name)
    return {"rejected": reject,
            "counterexample_repaired": {"new_stored": sorted(new.stored),
                                         "proof_nodes": [[e, p.paths] for e,p in sorted(new.nodes.items())],
                                         "sizes": bundle_sizes(new)}}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    root = Path(__file__).parent
    protocol_path = root / "joint_certificate_maintenance_v1.json"
    protocol = json.loads(protocol_path.read_text())
    inputs = [Path(__file__), protocol_path, root/"joint_certificate_maintenance_v1.py",
              root/"ordered_source_compile_v1.py", root/"available_source_repair_v1.py",
              root/"contract_budget_audit_v1.py"]
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
    audit_counts, init_counts, comparison = Counter(), Counter(), Counter()
    methods = {m: Counter() for m in METHODS}
    digest, graph_ids = hashlib.sha256(), set()
    for case, n, graph, actions, h, known, unknown, actual in bank(20261002):
        # Check the counted primitive against inherited producer paths/cuts.
        for edge in sorted(known | unknown):
            a = counted_flow(n, graph, actions, h, edge, Counter())
            b = support_proof(n, graph, actions, h, edge, Counter())
            assert a == b
            audit_counts["counted_flow_regressions"] += 1
        state = initial(n, graph, actions, h, known, unknown, actual, init_counts)
        process(state, actual, audit_counts, methods, comparison, digest,
                ["inherited", case, sorted(actual)])
        graph_ids.add(case)
        audit_counts["source_worlds"] += 1
    assert len(graph_ids) == 60 and audit_counts["source_worlds"] == 744
    stress = []
    for length, n, graph, actions, known, unknown, actual, action in mechanism_cases():
        state = initial(n, graph, actions, 1, known, unknown, actual, init_counts)
        row = {"chain_vertices": length, "unknown_present": bool(actual & unknown),
               "initial_bundle_bytes": bundle_sizes(state)["bundle_bytes"], "methods": {}}
        for method in METHODS:
            local = Counter()
            new, sizes = update(state, action, method, "joint_v1", contract_token(state), local)
            native_check(new, actual, audit_counts, method != "persistent_flat")
            row["methods"][method] = {"counts": dict(local), "sizes": sizes}
        stress.append(row)
    result = {"protocol_id": protocol["protocol_id"], "parent_commit": protocol["parent_commit"],
              "input_sha256": hashes, "audit_counts": dict(audit_counts),
              "shared_initialization": dict(init_counts), "methods": {m: dict(c) for m,c in methods.items()},
              "comparisons": dict(comparison), "mechanism_cases": stress,
              "attacks": attacks(), "ledger_sha256": digest.hexdigest(),
              "verdict": "Joint correctness checked on declared development histories; generic proof-DAG reuse matches candidate. No independent novelty, natural evidence or production full-cost superiority established."}
    assert hashes == {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    print(json.dumps({"audit_counts": result["audit_counts"], "comparisons": result["comparisons"],
                      "flows": {m: c["bounded_flow_requests"] for m,c in methods.items()},
                      "ledger_sha256": result["ledger_sha256"], "verdict": result["verdict"]}, indent=2))


if __name__ == "__main__":
    main()
