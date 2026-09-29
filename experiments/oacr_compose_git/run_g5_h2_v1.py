from __future__ import annotations
import argparse, hashlib, json, os, subprocess
from pathlib import Path

FIXED_DATE="2000-01-01T00:00:00Z"
FIXED_NAME="OACR COMPOSE"
FIXED_EMAIL="oacr-compose@example.invalid"

def run(cwd,*args,check=True,env_extra=None):
    env={**os.environ,"GIT_CONFIG_NOSYSTEM":"1"}
    if env_extra: env.update(env_extra)
    p=subprocess.run(list(args),cwd=cwd,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,env=env)
    if check and p.returncode!=0:
        raise RuntimeError(f"command failed ({p.returncode}): {' '.join(args)}\n{p.stdout}")
    return p

def git(cwd,*args,check=True,env_extra=None):
    return run(cwd,"git",*args,check=check,env_extra=env_extra)

def fresh(repo,commit):
    git(repo,"merge","--abort",check=False)
    git(repo,"reset","--hard","-q",commit)
    git(repo,"clean","-fdq")
    git(repo,"checkout","-q","--detach",commit)
    if git(repo,"status","--porcelain").stdout.strip():
        raise RuntimeError(f"dirty checkout at {commit}")

def payload_signature(payload):
    core={k:payload[k] for k in ("exit_code","already_up_to_date","merge_in_progress","unmerged_paths","index_tree","tracked_delta_sha256")}
    return hashlib.sha256(json.dumps(core,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def merge_payload(repo,head,target,persist=False):
    fresh(repo,head)
    p=git(repo,"merge","--no-commit","--no-ff",target,check=False)
    output=p.stdout
    unmerged=sorted(x for x in git(repo,"diff","--name-only","--diff-filter=U",check=False).stdout.splitlines() if x)
    diff=git(repo,"diff","--binary","--no-ext-diff","HEAD",check=False).stdout
    wt=git(repo,"write-tree",check=False)
    index_tree=wt.stdout.strip() if wt.returncode==0 else None
    payload={"exit_code":p.returncode,"already_up_to_date":"Already up to date." in output,"merge_in_progress":(repo/".git"/"MERGE_HEAD").exists(),"unmerged_paths":unmerged,"index_tree":index_tree,"tracked_delta_sha256":hashlib.sha256(diff.encode()).hexdigest()}
    payload["signature"]=payload_signature(payload)
    successor=None
    successor_tree=None
    if persist and p.returncode==0 and not unmerged and index_tree:
        if payload["already_up_to_date"]:
            successor=head
            successor_tree=git(repo,"rev-parse",f"{head}^{{tree}}").stdout.strip()
        else:
            env={"GIT_AUTHOR_NAME":FIXED_NAME,"GIT_AUTHOR_EMAIL":FIXED_EMAIL,"GIT_COMMITTER_NAME":FIXED_NAME,"GIT_COMMITTER_EMAIL":FIXED_EMAIL,"GIT_AUTHOR_DATE":FIXED_DATE,"GIT_COMMITTER_DATE":FIXED_DATE}
            msg=f"OACR COMPOSE first merge {target}"
            successor=git(repo,"commit-tree",index_tree,"-p",head,"-p",target,env_extra=env).stdout.strip()
            successor_tree=index_tree
    git(repo,"merge","--abort",check=False)
    git(repo,"reset","--hard","-q",head)
    git(repo,"clean","-fdq")
    return payload,successor,successor_tree

def load_bank(path):
    d=json.loads(path.read_text())
    if d.get("protocol")!="OACR_G5_SAME_CONTRACT_GIT_V1" or d.get("split")!="validation":
        raise RuntimeError("wrong G5 validation artifact")
    targets=[x["target"] for x in d["action_selection"]["targets"]]
    rows=[r for r in d["pair_rows"] if not r["required_separation"]]
    if len(targets)!=12 or len(rows)!=46:
        raise RuntimeError(f"frozen bank mismatch targets={len(targets)} pairs={len(rows)}")
    return d,targets,rows

def evaluate(repo,bank_path):
    d,targets,rows=load_bank(bank_path)
    source_head=d["source"]["source_head"]
    if git(repo,"rev-parse","HEAD").stdout.strip()!=source_head:
        raise RuntimeError("source HEAD mismatch")
    pair_outputs=[]
    total_eligible=total_div=divergent_pairs=h1_repro_mismatch=0
    for pi,row in enumerate(rows):
        a,b=row["A"],row["B"]
        first={}
        for side,c,expected in (("A",a,row["outcome_signatures_A"]),("B",b,row["outcome_signatures_B"])):
            first[side]={}
            for ti,t1 in enumerate(targets):
                p,succ,tree=merge_payload(repo,c,t1,persist=True)
                if p["signature"]!=expected[ti]:
                    h1_repro_mismatch+=1
                first[side][t1]={"payload":p,"successor":succ,"tree":tree}
        seq_rows=[]
        pair_div=0
        for t1 in targets:
            fa,fb=first["A"][t1],first["B"][t1]
            gate=(fa["successor"] is not None and fb["successor"] is not None and fa["payload"]["signature"]==fb["payload"]["signature"] and fa["tree"]==fb["tree"])
            if not gate:
                continue
            for t2 in targets:
                if t2==t1:
                    continue
                total_eligible+=1
                pa,_,_=merge_payload(repo,fa["successor"],t2,persist=False)
                pb,_,_=merge_payload(repo,fb["successor"],t2,persist=False)
                div=pa["signature"]!=pb["signature"]
                total_div+=int(div)
                pair_div+=int(div)
                seq_rows.append({"t1":t1,"t2":t2,"h1_successor_tree":fa["tree"],"h2_signature_A":pa["signature"],"h2_signature_B":pb["signature"],"divergent":div,"h2_A":pa,"h2_B":pb})
        divergent_pairs+=int(pair_div>0)
        pair_outputs.append({"pair_index":pi,"tree":row["tree"],"A":a,"B":b,"eligible_sequences":len(seq_rows),"divergent_sequences":pair_div,"sequences":seq_rows})
    return {"protocol":"OACR_COMPOSE_G_G5_H2_V1","source_g5_artifact":str(bank_path),"source_head":source_head,"summary":{"source_pairs":46,"targets":12,"registered_ordered_sequences_per_pair":132,"eligible_sequences":total_eligible,"divergent_sequences":total_div,"pairs_with_divergence":divergent_pairs,"h1_reproduction_mismatches":h1_repro_mismatch},"pairs":pair_outputs}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--repo",required=True)
    ap.add_argument("--g5_validation_json",required=True)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    repo=Path(args.repo).resolve()
    git(repo,"config","--local","rerere.enabled","false")
    git(repo,"config","--local","merge.conflictStyle","merge")
    out=evaluate(repo,Path(args.g5_validation_json).resolve())
    p=Path(args.out)
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(out,indent=2))
    print(json.dumps(out["summary"],indent=2))

if __name__=="__main__":
    main()
