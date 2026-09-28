"""OACR-G4 v1: natural same-tree Git control pairs under a frozen merge alphabet."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple


def run(cwd:Path,*args:str,check:bool=True):
    p=subprocess.run(list(args),cwd=cwd,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
                     env={**os.environ,"GIT_CONFIG_NOSYSTEM":"1"})
    if check and p.returncode!=0:
        raise RuntimeError(f"command failed ({p.returncode}): {' '.join(args)}\n{p.stdout}")
    return p


def git(cwd:Path,*args:str,check:bool=True):
    return run(cwd,"git",*args,check=check)


def chunks(xs,n):
    for i in range(0,len(xs),n):
        yield xs[i:i+n]


def tree_map(repo,commits):
    out={}
    for ch in chunks(sorted(set(commits)),250):
        p=git(repo,"show","-s","--format=%H %T",*ch)
        for line in p.stdout.splitlines():
            a=line.split()
            if len(a)==2: out[a[0]]=a[1]
    return out


def is_ancestor(repo,anc,desc):
    p=git(repo,"merge-base","--is-ancestor",anc,desc,check=False)
    if p.returncode not in (0,1): raise RuntimeError(p.stdout)
    return p.returncode==0


def merge_base(repo,a,b):
    p=git(repo,"merge-base",a,b,check=False)
    return p.stdout.strip() if p.returncode==0 else ""


def fresh(repo,commit):
    git(repo,"merge","--abort",check=False)
    git(repo,"reset","--hard","-q",commit)
    git(repo,"clean","-fdq")
    git(repo,"checkout","-q","--detach",commit)
    if git(repo,"status","--porcelain").stdout.strip():
        raise RuntimeError("dirty checkout")


def execute(repo,head,target):
    fresh(repo,head)
    p=git(repo,"merge","--no-commit","--no-ff",target,check=False)
    output=p.stdout
    unmerged=sorted(x for x in git(repo,"diff","--name-only","--diff-filter=U",check=False).stdout.splitlines() if x)
    diff=git(repo,"diff","--binary","--no-ext-diff","HEAD",check=False).stdout
    wt=hashlib.sha256(diff.encode()).hexdigest()
    w=git(repo,"write-tree",check=False)
    idx=w.stdout.strip() if w.returncode==0 else None
    payload={
        "exit_code":p.returncode,
        "already_up_to_date":"Already up to date." in output,
        "merge_in_progress":(repo/".git"/"MERGE_HEAD").exists(),
        "unmerged_paths":unmerged,
        "index_tree":idx,
        "tracked_delta_sha256":wt,
    }
    sig=hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    git(repo,"merge","--abort",check=False)
    git(repo,"reset","--hard","-q",head)
    git(repo,"clean","-fdq")
    return {"signature":sig,"output":output,**payload}


def discover_action_targets(repo,max_merges=10000,n=4):
    lines=git(repo,"rev-list","--merges","--all",f"--max-count={max_merges}","--parents").stdout.splitlines()
    triples=[]
    commits=[]
    for line in lines:
        p=line.split()
        if len(p)==3:
            b,a,t=p
            triples.append((b,a,t))
            commits.extend([b,a])
    tm=tree_map(repo,commits)
    targets=[]
    triples_out=[]
    for b,a,t in triples:
        if tm.get(b)!=tm.get(a): continue
        if is_ancestor(repo,t,a): continue
        if not is_ancestor(repo,t,b): continue
        targets.append(t)
        triples_out.append((b,a,t))
        if len(targets)>=n: break
    if len(targets)<n:
        raise RuntimeError(f"only {len(targets)} structural action targets")
    return targets,triples_out


def confusion(rows,key):
    tp=fp=fn=tn=0
    for r in rows:
        pred=bool(r[key])
        actual=bool(r["required_separation"])
        if pred and actual: tp+=1
        elif pred and not actual: fp+=1
        elif not pred and actual: fn+=1
        else: tn+=1
    return {"TP":tp,"FP_over_refinement":fp,"FN_under_refinement":fn,"TN":tn}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--repo",required=True)
    ap.add_argument("--out",required=True)
    ap.add_argument("--max_commits",type=int,default=20000)
    ap.add_argument("--max_pairs",type=int,default=32)
    args=ap.parse_args()

    repo=Path(args.repo).resolve()
    git(repo,"config","--local","rerere.enabled","false")
    git(repo,"config","--local","merge.conflictStyle","merge")

    source_head=git(repo,"rev-parse","HEAD").stdout.strip()
    targets,target_sources=discover_action_targets(repo,10000,4)

    commits=[x for x in git(repo,"rev-list","--all",f"--max-count={args.max_commits}").stdout.splitlines() if x]
    tm=tree_map(repo,commits)
    groups=defaultdict(list)
    for c in commits:
        if c in tm: groups[tm[c]].append(c)

    pairs=[]
    for tree in sorted(groups):
        cs=sorted(set(groups[tree]))
        if len(cs)<2: continue
        for i in range(len(cs)-1):
            pairs.append((tree,cs[i],cs[i+1]))
    pairs=sorted(pairs,key=lambda x:(x[0],x[1],x[2]))[:args.max_pairs]
    if not pairs:
        raise RuntimeError("no natural same-tree pairs")

    rows=[]
    for tree,a,b in pairs:
        outcomes_a={}
        outcomes_b={}
        execution_error=None
        try:
            for t in targets:
                outcomes_a[t]=execute(repo,a,t)
                outcomes_b[t]=execute(repo,b,t)
        except Exception as exc:
            execution_error=f"{type(exc).__name__}: {exc}"

        if execution_error:
            rows.append({"tree":tree,"A":a,"B":b,"execution_error":execution_error})
            continue

        sig_a=[outcomes_a[t]["signature"] for t in targets]
        sig_b=[outcomes_b[t]["signature"] for t in targets]
        required=sig_a!=sig_b

        f1a=[is_ancestor(repo,t,a) for t in targets]
        f1b=[is_ancestor(repo,t,b) for t in targets]
        f2a=[merge_base(repo,a,t) for t in targets]
        f2b=[merge_base(repo,b,t) for t in targets]

        rows.append({
            "tree":tree,"A":a,"B":b,
            "execution_error":None,
            "required_separation":required,
            "Ffull_separates":a!=b,
            "F1_ancestry_vector_A":f1a,
            "F1_ancestry_vector_B":f1b,
            "F1_separates":f1a!=f1b,
            "F2_merge_base_vector_A":f2a,
            "F2_merge_base_vector_B":f2b,
            "F2_separates":f2a!=f2b,
            "outcomes_A":outcomes_a,
            "outcomes_B":outcomes_b,
        })

    valid=[r for r in rows if r["execution_error"] is None]
    summary={
        "source_head":source_head,
        "commits_enumerated":len(commits),
        "same_tree_groups":sum(int(len(set(v))>=2) for v in groups.values()),
        "candidate_pairs_available":sum(max(0,len(set(v))-1) for v in groups.values()),
        "pairs_registered":len(pairs),
        "pairs_executed":len(valid),
        "execution_errors":len(rows)-len(valid),
        "required_separations":sum(int(r["required_separation"]) for r in valid),
        "behaviorally_equivalent_controls":sum(int(not r["required_separation"]) for r in valid),
        "Ffull":confusion(valid,"Ffull_separates"),
        "F1":confusion(valid,"F1_separates"),
        "F2":confusion(valid,"F2_separates"),
    }
    out={
        "protocol":"OACR_G4_NATURAL_GIT_CONTROLS_V1",
        "source":{"remote":git(repo,"remote","get-url","origin").stdout.strip(),"source_head":source_head,
                  "git_version":git(repo,"--version").stdout.strip()},
        "action_targets":targets,
        "action_target_source_triples":[list(x) for x in target_sources],
        "summary":summary,
        "rows":rows,
    }
    p=Path(args.out)
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(out,indent=2))
    print(json.dumps(summary,indent=2))


if __name__=="__main__":
    main()
