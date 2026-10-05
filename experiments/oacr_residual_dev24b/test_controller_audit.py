"""Check actual durable transport audit with synthetic, non-native events."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import export_results as audit
import transport_once as transport


class ControllerAuditTests(unittest.TestCase):
    def build(self, root, cleanup_failure=False, cached=False):
        private = root/'private'
        private.mkdir()
        mailbox = root/'mailbox'
        manager = transport.TransportOnce(mailbox, private/'transport_0')
        identity = '1'*32
        payload = {'op':'execute','code':'print(7)'}
        pending = mailbox/(identity+'.request.json')
        pending.write_text(json.dumps(payload))
        claim = manager.claim(pending)
        uhash = hashlib.sha256(identity.encode()).hexdigest()
        response = {'status':'native_receipt','receipt':'synthetic','step':1}
        events = [
            {'op':'transport_claim','uuid_sha256':uhash,'disposition':'new'},
            {'op':'request','request_file':pending.name,'request':payload,'actor_elapsed_seconds':0.1},
            {'op':'execute','metrics':{'request_uuid_sha256':uhash}},
        ]
        calls = []
        def callback(value):
            calls.append(value)
            return response
        if cleanup_failure:
            original = transport._HOST_UNLINK
            def fail(path):
                if path == claim.claimed_path:
                    raise OSError('synthetic')
                return original(path)
            with patch.object(transport,'_HOST_UNLINK',fail):
                try:
                    manager.execute(claim,callback)
                except transport.TransportError as exc:
                    publication = exc.publication
                else:
                    raise AssertionError('missing synthetic cleanup failure')
        else:
            publication = manager.execute(claim,callback)
        events.append({'op':'response','request_file':pending.name,'response':publication.response,
                       'publication_status':publication.status,'newly_published':publication.status=='published',
                       'published_response_bytes':publication.response_bytes})
        row = {'transport_new_claims':1,'transport_duplicate_deliveries':0,'transport_cache_publications':0,
               'mailbox_response_bytes':publication.response_bytes,'transport_prompt_text_bytes':0,
               'transport_receipt_text_bytes':len(response['receipt'].encode()),'prompt_pages_delivered':0,
               'receipt_pages_delivered':1,'prompt_page_requests':0,'receipt_page_requests':0,'bridge_request_errors':0}
        if cached:
            (mailbox/(identity+'.response.json')).unlink()
            pending.write_text(json.dumps(payload))
            duplicate = manager.claim(pending)
            pub = manager.publish_cached(duplicate)
            events.extend([{'op':'transport_claim','uuid_sha256':uhash,'disposition':'cache'},
                           {'op':'response','request_file':pending.name,'response':pub.response,
                            'publication_status':pub.status,'newly_published':True,'published_response_bytes':pub.response_bytes}])
            row.update(transport_duplicate_deliveries=1,transport_cache_publications=1,
                       mailbox_response_bytes=2*publication.response_bytes,
                       transport_receipt_text_bytes=2*len(response['receipt'].encode()),receipt_pages_delivered=2)
        self.assertEqual(len(calls),1)
        return private,events,row,manager,claim

    def test_new_and_cached_publication_audits(self):
        with tempfile.TemporaryDirectory() as tmp:
            private,events,row,_,_=self.build(Path(tmp),cached=True)
            errors=set(); result=audit.audit_transport(events,row,private,0,errors)
            self.assertEqual(errors,set())
            self.assertTrue(result['execute_uuid_unique'])
            self.assertEqual(result['cache_deliveries'],1)

    def test_duplicate_execution_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            private,events,row,_,_=self.build(Path(tmp))
            events.insert(3,events[2].copy())
            errors=set();audit.audit_transport(events,row,private,0,errors)
            self.assertIn('execute_uuid_reused',errors)

    def test_cache_tampering_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            private,events,row,manager,claim=self.build(Path(tmp))
            Path(manager._paths(claim.request_id)['cache']).write_text('{"wrong":true}\n')
            errors=set();audit.audit_transport(events,row,private,0,errors)
            self.assertIn('executed_cache_or_payload_hash_mismatch',errors)

    def test_published_cleanup_failure_is_charged_and_retained(self):
        with tempfile.TemporaryDirectory() as tmp:
            private,events,row,_,_=self.build(Path(tmp),cleanup_failure=True)
            errors=set();result=audit.audit_transport(events,row,private,0,errors)
            self.assertIn('responded_claim_input_retained_requires_review',errors)
            self.assertNotIn('transport_count_or_publication_cost_mismatch',errors)
            self.assertGreater(result['publication_counts_and_bytes']['mailbox_response_bytes'],0)


if __name__=='__main__':
    unittest.main(verbosity=2)
