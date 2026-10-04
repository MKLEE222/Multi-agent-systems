#!/usr/bin/env python3
"""Post-runtime controller adjudication; no task restart or action replay.

The original producer events remain byte-for-byte unchanged. A single unchanged
author grade reads its saved prefix only after the dead endpoint is marked closed.
Elapsed wall/model cost and complete native state are not inferred from logs.
"""
from __future__ import annotations
import argparse
from contextlib import redirect_stderr, redirect_stdout
import hashlib
import importlib.util
import json
from pathlib import Path
import traceback


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--index", type=int, choices=[10, 11, 12], required=True)
    args = p.parse_args()
    here = Path(__file__).resolve().parent
    root = here.parents[1].parent
    private = root / "ocar_moe_runtime/residual_dev24_recovery_private"
    source = root / "ocar_moe_runtime/ace_appworld"
    result = here / "recovery" / f"task_{args.index}_summary.json"
    if result.exists():
        raise FileExistsError("refuse grade or summary retry")
    freeze_path = here / "recovery/freeze.json"
    frozen = json.loads(freeze_path.read_text())
    mapping = json.loads((private / "selection_mapping.json").read_text())["selection"]
    original_events = private / f"events_{args.index}.jsonl"
    raw = original_events.read_bytes()
    events = [json.loads(line) for line in raw.decode().splitlines()]
    if any(e["op"] == "grade" for e in events):
        raise RuntimeError("an original grade exists")
    chain = "0" * 64
    for sequence, event in enumerate(events, 1):
        assert event["sequence"] == sequence and event["previous_sha256"] == chain
        chain = sha(json.dumps(event, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode())
    # The controller first independently verifies that no old process exists.
    marker = private / f"mailbox_{args.index}/terminated.txt"
    marker.write_text("Endpoint closed after workspace resource interruption; grading feedback withheld.\n")
    prompt = next(e["prompt"] for e in events if e["op"] == "ready")
    steps = [e["metrics"] for e in events if e["op"] == "execute"]
    responses = [e["response"] for e in events if e["op"] == "response"]
    requests = [e["request"] for e in events if e["op"] == "request" and "request" in e]
    delivered = 0
    for r in responses:
        if "prompt" in r and r["offset"] <= delivered:
            delivered = max(delivered, r["offset"] + len(r["prompt"]))
    last_elapsed = max((e.get("actor_elapsed_seconds") or 0 for e in events), default=0)
    grade = {"status": "evaluator_error", "attempts": 1, "scope": "saved_prefix_after_workspace_runtime_interruption"}
    spec = importlib.util.spec_from_file_location("frozen_controller", here / "native_batch_bridge.py")
    bridge = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bridge)
    assert bridge.source_head(source) == frozen["source_ref"]
    grade_log = private / f"interruption_grade_{args.index}.log"
    with grade_log.open("x") as stream:
        try:
            with bridge.grade_deadline(), redirect_stdout(stream), redirect_stderr(stream):
                from appworld.common.path_store import path_store
                path_store.update_root(str(source))
                from appworld.evaluator import evaluate_task
                tracker, _ = evaluate_task(task_id=mapping[args.index]["task_id"],
                    experiment_name=f"{frozen['protocol']}_{args.index}",
                    suppress_errors=True, save_report=True)
            grade.update(status="evaluated", success=tracker.success, num_tests=tracker.num_tests,
                         pass_count=tracker.pass_count, fail_count=tracker.fail_count)
        except BaseException as exc:
            grade["error_class"] = type(exc).__name__
            stream.write(traceback.format_exc())
    adjudication = {"index": args.index, "reason": "workspace_credit_error_and_worker_process_loss",
                    "original_events_sha256": sha(raw), "endpoint_closed_before_grade": True,
                    "action_replay": False, "world_restart": False, "grade": grade}
    record = private / f"interruption_adjudication_{args.index}.json"
    record.write_text(json.dumps(adjudication, indent=2) + "\n")
    row = {"protocol": frozen["protocol"], "index": args.index, "batch_denominator": 24,
           "task_id_sha256": frozen["selected_task_hashes"][args.index],
           "family_sha256": frozen["selected_family_hashes"][args.index],
           "manifest_index": frozen["selected_manifest_indices"][args.index],
           "actor_started": True, "actor_terminated": True,
           "finish_reason": "workspace_resource_interruption", "actor_finish_reason": None,
           "native_task_completed": None, "controller_error_class": "ExternalWorkerLoss",
           "actor_ground_truth_loaded": False, "actor_evaluator_feedback": False,
           "oacr_intervention": False, "execute_requests": len(steps),
           "native_execute_attempts": sum(s["native_executed"] for s in steps),
           "native_interactions": sum(s["native_interactions_delta"] for s in steps),
           "native_api_calls": sum(s["native_api_calls"] for s in steps),
           "bridge_rejections": sum(s["ast_rejection"] for s in steps),
           "parse_errors": sum(s["parse_error"] for s in steps),
           "native_execution_errors": sum(s["execution_error"] for s in steps),
           "generated_receipt_bytes": sum(s["receipt_bytes"] for s in steps),
           "generated_native_receipt_bytes": sum(s["receipt_bytes"] for s in steps if s["receipt_source"] == "native"),
           "generated_bridge_receipt_bytes": sum(s["receipt_bytes"] for s in steps if s["receipt_source"] != "native"),
           "prompt_bytes": len(prompt.encode()), "prompt_sha256": sha(prompt.encode()),
           "transport_prompt_text_bytes": sum(len(r["prompt"].encode()) for r in responses if "prompt" in r),
           "transport_receipt_text_bytes": sum(len(r["receipt"].encode()) for r in responses if "receipt" in r),
           "prompt_page_requests": sum(r["op"] == "start" for r in requests),
           "receipt_page_requests": sum(r["op"] == "receipt_page" for r in requests),
           "complete_prompt_delivered": delivered == len(prompt),
           "actor_elapsed_seconds": None, "observed_actor_elapsed_lower_bound_seconds": last_elapsed,
           "actor_actual_visible_bytes": None, "mailbox_response_bytes": None,
           "steps": steps, "grade": grade, "events_sha256": sha(raw),
           "events_chain_final_sha256": chain, "events_count": len(events),
           "freeze_sha256": sha(freeze_path.read_bytes()), "external_provider_model_calls": 0,
           "actor_invocations": 1, "subagent_model_calls": None,
           "subagent_model_tokens": None, "subagent_model_cost": None,
           "posthoc_controller_adjudication": True, "adjudication_sha256": sha(record.read_bytes()),
           "temporal_and_native_costs_complete": False,
           "interpretation": "Interrupted prefix retained; not a completed actor trajectory, actor failure mechanism or independent residual."}
    row["high_cost_flags"] = {k: (row[k] >= threshold if row[k] is not None else None)
                              for k, threshold in frozen["high_cost_thresholds"].items()}
    row["high_cost_screen_triggered"] = any(v is True for v in row["high_cost_flags"].values())
    result.write_text(json.dumps(row, indent=2) + "\n")
    print(json.dumps({"index": args.index, "scope": grade["scope"], "grade_status": grade["status"],
                      "task_restarted": False, "execute_prefix_requests": len(steps)}))


if __name__ == "__main__":
    main()
