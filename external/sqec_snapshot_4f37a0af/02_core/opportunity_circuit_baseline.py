"""Independent compact monotone-circuit baseline for opportunity frontiers."""

from __future__ import annotations

from dataclasses import dataclass, replace
from itertools import combinations


@dataclass(frozen=True)
class CircuitNode:
    node_id: int
    kind: str
    atom: str | None
    children: tuple[int, ...]


@dataclass(frozen=True)
class OpportunityCircuit:
    nodes: tuple[CircuitNode, ...]
    root: int
    atoms: tuple[str, ...]
    demanded_claims: tuple[str, ...]


class _CircuitBuilder:
    def __init__(self):
        self._nodes = []
        self._intern = {}

    def node(self, kind, atom=None, children=()):
        children = tuple(sorted(set(children)))
        if kind in {"and", "or"} and len(children) == 1:
            return children[0]
        key = (kind, atom, children)
        if key not in self._intern:
            node_id = len(self._nodes)
            self._intern[key] = node_id
            self._nodes.append(CircuitNode(node_id, kind, atom, children))
        return self._intern[key]

    def finish(self, root, claims):
        atoms = tuple(sorted(node.atom for node in self._nodes if node.kind == "atom"))
        return OpportunityCircuit(tuple(self._nodes), root, atoms, claims)


def compile_opportunity_circuit(certificate) -> OpportunityCircuit:
    """Compile AND-over-claims, OR-over-routes, AND-over-requirements."""

    builder = _CircuitBuilder()
    true_node = None
    by_claim = {
        claim: tuple(
            route for route in certificate.route_requirements if route.claim == claim
        )
        for claim in certificate.demanded_claims
    }
    claim_nodes = []
    for claim in certificate.demanded_claims:
        route_nodes = []
        for route in by_claim[claim]:
            literals = tuple(
                builder.node("atom", f"s::{token}")
                for token in route.safeguards
            ) + tuple(
                builder.node("atom", f"u::{token}")
                for token in route.unresolved
            )
            if not literals:
                if true_node is None:
                    true_node = builder.node("true")
                route_nodes.append(true_node)
            else:
                route_nodes.append(builder.node("and", children=literals))
        if not route_nodes:
            raise ValueError(f"circuit claim has no route: {claim}")
        claim_nodes.append(builder.node("or", children=tuple(route_nodes)))
    root = builder.node("and", children=tuple(claim_nodes))
    return builder.finish(root, certificate.demanded_claims)


def evaluate_opportunity_circuit(circuit, selected_atoms):
    selected = set(selected_atoms)
    values = {}
    for node in circuit.nodes:
        if node.kind == "true":
            values[node.node_id] = True
        elif node.kind == "false":
            values[node.node_id] = False
        elif node.kind == "atom":
            values[node.node_id] = node.atom in selected
        elif node.kind == "and":
            values[node.node_id] = all(values[child] for child in node.children)
        elif node.kind == "or":
            values[node.node_id] = any(values[child] for child in node.children)
        else:
            raise ValueError(f"unknown circuit node kind: {node.kind}")
    return values[circuit.root]


def enumerate_minimal_circuit_models(circuit):
    atoms = circuit.atoms
    satisfying = []
    for size in range(len(atoms) + 1):
        for subset in combinations(atoms, size):
            chosen = frozenset(subset)
            if evaluate_opportunity_circuit(circuit, chosen):
                satisfying.append(chosen)
    minimal = tuple(
        chosen
        for chosen in satisfying
        if not any(other < chosen for other in satisfying)
    )
    return tuple(sorted(tuple(sorted(item)) for item in minimal))


def frontier_as_circuit_models(certificate):
    return tuple(
        sorted(
            tuple(
                sorted(
                    tuple(f"s::{token}" for token in point.safeguards)
                    + tuple(f"u::{token}" for token in point.unresolved)
                )
            )
            for point in certificate.frontier
        )
    )


def verify_circuit_against_frontier(certificate, circuit, enumerate_models=True):
    expected = compile_opportunity_circuit(certificate)
    if expected != circuit:
        return False, "opportunity circuit mismatch"
    frontier_models = frontier_as_circuit_models(certificate)
    if any(not evaluate_opportunity_circuit(circuit, model) for model in frontier_models):
        return False, "frontier point does not satisfy opportunity circuit"
    if enumerate_models and enumerate_minimal_circuit_models(circuit) != frontier_models:
        return False, "opportunity circuit minimal models disagree with frontier"
    return True, "opportunity circuit matches frontier"


def tamper_opportunity_circuit(circuit):
    root = circuit.nodes[circuit.root]
    damaged_root = replace(root, kind="or" if root.kind == "and" else "and")
    nodes = tuple(damaged_root if node.node_id == root.node_id else node for node in circuit.nodes)
    return replace(circuit, nodes=nodes)
