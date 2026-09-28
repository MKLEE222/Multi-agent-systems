"""Prospective structural-hazard prediction for official GRACE + SCOTUS.

This stage intentionally does NOT execute any future edit. It builds the same
contract-preserving seed state and anchor/future candidate pool as the paired
R1 runner, commits each anchor, and predicts future selective-write divergence
from GRACE's exact iteration-0 key/radius structural projection alone.

Run this first and freeze its JSON output. Only then run
run_scotus_paired_closure.py and compare outcomes with
validate_structural_predictions.py.
"""
from __future__ import annotations
import argparse, json, os, random, sys
from pathlib import Path
from typing import Any
import numpy as np
import torch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run_scotus_paired_closure as R  # noqa: E402
from grace_write_probe import (  # noqa: E402
    capture_query,
    commit_anchor_write,
    get_adapter,
    projected_route_preservation_certificate,
    restore_adapter,
    route_probe,
    snapshot_adapter,
)


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--repo', required=True)
    p.add_argument('--out', required=True)
    p.add_argument('--seed_edits', type=int, default=4)
    p.add_argument('--candidate_bank', type=int, default=128)
    p.add_argument('--future_per_anchor', type=int, default=12)
    p.add_argument('--anchors_per_mode', type=int, default=1)
    p.add_argument('--seed_scan_limit', type=int, default=512)
    p.add_argument('--read_atol', type=float, default=1e-6)
    p.add_argument('--read_rtol', type=float, default=1e-5)
    p.add_argument('--seed', type=int, default=42)
    p.add_argument('--device', default='cuda' if torch.cuda.is_available() else 'cpu')
    return p.parse_args()


def _linf(a, b):
    return max((abs(float(x) - float(y)) for x, y in zip(a, b)), default=0.0)


def fallback_correctness(editor, obligations):
    """Evaluate each protected obligation with GRACE retrieval disabled."""
    adapter = get_adapter(editor)
    snap = snapshot_adapter(adapter)
    if not snap.has_codebook:
        return [R.acc(editor, t) >= 1.0 for t in obligations]
    old_eps = adapter.epsilons.detach().clone()
    old_training = adapter.training
    adapter.training = False
    adapter.epsilons = torch.full_like(adapter.epsilons, -1e9)
    try:
        vals = [bool(R.acc(editor, t) >= 1.0) for t in obligations]
    finally:
        adapter.epsilons = old_eps
        adapter.training = old_training
    return vals


def main():
    args = parse_args()
    repo = Path(args.repo).resolve()
    sys.path.insert(0, str(repo))
    os.chdir(repo)
    random.seed(args.seed); np.random.seed(args.seed); torch.manual_seed(args.seed)

    from grace.dataset import SCOTUS
    from grace.editors import GRACE
    from grace.models import Classifier

    cfg = R.load_config(repo, args.device)
    model = Classifier(cfg).to(args.device)
    editor = GRACE(cfg, model)
    dataset = SCOTUS(split='edit')

    seed_rows, obligations, max_idx, seed_contract = R.build_contract_preserving_seed_state(
        editor, cfg, dataset, editor.tokenizer, args.device,
        args.seed_edits, args.seed_scan_limit, args.seed,
    )
    state_pre = snapshot_adapter(get_adapter(editor))
    restore_adapter(get_adapter(editor), state_pre)
    fallback_ok = fallback_correctness(editor, obligations)
    bank = R.collect_errors(editor, dataset, editor.tokenizer, args.device, max_idx + 1, args.candidate_bank)
    enriched = R.enrich_routes(editor, bank)
    anchors = R.choose_anchors_by_native_mode(enriched, args.anchors_per_mode)

    out = {
        'protocol': 'R1_GRACE_SCOTUS_STRUCTURAL_PREDICTION_V1',
        'future_edits_executed': False,
        'criterion': (
            'eligible iff anchor target succeeds and preserves fixed obligations, candidate logits and '
            'fixed-obligation logits match pre/post within frozen tolerance, and candidate remains a '
            'nonzero-write target; predict strict selective gain iff pre projection structurally removes '
            'support from at least one protected obligation whose retrieval-disabled fallback is wrong, '
            'while post projection has a protected-route preservation certificate'
        ),
        'seed': args.seed,
        'seed_indices': [x['idx'] for x in seed_rows],
        'seed_contract': seed_contract,
        'protected_fallback_correct': fallback_ok,
        'config': {
            'seed_edits': args.seed_edits,
            'candidate_bank': args.candidate_bank,
            'future_per_anchor': args.future_per_anchor,
            'anchors_per_mode': args.anchors_per_mode,
            'seed_scan_limit': args.seed_scan_limit,
            'read_atol': args.read_atol,
            'read_rtol': args.read_rtol,
        },
        'pairs': [],
    }

    for anchor in anchors:
        aid = anchor['idx']
        restore_adapter(get_adapter(editor), state_pre)
        future = R.select_future_pool(anchor, enriched, args.future_per_anchor)

        fixed_read_pre = R.read_family_signatures(editor, obligations)
        protected_queries_pre = [capture_query(editor, t) for t in obligations]
        anchor_pre_acc = R.acc(editor, anchor['tokens'])
        anchor_route_pre = route_probe(
            get_adapter(editor), capture_query(editor, anchor['tokens']), anchor['tokens']['labels']
        ).to_dict()

        state_post = commit_anchor_write(
            editor, cfg, anchor['tokens'], seed=R.derive_seed(args.seed, 'anchor', aid)
        )
        anchor_post_acc = R.acc(editor, anchor['tokens'])
        anchor_preserves = R.obligation_status(editor, obligations)['all_satisfied']
        fixed_read_post = R.read_family_signatures(editor, obligations)
        fixed_cmp = R.compare_read_family(
            fixed_read_pre, fixed_read_post, args.read_atol, args.read_rtol
        )
        protected_queries_post = [capture_query(editor, t) for t in obligations]
        qdrifts = [
            float(torch.linalg.vector_norm(a - b).detach().cpu().item())
            for a, b in zip(protected_queries_pre, protected_queries_post)
        ]

        for cand in future:
            cid = cand['idx']
            restore_adapter(get_adapter(editor), state_pre)
            pre_acc = R.acc(editor, cand['tokens'])
            pre_sig = R.read_signature(editor, cand['tokens'])
            pre_q = capture_query(editor, cand['tokens'])
            pre_route = route_probe(get_adapter(editor), pre_q, cand['tokens']['labels']).to_dict()
            pre_hazard = projected_route_preservation_certificate(
                get_adapter(editor), state_pre, pre_q, cand['tokens']['labels'], protected_queries_pre
            )

            restore_adapter(get_adapter(editor), state_post)
            post_acc = R.acc(editor, cand['tokens'])
            post_sig = R.read_signature(editor, cand['tokens'])
            post_q = capture_query(editor, cand['tokens'])
            post_route = route_probe(get_adapter(editor), post_q, cand['tokens']['labels']).to_dict()
            post_hazard = projected_route_preservation_certificate(
                get_adapter(editor), state_post, post_q, cand['tokens']['labels'], protected_queries_post
            )

            candidate_match = bool(np.allclose(
                np.asarray(pre_sig['logits']), np.asarray(post_sig['logits']),
                atol=args.read_atol, rtol=args.read_rtol,
            ))
            eligible = bool(
                anchor_post_acc >= 1.0 and anchor_preserves and candidate_match
                and fixed_cmp['strict_logits_matched'] and pre_acc < 1.0 and post_acc < 1.0
            )
            forced_failure = [
                i for i in pre_hazard['lost_indices']
                if i < len(fallback_ok) and not fallback_ok[i]
            ]
            predicted = bool(
                eligible and len(forced_failure) > 0
                and post_hazard['preservation_certificate']
            )
            out['pairs'].append({
                'anchor_id': aid,
                'candidate_id': cid,
                'stratum': cand['stratum'],
                'anchor_route_mode': anchor_route_pre['update_mode'],
                'anchor_pre_accuracy': anchor_pre_acc,
                'anchor_post_accuracy': anchor_post_acc,
                'anchor_preserves_fixed': bool(anchor_preserves),
                'candidate_pre_accuracy': pre_acc,
                'candidate_post_accuracy': post_acc,
                'candidate_read_linf': _linf(pre_sig['logits'], post_sig['logits']),
                'fixed_read_linf': fixed_cmp['max_logit_linf'],
                'fixed_read_strict': fixed_cmp['strict_logits_matched'],
                'protected_query_max_drift_l2': max(qdrifts) if qdrifts else 0.0,
                'pre_route_mode': pre_route['update_mode'],
                'post_route_mode': post_route['update_mode'],
                'pre_lost_support': pre_hazard['lost_indices'],
                'pre_forced_failure_indices': forced_failure,
                'post_lost_support': post_hazard['lost_indices'],
                'post_preservation_certificate': post_hazard['preservation_certificate'],
                'post_trained_value_index': post_hazard['trained_value_index'],
                'post_protected_uses_trained_row': post_hazard['protected_uses_trained_row'],
                'eligible': eligible,
                'predicted_strict_gain': predicted,
            })

    out['n_pairs'] = len(out['pairs'])
    out['n_eligible'] = sum(x['eligible'] for x in out['pairs'])
    out['n_predicted_positive'] = sum(x['predicted_strict_gain'] for x in out['pairs'])
    out['predicted_pairs'] = [
        {k: x[k] for k in (
            'anchor_id','candidate_id','stratum','pre_route_mode','post_route_mode',
            'pre_lost_support','pre_forced_failure_indices','post_lost_support',
            'post_preservation_certificate','post_trained_value_index'
        )}
        for x in out['pairs'] if x['predicted_strict_gain']
    ]
    Path(args.out).write_text(json.dumps(out, indent=2))
    print(json.dumps({
        'protocol': out['protocol'],
        'n_pairs': out['n_pairs'],
        'n_eligible': out['n_eligible'],
        'n_predicted_positive': out['n_predicted_positive'],
        'predicted_pairs': out['predicted_pairs'],
    }, indent=2))

if __name__ == '__main__':
    main()