"""Prepare a dev-only full-record manifest from the frozen N0 split.

This program is structural-only. It may read the frozen RippleEdits release to
materialize the already-selected 128 dev units, but emits no evaluation units.
"""
from __future__ import annotations
import argparse, importlib.util, json, sys
from pathlib import Path

def load_preflight(root: Path):
    p=root/"experiments/oacr_natural_learned/preflight_rippleedits_v1.py"
    spec=importlib.util.spec_from_file_location("n0", p)
    mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--repo_root", required=True)
    ap.add_argument("--ripple_dir", required=True)
    ap.add_argument("--out", required=True)
    a=ap.parse_args()
    root=Path(a.repo_root).resolve(); ripple=Path(a.ripple_dir).resolve()
    n0=load_preflight(root)

    rows_by_subset={}
    full_by_id={}
    dev=[]
    for subset in ("recent","random","popular"):
        src=json.loads((ripple/"data"/"benchmark"/f"{subset}.json").read_text(encoding="utf-8"))
        inspected=[]
        for entry in src:
            row=n0.inspect_entry(entry, subset)
            inspected.append(row)
            full_by_id[row["unit_id"]]={"unit_id":row["unit_id"],"subset":subset,"entry":entry}
        d,_=n0.split_subset(inspected, subset)
        rows_by_subset[subset]=d
        dev.extend(d)

    if len(dev)!=128:
        raise SystemExit(f"expected 128 frozen dev units, got {len(dev)}")
    dev_ids=[x["unit_id"] for x in dev]
    if len(set(dev_ids))!=128:
        raise SystemExit("duplicate dev ids")

    # Freeze an outcome-blind matched-sham mapping inside the dev bank.
    meta={x["unit_id"]:x for x in dev}
    sham={}
    for uid in dev_ids:
        x=meta[uid]
        pool=[v for v in dev_ids if v!=uid and meta[v]["relation"]!=x["relation"] and meta[v]["subject_id"]!=x["subject_id"]]
        if not pool:
            raise SystemExit(f"no sham pool for {uid}")
        pool=sorted(pool, key=lambda v:n0.h(n0.SEED,"n1-sham",uid,v))
        sham[uid]=pool[0]

    payload={
        "protocol":"OACR_NATURAL_LEARNED_N1_DEV_MANIFEST_V1",
        "n0_seed":n0.SEED,
        "ripple_commit":"54f3b88af4895a3aacb580ec63ce7ae857185040",
        "development_size":128,
        "evaluation_units_emitted":0,
        "unit_ids":dev_ids,
        "sham_map":sham,
        "units":[full_by_id[u] for u in dev_ids],
    }
    out=Path(a.out); out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({"status":"PASS","development_size":128,"evaluation_units_emitted":0},indent=2))

if __name__=="__main__":
    main()
