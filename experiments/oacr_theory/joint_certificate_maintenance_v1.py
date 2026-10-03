"""Joint physical-representation / proof maintenance in the inherited DAG model.

This is a bounded candidate and classical proof-substitution control, not a
novelty-cleared algorithm. Update never receives the source or hidden additions.
"""
from __future__ import annotations

from collections import Counter, deque
from dataclasses import dataclass, replace
import hashlib
import json
import time

from ordered_source_compile_v1 import (
    Proof, compile_from_source, topological_rank, transport_paths,
)

METHODS = ("cold_flat", "dependency_flat", "substitution_dag",
           "generic_dependency_dag", "persistent_flat")


@dataclass(frozen=True)
class Maintained:
    n: int
    graph: frozenset[tuple[int, int]]
    actions: frozenset[tuple[int, int]]
    budget: int
    universe: frozenset[tuple[int, int]]
    negatives: frozenset[tuple[int, int]]
    stored: frozenset[tuple[int, int]]
    nodes: dict[tuple[int, int], Proof]
    rank: dict[int, int]
    epoch: str
    step: int = 0


def order(state, edges):
    return sorted(edges, key=lambda e: (state.rank[e[1]] - state.rank[e[0]],
                                        state.rank[e[0]], state.rank[e[1]]))


def contract_token(state):
    payload = [state.n, sorted(state.graph), sorted(state.actions), state.budget,
               sorted(state.stored), state.epoch, state.step]
    return hashlib.sha256(json.dumps(payload, separators=(",", ":")).encode()).hexdigest()


def dependency_index(nodes, counts=None):
    index = {}
    for target, proof in sorted(nodes.items()):
        for path in proof.paths:
            for edge in zip(path, path[1:]):
                if counts is not None:
                    counts["index_path_edge_visits"] += 1
                index.setdefault(edge, set()).add(target)
    return {edge: frozenset(targets) for edge, targets in index.items()}


def bundle_sizes(state, index=None):
    """Actual compact UTF-8 JSON bytes, not Python RSS or physical optimality."""
    if index is None:
        index = dependency_index(state.nodes)
    rep = sorted(state.stored)
    proofs = [[edge, proof.paths] for edge, proof in sorted(state.nodes.items())]
    deps = [[edge, sorted(targets)] for edge, targets in sorted(index.items())]
    metadata = {"n": state.n, "graph": sorted(state.graph),
                "actions": sorted(state.actions), "budget": state.budget,
                "universe": sorted(state.universe), "negatives": sorted(state.negatives),
                "rank": sorted(state.rank.items()), "epoch": state.epoch,
                "step": state.step, "contract_token": contract_token(state)}
    payload = {"representation": rep, "proofs": proofs, "index": deps, "metadata": metadata}
    sizes = {name + "_bytes": len(json.dumps(value, separators=(",", ":")).encode())
             for name, value in payload.items()}
    sizes["bundle_bytes"] = len(json.dumps(payload, separators=(",", ":")).encode())
    sizes["stored_additions"] = len(state.stored)
    sizes["proof_nodes"] = len(state.nodes)
    sizes["proof_path_edges"] = sum(len(path)-1 for proof in state.nodes.values() for path in proof.paths)
    return sizes


def check_dag(state, counts=None, prefix="checker"):
    """Standalone local checker: no flow, source, or native behavior oracle.

    A virtual edge means robust reachability proved by another node. Universal
    quantification over the SAME remaining failure set permits substitution.
    """
    if counts is None:
        counts = Counter()
    physical = state.graph | state.stored
    if not state.actions <= state.graph or not 0 <= state.budget <= len(state.actions):
        return False
    if state.stored & state.graph or state.negatives & state.stored:
        return False
    if not state.stored | state.negatives <= state.universe:
        return False
    if set(state.nodes) != state.universe - state.negatives - state.stored:
        return False
    try:
        topological_rank(state.n, state.graph | state.universe)
    except ValueError:
        return False
    done, visiting = set(), set()

    def visit(edge):
        if edge in done:
            return True
        if edge in visiting or edge not in state.nodes or edge in physical:
            return False
        counts[prefix + "_nodes"] += 1
        visiting.add(edge)
        proof = state.nodes[edge]
        if proof.kind != "paths" or proof.source_side or len(proof.paths) != state.budget + 1:
            return False
        used = Counter()
        for path in proof.paths:
            if not path or path[0] != edge[0] or path[-1] != edge[1] or len(set(path)) != len(path):
                return False
            if any(not 0 <= v < state.n for v in path):
                return False
            for support in zip(path, path[1:]):
                counts[prefix + "_path_edge_visits"] += 1
                if support in physical:
                    if support in state.actions:
                        used[support] += 1
                elif not visit(support):
                    return False
        if any(value > 1 for value in used.values()):
            return False
        visiting.remove(edge)
        done.add(edge)
        return True

    return all(visit(edge) for edge in sorted(state.nodes))


def counted_flow(n, edges, actions, h, edge, counts):
    """Same classical bounded Edmonds--Karp primitive for every comparator.

    Extra counters count the implemented matrix/BFS work, not intrinsic lower
    bounds. No graph size compression is restricted for other algorithms.
    """
    counts["bounded_flow_requests"] += 1
    counts["flow_network_edges"] += len(edges)
    counts["flow_matrix_cells"] += 2*n*n
    source, target = edge
    if edge in edges or not actions <= edges or not 0 <= h <= len(actions):
        raise ValueError("invalid support test")
    capacity = [[0]*n for _ in range(n)]
    for u, v in edges:
        capacity[u][v] = 1 if (u, v) in actions else h+1
    residual = [row[:] for row in capacity]
    value = 0
    while value <= h:
        parent = [-1]*n
        parent[source] = source
        queue = deque([source])
        while queue and parent[target] < 0:
            u = queue.popleft()
            for v in range(n):
                counts["flow_bfs_arc_inspections"] += 1
                if parent[v] < 0 and residual[u][v] > 0:
                    parent[v] = u
                    queue.append(v)
        if parent[target] < 0:
            return Proof("cut", source_side=frozenset(i for i, p in enumerate(parent) if p >= 0))
        add, v = h+1-value, target
        while v != source:
            u = parent[v]
            add, v = min(add, residual[u][v]), u
        v = target
        while v != source:
            u = parent[v]
            residual[u][v] -= add
            residual[v][u] += add
            v = u
        value += add
        counts["augmentations"] += 1
    flow = {(u, v): capacity[u][v]-residual[u][v] for u, v in edges}
    paths = []
    for _ in range(h+1):
        u, path = source, [source]
        while u != target:
            v = min(v for a, v in edges if a == u and flow[(a, v)] > 0)
            flow[(u, v)] -= 1
            path.append(v)
            u = v
        paths.append(tuple(path))
    assert not any(flow.values())
    return Proof("paths", paths=tuple(paths))


def initialize(n, graph, actions, budget, known, unknown, source, epoch, counts):
    result = compile_from_source(n, graph, actions, budget, known, unknown, source, epoch, counts)
    if not result.exact:
        raise ValueError("initial representation unresolved")
    state = Maintained(n, graph, actions, budget, known | unknown,
                       frozenset(e for e, answer in result.transcript if not answer),
                       result.stored,
                       {r.edge: r.proof for r in result.receipts if r.proof.kind == "paths"},
                       topological_rank(n, graph | known | unknown), epoch)
    if not check_dag(state):
        raise AssertionError("invalid initial proof state")
    return state, result.transcript


def canonicalize(state, counts):
    stored, dropped = frozenset(), {}
    for edge in order(state, state.stored):
        proof = counted_flow(state.n, state.graph | stored, state.actions,
                             state.budget, edge, counts)
        if proof.kind == "paths":
            dropped[edge] = proof
        else:
            stored |= {edge}
    return stored, dropped


def update(state, action, method, epoch, expected_token, counts):
    """No source object/callback is accepted. It cannot reacquire source bits."""
    start = time.perf_counter()
    if method not in METHODS:
        raise ValueError("unknown method")
    if state.epoch != epoch or expected_token != contract_token(state):
        raise ValueError("stale epoch or wrong predecessor contract")
    if state.budget <= 0 or action not in state.actions:
        raise ValueError("action outside remaining contract")
    if not check_dag(state, counts, "input_checker"):
        raise ValueError("invalid predecessor certificate")
    post = replace(state, graph=state.graph-{action}, actions=state.actions-{action},
                   budget=state.budget-1, step=state.step+1)
    if method == "persistent_flat":
        stored, dropped = state.stored, {}
    else:
        stored, dropped = canonicalize(post, counts)
    counts["dropped_additions"] += len(dropped)
    transported = {}
    for edge, proof in state.nodes.items():
        counts["transport_path_edge_visits"] += sum(len(p)-1 for p in proof.paths)
        transported[edge] = transport_paths(proof, action)
    new_nodes = {}
    physical = post.graph | stored
    roots = post.universe - post.negatives - stored
    if method == "cold_flat":
        for edge in order(post, roots):
            proof = counted_flow(post.n, physical, post.actions, post.budget, edge, counts)
            assert proof.kind == "paths"
            new_nodes[edge] = proof
    elif method in ("dependency_flat", "persistent_flat"):
        new_nodes.update(dropped)
        for edge, proof in transported.items():
            leaf_edges = {e for p in proof.paths for e in zip(p, p[1:])}
            counts["flat_support_edge_checks"] += sum(len(p)-1 for p in proof.paths)
            if leaf_edges <= physical:
                new_nodes[edge] = proof
            else:
                counts["invalidated_flat_nodes"] += 1
                replacement = counted_flow(post.n, physical, post.actions, post.budget, edge, counts)
                assert replacement.kind == "paths"
                new_nodes[edge] = replacement
    elif method == "substitution_dag":
        # Bind each removed concrete support to its own robust proof. Existing
        # path nodes become compositional nodes; no literal-path flattening.
        new_nodes = dict(transported)
        new_nodes.update(dropped)
        for edge, targets in dependency_index(transported, counts).items():
            if edge in dropped:
                counts["rebound_dependency_links"] += len(targets)
    elif method == "generic_dependency_dag":
        # Separate generic bottom-up justification construction. Local premises
        # are current concrete edges or an already established earlier lemma.
        available = dict(dropped)
        for edge in order(post, roots):
            proof = available.get(edge, transported.get(edge))
            assert proof is not None
            for path in proof.paths:
                for support in zip(path, path[1:]):
                    counts["generic_premise_edge_visits"] += 1
                    assert support in physical or support in new_nodes
            new_nodes[edge] = proof
    candidate = replace(post, stored=stored, nodes=new_nodes)
    if not check_dag(candidate, counts, "output_checker"):
        raise AssertionError("joint output invariant failed")
    index = dependency_index(candidate.nodes, counts)
    sizes = bundle_sizes(candidate, index)
    counts["updates"] += 1
    counts["source_queries"] += 0
    counts["producer_seconds_diagnostic"] += time.perf_counter()-start
    return candidate, sizes
