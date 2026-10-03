"""Certificate-carrying Need updates and joint release in the inherited DAG.

Unit deletion repair is classical (Gupta/Khan 2018, Section 4.1), not a new
max-flow algorithm. Source values and native evaluator outputs are not inputs.
"""
from __future__ import annotations

from collections import Counter, deque
from dataclasses import dataclass, replace
import json

from ordered_source_compile_v1 import Proof, transport_paths
from joint_certificate_maintenance_v1 import (
    Maintained, bundle_sizes, check_dag, contract_token, dependency_index, order,
    update as inherited_update,
)

METHODS = ("cold_dag", "cut_cache_dag", "residual_need_dag",
           "generic_indexed_flow_dag", "persistent_flat")


@dataclass(frozen=True)
class Capsule:
    # Earlier physical supports at capsule creation; later releases are virtual.
    prefix: frozenset[tuple[int, int]]
    limit: int
    value: int
    flow: dict[tuple[int, int], int]
    side: frozenset[int]


@dataclass(frozen=True)
class Incremental:
    base: Maintained
    capsules: dict[tuple[int, int], Capsule]
    incidence: dict[tuple[int, int], frozenset[tuple[int, int]]]
    buckets: dict[int, frozenset[tuple[int, int]]]


def residual(n, graph, actions, capsule, counts):
    adjacency = [[] for _ in range(n)]
    for edge in sorted(graph | capsule.prefix):
        counts["residual_network_edge_visits"] += 1
        u, v = edge
        cap = 1 if edge in actions else capsule.limit
        amount = capsule.flow.get(edge, 0)
        if amount < cap:
            adjacency[u].append((v, edge, 1, cap-amount))
        if amount:
            adjacency[v].append((u, edge, -1, amount))
    for neighbors in adjacency:
        neighbors.sort()
    return adjacency


def search(adjacency, source, target, counts, label):
    counts[label + "_searches"] += 1
    parent = {source: None}
    queue = deque([source])
    while queue and target not in parent:
        u = queue.popleft()
        for v, edge, sign, cap in adjacency[u]:
            counts[label + "_arc_inspections"] += 1
            if v not in parent:
                parent[v] = (u, edge, sign, cap)
                queue.append(v)
                if v == target:
                    break
    if target not in parent:
        return None, frozenset(parent)
    path, v = [], target
    while v != source:
        u, edge, sign, cap = parent[v]
        path.append((edge, sign, cap))
        v = u
    return tuple(reversed(path)), frozenset(parent)


def push(flow, path, amount, counts):
    for edge, sign, _ in path:
        counts["flow_edge_writes"] += 1
        value = flow.get(edge, 0) + sign*amount
        assert value >= 0
        if value:
            flow[edge] = value
        else:
            flow.pop(edge, None)


def paths(edge, capsule, counts):
    remaining = dict(capsule.flow)
    counts["decomposition_flow_copy_entries"] += len(remaining)
    adjacency = {}
    for support in sorted(remaining):
        counts["decomposition_index_edge_visits"] += 1
        adjacency.setdefault(support[0], []).append(support)
    result = []
    for _ in range(capsule.value):
        u, vertices = edge[0], [edge[0]]
        while u != edge[1]:
            chosen = None
            for support in adjacency.get(u, ()):
                counts["decomposition_arc_inspections"] += 1
                if remaining.get(support, 0):
                    chosen = support
                    break
            assert chosen is not None
            remaining[chosen] -= 1
            u = chosen[1]
            vertices.append(u)
        result.append(tuple(vertices))
    assert not any(remaining.values())
    return tuple(result)


def build(base, edge, prefix, counts):
    """Classical cold bounded max-flow; retain exact primal/dual data if needed."""
    counts["cold_flow_requests"] += 1
    cap = Capsule(prefix, base.budget+1, 0, {}, frozenset())
    flow, value = {}, 0
    while value <= base.budget:
        cap = replace(cap, flow=flow, value=value)
        adjacency = residual(base.n, base.graph, base.actions, cap, counts)
        path, side = search(adjacency, edge[0], edge[1], counts, "cold")
        if path is None:
            return replace(cap, side=side), None
        amount = min(base.budget+1-value, min(a[2] for a in path))
        push(flow, path, amount, counts)
        value += amount
        counts["cold_augmentations"] += 1
    cap = replace(cap, flow=flow, value=value)
    return None, Proof("paths", paths=paths(edge, cap, counts))


def repair_unit(base, edge, cap, action, counts):
    """Classical single-edge rerouting, with one BFS only if f carries flow."""
    if not cap.flow.get(action, 0):
        counts["zero_flow_transports"] += 1
        return cap
    assert cap.flow[action] == 1 and action in base.actions
    adjacency = residual(base.n, base.graph, base.actions, cap, counts)
    alternate, side = search(adjacency, action[0], action[1], counts, "repair")
    flow = dict(cap.flow)
    counts["repair_flow_copy_entries"] += len(flow)
    if alternate is not None:
        push(flow, alternate, 1, counts)
        push(flow, ((action, -1, 1),), 1, counts)
        counts["successful_reroutes"] += 1
        return replace(cap, flow=flow)
    # The failed residual search contains s and excludes t: reverse flow
    # paths reach s from action.tail and reach action.head from t.
    decomposition = paths(edge, cap, counts)
    containing = [p for p in decomposition if action in tuple(zip(p, p[1:]))]
    assert len(containing) == 1
    push(flow, tuple((e, -1, 1) for e in zip(containing[0], containing[0][1:])), 1, counts)
    counts["one_unit_losses"] += 1
    return replace(cap, flow=flow, value=cap.value-1, side=side)


def indexes(capsules, actions, counts=None):
    incidence, buckets = {}, {}
    for edge, cap in capsules.items():
        if counts is not None:
            counts["index_rebuild_capsule_visits"] += 1
        buckets.setdefault(cap.value, set()).add(edge)
        for support in cap.flow:
            if counts is not None:
                counts["index_rebuild_flow_visits"] += 1
            if support in actions:
                incidence.setdefault(support, set()).add(edge)
    return ({e: frozenset(v) for e, v in incidence.items()},
            {k: frozenset(v) for k, v in buckets.items()})


def initialize(base, method, counts):
    capsules = {}
    if method not in ("cold_dag", "persistent_flat"):
        prefix = frozenset()
        for edge in order(base, base.stored):
            cap, omitted = build(base, edge, prefix, counts)
            assert cap is not None and omitted is None
            if method == "cut_cache_dag":
                cap = replace(cap, flow={})
            capsules[edge] = cap
            prefix |= {edge}
    incidence, buckets = ({}, {}) if method == "cut_cache_dag" else indexes(capsules, base.actions, counts)
    state = Incremental(base, capsules, incidence, buckets)
    if not check(state, method, counts):
        raise ValueError("invalid initial operator certificates")
    return state


def check(state, method, counts=None):
    if counts is None:
        counts = Counter()
    base = state.base
    if not check_dag(base, counts, "joint_checker"):
        return False
    if method in ("cold_dag", "persistent_flat"):
        return not state.capsules and not state.incidence and not state.buckets
    if set(state.capsules) != base.stored:
        return False
    for edge, cap in state.capsules.items():
        counts["capsule_checker_visits"] += 1
        if cap.limit <= base.budget or cap.value < 0 or cap.value > base.budget:
            return False
        if edge[0] not in cap.side or edge[1] in cap.side or not cap.side <= set(range(base.n)):
            return False
        # Every frozen support has already been retained or proved; no source
        # truth is inferred from the virtual support's identity.
        if not cap.prefix <= base.stored | set(base.nodes):
            return False
        if any(order(base, [support, edge])[-1] != edge or support == edge for support in cap.prefix):
            return False
        edges = base.graph | cap.prefix
        crossing = frozenset(e for e in edges if e[0] in cap.side and e[1] not in cap.side)
        counts["capsule_checker_network_edge_visits"] += len(edges)
        if not crossing <= base.actions or len(crossing) != cap.value:
            return False
        if method == "cut_cache_dag":
            if cap.flow:
                return False
            continue
        balances = [0]*base.n
        for support, amount in cap.flow.items():
            counts["capsule_checker_flow_edge_visits"] += 1
            if support not in edges or not isinstance(amount, int) or amount <= 0:
                return False
            if amount > (1 if support in base.actions else cap.limit):
                return False
            balances[support[0]] += amount
            balances[support[1]] -= amount
        expected = [0]*base.n
        expected[edge[0]], expected[edge[1]] = cap.value, -cap.value
        if balances != expected:
            return False
    if method == "cut_cache_dag":
        return not state.incidence and not state.buckets
    expected_i, expected_b = indexes(state.capsules, base.actions, counts)
    return state.incidence == expected_i and state.buckets == expected_b


def sizes(state):
    result = bundle_sizes(state.base)
    extra = {"capsules": [[e, sorted(c.prefix), c.limit, c.value,
                           [[f,v] for f,v in sorted(c.flow.items())], sorted(c.side)]
                          for e,c in sorted(state.capsules.items())],
             "flow_incidence": [[e, sorted(v)] for e,v in sorted(state.incidence.items())],
             "value_buckets": [[k, sorted(v)] for k,v in sorted(state.buckets.items())]}
    # Same outer serialization convention, with the existing bundle nested.
    extra_bytes = len(json.dumps(extra, separators=(",", ":")).encode())
    result["need_certificate_bytes"] = extra_bytes
    result["complete_bundle_bytes"] = result["bundle_bytes"] + extra_bytes + len(b'{"base":,"need":}')
    result["flow_records"] = sum(len(c.flow) for c in state.capsules.values())
    result["cut_capsules"] = len(state.capsules)
    result["flow_index_links"] = sum(len(v) for v in state.incidence.values())
    return result


def edit_indexes(incidence, buckets, edge, old, new, old_actions, new_actions, counts):
    for support in old.flow:
        counts["index_old_flow_visits"] += 1
        if support in old_actions:
            incidence[support].discard(edge)
            if not incidence[support]:
                del incidence[support]
    buckets[old.value].discard(edge)
    if not buckets[old.value]:
        del buckets[old.value]
    if new is not None:
        buckets.setdefault(new.value, set()).add(edge)
        for support in new.flow:
            counts["index_new_flow_visits"] += 1
            if support in new_actions:
                incidence.setdefault(support, set()).add(edge)


def update(state, action, method, epoch, token, counts):
    if method not in METHODS:
        raise ValueError("unknown method")
    base = state.base
    if epoch != base.epoch or token != contract_token(base):
        raise ValueError("stale epoch or wrong predecessor")
    if action not in base.actions or base.budget <= 0:
        raise ValueError("action outside residual contract")
    if method in ("cold_dag", "persistent_flat"):
        if state.capsules or state.incidence or state.buckets:
            raise ValueError("unexpected demand certificates")
        before = Counter()
        new, _ = inherited_update(base, action,
                                  "substitution_dag" if method == "cold_dag" else method,
                                  epoch, token, before)
        counts.update(before)
        counts["cold_flow_requests"] += before["bounded_flow_requests"]
        counts["need_edge_visits"] += len(base.stored) if method == "cold_dag" else 0
        return Incremental(new, {}, {}, {})
    if not check(state, method, counts):
        raise ValueError("invalid predecessor proof/cut/flow/index")
    post = replace(base, graph=base.graph-{action}, actions=base.actions-{action},
                   budget=base.budget-1, step=base.step+1)
    nodes = {e: transport_paths(p, action) for e,p in base.nodes.items()}
    counts["transport_path_edge_visits"] += sum(len(p)-1 for proof in base.nodes.values() for p in proof.paths)
    stored = set(base.stored)
    capsules = dict(state.capsules)
    counts["capsule_map_copy_entries"] += len(capsules)
    incidence = {e: set(v) for e,v in state.incidence.items()}
    buckets = {k: set(v) for k,v in state.buckets.items()}
    counts["index_copy_links"] += sum(len(v) for v in incidence.values()) + sum(len(v) for v in buckets.values())
    if method == "cut_cache_dag":
        for edge in order(base, base.stored):
            counts["need_edge_visits"] += 1
            old = capsules[edge]
            k = old.value - int(action[0] in old.side and action[1] not in old.side)
            if k <= post.budget:
                capsules[edge] = replace(old, value=k)
                counts["valid_cut_transports"] += 1
            else:
                cap, proof = build(post, edge, old.prefix, counts)
                if cap is not None:
                    capsules[edge] = replace(cap, flow={})
                else:
                    stored.remove(edge)
                    del capsules[edge]
                    nodes[edge] = proof
                    counts["released_components"] += 1
    else:
        touched = set(state.buckets.get(base.budget, ())) | set(state.incidence.get(action, ()))
        counts["need_edge_visits"] += len(touched)
        counts["skipped_need_edges"] += len(base.stored)-len(touched)
        if method == "residual_need_dag":
            # Construct each certificate and physical release together.
            for edge in order(base, touched):
                old = capsules[edge]
                cap = repair_unit(base, edge, old, action, counts)
                retained = cap.value <= post.budget
                edit_indexes(incidence, buckets, edge, old, cap if retained else None,
                             base.actions, post.actions, counts)
                if retained:
                    capsules[edge] = cap
                else:
                    stored.remove(edge)
                    del capsules[edge]
                    nodes[edge] = Proof("paths", paths=paths(edge, cap, counts))
                    counts["released_components"] += 1
        else:
            # Generic control: update the affected classical flow instances,
            # then discharge the residual threshold and assemble proofs.
            repaired = {}
            for edge in sorted(touched):
                repaired[edge] = repair_unit(base, edge, capsules[edge], action, counts)
            release = {e for e,c in repaired.items() if c.value > post.budget}
            for edge, cap in repaired.items():
                old = capsules[edge]
                edit_indexes(incidence, buckets, edge, old, None if edge in release else cap,
                             base.actions, post.actions, counts)
                if edge in release:
                    del capsules[edge]
                else:
                    capsules[edge] = cap
            stored.difference_update(release)
            for edge in order(base, release):
                nodes[edge] = Proof("paths", paths=paths(edge, repaired[edge], counts))
                counts["released_components"] += 1
        assert action not in incidence
    candidate = Incremental(replace(post, stored=frozenset(stored), nodes=nodes), capsules,
                            {e: frozenset(v) for e,v in incidence.items()},
                            {k: frozenset(v) for k,v in buckets.items()})
    if not check(candidate, method, counts):
        raise AssertionError("joint output invariant failed")
    dependency_index(candidate.base.nodes, counts)
    counts["updates"] += 1
    counts["source_queries"] += 0
    return candidate
