"""Aggregate outcome classifier for OACR-L2b fold-diverse parameter-state H2."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

PROTOCOL="OACR_L2B_FOLD_DIVERSE_FT_H2_V1"


def load(path):
    x=json.loads(Path(path).read_text())
    if x.get("protocol") != PROTOCOL:
        raise RuntimeError(f"{path}: unexpected protocol {x.get('protocol')}")
    return x


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--artifact", action="append", required=True)
    ap.add_argument("--out", required=True)
    args=ap.parse_args()

    xs=[load(p) for p in args.artifact]
    folds=[int(x["fold"]) for x in xs]
    if len(set(folds)) != len(folds):
        raise RuntimeError("duplicate fold artifacts")

    rows=[]
    total_pairs=0
    total_h1=0
    total_h2=0
    total_attempts=0
    total_retained_nonbase=0
    complete=0

    for x in sorted(xs,key=lambda z:int(z["fold"])):
        status=x["status"]
        row={"fold":int(x["fold"]),"status":status}
        if status=="COMPLETE":
            complete+=1
            s=x["summary"]
            row.update({
                "states":s["states"],
                "anchor_attempts":s["anchor_attempts_executed"],
                "retained_nonbase_states":s["retained_nonbase_states"],
                "h0_pairs":s["h0_task_collision_pairs"],
                "h1_separations":s["h1_task_separations_from_h0"],
                "h2_separations":s["h2_task_separations_from_h1"],
                "h2_operational_classes":s["h2_task_operational_classes"],
                "parameter_identity_over_refinement_pairs":
                    s["parameter_identity_over_refinement_pairs"],
            })
            total_pairs += int(s["h0_task_collision_pairs"])
            total_h1 += int(s["h1_task_separations_from_h0"])
            total_h2 += int(s["h2_task_separations_from_h1"])
            total_attempts += int(s["anchor_attempts_executed"])
            total_retained_nonbase += int(s["retained_nonbase_states"])
        elif status=="UNDERPOWERED_STATE_CONSTRUCTION":
            n=int(x.get("anchor_attempts_executed",len(x.get("anchor_attempts",[]))))
            total_attempts+=n
            total_retained_nonbase += max(0,int(x.get("states",1))-1)
            row.update({
                "states":int(x.get("states",1)),
                "anchor_attempts":n,
                "retained_nonbase_states":max(0,int(x.get("states",1))-1),
            })
        elif status in {"SEED_CONSTRUCTION_FAILURE","UNDERPOWERED_CANDIDATE_BANK"}:
            row["anchor_attempts"]=0
        else:
            raise RuntimeError(f"unrecognized status {status}")
        rows.append(row)

    positive=(total_h1+total_h2)>0
    strong_negative=(
        not positive
        and complete>=4
        and total_pairs>=30
    )
    h0_visibility=(
        not positive
        and complete<4
        and total_attempts>=1000
        and total_retained_nonbase==0
    )

    if positive:
        classification="POSITIVE_REQUIRES_NATIVE_REPLAY"
    elif strong_negative:
        classification="STRONG_FUTURE_NEGATIVE"
    elif h0_visibility:
        classification="PARAMETER_STATE_H0_VISIBILITY_BOUNDARY"
    else:
        classification="UNDERPOWERED"

    out={
        "protocol":PROTOCOL,
        "fold_artifacts":len(xs),
        "complete_folds":complete,
        "aggregate_h0_pairs":total_pairs,
        "aggregate_h1_separations":total_h1,
        "aggregate_h2_separations":total_h2,
        "aggregate_anchor_attempts":total_attempts,
        "aggregate_retained_nonbase_states":total_retained_nonbase,
        "classification":classification,
        "thresholds":{
            "strong_negative_min_complete_folds":4,
            "strong_negative_min_h0_pairs":30,
            "h0_visibility_max_complete_folds":3,
            "h0_visibility_min_anchor_attempts":1000,
            "h0_visibility_required_retained_nonbase_states":0,
        },
        "folds":rows,
    }

    p=Path(args.out)
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(out,indent=2))
    print(json.dumps(out,indent=2))


if __name__=="__main__":
    main()
