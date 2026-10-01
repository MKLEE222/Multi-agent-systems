"""OACR Natural Learned N1 dev-only execution smoke.

Primary edit: official GRACE T5-small QA path.
Representation interventions:
  B0 base GRACE adaptor after the factual edit.
  B1 predictive auxiliary keys from construction-visible condition prompts.
  B2 same-cost sham keys from a frozen matched dev unit.
  A0 oracle diagnostic keys from held-out dev test prompts.

No evaluation-bank file or ID is accepted by this program.
"""
from __future__ import annotations
import argparse, copy, gc, json, math, random, re, sys
from pathlib import Path
from typing import Any
import torch
from omegaconf import OmegaConf

CRITERIA=("Relation_Specificity","Logical_Generalization","Subject_Aliasing",
          "Compositionality_I","Compositionality_II","Forgetfulness")

def norm(s:str)->str:
    import string
    s=s.lower()
    s="".join(ch for ch in s if ch not in set(string.punctuation))
    s=re.sub(r"\b(a|an|the)\b"," ",s)
    return " ".join(s.split())

def parse_edit_fact(sentence:str):
    s=str(sentence).strip().rstrip(".")
    for sep in (" is followed by "," follows "," are "," is "):
        i=s.rfind(sep)
        if i>=0:
            prompt=s[:i+len(sep)].strip()
            target=s[i+len(sep):].strip()
            if prompt and target:
                return prompt,target
    return None,None

def all_blocks(entry):
    for criterion in CRITERIA:
        for block in entry.get(criterion,[]) or []:
            if isinstance(block,dict):
                yield criterion,block

def query_rows(entry, field):
    out=[]
    for criterion,block in all_blocks(entry):
        for q in block.get(field,[]) or []:
            if isinstance(q,dict) and isinstance(q.get("prompt"),str):
                out.append((criterion,q))
    return out

def unique_prompts(entry, field, exclude=None):
    ex={norm(x) for x in (exclude or [])}
    seen=set(); out=[]
    for _,q in query_rows(entry,field):
        p=q["prompt"].strip(); n=norm(p)
        if not n or n in ex or n in seen: continue
        seen.add(n); out.append(p)
    return out

def heldout_queries(entry):
    cond=[q["prompt"] for _,q in query_rows(entry,"condition_queries")]
    condn={norm(x) for x in cond}
    seen=set(); out=[]
    for criterion,q in query_rows(entry,"test_queries"):
        n=norm(q["prompt"])
        if not n or n in condn or n in seen: continue
        seen.add(n); out.append((criterion,q))
    return out

def accepted_answer_groups(q):
    groups=[]
    for a in q.get("answers",[]) or []:
        vals=[]
        if isinstance(a,dict):
            if a.get("value") is not None: vals.append(str(a["value"]))
            vals += [str(x) for x in (a.get("aliases") or [])]
        vals=[norm(x) for x in vals if norm(x)]
        if vals: groups.append(vals)
    return groups

def query_pass(text,q):
    pred=norm(text)
    groups=accepted_answer_groups(q)
    if not groups: return False
    return all(any(v in pred for v in group) for group in groups)

def cfg(device,n_iter):
    return OmegaConf.create({
        "device":device,"re_init_model":False,"dropout":0.0,
        "model":{
            "name":"google/t5-small-ssm-nq",
            "class_name":"AutoModelForSeq2SeqLM",
            "tokenizer_class":"AutoTokenizer",
            "tokenizer_name":"google/t5-small-ssm-nq",
            "inner_params":["encoder.block[4].layer[1].DenseReluDense.wo.weight"],
            "pt":None,
        },
        "experiment":{"task":"qa","dataset":"rippleedits","cbase":1.0},
        "editor":{
            "_name":"grace","edit_lr":1.0,"n_iter":int(n_iter),"eps":1.0,
            "dist_fn":"euc","val_init":"cold","val_train":"sgd","val_reg":None,
            "reg":"early_stop","replacement":"replace_prompt","eps_expand":"coverage","num_pert":8,
        },
    })

def tokenize_pair(prompt,target,tok,device):
    enc=tok([prompt],padding="longest",max_length=64,truncation=True,return_tensors="pt")
    tgt=tok([target],padding="longest",max_length=32,truncation=True,return_tensors="pt")
    labels=tgt.input_ids.clone(); labels[labels==tok.pad_token_id]=-100
    return {"input_ids":enc.input_ids.to(device),"attention_mask":enc.attention_mask.to(device),"labels":labels.to(device)}

def gen(editor,prompt):
    tok=editor.tokenizer
    enc=tok([prompt],padding=True,max_length=64,truncation=True,return_tensors="pt")
    enc={k:v.to(editor.config["device"]) for k,v in enc.items()}
    with torch.no_grad():
        ids=editor.generate(**enc,max_new_tokens=24)
    return tok.decode(ids[0],skip_special_tokens=True)

def get_adapter(editor):
    return eval(f"editor.model.{editor.layer}")

def snapshot(adapter):
    return {
        "keys":adapter.keys.detach().clone(),
        "values":adapter.values.detach().clone(),
        "epsilons":adapter.epsilons.detach().clone(),
        "key_labels":[x.detach().clone() if torch.is_tensor(x) else copy.deepcopy(x) for x in adapter.key_labels],
    }

def restore(adapter,s):
    adapter.keys=s["keys"].detach().clone().to(adapter.device)
    adapter.values=torch.nn.Parameter(s["values"].detach().clone().to(adapter.device),requires_grad=True)
    adapter.epsilons=s["epsilons"].detach().clone().to(adapter.device)
    adapter.key_labels=[x.detach().clone().to(adapter.device) if torch.is_tensor(x) else copy.deepcopy(x) for x in s["key_labels"]]

def capture_key(editor,prompt):
    adapter=get_adapter(editor); box={}
    def hook(module,args):
        token_to_edit=min(module.key_id,args[0].shape[1]-1)
        box["q"]=args[0][:,token_to_edit,:].detach().clone()
    h=adapter.register_forward_pre_hook(hook)
    tok=editor.tokenizer([prompt],padding=True,max_length=64,truncation=True,return_tensors="pt")
    tok={k:v.to(editor.config["device"]) for k,v in tok.items()}
    with torch.no_grad(): editor.model(**tok)
    h.remove()
    return box["q"]

def add_aux(editor,prompts,max_aux):
    adapter=get_adapter(editor)
    if not prompts or max_aux<=0: return 0
    n=0
    base_value=adapter.values[0].detach().clone().view(1,-1)
    base_label=adapter.key_labels[0]
    for p in prompts[:max_aux]:
        q=capture_key(editor,p).detach().view(1,-1)
        adapter.keys=torch.vstack([adapter.keys,q])
        adapter.values=torch.nn.Parameter(torch.vstack([adapter.values.detach(),base_value.to(adapter.device)]),requires_grad=True)
        eps=torch.tensor(adapter.init_epsilon,device=adapter.device).view(1)
        adapter.epsilons=torch.vstack([adapter.epsilons,eps])
        adapter.key_labels.append(base_label.detach().clone() if torch.is_tensor(base_label) else copy.deepcopy(base_label))
        n+=1
    return n

def evaluate(editor,queries):
    rows=[]
    for criterion,q in queries:
        ans=gen(editor,q["prompt"])
        rows.append({"criterion":criterion,"prompt":q["prompt"],"prediction":ans,"pass":bool(query_pass(ans,q))})
    passed=sum(int(x["pass"]) for x in rows)
    return {"n":len(rows),"passed":passed,"accuracy":passed/len(rows) if rows else None,"rows":rows}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--manifest",required=True)
    ap.add_argument("--grace_repo",required=True)
    ap.add_argument("--out",required=True)
    ap.add_argument("--limit",type=int,default=8)
    ap.add_argument("--max_aux",type=int,default=2)
    ap.add_argument("--n_iter",type=int,default=100)
    ap.add_argument("--device",default="cpu")
    a=ap.parse_args()

    m=json.loads(Path(a.manifest).read_text(encoding="utf-8"))
    if m.get("evaluation_units_emitted")!=0 or "evaluation" in m:
        raise RuntimeError("evaluation bank access forbidden")
    if m.get("development_size")!=128:
        raise RuntimeError("wrong dev manifest")
    units={u["unit_id"]:u for u in m["units"]}
    order=m["unit_ids"][:a.limit]

    sys.path.insert(0,str(Path(a.grace_repo).resolve()))
    from grace.models import QAModel
    from grace.editors import GRACE

    random.seed(1729); torch.manual_seed(1729)
    results=[]
    for idx,uid in enumerate(order):
        unit=units[uid]; entry=unit["entry"]
        edit_prompt,edit_target=parse_edit_fact(entry["edit"]["prompt"])
        if not edit_prompt:
            results.append({"unit_id":uid,"status":"UNPARSABLE_EDIT"}); continue

        c=cfg(a.device,a.n_iter)
        model=QAModel(c).to(a.device)
        editor=GRACE(c,model)
        editor.generate=model.model.generate

        tokens=tokenize_pair(edit_prompt,edit_target,editor.tokenizer,a.device)
        editor.edit(c,tokens,batch_history=[])
        adapter=get_adapter(editor)
        base_snap=snapshot(adapter)

        future=heldout_queries(entry)
        cond=unique_prompts(entry,"condition_queries")
        sham_uid=m["sham_map"][uid]
        sham_entry=units[sham_uid]["entry"]
        sham_prompts=unique_prompts(sham_entry,"condition_queries")
        oracle_prompts=[q["prompt"] for _,q in future]

        immediate=gen(editor,edit_prompt)
        immediate_ok=norm(edit_target) in norm(immediate)

        variants={}
        for name,prompts in (("B0_base",[]),("B1_predictive",cond),("B2_sham",sham_prompts),("A0_oracle",oracle_prompts)):
            restore(adapter,base_snap)
            added=add_aux(editor,prompts,a.max_aux) if prompts else 0
            variants[name]={"aux_keys":added,"future":evaluate(editor,future)}

        results.append({
            "unit_id":uid,"subset":unit["subset"],"status":"COMPLETE",
            "edit_prompt":edit_prompt,"edit_target":edit_target,
            "immediate_prediction":immediate,"immediate_success":bool(immediate_ok),
            "heldout_queries":len(future),"condition_prompts":len(cond),
            "sham_unit_id":sham_uid,"variants":variants,
        })
        del editor,model; gc.collect()

    complete=[x for x in results if x.get("status")=="COMPLETE"]
    def mean_acc(name):
        vals=[x["variants"][name]["future"]["accuracy"] for x in complete if x["variants"][name]["future"]["accuracy"] is not None]
        return sum(vals)/len(vals) if vals else None
    summary={
        "protocol":"OACR_NATURAL_LEARNED_N1_DEV_SMOKE_V1",
        "development_only":True,"evaluation_units_loaded":0,
        "requested_units":a.limit,"complete_units":len(complete),
        "unparsable_units":sum(x.get("status")=="UNPARSABLE_EDIT" for x in results),
        "max_aux":a.max_aux,"n_iter":a.n_iter,
        "mean_future_accuracy":{
            k:mean_acc(k) for k in ("B0_base","B1_predictive","B2_sham","A0_oracle")
        },
        "immediate_success_rate":(sum(int(x["immediate_success"]) for x in complete)/len(complete)) if complete else None,
    }
    out={"summary":summary,"units":results}
    p=Path(a.out); p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(summary,indent=2))
    if len(complete)<max(4,a.limit//2):
        raise SystemExit(2)

if __name__=="__main__":
    main()
