"""Typed stages for action-conditioned evidence routes.

The same action can affect route access, the evidence-bearing carrier, the
validity of an evidence-producing transformation, result delivery, and the
semantic claim mapping differently.  A workflow label or one resource scalar
is therefore a projection of the route state rather than the route state.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum


class RouteStageKind(str, Enum):
    ACCESS = "access"
    CARRIER = "carrier"
    TRANSFORM = "transform"
    DELIVERY = "delivery"
    SEMANTIC = "semantic"


@dataclass(frozen=True)
class RouteStageValue:
    name: str
    kind: RouteStageKind
    qualified: bool | None
    source: str


@dataclass(frozen=True)
class StagedRouteSnapshot:
    snapshot_id: str
    claim: str
    route: str
    stages: tuple[RouteStageValue, ...]


@dataclass(frozen=True)
class StageProjectionCertificate:
    claim: str
    route: str
    retained_kinds: tuple[RouteStageKind, ...]
    retained_signature: tuple[tuple[str, bool | None], ...]
    left_snapshot: str
    right_snapshot: str
    left_qualification: bool | None
    right_qualification: bool | None
    omitted_distinguishing_stages: tuple[str, ...]


@dataclass(frozen=True)
class StageTransitionCertificate:
    action: str
    claim: str
    route: str
    opened_stages: tuple[str, ...]
    closed_stages: tuple[str, ...]
    preserved_stages: tuple[str, ...]
    unresolved_stages: tuple[str, ...]
    qualification_before: bool | None
    qualification_after: bool | None


def _validate(snapshot: StagedRouteSnapshot) -> None:
    names = [stage.name for stage in snapshot.stages]
    if (
        not snapshot.snapshot_id
        or not snapshot.claim
        or not snapshot.route
        or not snapshot.stages
        or any(not stage.name or not stage.source for stage in snapshot.stages)
        or len(set(names)) != len(names)
    ):
        raise ValueError("invalid staged qualification route")


def evaluate_staged_route(snapshot: StagedRouteSnapshot) -> bool | None:
    _validate(snapshot)
    values = tuple(stage.qualified for stage in snapshot.stages)
    if False in values:
        return False
    if None in values:
        return None
    return True


def _by_name(snapshot: StagedRouteSnapshot) -> dict[str, RouteStageValue]:
    _validate(snapshot)
    return {stage.name: stage for stage in snapshot.stages}


def certify_stage_projection_insufficiency(
    left: StagedRouteSnapshot,
    right: StagedRouteSnapshot,
    retained_kinds: tuple[RouteStageKind, ...],
) -> StageProjectionCertificate:
    if not retained_kinds or len(set(retained_kinds)) != len(retained_kinds):
        raise ValueError("retained route-stage kinds must be nonempty and unique")
    if left.claim != right.claim or left.route != right.route:
        raise ValueError("projection witness must compare the same claim route")
    left_by_name = _by_name(left)
    right_by_name = _by_name(right)
    if set(left_by_name) != set(right_by_name):
        raise ValueError("projection witness stage names differ")
    for name in left_by_name:
        if left_by_name[name].kind != right_by_name[name].kind:
            raise ValueError("projection witness stage kinds differ")

    retained = set(retained_kinds)
    left_signature = tuple(
        sorted(
            (stage.name, stage.qualified)
            for stage in left.stages
            if stage.kind in retained
        )
    )
    right_signature = tuple(
        sorted(
            (stage.name, stage.qualified)
            for stage in right.stages
            if stage.kind in retained
        )
    )
    if not left_signature:
        raise ValueError("projection retains no observed route stage")
    if left_signature != right_signature:
        raise ValueError("projected route states are distinguishable")
    left_q = evaluate_staged_route(left)
    right_q = evaluate_staged_route(right)
    if left_q is None or right_q is None or left_q == right_q:
        raise ValueError("projection witness lacks opposite qualification")
    omitted = tuple(
        sorted(
            name
            for name in left_by_name
            if left_by_name[name].kind not in retained
            and left_by_name[name].qualified != right_by_name[name].qualified
        )
    )
    if not omitted:
        raise ValueError("no omitted stage explains qualification separation")
    return StageProjectionCertificate(
        left.claim,
        left.route,
        tuple(retained_kinds),
        left_signature,
        left.snapshot_id,
        right.snapshot_id,
        left_q,
        right_q,
        omitted,
    )


def certify_stage_transition(
    action: str,
    before: StagedRouteSnapshot,
    after: StagedRouteSnapshot,
) -> StageTransitionCertificate:
    if not action or before.claim != after.claim or before.route != after.route:
        raise ValueError("invalid staged route transition")
    before_by_name = _by_name(before)
    after_by_name = _by_name(after)
    if set(before_by_name) != set(after_by_name):
        raise ValueError("route stages change identity across action")
    opened = []
    closed = []
    preserved = []
    unresolved = []
    for name in sorted(before_by_name):
        left = before_by_name[name]
        right = after_by_name[name]
        if left.kind != right.kind:
            raise ValueError("route-stage kind changes across action")
        pair = (left.qualified, right.qualified)
        if pair == (False, True):
            opened.append(name)
        elif pair == (True, False):
            closed.append(name)
        elif left.qualified is None or right.qualified is None:
            unresolved.append(name)
        else:
            preserved.append(name)
    return StageTransitionCertificate(
        action,
        before.claim,
        before.route,
        tuple(opened),
        tuple(closed),
        tuple(preserved),
        tuple(unresolved),
        evaluate_staged_route(before),
        evaluate_staged_route(after),
    )


def verify_stage_projection_certificate(
    left: StagedRouteSnapshot,
    right: StagedRouteSnapshot,
    certificate: StageProjectionCertificate,
) -> tuple[bool, str]:
    try:
        expected = certify_stage_projection_insufficiency(
            left, right, certificate.retained_kinds
        )
    except ValueError as exc:
        return False, str(exc)
    if expected != certificate:
        return False, "route-stage projection certificate mismatch"
    return True, "route-stage projection certificate verified"


def tamper_stage_projection_certificate(
    certificate: StageProjectionCertificate,
) -> StageProjectionCertificate:
    return replace(certificate, omitted_distinguishing_stages=("invented-stage",))
