"""Exact multistep planning when actions change future observation legality."""

from __future__ import annotations

from dataclasses import dataclass, replace
from fractions import Fraction
from heapq import heappop, heappush
from itertools import permutations

from dynamic_qualification_frontier import (
    AtomStatus,
    EventKind,
    QualificationEvent,
    QualificationState,
    apply_qualification_event,
    compile_dynamic_qualification_model,
    initial_dynamic_snapshot,
    make_precondition,
    make_transition,
)
from event_window_opportunity import (
    EventWindowOpportunityCertificate,
    RouteRequirement,
)


@dataclass(frozen=True)
class LegalEventOption:
    name: str
    event: QualificationEvent
    cost: Fraction


@dataclass(frozen=True)
class MultistepLegalityProblem:
    model: object
    options: tuple[LegalEventOption, ...]
    horizon: int
    failure_loss: Fraction


@dataclass(frozen=True)
class MultistepLegalityPolicy:
    sequence: tuple[str, ...]
    action_cost: Fraction
    terminal_qualified: bool
    objective: Fraction
    states_expanded: int
    illegal_edges_pruned: int
    solver: str


@dataclass(frozen=True)
class LegalityProjectionCertificate:
    full_policy: MultistepLegalityPolicy
    projected_policy: MultistepLegalityPolicy
    projected_replay_legal: bool
    projected_replay_objective: Fraction
    replay_regret: Fraction


def _validate(problem):
    if problem.horizon < 0 or problem.failure_loss < 0:
        raise ValueError("horizon and failure loss must be nonnegative")
    if len({option.name for option in problem.options}) != len(problem.options):
        raise ValueError("event option names must be unique")
    if any(option.cost < 0 or option.name != option.event.event_id for option in problem.options):
        raise ValueError("event options need matching names and nonnegative costs")


def _objective(snapshot, cost, failure_loss):
    qualified = snapshot.joint_state == QualificationState.QUALIFIED
    return cost + (Fraction(0) if qualified else failure_loss), qualified


def solve_multistep_sequence_oracle(problem):
    _validate(problem)
    initial = initial_dynamic_snapshot(problem.model)
    candidates = []
    expanded = 0
    illegal = 0
    for depth in range(min(problem.horizon, len(problem.options)) + 1):
        for sequence in permutations(problem.options, depth):
            snapshot = initial
            cost = Fraction(0)
            legal = True
            for option in sequence:
                expanded += 1
                try:
                    snapshot = apply_qualification_event(
                        problem.model, snapshot, option.event
                    )
                except ValueError as exc:
                    if "is illegal" not in str(exc):
                        raise
                    illegal += 1
                    legal = False
                    break
                cost += option.cost
            if legal:
                value, qualified = _objective(snapshot, cost, problem.failure_loss)
                candidates.append(
                    (value, tuple(item.name for item in sequence), cost, qualified)
                )
    value, sequence, cost, qualified = min(candidates)
    return MultistepLegalityPolicy(
        sequence, cost, qualified, value, expanded, illegal, "sequence-oracle"
    )


def solve_generic_legality_state_graph(problem):
    """Independent Dijkstra search over typed state and used-event mask."""

    _validate(problem)
    initial = initial_dynamic_snapshot(problem.model)
    queue = [(Fraction(0), (), 0, initial)]
    best = {(initial.atom_statuses, 0): Fraction(0)}
    candidates = []
    expanded = 0
    illegal = 0
    while queue:
        cost, sequence, mask, snapshot = heappop(queue)
        if cost != best.get((snapshot.atom_statuses, mask)):
            continue
        value, qualified = _objective(snapshot, cost, problem.failure_loss)
        candidates.append((value, sequence, cost, qualified))
        if len(sequence) == problem.horizon:
            continue
        for index, option in enumerate(problem.options):
            if mask & (1 << index):
                continue
            expanded += 1
            try:
                successor = apply_qualification_event(
                    problem.model, snapshot, option.event
                )
            except ValueError as exc:
                if "is illegal" not in str(exc):
                    raise
                illegal += 1
                continue
            new_cost = cost + option.cost
            new_mask = mask | (1 << index)
            key = (successor.atom_statuses, new_mask)
            new_sequence = sequence + (option.name,)
            previous = best.get(key)
            if previous is None or new_cost < previous:
                best[key] = new_cost
                heappush(queue, (new_cost, new_sequence, new_mask, successor))
    value, sequence, cost, qualified = min(candidates)
    return MultistepLegalityPolicy(
        sequence, cost, qualified, value, expanded, illegal, "generic-state-graph"
    )


def project_away_event_legality(problem):
    options = tuple(
        replace(
            option,
            event=replace(option.event, preconditions=()),
        )
        for option in problem.options
    )
    return replace(problem, options=options)


def replay_policy(problem, policy):
    by_name = {option.name: option for option in problem.options}
    snapshot = initial_dynamic_snapshot(problem.model)
    cost = Fraction(0)
    for name in policy.sequence:
        option = by_name[name]
        try:
            snapshot = apply_qualification_event(
                problem.model, snapshot, option.event
            )
        except ValueError as exc:
            if "is illegal" not in str(exc):
                raise
            return False, cost + problem.failure_loss
        cost += option.cost
    value, _ = _objective(snapshot, cost, problem.failure_loss)
    return True, value


def compile_legality_projection_certificate(problem):
    full = solve_generic_legality_state_graph(problem)
    projected = solve_generic_legality_state_graph(
        project_away_event_legality(problem)
    )
    legal, replay_value = replay_policy(problem, projected)
    return LegalityProjectionCertificate(
        full,
        projected,
        legal,
        replay_value,
        replay_value - full.objective,
    )


def verify_multistep_legality(problem, certificate):
    expected = compile_legality_projection_certificate(problem)
    if expected != certificate:
        return False, "multistep legality certificate mismatch"
    oracle = solve_multistep_sequence_oracle(problem)
    if (
        oracle.sequence != certificate.full_policy.sequence
        or oracle.objective != certificate.full_policy.objective
    ):
        return False, "generic state graph disagrees with sequence oracle"
    return True, "multistep legality certificate verified"


def build_controlled_observation_legality_problem():
    certificate = EventWindowOpportunityCertificate(
        ("post-action-claim",),
        (
            RouteRequirement(
                "post-action-claim",
                "claim-route",
                "task result plus latent semantic observation",
                ("task-done",),
                ("latent-semantics",),
            ),
        ),
        (), (), False, 0, 0,
    )
    model = compile_dynamic_qualification_model(
        certificate,
        {"s::observation-route": AtomStatus.ACTION_OPEN},
    )
    total = {status: status for status in AtomStatus}

    commit_task = dict(total)
    commit_task[AtomStatus.ACTION_OPEN] = AtomStatus.SATISFIED
    close_route = dict(total)
    close_route[AtomStatus.ACTION_OPEN] = AtomStatus.CLOSED
    commit = QualificationEvent(
        "commit-task",
        EventKind.ACTION,
        (
            make_transition("s::task-done", commit_task),
            make_transition("s::observation-route", close_route),
        ),
        "controlled",
        "observation-legality separation",
    )

    reveal = dict(total)
    reveal[AtomStatus.UNKNOWN] = AtomStatus.SATISFIED
    observe = QualificationEvent(
        "observe-semantics",
        EventKind.OBSERVATION,
        (make_transition("u::latent-semantics", reveal),),
        "controlled",
        "observation-legality separation",
        (
            make_precondition(
                "s::observation-route",
                (AtomStatus.ACTION_OPEN, AtomStatus.SATISFIED),
            ),
        ),
    )

    retain_route = dict(total)
    retain_route[AtomStatus.ACTION_OPEN] = AtomStatus.SATISFIED
    retain = QualificationEvent(
        "retain-observation-route",
        EventKind.ACTION,
        (make_transition("s::observation-route", retain_route),),
        "controlled",
        "observation-legality separation",
    )
    return MultistepLegalityProblem(
        model,
        (
            LegalEventOption("commit-task", commit, Fraction(0)),
            LegalEventOption("observe-semantics", observe, Fraction(1, 5)),
            LegalEventOption("retain-observation-route", retain, Fraction(1)),
        ),
        3,
        Fraction(10),
    )


def tamper_legality_certificate(certificate):
    return replace(certificate, replay_regret=certificate.replay_regret + 1)

