#!/usr/bin/env python3
"""Post-run artifact audit; no native execution, evaluator or model calls."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path


def read(path):
    return json.loads(path.read_text())


def sha(data):
    return hashlib.sha256(data).hexdigest()


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def main():
    parser = argparse.ArgumentParser(__doc__)
    for key in ['private-root', 'public-root', 'source-root', 'original-private-root', 'commit-proof']:
        parser.add_argument('--' + key, type=Path, required=True)
    args = parser.parse_args()
    here = Path(__file__).resolve().parent
    spec = importlib.util.spec_from_file_location('frozen_quote_runner', here / 'paired_quote_diagnostic.py')
    q = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(q)
    args.freeze = args.public_root / 'freeze.json'
    args.original_freeze = here.parent / 'oacr_residual_discovery/recovery/freeze.json'
    args.freeze_commit = read(args.commit_proof)['commit_sha']
    frozen = q.verify_prepared(args, committed=True)
    public = read(args.public_root / 'RESULT_2026-10-04.json')
    require(public['freeze_sha256'] == sha(args.freeze.read_bytes()), 'result freeze mismatch')
    require(public['freeze_commit'] == args.freeze_commit, 'result commit mismatch')
    require(public['commit_proof_sha256'] == sha(args.commit_proof.read_bytes()), 'proof mismatch')
    require(public['status'] == 'paired_complete' and public['paired_invariants_passed'], 'pair incomplete')
    metadata = read(args.private_root / 'metadata.json')
    steps = [str(e) for e in q.EVENTS[:-2]] + ['check'] + [str(e) for e in q.EVENTS[-2:]]
    summaries, totals = {}, {}
    directory = args.private_root
    ready = max((directory / a / 'predelete_ready.json').stat().st_mtime_ns for a in ['A', 'B'])
    closed = max((directory / a / 'closed.json').stat().st_mtime_ns for a in ['A', 'B'])
    for arm in ['A', 'B']:
        root = directory / arm
        files = sorted(root.glob('ledger_*.json'))
        entries = [read(p) for p in files]
        expected_ops = ['world_init_attempt'] + ['native_attempt', 'native_result'] * 10 + ['world_close_attempt', 'grade_attempt']
        require([e['op'] for e in entries] == expected_ops, 'attempt/result sequence mismatch')
        require(entries[0]['load_ground_truth'] is False, 'ground truth enabled')
        attempts = [e for e in entries if e['op'] == 'native_attempt']
        results = [e for e in entries if e['op'] == 'native_result']
        require([e['step'] for e in attempts] == steps, 'unexpected or repeated step')
        require([e['attempt'] for e in attempts] == list(range(1, 11)), 'attempt numbering')
        require([e['step'] for e in results] == steps, 'missing or reordered result')
        for attempted, returned in zip(attempts, results):
            step = attempted['step']
            require(attempted['code_sha256'] == frozen['payload_sha256'][arm][step], 'payload mismatch')
            receipt = (root / (step + '.receipt.txt')).read_bytes()
            require(sha(receipt) == returned['receipt_sha256'], 'receipt hash mismatch')
            require(len(receipt) == returned['receipt_bytes'], 'receipt size mismatch')
            require(returned['execution_error'] is False, 'native failure')
        require(results[7]['native_api_calls'] == 0, 'parser made business API calls')
        recomputed = q.summary_from_payload(read(root / 'predelete_payload.json'), metadata, arm)
        recomputed.update(native_attempts=8, native_api_calls=sum(e['native_api_calls'] for e in results[:8]))
        require(recomputed == read(root / 'predelete_ready.json') == public['predelete'][arm], 'readback audit mismatch')
        summaries[arm] = recomputed
        authorize = {'freeze_sha256': public['freeze_sha256'], 'command': 'authorize_delete'}
        require(read(root / 'authorize_delete.json') == authorize, 'delete authorization mismatch')
        require(ready <= (root / 'authorize_delete.json').stat().st_mtime_ns <= files[17].stat().st_mtime_ns, 'delete barrier order')
        authorize['command'] = 'authorize_grade'
        require(read(root / 'authorize_grade.json') == authorize, 'grade authorization mismatch')
        require(closed <= (root / 'authorize_grade.json').stat().st_mtime_ns <= files[-1].stat().st_mtime_ns, 'grade barrier order')
        require(entries[-1] == {'op': 'grade_attempt', 'attempt': 1, 'after_close': True}, 'grade attempt mismatch')
        grade = read(root / 'grade.json')
        require(grade['attempts'] == 1 and grade['status'] == 'evaluated', 'grade did not return once')
        require(grade['success_count'] == public['producer_success_counts'][arm], 'score mismatch')
        total = {'native_attempts': len(attempts), 'native_api_calls': sum(e['native_api_calls'] for e in results),
                 'receipt_bytes': sum(e['receipt_bytes'] for e in results),
                 'native_elapsed_seconds': sum(e['elapsed_seconds'] for e in results), 'grade_attempts': 1}
        status = public['arm_status'][arm]
        require(total['native_api_calls'] == status['native_api_calls_known_subtotal'], 'API total mismatch')
        require(total['receipt_bytes'] == status['generated_receipt_bytes_known_subtotal'], 'byte total mismatch')
        require(total['native_elapsed_seconds'] == status['native_elapsed_seconds_known_subtotal'], 'elapsed total mismatch')
        require(read(root / 'closed.json')['native_attempts'] == total['native_attempts'], 'close count mismatch')
        totals[arm] = total
    q.cross_arm_check(summaries['A'], summaries['B'])
    require(public['grade_attempts'] == 2, 'grade total mismatch')
    branch = ''.join(str(public['producer_success_counts'][a]) for a in ['A', 'B'])
    require(public['branch'] == frozen['branch_registration'][branch], 'unregistered branch')
    # The original A native outputs are pinned to the old legal receipts.
    for step, expected in zip(q.EVENTS, q.ORIGINAL_RECEIPT_SHA):
        require(sha((directory / 'A' / (str(step) + '.receipt.txt')).read_bytes()) == expected, 'A differs from original receipt')
    result = {'date': '2026-10-05', 'scope': 'post_run_artifact_audit', 'passed': True,
              'result_sha256': sha((args.public_root / 'RESULT_2026-10-04.json').read_bytes()),
              'freeze_commit': args.freeze_commit, 'freeze_sha256': public['freeze_sha256'],
              'audit_source_sha256': sha(Path(__file__).read_bytes()), 'arm_costs': totals,
              'fixed_native_steps_each_once': True, 'receipts_and_payload_hashes_verified': True,
              'paired_parsers_and_readback_rechecked': True, 'barrier_source_and_file_order_verified': True,
              'canonical_shared_assets_matching_after_run': 12, 'original_A_receipt_hashes_matching': 9,
              'original_frozen_code_and_legal_evidence_hashes_reverified': True,
              'model_calls_by_audit': 0, 'world_native_evaluator_calls_by_audit': 0,
              'limits': ['artifact audit and frozen source verification; not an independent native replication',
                         'file order checks use local filesystem metadata; no cryptographic execution attestation',
                         'root model tokens and billing are unavailable',
                         'installed native app source hashes are pinned; not tracked in the ACE Git revision']}
    target = args.public_root / 'AUDIT_2026-10-05.json'
    with target.open('x') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    print(json.dumps({'passed': True, 'native_attempts': sum(t['native_attempts'] for t in totals.values()),
                      'native_api_calls': sum(t['native_api_calls'] for t in totals.values()),
                      'generated_receipt_bytes': sum(t['receipt_bytes'] for t in totals.values())}))


if __name__ == '__main__':
    main()
