"""Blindly compare a frozen structural-hazard manifest with actual R1 outcomes."""
from __future__ import annotations
import argparse, json
from pathlib import Path

p=argparse.ArgumentParser(); p.add_argument('--prediction',required=True); p.add_argument('--actual',required=True); p.add_argument('--out',required=True); args=p.parse_args()
pred=json.loads(Path(args.prediction).read_text()); act=json.loads(Path(args.actual).read_text())
if pred.get('future_edits_executed') is not False:
    raise RuntimeError('Prediction manifest is not marked future_edits_executed=false')
pm={(int(x['anchor_id']),int(x['candidate_id'])):bool(x['predicted_strict_gain']) for x in pred['pairs']}
am={}
for ar in act.get('anchor_runs',[]):
    if ar.get('status')!='COMMITTED': continue
    aid=int(ar['anchor']['dataset_index'])
    for row in ar.get('pairs',[]):
        am[(aid,int(row['candidate_id']))]=bool(row.get('strict_full_read_selective_witness'))
keys=sorted(set(pm)&set(am)); conf={'tp':0,'fp':0,'fn':0,'tn':0}
for k in keys:
    a,b=pm[k],am[k]
    conf['tp' if a and b else 'fp' if a and not b else 'fn' if (not a and b) else 'tn']+=1
out={'prediction_protocol':pred.get('protocol'),'actual_protocol':act.get('protocol'),'prediction_pairs':len(pm),'actual_pairs':len(am),'matched_pairs':len(keys),'missing_actual':len(set(pm)-set(am)),'missing_prediction':len(set(am)-set(pm)),'confusion':conf,'predicted_positive_pairs':[list(k) for k,v in pm.items() if v],'actual_strict_pairs':[list(k) for k,v in am.items() if v]}
Path(args.out).write_text(json.dumps(out,indent=2)); print(json.dumps(out,indent=2))