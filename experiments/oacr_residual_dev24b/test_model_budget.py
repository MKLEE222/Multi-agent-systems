"""Budget/controller-only tests: no provider, native task or model calls."""
from concurrent.futures import ThreadPoolExecutor
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import unittest

from model_budget import ModelBudget, BudgetBlocked, require_launch_registration
import selection_prepare


def config():
    return {'schema':'oacr_model_budget_v1', 'identity':{'model_snapshot':'stub-fixed-snapshot',
            'inference_settings':{'reasoning_effort':'stub'}},
            'limits':{'task_calls':5,'task_tokens':100,'batch_calls':10,'batch_tokens':300,
                      'output_tokens_per_call':10}, 'max_concurrent_model_calls':1,'automatic_retry':False}


def result(input_tokens=4, output_tokens=3, **extra):
    usage = dict(input_tokens=input_tokens, output_tokens=output_tokens,
                 total_tokens=input_tokens+output_tokens)
    usage.update(extra)
    return dict(model='stub-fixed-snapshot', usage=usage)


class Tests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.path = Path(self.temporary.name)
        self.configuration = config()
        self.callbacks = 0

    def invoke(self, ledger, identity=1, task=0, input_bound=4, output_cap=5, response=None):
        def callback(cap):
            self.callbacks += 1
            self.assertEqual(cap, output_cap)
            return result() if response is None else response
        return ledger.call(task_index=task, call_id=f'{identity:032x}', input_bound=input_bound,
                           max_output_tokens=output_cap, callback=callback)

    def test_returned_usage_charged_and_unused_reservation_released(self):
        self.configuration['limits']['task_tokens'] = 16
        ledger = ModelBudget(self.path, self.configuration)
        self.invoke(ledger, identity=1)
        self.invoke(ledger, identity=2)
        with self.assertRaises(BudgetBlocked):
            self.invoke(ledger, identity=3)
        self.assertEqual(self.callbacks, 2)

    def test_maximum_call_reservation_rejected_before_callback(self):
        self.configuration['limits']['batch_tokens'] = 8
        with self.assertRaises(BudgetBlocked):
            self.invoke(ModelBudget(self.path, self.configuration))
        self.assertEqual(self.callbacks, 0)

    def test_task_call_limit_and_other_task_can_continue(self):
        self.configuration['limits']['task_calls'] = 1
        ledger = ModelBudget(self.path, self.configuration)
        self.invoke(ledger)
        with self.assertRaises(BudgetBlocked):
            self.invoke(ledger, identity=2)
        self.invoke(ledger, identity=3, task=1)
        self.assertEqual(self.callbacks, 2)

    def test_batch_call_limit(self):
        self.configuration['limits']['batch_calls'] = 1
        ledger = ModelBudget(self.path, self.configuration)
        self.invoke(ledger)
        with self.assertRaises(BudgetBlocked):
            self.invoke(ledger, identity=2, task=1)
        self.assertEqual(self.callbacks, 1)

    def test_cached_and_reasoning_are_subcounts_not_extra_tokens(self):
        ledger = ModelBudget(self.path, self.configuration)
        self.invoke(ledger, response=result(input_tokens_details={'cached_tokens':2},
                                           output_tokens_details={'reasoning_tokens':2}))
        record = json.loads(ledger.path.read_text())['calls'][0]
        self.assertEqual((record['actual_tokens'],record['cached_tokens'],record['reasoning_tokens']), (7,2,2))

    def test_full_repeated_input_is_charged_again(self):
        ledger = ModelBudget(self.path, self.configuration)
        self.invoke(ledger, identity=1, input_bound=20, response=result(20,3))
        self.invoke(ledger, identity=2, input_bound=20, response=result(20,3))
        self.assertEqual(sum(c['actual_tokens'] for c in json.loads(ledger.path.read_text())['calls']), 46)

    def test_missing_detail_counts_and_dollar_cost_stay_unknown(self):
        ledger = ModelBudget(self.path, self.configuration)
        self.invoke(ledger)
        record = json.loads(ledger.path.read_text())['calls'][0]
        self.assertIsNone(record['cached_tokens'])
        self.assertIsNone(record['reasoning_tokens'])
        self.assertIsNone(record['provider_reported_cost'])

    def test_missing_usage_blocks_restart_without_retry(self):
        ledger = ModelBudget(self.path, self.configuration)
        with self.assertRaises(KeyError):
            self.invoke(ledger, response={'model':'stub-fixed-snapshot'})
        with self.assertRaises(BudgetBlocked):
            self.invoke(ModelBudget(self.path, self.configuration), identity=2)
        self.assertEqual(self.callbacks, 1)

    def test_timeout_blocks_future_calls(self):
        ledger = ModelBudget(self.path, self.configuration)
        def timeout(cap):
            self.callbacks += 1
            raise TimeoutError()
        with self.assertRaises(TimeoutError):
            ledger.call(task_index=0,call_id='a'*32,input_bound=4,max_output_tokens=5,callback=timeout)
        with self.assertRaises(BudgetBlocked):
            self.invoke(ledger)
        self.assertEqual(self.callbacks, 1)

    def test_duplicate_identity_never_invokes_twice(self):
        ledger = ModelBudget(self.path, self.configuration)
        self.invoke(ledger)
        with self.assertRaises(BudgetBlocked):
            self.invoke(ledger)
        self.assertEqual(self.callbacks, 1)

    def test_killed_process_claim_blocks_without_callback_retry(self):
        cfg = json.dumps(self.configuration)
        script = ('import os,json;from model_budget import ModelBudget;'
                  'ledger=ModelBudget('+repr(str(self.path))+',json.loads('+repr(cfg)+'));'
                  'ledger.call(task_index=0,call_id="a"*32,input_bound=4,max_output_tokens=5,callback=lambda cap:os._exit(7))')
        process = subprocess.run([sys.executable,'-c',script],cwd=Path(__file__).parent,timeout=10)
        self.assertEqual(process.returncode, 7)
        with self.assertRaises(BudgetBlocked):
            self.invoke(ModelBudget(self.path,self.configuration))
        self.assertEqual(self.callbacks, 0)

    def test_changing_configuration_cannot_reset_ledger_budget(self):
        self.invoke(ModelBudget(self.path,self.configuration))
        changed = copy.deepcopy(self.configuration)
        changed['limits']['batch_tokens'] += 1
        with self.assertRaises(BudgetBlocked):
            self.invoke(ModelBudget(self.path,changed),identity=2)
        self.assertEqual(self.callbacks, 1)

    def test_concurrent_callbacks_remain_serial_and_bounded(self):
        self.configuration['limits']['batch_calls'] = 3
        active = maximum = completed = 0
        mutex = threading.Lock()
        def run(identity):
            ledger = ModelBudget(self.path,self.configuration)
            def callback(cap):
                nonlocal active, maximum, completed
                with mutex:
                    active += 1
                    maximum = max(maximum,active)
                time.sleep(0.01)
                with mutex:
                    active -= 1
                    completed += 1
                return result()
            try:
                ledger.call(task_index=identity,call_id=f'{identity:032x}',input_bound=4,max_output_tokens=5,callback=callback)
            except BudgetBlocked:
                pass
        with ThreadPoolExecutor(max_workers=8) as executor:
            list(executor.map(run,range(8)))
        self.assertEqual((maximum,completed),(1,3))

    def test_wrong_model_or_excess_usage_stops_after_one_callback(self):
        responses = [dict(model='wrong-snapshot',usage=result()['usage']), result(5,3), result(4,6),
                     dict(model='stub-fixed-snapshot',usage=dict(input_tokens=4,output_tokens=3,total_tokens=8)),
                     result(input_tokens_details={'cached_tokens':5}), result(output_tokens_details={'reasoning_tokens':4})]
        for index,response in enumerate(responses):
            with self.subTest(index=index):
                ledger = ModelBudget(self.path/str(index),self.configuration)
                with self.assertRaises(BudgetBlocked):
                    self.invoke(ledger,response=response)
                with self.assertRaises(BudgetBlocked):
                    self.invoke(ledger,identity=2)
        self.assertEqual(self.callbacks,len(responses))

    def test_invalid_limits_and_identity_rejected(self):
        for invalid in [True,0,-1,None,1.5]:
            broken = copy.deepcopy(self.configuration)
            broken['limits']['task_calls'] = invalid
            with self.assertRaises(BudgetBlocked):
                ModelBudget(self.path,broken)
        broken = copy.deepcopy(self.configuration)
        broken['identity']['model_snapshot'] = ''
        with self.assertRaises(BudgetBlocked):
            ModelBudget(self.path,broken)
        self.assertEqual(self.callbacks,0)

    def test_prepare_and_serve_verification_block_before_task_metadata(self):
        class NeverRead:
            def manifest(self,*args):
                raise AssertionError('manifest accessed before model launch gate')
        registration = selection_prepare.MODEL_REGISTRATION
        selection_prepare.MODEL_REGISTRATION = self.path/'missing_registration.json'
        self.addCleanup(setattr,selection_prepare,'MODEL_REGISTRATION',registration)
        with self.assertRaises(BudgetBlocked):
            selection_prepare.prepare(NeverRead(),self.path,self.path/'freeze.json',self.path/'private',None)
        with self.assertRaises(BudgetBlocked):
            selection_prepare.verify(NeverRead(),self.path,self.path/'freeze.json',self.path/'private')
        self.assertFalse((self.path/'freeze.json').exists())
        self.assertFalse((self.path/'private').exists())

    def test_valid_numbers_alone_do_not_allow_launch(self):
        path = self.path/'registration.json'
        path.write_text(json.dumps(self.configuration))
        with self.assertRaises(BudgetBlocked):
            require_launch_registration(path)


if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(Tests)
    outcome = unittest.TextTestRunner(verbosity=1).run(suite)
    report = {'date':'2026-10-05','scope':'model_budget_controller_stub_only','tests_run':outcome.testsRun,
              'failures':len(outcome.failures),'errors':len(outcome.errors),'passed':outcome.wasSuccessful(),
              'real_provider_model_calls':0,'native_world_task_api_evaluator_calls':0,
              'actual_model_usage_connected':False,'B_frozen':False,'B_started':False,
              'source_sha256':hashlib.sha256((Path(__file__).parent/'model_budget.py').read_bytes()).hexdigest(),
              'test_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'selection_source_sha256':hashlib.sha256((Path(__file__).parent/'selection_prepare.py').read_bytes()).hexdigest()}
    print(json.dumps(report))
    sys.exit(not outcome.wasSuccessful())
