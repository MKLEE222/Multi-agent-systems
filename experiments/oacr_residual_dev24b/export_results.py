#!/usr/bin/env python3
"""Read-only audit of fixed development rows and durable transport.

Private events and ledger artifacts are read only by this controller program.
Public output contains hashes, counts and fixed labels, never raw task IDs,
UUIDs, requests, code, prompts or receipts. No native imports or native calls.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re

REQUEST_NAME = re.compile(r"([0-9a-f]{32})\.request\.json\Z")
LEDGER_NAME = re.compile(r"([0-9a-f]{32})\.(claimed\.json|claimed\.request\.json|cache\.json|executed\.json|responded\.json|lock)\Z")
HASH = re.compile(r"[0-9a-f]{64}\Z")
COST_KEYS = ["execute_requests", "native_execute_attempts", "native_interactions", "native_api_calls",
             "bridge_rejections", "parse_errors", "native_execution_errors", "generated_receipt_bytes",
             "generated_native_receipt_bytes", "generated_bridge_receipt_bytes", "prompt_bytes",
             "transport_prompt_text_bytes", "transport_receipt_text_bytes", "prompt_page_requests",
             "receipt_page_requests", "mailbox_response_bytes", "actor_elapsed_seconds"]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def encoded(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode()


def request_hash(event, errors):
    name = event.get("request_file")
    matched = REQUEST_NAME.fullmatch(name) if isinstance(name, str) else None
    if matched is None:
        errors.add("invalid_private_request_filename")
        return None
    return digest(matched.group(1).encode())


def audit_transport(events, row, private_root, index, errors):
    """Validate final UUID states and chronological dispatch/publication evidence."""
    directory = private_root / f"transport_{index}"
    artifacts = defaultdict(dict)
    file_hashes, temporary_count = [], 0
    if not directory.is_dir() or directory.is_symlink():
        errors.add("missing_or_unsafe_transport_ledger")
        paths = []
    else:
        paths = sorted(directory.iterdir(), key=lambda path: path.name)
    for path in paths:
        matched = LEDGER_NAME.fullmatch(path.name)
        if path.is_symlink() or not path.is_file():
            errors.add("unsafe_transport_ledger_artifact")
            continue
        if matched is None:
            temporary_count += 1
            errors.add("unexpected_or_partial_transport_artifact")
            continue
        identifier, kind = matched.groups()
        uuid_hash = digest(identifier.encode())
        try:
            raw = path.read_bytes()
            file_hashes.append([uuid_hash, kind, digest(raw)])
            if kind == "lock":
                continue
            value = json.loads(raw)
            if not isinstance(value, dict):
                raise ValueError()
            if kind in {"claimed.json", "executed.json", "responded.json"}:
                if (value.get("schema_version") != 1 or value.get("request_id") != identifier
                        or value.get("state") != kind.split(".")[0]):
                    raise ValueError()
            if kind != "claimed.request.json" and encoded(value) + b"\n" != raw:
                raise ValueError()
            artifacts[uuid_hash][kind] = (value, raw)
        except (OSError, ValueError, TypeError):
            errors.add("transport_artifact_integrity_mismatch")
            artifacts[uuid_hash][kind] = (None, None)

    claims, requests, execute_uuids, responses, publication = (Counter() for _ in range(5))
    active = None
    segment_requests = segment_responses = incomplete_segments = 0

    def close_segment():
        nonlocal incomplete_segments
        if active is not None and active[1] in {"new", "cache"} and segment_responses != 1:
            incomplete_segments += 1
            errors.add("transport_claim_without_one_response_event")

    for event in events:
        op = event.get("op")
        if op == "transport_claim":
            close_segment()
            uuid_hash, disposition = event.get("uuid_sha256"), event.get("disposition")
            if not isinstance(uuid_hash, str) or HASH.fullmatch(uuid_hash) is None:
                errors.add("invalid_transport_claim_hash")
                active = None
                continue
            if disposition not in {"new", "cache", "inflight", "conflict"}:
                errors.add("invalid_transport_claim_disposition")
            claims[(uuid_hash, disposition)] += 1
            active = (uuid_hash, disposition)
            segment_requests = segment_responses = 0
            if disposition in {"inflight", "conflict"}:
                errors.add("transport_endpoint_failed_closed_requires_review")
        elif op == "request":
            uuid_hash = request_hash(event, errors)
            if uuid_hash is None:
                continue
            requests[uuid_hash] += 1
            segment_requests += 1
            if active != (uuid_hash, "new") or segment_requests != 1:
                errors.add("dispatch_without_unique_new_admission")
            payload = event.get("request")
            claimed = artifacts.get(uuid_hash, {}).get("claimed.json", (None, None))[0]
            try:
                if (not isinstance(payload, dict) or claimed is None
                        or digest(encoded(payload) + b"\n") != claimed.get("payload_sha256")):
                    errors.add("transport_request_payload_hash_mismatch")
            except (ValueError, TypeError):
                errors.add("transport_request_payload_hash_mismatch")
            if isinstance(payload, dict):
                if payload.get("op") == "start":
                    publication["prompt_page_requests"] += 1
                if payload.get("op") == "receipt_page" and event.get("actor_elapsed_seconds") is not None:
                    publication["receipt_page_requests"] += 1
        elif op == "execute":
            metrics = event.get("metrics", {})
            uuid_hash = metrics.get("request_uuid_sha256") if isinstance(metrics, dict) else None
            if not isinstance(uuid_hash, str) or HASH.fullmatch(uuid_hash) is None:
                errors.add("missing_execute_uuid_hash")
                continue
            execute_uuids[uuid_hash] += 1
            if active != (uuid_hash, "new") or requests[uuid_hash] != 1:
                errors.add("execute_without_unique_new_dispatch")
        elif op == "response":
            uuid_hash = request_hash(event, errors)
            if uuid_hash is None:
                continue
            responses[uuid_hash] += 1
            segment_responses += 1
            if active is None or active[0] != uuid_hash or active[1] not in {"new", "cache"} or segment_responses != 1:
                errors.add("response_without_matching_transport_claim")
            response = event.get("response")
            cached = artifacts.get(uuid_hash, {}).get("cache.json", (None, None))[1]
            try:
                raw = encoded(response) + b"\n"
                if not isinstance(response, dict) or cached != raw:
                    errors.add("response_event_cache_hash_mismatch")
            except (ValueError, TypeError):
                errors.add("response_event_cache_hash_mismatch")
                continue
            status, published = event.get("publication_status"), event.get("newly_published")
            if status not in {"published", "already_published"} or published is not (status == "published"):
                errors.add("invalid_publication_event_status")
            if response.get("status") == "bridge_error":
                publication["bridge_request_errors"] += 1
            if published is True:
                publication["mailbox_response_bytes"] += len(raw)
                if active is not None and active[1] == "cache":
                    publication["transport_cache_publications"] += 1
                for key in ("prompt", "receipt"):
                    if key in response:
                        if not isinstance(response[key], str):
                            errors.add("invalid_publication_text_field")
                            continue
                        publication[f"transport_{key}_text_bytes"] += len(response[key].encode())
                        publication[f"{key}_pages_delivered"] += 1
    close_segment()
    if any(n != 1 for n in execute_uuids.values()):
        errors.add("execute_uuid_reused")
    if any(n != 1 for n in requests.values()):
        errors.add("request_callback_uuid_reused")
    new_uuids = {u for (u, disposition), n in claims.items() if disposition == "new" and n}
    if any(n != 1 for (_, disposition), n in claims.items() if disposition == "new"):
        errors.add("new_uuid_admission_reused")
    if not set(execute_uuids).issubset(new_uuids) or not set(requests).issubset(new_uuids):
        errors.add("dispatch_uuid_missing_new_admission")
    request_execute = Counter(request_hash(e, errors) for e in events
                              if e.get("op") == "request" and isinstance(e.get("request"), dict)
                              and e["request"].get("op") == "execute" and e.get("actor_elapsed_seconds") is not None)
    if request_execute != execute_uuids:
        errors.add("execute_request_uuid_ledger_mismatch")
    state_counts = Counter()
    for uuid_hash in set(artifacts) | {key[0] for key in claims}:
        parts = artifacts.get(uuid_hash, {})
        claimed = parts.get("claimed.json", (None, None))[0]
        executed = parts.get("executed.json", (None, None))[0]
        responded = parts.get("responded.json", (None, None))[0]
        cache, cache_raw = parts.get("cache.json", (None, None))
        input_value = parts.get("claimed.request.json", (None, None))[0]
        if claimed is None:
            state_counts["orphan_or_invalid"] += 1
            errors.add("transport_uuid_missing_valid_claim")
            continue
        payload_hash = claimed.get("payload_sha256")
        if not isinstance(payload_hash, str) or HASH.fullmatch(payload_hash) is None:
            errors.add("invalid_claim_payload_hash")
        if input_value is not None and digest(encoded(input_value) + b"\n") != payload_hash:
            errors.add("retained_claim_input_hash_mismatch")
        if claimed.get("blocked_reason"):
            state_counts["blocked"] += 1
            errors.add("blocked_claim_requires_review")
            if executed is not None or cache is not None or requests[uuid_hash]:
                errors.add("blocked_claim_dispatched_or_executed")
        elif executed is None:
            state_counts["claimed_without_executed_result"] += 1
            errors.add("claimed_without_executed_result_requires_review")
        elif (cache is None or executed.get("payload_sha256") != payload_hash
              or executed.get("response_sha256") != digest(cache_raw)):
            state_counts["invalid_execution_result"] += 1
            errors.add("executed_cache_or_payload_hash_mismatch")
        elif responded is None:
            state_counts["executed_without_responded_record"] += 1
            errors.add("executed_without_responded_record_requires_review")
        else:
            state_counts["responded"] += 1
            if (responded.get("response_sha256") != digest(cache_raw)
                    or responded.get("meaning") != "published_not_consumption_acknowledged"):
                errors.add("responded_cache_hash_or_meaning_mismatch")
            if "claimed.request.json" in parts:
                errors.add("responded_claim_input_retained_requires_review")
        if executed is not None and requests[uuid_hash] != 1:
            errors.add("durable_execution_without_one_callback_event")
        if claimed.get("blocked_reason") is None and uuid_hash not in new_uuids:
            errors.add("ledger_uuid_missing_new_claim_event")
    publication["transport_new_claims"] = sum(n for (_, d), n in claims.items() if d == "new")
    publication["transport_duplicate_deliveries"] = sum(n for (_, d), n in claims.items() if d == "cache")
    for key in ["transport_new_claims", "transport_duplicate_deliveries", "transport_cache_publications",
                "mailbox_response_bytes", "transport_prompt_text_bytes", "transport_receipt_text_bytes",
                "prompt_pages_delivered", "receipt_pages_delivered", "prompt_page_requests",
                "receipt_page_requests", "bridge_request_errors"]:
        if row.get(key) != publication[key]:
            errors.add("transport_count_or_publication_cost_mismatch")
    return {"uuid_records": len(artifacts), "new_admissions": publication["transport_new_claims"],
            "cache_deliveries": publication["transport_duplicate_deliveries"],
            "execute_uuid_count": len(execute_uuids), "execute_uuid_unique": all(n == 1 for n in execute_uuids.values()),
            "state_counts": dict(sorted(state_counts.items())), "incomplete_claim_segments": incomplete_segments,
            "partial_or_unrecognized_artifacts": temporary_count,
            "artifact_hashes_sha256": digest(encoded(sorted(file_hashes))),
            "publication_counts_and_bytes": dict(sorted(publication.items())),
            "proof_source": "private event sequence plus durable UUID ledger; guard flag is not proof"}


def audit_row(row, frozen, index, private_root, freeze_hash):
    errors = set()
    for key, expected in [("task_id_sha256", frozen["selected_task_hashes"][index]),
                          ("family_sha256", frozen["selected_family_hashes"][index]),
                          ("index", index), ("batch_denominator", frozen["actors"]), ("freeze_sha256", freeze_hash)]:
        if row.get(key) != expected:
            errors.add("frozen_identity_or_denominator_mismatch")
    events_path = private_root / f"events_{index}.jsonl"
    try:
        if events_path.is_symlink():
            raise ValueError()
        raw_events = events_path.read_bytes()
        events = [json.loads(line) for line in raw_events.splitlines()]
        if any(not isinstance(event, dict) for event in events):
            raise ValueError()
    except (OSError, ValueError, TypeError):
        return {"index": index, "status": "requires_review", "errors": ["missing_or_invalid_private_events"]}
    chain = "0" * 64
    transport = None
    try:
        for seq, event in enumerate(events, 1):
            if event.get("sequence") != seq or event.get("previous_sha256") != chain:
                errors.add("event_chain_mismatch")
            chain = digest(encoded(event))
        if (chain != row.get("events_chain_final_sha256") or digest(raw_events) != row.get("events_sha256")
                or len(events) != row.get("events_count")):
            errors.add("final_event_hash_or_count_mismatch")
        executions = [e for e in events if e.get("op") == "execute"]
        if len(executions) != row.get("execute_requests") or [e.get("metrics") for e in executions] != row.get("steps"):
            errors.add("execute_ledger_mismatch")
        if not isinstance(row.get("execute_requests"), int) or not 0 <= row["execute_requests"] <= frozen["max_execute_requests_per_actor"]:
            errors.add("execute_budget_exceeded_or_unknown")
        for step, event in enumerate(executions, 1):
            metrics, receipt, code = event["metrics"], event["receipt"], event.get("code")
            code_text = code if isinstance(code, str) else encoded(code).decode()
            if (metrics.get("request_index") != step or not isinstance(receipt, str)
                    or metrics.get("receipt_sha256") != digest(receipt.encode()) or metrics.get("receipt_bytes") != len(receipt.encode())
                    or metrics.get("code_sha256") != digest(code_text.encode()) or metrics.get("code_bytes") != len(code_text.encode())):
                errors.add("execute_code_receipt_or_order_mismatch")
        for field, total_key, error in [("native_api_calls", "native_api_calls", "native_requester_count_mismatch"),
                                        ("native_interactions_delta", "native_interactions", "native_interaction_count_mismatch")]:
            if sum(e["metrics"][field] for e in executions) != row.get(total_key):
                errors.add(error)
        for key, predicate in [("generated_receipt_bytes", lambda m: True),
                               ("generated_native_receipt_bytes", lambda m: m["receipt_source"] == "native"),
                               ("generated_bridge_receipt_bytes", lambda m: m["receipt_source"] != "native")]:
            if sum(e["metrics"]["receipt_bytes"] for e in executions if predicate(e["metrics"])) != row.get(key):
                errors.add("receipt_cost_mismatch")
        if sum(e["metrics"]["native_executed"] is True for e in executions) != row.get("native_execute_attempts"):
            errors.add("native_execute_attempt_count_mismatch")
        grades = [i for i, e in enumerate(events) if e.get("op") == "grade"]
        stops = [i for i, e in enumerate(events) if e.get("op") == "actor_stop"]
        grade = row["grade"]
        if grade.get("attempts") != len(grades) or len(grades) > 1:
            errors.add("grading_count_mismatch")
        if grades and events[grades[0]].get("grade") != grade:
            errors.add("grading_event_summary_mismatch")
        if len(stops) != 1 or (grades and grades[0] <= stops[0]):
            errors.add("grade_before_actor_stop_or_invalid_stop_count")
        if row.get("actor_ground_truth_loaded") is not False or row.get("actor_evaluator_feedback") is not False or row.get("oacr_intervention") is not False:
            errors.add("information_or_intervention_boundary_mismatch")
        if row.get("actor_started") and row.get("complete_prompt_delivered") is not True:
            errors.add("initial_prompt_not_fully_delivered")
        transport = audit_transport(events, row, private_root, index, errors)
    except (KeyError, ValueError, TypeError, OSError):
        errors.add("incomplete_or_invalid_audit_schema")
    return {"index": index, "status": "passed" if not errors else "requires_review", "errors": sorted(errors), "transport": transport}


def build_result(result_root, private_root, freeze_commit):
    freeze_raw = (result_root / "freeze.json").read_bytes()
    frozen = json.loads(freeze_raw)
    if (frozen.get("actors") != 24 or len(frozen.get("selected_task_hashes", [])) != 24
            or len(set(frozen.get("selected_family_hashes", []))) != 24):
        raise ValueError("fixed_denominator_mismatch")
    rows, audits = [], []
    for index in range(24):
        path = result_root / f"task_{index}_summary.json"
        try:
            if path.is_symlink():
                raise ValueError()
            row = json.loads(path.read_text())
            if not isinstance(row, dict) or not isinstance(row.get("grade"), dict):
                raise ValueError()
        except (OSError, ValueError, TypeError):
            rows.append({"index": index, "task_id_sha256": frozen["selected_task_hashes"][index],
                         "family_sha256": frozen["selected_family_hashes"][index], "grade": {"status": "missing_summary", "success": None},
                         "actor_started": None, "finish_reason": "missing_summary"})
            audits.append({"index": index, "status": "missing_summary_requires_controller_review"})
            continue
        rows.append(row)
        audits.append(audit_row(row, frozen, index, private_root, digest(freeze_raw)))
    evaluated = [r for r in rows if r["grade"].get("status") == "evaluated"]
    flags = [r["index"] for r in rows if r.get("high_cost_screen_triggered")]
    failures = [r["index"] for r in rows if r["grade"].get("success") is not True]
    return {"protocol": frozen["protocol"], "freeze_commit": freeze_commit, "freeze_sha256": digest(freeze_raw),
            "tasks": 24, "distinct_families": 24, "native_scored_tasks": len(evaluated),
            "native_task_successes": sum(r["grade"].get("success") is True for r in rows), "not_successful_or_unscored_indices": failures,
            "native_test_passed_known_subtotal": sum(r["grade"].get("pass_count", 0) for r in evaluated),
            "native_test_total_known_subtotal": sum(r["grade"].get("num_tests", 0) for r in evaluated),
            "high_cost_screen_indices": flags, "diagnosis_required_indices": sorted(set(failures + flags)),
            "high_cost_thresholds": frozen["high_cost_thresholds"],
            "grade_status_counts": dict(Counter(r["grade"].get("status", "unknown") for r in rows)),
            "cost_known_subtotals": {k: sum(r[k] for r in rows if isinstance(r.get(k), (int, float))) for k in COST_KEYS},
            "missing_cost_rows": [r["index"] for r in rows if any(r.get(k) is None for k in COST_KEYS)],
            "native_evaluator_invocations": sum(r["grade"].get("attempts", 0) for r in rows),
            "actor_invocations_started": sum(r.get("actor_started") is True for r in rows),
            "model_usage": "nonzero; model checkpoint, sampling seed, calls, tokens and cost unknown",
            "external_provider_model_calls": sum(r.get("external_provider_model_calls", 0) for r in rows),
            "actor_actual_visible_bytes": None, "oacr_intervention": False, "method_comparison": False,
            "sealed_evaluation_bank_512_used": False, "task_replacement_or_score_conditioned_retry": False,
            "audit": audits, "all_fixed_rows_audited": all(a["status"] == "passed" for a in audits),
            "source_ref": frozen["source_ref"], "final_broad_discovery": frozen.get("final_broad_discovery"),
            "stop_if_no_R1": frozen.get("stop_if_no_R1"), "R1_threshold": frozen.get("R1_threshold"),
            "interpretation": "Final fixed next-variant train discovery; costs require attribution; unresolved does not establish classical survival or novelty; no further broad discovery if R1 is absent."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--result-root", type=Path, required=True)
    parser.add_argument("--private-root", type=Path, required=True)
    parser.add_argument("--freeze-commit", required=True)
    args = parser.parse_args()
    result = build_result(args.result_root, args.private_root, args.freeze_commit)
    destination = args.result_root / "RESULT_2026-10-04.json"
    with destination.open("x") as stream:
        stream.write(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k: result[k] for k in ["tasks", "native_scored_tasks", "native_task_successes",
          "high_cost_screen_indices", "diagnosis_required_indices", "all_fixed_rows_audited"]}))


if __name__ == "__main__":
    main()
