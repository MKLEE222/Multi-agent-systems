"""Action/observation-conditioned evolution of qualification opportunity.

The module deliberately separates three layers:

* a monotone route circuit states what a joint claim demand requires;
* typed atom states record whether a requirement is satisfied, still
  actionable, epistemically unresolved, or irreversibly closed;
* typed events update those states without assigning a decision objective.

This is a transition and certificate layer.  A generic planner may consume its
output; costs, probabilities, and carrier-specific policies are not invented
here.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from itertools import product

from opportunity_circuit_baseline import (
    CircuitNode,
    OpportunityCircuit,
    compile_opportunity_circuit,
    evaluate_opportunity_circuit,
)


class AtomStatus(str, Enum):
    SATISFIED = "satisfied"
    ACTION_OPEN = "action-open"
    UNKNOWN = "unknown"
    CLOSED = "closed"


class EventKind(str, Enum):
    ACTION = "action"
    OBSERVATION = "observation"
    TIME = "time"


class QualificationState(str, Enum):
    QUALIFIED = "qualified"
    ACTION_OPEN = "action-open"
    EPISTEMICALLY_OPEN = "epistemically-open"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class AtomTransition:
    atom: str
    cases: tuple[tuple[AtomStatus, AtomStatus], ...]


@dataclass(frozen=True)
class AtomPrecondition:
    atom: str
    allowed: tuple[AtomStatus, ...]


@dataclass(frozen=True)
class QualificationEvent:
    event_id: str
    kind: EventKind
    transitions: tuple[AtomTransition, ...]
    evidence_basis: str
    source: str
    preconditions: tuple[AtomPrecondition, ...] = ()


@dataclass(frozen=True)
class DynamicQualificationModel:
    demanded_claims: tuple[str, ...]
    route_requirements: tuple
    circuit: OpportunityCircuit
    initial_statuses: tuple[tuple[str, AtomStatus], ...]


@dataclass(frozen=True)
class DynamicQualificationSnapshot:
    step: int
    event_id: str | None
    atom_statuses: tuple[tuple[str, AtomStatus], ...]
    claim_states: tuple[tuple[str, QualificationState], ...]
    joint_state: QualificationState
    residual_circuit: OpportunityCircuit


@dataclass(frozen=True)
class DynamicQualificationTraceCertificate:
    event_ids: tuple[str, ...]
    snapshots: tuple[DynamicQualificationSnapshot, ...]


class _ResidualBuilder:
    def __init__(self):
        self.nodes = []
        self.intern = {}

    def node(self, kind, atom=None, children=()):
        children = tuple(sorted(set(children)))
        if kind in {"and", "or"} and len(children) == 1:
            return children[0]
        key = (kind, atom, children)
        if key not in self.intern:
            node_id = len(self.nodes)
            self.intern[key] = node_id
            self.nodes.append(CircuitNode(node_id, kind, atom, children))
        return self.intern[key]

    def finish(self, root, claims):
        atoms = tuple(sorted(node.atom for node in self.nodes if node.kind == "atom"))
        return OpportunityCircuit(tuple(self.nodes), root, atoms, claims)


def make_transition(atom, mapping):
    return AtomTransition(atom, tuple(sorted(mapping.items(), key=lambda item: item[0].value)))


def make_precondition(atom, allowed):
    values = tuple(sorted(set(allowed), key=lambda item: item.value))
    return AtomPrecondition(atom, values)


def compile_dynamic_qualification_model(certificate, additional_atom_statuses=None):
    circuit = compile_opportunity_circuit(certificate)
    statuses = dict(
        (atom, AtomStatus.ACTION_OPEN if atom.startswith("s::") else AtomStatus.UNKNOWN)
        for atom in circuit.atoms
    )
    for atom, status in dict(additional_atom_statuses or {}).items():
        if atom in statuses:
            raise ValueError(f"additional atom duplicates circuit atom: {atom}")
        if not atom.startswith(("s::", "u::")):
            raise ValueError("additional atom must be typed as safeguard or epistemic")
        if not isinstance(status, AtomStatus):
            raise ValueError("additional atom status must be typed")
        statuses[atom] = status
    return DynamicQualificationModel(
        certificate.demanded_claims,
        certificate.route_requirements,
        circuit,
        tuple(sorted(statuses.items())),
    )


def _validate_event(model, event):
    if not event.event_id or not event.evidence_basis or not event.source:
        raise ValueError("event id, evidence basis, and source must be nonempty")
    known_atoms = set(dict(model.initial_statuses))
    precondition_atoms = set()
    for precondition in event.preconditions:
        if precondition.atom not in known_atoms:
            raise ValueError(f"event precondition references unknown atom: {precondition.atom}")
        if precondition.atom in precondition_atoms:
            raise ValueError(f"event repeats atom precondition: {precondition.atom}")
        precondition_atoms.add(precondition.atom)
        if not precondition.allowed or len(set(precondition.allowed)) != len(precondition.allowed):
            raise ValueError("event precondition statuses must be nonempty and unique")
    seen = set()
    for transition in event.transitions:
        if transition.atom not in known_atoms:
            raise ValueError(f"event references unknown atom: {transition.atom}")
        if transition.atom in seen:
            raise ValueError(f"event repeats atom transition: {transition.atom}")
        seen.add(transition.atom)
        sources = tuple(source for source, _ in transition.cases)
        if not sources or len(set(sources)) != len(sources):
            raise ValueError("transition cases must have unique nonempty sources")
        if event.kind == EventKind.ACTION and transition.atom.startswith("u::"):
            raise ValueError("actions cannot resolve epistemic coordinates")
        if event.kind == EventKind.OBSERVATION and transition.atom.startswith("s::"):
            raise ValueError("observations cannot supply safeguards")


def _status_map(snapshot):
    return dict(snapshot.atom_statuses)


def restrict_opportunity_circuit(circuit, statuses):
    builder = _ResidualBuilder()
    old_to_new = {}
    true_id = builder.node("true")
    false_id = builder.node("false")
    for node in circuit.nodes:
        if node.kind == "true":
            old_to_new[node.node_id] = true_id
        elif node.kind == "false":
            old_to_new[node.node_id] = false_id
        elif node.kind == "atom":
            status = statuses[node.atom]
            if status == AtomStatus.SATISFIED:
                old_to_new[node.node_id] = true_id
            elif status == AtomStatus.CLOSED:
                old_to_new[node.node_id] = false_id
            else:
                old_to_new[node.node_id] = builder.node("atom", node.atom)
        elif node.kind in {"and", "or"}:
            children = tuple(old_to_new[child] for child in node.children)
            child_kinds = tuple(builder.nodes[child].kind for child in children)
            if node.kind == "and" and "false" in child_kinds:
                old_to_new[node.node_id] = false_id
            elif node.kind == "or" and "true" in child_kinds:
                old_to_new[node.node_id] = true_id
            else:
                identity = true_id if node.kind == "and" else false_id
                reduced = tuple(
                    child for child in children
                    if child != identity
                )
                if not reduced:
                    old_to_new[node.node_id] = identity
                else:
                    old_to_new[node.node_id] = builder.node(node.kind, children=reduced)
        else:
            raise ValueError(f"unknown circuit node kind: {node.kind}")
    return builder.finish(old_to_new[circuit.root], circuit.demanded_claims)


def _route_state(route, statuses):
    atoms = tuple(f"s::{item}" for item in route.safeguards) + tuple(
        f"u::{item}" for item in route.unresolved
    )
    values = tuple(statuses[atom] for atom in atoms)
    if any(value == AtomStatus.CLOSED for value in values):
        return QualificationState.BLOCKED
    if all(value == AtomStatus.SATISFIED for value in values):
        return QualificationState.QUALIFIED
    if any(value == AtomStatus.UNKNOWN for value in values):
        return QualificationState.EPISTEMICALLY_OPEN
    return QualificationState.ACTION_OPEN


def _claim_states(model, statuses):
    result = []
    for claim in model.demanded_claims:
        routes = tuple(
            _route_state(route, statuses)
            for route in model.route_requirements
            if route.claim == claim
        )
        if QualificationState.QUALIFIED in routes:
            state = QualificationState.QUALIFIED
        elif QualificationState.ACTION_OPEN in routes:
            state = QualificationState.ACTION_OPEN
        elif QualificationState.EPISTEMICALLY_OPEN in routes:
            state = QualificationState.EPISTEMICALLY_OPEN
        else:
            state = QualificationState.BLOCKED
        result.append((claim, state))
    return tuple(result)


def _joint_state(claim_states):
    values = tuple(state for _, state in claim_states)
    if all(state == QualificationState.QUALIFIED for state in values):
        return QualificationState.QUALIFIED
    if QualificationState.BLOCKED in values:
        return QualificationState.BLOCKED
    if QualificationState.EPISTEMICALLY_OPEN in values:
        return QualificationState.EPISTEMICALLY_OPEN
    return QualificationState.ACTION_OPEN


def _snapshot(model, statuses, step, event_id):
    ordered = tuple((atom, statuses[atom]) for atom in sorted(statuses))
    claims = _claim_states(model, statuses)
    return DynamicQualificationSnapshot(
        step,
        event_id,
        ordered,
        claims,
        _joint_state(claims),
        restrict_opportunity_circuit(model.circuit, statuses),
    )


def initial_dynamic_snapshot(model):
    return _snapshot(model, dict(model.initial_statuses), 0, None)


def apply_qualification_event(model, snapshot, event):
    _validate_event(model, event)
    statuses = _status_map(snapshot)
    for precondition in event.preconditions:
        if statuses[precondition.atom] not in precondition.allowed:
            raise ValueError(
                f"event {event.event_id} is illegal: precondition on "
                f"{precondition.atom} is not satisfied"
            )
    for transition in event.transitions:
        cases = dict(transition.cases)
        current = statuses[transition.atom]
        if current not in cases:
            raise ValueError(
                f"event {event.event_id} has no transition for "
                f"{transition.atom} from {current.value}"
            )
        statuses[transition.atom] = cases[current]
    return _snapshot(model, statuses, snapshot.step + 1, event.event_id)


def compile_dynamic_trace(model, events):
    snapshots = [initial_dynamic_snapshot(model)]
    for event in events:
        snapshots.append(apply_qualification_event(model, snapshots[-1], event))
    return DynamicQualificationTraceCertificate(
        tuple(event.event_id for event in events), tuple(snapshots)
    )


def _direct_circuit_value(circuit, statuses, completion):
    selected = {
        atom for atom, status in statuses.items()
        if status == AtomStatus.SATISFIED
    } | set(completion)
    return evaluate_opportunity_circuit(circuit, selected)


def verify_snapshot_semantics(model, snapshot, exhaustive_limit=16):
    statuses = _status_map(snapshot)
    if set(statuses) != set(dict(model.initial_statuses)):
        return False, "snapshot atom domain mismatch"
    expected_claims = _claim_states(model, statuses)
    if expected_claims != snapshot.claim_states:
        return False, "snapshot claim states disagree with route oracle"
    if _joint_state(expected_claims) != snapshot.joint_state:
        return False, "snapshot joint state disagrees with route oracle"
    residual = restrict_opportunity_circuit(model.circuit, statuses)
    if residual != snapshot.residual_circuit:
        return False, "snapshot residual circuit mismatch"

    undecided = tuple(
        atom for atom, status in statuses.items()
        if status in {AtomStatus.ACTION_OPEN, AtomStatus.UNKNOWN}
    )
    if len(undecided) <= exhaustive_limit:
        for bits in product((False, True), repeat=len(undecided)):
            completion = tuple(atom for atom, bit in zip(undecided, bits) if bit)
            original = _direct_circuit_value(model.circuit, statuses, completion)
            residual_value = evaluate_opportunity_circuit(residual, completion)
            if original != residual_value:
                return False, "residual circuit disagrees with completion oracle"
    return True, "dynamic qualification snapshot verified"


def verify_dynamic_trace(model, certificate, event_catalog):
    try:
        events = tuple(event_catalog[event_id] for event_id in certificate.event_ids)
    except KeyError as exc:
        return False, f"trace references unknown event: {exc.args[0]}"
    try:
        expected = compile_dynamic_trace(model, events)
    except ValueError as exc:
        return False, str(exc)
    if expected != certificate:
        return False, "dynamic qualification trace mismatch"
    for snapshot in certificate.snapshots:
        valid, message = verify_snapshot_semantics(model, snapshot)
        if not valid:
            return False, message
    return True, "dynamic qualification trace verified"


def tamper_dynamic_trace(certificate):
    last = certificate.snapshots[-1]
    damaged_state = (
        QualificationState.BLOCKED
        if last.joint_state == QualificationState.QUALIFIED
        else QualificationState.QUALIFIED
    )
    damaged = replace(last, joint_state=damaged_state)
    return replace(certificate, snapshots=(*certificate.snapshots[:-1], damaged))
