#!/usr/bin/env python3
"""Native train actor bridge; actor never receives gold or evaluator feedback.

Protected prompts/trajectories stay outside the repository. Exported summaries
contain hashes, counts and aggregate native checks only. This is a subagent
backbone experiment, not the complete original ACE learning system.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

AUTHOR_SHA = "9f3e92155345a9159f3a8b25abc334eeca05b545"
HERE = Path(__file__).resolve().parent
FORBIDDEN = {"ground_truth", "required_apis", "model_collection", "evaluate_task",
             "AppWorld", "Task", "expose_internals", "load_state", "world"}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def prepare(root, target):
    from appworld.task import load_task_ids
    ids = load_task_ids("train")
    # Only the public split manifest is read; no task, evaluator or output.
    freeze = {"protocol": "subagent_native_train_smoke_v2", "source_ref": AUTHOR_SHA,
        "selection": "first three IDs of unchanged native train manifest",
        "dataset": "train", "train_count": len(ids),
        "train_manifest_sha256": sha("\n".join(ids).encode()),
        "selected_task_hashes": [sha(x.encode()) for x in ids[:3]],
        "selected_generator_hashes": [sha(x.split("_")[0].encode()) for x in ids[:3]],
        "actors": 3, "fresh_worlds": True, "max_execute_requests_per_actor": 40,
        "environment_random_seed": 123, "code_timeout_seconds": 20,
        "actor_context": "native public task + author rendered generator demonstrations + initial playbook + own full receipts",
        "actor_ground_truth_loaded": False, "task_prior_or_feedback": False,
        "roles_executed": ["independent cold subagent actor"],
        "roles_not_executed": ["ACE reflector", "ACE curator", "learned playbook updates"],
        "grading": "unchanged author evaluate_task once, after actor termination; never returned to actor",
        "retries_or_task_replacement": False,
        "model": "inherited ChatGPT subagent backend; version/seed/token/billing not exposed",
        "interpretation": "exposed-train feasibility/diagnostic; no method comparison, novelty or generalization claim",
        "protected_content": "private local artifacts; only encrypted archive or metadata may be committed",
        "transport": "atomic local file mailbox; socket v1 aborted before actor actions",
        "implementation_sha256": {name: sha((HERE/name).read_bytes()) for name in
                                  ("native_actor_bridge.py", "actor_client.py")},
        "author_prompt_sha256": sha((root/"experiments/prompts/appworld_react_generator_prompt.txt").read_bytes()),
        "initial_playbook_sha256": sha((root/"experiments/playbooks/appworld_initial_playbook.txt").read_bytes())}
    if len(ids) < 3:
        raise ValueError("train manifest has fewer than three tasks")
    write_json(target, freeze)
    print(json.dumps({"status": "frozen", "selected": 3, "tasks_loaded": 0}))


def serve(root, freeze_path, index, mailbox, private_root, summary_path):
    from appworld import AppWorld
    from appworld.task import load_task_ids
    from jinja2 import Template
    from freezegun import api as clock
    freeze = json.loads(freeze_path.read_text())
    for name, expected in freeze["implementation_sha256"].items():
        if sha((HERE/name).read_bytes()) != expected:
            raise ValueError("frozen implementation mismatch: " + name)
    ids = load_task_ids("train")
    if sha("\n".join(ids).encode()) != freeze["train_manifest_sha256"]:
        raise ValueError("train manifest changed")
    task_id = ids[index]
    if sha(task_id.encode()) != freeze["selected_task_hashes"][index]:
        raise ValueError("task choice changed")
    private_root.mkdir(parents=True, exist_ok=True)
    events_path = private_root/f"events_{index}.jsonl"
    if events_path.exists() or summary_path.exists() or mailbox.exists():
        raise ValueError("refuse reuse/overwrite of this first-run world")
    experiment_name = f"oacr_subagent_train_smoke_v2_{index}"
    started = clock.real_perf_counter()
    world = AppWorld(task_id=task_id, experiment_name=experiment_name,
        load_ground_truth=False, random_seed=freeze["environment_random_seed"],
        max_interactions=freeze["max_execute_requests_per_actor"], timeout_seconds=20)
    template_path = root/"experiments/prompts/appworld_react_generator_prompt.txt"
    playbook_path = root/"experiments/playbooks/appworld_initial_playbook.txt"
    if sha(template_path.read_bytes()) != freeze["author_prompt_sha256"] or \
       sha(playbook_path.read_bytes()) != freeze["initial_playbook_sha256"]:
        raise ValueError("author prompt/playbook changed")
    # No required_apis read. The actual default public template has no such var.
    prompt = Template(template_path.read_text()).render(
        input_str=world.task.instruction, main_user=world.task.supervisor,
        app_descriptions=json.dumps([{"name":k,"description":v}
                                     for k,v in world.task.app_descriptions.items()], indent=1),
        playbook=playbook_path.read_text())
    (private_root/f"actor_prompt_{index}.txt").write_text(prompt)
    summaries, execute_requests, rejected = [], 0, 0
    finish_reason = "unresolved"
    chain = "0"*64

    def log_event(event):
        nonlocal chain
        event["previous_sha256"] = chain
        content = json.dumps(event, ensure_ascii=False, sort_keys=True)
        chain = sha(content.encode())
        with events_path.open("a") as stream:
            stream.write(content+"\n")

    log_event({"op": "start", "prompt": prompt})
    mailbox.mkdir(parents=True)
    os.chmod(mailbox, 0o700)
    if True:
        print(json.dumps({"status":"native_actor_ready", "index":index}), flush=True)
        done = False
        while not done:
            pending = sorted(mailbox.glob("*.request.json"))
            if not pending:
                time.sleep(0.05)
                continue
            request_path = pending[0]
            if True:
                try:
                    request = json.loads(request_path.read_text())
                    op = request.get("op")
                    if op == "start":
                        response = {"status":"actor_task", "index":index, "prompt":prompt,
                                    "max_execute_requests":40,
                                    "permitted_endpoint":"execute public apis in the persistent native REPL"}
                    elif op == "execute":
                        if execute_requests >= 40:
                            response = {"status":"budget_exhausted", "receipt":"40 execute requests consumed; send finish"}
                        else:
                            code = request["code"]
                            execute_requests += 1
                            before = len(world.requester.requests)
                            begin = clock.real_perf_counter()
                            tree = ast.parse(code)
                            forbidden = any((isinstance(n,ast.Name) and n.id in FORBIDDEN) or
                                            (isinstance(n,ast.Attribute) and n.attr in FORBIDDEN)
                                            for n in ast.walk(tree))
                            if forbidden:
                                rejected += 1
                                receipt = "Bridge rejected nonpublic backend/evaluator access."
                                native_executed = False
                            else:
                                receipt = world.execute(code)
                                native_executed = True
                            native_calls = len(world.requester.requests)-before
                            elapsed = clock.real_perf_counter()-begin
                            row = {"index":execute_requests, "code_sha256":sha(code.encode()),
                                   "receipt_sha256":sha(receipt.encode()), "receipt_bytes":len(receipt.encode()),
                                   "native_executed":native_executed, "native_api_calls":native_calls,
                                   "elapsed_seconds":elapsed,
                                   "execution_error":receipt.startswith("Execution failed")}
                            summaries.append(row)
                            log_event({"op":"execute", "code":code, "receipt":receipt, "metrics":row})
                            response = {"status":"native_receipt", "step":execute_requests,
                                        "receipt":receipt, "remaining_execute_requests":40-execute_requests}
                    elif op == "finish":
                        finish_reason = str(request.get("reason","actor_declared_finished"))
                        log_event({"op":"finish", "reason":finish_reason})
                        response = {"status":"actor_terminated", "grading_feedback":"withheld"}
                        done = True
                    else:
                        response = {"status":"bridge_error", "error":"unknown op"}
                except Exception as exc:
                    response = {"status":"bridge_error", "error_class":type(exc).__name__}
                    log_event({"op":"bridge_error", "error_class":type(exc).__name__})
                response_path = request_path.with_name(request_path.name.replace(".request.json", ".response.json"))
                temp_response = response_path.with_suffix(".tmp")
                temp_response.write_text(json.dumps(response,ensure_ascii=False))
                temp_response.rename(response_path)
                request_path.unlink()
    # Actor endpoint is closed before importing/calling private evaluation.
    (mailbox/"terminated.txt").write_text("Actor terminated; grading feedback withheld.\n")
    actor_seconds = clock.real_perf_counter()-started
    native_interactions = len(world.environment_io)
    native_calls = len(world.requester.requests)
    world.close()
    grade = {"status":"not_run"}
    from appworld.evaluator import evaluate_task
    try:
        tracker, _ = evaluate_task(task_id=task_id, experiment_name=experiment_name,
                                   suppress_errors=True, save_report=True)
        grade = {"status":"evaluated", "success":tracker.success,
                 "num_tests":tracker.num_tests, "pass_count":tracker.pass_count,
                 "fail_count":tracker.fail_count}
    except Exception as exc:
        grade = {"status":"evaluator_error", "class":type(exc).__name__}
    result = {"protocol":freeze["protocol"], "index":index,
        "task_id_sha256":sha(task_id.encode()),
        "generator_sha256":freeze["selected_generator_hashes"][index],
        "actor_terminated":True, "finish_reason":finish_reason,
        "actor_ground_truth_loaded":False, "actor_evaluator_feedback":False,
        "execute_requests":execute_requests, "native_interactions":native_interactions,
        "native_api_calls":native_calls, "bridge_rejections":rejected,
        "actor_elapsed_seconds":actor_seconds, "steps":summaries, "grade":grade,
        "events_sha256":sha(events_path.read_bytes()), "events_chain_final_sha256":chain,
        "prompt_sha256":sha(prompt.encode()), "prompt_bytes":len(prompt.encode()),
        "external_provider_model_calls":0, "subagent_model_usage":"nonzero; token/billing not exposed",
        "interpretation":"subagent-native exposed-train smoke; not complete ACE or OCAR advantage"}
    write_json(summary_path,result)
    print(json.dumps({"status":"actor_run_complete", "index":index,
                      "success":grade.get("success"), "native_interactions":native_interactions}),flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root",type=Path,required=True)
    parser.add_argument("--freeze",type=Path,required=True)
    parser.add_argument("--prepare",action="store_true")
    parser.add_argument("--index",type=int,choices=range(3))
    parser.add_argument("--mailbox",type=Path)
    parser.add_argument("--private-root",type=Path)
    parser.add_argument("--summary",type=Path)
    args = parser.parse_args()
    root = args.source_root.resolve()
    actual = subprocess.check_output(["git","rev-parse","HEAD"],cwd=root,text=True).strip()
    if actual != AUTHOR_SHA:
        parser.error("author source HEAD differs from freeze")
    os.environ["APPWORLD_PROJECT_PATH"] = str(root)
    from appworld.common.path_store import path_store
    path_store.update_root(str(root))
    if args.prepare:
        prepare(root,args.freeze)
    else:
        if any(x is None for x in (args.index,args.mailbox,args.private_root,args.summary)):
            parser.error("serve requires index/mailbox/private-root/summary")
        serve(root,args.freeze,args.index,args.mailbox,args.private_root,args.summary)


if __name__ == "__main__":
    main()
