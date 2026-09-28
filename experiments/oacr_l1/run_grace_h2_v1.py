"""OACR-L1 v1: H=0/1/2 behavioral refinement on official GRACE + SCOTUS."""
from __future__ import annotations

import argparse
import itertools
import json
import os
import random
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import torch

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
sys.path.insert(0,str(ROOT/"oacr_w1"))
sys.path.insert(0,str(ROOT.parent/"r1_grace_scotus"))

import run_operational_congruence_v1 as W  # noqa: E402
import run_scotus_paired_closure as R  # noqa: E402
from grace_write_probe import (  # noqa: E402
    commit_anchor_write,
    get_adapter,
    isolated_rng,
    restore_adapter,
    snapshot_adapter,
)


def args():
    p=argparse.ArgumentParser()
    p.add_argument("--repo",required=True)
    p.add_argument("--out",required=True)
    p.add_argument("--seed",type=int,required=True)
    p.add_argument("--seed_edits",type=int,default=4)
    p.add_argument("--seed_scan_limit",type=int,default=512)
    p.add_argument("--candidate_bank",type=int,default=64)
    p.add_argument("--future_actions",type=int,default=3)
    p.add_argument("--sentinel_reads",type=int,default=16)
    p.add_argument("--max_states",type=int,default=4)
    p.add_argument("--read_atol",type=float,default=1e-6)
    p.add_argument("--read_rtol",type=float,default=1e-5)
    p.add_argument("--device",default="cpu")
    return p.parse_args()


def meta_signature(x: Dict[str,Any]) -> Tuple[Any,...]:
    return (
        x["status"],
        bool(x["target_realized"]),
        bool(x["fixed_all_satisfied"]),
    )


def apply_action(editor,cfg,start_snap,action,protected_tokens,read_panel_tokens,branch_seed):
    adapter=get_adapter(editor)
    restore_adapter(adapter,start_snap)
    expected=W.snapshot_hash(start_snap)
    if W.snapshot_hash(snapshot_adapter(adapter)) != expected:
        raise RuntimeError("restore mismatch before branch")

    pre_target=R.acc(editor,action["tokens"])
    if pre_target >= 1.0:
        status="ALREADY_SATISFIED_ZERO_WRITE"
    else:
        status="EDIT_EXECUTED"
        with isolated_rng(int(branch_seed)):
            editor.edit(cfg,action["tokens"],batch_history=[])

    post_target=R.acc(editor,action["tokens"])
    fixed=R.obligation_status(editor,protected_tokens)
    reads=R.read_family_signatures(editor,read_panel_tokens)
    post_snap=snapshot_adapter(adapter)
    post_hash=W.snapshot_hash(post_snap)

    restore_adapter(adapter,start_snap)
    if W.snapshot_hash(snapshot_adapter(adapter)) != expected:
        raise RuntimeError("restore mismatch after branch")

    serial={
        "status":status,
        "branch_seed":int(branch_seed),
        "target_realized":bool(post_target>=1.0),
        "fixed_all_satisfied":bool(fixed["all_satisfied"]),
        "post_reads":reads,
        "post_state_hash":post_hash,
    }
    return serial,post_snap


def reads_equal(a,b,atol,rtol):
    return bool(R.compare_read_family(a,b,atol,rtol)["strict_logits_matched"])


def transitivity_audit(state_ids,eq):
    violations=[]
    for a in state_ids:
        for b in state_ids:
            for c in state_ids:
                if eq[(a,b)] and eq[(b,c)] and not eq[(a,c)]:
                    violations.append([a,b,c])
                    if len(violations)>=20:
                        return {"transitive":False,"violations_sample":violations}
    return {"transitive":not violations,"violations_sample":violations}


def count_blocks_if_equivalence(state_ids,eq):
    audit=transitivity_audit(state_ids,eq)
    if not audit["transitive"]:
        return None,audit
    seen=set()
    blocks=[]
    for a in state_ids:
        if a in seen:
            continue
        block=[b for b in state_ids if eq[(a,b)]]
        for b in block:
            seen.add(b)
        blocks.append(sorted(block))
    return len(blocks),audit


def main():
    a=args()
    repo=Path(a.repo).resolve()
    sys.path.insert(0,str(repo))
    os.chdir(repo)

    random.seed(a.seed)
    np.random.seed(a.seed)
    torch.manual_seed(a.seed)

    from grace.editors import GRACE
    from grace.models import Classifier

    cfg=R.load_config(repo,a.device)
    model=Classifier(cfg).to(a.device)
    editor=GRACE(cfg,model)
    dataset=R.load_scotus_edit_dataset()

    seed_rows,protected_tokens,max_idx,seed_contract=R.build_contract_preserving_seed_state(
        editor,cfg,dataset,editor.tokenizer,a.device,
        a.seed_edits,a.seed_scan_limit,a.seed
    )
    seed_ids=[int(x["idx"]) for x in seed_rows]
    base=snapshot_adapter(get_adapter(editor))

    bank=R.collect_errors(
        editor,dataset,editor.tokenizer,a.device,max_idx+1,a.candidate_bank
    )
    enriched=R.enrich_routes(editor,bank)
    anchors=R.choose_anchors_by_native_mode(enriched,1)
    anchor_ids={int(x["idx"]) for x in anchors}
    future=W.choose_future_actions(enriched,anchor_ids,a.future_actions)
    if len(future)!=a.future_actions:
        raise RuntimeError(f"expected {a.future_actions} future actions, got {len(future)}")
    future_ids={int(x["idx"]) for x in future}

    sent=W.collect_sentinels(
        dataset,editor.tokenizer,a.device,
        set(seed_ids)|anchor_ids|future_ids,a.sentinel_reads
    )
    panel_tokens=list(protected_tokens)+[x["tokens"] for x in future]+[x["tokens"] for x in sent]
    panel_manifest=(
        [{"kind":"seed","dataset_index":int(x["idx"])} for x in seed_rows]
        +[{"kind":"future","dataset_index":int(x["idx"])} for x in future]
        +[{"kind":"sentinel","dataset_index":int(x["idx"])} for x in sent]
    )

    states=[{
        "state_id":"base","snapshot":base,"kind":"base",
        "anchor_id":None,"anchor_mode":None
    }]
    attempts=[]
    for anchor in anchors:
        restore_adapter(get_adapter(editor),base)
        sd=R.derive_seed(a.seed,"oacr_l1_anchor",anchor["idx"])
        post=commit_anchor_write(editor,cfg,anchor["tokens"],seed=sd)
        target=R.acc(editor,anchor["tokens"])
        fixed=R.obligation_status(editor,protected_tokens)
        ok=bool(target>=1.0 and fixed["all_satisfied"])
        attempts.append({
            "anchor_id":int(anchor["idx"]),
            "mode":anchor["route"]["update_mode"],
            "seed":int(sd),
            "target_realized":bool(target>=1.0),
            "fixed_preserved":bool(fixed["all_satisfied"]),
            "committed":ok,
        })
        if ok and len(states)<a.max_states:
            states.append({
                "state_id":f"anchor:{anchor['idx']}",
                "snapshot":post,
                "kind":"anchor",
                "anchor_id":int(anchor["idx"]),
                "anchor_mode":anchor["route"]["update_mode"],
            })
    if len(states)<2:
        raise RuntimeError("fewer than two contract-valid states")

    runtime={}
    serial_states=[]
    for st in states:
        restore_adapter(get_adapter(editor),st["snapshot"])
        h0=W.snapshot_hash(snapshot_adapter(get_adapter(editor)))
        reads=R.read_family_signatures(editor,panel_tokens)
        h1=W.snapshot_hash(snapshot_adapter(get_adapter(editor)))
        if h0!=h1:
            raise RuntimeError("root READ mutated state")
        feats={}
        for act in future:
            feats[str(int(act["idx"]))]=W.measure_state_action(
                editor,st["snapshot"],act,protected_tokens
            )
        runtime[st["state_id"]]={**st,"root_reads":reads,"features":feats}
        serial_states.append({
            "state_id":st["state_id"],"kind":st["kind"],
            "anchor_id":st["anchor_id"],"anchor_mode":st["anchor_mode"],
            "state_hash":h0,
        })

    action_map={str(int(x["idx"])):x for x in future}
    action_ids=list(action_map)
    tree={}

    for sid,st in runtime.items():
        one={}
        one_snaps={}
        for aid in action_ids:
            seed1=R.derive_seed(a.seed,"oacr_l1_h1",aid)
            meta,snap=apply_action(
                editor,cfg,st["snapshot"],action_map[aid],
                protected_tokens,panel_tokens,seed1
            )
            one[aid]=meta
            one_snaps[aid]=snap

        two={}
        for aid in action_ids:
            for bid in action_ids:
                seed2=R.derive_seed(a.seed,"oacr_l1_h2",aid,bid)
                meta,_=apply_action(
                    editor,cfg,one_snaps[aid],action_map[bid],
                    protected_tokens,panel_tokens,seed2
                )
                two[f"{aid}>{bid}"]=meta
        tree[sid]={"h1":one,"h2":two}

    # Determinism control: base, first action, replay twice.
    aid0=action_ids[0]
    sd0=R.derive_seed(a.seed,"oacr_l1_h1",aid0)
    c1,_=apply_action(editor,cfg,runtime["base"]["snapshot"],action_map[aid0],
                      protected_tokens,panel_tokens,sd0)
    c2,_=apply_action(editor,cfg,runtime["base"]["snapshot"],action_map[aid0],
                      protected_tokens,panel_tokens,sd0)
    replay_ok=(
        meta_signature(c1)==meta_signature(c2)
        and reads_equal(c1["post_reads"],c2["post_reads"],a.read_atol,a.read_rtol)
        and c1["post_state_hash"]==c2["post_state_hash"]
    )
    if not replay_ok:
        raise RuntimeError("duplicate replay failed")

    state_ids=[x["state_id"] for x in serial_states]
    eq_by_h={h:{} for h in (0,1,2)}
    pair_rows=[]

    def root_eq(x,y):
        return reads_equal(runtime[x]["root_reads"],runtime[y]["root_reads"],
                           a.read_atol,a.read_rtol)

    for x in state_ids:
        for y in state_ids:
            e0=root_eq(x,y)
            e1=e0
            if e1:
                for aid in action_ids:
                    bx,by=tree[x]["h1"][aid],tree[y]["h1"][aid]
                    if meta_signature(bx)!=meta_signature(by) or not reads_equal(
                        bx["post_reads"],by["post_reads"],a.read_atol,a.read_rtol
                    ):
                        e1=False
                        break
            e2=e1
            if e2:
                for seq in sorted(tree[x]["h2"]):
                    bx,by=tree[x]["h2"][seq],tree[y]["h2"][seq]
                    if meta_signature(bx)!=meta_signature(by) or not reads_equal(
                        bx["post_reads"],by["post_reads"],a.read_atol,a.read_rtol
                    ):
                        e2=False
                        break
            eq_by_h[0][(x,y)]=e0
            eq_by_h[1][(x,y)]=e1
            eq_by_h[2][(x,y)]=e2

    def feature_sig(sid,level):
        f=runtime[sid]["features"]
        out=[]
        for aid in action_ids:
            x=f[aid]
            if level==1:
                out.append(x["action_route"]["update_mode"])
            elif level==2:
                out.append({
                    "route":x["action_route"],
                    "protected":x["protected_route_signature"],
                })
            else:
                out.append({
                    "route":x["action_route"],
                    "protected":x["protected_route_signature"],
                    "projection":x["projection_signature"],
                })
        return json.dumps(out,sort_keys=True,separators=(",",":"))

    for x,y in itertools.combinations(state_ids,2):
        e0,e1,e2=(eq_by_h[h][(x,y)] for h in (0,1,2))
        if not e0: first=0
        elif not e1: first=1
        elif not e2: first=2
        else: first=None
        feats={f"F{k}_equal":feature_sig(x,k)==feature_sig(y,k) for k in (1,2,3)}
        pair_rows.append({
            "state_a":x,"state_b":y,
            "equiv_h0":e0,"equiv_h1":e1,"equiv_h2":e2,
            "first_separation_horizon":first,
            **feats,
        })

    horizon={}
    for h in (0,1,2):
        n,audit=count_blocks_if_equivalence(state_ids,eq_by_h[h])
        horizon[str(h)]={
            "transitivity":audit,
            "N_h":n,
            "pairwise_equivalent_pairs":sum(
                int(r[f"equiv_h{h}"]) for r in pair_rows
            ),
        }

    feature_stats={}
    h0pairs=[r for r in pair_rows if r["equiv_h0"]]
    for k in (1,2,3):
        key=f"F{k}_equal"
        under=sum(int(r[key] and not r["equiv_h2"]) for r in h0pairs)
        over=sum(int((not r[key]) and r["equiv_h2"]) for r in h0pairs)
        feature_stats[f"F{k}"]={
            "h0_collision_pairs":len(h0pairs),
            "under_refinement_pairs_at_h2":under,
            "over_refinement_pairs_at_h2":over,
        }

    summary={
        "seed":a.seed,
        "states":len(state_ids),
        "actions":len(action_ids),
        "h1_trajectories_per_state":len(action_ids),
        "h2_trajectories_per_state":len(action_ids)**2,
        "h0_collision_pairs":sum(int(r["equiv_h0"]) for r in pair_rows),
        "h1_separations_from_h0":sum(int(r["equiv_h0"] and not r["equiv_h1"]) for r in pair_rows),
        "h2_separations_from_h1":sum(int(r["equiv_h1"] and not r["equiv_h2"]) for r in pair_rows),
        "horizon":horizon,
        "feature_stats":feature_stats,
        "duplicate_replay_pass":replay_ok,
    }

    serial_tree={}
    for sid in state_ids:
        serial_tree[sid]=tree[sid]

    out={
        "protocol":"OACR_L1_GRACE_H2_V1",
        "official_grace_commit":"f674183f17a995d109e10ee6140d4c3e6d016115",
        "seed":a.seed,
        "read_match":{"atol":a.read_atol,"rtol":a.read_rtol},
        "seed_contract":seed_contract,
        "panel_manifest":panel_manifest,
        "anchor_attempts":attempts,
        "states":serial_states,
        "action_ids":[int(x) for x in action_ids],
        "behavior_tree":serial_tree,
        "pairs":pair_rows,
        "summary":summary,
    }
    p=Path(a.out)
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(out,indent=2))
    print(json.dumps(summary,indent=2))


if __name__=="__main__":
    main()
