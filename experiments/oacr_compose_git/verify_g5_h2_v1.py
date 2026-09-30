from __future__ import annotations
import argparse, hashlib, json, os, subprocess
from pathlib import Path

FIXED_DATE="2000-01-01T00:00:00Z"
FIXED_NAME="OACR COMPOSE"
FIXED_EMAIL="oacr-compose@example.invalid"

def cmd(cwd,*xs,ok=(0,),env=None):
    e={**os.environ,"GIT_CONFIG_NOSYSTEM":"1"}
    e.update(env or {})
    p=subprocess.run(list(xs),cwd=cwd,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,env=e)
    if p.returncode not in ok:
        raise RuntimeError(f"failed {p.returncode}: {' '.join(xs)}\n{p.stdout}")
    return p

def g(cwd,*xs,ok=(0,),env=None):
    return cmd(cwd,"git",*xs,ok=ok,env=env)

def reset(repo,rev):
    g(repo,"merge","--abort",ok=(0,1,128))
    g(repo,"reset","--hard","-q",rev)
    g(repo,"clean","-fdq")
    g(repo,"checkout","-q","--detach",rev)

def observe(repo,head,target,make_successor):
    reset(repo,head)
    p=g(repo,"merge","--no-commit","--no-ff",target,ok=(0,1))
    conflicts=sorted(x for x in g(repo,"diff","--name-only","--diff-filter=U").stdout.splitlines() if x)
    diff=g(repo,"diff","--binary","--no-ext-diff","HEAD").stdout
    wt=g(repo,"write-tree",ok=(0,1,128))
    tree=wt.stdout.strip() if wt.returncode==0 else None
    core={"exit_code":p.returncode,"already_up_to_date":"Already up to date." in p.stdout,"merge_in_progress":(repo/".git"/"MERGE_HEAD").exists(),"unmerged_paths":conflicts,"index_tree":tree,"tracked_delta_sha256":hashlib.sha256(diff.encode()).hexdigest()}
    sig=hashlib.sha256(json.dumps(core,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    succ=None
    succ_tree=None
    if make_successor and p.returncode==0 and not conflicts and tree:
        if core["already_up_to_date"]:
            succ=head
            succ_tree=g(repo,"rev-parse",f"{head}^{{tree}}").stdout.strip()
        else:
            env={"GIT_AUTHOR_NAME":FIXED_NAME,"GIT_AUTHOR_EMAIL":FIXED_EMAIL,"GIT_COMMITTER_NAME":FIXED_NAME,"GIT_COMMITTER_EMAIL":FIXED_EMAIL,"GIT_AUTHOR_DATE":FIXED_DATE,"GIT_COMMITTER_DATE":FIXED_DATE}
            succ=g(repo,"commit-tree",tree,"-p",head,"-p",target,env=env).stdout.strip()
            succ_tree=tree
    g(repo,"merge","--abort",ok=(0,1,128))
    g(repo,"reset","--hard","-q",head)
    g(repo,"clean","-fdq")
    return sig,succ,succ_tree

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--repo",required=True)
    ap.add_argument("--g5_validation_json",required=True)
    ap.add_argument("--producer_json",required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()

    repo=Path(a.repo).resolve()
    bank=json.load(open(a.g5_validation_json))
    prod=json.load(open(a.producer_json))
    targets=[x["target"] for x in bank["action_selection"]["targets"]]
    rows=[r for r in bank["pair_rows"] if not r["required_separation"]]
    if len(rows)!=46 or len(targets)!=12:
        raise RuntimeError("bank mismatch")
    if prod["protocol"]!="OACR_COMPOSE_G_G5_H2_V1":
        raise RuntimeError("producer protocol mismatch")
    # Engineering normalization only: make native merge invocations independent
    # of runner-global Git identity.  These values are already frozen for the
    # deterministic persisted merge commits in the protocol.
    g(repo,"config","--local","user.name",FIXED_NAME)
    g(repo,"config","--local","user.email",FIXED_EMAIL)
    source_head=bank["source"]["source_head"]
    # Engineering normalization only: producer leaves the detached checkout at
    # the last replayed pair head.  The verifier must start from the frozen
    # source repository state, not require the caller's checkout position.
    reset(repo,source_head)
    if g(repo,"rev-parse","HEAD").stdout.strip()!=source_head:
        raise RuntimeError("failed to normalize verifier checkout to frozen source head")

    prod_by={(p["A"],p["B"]):p for p in prod["pairs"]}
    total=divs=divpairs=h1bad=0
    mismatches=[]
    for row in rows:
        A,B=row["A"],row["B"]
        pp=prod_by.get((A,B))
        if pp is None:
            mismatches.append(f"missing pair {A} {B}")
            continue
        first={}
        for side,c,expected in (("A",A,row["outcome_signatures_A"]),("B",B,row["outcome_signatures_B"])):
            first[side]={}
            for i,t in enumerate(targets):
                sig,succ,tree=observe(repo,c,t,True)
                h1bad+=int(sig!=expected[i])
                first[side][t]=(sig,succ,tree)

        expected_rows={(x["t1"],x["t2"]):x for x in pp["sequences"]}
        pairdiv=0
        seen=set()
        for t1 in targets:
            sa,ca,ta=first["A"][t1]
            sb,cb,tb=first["B"][t1]
            if not (ca and cb and sa==sb and ta==tb):
                continue
            for t2 in targets:
                if t2==t1:
                    continue
                total+=1
                xa,_,_=observe(repo,ca,t2,False)
                xb,_,_=observe(repo,cb,t2,False)
                dv=xa!=xb
                divs+=int(dv)
                pairdiv+=int(dv)
                seen.add((t1,t2))
                pr=expected_rows.get((t1,t2))
                if pr is None or pr["h2_signature_A"]!=xa or pr["h2_signature_B"]!=xb or bool(pr["divergent"])!=dv:
                    mismatches.append(f"sequence mismatch {A[:8]} {t1[:8]} {t2[:8]}")
        if seen!=set(expected_rows):
            mismatches.append(f"eligible sequence set mismatch {A[:8]}")
        if pairdiv!=pp["divergent_sequences"]:
            mismatches.append(f"pair count mismatch {A[:8]}")
        divpairs+=int(pairdiv>0)

    summary={"verified":not mismatches,"source_pairs":46,"eligible_sequences":total,"divergent_sequences":divs,"pairs_with_divergence":divpairs,"h1_reproduction_mismatches":h1bad,"mismatch_count":len(mismatches),"mismatch_sample":mismatches[:20]}
    ps=prod["summary"]
    if ps["eligible_sequences"]!=total or ps["divergent_sequences"]!=divs or ps["pairs_with_divergence"]!=divpairs or ps["h1_reproduction_mismatches"]!=h1bad:
        summary["verified"]=False
        summary["mismatch_count"]+=1
        summary["mismatch_sample"].append("summary mismatch")
    Path(a.out).parent.mkdir(parents=True,exist_ok=True)
    Path(a.out).write_text(json.dumps(summary,indent=2))
    print(json.dumps(summary,indent=2))
    if not summary["verified"]:
        raise SystemExit(2)

if __name__=="__main__":
    main()
