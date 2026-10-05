"""Synthetic transport stress only: no task/runtime/API/model/evaluator imports."""
from __future__ import annotations

import argparse
import builtins
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import io
import os
from pathlib import Path
import tempfile
import threading
import subprocess
import sys
import unittest
from unittest.mock import patch

import transport_once as transport


_COUNTS: dict[str, dict[str, int]] = {}


class TransportOnlyTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="transport_only_")
        self.mailbox = Path(self.temporary.name) / "mailbox"
        self.controller = transport.TransportOnce(self.mailbox)
        self.calls = Counter()
        self.accepted = set()
        self.rejected = set()
        self.abandoned = set()
        self.identifier = 0

    def tearDown(self):
        for request_id in self.accepted:
            self.assertEqual(self.calls[request_id], 1)
        for request_id in self.rejected:
            self.assertEqual(self.calls[request_id], 0)
        for request_id in self.abandoned:
            self.assertEqual(self.calls[request_id], 0)
        _COUNTS[self._testMethodName] = {
            "accepted_uuids": len(self.accepted), "callback_calls": sum(self.calls.values()),
            "new_claims": len(self.accepted) + len(self.abandoned),
            "rejected_before_callback": len(self.rejected),
            "abandoned_new_claims_before_callback": len(self.abandoned),
            "accepted_each_exactly_one_callback": all(self.calls[u] == 1 for u in self.accepted),
            "rejected_each_zero_callbacks": all(self.calls[u] == 0 for u in self.rejected),
        }
        self.temporary.cleanup()

    def request(self, request_id=None, payload=None):
        if request_id is None:
            self.identifier += 1
            request_id = f"{self.identifier:032x}"
        path = self.mailbox / (request_id + ".request.json")
        path.write_text(json.dumps(payload or {"op": "stub", "value": 7}))
        return path

    def claim_new(self, path):
        claim = self.controller.claim(path)
        self.assertEqual(claim.disposition, "new")
        self.accepted.add(claim.request_id)
        self.assertFalse(path.exists())
        self.assertTrue(Path(claim.claimed_path).exists())
        claimed = self.controller._paths(claim.request_id)["claimed"]
        self.assertTrue(Path(claimed).exists())
        return claim

    def stub(self, claim, hook=None):
        def callback(payload):
            self.calls[claim.request_id] += 1
            if hook:
                hook()
            return {"status": "synthetic_receipt", "value": payload["value"]}
        return callback

    def duplicate(self, claim, payload=None, controller=None):
        path = self.request(claim.request_id, payload)
        return (controller or self.controller).claim(path)

    def assert_known_publication(self, error, claim, status="published"):
        self.assertEqual(error.publication_state, "known")
        self.assertIsNotNone(error.publication)
        publication = error.publication
        self.assertEqual(publication.status, status)
        self.assertFalse(publication.cleanup_complete)
        cached = Path(self.controller._paths(claim.request_id)["cache"]).read_bytes()
        self.assertEqual(publication.response, json.loads(cached))
        self.assertEqual(publication.response_bytes, len(cached))

    def test_duplicate_pending_uuid_while_inflight(self):
        claim = self.claim_new(self.request())
        def hook():
            self.assertEqual(self.duplicate(claim).disposition, "inflight")
        self.controller.execute(claim, self.stub(claim, hook))
        with self.assertRaisesRegex(transport.TransportError, "CallbackNotAuthorized"):
            self.controller.execute(claim, self.stub(claim))

    def test_duplicate_delivery_republishes_cache(self):
        claim = self.claim_new(self.request())
        self.controller.execute(claim, self.stub(claim))
        response_path = self.mailbox / (claim.request_id + ".response.json")
        original = response_path.read_bytes()
        response_path.unlink()  # Synthetic consumer; no task data.
        duplicate = self.duplicate(claim)
        self.assertEqual(duplicate.disposition, "cache")
        self.assertEqual(self.controller.publish_cached(duplicate).status, "published")
        self.assertEqual(response_path.read_bytes(), original)
        self.assertEqual(self.controller.publish_cached(duplicate).status, "already_published")

    def test_cleanup_unlink_raises_after_accepted_execution(self):
        claim = self.claim_new(self.request())
        original = transport._HOST_UNLINK
        def failing(path):
            if path == claim.claimed_path:
                raise OSError("synthetic cleanup failure")
            return original(path)
        with patch.object(transport, "_HOST_UNLINK", failing):
            with self.assertRaisesRegex(transport.TransportError, "CleanupFailed") as caught:
                self.controller.execute(claim, self.stub(claim))
            self.assert_known_publication(caught.exception, claim)
        duplicate = self.duplicate(claim)
        self.assertEqual(duplicate.disposition, "cache")
        self.controller.publish_cached(duplicate)

    def test_cleanup_unlink_noop_after_accepted_execution(self):
        claim = self.claim_new(self.request())
        original = transport._HOST_UNLINK
        def ineffective(path):
            if path == claim.claimed_path:
                return None
            return original(path)
        with patch.object(transport, "_HOST_UNLINK", ineffective):
            with self.assertRaisesRegex(transport.TransportError, "CleanupFailed") as caught:
                self.controller.execute(claim, self.stub(claim))
            self.assert_known_publication(caught.exception, claim)
        self.assertEqual(self.duplicate(claim).disposition, "cache")

    def test_already_existing_matching_response(self):
        claim = self.claim_new(self.request())
        self.controller.execute(claim, self.stub(claim))
        duplicate = self.duplicate(claim)
        self.assertEqual(self.controller.publish_cached(duplicate).status, "already_published")

    def test_harmful_response_appears_after_callback(self):
        claim = self.claim_new(self.request())
        response_path = self.mailbox / (claim.request_id + ".response.json")
        def hook():
            response_path.write_text('{"status":"stale_unrelated_receipt"}')
        with self.assertRaisesRegex(transport.TransportError, "ExistingResponseConflict"):
            self.controller.execute(claim, self.stub(claim, hook))
        self.assertEqual(json.loads(response_path.read_text())["status"], "stale_unrelated_receipt")
        duplicate = self.duplicate(claim)
        self.assertEqual(duplicate.disposition, "cache")
        with self.assertRaisesRegex(transport.TransportError, "ExistingResponseConflict"):
            self.controller.publish_cached(duplicate)

    def test_harmful_response_before_claim_rejected(self):
        pending = self.request()
        request_id = pending.name.removesuffix(".request.json")
        response_path = self.mailbox / (request_id + ".response.json")
        response_path.write_text('{"status":"stale_unrelated_receipt"}')
        claim = self.controller.claim(pending)
        self.assertEqual(claim.disposition, "conflict")
        self.assertEqual(claim.reason, "UnexpectedExistingResponse")
        self.rejected.add(request_id)
        response_path.unlink()
        restarted = transport.TransportOnce(self.mailbox)
        self.assertEqual(self.duplicate(claim, controller=restarted).disposition, "conflict")

    def test_delayed_cleanup_with_duplicate_thread(self):
        claim = self.claim_new(self.request())
        original = transport._HOST_UNLINK
        entered, release, duplicate_started = threading.Event(), threading.Event(), threading.Event()
        errors, duplicates = [], []
        def delayed(path):
            if path == claim.claimed_path:
                entered.set()
                if not release.wait(3):
                    raise OSError("synthetic cleanup release missing")
            return original(path)
        def publisher():
            try:
                self.controller.execute(claim, self.stub(claim))
            except BaseException as exc:
                errors.append(exc)
        def duplicate_worker():
            try:
                duplicate_started.set()
                duplicates.append(self.duplicate(claim))
            except BaseException as exc:
                errors.append(exc)
        with patch.object(transport, "_HOST_UNLINK", delayed):
            publishing = threading.Thread(target=publisher)
            publishing.start()
            self.assertTrue(entered.wait(3))
            duplicating = threading.Thread(target=duplicate_worker)
            duplicating.start()
            self.assertTrue(duplicate_started.wait(3))
            release.set()
            publishing.join(3)
            duplicating.join(3)
        self.assertFalse(publishing.is_alive())
        self.assertFalse(duplicating.is_alive())
        self.assertEqual(errors, [])
        self.assertEqual(duplicates[0].disposition, "cache")
        self.controller.publish_cached(duplicates[0])

    def test_publication_failure_then_cached_recovery(self):
        claim = self.claim_new(self.request())
        original = transport._HOST_LINK
        def failing(source, destination, **kwargs):
            if destination.endswith(".response.json"):
                paths = self.controller._paths(claim.request_id)
                self.assertTrue(Path(paths["cache"]).exists())
                self.assertTrue(Path(paths["executed"]).exists())
                raise OSError("synthetic publication failure")
            return original(source, destination, **kwargs)
        with patch.object(transport, "_HOST_LINK", failing):
            with self.assertRaisesRegex(transport.TransportError, "PublicationFailed") as caught:
                self.controller.execute(claim, self.stub(claim))
            self.assertEqual(caught.exception.publication_state, "unknown")
            self.assertIsNone(caught.exception.publication)
        self.controller.publish_cached(self.duplicate(claim))

    def test_responded_record_failure_preserves_published_cost(self):
        claim = self.claim_new(self.request())
        original = transport._HOST_LINK
        def failing(source, destination, **kwargs):
            if destination.endswith(".responded.json"):
                raise OSError("synthetic responded-ledger failure")
            return original(source, destination, **kwargs)
        with patch.object(transport, "_HOST_LINK", failing):
            with self.assertRaisesRegex(transport.TransportError, "PublicationFailed") as caught:
                self.controller.execute(claim, self.stub(claim))
            self.assert_known_publication(caught.exception, claim)
        self.controller.publish_cached(self.duplicate(claim))

    def test_response_fsync_failure_preserves_installed_cost(self):
        claim = self.claim_new(self.request())
        original = transport._sync_directory
        failed = [False]
        response_path = str(self.mailbox / (claim.request_id + ".response.json"))
        def failing(path):
            if path == str(self.mailbox) and transport._exists(response_path) and not failed[0]:
                failed[0] = True
                raise OSError("synthetic response directory fsync failure")
            return original(path)
        with patch.object(transport, "_sync_directory", failing):
            with self.assertRaisesRegex(transport.TransportError, "PublicationFailed") as caught:
                self.controller.execute(claim, self.stub(claim))
            self.assert_known_publication(caught.exception, claim)
        self.controller.publish_cached(self.duplicate(claim))

    def test_response_temporary_cleanup_failure_preserves_installed_cost(self):
        claim = self.claim_new(self.request())
        original = transport._HOST_UNLINK
        def failing(path):
            if ".response.json.tmp." in path:
                raise OSError("synthetic response temporary cleanup failure")
            return original(path)
        with patch.object(transport, "_HOST_UNLINK", failing):
            with self.assertRaisesRegex(transport.TransportError, "PublicationFailed") as caught:
                self.controller.execute(claim, self.stub(claim))
            self.assert_known_publication(caught.exception, claim)
        self.controller.publish_cached(self.duplicate(claim))

    def test_existing_matching_response_later_cleanup_failure_cost(self):
        claim = self.claim_new(self.request())
        self.controller.execute(claim, self.stub(claim))
        duplicate = self.duplicate(claim)
        original = transport._HOST_UNLINK
        def failing(path):
            if path == duplicate.pending_path:
                raise OSError("synthetic duplicate cleanup failure")
            return original(path)
        with patch.object(transport, "_HOST_UNLINK", failing):
            with self.assertRaisesRegex(transport.TransportError, "CleanupFailed") as caught:
                self.controller.publish_cached(duplicate)
            self.assert_known_publication(caught.exception, claim, "already_published")

    def test_consumer_unlinks_new_response_before_publisher_finishes(self):
        claim = self.claim_new(self.request())
        original = transport._HOST_LINK
        consumed = []
        def consume_after_link(source, destination, **kwargs):
            result = original(source, destination, **kwargs)
            if destination.endswith(".response.json"):
                consumed.append(transport._read(destination))
                transport._HOST_UNLINK(destination)
            return result
        with patch.object(transport, "_HOST_LINK", consume_after_link):
            publication = self.controller.execute(claim, self.stub(claim))
        self.assertEqual(publication.status, "published")
        self.assertEqual(publication.response, json.loads(consumed[0]))
        self.assertEqual(publication.response_bytes, len(consumed[0]))
        self.assertFalse((self.mailbox / (claim.request_id + ".response.json")).exists())
        self.controller.publish_cached(self.duplicate(claim))

    def test_cache_persisted_executed_record_failed_restart_closed(self):
        claim = self.claim_new(self.request())
        original = transport._HOST_LINK
        def failing(source, destination, **kwargs):
            if destination.endswith(".executed.json"):
                self.assertTrue(Path(self.controller._paths(claim.request_id)["cache"]).exists())
                raise OSError("synthetic executed-ledger persistence failure")
            return original(source, destination, **kwargs)
        with patch.object(transport, "_HOST_LINK", failing):
            with self.assertRaisesRegex(transport.TransportError, "ResultPersistenceFailed"):
                self.controller.execute(claim, self.stub(claim))
        restarted = transport.TransportOnce(self.mailbox)
        duplicate = self.duplicate(claim, controller=restarted)
        self.assertEqual(duplicate.disposition, "inflight")
        with self.assertRaisesRegex(transport.TransportError, "CallbackNotAuthorized"):
            restarted.execute(duplicate, self.stub(claim))

    def test_global_os_path_unlink_monkeypatch_independent_host(self):
        claim = self.claim_new(self.request())
        with patch.object(os, "unlink", lambda *args, **kwargs: None), \
                patch.object(Path, "unlink", lambda *args, **kwargs: None), \
                patch.object(os, "rename", lambda *args, **kwargs: None):
            self.controller.execute(claim, self.stub(claim))
            # Fresh claim also uses captured rename while globals are disabled.
            second = self.claim_new(self.request())
            self.controller.execute(second, self.stub(second))
            self.assertFalse(transport._exists(claim.claimed_path))
            self.assertFalse(transport._exists(second.claimed_path))

    def test_full_guard_filesystem_monkeypatch_independent_host(self):
        first_pending, second_pending = self.request(), self.request()
        ledger = self.mailbox / "full_guard_ledger"
        disabled = lambda *args, **kwargs: None
        # All request fixtures exist before the synthetic native global patches.
        with patch.multiple(os, open=disabled, read=disabled, write=disabled,
                            close=disabled, rename=disabled, unlink=disabled,
                            mkdir=disabled), \
                patch.multiple(Path, open=disabled, write_text=disabled,
                               mkdir=disabled, unlink=disabled, rename=disabled), \
                patch.object(builtins, "open", disabled), patch.object(io, "open", disabled):
            self.controller = transport.TransportOnce(self.mailbox, ledger)
            first, second = self.claim_new(first_pending), self.claim_new(second_pending)
            self.controller.execute(first, self.stub(first))
            self.controller.execute(second, self.stub(second))
            transport._write_immutable(first.pending_path, transport._canonical({"op": "stub", "value": 7}))
            duplicate = self.controller.claim(first.pending_path)
            self.assertEqual(duplicate.disposition, "cache")
            self.assertEqual(self.controller.publish_cached(duplicate).status, "already_published")
            self.assertFalse(transport._exists(first.pending_path))

    def test_restart_executed_cache_only(self):
        claim = self.claim_new(self.request())
        self.controller.execute(claim, self.stub(claim))
        restarted = transport.TransportOnce(self.mailbox)
        duplicate = self.duplicate(claim, controller=restarted)
        self.assertEqual(duplicate.disposition, "cache")
        restarted.publish_cached(duplicate)
        with self.assertRaisesRegex(transport.TransportError, "CallbackNotAuthorized"):
            restarted.execute(duplicate, self.stub(claim))

    def test_restart_claimed_without_result_fail_closed(self):
        claim = self.claim_new(self.request())
        # Synthetic crash window after callback, before complete/cache.
        self.stub(claim)(claim.payload)
        restarted = transport.TransportOnce(self.mailbox)
        duplicate = self.duplicate(claim, controller=restarted)
        self.assertEqual(duplicate.disposition, "inflight")
        with self.assertRaisesRegex(transport.TransportError, "CallbackNotAuthorized"):
            restarted.execute(duplicate, self.stub(claim))
        with self.assertRaisesRegex(transport.TransportError, "CompletionNotAuthorized"):
            restarted.complete(claim, {"status": "fabricated_after_restart"})

    def test_restart_claimed_before_callback_abandoned_no_retry(self):
        claim = self.controller.claim(self.request())
        self.assertEqual(claim.disposition, "new")
        # This intentionally abandoned claim never entered callback admission.
        self.abandoned.add(claim.request_id)
        restarted = transport.TransportOnce(self.mailbox)
        duplicate = self.duplicate(claim, controller=restarted)
        self.assertEqual(duplicate.disposition, "inflight")
        with self.assertRaisesRegex(transport.TransportError, "CallbackNotAuthorized"):
            restarted.execute(duplicate, self.stub(claim))

    def test_changed_payload_same_uuid_fail_closed(self):
        claim = self.claim_new(self.request())
        self.controller.execute(claim, self.stub(claim))
        duplicate = self.duplicate(claim, {"op": "stub", "value": 8})
        self.assertEqual(duplicate.disposition, "conflict")
        self.assertEqual(duplicate.reason, "PayloadChanged")
        with self.assertRaisesRegex(transport.TransportError, "CallbackNotAuthorized"):
            self.controller.execute(duplicate, self.stub(claim))
        with self.assertRaisesRegex(transport.TransportError, "CachedPublicationNotAuthorized"):
            self.controller.publish_cached(duplicate)

    def test_corrupted_cache_never_reexecutes(self):
        claim = self.claim_new(self.request())
        self.controller.execute(claim, self.stub(claim))
        Path(self.controller._paths(claim.request_id)["cache"]).write_text('{"status":"tampered"}')
        restarted = transport.TransportOnce(self.mailbox)
        with self.assertRaisesRegex(transport.TransportError, "CacheIntegrity"):
            self.duplicate(claim, controller=restarted)

    def test_response_tampering_does_not_mutate_cache(self):
        claim = self.claim_new(self.request())
        self.controller.execute(claim, self.stub(claim))
        response_path = self.mailbox / (claim.request_id + ".response.json")
        response_path.write_text('{"status":"tampered_publication"}')
        duplicate = self.duplicate(claim)
        self.assertEqual(duplicate.disposition, "cache")
        with self.assertRaisesRegex(transport.TransportError, "ExistingResponseConflict"):
            self.controller.publish_cached(duplicate)
        cached = json.loads(Path(self.controller._paths(claim.request_id)["cache"]).read_text())
        self.assertEqual(cached["status"], "synthetic_receipt")

    def test_same_live_claim_concurrent_callback_admission(self):
        claim = self.claim_new(self.request())
        entered, release = threading.Event(), threading.Event()
        def hook():
            entered.set()
            self.assertTrue(release.wait(3))
        with ThreadPoolExecutor(max_workers=2) as pool:
            first = pool.submit(self.controller.execute, claim, self.stub(claim, hook))
            self.assertTrue(entered.wait(3))
            second = pool.submit(self.controller.execute, claim, self.stub(claim))
            with self.assertRaisesRegex(transport.TransportError, "CallbackNotAuthorized"):
                second.result(timeout=3)
            release.set()
            first.result(timeout=3)

    def test_batch_stress_128_uuids_2048_cache_deliveries(self):
        def worker(number):
            request_id = f"{number:032x}"
            claim = self.claim_new(self.request(request_id))
            self.controller.execute(claim, self.stub(claim))
            for repeat in range(16):
                if repeat % 3 == 0:
                    (self.mailbox / (request_id + ".response.json")).unlink()
                restarted = transport.TransportOnce(self.mailbox)
                duplicate = self.duplicate(claim, controller=restarted)
                self.assertEqual(duplicate.disposition, "cache")
                restarted.publish_cached(duplicate)
        with ThreadPoolExecutor(max_workers=8) as pool:
            list(pool.map(worker, range(1, 129)))
        self.assertEqual(len(self.accepted), 128)
        self.assertEqual(sum(self.calls.values()), 128)

    def test_separate_process_restart_executed_and_claimed(self):
        # Child imports only this transport module and stdlib; no native runtime.
        script = '''
import json, sys
import transport_once as t
controller = t.TransportOnce(sys.argv[1])
claim = controller.claim(sys.argv[2])
calls = [0]
def callback(payload):
    calls[0] += 1
    return {"status":"synthetic_forbidden_retry"}
try:
    controller.execute(claim, callback)
except t.TransportError as error:
    assert error.code == "CallbackNotAuthorized"
else:
    raise AssertionError("restart authorized callback")
if claim.disposition == "cache":
    controller.publish_cached(claim)
print(json.dumps({"disposition":claim.disposition,"callback_calls":calls[0]}))
'''
        executed = self.claim_new(self.request())
        self.controller.execute(executed, self.stub(executed))
        interrupted = self.claim_new(self.request())
        self.stub(interrupted)(interrupted.payload)  # Lost result crash window.
        for claim, expected in [(executed, "cache"), (interrupted, "inflight")]:
            pending = self.request(claim.request_id)
            completed = subprocess.run(
                [sys.executable, "-B", "-c", script, str(self.mailbox), str(pending)],
                cwd=Path(__file__).parent, text=True, capture_output=True, timeout=10,
                check=True,
            )
            self.assertEqual(json.loads(completed.stdout), {"disposition": expected, "callback_calls": 0})


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--result", type=Path)
    args = parser.parse_args()
    if any(name == "appworld" or name.startswith("appworld.") for name in sys.modules):
        raise RuntimeError("transport-only runner found an imported native runtime")
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TransportOnlyTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if args.result:
        source = Path(__file__).with_name("transport_once.py")
        report = {
            "schema_version": 1, "date": "2026-10-04", "scope": "synthetic_transport_only",
            "appworld_imported": any(name == "appworld" or name.startswith("appworld.") for name in sys.modules),
            "task_world_api_model_evaluator_calls": 0,
            "real_task_data_used": False, "tests_run": result.testsRun,
            "tests_passed": result.testsRun - len(result.failures) - len(result.errors),
            "failures": len(result.failures), "errors": len(result.errors),
            "successful": result.wasSuccessful(), "cases": _COUNTS,
            "accepted_callback_uuids_total": sum(x["accepted_uuids"] for x in _COUNTS.values()),
            "new_claims_total": sum(x["new_claims"] for x in _COUNTS.values()),
            "callback_calls_total": sum(x["callback_calls"] for x in _COUNTS.values()),
            "rejected_before_callback_total": sum(x["rejected_before_callback"] for x in _COUNTS.values()),
            "abandoned_new_claims_before_callback_total": sum(x["abandoned_new_claims_before_callback"] for x in _COUNTS.values()),
            "transport_source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            "test_source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "limits": ["at-most-once admission, not general exactly-once execution",
                       "claimed without executed result fails closed, even if callback never ran",
                       "response publication is not consumer acknowledgment",
                       "local POSIX filesystem and durable ledger must be retained",
                       "native bridge integration and native task controls not tested here"],
        }
        args.result.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
