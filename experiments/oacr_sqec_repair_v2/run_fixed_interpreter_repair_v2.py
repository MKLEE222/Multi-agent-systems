"""OACR-SQEC v2 fixed-interpreter matched representation repairs."""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass, replace
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

PROTOCOL = "OACR_SQEC_FIXED_INTERPRETER_REPAIR_V2"
PROTOCOL_COMMIT = "3b030fed64a44e018d527568ec2ee55084958d91"
EXECUTOR_ID = "dynamic_qualification_frontier.apply_qualification_event"
EXECUTOR_SOURCE_BLOB_SHA = "0ff2fb8e3d1f532998bceb673b1ab9ef1402b408"

ROUTE_ATOM = "s::observation-route"
TASK_ATOM = "s::task-done"
LATENT_ATOM = "u::latent-semantics"
OBS_EVENTS = ("observe-qualified", "observe-unqualified")
EVENT_ORDER = (
    "commit-task",
    "universal-remediation",
    "observe-qualified",
    "observe-unqualified",
)
ROUTE_ALLOWED = (AtomStatus.ACTION_OPEN, AtomStatus.SATISFIED)
ALL_STATUSES = tuple(sorted(tuple(AtomStatus), key=lambda x: x.value))
VARIANT_TARGETS = (
    AtomStatus.CLOSED,
    AtomStatus.SATISFIED,
    AtomStatus.UNKNOWN,
    AtomStatus.ACTION_OPEN,
    AtomStatus.UNKNOWN,
    AtomStatus.SATISFIED,
    AtomStatus.CLOSED,
    AtomStatus.ACTION_OPEN,
    AtomStatus.CLOSED,
    AtomStatus.SATISFIED,
    AtomStatus.UNKNOWN,
    AtomStatus.ACTION_OPEN,
)
POSITIVE_VARIANTS = (0, 2, 4, 6, 8, 10)
NEGATIVE_VARIANTS = (1, 3, 5, 7, 9, 11)


@dataclass(frozen=True)
class GuardRule:
    rule_id: str
    atom: str
    allowed: tuple[AtomStatus, ...]
    applies_to: tuple[str, ...]


@dataclass(frozen=True)
class ContinuationRepresentation:
    representation_id: str
    guard_rules: tuple[GuardRule, ...]


@dataclass(frozen=True)
class VariantSkeleton:
    variant: int
    model: object
    events: tuple[QualificationEvent, ...]


def canonical_json(x) -> str:
    return json.dumps(x, sort_keys=True, separators=(",", ":"))


def sha_obj(x) -> str:
    return hashlib.sha256(canonical_json(x).encode()).hexdigest()


def transition_rows(event: QualificationEvent):
    return [
        {
            "atom": t.atom,
            "cases": [[src.value, dst.value] for src, dst in t.cases],
        }
        for t in event.transitions
    ]


def skeleton_payload(s: VariantSkeleton):
    return {
        "variant": s.variant,
        "initial_statuses": [[a, st.value] for a, st in s.model.initial_statuses],
        "events": [
            {
                "event_id": e.event_id,
                "kind": e.kind.value,
                "transitions": transition_rows(e),
                "evidence_basis": e.evidence_basis,
                "source": e.source,
                "preconditions": [],
            }
            for e in s.events
        ],
    }


def representation_payload(r: ContinuationRepresentation):
    return {
        "representation_id": r.representation_id,
        "guard_rules": [
            {
                "rule_id": g.rule_id,
                "atom": g.atom,
                "allowed": [x.value for x in g.allowed],
                "applies_to": list(g.applies_to),
            }
            for g in r.guard_rules
        ],
    }


def build_skeleton(index: int) -> VariantSkeleton:
    if index not in range(12):
        raise ValueError("variant index must be 0..11")

    cert = EventWindowOpportunityCertificate(
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
        cert, {ROUTE_ATOM: AtomStatus.ACTION_OPEN}
    )

    total = {status: status for status in AtomStatus}

    task = dict(total)
    task[AtomStatus.ACTION_OPEN] = AtomStatus.SATISFIED
    task[AtomStatus.SATISFIED] = AtomStatus.SATISFIED

    route_target = VARIANT_TARGETS[index]
    route = {status: route_target for status in AtomStatus}

    commit = QualificationEvent(
        "commit-task",
        EventKind.ACTION,
        (
            make_transition(TASK_ATOM, task),
            make_transition(ROUTE_ATOM, route),
        ),
        "controlled",
        f"oacr-sqec-v2-variant-{index}",
        (),
    )

    remediation = dict(total)
    remediation[AtomStatus.ACTION_OPEN] = AtomStatus.SATISFIED
    universal = QualificationEvent(
        "universal-remediation",
        EventKind.ACTION,
        (make_transition("s::universal-remediation", remediation),),
        "controlled",
        f"oacr-sqec-v2-variant-{index}",
        (),
    )

    obs = []
    for label, target in (
        ("qualified", AtomStatus.SATISFIED),
        ("unqualified", AtomStatus.CLOSED),
    ):
        mapping = dict(total)
        mapping[AtomStatus.UNKNOWN] = target
        obs.append(
            QualificationEvent(
                f"observe-{label}",
                EventKind.OBSERVATION,
                (make_transition(LATENT_ATOM, mapping),),
                "controlled",
                f"oacr-sqec-v2-variant-{index}",
                (),
            )
        )

    events = (commit, universal, *obs)
    if tuple(e.event_id for e in events) != EVENT_ORDER:
        raise RuntimeError("event order mismatch")
    if any(e.preconditions for e in events):
        raise RuntimeError("transition skeleton must contain no preconditions")
    return VariantSkeleton(index, model, events)


def full_representation(rep_id: str) -> ContinuationRepresentation:
    return ContinuationRepresentation(
        rep_id,
        (
            GuardRule(
                "route-qualified",
                ROUTE_ATOM,
                ROUTE_ALLOWED,
                ("observe-qualified",),
            ),
            GuardRule(
                "route-unqualified",
                ROUTE_ATOM,
                ROUTE_ALLOWED,
                ("observe-unqualified",),
            ),
        ),
    )


def representations():
    return {
        "FULL": full_representation("FULL"),
        "B0": ContinuationRepresentation("B0", ()),
        "B1": full_representation("B1"),
        "B2": ContinuationRepresentation(
            "B2",
            (
                GuardRule(
                    "shared-route-guard",
                    ROUTE_ATOM,
                    ROUTE_ALLOWED,
                    OBS_EVENTS,
                ),
            ),
        ),
        "B3": ContinuationRepresentation(
            "B3",
            (
                GuardRule(
                    "shared-sham-task-guard",
                    TASK_ATOM,
                    ALL_STATUSES,
                    OBS_EVENTS,
                ),
            ),
        ),
    }


def compile_representation(
    skeleton: VariantSkeleton,
    representation: ContinuationRepresentation,
) -> tuple[QualificationEvent, ...]:
    """The one fixed representation -> native-event compiler."""
    known = set(EVENT_ORDER)
    pre_by_event: dict[str, list] = {eid: [] for eid in EVENT_ORDER}

    for rule in representation.guard_rules:
        if not rule.rule_id:
            raise ValueError("guard rule id must be nonempty")
        if not rule.applies_to:
            raise ValueError("guard rule must apply to at least one event")
        pre = make_precondition(rule.atom, rule.allowed)
        for event_id in rule.applies_to:
            if event_id not in known:
                raise ValueError(f"unknown event in rule: {event_id}")
            pre_by_event[event_id].append(pre)

    compiled = []
    for event in skeleton.events:
        preconditions = tuple(
            sorted(
                pre_by_event[event.event_id],
                key=lambda x: (x.atom, tuple(s.value for s in x.allowed)),
            )
        )
        compiled.append(replace(event, preconditions=preconditions))
    return tuple(compiled)


def event_catalog(events):
    d = {e.event_id: e for e in events}
    if tuple(d) != EVENT_ORDER:
        raise RuntimeError("compiled event order mismatch")
    return d


def status_rows(snapshot):
    return [[atom, status.value] for atom, status in snapshot.atom_statuses]


def execute_sequence(skeleton: VariantSkeleton, events, seq):
    catalog = event_catalog(events)
    snap = initial_dynamic_snapshot(skeleton.model)
    for step, event_id in enumerate(seq, start=1):
        try:
            snap = apply_qualification_event(
                skeleton.model, snap, catalog[event_id]
            )
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


def sequence_bank():
    rows = []
    for length in (1, 2):
        rows.extend(product(EVENT_ORDER, repeat=length))
    return tuple(rows)


def matrix(skeleton, representation):
    compiled = compile_representation(skeleton, representation)
    out = {}
    for seq in sequence_bank():
        payload = execute_sequence(skeleton, compiled, seq)
        key = ">".join(seq)
        out[key] = {
            "signature": sha_obj(payload),
            "payload": payload,
        }
    return out


def mismatch_keys(reference, candidate, length):
    want_sep = ">" if length == 2 else None
    keys = []
    for key in reference:
        is_h2 = ">" in key
        if (length == 2) != is_h2:
            continue
        if reference[key]["signature"] != candidate[key]["signature"]:
            keys.append(key)
    return keys


def expected_delayed_keys(index):
    if index not in POSITIVE_VARIANTS:
        return []
    return [
        "commit-task>observe-qualified",
        "commit-task>observe-unqualified",
    ]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    reps = representations()
    rep_manifest = {k: representation_payload(v) for k, v in reps.items()}
    rep_costs = {k: len(v.guard_rules) for k, v in reps.items()}

    rows = []
    aggregate = {
        key: {"h1": 0, "h2": 0}
        for key in ("B0", "B1", "B2", "B3")
    }
    skeleton_digests = {}

    for index in range(12):
        skeleton = build_skeleton(index)
        skel_sha = sha_obj(skeleton_payload(skeleton))
        skeleton_digests[str(index)] = skel_sha

        matrices = {
            name: matrix(skeleton, rep)
            for name, rep in reps.items()
        }
        full = matrices["FULL"]

        row = {
            "variant": index,
            "post_commit_route": VARIANT_TARGETS[index].value,
            "expected_positive": index in POSITIVE_VARIANTS,
            "skeleton_sha256": skel_sha,
            "matrices": matrices,
            "mismatches": {},
        }

        expected = expected_delayed_keys(index)
        for name in ("B0", "B1", "B2", "B3"):
            h1 = mismatch_keys(full, matrices[name], 1)
            h2 = mismatch_keys(full, matrices[name], 2)
            row["mismatches"][name] = {"h1": h1, "h2": h2}
            aggregate[name]["h1"] += len(h1)
            aggregate[name]["h2"] += len(h2)

            if h1:
                raise RuntimeError(
                    f"variant {index} {name} violates H1 invariance: {h1}"
                )

            if name in ("B0", "B3"):
                if h2 != expected:
                    raise RuntimeError(
                        f"variant {index} {name} H2 mismatch set "
                        f"{h2} != frozen {expected}"
                    )
            else:
                if h2:
                    raise RuntimeError(
                        f"variant {index} {name} should be exact: {h2}"
                    )

        rows.append(row)

    required = {
        "B0": {"h1": 0, "h2": 12},
        "B1": {"h1": 0, "h2": 0},
        "B2": {"h1": 0, "h2": 0},
        "B3": {"h1": 0, "h2": 12},
    }
    if aggregate != required:
        raise RuntimeError(f"aggregate mismatch {aggregate} != {required}")

    out = {
        "protocol": PROTOCOL,
        "protocol_commit": PROTOCOL_COMMIT,
        "executor": {
            "id": EXECUTOR_ID,
            "source_blob_sha": EXECUTOR_SOURCE_BLOB_SHA,
        },
        "fixed_compiler": {
            "function": "compile_representation",
            "baseline_varying_input": "ContinuationRepresentation only",
        },
        "variant_targets": [x.value for x in VARIANT_TARGETS],
        "positive_variants": list(POSITIVE_VARIANTS),
        "negative_variants": list(NEGATIVE_VARIANTS),
        "event_order": list(EVENT_ORDER),
        "sequence_count": len(sequence_bank()),
        "representation_manifest": rep_manifest,
        "representation_cost_rules": rep_costs,
        "skeleton_digests": skeleton_digests,
        "summary": {
            "variants": 12,
            "aggregate_mismatches": aggregate,
            "required_aggregate_mismatches": required,
            "fixed_interpreter_gate": True,
            "same_size_B2_B3": rep_costs["B2"] == rep_costs["B3"] == 1,
        },
        "variants": rows,
    }

    p = Path(args.out)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(out, indent=2))
    print(json.dumps(out["summary"], indent=2))


if __name__ == "__main__":
    main()
