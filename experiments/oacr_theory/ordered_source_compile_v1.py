"""One-pass physical compilation and source acquisition on a public DAG.

Classical bounded maxflow supplies independently checkable support/cut proofs.
The working pointwise query theorem is specific to full reachability and an
independent source cube; neither novelty nor general-carrier coverage is assumed.
"""
from __future__ import annotations

from collections import Counter, deque
from dataclasses import dataclass
import heapq
import json

from available_source_repair_v1 import SourcePort


@dataclass(frozen=True)
class Proof:
    kind: str
    paths: tuple[tuple[int, ...], ...] = ()
    source_side: frozenset[int] = frozenset()


@dataclass(frozen=True)
class Receipt:
    edge: tuple[int, int]
    known: bool
    answer: bool | None
    proof: Proof


@dataclass(frozen=True)
class Result:
    exact: bool
    stored: frozenset[tuple[int, int]]
    transcript: tuple[tuple[tuple[int, int], bool], ...]
    receipts: tuple[Receipt, ...]
    reason: str


def topological_rank(n, edges):
    if n < 2 or any(not (0 <= u < n and 0 <= v < n and u != v) for u, v in edges):
        raise ValueError("invalid vertices")
    degree, successors = [0] * n, [[] for _ in range(n)]
    for u, v in sorted(edges):
        degree[v] += 1
        successors[u].append(v)
    ready = [u for u in range(n) if degree[u] == 0]
    heapq.heapify(ready)
    rank = {}
    while ready:
        u = heapq.heappop(ready)
        rank[u] = len(rank)
        for v in successors[u]:
            degree[v] -= 1
            if degree[v] == 0:
                heapq.heappush(ready, v)
    if len(rank) != n:
        raise ValueError("potential augmented graph must be acyclic")
    return rank


def support_proof(n, edges, actions, h, edge, counts):
    """Stop flow at h+1. Return paths or a separating partition, not a label."""
    counts["bounded_flow_requests"] += 1
    source, target = edge
    if edge in edges or not actions <= edges or not 0 <= h <= len(actions):
        raise ValueError("invalid support test")
    capacity = [[0] * n for _ in range(n)]
    for u, v in edges:
        capacity[u][v] = 1 if (u, v) in actions else h + 1
    residual = [row[:] for row in capacity]
    value = 0
    while value <= h:
        parent = [-1] * n
        parent[source] = source
        queue = deque([source])
        while queue and parent[target] < 0:
            u = queue.popleft()
            for v in range(n):
                if parent[v] < 0 and residual[u][v] > 0:
                    parent[v] = u
                    queue.append(v)
        if parent[target] < 0:
            return Proof("cut", source_side=frozenset(i for i, p in enumerate(parent) if p >= 0))
        add, v = h + 1 - value, target
        while v != source:
            u = parent[v]
            add = min(add, residual[u][v])
            v = u
        v = target
        while v != source:
            u = parent[v]
            residual[u][v] -= add
            residual[v][u] += add
            v = u
        value += add
        counts["augmentations"] += 1
    # Original edges are acyclic, so their positive integral flow has no cycles.
    flow = {(u, v): capacity[u][v] - residual[u][v] for u, v in edges}
    paths = []
    for _ in range(h + 1):
        u, path = source, [source]
        while u != target:
            v = min(v for a, v in edges if a == u and flow[(a, v)] > 0)
            flow[(u, v)] -= 1
            path.append(v)
            u = v
        paths.append(tuple(path))
    assert not any(flow.values())
    return Proof("paths", paths=tuple(paths))


def check_proof(n, edges, actions, h, edge, proof):
    """Independent arithmetic/adjacency checker: no maxflow or world outcomes."""
    if edge in edges or not actions <= edges or not 0 <= h <= len(actions):
        return False
    source, target = edge
    if proof.kind == "paths":
        if len(proof.paths) != h + 1 or proof.source_side:
            return False
        used = Counter()
        for path in proof.paths:
            if not path or path[0] != source or path[-1] != target or len(set(path)) != len(path):
                return False
            for e in zip(path, path[1:]):
                if e not in edges:
                    return False
                used[e] += 1
        return all(used[e] <= 1 for e in actions)
    if proof.kind == "cut":
        side = proof.source_side
        if proof.paths or not side <= frozenset(range(n)) or source not in side or target in side:
            return False
        crossing = frozenset((u, v) for u, v in edges if u in side and v not in side)
        return crossing <= actions and len(crossing) <= h
    return False


def transport_paths(proof, action):
    """One legal base deletion consumes one path and one budget unit."""
    if proof.kind != "paths" or len(proof.paths) < 2:
        raise ValueError("no legal positive-budget path transport")
    hit = [i for i, path in enumerate(proof.paths) if action in tuple(zip(path, path[1:]))]
    if len(hit) > 1:
        raise ValueError("deletable edge shared by paths")
    remove = hit[0] if hit else 0
    return Proof("paths", paths=tuple(p for i, p in enumerate(proof.paths) if i != remove))


def receipt_payload(receipts):
    return [{"edge": r.edge, "known": r.known, "answer": r.answer,
             "proof": {"kind": r.proof.kind, "paths": r.proof.paths,
                       "source_side": sorted(r.proof.source_side)}} for r in receipts]


def compile_from_source(n, graph, actions, h, known, unknown, source: SourcePort,
                        snapshot, counts):
    """Visible inputs exclude actual B, possible-world banks and native outputs."""
    if known & unknown or (known | unknown) & graph or not actions <= graph or not 0 <= h <= len(actions):
        raise ValueError("invalid source cube")
    rank = topological_rank(n, graph | known | unknown)
    ordered = sorted(known | unknown, key=lambda e: (rank[e[1]] - rank[e[0]], rank[e[0]], rank[e[1]]))
    stored, transcript, receipts = frozenset(), [], []

    def finish(exact, reason):
        counts["source_queries"] += len(transcript)
        counts["retained_edge_records"] += len(stored)
        counts["receipt_serialized_bytes"] += len(json.dumps(receipt_payload(receipts), separators=(",", ":")).encode())
        counts["requests"] += 1
        return Result(exact, stored, tuple(transcript), tuple(receipts), reason)

    if source.epoch != snapshot:
        return finish(False, "stale_source")
    for edge in ordered:
        proof = support_proof(n, graph | stored, actions, h, edge, counts)
        if proof.kind == "paths":
            receipts.append(Receipt(edge, edge in known, None, proof))
            continue
        if edge in known:
            receipts.append(Receipt(edge, True, True, proof))
            stored |= {edge}
            continue
        if edge not in source.permissions:
            receipts.append(Receipt(edge, False, None, proof))
            return finish(False, "necessary_source_unavailable")
        if len(transcript) >= source.budget:
            receipts.append(Receipt(edge, False, None, proof))
            return finish(False, "necessary_source_budget_exhausted")
        answer = source.membership(edge, snapshot)
        transcript.append((edge, answer))
        receipts.append(Receipt(edge, False, answer, proof))
        if answer:
            stored |= {edge}
    return finish(True, "exact_physical_compilation")
