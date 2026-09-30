"""Independent verifier for OACR-SQEC v2 fixed-interpreter repairs."""

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

ROUTE = "s::observation-route"
TASK = "s::task-done"
LATENT = "u::latent-semantics"
EVENTS = (
    "commit-task",
    "universal-remediation",
    "observe-qualified",
    "observe-unqualified",
)
OBS = ("observe-qualified", "observe-unqualified")
ALLOWED = (AtomStatus.ACTION_OPEN, AtomStatus.SATISFIED)
ALL = tuple(sorted(tuple(AtomStatus), key=lambda x: x.value))
TARGETS = (
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
POS = (0, 2, 4, 6, 8, 10)
NEG = (1, 3, 5, 7, 9, 11)


@dataclass(frozen=True)
class Rule:
    rid: str
    atom: str
    allowed: tuple[AtomStatus, ...]
    events: tuple[str, ...]


@dataclass(frozen=True)
class Rep:
    rid: str
    rules: tuple[Rule, ...]


@dataclass(frozen=True)
class Skeleton:
    variant: int
    model: object
    events: tuple[QualificationEvent, ...]


def jhash(x):
    return hashlib.sha256(
        json.dumps(x, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def trans_rows(event):
    return [
        {
            "atom": t.atom,
            "cases": [[a.value, b.value] for a, b in t.cases],
        }
        for t in event.transitions
    ]


def skel_payload(s):
    return {
        "variant": s.variant,
        "initial_statuses": [[a, st.value] for a, st in s.model.initial_statuses],
        "events": [
            {
                "event_id": e.event_id,
                "kind": e.kind.value,
                "transitions": trans_rows(e),
                "evidence_basis": e.evidence_basis,
                "source": e.source,
                "preconditions": [],
            }
            for e in s.events
        ],
    }


def rep_payload(r):
    return {
        "representation_id": r.rid,
        "guard_rules": [
            {
                "rule_id": z.rid,
                "atom": z.atom,
                "allowed": [x.value for x in z.allowed],
                "applies_to": list(z.events),
            }
            for z in r.rules
        ],
    }


def make_skeleton(i):
    cert=EventWindowOpportunityCertificate(
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
    model=compile_dynamic_qualification_model(
        cert,{ROUTE:AtomStatus.ACTION_OPEN}
    )
    total={s:s for s in AtomStatus}

    tmap=dict(total)
    tmap[AtomStatus.ACTION_OPEN]=AtomStatus.SATISFIED
    tmap[AtomStatus.SATISFIED]=AtomStatus.SATISFIED
    rmap={s:TARGETS[i] for s in AtomStatus}
    commit=QualificationEvent(
        "commit-task",EventKind.ACTION,
        (make_transition(TASK,tmap),make_transition(ROUTE,rmap)),
        "controlled",f"oacr-sqec-v2-variant-{i}",(),
    )

    umap=dict(total)
    umap[AtomStatus.ACTION_OPEN]=AtomStatus.SATISFIED
    universal=QualificationEvent(
        "universal-remediation",EventKind.ACTION,
        (make_transition("s::universal-remediation",umap),),
        "controlled",f"oacr-sqec-v2-variant-{i}",(),
    )

    obs=[]
    for label,target in (
        ("qualified",AtomStatus.SATISFIED),
        ("unqualified",AtomStatus.CLOSED),
    ):
        m=dict(total)
        m[AtomStatus.UNKNOWN]=target
        obs.append(QualificationEvent(
            f"observe-{label}",EventKind.OBSERVATION,
            (make_transition(LATENT,m),),
            "controlled",f"oacr-sqec-v2-variant-{i}",(),
        ))

    events=(commit,universal,*obs)
    assert tuple(e.event_id for e in events)==EVENTS
    assert not any(e.preconditions for e in events)
    return Skeleton(i,model,events)


def full_rep(rid):
    return Rep(rid,(
        Rule("route-qualified",ROUTE,ALLOWED,("observe-qualified",)),
        Rule("route-unqualified",ROUTE,ALLOWED,("observe-unqualified",)),
    ))


def reps():
    return {
        "FULL":full_rep("FULL"),
        "B0":Rep("B0",()),
        "B1":full_rep("B1"),
        "B2":Rep("B2",(Rule("shared-route-guard",ROUTE,ALLOWED,OBS),)),
        "B3":Rep("B3",(Rule("shared-sham-task-guard",TASK,ALL,OBS),)),
    }


def compile_rep(s,r):
    pre={eid:[] for eid in EVENTS}
    for rule in r.rules:
        p=make_precondition(rule.atom,rule.allowed)
        for eid in rule.events:
            if eid not in pre:
                raise RuntimeError(f"unknown event {eid}")
            pre[eid].append(p)
    out=[]
    for e in s.events:
        pp=tuple(sorted(
            pre[e.event_id],
            key=lambda x:(x.atom,tuple(st.value for st in x.allowed))
        ))
        out.append(replace(e,preconditions=pp))
    return tuple(out)


def rows(snapshot):
    return [[a,s.value] for a,s in snapshot.atom_statuses]


def execute(s,compiled,seq):
    cat={e.event_id:e for e in compiled}
    snap=initial_dynamic_snapshot(s.model)
    for step,eid in enumerate(seq,1):
        try:
            snap=apply_qualification_event(s.model,snap,cat[eid])
        except ValueError as exc:
            if "is illegal" not in str(exc):
                raise
            return {
                "legal":False,
                "illegal_at":step,
                "illegal_event":eid,
                "prefix_atom_statuses":rows(snap),
                "prefix_joint_state":snap.joint_state.value,
            }
    return {
        "legal":True,
        "final_atom_statuses":rows(snap),
        "final_joint_state":snap.joint_state.value,
    }


def seqs():
    z=[]
    for n in (1,2):
        z.extend(product(EVENTS,repeat=n))
    return tuple(z)


def build_matrix(s,r):
    compiled=compile_rep(s,r)
    out={}
    for seq in seqs():
        p=execute(s,compiled,seq)
        out[">".join(seq)]={"signature":jhash(p),"payload":p}
    return out


def mm(a,b,n):
    out=[]
    for k in a:
        is2=">" in k
        if (n==2)!=is2:
            continue
        if a[k]["signature"]!=b[k]["signature"]:
            out.append(k)
    return out


def expected(i):
    if i not in POS:
        return []
    return [
        "commit-task>observe-qualified",
        "commit-task>observe-unqualified",
    ]


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--artifact",required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()

    prod=json.loads(Path(a.artifact).read_text())
    errors=[]
    def check(ok,msg):
        if not ok: errors.append(msg)

    check(prod.get("protocol")==PROTOCOL,"protocol")
    check(prod.get("protocol_commit")==PROTOCOL_COMMIT,"protocol commit")
    check(prod.get("executor",{}).get("id")==EXECUTOR_ID,"executor id")
    check(prod.get("executor",{}).get("source_blob_sha")==EXECUTOR_SOURCE_BLOB_SHA,"executor source")
    check(prod.get("variant_targets")==[x.value for x in TARGETS],"variant targets")
    check(prod.get("positive_variants")==list(POS),"positive variants")
    check(prod.get("negative_variants")==list(NEG),"negative variants")
    check(prod.get("event_order")==list(EVENTS),"event order")

    rr=reps()
    expected_manifest={k:rep_payload(v) for k,v in rr.items()}
    check(prod.get("representation_manifest")==expected_manifest,"representation manifest")
    expected_costs={k:len(v.rules) for k,v in rr.items()}
    check(prod.get("representation_cost_rules")==expected_costs,"representation costs")

    byv={int(x["variant"]):x for x in prod.get("variants",[])}
    agg={k:{"h1":0,"h2":0} for k in ("B0","B1","B2","B3")}
    matrix_mismatch=0

    for i in range(12):
        if i not in byv:
            errors.append(f"missing variant {i}")
            continue
        s=make_skeleton(i)
        ssha=jhash(skel_payload(s))
        check(prod["skeleton_digests"].get(str(i))==ssha,f"skeleton digest {i}")

        mats={name:build_matrix(s,r) for name,r in rr.items()}
        row=byv[i]
        for name in rr:
            stored=row["matrices"].get(name)
            if stored!=mats[name]:
                matrix_mismatch+=1
                errors.append(f"matrix {i} {name}")

        full=mats["FULL"]
        exp=expected(i)
        for name in ("B0","B1","B2","B3"):
            h1=mm(full,mats[name],1)
            h2=mm(full,mats[name],2)
            agg[name]["h1"]+=len(h1)
            agg[name]["h2"]+=len(h2)
            stored=row["mismatches"].get(name)
            check(stored=={"h1":h1,"h2":h2},f"mismatch list {i} {name}")
            check(h1==[],f"H1 invariance {i} {name}")
            if name in ("B0","B3"):
                check(h2==exp,f"frozen delayed mismatch {i} {name}")
            else:
                check(h2==[],f"exact repair {i} {name}")

    required={
        "B0":{"h1":0,"h2":12},
        "B1":{"h1":0,"h2":0},
        "B2":{"h1":0,"h2":0},
        "B3":{"h1":0,"h2":12},
    }
    check(agg==required,"aggregate disposition")
    check(prod.get("summary",{}).get("aggregate_mismatches")==required,"producer aggregate")
    check(prod.get("summary",{}).get("required_aggregate_mismatches")==required,"required aggregate manifest")
    check(prod.get("summary",{}).get("same_size_B2_B3") is True,"same-size sham gate")

    report={
        "protocol":"OACR_SQEC_FIXED_INTERPRETER_REPAIR_VERIFY_V2",
        "verified":not errors,
        "verifier_mismatch_count":len(errors),
        "matrix_mismatch_count":matrix_mismatch,
        "aggregate_mismatches":agg,
        "required":required,
        "variants_verified":12,
        "sequence_count":len(seqs()),
        "representation_cost_rules":expected_costs,
        "executor_id":EXECUTOR_ID,
        "error_sample":errors[:40],
    }
    Path(a.out).parent.mkdir(parents=True,exist_ok=True)
    Path(a.out).write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))
    if errors:
        raise SystemExit(2)


if __name__=="__main__":
    main()
