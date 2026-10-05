"""Work launch contract and watchdog tests, without native/model imports."""
import copy
import hashlib
import json
from pathlib import Path
import signal
import tempfile
import unittest

from model_budget import BudgetBlocked, require_launch_registration
from native_batch_bridge import Watchdog

HERE = Path(__file__).parent


class WorkSerialTests(unittest.TestCase):
    def test_work_contract_keeps_usage_unknown_and_limits_two_admissions(self):
        profile = require_launch_registration(HERE/'MODEL_BUDGET_REGISTRATION.json')
        self.assertEqual((profile['max_live_actors'],profile['session_actor_admissions']),(1,2))
        self.assertEqual((profile['actor_wall_seconds'],profile['mailbox_requests']),(300,120))
        self.assertIsNone(profile['model_tokens'])
        self.assertIsNone(profile['model_cost'])

    def test_invented_usage_or_parallelism_or_restart_rejected(self):
        original = json.loads((HERE/'MODEL_BUDGET_REGISTRATION.json').read_text())
        for key,value in [('model_tokens',0),('max_live_actors',2),('fork_turns','all'),
                          ('automatic_restart',True),('mailbox_requests',121),('actor_wall_seconds',1201)]:
            with self.subTest(key=key), tempfile.TemporaryDirectory() as directory:
                changed = copy.deepcopy(original);changed[key]=value
                path=Path(directory)/'registration.json';path.write_text(json.dumps(changed))
                with self.assertRaises(BudgetBlocked):
                    require_launch_registration(path)

    def test_effective_watchdog_uses_300_seconds_not_legacy_1200(self):
        previous=signal.getsignal(signal.SIGUSR1)
        watchdog=Watchdog(lambda:10.0,300)
        try:
            watchdog.start(10.0)
            self.assertEqual(watchdog.deadline,310.0)
        finally:
            watchdog.stop();signal.signal(signal.SIGUSR1,previous)


if __name__=='__main__':
    result=unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromTestCase(WorkSerialTests))
    print(json.dumps({'date':'2026-10-05','scope':'work_serial_launch_controller_only',
        'tests_run':result.testsRun,'passed':result.wasSuccessful(),'failures':len(result.failures),
        'errors':len(result.errors),'native_model_evaluator_calls':0,
        'native_bridge_sha256':hashlib.sha256((HERE/'native_batch_bridge.py').read_bytes()).hexdigest(),
        'selection_sha256':hashlib.sha256((HERE/'selection_prepare.py').read_bytes()).hexdigest(),
        'model_budget_sha256':hashlib.sha256((HERE/'model_budget.py').read_bytes()).hexdigest(),
        'test_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}))
    raise SystemExit(not result.wasSuccessful())
