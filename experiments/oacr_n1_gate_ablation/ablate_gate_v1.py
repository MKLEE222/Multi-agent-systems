"""Retrospective gate ablation, with exact original replay and RNG restoration.

All-key radius 1e6 is an intervention for causal diagnosis, not a deployable
constructor or a predictive upper bound. No future answer selects a parameter.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import random
import sys

import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'oacr_n1_diagnostics'))
from replay_routing_v1 import (REFERENCE_SHA256, RUNNER_SHA256, SOURCE_DIR,
                               VARIANTS, RoutingObserver, codebook_digest,
                               compare_reports, runner)

FORCED_RADIUS = 1_000_000.0


def main():
    parser = argparse.ArgumentParser()
    for name in ('manifest', 'grace_repo', 'model_dir'):
        parser.add_argument('--' + name, required=True)
    for name in ('reference_report', 'replay_out', 'out'):
        parser.add_argument('--' + name, required=True, type=Path)
    args = parser.parse_args()
    assert hashlib.sha256((SOURCE_DIR / 'run_n1_dev_only.py').read_bytes()).hexdigest() == RUNNER_SHA256
    assert hashlib.sha256(args.reference_report.read_bytes()).hexdigest() == REFERENCE_SHA256
    assert args.replay_out.resolve() != args.reference_report.resolve()
    reference = json.loads(args.reference_report.read_text())
    assert reference['summary']['complete_units'] == 8
    original_evaluate = runner.evaluate
    observations = []

    def evaluate(editor, queries):
        call = len(observations)
        adapter = runner.get_adapter(editor)
        digest = codebook_digest(adapter)
        native = original_evaluate(editor, queries)
        # GRACE's inference itself draws an unused cold value. Preserve that
        # native RNG stream across the extra counterfactual forward calls.
        torch_rng = torch.get_rng_state().clone()
        python_rng = random.getstate()
        original_radii = adapter.epsilons.detach().clone()
        try:
            adapter.epsilons = torch.full_like(original_radii, FORCED_RADIUS)
            with RoutingObserver(adapter) as observer:
                forced = original_evaluate(editor, queries)
        finally:
            adapter.epsilons = original_radii
            torch.set_rng_state(torch_rng)
            random.setstate(python_rng)
        assert codebook_digest(adapter) == digest
        assert torch.equal(torch.get_rng_state(), torch_rng) and random.getstate() == python_rng
        assert len(observer.rows) == len(forced['rows']) == len(native['rows'])
        assert all(r['gate_active'] and r['copied_values_equal_base'] for r in observer.rows)
        observations.append({
            'unit_id': reference['units'][call // 4]['unit_id'],
            'variant': VARIANTS[call % 4],
            'queries': [dict(row, native_prediction=base['prediction'], native_pass=base['pass'], routing=telemetry)
                        for row, base, telemetry in zip(forced['rows'], native['rows'], observer.rows)],
        })
        return native

    runner.evaluate = evaluate
    original_argv = sys.argv
    sys.argv = [str(SOURCE_DIR / 'run_n1_dev_only.py'),
                '--manifest', args.manifest, '--grace_repo', args.grace_repo,
                '--model_dir', args.model_dir, '--out', str(args.replay_out),
                '--limit', '8', '--max_aux', '2', '--n_iter', '100', '--device', 'cpu']
    try:
        runner.main()
    finally:
        runner.evaluate = original_evaluate
        sys.argv = original_argv
    errors = compare_reports(reference, json.loads(args.replay_out.read_text()))
    totals = {}
    for variant in VARIANTS:
        counts = Counter()
        unit_acc = []
        for panel in observations:
            if panel['variant'] != variant:
                continue
            rows = panel['queries']
            unit_acc.append(sum(q['pass'] for q in rows) / len(rows))
            for q in rows:
                counts['queries'] += 1
                counts['gate_active'] += q['routing']['gate_active']
                counts['layer_output_changed'] += q['routing']['output_change_l2'] > 0
                counts['prediction_changed'] += q['prediction'] != q['native_prediction']
                counts['correct'] += q['pass']
                counts['gain'] += q['pass'] and not q['native_pass']
                counts['loss'] += q['native_pass'] and not q['pass']
        totals[variant] = dict(counts, mean_unit_accuracy=sum(unit_acc) / len(unit_acc))
    forced_identical = all(
        [(q['prediction'], q['pass']) for q in observations[i]['queries']] ==
        [(q['prediction'], q['pass']) for q in observations[i + j]['queries']]
        for i in range(0, len(observations), 4) for j in (1, 2, 3))
    report = {
        'protocol': 'OACR_N1_RETROSPECTIVE_ALL_KEY_GATE_ABLATION_V1',
        'authority': 'development causal diagnosis only; severe test-query intervention, no fresh confirmation',
        'evaluation_units_loaded': 0, 'reference_run': 36824729008,
        'reference_report_sha256': REFERENCE_SHA256, 'inherited_runner_sha256': RUNNER_SHA256,
        'forced_radius': FORCED_RADIUS, 'replay_exact': not errors, 'replay_errors': errors,
        'all_forced_variants_identical': forced_identical, 'summary': totals,
        'observations': observations,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ('replay_exact', 'all_forced_variants_identical', 'summary')}, indent=2))
    if errors:
        raise SystemExit('original replay differs; ablation has no localization authority')


if __name__ == '__main__':
    main()
