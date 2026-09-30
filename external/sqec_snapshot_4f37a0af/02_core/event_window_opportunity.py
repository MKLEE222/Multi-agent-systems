"""Symbolic multi-route opportunity over qualification windows.

The compiler first derives an inclusion-minimal frontier of known safeguards
and unresolved coordinates.  Numerical action choice is permitted only after
every required safeguard has a supplied cost and every unresolved coordinate
has been discharged.  This keeps source identification separate from the
generic set-cover/shortest-choice optimization layer.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from fractions import Fraction
from itertools import combinations, product

from qualification_route_stage_contract import RouteStageKind, RouteStageValue, StagedRouteSnapshot
from qualification_window_compiler import (
    BoundCoordinate,
    EvidenceBasis,
    QualificationWindowContract,
    QualificationWindowEpisode,
    WindowRelation,
)


@dataclass(frozen=True)
class RouteRequirement:
    claim: str
    episode_id: str
    route: str
    safeguards: tuple[str, ...]
    unresolved: tuple[str, ...]


@dataclass(frozen=True)
class OpportunityFrontierPoint:
    safeguards: tuple[str, ...]
    unresolved: tuple[str, ...]
    chosen_episodes: tuple[str, ...]


@dataclass(frozen=True)
class EventWindowOpportunityCertificate:
    demanded_claims: tuple[str, ...]
    route_requirements: tuple[RouteRequirement, ...]
    frontier: tuple[OpportunityFrontierPoint, ...]
    safeguard_aliases: tuple[tuple[str, str, str], ...]
    numerical_decision_identified: bool
    combination_expansions: int
    maximum_frontier_width: int


@dataclass(frozen=True)
class CostedOpportunityChoice:
    safeguards: tuple[str, ...]
    chosen_episodes: tuple[str, ...]
    total_cost: Fraction


def _stage_token(episode_id: str, stage_name: str) -> str:
    return f"{episode_id}::{stage_name}"


def _normalize_aliases(aliases):
    rows = tuple(sorted((episode, stage, alias) for (episode, stage), alias in aliases.items()))
    if any(not episode or not stage or not alias for episode, stage, alias in rows):
        raise ValueError("safeguard aliases must be nonempty")
    return rows


def _compile_route_requirement(episode, aliases) -> RouteRequirement:
    safeguards = []
    unresolved = []
    for stage in episode.at_demand.stages:
        token = aliases.get(
            (episode.episode_id, stage.name),
            _stage_token(episode.episode_id, stage.name),
        )
        if stage.qualified is False:
            safeguards.append(token)
        elif stage.qualified is None:
            unresolved.append(token)
    if episode.window_relation == WindowRelation.UNKNOWN:
        unresolved.append(
            aliases.get(
                (episode.episode_id, "window-relation"),
                _stage_token(episode.episode_id, "window-relation"),
            )
        )
    return RouteRequirement(
        episode.claim,
        episode.episode_id,
        episode.route,
        tuple(sorted(set(safeguards))),
        tuple(sorted(set(unresolved))),
    )


def _dominates(left: OpportunityFrontierPoint, right: OpportunityFrontierPoint) -> bool:
    return (
        set(left.safeguards) <= set(right.safeguards)
        and set(left.unresolved) <= set(right.unresolved)
    )


def _prune(points):
    unique = {}
    for point in points:
        key = (point.safeguards, point.unresolved)
        previous = unique.get(key)
        if previous is None or point.chosen_episodes < previous.chosen_episodes:
            unique[key] = point
    values = tuple(unique.values())
    kept = tuple(
        point
        for point in values
        if not any(
            other != point and _dominates(other, point)
            for other in values
        )
    )
    return tuple(sorted(kept, key=lambda item: (item.safeguards, item.unresolved, item.chosen_episodes)))


def compile_event_window_opportunity(
    contract: QualificationWindowContract,
    demanded_claims: tuple[str, ...],
    safeguard_aliases: dict[tuple[str, str], str] | None = None,
) -> EventWindowOpportunityCertificate:
    if not demanded_claims or len(set(demanded_claims)) != len(demanded_claims):
        raise ValueError("demanded claims must be nonempty and unique")
    aliases = dict(safeguard_aliases or {})
    episode_ids = {item.episode_id for item in contract.episodes}
    if any(episode not in episode_ids for episode, _ in aliases):
        raise ValueError("safeguard alias references an unknown episode")

    requirements = tuple(
        _compile_route_requirement(item, aliases)
        for item in contract.episodes
        if item.claim in demanded_claims
    )
    by_claim = {
        claim: tuple(item for item in requirements if item.claim == claim)
        for claim in demanded_claims
    }
    missing = tuple(claim for claim, routes in by_claim.items() if not routes)
    if missing:
        raise ValueError(f"demanded claims have no registered routes: {missing}")

    frontier = (OpportunityFrontierPoint((), (), ()),)
    expansions = 0
    maximum_frontier_width = 1
    for claim in demanded_claims:
        expanded = []
        for prefix, route in product(frontier, by_claim[claim]):
            expansions += 1
            expanded.append(
                OpportunityFrontierPoint(
                    tuple(sorted(set(prefix.safeguards) | set(route.safeguards))),
                    tuple(sorted(set(prefix.unresolved) | set(route.unresolved))),
                    prefix.chosen_episodes + (route.episode_id,),
                )
            )
        frontier = _prune(expanded)
        maximum_frontier_width = max(maximum_frontier_width, len(frontier))

    return EventWindowOpportunityCertificate(
        demanded_claims,
        requirements,
        frontier,
        _normalize_aliases(aliases),
        numerical_decision_identified=all(not point.unresolved for point in frontier),
        combination_expansions=expansions,
        maximum_frontier_width=maximum_frontier_width,
    )


def verify_event_window_opportunity(contract, certificate):
    aliases = {
        (episode, stage): alias
        for episode, stage, alias in certificate.safeguard_aliases
    }
    try:
        expected = compile_event_window_opportunity(
            contract, certificate.demanded_claims, aliases
        )
    except ValueError as exc:
        return False, str(exc)
    if expected != certificate:
        return False, "event-window opportunity certificate mismatch"
    return True, "event-window opportunity certificate verified"


def select_costed_opportunity(certificate, safeguard_costs):
    if not certificate.numerical_decision_identified:
        raise ValueError("opportunity frontier contains unresolved coordinates")
    missing = sorted(
        {
            item
            for point in certificate.frontier
            for item in point.safeguards
            if item not in safeguard_costs
        }
    )
    if missing:
        raise ValueError(f"missing safeguard costs: {missing}")
    if any(Fraction(value) < 0 for value in safeguard_costs.values()):
        raise ValueError("safeguard costs must be nonnegative")
    candidates = tuple(
        CostedOpportunityChoice(
            point.safeguards,
            point.chosen_episodes,
            sum((Fraction(safeguard_costs[item]) for item in point.safeguards), Fraction(0)),
        )
        for point in certificate.frontier
    )
    return min(candidates, key=lambda item: (item.total_cost, item.safeguards, item.chosen_episodes))


def brute_force_opportunity_oracle(certificate):
    """Independent subset oracle over the compiled route requirements."""

    tokens = tuple(
        sorted(
            {
                ("s", token)
                for route in certificate.route_requirements
                for token in route.safeguards
            }
            | {
                ("u", token)
                for route in certificate.route_requirements
                for token in route.unresolved
            }
        )
    )
    by_claim = {
        claim: tuple(
            route for route in certificate.route_requirements if route.claim == claim
        )
        for claim in certificate.demanded_claims
    }
    feasible = []
    for size in range(len(tokens) + 1):
        for subset_tuple in combinations(tokens, size):
            subset = set(subset_tuple)
            if all(
                any(
                    {("s", item) for item in route.safeguards} <= subset
                    and {("u", item) for item in route.unresolved} <= subset
                    for route in by_claim[claim]
                )
                for claim in certificate.demanded_claims
            ):
                feasible.append(subset)
    minimal = tuple(
        subset
        for subset in feasible
        if not any(other < subset for other in feasible)
    )
    return tuple(
        sorted(
            (
                tuple(sorted(token for kind, token in subset if kind == "s")),
                tuple(sorted(token for kind, token in subset if kind == "u")),
            )
            for subset in minimal
        )
    )


def verify_against_opportunity_oracle(certificate):
    compiled = tuple(
        sorted((point.safeguards, point.unresolved) for point in certificate.frontier)
    )
    oracle = brute_force_opportunity_oracle(certificate)
    if compiled != oracle:
        return False, "event-window frontier disagrees with subset oracle"
    return True, "event-window frontier matches subset oracle"


def tamper_event_window_opportunity(certificate):
    point = certificate.frontier[0]
    damaged = replace(point, safeguards=())
    return replace(certificate, frontier=(damaged, *certificate.frontier[1:]))


def _controlled_snapshot(snapshot_id, claim, route, false_kind):
    kinds = (
        ("route-access", RouteStageKind.ACCESS),
        ("evidence-carrier", RouteStageKind.CARRIER),
        ("recovery-transform", RouteStageKind.TRANSFORM),
        ("result-delivery", RouteStageKind.DELIVERY),
        ("claim-semantics", RouteStageKind.SEMANTIC),
    )
    return StagedRouteSnapshot(
        snapshot_id,
        claim,
        route,
        tuple(
            RouteStageValue(name, kind, kind != false_kind, "controlled safeguard family")
            for name, kind in kinds
        ),
    )


def build_controlled_shared_safeguard_family():
    specs = (
        ("a-log", "claim-a", "shared log", RouteStageKind.CARRIER),
        ("a-recollect", "claim-a", "recollect A", RouteStageKind.TRANSFORM),
        ("b-log", "claim-b", "shared log", RouteStageKind.CARRIER),
        ("b-recollect", "claim-b", "recollect B", RouteStageKind.TRANSFORM),
        ("c-identity", "claim-c", "identity guard", RouteStageKind.SEMANTIC),
    )
    episodes = []
    for episode_id, claim, route, false_kind in specs:
        snapshot = _controlled_snapshot(episode_id, claim, route, false_kind)
        episodes.append(
            QualificationWindowEpisode(
                episode_id,
                "controlled shared-safeguard family",
                claim,
                "supply the registered safeguard",
                route,
                snapshot,
                snapshot,
                WindowRelation.UNBOUNDED,
                EvidenceBasis.CONTROLLED,
                False,
                False,
                "controlled",
                "controlled",
                False,
                False,
                (BoundCoordinate("family", "controlled", EvidenceBasis.CONTROLLED, "local"),),
            )
        )
    contract = QualificationWindowContract(
        "controlled-shared-safeguard-v0",
        (),
        "local controlled family",
        tuple(episodes),
        False,
    )
    aliases = {
        ("a-log", "evidence-carrier"): "retain-shared-log",
        ("b-log", "evidence-carrier"): "retain-shared-log",
        ("a-recollect", "recovery-transform"): "recollect-a",
        ("b-recollect", "recovery-transform"): "recollect-b",
        ("c-identity", "claim-semantics"): "preserve-semantic-identity",
    }
    return contract, aliases


def build_controlled_shared_safeguard_scaling_family(width: int):
    if width < 1:
        raise ValueError("shared-safeguard width must be positive")
    episodes = []
    aliases = {}
    claims = []
    for index in range(width):
        claim = f"claim-{index}"
        claims.append(claim)
        shared_id = f"claim-{index}-shared"
        unique_id = f"claim-{index}-unique"
        for episode_id, route, false_kind in (
            (shared_id, "shared safeguard", RouteStageKind.CARRIER),
            (unique_id, f"unique safeguard {index}", RouteStageKind.TRANSFORM),
        ):
            snapshot = _controlled_snapshot(episode_id, claim, route, false_kind)
            episodes.append(
                QualificationWindowEpisode(
                    episode_id,
                    "controlled shared-safeguard scaling family",
                    claim,
                    "supply the registered safeguard",
                    route,
                    snapshot,
                    snapshot,
                    WindowRelation.UNBOUNDED,
                    EvidenceBasis.CONTROLLED,
                    False,
                    False,
                    "controlled",
                    "controlled",
                    False,
                    False,
                    (BoundCoordinate("family", "controlled", EvidenceBasis.CONTROLLED, "local"),),
                )
            )
        aliases[(shared_id, "evidence-carrier")] = "retain-shared-carrier"
        aliases[(unique_id, "recovery-transform")] = f"unique-{index}"
    contract = QualificationWindowContract(
        "controlled-shared-safeguard-scaling-v0",
        (),
        "local controlled family",
        tuple(episodes),
        False,
    )
    return contract, tuple(claims), aliases
