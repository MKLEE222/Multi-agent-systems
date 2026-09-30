"""Source-bound compilation of finite qualification windows.

A window is not a retention score.  It is a time-indexed transition of the
existing access/carrier/transform/delivery/semantic route stages.  The source
contract records which coordinates are observed, source-stated, controlled,
or unresolved so that a natural mechanism cannot silently become a natural
policy-effect estimate.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from hashlib import sha256
from pathlib import Path

from qualification_route_stage_contract import (
    RouteStageKind,
    RouteStageValue,
    StagedRouteSnapshot,
    evaluate_staged_route,
)


DELF_EXPECTED_HASHES = {
    "DELF_USENIX_SECURITY_2020.pdf":
        "6f189df5dc501778959035a8e7e23d0b01a4620c45bfb8b436935bfb2fb109e5",
    "DELF_USENIX_SECURITY_2020.txt":
        "135e5f3928bd447bae75ed8c785fb3fe20d45c7f137b139a8b94ee9f1968b940",
}


class EvidenceBasis(str, Enum):
    OBSERVED = "observed"
    SOURCE_STATED = "source-stated"
    CONTROLLED = "controlled"
    UNKNOWN = "unknown"


class WindowRelation(str, Enum):
    WITHIN = "within-window"
    OUTSIDE = "outside-window"
    UNBOUNDED = "unbounded"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class BoundCoordinate:
    name: str
    value: str
    basis: EvidenceBasis
    source: str


@dataclass(frozen=True)
class QualificationWindowEpisode:
    episode_id: str
    carrier: str
    claim: str
    action: str
    route: str
    post_action: StagedRouteSnapshot
    at_demand: StagedRouteSnapshot
    window_relation: WindowRelation
    timing_basis: EvidenceBasis
    demand_observed: bool
    consequence_observed: bool
    consequence: str
    evidence_grade: str
    exact_window_duration_observed: bool
    natural_action_assignment_observed: bool
    coordinates: tuple[BoundCoordinate, ...]

    @property
    def qualification_post_action(self) -> bool | None:
        return evaluate_staged_route(self.post_action)

    @property
    def qualification_at_demand(self) -> bool | None:
        return evaluate_staged_route(self.at_demand)


@dataclass(frozen=True)
class QualificationWindowContract:
    compiler_version: str
    source_hashes: tuple[tuple[str, str], ...]
    source_url: str
    episodes: tuple[QualificationWindowEpisode, ...]
    natural_policy_regret_identified: bool


def _digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _stage(
    name: str,
    kind: RouteStageKind,
    value: bool | None,
    source: str,
) -> RouteStageValue:
    return RouteStageValue(name, kind, value, source)


def _snapshot(
    snapshot_id: str,
    claim: str,
    route: str,
    values: tuple[bool | None, bool | None, bool | None, bool | None, bool | None],
    sources: tuple[str, str, str, str, str],
) -> StagedRouteSnapshot:
    names = (
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
            _stage(name, kind, value, source)
            for (name, kind), value, source in zip(names, values, sources)
        ),
    )


def _require_markers(text: str, markers: tuple[str, ...]) -> None:
    missing = tuple(marker for marker in markers if marker not in text)
    if missing:
        raise ValueError(f"DELF source missing registered evidence markers: {missing}")


def compile_delf_qualification_windows(upstream: Path) -> QualificationWindowContract:
    """Compile three distinct DELF qualification states from the pinned paper.

    The observed device and expiry episodes support a natural mechanism and
    consequence (Grade B+).  The intervening-state example is explicitly a
    source-stated semantic counterexample, not an observed incident.
    """

    hashes = []
    for name, expected in DELF_EXPECTED_HASHES.items():
        path = upstream / name
        if not path.is_file():
            raise ValueError(f"missing pinned DELF source: {name}")
        observed = _digest(path)
        if observed != expected:
            raise ValueError(f"source hash mismatch for {name}")
        hashes.append((name, observed))

    text = (upstream / "DELF_USENIX_SECURITY_2020.txt").read_text(encoding="utf-8")
    _require_markers(
        text,
        (
            "Both should be retained for the\nmaximum period permitted by the deletion policy.",
            "Restorations may be unsafe to perform.",
            "if another user subsequently claims the phone num-\nber",
            "We in-\nspect all 21 such incidents between February and December\n2019",
            "detected before restoration logs expire",
            "approximately 100 million devices",
            "same day. The recovery process spanned 12 hours",
            "remained un-\ndetected for 2 years",
            "policy allowed DELF restoration logs to persist",
        ),
    )

    url = "https://www.usenix.org/system/files/sec20-cohn-gordon.pdf"
    common_open_sources = (
        "DELF restoration logs indexed for retrieval",
        "serialized deleted graph remains inside policy window",
        "reverse-order staged restoration is available",
        "restoration result can be delivered",
        "restored object preserves the demanded identity",
    )

    device_claim = "recover the inadvertently deleted device objects"
    device_route = "DELF restoration log plus staged reverse traversal"
    device_post = _snapshot(
        "delf-devices-post-delete",
        device_claim,
        device_route,
        (True, True, True, True, True),
        common_open_sources,
    )
    device_demand = _snapshot(
        "delf-devices-same-day-demand",
        device_claim,
        device_route,
        (True, True, True, True, True),
        common_open_sources,
    )
    device = QualificationWindowEpisode(
        "delf-100m-devices-within-window",
        "Facebook DELF production deletion",
        device_claim,
        "cleanup migration deletes selected device objects",
        device_route,
        device_post,
        device_demand,
        WindowRelation.WITHIN,
        EvidenceBasis.OBSERVED,
        True,
        True,
        "product alerts detected the deletion the same day; recovery spanned 12 hours",
        "B+",
        False,
        False,
        (
            BoundCoordinate("affected-objects", "approximately 100 million devices", EvidenceBasis.OBSERVED, url),
            BoundCoordinate("detection-time", "same day", EvidenceBasis.OBSERVED, url),
            BoundCoordinate("recovery-duration", "12 hours", EvidenceBasis.OBSERVED, url),
            BoundCoordinate("retention-duration", "unreported policy-bounded duration", EvidenceBasis.UNKNOWN, url),
        ),
    )

    expired_claim = "recover video objects deleted by erroneous application logic"
    expired_route = "DELF restoration log after delayed detection"
    expired_post = _snapshot(
        "delf-video-post-delete",
        expired_claim,
        expired_route,
        (True, True, True, None, None),
        (
            "restoration log exists immediately after deletion",
            "serialized deleted graph exists immediately after deletion",
            "DELF restoration machinery exists",
            "later delivery outcome not yet determined",
            "later semantic consistency not yet determined",
        ),
    )
    expired_demand = _snapshot(
        "delf-video-two-year-demand",
        expired_claim,
        expired_route,
        (False, False, True, False, None),
        (
            "detection occurred after the permitted persistence period",
            "restoration logs no longer persisted",
            "DELF restoration machinery still exists",
            "no carrier remains to deliver a restored result",
            "paper does not identify semantic consistency of a hypothetical restore",
        ),
    )
    expired = QualificationWindowEpisode(
        "delf-video-outside-window",
        "Facebook DELF production deletion",
        expired_claim,
        "application logic deletes the wrong video objects",
        expired_route,
        expired_post,
        expired_demand,
        WindowRelation.OUTSIDE,
        EvidenceBasis.OBSERVED,
        True,
        True,
        "user reports surfaced the bug after two years, beyond log persistence; significant data loss occurred",
        "B+",
        False,
        False,
        (
            BoundCoordinate("detection-delay", "2 years", EvidenceBasis.OBSERVED, url),
            BoundCoordinate("window-comparison", "significantly longer than permitted persistence", EvidenceBasis.OBSERVED, url),
            BoundCoordinate("exact-retention-duration", "unreported", EvidenceBasis.UNKNOWN, url),
        ),
    )

    conflict_claim = "restore a deleted user account under its original phone identity"
    conflict_route = "DELF restoration log after phone-number reassignment"
    conflict_post = _snapshot(
        "delf-account-post-delete",
        conflict_claim,
        conflict_route,
        (True, True, True, True, True),
        common_open_sources,
    )
    conflict_demand = _snapshot(
        "delf-account-intervening-state-demand",
        conflict_claim,
        conflict_route,
        (True, True, True, False, False),
        (
            "restoration request can access the retained log",
            "serialized account graph is assumed present",
            "staged reverse traversal checks dependencies",
            "restoration fails early when phone restoration is impossible",
            "the original phone identity now belongs to another user",
        ),
    )
    conflict = QualificationWindowEpisode(
        "delf-phone-reassignment-with-carrier",
        "DELF source-stated restoration counterexample",
        conflict_claim,
        "another user claims the deleted account's phone number before restoration",
        conflict_route,
        conflict_post,
        conflict_demand,
        WindowRelation.WITHIN,
        EvidenceBasis.SOURCE_STATED,
        False,
        False,
        "the paper states that restoration should no longer be feasible and must fail early",
        "C",
        False,
        False,
        (
            BoundCoordinate("intervening-state", "phone number reassigned", EvidenceBasis.SOURCE_STATED, url),
            BoundCoordinate("carrier-at-demand", "assumed retained for the counterexample", EvidenceBasis.SOURCE_STATED, url),
            BoundCoordinate("realized-incident", "not reported", EvidenceBasis.UNKNOWN, url),
        ),
    )

    return QualificationWindowContract(
        "qualification-window-compiler-v0",
        tuple(sorted(hashes)),
        url,
        (device, expired, conflict),
        natural_policy_regret_identified=False,
    )


def adapt_pathology_recovery_windows(contract) -> QualificationWindowContract:
    """Adapt documented specimen alternatives without inventing timing.

    The adapter intentionally leaves every window relation unknown.  A
    successful alternative assay establishes a qualified route at demand, but
    the source does not report an expiry law or randomized retention action.
    """

    episodes = []
    for item in contract.alternative_routes:
        claim = f"obtain a qualified NGS result for specimen {item.source_specimen}"
        route = item.alternative_route
        sources = (
            "documented alternative route is accessible in the episode",
            "documented alternative specimen or smear is available",
            "alternative route produced an NGS result",
            "alternative result is reported",
            item.relation,
        )
        snapshot = _snapshot(
            f"pathology-{item.episode_id}-demand",
            claim,
            route,
            (True, True, True, True, True),
            sources,
        )
        episodes.append(
            QualificationWindowEpisode(
                item.episode_id,
                "clinical limited-specimen NGS cohort",
                claim,
                "retain or obtain the documented alternative specimen route",
                route,
                snapshot,
                snapshot,
                WindowRelation.UNKNOWN,
                EvidenceBasis.UNKNOWN,
                True,
                True,
                item.alternative_result,
                "B",
                False,
                False,
                (
                    BoundCoordinate("route-existed-before-source-failure", str(item.route_existed_before_source_failure).lower(), EvidenceBasis.OBSERVED, contract.publisher_url),
                    BoundCoordinate("expiry-law", "unreported", EvidenceBasis.UNKNOWN, contract.publisher_url),
                    BoundCoordinate("natural-action-cost", "unreported", EvidenceBasis.UNKNOWN, contract.publisher_url),
                ),
            )
        )
    return QualificationWindowContract(
        "qualification-window-compiler-v0",
        contract.source_hashes,
        contract.publisher_url,
        tuple(episodes),
        natural_policy_regret_identified=False,
    )


def verify_delf_qualification_windows(
    upstream: Path,
    certificate: QualificationWindowContract,
) -> tuple[bool, str]:
    try:
        expected = compile_delf_qualification_windows(upstream)
    except ValueError as exc:
        return False, str(exc)
    if expected != certificate:
        return False, "qualification-window contract mismatch"
    return True, "qualification-window contract verified"


def tamper_window_certificate(
    certificate: QualificationWindowContract,
) -> QualificationWindowContract:
    episode = certificate.episodes[0]
    stage = episode.at_demand.stages[1]
    damaged_stage = replace(stage, qualified=False)
    damaged_snapshot = replace(
        episode.at_demand,
        stages=(episode.at_demand.stages[0], damaged_stage, *episode.at_demand.stages[2:]),
    )
    damaged_episode = replace(episode, at_demand=damaged_snapshot)
    return replace(certificate, episodes=(damaged_episode, *certificate.episodes[1:]))
