"""Controller-only admission ledger for a future metered model adapter.

No provider or native imports. Hard token bounds are conditional on the trusted
adapter supplying a verified input bound, enforcing max_output_tokens including
reasoning, making one request without SDK retries, and returning actual usage.
Never import this into actor/native code. No dollar estimates are fabricated.
"""
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile


class BudgetBlocked(RuntimeError):
    pass


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def number(value, positive=False):
    if type(value) is not int or value < int(positive):
        raise BudgetBlocked('non_integer_or_invalid_budget')
    return value


def validate(config):
    if not isinstance(config, dict) or config.get('schema') != 'oacr_model_budget_v1':
        raise BudgetBlocked('model_budget_registration_missing')
    identity = config.get('identity', {})
    if not isinstance(identity.get('model_snapshot'), str) or not identity['model_snapshot'].strip():
        raise BudgetBlocked('model_identity_missing')
    if not isinstance(identity.get('inference_settings'), dict):
        raise BudgetBlocked('model_settings_missing')
    limits = config.get('limits', {})
    for key in ['task_calls', 'task_tokens', 'batch_calls', 'batch_tokens', 'output_tokens_per_call']:
        number(limits.get(key), positive=True)
    if type(config.get('max_concurrent_model_calls')) is not int or config.get('max_concurrent_model_calls') != 1 or config.get('automatic_retry') is not False:
        raise BudgetBlocked('serial_no_retry_contract_required')
    return config


def require_launch_registration(path):
    """B stays locked until a real adapter is connected and separately audited.

    This check is not provider attestation. Trusted registration must identify
    the actual calling code and usage probe before marking it ready.
    """
    try:
        config = json.loads(Path(path).read_text())
    except FileNotFoundError:
        raise BudgetBlocked('B_unmetered_actor_not_launchable') from None
    validate(config)
    evidence = config.get('adapter_evidence', {})
    for key in ['source_sha256', 'usage_probe_sha256', 'input_bound_audit_sha256', 'output_cap_audit_sha256']:
        if not re.fullmatch('[0-9a-f]{64}', str(evidence.get(key, ''))):
            raise BudgetBlocked('metered_adapter_evidence_missing')
    if config.get('status') != 'ready' or evidence.get('integrated_call_path_verified') is not True:
        raise BudgetBlocked('metered_adapter_not_connected')
    return config


class ModelBudget:
    def __init__(self, directory, config):
        self.config = json.loads(json.dumps(validate(config)))
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.path = self.directory / 'model_budget_ledger.json'
        self.lock_path = self.directory / 'model_budget.lock'

    def _load(self):
        if not self.path.exists():
            return {'schema': 'oacr_model_budget_ledger_v1', 'config_sha256': digest(self.config),
                    'blocked': False, 'calls': []}
        try:
            state = json.loads(self.path.read_text())
            if state['schema'] != 'oacr_model_budget_ledger_v1' or state['config_sha256'] != digest(self.config):
                raise BudgetBlocked('ledger_configuration_changed')
            calls = state['calls']
            if len({c['call_id'] for c in calls}) != len(calls):
                raise BudgetBlocked('duplicate_ledger_identity')
            for call in calls:
                number(call['task_index'])
                if call['task_index'] >= 24:
                    raise BudgetBlocked('invalid_task_index')
                number(call['reserved_tokens'], positive=True)
                if call['phase'] == 'completed':
                    number(call['actual_tokens'])
                    if call['actual_tokens'] > call['reserved_tokens']:
                        raise BudgetBlocked('completed_ledger_bound_violated')
                elif call['phase'] not in ['claimed', 'unknown_or_invalid']:
                    raise BudgetBlocked('invalid_ledger_phase')
            return state
        except (KeyError, TypeError, ValueError):
            raise BudgetBlocked('unreadable_model_ledger') from None

    def _save(self, state):
        fd, temporary = tempfile.mkstemp(dir=self.directory)
        try:
            with os.fdopen(fd, 'w') as stream:
                json.dump(state, stream, sort_keys=True)
                stream.write('\n')
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, self.path)
            directory_fd = os.open(self.directory, os.O_RDONLY | os.O_DIRECTORY)
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)

    def call(self, *, task_index, call_id, input_bound, max_output_tokens, callback):
        """Invoke callback(cap) at most once for this ID; record only metadata.

        Missing/invalid usage, response loss and uncertain crash claims block
        the entire ledger. Timeout must be enforced by the external adapter;
        this module cannot cancel remote inference or cap other model clients.
        """
        number(task_index)
        if task_index >= 24 or not isinstance(call_id, str) or not re.fullmatch('[0-9a-f]{32}', call_id):
            raise BudgetBlocked('invalid_model_call_identity')
        number(input_bound)
        number(max_output_tokens, positive=True)
        limits = self.config['limits']
        if max_output_tokens > limits['output_tokens_per_call']:
            raise BudgetBlocked('per_call_output_budget_exceeded')
        reserved = input_bound + max_output_tokens
        with self.lock_path.open('a+b') as lock:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
            state = self._load()
            if state['blocked'] or any(c['phase'] != 'completed' for c in state['calls']):
                raise BudgetBlocked('unknown_model_consumption_fail_closed')
            if any(c['call_id'] == call_id for c in state['calls']):
                raise BudgetBlocked('model_call_replay_forbidden')
            task_calls = [c for c in state['calls'] if c['task_index'] == task_index]
            for calls, call_cap, token_cap in [(state['calls'], limits['batch_calls'], limits['batch_tokens']),
                                               (task_calls, limits['task_calls'], limits['task_tokens'])]:
                used = sum(c['actual_tokens'] for c in calls)
                if len(calls) >= call_cap or used + reserved > token_cap:
                    raise BudgetBlocked('model_call_or_token_budget_exhausted')
            record = {'call_id': call_id, 'task_index': task_index, 'phase': 'claimed',
                      'input_bound': input_bound, 'max_output_tokens': max_output_tokens,
                      'reserved_tokens': reserved}
            state['calls'].append(record)
            self._save(state)  # Committed before any callback can run.
            try:
                response = callback(max_output_tokens)
                if response.get('model') != self.config['identity']['model_snapshot']:
                    raise BudgetBlocked('returned_model_identity_mismatch')
                usage = response['usage']
                used_input = number(usage['input_tokens'])
                used_output = number(usage['output_tokens'])
                total = number(usage['total_tokens'])
                if total != used_input + used_output or used_input > input_bound or used_output > max_output_tokens:
                    raise BudgetBlocked('reported_usage_or_bound_invalid')
                cached = usage.get('input_tokens_details', {}).get('cached_tokens')
                reasoning = usage.get('output_tokens_details', {}).get('reasoning_tokens')
                for detail, upper in [(cached, used_input), (reasoning, used_output)]:
                    if detail is not None and number(detail) > upper:
                        raise BudgetBlocked('usage_detail_exceeds_parent')
                record.update(phase='completed', actual_tokens=total, input_tokens=used_input,
                              output_tokens=used_output, cached_tokens=cached, reasoning_tokens=reasoning,
                              provider_reported_cost=None, billing_status='unavailable')
                self._save(state)
                return response
            except BaseException:
                record['phase'] = 'unknown_or_invalid'
                state['blocked'] = True
                self._save(state)
                raise
