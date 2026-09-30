"""Independent verifier for OACR-SQEC continuation-repair family."""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import replace
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
TARGETS = (
    AtomStatus.CLOSED,
    AtomStatus.SATISFIED,
    AtomStatus.CLOSED,
    AtomStatus.ACTION_OPEN,
    AtomStatus.CLOSED,
    AtomStatus.SATISFIED,
    AtomStatus.CLOSED,
    AtomStatus.ACTION_OPEN,
)
EVENTS = (
    "commit-task",
    "universal-remediation",
    "observe-qualified",
    "observe-unqualified",
)
ATOM = "s::observation-route"
ALLOWED = (AtomStatus.ACTION_OPEN, AtomStatus.SATISFIED)


def build(index):
    cert = EventWindowOpportunityCertificate(
        ("post-action-claim",),
        (
            RouteRequirement(
                "post-action-claim","observed-route","observed semantics",
                ("task-done",),("latent-semantics",)
            ),
            RouteRequirement(
                "post-action-claim","universal-route","universal remediation",
                ("task-done","universal-remediation"),()
            ),
        ),
        (),(),False,0,0,
    )
    model=compile_dynamic_qualification_model(cert,{ATOM:AtomStatus.ACTION_OPEN})
    total={x:x for x in AtomStatus}

    task=dict(total)
    task[AtomStatus.ACTION_OPEN]=AtomStatus.SATISFIED
    task[AtomStatus.SATISFIED]=AtomStatus.SATISFIED
    route={x:TARGETS[index] for x in AtomStatus}
    commit=QualificationEvent(
        "commit-task",EventKind.ACTION,
        (make_transition("s::task-done",task),make_transition(ATOM,route)),
        "controlled",f"oacr-sqec-variant-{index}",
    )

    repair=dict(total)
    repair[AtomStatus.ACTION_OPEN]=AtomStatus.SATISFIED
    universal=QualificationEvent(
        "universal-remediation",EventKind.ACTION,
        (make_transition("s::universal-remediation",repair),),
        "controlled",f"oacr-sqec-variant-{index}",
    )

    pre=(make_precondition(ATOM,ALLOWED),)
    outs=[]
    for label,target in (
        ("qualified",AtomStatus.SATISFIED),
        ("unqualified",AtomStatus.CLOSED),
    ):
        mapping=dict(total)
        mapping[AtomStatus.UNKNOWN]=target
        outs.append(
            StochasticLegalityOutcome(
                label,Fraction(1,2),
                QualificationEvent(
                    f"observe-{label}",EventKind.OBSERVATION,
                    (make_transition("u::latent-semantics",mapping),),
                    "controlled",f"oacr-sqec-variant-{index}",pre,
                ),
            )
        )
    return StochasticLegalityProblem(
        model,
        (
            LegalEventOption("commit-task",commit,Fraction(0)),
            LegalEventOption("universal-remediation",universal,Fraction(3)),
        ),
        StochasticLegalityObservation("observe-semantics",Fraction(1,5),tuple(outs)),
        3,Fraction(10),
    )


def repair_projection(problem):
    projected=project_stochastic_legality(problem)
    pre=(make_precondition(ATOM,ALLOWED),)
    outs=tuple(
        replace(x,event=replace(x.event,preconditions=pre))
        for x in projected.observation.outcomes
    )
    return replace(
        projected,
        observation=replace(projected.observation,outcomes=outs),
    )


def catalog(problem):
    d={x.event.event_id:x.event for x in problem.actions}
    d.update({x.event.event_id:x.event for x in problem.observation.outcomes})
    return d


def sig(problem,seq):
    snap=initial_dynamic_snapshot(problem.model)
    cats=catalog(problem)
    payload=None
    for step,eid in enumerate(seq,1):
        try:
            snap=apply_qualification_event(problem.model,snap,cats[eid])
        except ValueError as exc:
            if "is illegal" not in str(exc):
                raise
            payload={
                "legal":False,
                "illegal_at":step,
                "illegal_event":eid,
                "prefix_atom_statuses":[[a,s.value] for a,s in snap.atom_statuses],
                "prefix_joint_state":snap.joint_state.value,
            }
            break
    if payload is None:
        payload={
            "legal":True,
            "final_atom_statuses":[[a,s.value] for a,s in snap.atom_statuses],
            "final_joint_state":snap.joint_state.value,
        }
    return hashlib.sha256(
        json.dumps(payload,sort_keys=True,separators=(",",":")).encode()
    ).hexdigest()


def sequences():
    return tuple(
        list(product(EVENTS,repeat=1))
        + list(product(EVENTS,repeat=2))
    )


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--artifact",required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()
    prod=json.loads(Path(a.artifact).read_text())

    if prod.get("protocol")!=PROTOCOL:
        raise RuntimeError("protocol mismatch")
    if prod.get("protocol_commit")!=PROTOCOL_COMMIT:
        raise RuntimeError("protocol commit mismatch")
    if prod.get("variant_targets")!=[x.value for x in TARGETS]:
        raise RuntimeError("variant manifest mismatch")
    if prod.get("event_order")!=list(EVENTS):
        raise RuntimeError("event manifest mismatch")

    mismatches=[]
    proj_h1=proj_h2=repair_mis=0
    by_variant={int(x["variant"]):x for x in prod["variants"]}

    for i in range(8):
        if i not in by_variant:
            mismatches.append(f"missing variant {i}")
            continue
        row=by_variant[i]
        full=build(i)
        projected=project_stochastic_legality(full)
        repaired=repair_projection(full)
        for seq in sequences():
            key=">".join(seq)
            sf=sig(full,seq)
            sp=sig(projected,seq)
            sr=sig(repaired,seq)
            pentry=row["full_matrix"].get(key)
            qentry=row["projected_matrix"].get(key)
            rentry=row["repaired_matrix"].get(key)
            if not pentry or pentry["signature"]!=sf:
                mismatches.append(f"full signature {i} {key}")
            if not qentry or qentry["signature"]!=sp:
                mismatches.append(f"projected signature {i} {key}")
            if not rentry or rentry["signature"]!=sr:
                mismatches.append(f"repaired signature {i} {key}")
            if sf!=sp:
                if len(seq)==1: proj_h1+=1
                else: proj_h2+=1
            if sf!=sr:
                repair_mis+=1

    summary={
        "verified":not mismatches,
        "variants":8,
        "projected_h1_mismatches":proj_h1,
        "projected_h2_mismatches":proj_h2,
        "repaired_depth_le_2_mismatches":repair_mis,
        "mismatch_count":len(mismatches),
        "mismatch_sample":mismatches[:20],
    }
    expected=prod["summary"]
    for k in (
        "projected_h1_mismatches",
        "projected_h2_mismatches",
        "repaired_depth_le_2_mismatches",
    ):
        if int(expected[k])!=int(summary[k]):
            summary["verified"]=False
            summary["mismatch_count"]+=1
            summary["mismatch_sample"].append(f"summary mismatch {k}")

    p=Path(a.out)
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(summary,indent=2))
    print(json.dumps(summary,indent=2))
    if not summary["verified"]:
        raise SystemExit(2)


if __name__=="__main__":
    main()
