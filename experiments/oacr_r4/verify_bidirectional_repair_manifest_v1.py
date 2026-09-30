"""Verify the accepted R4-building bidirectional repair manifest."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def sha256_obj(x) -> str:
    raw=(json.dumps(x,sort_keys=True,separators=(",",":"))+"\n").encode()
    return sha256_bytes(raw)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--result",required=True)
    ap.add_argument("--manifest",required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()

    result_path=Path(a.result)
    manifest_path=Path(a.manifest)
    raw=result_path.read_bytes()
    x=json.loads(raw)
    m=json.loads(manifest_path.read_text())

    errors=[]
    def req(cond,msg):
        if not cond: errors.append(msg)

    req(m.get("protocol")=="OACR_R4_BIDIRECTIONAL_REPAIR_MANIFEST_V1","protocol")
    req(m.get("source_result_sha256")==sha256_bytes(raw),"source_result_sha256")
    req(x.get("status")=="INCLUDED","source status")
    req(x.get("root")==m.get("root"),"root")
    req(x["manifest_hashes"]["state_manifest_sha256"]==m["state_manifest_sha256"],"state manifest")
    req(x["manifest_hashes"]["action_manifest_sha256"]==m["action_manifest_sha256"],"action manifest")

    active=x["active_state_ids"]
    inactive=x["inactive_state_ids"]
    req(active==m["active_state_ids"],"active ids exact")
    req(sha256_obj(active)==m["active_state_ids_sha256"],"active ids digest")
    req(len(inactive)==m["inactive_state_ids_count"],"inactive count")
    req(sha256_obj(inactive)==m["inactive_state_ids_sha256"],"inactive digest")
    req(len(active)==22,"active count 22")
    req(len(inactive)==249,"inactive count 249")
    req(len(active)+len(inactive)==271,"registered augmented deltas 271")
    req(set(active).isdisjoint(inactive),"active/inactive disjoint")

    add=m["additive_repair"]
    sub=m["subtractive_repair"]
    req(add["source_delta_records"]==0 and add["delta_edits"]==22,"additive accounting")
    req(sub["source_delta_records"]==271 and sub["delta_edits"]==249,"subtractive accounting")
    req(add["target"]==sub["target"]=="Rgate_contract_gated_delta","common target")

    gate=x["diagnostics"]["Rgate_contract_gated_delta"]
    tgt=m["target"]
    req(gate["representation_blocks"]==23==tgt["representation_blocks"],"target blocks")
    req(float(gate["omission_U_bits"])==0.0==float(tgt["U_bits"]),"target U")
    req(float(gate["excess_E_bits"])==0.0==float(tgt["E_bits"]),"target E")
    req(bool(gate["partition_match_almost_surely"]),"partition exact")
    req(x["summary"]["native_replay_mismatches"]==0==tgt["native_replay_mismatches"],"native replay mismatches")
    cells=x["summary"]["states"]*x["summary"]["registered_actions"]
    req(cells==17408==tgt["native_replay_cells"],"native replay cells")
    req(x["manifest_hashes"]["original_outcome_matrix_sha256"]==tgt["original_outcome_matrix_sha256"],"original matrix digest")
    req(x["manifest_hashes"]["compressed_outcome_matrix_sha256"]==tgt["compressed_outcome_matrix_sha256"],"compressed matrix digest")
    req(tgt["original_outcome_matrix_sha256"]==tgt["compressed_outcome_matrix_sha256"],"outcome matrices identical")

    report={
        "protocol":"OACR_R4_BIDIRECTIONAL_REPAIR_VERIFY_V1",
        "verified":not errors,
        "errors":errors,
        "source_result_sha256":sha256_bytes(raw),
        "active_deltas":len(active),
        "inactive_deltas":len(inactive),
        "additive_edits":add["delta_edits"],
        "subtractive_edits":sub["delta_edits"],
        "target_blocks":gate["representation_blocks"],
        "target_U_bits":gate["omission_U_bits"],
        "target_E_bits":gate["excess_E_bits"],
        "native_replay_cells":cells,
        "native_replay_mismatches":x["summary"]["native_replay_mismatches"],
    }
    Path(a.out).parent.mkdir(parents=True,exist_ok=True)
    Path(a.out).write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))
    if errors:
        raise SystemExit(2)

if __name__=="__main__":
    main()
