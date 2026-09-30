"""Structural verifier for OACR-COMPOSE-L recovery-hysteresis artifacts."""
from __future__ import annotations
import argparse, json
from pathlib import Path

PROTOCOL="OACR_COMPOSE_L_RECOVERY_HYSTERESIS_V1"
PROTOCOL_COMMIT="e1d00a7bb57d30ef2d49eb667dbcd6fd7f0d1e8f"
GRACE_COMMIT="f674183f17a995d109e10ee6140d4c3e6d016115"

def fail(msg):
    raise SystemExit(msg)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--artifact",required=True)
    a=ap.parse_args()
    d=json.loads(Path(a.artifact).read_text())

    if d.get("protocol")!=PROTOCOL: fail("protocol mismatch")
    if d.get("protocol_commit")!=PROTOCOL_COMMIT: fail("protocol commit mismatch")
    if d.get("official_grace_commit")!=GRACE_COMMIT: fail("GRACE commit mismatch")
    if d.get("fold") not in range(8): fail("fold mismatch")
    if d.get("status") not in {"COMPLETE","RECOVERY_STATE_UNDERPOWERED","UNDERPOWERED_FUTURE_BANK","UNDERPOWERED_ANCHOR_BANK"}:
        fail("unknown status")

    status=d["status"]
    if status.startswith("UNDERPOWERED_"):
        if d.get("future_outcomes_executed") is not False:
            fail("underpowered artifact executed future outcomes")
        print(json.dumps({"verified":True,"status":status,"fold":d["fold"]},indent=2))
        return

    if len(d.get("future_ids",[]))!=3: fail("future action count mismatch")
    if len(set(d["future_ids"]))!=3: fail("duplicate future IDs")
    if len(d.get("anchor_bank_ids",[]))!=256: fail("anchor bank size mismatch")
    if len(set(d["anchor_bank_ids"]))!=256: fail("duplicate anchor IDs")
    if set(d["future_ids"]).intersection(d["anchor_bank_ids"]): fail("future/anchor overlap")
    if len(d.get("sentinel_ids",[]))!=32: fail("sentinel count mismatch")
    if set(d["sentinel_ids"]).intersection(d["future_ids"]): fail("sentinel/future overlap")
    if set(d["sentinel_ids"]).intersection(d["anchor_bank_ids"]): fail("sentinel/anchor overlap")
    if d.get("non_target_unchanged") is not True: fail("non-target parameters changed")

    attempts=d.get("attempts",[])
    recovered=d.get("recovered_states",[])
    future=d.get("future_results",[])
    if len(attempts)>256: fail("too many attempts")
    if len(recovered)>4: fail("too many recovered states")
    if status=="RECOVERY_STATE_UNDERPOWERED":
        if recovered: fail("underpowered recovery artifact has recovered states")
        if d.get("future_outcomes_executed") is not False: fail("recovery-underpowered executed future")
    if status=="COMPLETE":
        if not recovered: fail("complete artifact lacks recovered state")
        if d.get("future_outcomes_executed") is not True: fail("complete artifact lacks future outcomes")
        if len(future)!=len(recovered): fail("future result count mismatch")

    accepted_attempts={int(x["anchor_id"]):x for x in attempts if x.get("accepted")}
    rec_ids=[int(x["anchor_id"]) for x in recovered]
    if set(rec_ids)!=set(accepted_attempts): fail("accepted attempts != recovered states")
    if len(rec_ids)!=len(set(rec_ids)): fail("duplicate recovered anchor")
    for x in recovered:
        if x.get("root_task_equal") is not True: fail("accepted recovered state not root-task equal")
        if x.get("parameter_hash")==d.get("base_parameter_hash"): fail("accepted recovered hash equals base")
        if len(x.get("panel_manifest",[]))!=36: fail("unexpected pair panel size")

    sep=0
    sep_pairs=0
    selective=0
    for row in future:
        if int(row["anchor_id"]) not in set(rec_ids): fail("future row unknown anchor")
        if row.get("root_task_equal") is not True: fail("future row root mismatch")
        actions=row.get("actions",[])
        if len(actions)!=3: fail("future action count mismatch")
        if {int(x["action_id"]) for x in actions}!=set(d["future_ids"]): fail("future action IDs mismatch")
        row_sep=sum(int(bool(x.get("separates"))) for x in actions)
        if row_sep!=int(row.get("future_separations",0)): fail("pair separation count mismatch")
        calc_selective=(0<row_sep<3)
        if bool(row.get("selective_future_response"))!=calc_selective: fail("selectivity mismatch")
        sep += row_sep
        sep_pairs += int(row_sep>0)
        selective += int(calc_selective)

    s=d.get("summary",{})
    if int(s.get("anchor_candidates_attempted",-1))!=len(attempts): fail("attempt summary mismatch")
    if int(s.get("accepted_recovered_states",-1))!=len(recovered): fail("recovered summary mismatch")
    if int(s.get("future_branches",-1))!=len(recovered)*3: fail("future branch summary mismatch")
    if int(s.get("future_separations",-1))!=sep: fail("future separation summary mismatch")
    if int(s.get("pairs_with_future_separation",-1))!=sep_pairs: fail("separating pair summary mismatch")
    if int(s.get("selective_pairs",-1))!=selective: fail("selective pair summary mismatch")

    print(json.dumps({
        "verified":True,
        "status":status,
        "fold":d["fold"],
        "accepted_recovered_states":len(recovered),
        "future_separations":sep,
        "pairs_with_future_separation":sep_pairs,
    },indent=2))

if __name__=="__main__":
    main()
