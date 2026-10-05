#!/usr/bin/env python3
"""Audit a fixed development denominator without exporting protected traces."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path


def digest(data):
    return hashlib.sha256(data).hexdigest()


def encoded(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--result-root", type=Path, required=True)
    p.add_argument("--private-root", type=Path, required=True)
    p.add_argument("--freeze-commit", required=True)
    args = p.parse_args()
    frozen = json.loads((args.result_root / "freeze.json").read_text())
    rows, audits = [], []
    for index in range(frozen["actors"]):
        path = args.result_root / f"task_{index}_summary.json"
        if not path.exists():
            rows.append({"index": index, "task_id_sha256": frozen["selected_task_hashes"][index],
                         "family_sha256": frozen["selected_family_hashes"][index],
                         "grade": {"status": "missing_summary", "success": None},
                         "actor_started": None, "finish_reason": "missing_summary"})
            audits.append({"index": index, "status": "missing_summary_requires_controller_review"})
            continue
        row = json.loads(path.read_text())
        errors = []
        for key, expected in [("task_id_sha256", frozen["selected_task_hashes"][index]),
                              ("family_sha256", frozen["selected_family_hashes"][index]),
                              ("index", index), ("batch_denominator", frozen["actors"]),
                              ("freeze_sha256", digest((args.result_root / "freeze.json").read_bytes()))]:
            if row.get(key) != expected:
                errors.append("frozen_identity_or_denominator_mismatch")
        events_path = args.private_root / f"events_{index}.jsonl"
        events = [json.loads(line) for line in events_path.read_text().splitlines()]
        chain = "0" * 64
        for seq, event in enumerate(events, 1):
            if event.get("sequence") != seq or event.get("previous_sha256") != chain:
                errors.append("event_chain_mismatch")
            chain = digest(encoded(event))
        if chain != row["events_chain_final_sha256"] or digest(events_path.read_bytes()) != row["events_sha256"]:
            errors.append("final_event_hash_mismatch")
        executions = [event for event in events if event["op"] == "execute"]
        if len(executions) != row["execute_requests"] or [e["metrics"] for e in executions] != row["steps"]:
            errors.append("execute_ledger_mismatch")
        if row["execute_requests"] > frozen["max_execute_requests_per_actor"]:
            errors.append("execute_budget_exceeded")
        if sum(e["metrics"]["native_api_calls"] for e in executions) != row["native_api_calls"]:
            errors.append("native_requester_count_mismatch")
        if sum(e["metrics"]["native_interactions_delta"] for e in executions) != row["native_interactions"]:
            errors.append("native_interaction_count_mismatch")
        if sum(e["metrics"]["receipt_bytes"] for e in executions if e["metrics"]["receipt_source"] == "native") != row["generated_native_receipt_bytes"]:
            errors.append("native_receipt_cost_mismatch")
        if row["grade"]["attempts"] != len([e for e in events if e["op"] == "grade"]):
            errors.append("grading_count_mismatch")
        if row["actor_ground_truth_loaded"] or row["actor_evaluator_feedback"] or row["oacr_intervention"]:
            errors.append("information_or_intervention_boundary_mismatch")
        stops = [i for i, e in enumerate(events) if e["op"] == "actor_stop"]
        grades = [i for i, e in enumerate(events) if e["op"] == "grade"]
        if not stops or (grades and min(grades) <= max(stops)):
            errors.append("grade_before_actor_stop")
        if row["actor_started"] and not row["complete_prompt_delivered"]:
            errors.append("initial_prompt_not_fully_delivered")
        rows.append(row)
        audits.append({"index": index, "status": "passed" if not errors else "requires_review", "errors": sorted(set(errors))})
    evaluated = [r for r in rows if r["grade"]["status"] == "evaluated"]
    flags = [r["index"] for r in rows if r.get("high_cost_screen_triggered")]
    failures = [r["index"] for r in rows if r["grade"].get("success") is not True]
    cost_keys = ["execute_requests", "native_execute_attempts", "native_interactions", "native_api_calls",
                 "bridge_rejections", "parse_errors", "native_execution_errors", "generated_receipt_bytes",
                 "generated_native_receipt_bytes", "generated_bridge_receipt_bytes", "prompt_bytes",
                 "transport_prompt_text_bytes", "transport_receipt_text_bytes", "prompt_page_requests",
                 "receipt_page_requests", "mailbox_response_bytes", "actor_elapsed_seconds"]
    result = {
        "protocol": frozen["protocol"], "freeze_commit": args.freeze_commit,
        "freeze_sha256": digest((args.result_root / "freeze.json").read_bytes()),
        "tasks": len(rows), "distinct_families": len(set(frozen["selected_family_hashes"])),
        "native_scored_tasks": len(evaluated),
        "native_task_successes": sum(r["grade"].get("success") is True for r in rows),
        "not_successful_or_unscored_indices": failures,
        "native_test_passed_known_subtotal": sum(r["grade"]["pass_count"] for r in evaluated),
        "native_test_total_known_subtotal": sum(r["grade"]["num_tests"] for r in evaluated),
        "high_cost_screen_indices": flags,
        "diagnosis_required_indices": sorted(set(failures + flags)),
        "high_cost_thresholds": frozen["high_cost_thresholds"],
        "grade_status_counts": {s: sum(r["grade"]["status"] == s for r in rows) for s in sorted(set(r["grade"]["status"] for r in rows))},
        "cost_known_subtotals": {k: sum(r[k] for r in rows if isinstance(r.get(k), (int, float))) for k in cost_keys},
        "missing_cost_rows": [r["index"] for r in rows if any(r.get(k) is None for k in cost_keys)],
        "native_evaluator_invocations": sum(r["grade"].get("attempts", 0) for r in rows),
        "actor_invocations_started": sum(r.get("actor_started") is True for r in rows),
        "model_usage": "nonzero; model checkpoint, sampling seed, calls, tokens and cost unknown",
        "external_provider_model_calls": sum(r.get("external_provider_model_calls", 0) for r in rows),
        "actor_actual_visible_bytes": None,
        "oacr_intervention": False, "method_comparison": False,
        "sealed_evaluation_bank_512_used": False, "task_replacement_or_score_conditioned_retry": False,
        "audit": audits, "all_fixed_rows_audited": all(a["status"] == "passed" for a in audits),
        "source_ref": frozen["source_ref"],
        "interpretation": "Fixed manifest-prefix train discovery; cost flags require attribution, unresolved does not imply classical survival or novelty."
    }
    destination = args.result_root / "RESULT_2026-10-04.json"
    if destination.exists():
        raise FileExistsError("refuse replacing original aggregate")
    destination.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k: result[k] for k in ["tasks", "native_scored_tasks", "native_task_successes",
          "high_cost_screen_indices", "diagnosis_required_indices", "all_fixed_rows_audited"]}))


if __name__ == "__main__":
    main()
