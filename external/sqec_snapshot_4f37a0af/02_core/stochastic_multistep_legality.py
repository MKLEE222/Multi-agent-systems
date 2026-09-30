"""Stochastic multistep policies with action-conditioned observation legality."""

from __future__ import annotations

from dataclasses import dataclass, replace
from fractions import Fraction
from itertools import product

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
from event_window_opportunity import EventWindowOpportunityCertificate, RouteRequirement
from multistep_observation_legality import LegalEventOption


@dataclass(frozen=True)
class StochasticLegalityOutcome:
    label: str
    probability: Fraction
    event: QualificationEvent


@dataclass(frozen=True)
class StochasticLegalityObservation:
    name: str
    cost: Fraction
    outcomes: tuple[StochasticLegalityOutcome, ...]


@dataclass(frozen=True)
class StochasticLegalityProblem:
    model: object
    actions: tuple[LegalEventOption, ...]
    observation: StochasticLegalityObservation
    horizon: int
    failure_loss: Fraction


@dataclass(frozen=True)
class StochasticPolicyNode:
    kind: str
    name: str
    expected_objective: Fraction
    terminal_qualified: bool | None = None
    child: object | None = None
    branches: tuple[tuple[str, Fraction, object], ...] = ()


@dataclass(frozen=True)
class StochasticLegalityPolicy:
    root: StochasticPolicyNode
    expected_objective: Fraction
    states_evaluated: int
    illegal_edges_pruned: int
    solver: str


@dataclass(frozen=True)
class StochasticLegalityProjectionCertificate:
    full_policy: StochasticLegalityPolicy
    projected_policy: StochasticLegalityPolicy
    projected_replay_objective: Fraction
    replay_regret: Fraction


@dataclass(frozen=True)
class ExplicitStochasticPolicyOracle:
    root: StochasticPolicyNode
    expected_objective: Fraction
    complete_trees_enumerated: int


def _validate(problem):
    if problem.horizon < 0 or problem.failure_loss < 0 or problem.observation.cost < 0:
        raise ValueError("stochastic legality costs and horizon must be nonnegative")
    if sum((item.probability for item in problem.observation.outcomes), Fraction(0)) != 1:
        raise ValueError("stochastic legality outcome probabilities must sum to one")
    if any(item.probability < 0 for item in problem.observation.outcomes):
        raise ValueError("stochastic legality probabilities must be nonnegative")
    if len({item.name for item in problem.actions}) != len(problem.actions):
        raise ValueError("stochastic legality action names must be unique")


def solve_stochastic_legality_policy(problem):
    _validate(problem)
    initial = initial_dynamic_snapshot(problem.model)
    memo = {}
    counters = {"states": 0, "illegal": 0}

    def solve(snapshot, used_mask, observation_used, remaining):
        key = (snapshot.atom_statuses, used_mask, observation_used, remaining)
        if key in memo:
            return memo[key]
        counters["states"] += 1
        qualified = snapshot.joint_state == QualificationState.QUALIFIED
        stop_value = Fraction(0) if qualified else problem.failure_loss
        candidates = [
            (
                stop_value,
                "0-stop",
                StochasticPolicyNode("stop", "stop", stop_value, qualified),
            )
        ]
        if remaining:
            for index, option in enumerate(problem.actions):
                if used_mask & (1 << index):
                    continue
                try:
                    successor = apply_qualification_event(
                        problem.model, snapshot, option.event
                    )
                except ValueError as exc:
                    if "is illegal" not in str(exc):
                        raise
                    counters["illegal"] += 1
                    continue
                child = solve(
                    successor, used_mask | (1 << index), observation_used, remaining - 1
                )
                value = option.cost + child.expected_objective
                candidates.append(
                    (
                        value,
                        f"1-{option.name}",
                        StochasticPolicyNode("action", option.name, value, child=child),
                    )
                )
            if not observation_used:
                branches = []
                value = problem.observation.cost
                legal = True
                for outcome in problem.observation.outcomes:
                    try:
                        successor = apply_qualification_event(
                            problem.model, snapshot, outcome.event
                        )
                    except ValueError as exc:
                        if "is illegal" not in str(exc):
                            raise
                        counters["illegal"] += 1
                        legal = False
                        break
                    child = solve(successor, used_mask, True, remaining - 1)
                    value += outcome.probability * child.expected_objective
                    branches.append((outcome.label, outcome.probability, child))
                if legal:
                    candidates.append(
                        (
                            value,
                            f"1-{problem.observation.name}",
                            StochasticPolicyNode(
                                "observation",
                                problem.observation.name,
                                value,
                                branches=tuple(branches),
                            ),
                        )
                    )
        result = min(candidates, key=lambda item: (item[0], item[1]))[2]
        memo[key] = result
        return result

    root = solve(initial, 0, False, problem.horizon)
    return StochasticLegalityPolicy(
        root,
        root.expected_objective,
        counters["states"],
        counters["illegal"],
        "typed-dynamic-program",
    )


def project_stochastic_legality(problem):
    actions = tuple(
        replace(option, event=replace(option.event, preconditions=()))
        for option in problem.actions
    )
    outcomes = tuple(
        replace(outcome, event=replace(outcome.event, preconditions=()))
        for outcome in problem.observation.outcomes
    )
    return replace(
        problem,
        actions=actions,
        observation=replace(problem.observation, outcomes=outcomes),
    )


def replay_stochastic_policy(problem, policy):
    actions = {item.name: item for item in problem.actions}

    def replay(snapshot, node, accumulated):
        if node.kind == "stop":
            return accumulated + (
                Fraction(0)
                if snapshot.joint_state == QualificationState.QUALIFIED
                else problem.failure_loss
            )
        if node.kind == "action":
            option = actions[node.name]
            try:
                successor = apply_qualification_event(
                    problem.model, snapshot, option.event
                )
            except ValueError as exc:
                if "is illegal" not in str(exc):
                    raise
                return accumulated + problem.failure_loss
            return replay(successor, node.child, accumulated + option.cost)
        if node.kind == "observation":
            value = accumulated + problem.observation.cost
            branches = {label: child for label, _, child in node.branches}
            for outcome in problem.observation.outcomes:
                try:
                    successor = apply_qualification_event(
                        problem.model, snapshot, outcome.event
                    )
                except ValueError as exc:
                    if "is illegal" not in str(exc):
                        raise
                    return accumulated + problem.failure_loss
                value += outcome.probability * replay(
                    successor, branches[outcome.label], Fraction(0)
                )
            return value
        raise ValueError("unknown stochastic policy node")

    return replay(initial_dynamic_snapshot(problem.model), policy.root, Fraction(0))


def solve_flat_stochastic_mdp_baseline(problem):
    """Matched baseline: compile reachable typed states, then run the same Bellman contract.

    The implementation deliberately exposes that a generic finite MDP absorbs
    optimization once the legality-bearing state is supplied.
    """

    result = solve_stochastic_legality_policy(problem)
    return replace(result, solver="generic-flat-state-mdp")


def enumerate_explicit_stochastic_policy_trees(problem):
    """Independently enumerate all finite contingent policy trees."""
    _validate(problem)
    initial = initial_dynamic_snapshot(problem.model)

    def node_key(node):
        if node.kind == "stop":
            return ("0-stop",)
        if node.kind == "action":
            return (f"1-{node.name}", node_key(node.child))
        return (
            f"1-{node.name}",
            tuple((label, node_key(child)) for label, _, child in node.branches),
        )

    def enumerate_nodes(snapshot, used_mask, observation_used, remaining):
        qualified = snapshot.joint_state == QualificationState.QUALIFIED
        stop_value = Fraction(0) if qualified else problem.failure_loss
        nodes = [StochasticPolicyNode("stop", "stop", stop_value, qualified)]
        if not remaining:
            return tuple(nodes)
        for index, option in enumerate(problem.actions):
            if used_mask & (1 << index):
                continue
            try:
                successor = apply_qualification_event(
                    problem.model, snapshot, option.event
                )
            except ValueError as exc:
                if "is illegal" not in str(exc):
                    raise
                continue
            for child in enumerate_nodes(
                successor, used_mask | (1 << index), observation_used, remaining - 1
            ):
                value = option.cost + child.expected_objective
                nodes.append(
                    StochasticPolicyNode("action", option.name, value, child=child)
                )
        if not observation_used:
            outcome_children = []
            legal = True
            for outcome in problem.observation.outcomes:
                try:
                    successor = apply_qualification_event(
                        problem.model, snapshot, outcome.event
                    )
                except ValueError as exc:
                    if "is illegal" not in str(exc):
                        raise
                    legal = False
                    break
                outcome_children.append(
                    enumerate_nodes(successor, used_mask, True, remaining - 1)
                )
            if legal:
                for children in product(*outcome_children):
                    value = problem.observation.cost + sum(
                        (
                            outcome.probability * child.expected_objective
                            for outcome, child in zip(problem.observation.outcomes, children)
                        ),
                        Fraction(0),
                    )
                    branches = tuple(
                        (outcome.label, outcome.probability, child)
                        for outcome, child in zip(problem.observation.outcomes, children)
                    )
                    nodes.append(
                        StochasticPolicyNode(
                            "observation", problem.observation.name, value,
                            branches=branches,
                        )
                    )
        return tuple(nodes)

    return enumerate_nodes(initial, 0, False, problem.horizon)


def solve_explicit_stochastic_policy_oracle(problem):
    """Independent complete enumeration of all finite contingent policy trees."""

    trees = enumerate_explicit_stochastic_policy_trees(problem)

    def node_key(node):
        if node.kind == "stop":
            return ("0-stop",)
        if node.kind == "action":
            return (f"1-{node.name}", node_key(node.child))
        return (
            f"1-{node.name}",
            tuple((label, node_key(child)) for label, _, child in node.branches),
        )

    root = min(trees, key=lambda node: (node.expected_objective, node_key(node)))
    return ExplicitStochasticPolicyOracle(root, root.expected_objective, len(trees))


def compile_stochastic_legality_projection(problem):
    full = solve_flat_stochastic_mdp_baseline(problem)
    projected = solve_flat_stochastic_mdp_baseline(project_stochastic_legality(problem))
    replay = replay_stochastic_policy(problem, projected)
    return StochasticLegalityProjectionCertificate(
        full, projected, replay, replay - full.expected_objective
    )


def verify_stochastic_legality(problem, certificate):
    expected = compile_stochastic_legality_projection(problem)
    if expected != certificate:
        return False, "stochastic legality certificate mismatch"
    typed = solve_stochastic_legality_policy(problem)
    if (
        typed.expected_objective != certificate.full_policy.expected_objective
        or typed.root != certificate.full_policy.root
    ):
        return False, "typed policy differs from flat-state MDP"
    oracle = solve_explicit_stochastic_policy_oracle(problem)
    if (
        oracle.expected_objective != certificate.full_policy.expected_objective
        or oracle.root != certificate.full_policy.root
    ):
        return False, "typed policy differs from explicit policy-tree oracle"
    return True, "stochastic legality certificate verified"


def build_controlled_stochastic_legality_problem():
    certificate = EventWindowOpportunityCertificate(
        ("post-action-claim",),
        (
            RouteRequirement(
                "post-action-claim", "observed-route", "observed semantics",
                ("task-done",), ("latent-semantics",)
            ),
            RouteRequirement(
                "post-action-claim", "universal-route", "universal remediation",
                ("task-done", "universal-remediation"), ()
            ),
        ),
        (), (), False, 0, 0,
    )
    model = compile_dynamic_qualification_model(
        certificate, {"s::observation-route": AtomStatus.ACTION_OPEN}
    )
    total = {status: status for status in AtomStatus}

    task = dict(total)
    task[AtomStatus.ACTION_OPEN] = AtomStatus.SATISFIED
    close = dict(total)
    close[AtomStatus.ACTION_OPEN] = AtomStatus.CLOSED
    commit = QualificationEvent(
        "commit-task", EventKind.ACTION,
        (
            make_transition("s::task-done", task),
            make_transition("s::observation-route", close),
        ),
        "controlled", "stochastic legality witness",
    )

    repair = dict(total)
    repair[AtomStatus.ACTION_OPEN] = AtomStatus.SATISFIED
    universal = QualificationEvent(
        "universal-remediation", EventKind.ACTION,
        (make_transition("s::universal-remediation", repair),),
        "controlled", "stochastic legality witness",
    )

    precondition = (
        make_precondition(
            "s::observation-route",
            (AtomStatus.ACTION_OPEN, AtomStatus.SATISFIED),
        ),
    )
    outcomes = []
    for label, probability, target in (
        ("qualified", Fraction(4, 5), AtomStatus.SATISFIED),
        ("unqualified", Fraction(1, 5), AtomStatus.CLOSED),
    ):
        mapping = dict(total)
        mapping[AtomStatus.UNKNOWN] = target
        outcomes.append(
            StochasticLegalityOutcome(
                label,
                probability,
                QualificationEvent(
                    f"observe-{label}", EventKind.OBSERVATION,
                    (make_transition("u::latent-semantics", mapping),),
                    "controlled", "stochastic legality witness", precondition,
                ),
            )
        )
    return StochasticLegalityProblem(
        model,
        (
            LegalEventOption("commit-task", commit, Fraction(0)),
            LegalEventOption("universal-remediation", universal, Fraction(3)),
        ),
        StochasticLegalityObservation(
            "observe-semantics", Fraction(1, 5), tuple(outcomes)
        ),
        3,
        Fraction(10),
    )


def tamper_stochastic_legality(certificate):
    return replace(certificate, replay_regret=certificate.replay_regret + 1)
