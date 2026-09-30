"""Prospective OACR-SQEC continuation-repair confirmation family."""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict, replace
from fractions import Fraction
from itertools import product
from pathlib import Path

from dynamic_qualification_frontier import (
    AtomStatus,
    EventKind,
    QualificationEvent,
    apply_qualification_event,
    compile_dynamic_qualification_model,
    initial_dynamic_snapshot,
    make_precondition,
    make_transition,
)
from event_window_opportunity import EventWindowOpportunityCertificate, RouteRequirement
from multistep_observation_legality import LegalEventOption
from stochastic_multistep_legality import (
    StochasticLegalityObservation,
    StochasticLegalityOutcome,
    StochasticLegalityProblem,
    project_stochastic_legality,
)

PROTOCOL = "OACR_SQEC_CONTINUATION_REPAIR_V1"
PROTOCOL_COMMIT = "83091035685b8d11fc1b293051285835d9c1feb7"
VARIANT_TARGETS = (
    AtomStatus.CLOSED,
    AtomStatus.SATISFIED,
    AtomStatus.CLOSED,
    AtomStatus.ACTION_OPEN,
    AtomStatus.CLOSED,
    AtomStatus.SATISFIED,
    AtomStatus.CLOSED,
    AtomStatus.ACTION_OPEN,
)
GUARD_ATOM = "s::observation-route"
GUARD_ALLOWED = (AtomStatus.ACTION_OPEN, AtomStatus.SATISFIED)
EVENT_ORDER = (
    "commit-task",
    "universal-remediation",
    "observe-qualified",
    "observe-unqualified",
)


def build_variant(index: int) -> StochasticLegalityProblem:
    if index not in range(8):
        raise ValueError("variant index must be 0..7")
    certificate = EventWindowOpportunityCertificate(
        ("post-action-claim",),
        (
            RouteRequirement(
                "post-action-claim",
                "observed-route",
                "observed semantics",
                ("task-done",),
                ("latent-semantics",),
            ),
            RouteRequirement(
                "post-action-claim",
                "universal-route",
                "universal remediation",
                ("task-done", "universal-remediation"),
                (),
            ),
        ),
        (),
        (),
        False,
        0,
        0,
    )
    model = compile_dynamic_qualification_model(
        certificate, {GUARD_ATOM: AtomStatus.ACTION_OPEN}
    )
    total = {status: status for status in AtomStatus}

    task = dict(total)
    task[AtomStatus.ACTION_OPEN] = AtomStatus.SATISFIED
    task[AtomStatus.SATISFIED] = AtomStatus.SATISFIED
    route = dict(total)
    route_target = VARIANT_TARGETS[index]
    for status in AtomStatus:
        route[status] = route_target
    commit = QualificationEvent(
        "commit-task",
        EventKind.ACTION,
        (
            make_transition("s::task-done", task),
            make_transition(GUARD_ATOM, route),
        ),
        "controlled",
        f"oacr-sqec-variant-{index}",
    )

    repair = dict(total)
    repair[AtomStatus.ACTION_OPEN] = AtomStatus.SATISFIED
    universal = QualificationEvent(
        "universal-remediation",
        EventKind.ACTION,
        (make_transition("s::universal-remediation", repair),),
        "controlled",
        f"oacr-sqec-variant-{index}",
    )

    precondition = (make_precondition(GUARD_ATOM, GUARD_ALLOWED),)
    outcomes = []
    for label, target in (
        ("qualified", AtomStatus.SATISFIED),
        ("unqualified", AtomStatus.CLOSED),
    ):
        mapping = dict(total)
        mapping[AtomStatus.UNKNOWN] = target
        outcomes.append(
            StochasticLegalityOutcome(
                label,
                Fraction(1, 2),
                QualificationEvent(
                    f"observe-{label}",
                    EventKind.OBSERVATION,
                    (make_transition("u::latent-semantics", mapping),),
                    "controlled",
                    f"oacr-sqec-variant-{index}",
                    precondition,
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


def canonical_guard_repair(projected: StochasticLegalityProblem) -> StochasticLegalityProblem:
    pre = (make_precondition(GUARD_ATOM, GUARD_ALLOWED),)
    outcomes = tuple(
        replace(outcome, event=replace(outcome.event, preconditions=pre))
        for outcome in projected.observation.outcomes
    )
    return replace(
        projected,
        observation=replace(projected.observation, outcomes=outcomes),
    )


def event_catalog(problem: StochasticLegalityProblem) -> dict[str, QualificationEvent]:
    result = {item.event.event_id: item.event for item in problem.actions}
    result.update(
        {item.event.event_id: item.event for item in problem.observation.outcomes}
    )
    if tuple(result) != EVENT_ORDER:
        # dict insertion order should follow action then outcome order.
        if set(result) != set(EVENT_ORDER):
            raise RuntimeError(f"event alphabet mismatch: {tuple(result)}")
    return result


def status_rows(snapshot):
    return [[atom, status.value] for atom, status in snapshot.atom_statuses]


def execute_sequence(problem: StochasticLegalityProblem, seq: tuple[str, ...]):
    catalog = event_catalog(problem)
    snap = initial_dynamic_snapshot(problem.model)
    for step, event_id in enumerate(seq, start=1):
        try:
            snap = apply_qualification_event(problem.model, snap, catalog[event_id])
        except ValueError as exc:
            if "is illegal" not in str(exc):
                raise
            return {
                "legal": False,
                "illegal_at": step,
                "illegal_event": event_id,
                "prefix_atom_statuses": status_rows(snap),
                "prefix_joint_state": snap.joint_state.value,
            }
    return {
        "legal": True,
        "final_atom_statuses": status_rows(snap),
        "final_joint_state": snap.joint_state.value,
    }


def signature(payload) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def sequence_bank():
    out = []
    for length in (1, 2):
        out.extend(product(EVENT_ORDER, repeat=length))
    return tuple(out)


def compare_matrix(reference, candidate):
    mismatches = []
    for key in reference:
        if reference[key]["signature"] != candidate[key]["signature"]:
            mismatches.append(key)
    return mismatches


def matrix(problem):
    result = {}
    for seq in sequence_bank():
        payload = execute_sequence(problem, seq)
        key = ">".join(seq)
        result[key] = {"signature": signature(payload), "payload": payload}
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    variants = []
    total_proj_h1 = total_proj_h2 = 0
    total_repair_mismatch = 0

    for index in range(8):
        full = build_variant(index)
        projected = project_stochastic_legality(full)
        repaired = canonical_guard_repair(projected)

        mf = matrix(full)
        mp = matrix(projected)
        mr = matrix(repaired)

        h1_keys = [k for k in mf if ">" not in k]
        h2_keys = [k for k in mf if ">" in k]

        proj_h1 = [k for k in h1_keys if mf[k]["signature"] != mp[k]["signature"]]
        proj_h2 = [k for k in h2_keys if mf[k]["signature"] != mp[k]["signature"]]
        rep_all = [k for k in mf if mf[k]["signature"] != mr[k]["signature"]]

        total_proj_h1 += len(proj_h1)
        total_proj_h2 += len(proj_h2)
        total_repair_mismatch += len(rep_all)

        expected_positive = index in {0, 2, 4, 6}
        if proj_h1:
            raise RuntimeError(f"variant {index} violates frozen H1 gate: {proj_h1}")
        if expected_positive and not proj_h2:
            raise RuntimeError(f"variant {index} missing delayed divergence")
        if not expected_positive and proj_h2:
            raise RuntimeError(
                f"variant {index} no-divergence control unexpectedly differs: {proj_h2}"
            )
        if rep_all:
            raise RuntimeError(f"variant {index} guard repair mismatch: {rep_all}")

        variants.append(
            {
                "variant": index,
                "post_commit_route": VARIANT_TARGETS[index].value,
                "expected_delayed_guard_positive": expected_positive,
                "projected_h1_mismatches": proj_h1,
                "projected_h2_mismatches": proj_h2,
                "repaired_all_mismatches": rep_all,
                "full_matrix": mf,
                "projected_matrix": mp,
                "repaired_matrix": mr,
            }
        )

    out = {
        "protocol": PROTOCOL,
        "protocol_commit": PROTOCOL_COMMIT,
        "variant_targets": [x.value for x in VARIANT_TARGETS],
        "guard": {
            "atom": GUARD_ATOM,
            "allowed": [x.value for x in GUARD_ALLOWED],
        },
        "event_order": list(EVENT_ORDER),
        "sequence_count": len(sequence_bank()),
        "representation_accounting": {
            "full_observation_precondition_clauses": 2,
            "canonical_repair_guard_rules": 1,
        },
        "summary": {
            "variants": 8,
            "projected_h1_mismatches": total_proj_h1,
            "projected_h2_mismatches": total_proj_h2,
            "repaired_depth_le_2_mismatches": total_repair_mismatch,
            "positive_control_variants": [0, 2, 4, 6],
            "negative_control_variants": [1, 3, 5, 7],
        },
        "variants": variants,
    }

    p = Path(args.out)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(out, indent=2))
    print(json.dumps(out["summary"], indent=2))


if __name__ == "__main__":
    main()
