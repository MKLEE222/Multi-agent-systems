"""Aggregate OACR-COMPOSE-L recovery-hysteresis fold artifacts."""
from __future__ import annotations
import argparse, json
from pathlib import Path

PROTOCOL="OACR_COMPOSE_L_RECOVERY_HYSTERESIS_V1"

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--inputs",nargs="+",required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()
    rows=[json.loads(Path(p).read_text()) for p in a.inputs]
    if len(rows)!=8:
        raise SystemExit(f"need exactly 8 folds, got {len(rows)}")
    if {int(x["fold"]) for x in rows}!=set(range(8)):
        raise SystemExit("fold set mismatch")
    if any(x.get("protocol")!=PROTOCOL for x in rows):
        raise SystemExit("protocol mismatch")

    rows=sorted(rows,key=lambda x:int(x["fold"]))
    complete=sum(int(x.get("status")=="COMPLETE") for x in rows)
    attempts=sum(int(x.get("summary",{}).get("anchor_candidates_attempted",0)) for x in rows)
    recovered=sum(int(x.get("summary",{}).get("accepted_recovered_states",0)) for x in rows)
    branches=sum(int(x.get("summary",{}).get("future_branches",0)) for x in rows)
    separations=sum(int(x.get("summary",{}).get("future_separations",0)) for x in rows)
    sep_pairs=sum(int(x.get("summary",{}).get("pairs_with_future_separation",0)) for x in rows)
    selective=sum(int(x.get("summary",{}).get("selective_pairs",0)) for x in rows)
    expected_branches=3*recovered
    branch_complete=branches==expected_branches

    if separations>0:
        disposition="RECOVERY_HYSTERESIS_POSITIVE_PENDING_TARGETED_REPLAY"
    elif complete>=4 and recovered>=20 and branch_complete:
        disposition="STRONG_RECOVERY_FUTURE_NEGATIVE"
    elif attempts>=1024 and recovered<8:
        disposition="RECOVERY_STATE_UNDERPOWERED"
    else:
        disposition="INSUFFICIENT_AGGREGATE_POWER"

    out={
      "protocol":"OACR_COMPOSE_L_RECOVERY_HYSTERESIS_AGGREGATE_V1",
      "source_protocol":PROTOCOL,
      "folds":8,
      "fold_statuses":[{"fold":int(x["fold"]),"status":x["status"],"summary":x.get("summary",{})} for x in rows],
      "summary":{
        "complete_folds":complete,
        "aggregate_anchor_attempts":attempts,
        "accepted_recovered_states":recovered,
        "future_branches":branches,
        "expected_future_branches":expected_branches,
        "all_registered_future_branches_complete":branch_complete,
        "future_separations":separations,
        "pairs_with_future_separation":sep_pairs,
        "selective_pairs":selective,
        "disposition":disposition,
      }
    }
    p=Path(a.out); p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(out,indent=2))
    print(json.dumps(out["summary"],indent=2))

if __name__=="__main__":
    main()
