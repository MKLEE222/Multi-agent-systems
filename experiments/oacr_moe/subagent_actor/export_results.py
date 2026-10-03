#!/usr/bin/env python3
"""Audit all fixed actor attempts and encrypt protected native traces for sharing."""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
from pathlib import Path


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root",type=Path,required=True)
    parser.add_argument("--private-root",type=Path,required=True)
    parser.add_argument("--result-root",type=Path,required=True)
    args = parser.parse_args()
    freeze = json.loads((args.result_root/"freeze.json").read_text())
    rows = [json.loads((args.result_root/f"task_{i}_summary.json").read_text()) for i in range(3)]
    for i, row in enumerate(rows):
        assert row["task_id_sha256"] == freeze["selected_task_hashes"][i]
        events_path = args.private_root/f"events_{i}.jsonl"
        events = [json.loads(line) for line in events_path.read_text().splitlines()]
        chain = "0"*64
        for event in events:
            assert event["previous_sha256"] == chain
            chain = digest(json.dumps(event,ensure_ascii=False,sort_keys=True).encode())
        assert events[-1]["op"] == "finish" and row["actor_terminated"]
        assert chain == row["events_chain_final_sha256"]
        assert digest(events_path.read_bytes()) == row["events_sha256"]
        calls = [event for event in events if event["op"] == "execute"]
        assert len(calls) == row["execute_requests"] == row["native_interactions"]
        assert sum(x["metrics"]["native_api_calls"] for x in calls) == row["native_api_calls"]
        assert not row["actor_ground_truth_loaded"] and not row["actor_evaluator_feedback"]
        assert row["grade"]["status"] == "evaluated"
    # Preserve private task mapping only inside the encrypted archive.
    from appworld.common.path_store import path_store
    path_store.update_root(str(args.source_root.resolve()))
    from appworld.task import load_task_ids
    selected = load_task_ids("train")[:3]
    (args.private_root/"task_mapping.json").write_text(json.dumps(selected))
    from appworld.common.utils import pack_bundle, unpack_bundle
    from appworld.common.constants import PASSWORD, SALT
    bundle = args.private_root.parent/"subagent_train_traces.bundle"
    packed = pack_bundle(str(bundle),str(args.private_root.parent),
        include_directories=[args.private_root.name],password=PASSWORD,salt=SALT)
    bundle_bytes = bundle.read_bytes()
    (args.result_root/"protected_traces.bundle.b64").write_text(base64.b64encode(bundle_bytes).decode()+"\n")
    # Verify archive integrity without exposing decoded protected content.
    unpack_root = args.private_root.parent/"archive_verification"
    unpack_bundle(str(bundle),str(unpack_root),password=PASSWORD,salt=SALT)
    for i,row in enumerate(rows):
        restored = unpack_root/args.private_root.name/f"events_{i}.jsonl"
        assert digest(restored.read_bytes()) == row["events_sha256"]
    result = {"protocol":freeze["protocol"], "tasks":3,
        "task_successes":sum(r["grade"]["success"] for r in rows),
        "distinct_scenarios":len(set(freeze["selected_generator_hashes"])),
        "native_tests_passed":sum(r["grade"]["pass_count"] for r in rows),
        "native_tests_total":sum(r["grade"]["num_tests"] for r in rows),
        "execute_requests":sum(r["execute_requests"] for r in rows),
        "native_api_calls":sum(r["native_api_calls"] for r in rows),
        "native_execution_errors":sum(s["execution_error"] for r in rows for s in r["steps"]),
        "bridge_rejections":sum(r["bridge_rejections"] for r in rows),
        "native_evaluator_invocations":3, "actor_evaluator_feedback":False,
        "initial_prompt_bytes":sum(r["prompt_bytes"] for r in rows),
        "receipt_bytes":sum(s["receipt_bytes"] for r in rows for s in r["steps"]),
        "external_provider_api_model_calls":0,
        "subagent_model_usage":"nonzero; model version/seed/token/billing not exposed",
        "complete_ACE_roles_executed":False, "method_comparison":False,
        "OCAR_advantage_claim":False, "evaluation_bank_512_used":False,
        "retry_after_grading":False, "source_ref":freeze["source_ref"],
        "archive":{"format":"author AppWorld encrypted .bundle encoded as base64 text",
                   "packed_files":len(packed),"bundle_bytes":len(bundle_bytes),
                   "bundle_sha256":digest(bundle_bytes),"restored_event_hashes_match":True,
                   "uploaded_to_github":False,
                   "upload_status":"local only; protected trace disclosure not explicitly authorized"},
        "interpretation":"same-scenario exposed-train native execution feasibility; not test TGC/SGC or independent generalization"}
    (args.result_root/"RESULT_2026-10-02.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({k:result[k] for k in ("tasks","task_successes","native_tests_passed",
        "native_tests_total","execute_requests","native_api_calls","native_execution_errors","receipt_bytes")}))


if __name__ == "__main__":
    main()
