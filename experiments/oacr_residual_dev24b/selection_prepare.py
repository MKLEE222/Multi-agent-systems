"""Metadata-only next-variant preparation for the final AppWorld discovery.

No AppWorld import, task load, prompt read, evaluation or outcome-based selection.
"""
from __future__ import annotations
import copy
import hashlib
import json
from pathlib import Path
from model_budget import require_launch_registration

HERE = Path(__file__).resolve().parent
BASELINE_FREEZE = HERE.parent / 'oacr_residual_discovery/recovery/freeze.json'
MODEL_REGISTRATION = HERE / 'MODEL_BUDGET_REGISTRATION.json'

class MissingVariants(ValueError):
    def __init__(self, rows):
        super().__init__('not_started_no_unused_variant; no substitute or wraparound')
        self.public_rows = rows

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def select_next(ids, baseline):
    excluded = set(baseline['excluded_exposed_task_hashes']) | set(baseline['selected_task_hashes'])
    rows = []
    public_rows = []
    for i, (old_index, family_hash) in enumerate(zip(baseline['selected_manifest_indices'], baseline['selected_family_hashes'], strict=True)):
        if hashlib.sha256(ids[old_index].encode()).hexdigest() != baseline['selected_task_hashes'][i]:
            raise ValueError('original selection identity mismatch')
        match = None
        for j in range(old_index + 1, len(ids)):
            identity = ids[j]
            family = identity.split('_')[0]
            h = hashlib.sha256(identity.encode()).hexdigest()
            if hashlib.sha256(family.encode()).hexdigest() == family_hash and h not in excluded:
                match = {'index':i,'manifest_index':j,'task_id':identity,'family':family,
                         'task_sha256':h,'family_sha256':family_hash}
                break
        if match is None:
            public_rows.append({'index':i,'family_sha256':family_hash,'status':'not_started_no_unused_variant','task_id_sha256':None})
        else:
            public_rows.append({'index':i,'family_sha256':family_hash,'status':'metadata_candidate','task_id_sha256':match['task_sha256']})
            rows.append(match)
    if any(r['status']=='not_started_no_unused_variant' for r in public_rows):
        raise MissingVariants(public_rows)
    if len(rows) != 24 or len({r['family_sha256'] for r in rows}) != 24:
        raise ValueError('fixed family denominator changed')
    return rows

def verify_assets(root, frozen):
    for name, expected in frozen['canonical_shared_asset_sha256'].items():
        if digest(root/'data/base_dbs'/name) != expected:
            raise ValueError('shared canonical asset mismatch before world initialization')

def prepare(bridge, root, freeze_path, private_root, _exposure_path):
    model_registration = require_launch_registration(MODEL_REGISTRATION)
    baseline = json.loads(BASELINE_FREEZE.read_text())
    raw, ids = bridge.manifest(root)
    if bridge.source_head(root) != bridge.AUTHOR_SHA or bridge.sha(raw) != baseline['train_manifest_file_sha256']:
        raise ValueError('author source/manifest changed')
    try:
        selected = select_next(ids, baseline)
    except MissingVariants as exc:
        bridge.write_json_new(freeze_path.parent/'CAPACITY_RESULT_2026-10-04.json',{
            'fixed_denominator':24,'rows':exc.public_rows,'actors':0,'task_prompt_loads':0,
            'native_grades':0,'stop_without_replacement':True})
        raise
    stress_path = HERE/'TRANSPORT_STRESS_RESULT_2026-10-04.json'
    stress = json.loads(stress_path.read_text())
    if (stress.get('successful') is not True or stress.get('task_world_api_model_evaluator_calls') != 0
            or stress.get('appworld_imported') is not False
            or stress.get('transport_source_sha256') != digest(HERE/'transport_once.py')
            or stress.get('test_source_sha256') != digest(HERE/'test_transport_only.py')
            or not all(c['accepted_each_exactly_one_callback'] for c in stress['cases'].values())):
        raise ValueError('transport stub gate not passed')
    diagnostic_path = HERE/'diagnostic/RESULT_2026-10-04.json'
    diagnostic = json.loads(diagnostic_path.read_text())
    if diagnostic.get('diagnostic_terminal_record') is not True:
        raise ValueError('paired diagnostic has not reached disclosed terminal record')
    if diagnostic.get('paired_invariants_passed') is not True:
        raise ValueError('paired diagnostic control invalid; repair and separately register before B')
    frozen = copy.deepcopy(baseline)
    for key in ['infrastructure_reattempt','score_conditioned_actor_retry','task_replacement','aborted_batch_freeze_commit','aborted_batch_freeze_sha256','canonical_data_bundle_sha256','recovery_registration_sha256','native_outputs_namespace']:
        frozen.pop(key,None)
    frozen.update({
        'protocol':bridge.PROTOCOL,'run_id':bridge.PROTOCOL,
        'execution_protocol_sha256':digest(bridge.EXECUTION_PROTOCOL_PATH),
        'actor_instructions_sha256':digest(bridge.ACTOR_INSTRUCTIONS_PATH),
        'model_budget_registration_sha256':digest(MODEL_REGISTRATION),
        'model_identity_and_budget':model_registration,
        'model':model_registration.get('model_descriptor') if model_registration.get('schema')=='oacr_work_serial_actor_v1' else model_registration['identity']['model_snapshot'],
        'work_serial_protocol_sha256':digest(HERE.parents[1]/'docs/OACR_DEV24B_WORK_SERIAL_REGISTRATION_2026-10-05.md') if model_registration.get('schema')=='oacr_work_serial_actor_v1' else None,
        'baseline_recovery_freeze_sha256':digest(BASELINE_FREEZE),
        'selection':'fixed original family order; first unused manifest variant after original selected variant; no replacement or wraparound',
        'excluded_exposed_task_hashes':baseline['excluded_exposed_task_hashes'] + baseline['selected_task_hashes'],
        'original_selected_task_hashes':baseline['selected_task_hashes'],
        'selected_manifest_indices':[r['manifest_index'] for r in selected],
        'selected_task_hashes':[r['task_sha256'] for r in selected],
        'selected_family_hashes':[r['family_sha256'] for r in selected],
        'experiment_name_pattern':bridge.PROTOCOL+'_{index}',
        'retries_or_task_replacement':False,
        'transport':'atomic pre-dispatch claim; durable UUID claimed/executed/responded ledger; cached response only on duplicate; fail closed on unknown or conflicting UUID state',
        'implementation_sha256':{name:digest(HERE/name) for name in ['native_batch_bridge.py','actor_client.py','selection_prepare.py','transport_once.py','test_transport_only.py','export_results.py','model_budget.py']},
        'transport_stress_sha256':digest(stress_path),
        'paired_diagnostic_result_sha256':digest(diagnostic_path),
        'scope':'final outcome-independent AppWorld train broad discovery; no algorithm intervention or method comparison',
        'final_broad_discovery':True,
        'stop_if_no_R1':True,
        'R1_threshold':{'independent_tasks':3,'generator_families':2},
        'no_R1_interpretation':'No recurrent mechanism sufficient to induce a new core observed in two fixed development cross-sections; stop AppWorld core search, no universal absence claim.',
        'interpretation':'Final fixed next-variant development discovery; no test, novelty, method comparison or generalization claim',
    })
    verify_assets(root,frozen)
    for name,path in bridge.SOURCE_FILES.items():
        if digest(root/path) != baseline['source_file_sha256'][name]:
            raise ValueError('author implementation changed')
    if freeze_path.exists() or (private_root/'selection_mapping.json').exists():
        raise FileExistsError('refuse preparation overwrite')
    bridge.private_directory(private_root)
    mapping={'protocol':bridge.PROTOCOL,'train_manifest_sha256':frozen['train_manifest_sha256'],'selection':selected}
    bridge.write_json_new(private_root/'selection_mapping.json',mapping,private=True)
    frozen['selection_mapping_sha256']=digest(private_root/'selection_mapping.json')
    bridge.write_json_new(freeze_path,frozen)
    print(bridge.canonical({'status':'frozen','selected':24,'distinct_families':24,'tasks_loaded':0,'final_broad_discovery':True}))

def verify(bridge,root,freeze_path,private_root):
    model_registration = require_launch_registration(MODEL_REGISTRATION)
    frozen=json.loads(freeze_path.read_text())
    if digest(MODEL_REGISTRATION)!=frozen['model_budget_registration_sha256'] or model_registration!=frozen['model_identity_and_budget']:
        raise ValueError('frozen model identity or budget changed')
    if model_registration.get('schema')=='oacr_work_serial_actor_v1' and digest(HERE.parents[1]/'docs/OACR_DEV24B_WORK_SERIAL_REGISTRATION_2026-10-05.md')!=frozen['work_serial_protocol_sha256']:
        raise ValueError('frozen Work scope changed')
    baseline=json.loads(BASELINE_FREEZE.read_text())
    if frozen['protocol']!=bridge.PROTOCOL or bridge.source_head(root)!=bridge.AUTHOR_SHA:
        raise ValueError('protocol/source revision differs from freeze')
    if digest(BASELINE_FREEZE)!=frozen['baseline_recovery_freeze_sha256']:
        raise ValueError('baseline selection freeze changed')
    for path,key in [(bridge.PROTOCOL_PATH,'protocol_sha256'),(bridge.EXECUTION_PROTOCOL_PATH,'execution_protocol_sha256'),(bridge.ACTOR_INSTRUCTIONS_PATH,'actor_instructions_sha256')]:
        if digest(path)!=frozen[key]:raise ValueError('frozen protocol changed')
    for name,h in frozen['implementation_sha256'].items():
        if digest(HERE/name)!=h:raise ValueError('frozen implementation changed')
    for name,h in frozen['source_file_sha256'].items():
        if digest(root/bridge.SOURCE_FILES[name])!=h:raise ValueError('author implementation changed')
    for path,key in [(HERE/'TRANSPORT_STRESS_RESULT_2026-10-04.json','transport_stress_sha256'),(HERE/'diagnostic/RESULT_2026-10-04.json','paired_diagnostic_result_sha256')]:
        if digest(path)!=frozen[key]:raise ValueError('frozen prerequisite record changed')
    raw,ids=bridge.manifest(root)
    if bridge.sha(raw)!=frozen['train_manifest_file_sha256'] or bridge.sha('\n'.join(ids).encode())!=frozen['train_manifest_sha256']:
        raise ValueError('frozen manifest changed')
    selected=select_next(ids,baseline)
    for key,field in [('selected_manifest_indices','manifest_index'),('selected_task_hashes','task_sha256'),('selected_family_hashes','family_sha256')]:
        if [r[field] for r in selected]!=frozen[key]:raise ValueError('deterministic next variant changed')
    mapping_path=private_root/'selection_mapping.json'
    if digest(mapping_path)!=frozen['selection_mapping_sha256'] or json.loads(mapping_path.read_text())['selection']!=selected:
        raise ValueError('private selection mapping changed')
    checks={'max_execute_requests_per_actor':bridge.REQUEST_BUDGET,'code_timeout_seconds':bridge.CODE_TIMEOUT,'actor_wall_clock_seconds':bridge.ACTOR_TIMEOUT,'grade_timeout_seconds':bridge.GRADE_TIMEOUT,'transport_page_characters':bridge.PAGE_CHARS,'environment_random_seed':bridge.ENVIRONMENT_SEED,'actors':24,'high_cost_thresholds':bridge.HIGH_COST_THRESHOLDS}
    if any(frozen[k]!=v for k,v in checks.items()):raise ValueError('frozen budget changed')
    verify_assets(root,frozen)
    return frozen,selected
