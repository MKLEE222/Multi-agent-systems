#!/usr/bin/env python3
"""Prepare/freeze or run the authorized single-task paired quote diagnostic.

Public code contains no task identity, destination, credentials, or actor code.
Only explicitly selected legal private events supply those values. Preparation
never imports AppWorld or Task. Running requires a committed frozen specification.
"""
from __future__ import annotations

import argparse
import ast
import builtins
from contextlib import redirect_stderr, redirect_stdout
import csv
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from typing import Any


PROTOCOL = "oacr_residual_dev24b_quote_v1"
TASK_HASH = "ea980c2b3fe30c2479b7eeec44e1abfba374a3b34b0811d567fe70de3ee51086"
FAMILY_HASH = "6410b74c66b363243f508ed0e1dd0c943cb54b8155d25a1c68fba349c70e80a0"
TASK_INDEX = 2
EVENTS = (32, 45, 48, 56, 61, 69, 72, 75, 78)
ORIGINAL_CODE_SHA = (
    "2b1b805966c2f38066fe7748e170b771273001e45e9867c228b05bb306f5add6",
    "e9631a2fb0ab3898ba5f9d77fd40bcce6a02882f91bc214a5707316146624866",
    "c30afa1bc03c7ec1f7ab4d104701a7cb8d3ea78c250dd5407341705ccc97c581",
    "2a7cdc2f59cf675942c2cadc277813fef81f65aef6b495d5dd77b671aecb0e52",
    "77b00d715b94a95dd8bf65b38d66442556479b8311c80ab92cf18d164fca4a81",
    "dc4034c1a7ecf80a7c48dda446d549038f26f664ae7a90eaca17f27e2ba15b4d",
    "7c6efdc2192aacb1bc6896d13a5f6fe3ad3ae5ad05246933a4fa07cad6972302",
    "cfd60d8141c31c6e059dc13c97a8e6d59d4860178151cc5a38b3a14851dd5a9a",
    "15288b6f37ad12b7072b4fb80201b65feedf69225d19817d8881aa8e032d3aa4",
)
ORIGINAL_RECEIPT_SHA = (
    "891d0fb4a615c976aece4d7af71f46ebb82bd6dda22e3c822cf5722a2975646c",
    "114366cb74d9275a886110d2fb6f96b0fd0b74c275684da230b1ca8346b0f8d4",
    "79f9b0986d28f652e497e3a6a58299aa143f128b61a21d0a20163425eac358ac",
    "e46326917f339dc5ae4b555fafab9cc6325aaa71248182f4f1195bb8f74e56fc",
    "804b2529b4c4066f3257a5191e9056ea2067a082c75df75e0221fc15383b0264",
    "1893b6a6aee7b333e89b0b776319f5e4a27f95cf9998bb94308e8fb18548cdaf",
    "d7511f0a112b9ee99966d0be37d244177327f89039efd82bddfb52d6c724af9a",
    "c20a4d709526d4fae063ce01cbb58aeb4b7bb9e01cff0be3aa727adf3f8cd7f4",
    "762c3b5df6af85d2179be736eb9ab83a8488322f0e265a7e841a17eb51ab6a18",
)
PROMPT_SHA = "36072efeec0e525b0f90844500a9e08051092a0daca59b892e956bf161d5e596"
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
BRIDGE = REPO / "experiments/oacr_residual_discovery/native_batch_bridge.py"
DOCUMENT = REPO / "docs/OACR_DEV24B_QUOTE_DIAGNOSTIC_PROTOCOL_2026-10-04.md"
TRANSPORT_MODULE = HERE / 'transport_once.py'
TRANSPORT_TEST = HERE / 'test_transport_only.py'
TRANSPORT_STRESS = HERE / 'TRANSPORT_STRESS_RESULT_2026-10-04.json'
EXPECTED_REPOSITORY = 'MKLEE222/Multi-agent-systems'
MARKER = "OACR_QUOTE_CHECK:"
SEED, BUDGET, CODE_TIMEOUT, ACTOR_TIMEOUT, GRADE_TIMEOUT = 123, 40, 20, 1200, 120

MINIMAL_QUOTE_FUNCTION = '''def csv_quote(value):
    if any(character in value for character in [',', '"', '\\r', '\\n']):
        return '"' + value.replace('"', '""') + '"'
    return value
'''

# Independently implemented parser: it never calls the serializer and does not
# import io, inspect native state, or issue a business API call. Expected column
# names are injected only in the private payload from the original instruction.
PARSER_TEMPLATE = '''def oacr_parse_csv(text):
    records = []
    record = []
    field = []
    state = 'start'
    position = 0
    while position < len(text):
        character = text[position]
        if state == 'quoted':
            if character == '"':
                state = 'after_quote'
            else:
                field.append(character)
        elif state == 'after_quote' and character == '"':
            field.append('"')
            state = 'quoted'
        elif character == ',' and state in ['start', 'unquoted', 'after_quote']:
            record.append(''.join(field))
            field = []
            state = 'start'
        elif character in ['\\n', '\\r'] and state in ['start', 'unquoted', 'after_quote']:
            record.append(''.join(field))
            records.append(record)
            record = []
            field = []
            state = 'start'
            if character == '\\r' and position + 1 < len(text) and text[position + 1] == '\\n':
                position += 1
        elif character == '"' and state == 'start':
            state = 'quoted'
        elif state in ['start', 'unquoted'] and character != '"':
            field.append(character)
            state = 'unquoted'
        else:
            raise ValueError('Invalid CSV transition')
        position += 1
    assert state != 'quoted', 'Unterminated CSV field'
    if state != 'start' or record or field:
        record.append(''.join(field))
        records.append(record)
    return records

oacr_expected_header = EXPECTED_HEADER_LITERAL
oacr_expected_rows = [list(row) for row in rows]
oacr_prepared_parse = oacr_parse_csv(csv_content)
oacr_saved_parse = oacr_parse_csv(backup_file['content'])
assert oacr_prepared_parse and oacr_saved_parse
assert oacr_prepared_parse[0] == oacr_expected_header
assert oacr_saved_parse[0] == oacr_expected_header
assert all(len(row) == len(oacr_expected_header) for row in oacr_prepared_parse)
assert all(len(row) == len(oacr_expected_header) for row in oacr_saved_parse)
assert oacr_prepared_parse[1:] == oacr_expected_rows
assert oacr_saved_parse[1:] == oacr_expected_rows
assert len(oacr_saved_parse) - 1 == len(all_song_ids) == len(songs_by_id)
assert len(set(tuple(row) for row in oacr_saved_parse[1:])) == len(rows)
assert backup_file['content'] == csv_content
oacr_direct_ids = sorted(song['song_id'] for song in song_library)
oacr_album_ids = sorted(set(song_id for album in album_library for song_id in album['song_ids']))
oacr_playlist_ids = sorted(set(song_id for playlist in playlist_library for song_id in playlist['song_ids']))
assert set(oacr_direct_ids) | set(oacr_album_ids) | set(oacr_playlist_ids) == all_song_ids
assert set(songs_by_id) == all_song_ids
print('OACR_QUOTE_CHECK:' + repr({
    'header': oacr_expected_header,
    'expected_rows': oacr_expected_rows,
    'parsed_rows': oacr_saved_parse[1:],
    'source_ids': sorted(all_song_ids),
    'source_components': [oacr_direct_ids, oacr_album_ids, oacr_playlist_ids],
    'record_ids': sorted(songs_by_id),
    'content': backup_file['content'],
    'source_counts': [len(song_library), len(album_library), len(playlist_library)],
    'count': len(rows)
}))
'''


class DiagnosticFailure(Exception):
    """Fixed vocabulary only; raw native exceptions remain private."""


class HostArtifacts:
    """Tested host file helpers captured before any AppWorld import/guard.

    Native code has no reference to this class. Artifact creation is exclusive,
    fsynced, and never overwrites a failed or interrupted attempt.
    """
    def __init__(self) -> None:
        module_name = 'oacr_diagnostic_host_artifact_helpers'
        if module_name not in sys.modules:
            spec = importlib.util.spec_from_file_location(module_name, TRANSPORT_MODULE)
            if spec is None or spec.loader is None:
                raise DiagnosticFailure('host_artifact_helpers_load_error')
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
        self.helpers = sys.modules[module_name]
        self.chmod = os.chmod
        self.open_stream = builtins.open

    def read_bytes(self, path: Path) -> bytes:
        return self.helpers._read(str(path))

    def new(self, path: Path, data: bytes, private: bool = True) -> None:
        self.helpers._write_immutable(str(path), data)
        if not private:
            self.chmod(str(path), 0o644)
            self.helpers._sync_directory(str(path.parent))

    def json_new(self, path: Path, value: Any, private: bool = True) -> None:
        self.new(path, (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode(), private)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def value_sha(value: Any) -> str:
    return sha(json.dumps(value, ensure_ascii=False, sort_keys=True,
                          separators=(',', ':')).encode())


def load_json(path: Path, transport: HostArtifacts | None = None) -> Any:
    return json.loads((transport.read_bytes(path) if transport else path.read_bytes()).decode())


def git(*arguments: str, cwd: Path) -> bytes:
    return subprocess.check_output(['git', *arguments], cwd=cwd, stderr=subprocess.DEVNULL)


def load_bridge(original_freeze: Path | None = None) -> Any:
    original = load_json(original_freeze or REPO / 'experiments/oacr_residual_discovery/recovery/freeze.json')
    if sha(BRIDGE.read_bytes()) != original['implementation_sha256']['native_batch_bridge.py']:
        raise DiagnosticFailure('original_bridge_changed_before_import')
    spec = importlib.util.spec_from_file_location('oacr_frozen_native_bridge', BRIDGE)
    if spec is None or spec.loader is None:
        raise DiagnosticFailure('bridge_load_error')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify_transport_stress() -> None:
    result = load_json(TRANSPORT_STRESS)
    if (result.get('scope') != 'synthetic_transport_only' or result.get('tests_run') != 26
            or result.get('tests_passed') != 26 or result.get('failures') != 0
            or result.get('errors') != 0 or result.get('successful') is not True
            or result.get('appworld_imported') is not False or result.get('real_task_data_used') is not False
            or result.get('task_world_api_model_evaluator_calls') != 0):
        raise DiagnosticFailure('transport_stress_26_pass_required')
    if (result['transport_source_sha256'] != sha(TRANSPORT_MODULE.read_bytes())
            or result['test_source_sha256'] != sha(TRANSPORT_TEST.read_bytes())):
        raise DiagnosticFailure('transport_stress_source_hash_mismatch')


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def verify_commit_proof(args: argparse.Namespace) -> None:
    if not args.commit_proof or not args.freeze_commit or not re.fullmatch(r'[0-9a-f]{40}', args.freeze_commit):
        raise DiagnosticFailure('external_commit_proof_required')
    proof = load_json(args.commit_proof)
    if (proof.get('repository_full_name') != EXPECTED_REPOSITORY
            or proof.get('commit_sha') != args.freeze_commit
            or not re.fullmatch(r'[0-9a-f]{40}', str(proof.get('tree_sha', '')))
            or proof.get('verified_via') != 'GitHub connector read-back'):
        raise DiagnosticFailure('external_commit_proof_identity_mismatch')
    for path in [args.freeze, Path(__file__), DOCUMENT, BRIDGE, TRANSPORT_MODULE, TRANSPORT_TEST, TRANSPORT_STRESS]:
        relative = path.relative_to(REPO).as_posix()
        if proof.get('blobs', {}).get(relative) != git_blob_sha(path.read_bytes()):
            raise DiagnosticFailure('external_commit_proof_blob_mismatch')


def verify_original(args: argparse.Namespace, bridge: Any) -> tuple[dict[str, Any], dict[str, Any]]:
    frozen = load_json(args.original_freeze)
    if git('rev-parse', 'HEAD', cwd=args.source_root).decode().strip() != frozen['source_ref']:
        raise DiagnosticFailure('original_source_revision_changed')
    if frozen['selected_task_hashes'][TASK_INDEX] != TASK_HASH or frozen['selected_family_hashes'][TASK_INDEX] != FAMILY_HASH:
        raise DiagnosticFailure('original_frozen_selection_changed')
    if sha(BRIDGE.read_bytes()) != frozen['implementation_sha256']['native_batch_bridge.py']:
        raise DiagnosticFailure('original_bridge_changed')
    for name, expected in frozen['source_file_sha256'].items():
        if sha((args.source_root / bridge.SOURCE_FILES[name]).read_bytes()) != expected:
            raise DiagnosticFailure('original_public_source_changed')
    for name, expected in frozen['canonical_shared_asset_sha256'].items():
        if sha((args.source_root / 'data/base_dbs' / name).read_bytes()) != expected:
            raise DiagnosticFailure('canonical_shared_asset_mismatch_before_world')
    if (frozen['environment_random_seed'], frozen['max_execute_requests_per_actor'],
            frozen['code_timeout_seconds'], frozen['grade_timeout_seconds']) != (SEED, BUDGET, CODE_TIMEOUT, GRADE_TIMEOUT):
        raise DiagnosticFailure('original_native_parameters_changed')
    # Selection identities are read only from the explicitly authorized index.
    mapping = load_json(args.original_private_root / 'selection_mapping.json')['selection'][TASK_INDEX]
    if mapping['index'] != TASK_INDEX or sha(mapping['task_id'].encode()) != TASK_HASH:
        raise DiagnosticFailure('private_index_mapping_mismatch')
    if sha(mapping['family'].encode()) != FAMILY_HASH or mapping['family_sha256'] != FAMILY_HASH:
        raise DiagnosticFailure('private_family_mapping_mismatch')
    if mapping['task_sha256'] != TASK_HASH:
        raise DiagnosticFailure('private_task_hash_mismatch')
    return frozen, mapping


def selected_legal_events(original_private_root: Path) -> tuple[str, dict[int, dict[str, Any]]]:
    selected: dict[int, dict[str, Any]] = {}
    prompt = ''
    # Stop before completion metadata and grading events. Ignore nonselected
    # lines without decoding their JSON or accessing any of their fields.
    with (original_private_root / 'events_2.jsonl').open() as stream:
        for index, line in enumerate(stream):
            if index == 0:
                prompt = json.loads(line)['prompt']
            elif index in EVENTS:
                row = json.loads(line)
                selected[index] = {key: row[key] for key in ['code', 'receipt', 'metrics', 'sequence']}
            if index == EVENTS[-1]:
                break
    if sha(prompt.encode()) != PROMPT_SHA or set(selected) != set(EVENTS):
        raise DiagnosticFailure('legal_original_evidence_changed')
    for index, code_sha, receipt_sha in zip(EVENTS, ORIGINAL_CODE_SHA, ORIGINAL_RECEIPT_SHA):
        row = selected[index]
        if sha(row['code'].encode()) != code_sha or sha(row['receipt'].encode()) != receipt_sha:
            raise DiagnosticFailure('original_selected_event_hash_mismatch')
        if not row['metrics']['native_executed']:
            raise DiagnosticFailure('selected_event_not_native')
    return prompt, selected


def replace_quote_function(code: str) -> str:
    functions = [node for node in ast.parse(code).body
                 if isinstance(node, ast.FunctionDef) and node.name == 'csv_quote']
    if len(functions) != 1:
        raise DiagnosticFailure('original_quote_function_ambiguous')
    node = functions[0]
    lines = code.splitlines(keepends=True)
    # Original function occupies complete lines; preserve every other code byte.
    if node.col_offset != 0 or node.decorator_list:
        raise DiagnosticFailure('unsupported_original_quote_function')
    replacement = ''.join(lines[:node.lineno - 1]) + MINIMAL_QUOTE_FUNCTION + ''.join(lines[node.end_lineno:])
    old_tree, new_tree = ast.parse(code), ast.parse(replacement)
    new_tree.body = [n for n in new_tree.body if not (isinstance(n, ast.FunctionDef) and n.name == 'csv_quote')]
    old_tree.body = [n for n in old_tree.body if not (isinstance(n, ast.FunctionDef) and n.name == 'csv_quote')]
    if ast.dump(old_tree, include_attributes=False) != ast.dump(new_tree, include_attributes=False):
        raise DiagnosticFailure('non_quote_ast_change')
    return replacement


def private_instruction_contract(prompt: str, selected: dict[int, dict[str, Any]]) -> dict[str, Any]:
    actual_task = prompt.rsplit('Task: ', 1)[-1]
    match = re.search(r'headers,\s*"([^"]+)"\s+and\s*"([^"]+)"', actual_task)
    destinations = re.findall(r'"(~/[^"\n]+)"', actual_task)
    if not match or len(destinations) != 1:
        raise DiagnosticFailure('instruction_contract_unavailable')
    header = list(match.groups())
    paths = [kw.value.value for node in ast.walk(ast.parse(selected[72]['code']))
             if isinstance(node, ast.Call) for kw in node.keywords
             if kw.arg == 'file_path' and isinstance(kw.value, ast.Constant)]
    if len(paths) != 2 or any(path != destinations[0] for path in paths):
        raise DiagnosticFailure('original_destination_contract_mismatch')
    prefixes = [node.value.left.value for node in ast.walk(ast.parse(selected[69]['code']))
                if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'csv_content' for t in node.targets)
                and isinstance(node.value, ast.BinOp) and isinstance(node.value.left, ast.Constant)]
    if len(prefixes) != 1 or not prefixes[0].endswith('\n'):
        raise DiagnosticFailure('original_header_prefix_unavailable')
    if list(csv.reader([prefixes[0].removesuffix('\n')])) != [header]:
        raise DiagnosticFailure('original_header_contract_mismatch')
    return {'expected_header': header, 'header_prefix': prefixes[0]}


def prepare(args: argparse.Namespace) -> None:
    verify_transport_stress()
    bridge = load_bridge(args.original_freeze)
    original, mapping = verify_original(args, bridge)
    prompt, events = selected_legal_events(args.original_private_root)
    contract = private_instruction_contract(prompt, events)
    if args.private_root.exists() or args.freeze.exists():
        raise DiagnosticFailure('refuse_preparation_overwrite')
    if args.private_root.is_relative_to(REPO) or args.private_root.is_relative_to(args.source_root):
        raise DiagnosticFailure('private_payload_inside_repository')
    if args.private_root == args.original_private_root or args.private_root.is_relative_to(args.original_private_root):
        raise DiagnosticFailure('original_private_root_is_immutable')
    api_source_provenance = {}
    for relative in ('src/appworld/apps/spotify/apis.py', 'src/appworld/apps/file_system/apis.py'):
        present = subprocess.run(['git', 'cat-file', '-e', original['source_ref'] + ':' + relative],
                                 cwd=args.source_root, capture_output=True).returncode == 0
        if present:
            if (args.source_root / relative).read_bytes() != git('show', original['source_ref'] + ':' + relative, cwd=args.source_root):
                raise DiagnosticFailure('native_api_source_differs_from_pinned_git')
            api_source_provenance[relative] = 'author_git_blob_verified'
        else:
            # Installed app sources are not all tracked by the ACE checkout.
            # Pin their actual bytes, without claiming a Git provenance proof.
            if not (args.source_root / relative).is_file():
                raise DiagnosticFailure('installed_native_api_source_missing')
            api_source_provenance[relative] = 'installed_native_source_pinned_by_sha256; not tracked in ACE Git revision'
    parser = PARSER_TEMPLATE.replace('EXPECTED_HEADER_LITERAL', repr(contract['expected_header']))
    payloads: dict[str, dict[str, str]] = {}
    for arm in ['A', 'B']:
        codes = {str(index): events[index]['code'] for index in EVENTS}
        if arm == 'B':
            codes['69'] = replace_quote_function(codes['69'])
        codes['check'] = parser
        for code in codes.values():
            bridge.check_actor_ast(code)
        payloads[arm] = codes
    args.private_root.mkdir(parents=True, mode=0o700)
    os.chmod(args.private_root, 0o700)
    args.public_root.mkdir(parents=True, exist_ok=True)
    args.freeze.parent.mkdir(parents=True, exist_ok=True)
    transport = HostArtifacts()
    metadata = {'protocol': PROTOCOL, 'task_id': mapping['task_id'], **contract,
                'original_freeze_sha256': sha(args.original_freeze.read_bytes())}
    transport.json_new(args.private_root / 'metadata.json', metadata)
    payload_hashes: dict[str, dict[str, str]] = {}
    for arm, codes in payloads.items():
        directory = args.private_root / arm
        directory.mkdir(mode=0o700)
        payload_hashes[arm] = {}
        for index, code in codes.items():
            transport.new(directory / (index + '.py'), code.encode())
            payload_hashes[arm][index] = sha(code.encode())
    frozen = {
        'protocol': PROTOCOL, 'task_sha256': TASK_HASH, 'family_sha256': FAMILY_HASH,
        'tasks': 1, 'families': 1, 'arms': 2, 'fresh_worlds': 2,
        'actor_model_calls': 0, 'actor_ground_truth_loaded': False,
        'native_guard_enabled': True, 'environment_random_seed': SEED,
        'max_interactions': BUDGET, 'code_timeout_seconds': CODE_TIMEOUT,
        'actor_wall_clock_seconds': ACTOR_TIMEOUT, 'grade_timeout_seconds': GRADE_TIMEOUT,
        'grade_attempts_per_closed_arm': 1, 'grade_save_report': False,
        'original_freeze_sha256': sha(args.original_freeze.read_bytes()),
        'source_ref': original['source_ref'], 'source_file_sha256': original['source_file_sha256'],
        'bridge_sha256': sha(BRIDGE.read_bytes()), 'runner_sha256': sha(Path(__file__).read_bytes()),
        'protocol_sha256': sha(DOCUMENT.read_bytes()),
        'transport_module_sha256': sha(TRANSPORT_MODULE.read_bytes()),
        'transport_test_sha256': sha(TRANSPORT_TEST.read_bytes()),
        'transport_stress_sha256': sha(TRANSPORT_STRESS.read_bytes()),
        'external_commit_proof_required': True,
        'native_api_source_sha256': {relative: sha((args.source_root / relative).read_bytes()) for relative in
                                   ['src/appworld/apps/spotify/apis.py', 'src/appworld/apps/file_system/apis.py']},
        'native_api_source_provenance': api_source_provenance,
        'private_metadata_sha256': sha((args.private_root / 'metadata.json').read_bytes()),
        'payload_sha256': payload_hashes,
        'original_native_events': list(EVENTS), 'native_steps_per_arm': len(EVENTS) + 1,
        'quote_policy': {'A': 'original_quote_all', 'B': 'minimal'},
        'predelete_execution_order': ['A', 'B'],
        'cross_arm_barrier': 'both_predelete_pass_then_delete; both_closed_then_grade',
        'canonical_shared_asset_sha256': original['canonical_shared_asset_sha256'],
        'execution_cost_accounting': 'per-native-step elapsed, requester records and receipt bytes; parent wall time and grading attempts; actor model calls zero, root coding/model cost unexposed',
        'branch_registration': {'00': 'quote_alone_insufficient_no_new_core',
                                '01': 'quote_policy_acceptance_sensitivity',
                                '10': 'reverse_sensitivity_no_minimal_quote_fix',
                                '11': 'original_failure_not_reproduced_no_discrimination'},
        'retry': False, 'original_artifacts_modified': False,
    }
    transport.json_new(args.freeze, frozen, private=False)
    print(json.dumps({'status': 'prepared_no_world', 'tasks': 0, 'worlds': 0,
                      'payloads': 2, 'freeze_sha256': sha(args.freeze.read_bytes())}))


def verify_prepared(args: argparse.Namespace, committed: bool) -> dict[str, Any]:
    verify_transport_stress()
    bridge = load_bridge(args.original_freeze)
    verify_original(args, bridge)
    frozen = load_json(args.freeze)
    if frozen['protocol'] != PROTOCOL or sha(args.original_freeze.read_bytes()) != frozen['original_freeze_sha256']:
        raise DiagnosticFailure('frozen_original_reference_changed')
    for path, key in [(Path(__file__), 'runner_sha256'), (DOCUMENT, 'protocol_sha256'), (BRIDGE, 'bridge_sha256')]:
        if sha(path.read_bytes()) != frozen[key]:
            raise DiagnosticFailure('frozen_public_implementation_changed')
    for path, key in [(TRANSPORT_MODULE, 'transport_module_sha256'), (TRANSPORT_TEST, 'transport_test_sha256'),
                      (TRANSPORT_STRESS, 'transport_stress_sha256')]:
        if sha(path.read_bytes()) != frozen[key]:
            raise DiagnosticFailure('frozen_transport_evidence_changed')
    if sha((args.private_root / 'metadata.json').read_bytes()) != frozen['private_metadata_sha256']:
        raise DiagnosticFailure('frozen_private_metadata_changed')
    for relative, expected in frozen['native_api_source_sha256'].items():
        if sha((args.source_root / relative).read_bytes()) != expected:
            raise DiagnosticFailure('frozen_native_api_changed')
    for arm, hashes in frozen['payload_sha256'].items():
        for index, expected in hashes.items():
            code = (args.private_root / arm / (index + '.py')).read_bytes()
            if sha(code) != expected:
                raise DiagnosticFailure('frozen_private_payload_changed')
            bridge.check_actor_ast(code.decode())
    if committed:
        verify_commit_proof(args)
    return frozen


def summary_from_payload(payload: dict[str, Any], metadata: dict[str, Any], arm: str) -> dict[str, Any]:
    rows = payload['expected_rows']
    # Split only actual LF record/chunk boundaries, retaining LF inside quoted
    # fields. str.splitlines() also splits Unicode separators that CSV does not.
    pieces = payload['content'].split('\n')
    lines = [piece + '\n' for piece in pieces[:-1]]
    if pieces[-1]:
        lines.append(pieces[-1])
    parsed = list(csv.reader(lines, strict=True))
    if parsed != [metadata['expected_header'], *rows] or payload['parsed_rows'] != rows:
        raise DiagnosticFailure('independent_host_parse_mismatch')
    if payload['header'] != metadata['expected_header'] or payload['count'] != len(rows):
        raise DiagnosticFailure('native_header_count_mismatch')
    if len({tuple(row) for row in rows}) != len(rows):
        raise DiagnosticFailure('duplicate_output_pairs')
    if payload['source_ids'] != payload['record_ids'] or len(payload['source_ids']) != len(rows):
        raise DiagnosticFailure('native_union_record_mismatch')
    union = set().union(*(set(component) for component in payload['source_components']))
    if sorted(union) != payload['source_ids']:
        raise DiagnosticFailure('native_source_components_mismatch')

    def quote(value: str) -> str:
        if arm == 'A' or any(character in value for character in [',', '"', '\r', '\n']):
            return '"' + value.replace('"', '""') + '"'
        return value

    expected = metadata['header_prefix'] + ''.join(','.join(quote(value) for value in row) + '\n' for row in rows)
    if payload['content'] != expected:
        raise DiagnosticFailure('non_quote_output_byte_change')
    return {'status': 'predelete_pass', 'count': len(rows), 'distinct_pairs': len({tuple(row) for row in rows}),
            'source_counts': payload['source_counts'], 'header_sha256': value_sha(payload['header']),
            'source_union_sha256': value_sha(payload['source_ids']),
            'source_components_sha256': value_sha(payload['source_components']),
            'record_order_sha256': value_sha(payload['record_ids']),
            'row_order_sha256': value_sha(rows), 'row_set_sha256': value_sha(sorted(rows)),
            'readback_parsed_order_sha256': value_sha(payload['parsed_rows']),
            'readback_content_sha256': sha(payload['content'].encode()),
            'readback_content_bytes': len(payload['content'].encode())}


def worker(args: argparse.Namespace) -> None:
    frozen = verify_prepared(args, committed=True)
    transport = HostArtifacts()
    directory = args.private_root / args.worker_arm
    metadata = load_json(args.private_root / 'metadata.json', transport)
    bridge = load_bridge(args.original_freeze)
    experiment = PROTOCOL + '_' + sha(args.freeze.read_bytes())[:16] + '_' + args.worker_arm
    native_output = args.source_root / 'experiments/outputs' / experiment
    if native_output.exists():
        raise DiagnosticFailure('refuse_native_world_reuse')
    transport.new(directory / 'worker.started', b'first attempt\n')
    host_stream = transport.open_stream(directory / 'native_host.log', 'x')
    transport.chmod(str(directory / 'native_host.log'), 0o600)
    ledger_sequence = 0
    world = None
    status = 'worker_initialization_error'
    native_attempts = 0
    native_calls = 0
    closed = False
    # Captured before AppWorld can install any unsafe-execution patches.
    host_sleep = time.sleep
    clock = time.monotonic
    started = clock()

    def ledger(value: dict[str, Any]) -> None:
        nonlocal ledger_sequence
        ledger_sequence += 1
        transport.json_new(directory / f'ledger_{ledger_sequence:03}.json', value)

    def execute(index: str) -> str:
        nonlocal native_attempts, native_calls
        code = transport.read_bytes(directory / (index + '.py')).decode()
        if sha(code.encode()) != frozen['payload_sha256'][args.worker_arm][index]:
            raise DiagnosticFailure('native_payload_changed_before_execute')
        bridge.check_actor_ast(code)
        if clock() - started >= ACTOR_TIMEOUT:
            raise DiagnosticFailure('native_wall_budget_expired')
        before = len(world.requester.requests)
        # Durable attempt record precedes the only call. No retry on any error.
        ledger({'op': 'native_attempt', 'step': index, 'code_sha256': sha(code.encode()),
                'attempt': native_attempts + 1})
        native_attempts += 1
        receipt = None
        begin = clock()
        receipt_bytes = None
        result_logged = False
        try:
            with redirect_stdout(host_stream), redirect_stderr(host_stream):
                receipt = world.execute(code)
            if not isinstance(receipt, str):
                raise DiagnosticFailure('native_receipt_not_text')
            transport.new(directory / (index + '.receipt.txt'), receipt.encode())
            receipt_bytes = len(receipt.encode())
            ledger({'op': 'native_result', 'step': index, 'receipt_sha256': sha(receipt.encode()),
                    'receipt_bytes': receipt_bytes, 'native_api_calls': len(world.requester.requests) - before,
                    'elapsed_seconds': clock() - begin,
                    'execution_error': receipt.startswith('Execution failed')})
            result_logged = True
            if receipt.startswith('Execution failed'):
                raise DiagnosticFailure('native_execution_error')
            return receipt
        except BaseException as exc:
            if not result_logged:
                ledger({'op': 'native_result', 'step': index, 'error_class': type(exc).__name__,
                        'receipt_returned': receipt is not None, 'receipt_bytes': receipt_bytes,
                        'native_api_calls': len(world.requester.requests) - before,
                        'elapsed_seconds': clock() - begin})
            raise
        finally:
            native_calls += len(world.requester.requests) - before

    def wait_for(name: str, reject: str) -> None:
        while True:
            # FD access avoids Path I/O after native code has enabled a guard.
            try:
                command = load_json(directory / name, transport)
            except FileNotFoundError:
                try:
                    transport.read_bytes(directory / 'abort.json')
                except FileNotFoundError:
                    pass
                else:
                    raise DiagnosticFailure('parent_aborted')
                if clock() - started >= ACTOR_TIMEOUT:
                    raise DiagnosticFailure('barrier_wall_budget_expired')
                host_sleep(0.05)
                continue
            if command != {'freeze_sha256': sha(transport.read_bytes(args.freeze)), 'command': name.removesuffix('.json')}:
                raise DiagnosticFailure(reject)
            return

    try:
        with redirect_stdout(host_stream), redirect_stderr(host_stream):
            os.environ['APPWORLD_ROOT'] = str(args.source_root)
            os.environ['APPWORLD_PROJECT_PATH'] = str(args.source_root)
            sys.path.insert(0, str(args.source_root / 'src'))
            from appworld import AppWorld
            from appworld.common.path_store import path_store
            from freezegun.api import real_perf_counter
            path_store.update_root(str(args.source_root))
            clock = real_perf_counter
            started = clock()
            ledger({'op': 'world_init_attempt', 'task_sha256': TASK_HASH, 'load_ground_truth': False,
                    'seed': SEED, 'max_interactions': BUDGET, 'code_timeout_seconds': CODE_TIMEOUT})
            world = AppWorld(task_id=metadata['task_id'], experiment_name=experiment,
                             load_ground_truth=False, random_seed=SEED,
                             max_interactions=BUDGET, timeout_seconds=CODE_TIMEOUT,
                             raise_on_unsafe_syntax=True, null_patch_unsafe_execution=True)
        for index in EVENTS[:-2]:
            execute(str(index))
        receipt = execute('check')
        marker_lines = [line[len(MARKER):] for line in receipt.splitlines() if line.startswith(MARKER)]
        if len(marker_lines) != 1:
            raise DiagnosticFailure('independent_native_parser_payload_missing')
        payload = ast.literal_eval(marker_lines[0])
        summary = summary_from_payload(payload, metadata, args.worker_arm)
        transport.json_new(directory / 'predelete_payload.json', payload)
        summary.update({'native_attempts': native_attempts, 'native_api_calls': native_calls})
        transport.json_new(directory / 'predelete_ready.json', summary)
        status = 'predelete_ready'
        wait_for('authorize_delete.json', 'invalid_delete_authorization')
        execute('75')
        execute('78')
        status = 'postdelete_complete'
        # Close before grade; retain only the producer-native snapshot, not a
        # private-state inspection. This follows the original host cleanup.
        ledger({'op': 'world_close_attempt', 'native_attempts': native_attempts})
        with redirect_stdout(host_stream), redirect_stderr(host_stream):
            world._save_state(world.output_db_home_path_on_disk)
            world.save_logs()
            world.close()
        closed = True
        transport.json_new(directory / 'closed.json', {'status': 'closed', 'native_attempts': native_attempts,
                                                     'native_api_calls': native_calls})
        status = 'closed_waiting_grade'
        wait_for('authorize_grade.json', 'invalid_grade_authorization')
        ledger({'op': 'grade_attempt', 'attempt': 1, 'after_close': True})
        with bridge.grade_deadline(), redirect_stdout(host_stream), redirect_stderr(host_stream):
            from appworld.evaluator import evaluate_task
            tracker, unused = evaluate_task(task_id=metadata['task_id'], experiment_name=experiment,
                                            suppress_errors=True, save_report=False)
        # No evaluator report, labels, expected answers, or test text is read.
        success = tracker.success
        if not isinstance(success, bool):
            raise DiagnosticFailure('producer_success_bit_not_boolean')
        transport.json_new(directory / 'grade.json', {'status': 'evaluated', 'attempts': 1,
                                                   'success_count': int(success)})
        status = 'graded_once'
    except BaseException as exc:
        ledger({'op': 'worker_error', 'status': status, 'error_class': type(exc).__name__})
        if not closed and world is not None:
            try:
                with redirect_stdout(host_stream), redirect_stderr(host_stream):
                    world.close()
                closed = True
            except BaseException as cleanup:
                ledger({'op': 'cleanup_error', 'error_class': type(cleanup).__name__})
        transport.json_new(directory / 'blocked.json', {'status': 'blocked', 'phase': status,
                                                     'error_class': type(exc).__name__,
                                                     'closed': closed, 'retry': False})
    finally:
        host_stream.flush()
        host_stream.close()


def wait_artifact(process: subprocess.Popen[Any], directory: Path, name: str, deadline: float) -> dict[str, Any]:
    path = directory / name
    while time.monotonic() < deadline:
        if (directory / 'blocked.json').exists():
            raise DiagnosticFailure('worker_blocked')
        if path.exists():
            return load_json(path)
        if process.poll() is not None:
            raise DiagnosticFailure('worker_terminated_without_checkpoint')
        time.sleep(0.05)
    raise DiagnosticFailure('parent_barrier_timeout')


def cross_arm_check(a: dict[str, Any], b: dict[str, Any]) -> None:
    keys = ['count', 'distinct_pairs', 'source_counts', 'header_sha256', 'source_union_sha256',
            'source_components_sha256', 'record_order_sha256', 'row_order_sha256', 'row_set_sha256',
            'readback_parsed_order_sha256', 'native_attempts', 'native_api_calls']
    if a['status'] != 'predelete_pass' or b['status'] != 'predelete_pass' or any(a[key] != b[key] for key in keys):
        raise DiagnosticFailure('paired_predelete_invariant_failed')


def run(args: argparse.Namespace) -> None:
    transport = HostArtifacts()
    freeze_hash = sha(args.freeze.read_bytes())
    processes: dict[str, subprocess.Popen[Any]] = {}
    public: dict[str, Any] = {'protocol': PROTOCOL, 'task_sha256': TASK_HASH, 'family_sha256': FAMILY_HASH,
                             'freeze_sha256': freeze_hash, 'freeze_commit': args.freeze_commit,
                             'actor_ground_truth_loaded': False, 'actor_model_calls': 0,
                             'diagnostic_terminal_record': True, 'arms': 2,
                             'paired_invariants_passed': False,
                             'retry': False, 'status': 'control_invalid', 'grade_attempts': 0,
                             'arm_status': {arm: {'status': 'not_started', 'native_attempts': 0,
                                                 'delete_attempts': 0, 'grade_attempts': 0,
                                                 'grade_status': 'not_attempted'} for arm in ['A', 'B']}}
    begun = time.monotonic()
    try:
        frozen = verify_prepared(args, committed=True)
        public['commit_proof_sha256'] = sha(args.commit_proof.read_bytes())
        transport.json_new(args.private_root / 'run.started.json', {'freeze_sha256': freeze_hash,
                                                                 'freeze_commit': args.freeze_commit})
        prepared = {}
        for arm in ['A', 'B']:
            argv = [sys.executable, str(Path(__file__).resolve()), '--worker-arm', arm,
                    '--source-root', str(args.source_root), '--original-private-root', str(args.original_private_root),
                    '--private-root', str(args.private_root), '--public-root', str(args.public_root),
                    '--original-freeze', str(args.original_freeze), '--freeze', str(args.freeze),
                    '--freeze-commit', args.freeze_commit, '--commit-proof', str(args.commit_proof)]
            stream = transport.open_stream(args.private_root / arm / 'worker_process.log', 'x')
            transport.chmod(str(args.private_root / arm / 'worker_process.log'), 0o600)
            try:
                processes[arm] = subprocess.Popen(argv, stdout=stream, stderr=stream)
            finally:
                stream.close()
            prepared[arm] = wait_artifact(processes[arm], args.private_root / arm,
                                          'predelete_ready.json', begun + ACTOR_TIMEOUT)
        cross_arm_check(prepared['A'], prepared['B'])
        public['predelete'] = prepared
        public['paired_predelete_invariants'] = 'passed'
        public['paired_invariants_passed'] = True
        for arm in ['A', 'B']:
            transport.json_new(args.private_root / arm / 'authorize_delete.json',
                               {'freeze_sha256': freeze_hash, 'command': 'authorize_delete'})
        closed = {}
        for arm in ['A', 'B']:
            closed[arm] = wait_artifact(processes[arm], args.private_root / arm,
                                       'closed.json', begun + ACTOR_TIMEOUT)
        public['closed'] = closed
        if any(closed['A'][key] != closed['B'][key] for key in ['native_attempts', 'native_api_calls']):
            public['paired_invariants_passed'] = False
            raise DiagnosticFailure('paired_postdelete_counts_mismatch')
        for arm in ['A', 'B']:
            transport.json_new(args.private_root / arm / 'authorize_grade.json',
                               {'freeze_sha256': freeze_hash, 'command': 'authorize_grade'})
        grades = {}
        for arm in ['A', 'B']:
            grades[arm] = wait_artifact(processes[arm], args.private_root / arm, 'grade.json',
                                       time.monotonic() + GRADE_TIMEOUT + 15)
            if grades[arm]['attempts'] != 1 or grades[arm]['status'] != 'evaluated':
                raise DiagnosticFailure('producer_grade_not_completed_once')
        branch = str(grades['A']['success_count']) + str(grades['B']['success_count'])
        public.update({'status': 'paired_complete', 'grade_attempts': 2,
                       'producer_success_counts': {arm: grades[arm]['success_count'] for arm in ['A', 'B']},
                       'branch': frozen['branch_registration'][branch],
                       'qualifying_ocar_residual': False})
    except DiagnosticFailure as exc:
        public['blocked_reason'] = str(exc)
        public['qualifying_ocar_residual'] = False
    finally:
        for arm, process in processes.items():
            directory = args.private_root / arm
            if process.poll() is None:
                try:
                    transport.json_new(directory / 'abort.json', {'command': 'abort'})
                except FileExistsError:
                    pass
        for process in processes.values():
            try:
                process.wait(timeout=CODE_TIMEOUT + 5)
            except subprocess.TimeoutExpired:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)
        # Publish attempted grading counts even for interrupted/inconclusive
        # pairs; never infer an unreturned score or schedule a replacement.
        attempts = 0
        for arm in ['A', 'B']:
            directory = args.private_root / arm
            entries = [load_json(path) for path in directory.glob('ledger_*.json')]
            arm_attempts = sum(entry.get('op') == 'grade_attempt' for entry in entries)
            attempts += arm_attempts
            arm_state = public['arm_status'][arm]
            arm_state.update({'native_attempts': sum(entry.get('op') == 'native_attempt' for entry in entries),
                              'delete_attempts': sum(entry.get('op') == 'native_attempt' and entry.get('step') == '75' for entry in entries),
                              'grade_attempts': arm_attempts,
                              'grade_status': 'attempted_without_return' if arm_attempts else 'not_attempted'})
            for checkpoint, status in [('worker.started', 'started'), ('predelete_ready.json', 'predelete_ready'),
                                       ('closed.json', 'closed'), ('blocked.json', 'blocked'), ('grade.json', 'graded_once')]:
                if (directory / checkpoint).exists():
                    arm_state['status'] = status
            if (directory / 'grade.json').exists():
                arm_state['grade_status'] = 'evaluated_once'
                arm_state['producer_success_count'] = load_json(directory / 'grade.json')['success_count']
        public['grade_attempts'] = attempts
        public['execution_parent_wall_seconds'] = time.monotonic() - begun
        public['model_cost_scope'] = 'fixed diagnostic actor calls zero; root authoring/review model use is nonzero and unexposed'
        for arm in ['A', 'B']:
            entries = [load_json(path) for path in (args.private_root / arm).glob('ledger_*.json')]
            completed = [e for e in entries if e.get('op') == 'native_result']
            public['arm_status'][arm]['native_api_calls_known_subtotal'] = sum(e.get('native_api_calls', 0) for e in completed)
            public['arm_status'][arm]['generated_receipt_bytes_known_subtotal'] = sum(e.get('receipt_bytes') or 0 for e in completed)
            public['arm_status'][arm]['native_elapsed_seconds_known_subtotal'] = sum(e.get('elapsed_seconds', 0) for e in completed)
            public['arm_status'][arm]['native_cost_records_complete'] = (len(completed) == public['arm_status'][arm]['native_attempts'] and all(e.get('receipt_bytes') is not None for e in completed))
        if public['status'] != 'paired_complete':
            public['branch'] = 'control_invalid_no_quote_conclusion'
        transport.json_new(args.public_root / 'RESULT_2026-10-04.json', public, private=False)
    print(json.dumps({'status': public['status'], 'grade_attempts': public['grade_attempts'],
                      'qualifying_ocar_residual': False}))


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--prepare', action='store_true')
    mode.add_argument('--run', action='store_true')
    mode.add_argument('--worker-arm', choices=['A', 'B'], help=argparse.SUPPRESS)
    for flag in ['source-root', 'original-private-root', 'private-root', 'public-root']:
        parser.add_argument('--' + flag, type=Path, required=True)
    parser.add_argument('--freeze', type=Path)
    parser.add_argument('--original-freeze', type=Path,
                        default=REPO / 'experiments/oacr_residual_discovery/recovery/freeze.json')
    parser.add_argument('--freeze-commit')
    parser.add_argument('--commit-proof', type=Path)
    args = parser.parse_args()
    for key in ['source_root', 'original_private_root', 'private_root', 'public_root', 'original_freeze']:
        setattr(args, key, getattr(args, key).resolve())
    args.freeze = (args.freeze or args.public_root / 'freeze.json').resolve()
    if args.commit_proof:
        args.commit_proof = args.commit_proof.resolve()
    return args


def main() -> int:
    try:
        if sys.flags.optimize:
            raise DiagnosticFailure('optimized_python_disables_required_assertions')
        args = arguments()
        if args.prepare:
            prepare(args)
        elif args.worker_arm:
            worker(args)
        else:
            run(args)
        return 0
    except DiagnosticFailure as exc:
        print(json.dumps({'status': 'blocked_before_run', 'reason': str(exc), 'retry': False}))
        return 2
    except BaseException as exc:
        # Never print exception messages or tracebacks: they can contain literals.
        print(json.dumps({'status': 'blocked', 'error_class': type(exc).__name__, 'retry': False}))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
