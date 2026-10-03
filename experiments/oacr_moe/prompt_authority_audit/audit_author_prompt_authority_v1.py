#!/usr/bin/env python3
"""Audit public author templates with synthetic sentinels and intercepted transports.

No benchmark task, database, answer, evaluator, model, or actual generated prompt
is loaded or executed. Raw templates and rendered message contents are not saved.
Original initialize/reflector/curator methods are AST-selected from pinned public
source. A curator transport interception stops execution before any file writes.
"""
from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import importlib.metadata
import json
import os
import re
import string
from pathlib import Path
from types import SimpleNamespace

import _jsonnet
from jinja2 import Environment, Template, meta


SOURCE_REF = "9f3e92155345a9159f3a8b25abc334eeca05b545"
CONFIG_NAMES = [
    "ACE_offline_no_GT_adaptation", "ACE_offline_no_GT_evaluation",
    "ACE_offline_with_GT_adaptation", "ACE_offline_with_GT_evaluation",
    "ACE_online_no_GT",
]


def digest(value) -> str:
    if not isinstance(value, bytes):
        value = json.dumps(value, sort_keys=True, ensure_ascii=False).encode()
    return hashlib.sha256(value).hexdigest()


class AccessTrackedGroundTruth:
    def __init__(self, marker: str):
        self.marker, self.required_api_reads = marker, 0

    @property
    def required_apis(self):
        self.required_api_reads += 1
        return [self.marker]


class NullLogger:
    def show_message(self, **kwargs):
        pass


class InertBase:
    def initialize(self, world):
        self.world = world
        self.messages = []


class TransportCaptured(Exception):
    """Expected stop at the transport boundary; no network/model invocation."""


class RecordingTransport:
    def __init__(self, *, stop=False):
        self.messages, self.calls, self.stop = None, 0, stop

    def generate(self, *, messages):
        self.messages = copy.deepcopy(messages)
        self.calls += 1
        if self.stop:
            raise TransportCaptured()
        return {"content": "SYNTHETIC_REFLECTOR_RETURN_SENTINEL", "cost": 0}


def author_class(root: Path, *, adaptation: bool):
    file = "adaptation_react.py" if adaptation else "evaluation_react.py"
    name = "SimplifiedReActStarAgent" if adaptation else "SimplifiedReActAgent"
    path = root / "experiments/code/ace" / file
    tree = ast.parse(path.read_text())
    original = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == name)
    methods = {"initialize", "truncate_input", "text_to_messages", "messages_to_text", "trimmed_messages"}
    if adaptation:
        methods.update({"reflector_call", "curator_call"})
    body = [node for node in original.body if isinstance(node, ast.FunctionDef) and node.name in methods]
    if {node.name for node in body} != methods:
        raise ValueError("Author method selection incomplete")
    selected = ast.ClassDef(name=name, bases=[ast.Name(id="InertBase", ctx=ast.Load())],
                            keywords=[], body=copy.deepcopy(body), decorator_list=[])
    module = ast.fix_missing_locations(ast.Module(body=[selected], type_ignores=[]))
    env = {"InertBase": InertBase, "Template": Template, "AppWorld": object,
           "copy": copy, "json": json, "os": os, "re": re}
    exec(compile(module, str(path), "exec"), env)
    return env[name]


def initialized_agent(cls, template: str, api_marker: str):
    agent = cls.__new__(cls)
    agent.generator_prompt_template = template.lstrip()
    agent.max_prompt_length = None
    agent.max_output_length = 400000
    agent.playbook = "SYNTHETIC_PLAYBOOK_SENTINEL"
    agent.logger = NullLogger()
    agent.step_number = 1
    gt = AccessTrackedGroundTruth(api_marker)
    world = SimpleNamespace(task=SimpleNamespace(
        instruction="SYNTHETIC_TASK_INSTRUCTION_WITHOUT_BENCHMARK_CONTENT",
        supervisor={"name": "SYNTHETIC_SUPERVISOR"},
        app_descriptions={"synthetic_app": "SYNTHETIC_APP_DESCRIPTION"}, ground_truth=gt))
    agent.initialize(world)
    return agent, gt


def append_synthetic_history(agent, marker="SYNTHETIC_VISIBLE_EXECUTION_A"):
    agent.messages.extend([
        {"role": "assistant", "content": "SYNTHETIC_CODE_NO_EXECUTION"},
        {"role": "user", "content": "Output:\n```\n" + marker + "\n```\n\n"},
    ])


def capture_feedback(agent, reflector: str, curator: str, report_marker: str,
                     solution_marker: str, history_marker: str):
    agent.reflector_prompt = reflector
    agent.curator_prompt = curator
    agent.test_report = report_marker
    agent.world_gt_code = solution_marker
    agent.use_reflector = True
    agent.reflector_model = RecordingTransport()
    agent.curator_model = RecordingTransport(stop=True)
    append_synthetic_history(agent, history_marker)
    stopped = False
    try:
        agent.curator_call()
    except TransportCaptured:
        stopped = True
    assert stopped and agent.reflector_model.calls == 1 and agent.curator_model.calls == 1
    return {"reflector": agent.reflector_model.messages, "curator": agent.curator_model.messages,
            "expected_transport_stop": stopped}


def inspect_feedback_control_flow(root: Path) -> dict:
    path = root / "experiments/code/ace/adaptation_agent.py"
    tree = ast.parse(path.read_text())
    cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "StarAgent")
    method = next(node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name == "solve_task_wo_gt")
    evaluator_assignments, curator_calls, report_loads, test_tracker_loads = [], [], [], []
    for node in ast.walk(method):
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
            call = node.value.func
            if isinstance(call, ast.Name) and call.id == "evaluate_task":
                evaluator_assignments.append(node.lineno)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "curator_call":
            curator_calls.append(node.lineno)
        if isinstance(node, ast.Attribute) and node.attr == "test_report" and isinstance(node.ctx, ast.Load):
            report_loads.append(node.lineno)
        if isinstance(node, ast.Name) and node.id == "test_tracker" and isinstance(node.ctx, ast.Load):
            test_tracker_loads.append(node.lineno)
    return {"method": "StarAgent.solve_task_wo_gt", "evaluator_assignment_lines": evaluator_assignments,
            "curator_call_lines": curator_calls, "report_loads_in_execution_loop": report_loads,
            "test_tracker_loads_in_execution_loop": test_tracker_loads,
            "evaluator_runs_before_curator": bool(evaluator_assignments and curator_calls and
                min(evaluator_assignments) < min(curator_calls)),
            "stop_condition": "world.task_completed() or cost_tracker.exceeded(); not test_tracker.failures",
            "native_loop_not_executed": True}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--manifest", type=Path,
        default=Path(__file__).resolve().parents[1] / "baseline_capsule/author_ace_manifest_v1.json")
    args = parser.parse_args()
    root = args.source_root.resolve()
    manifest = json.loads(args.manifest.read_text())
    assert manifest["source_ref"] == SOURCE_REF
    expected = {item["path"]: item for item in manifest["files"]}
    result = {"source_repository": "ace-agent/ace-appworld", "source_ref": SOURCE_REF,
              "scope": "public-source template authority audit; only synthetic render variables/history",
              "runtime_versions": {name: importlib.metadata.version(name) for name in ("Jinja2", "jsonnet")},
              "source_hashes": [], "configs": [], "errors": [], "model_calls": 0,
              "benchmark_tasks_read": 0, "gold_answers_read": 0, "native_executions": 0,
              "raw_prompt_contents_persisted": False,
              "old_frozen_preflight_modified": False}
    used_paths = set()
    for config_name in CONFIG_NAMES:
        relative = f"experiments/configs/{config_name}.jsonnet"
        used_paths.add(relative)
        try:
            compiled = json.loads(_jsonnet.evaluate_file(str(root / relative),
                                 ext_vars={"APPWORLD_PROJECT_PATH": str(root)}))
            config, agent_config = compiled["config"], compiled["config"]["agent"]
            adaptation = config["run_type"] == "ace-adaptation"
            cls = author_class(root, adaptation=adaptation)
            template_path = Path(agent_config["generator_prompt_file_path"])
            used_paths.add(str(template_path.relative_to(root)))
            template = template_path.read_text()
            undeclared = sorted(meta.find_undeclared_variables(Environment().parse(template)))
            a, ga = initialized_agent(cls, template, "SYNTHETIC_REQUIRED_APIS_A")
            b, gb = initialized_agent(cls, template, "SYNTHETIC_REQUIRED_APIS_B")
            first_generator_a, first_generator_b = a.trimmed_messages, b.trimmed_messages
            message_a = json.dumps(a.messages, ensure_ascii=False)
            message_b = json.dumps(b.messages, ensure_ascii=False)
            api_enters = "SYNTHETIC_REQUIRED_APIS_A" in message_a or "SYNTHETIC_REQUIRED_APIS_B" in message_b
            record = {"config": config_name, "dataset_name_from_public_config": config.get("dataset"),
                      "run_type": config["run_type"], "agent_type": agent_config["type"],
                      "use_gt_code": agent_config.get("use_gt_code", False),
                      "generator_template": str(template_path.relative_to(root)),
                      "jinja_undeclared_variables": undeclared,
                      "source_reads_required_apis": ga.required_api_reads == gb.required_api_reads == 1,
                      "required_apis_in_rendered_actor_messages": api_enters,
                      "actor_messages_equal_after_only_required_apis_change": a.messages == b.messages,
                      "first_generator_input_equal_after_only_required_apis_change": first_generator_a == first_generator_b,
                      "required_apis_in_first_generator_input": "SYNTHETIC_REQUIRED_APIS_A" in json.dumps(first_generator_a),
                      "actor_message_sha256_pair": [digest(a.messages), digest(b.messages)],
                      "actor_message_count": len(a.messages),
                      "instruction_sentinel_present": "SYNTHETIC_TASK_INSTRUCTION_WITHOUT_BENCHMARK_CONTENT" in message_a,
                      "benchmark_task_loaded": False}
            assert ga.required_api_reads == gb.required_api_reads == 1
            assert not api_enters and a.messages == b.messages
            assert first_generator_a == first_generator_b
            assert "SYNTHETIC_REQUIRED_APIS_A" not in json.dumps(first_generator_a)
            assert "relevant_apis" not in undeclared
            if adaptation:
                reflector_path = Path(agent_config["reflector_prompt_file_path"])
                curator_path = Path(agent_config["curator_prompt_file_path"])
                used_paths.update([str(reflector_path.relative_to(root)), str(curator_path.relative_to(root))])
                reflector, curator = reflector_path.read_text(), curator_path.read_text()
                def run(report, solution, history):
                    agent, _ = initialized_agent(cls, template, "SYNTHETIC_REQUIRED_APIS_A")
                    return capture_feedback(agent, reflector, curator, report, solution, history)
                fixed = run("SYNTHETIC_EVALUATOR_REPORT_A", "SYNTHETIC_COMPILED_SOLUTION_A", "SYNTHETIC_VISIBLE_EXECUTION_A")
                changed_report = run("SYNTHETIC_EVALUATOR_REPORT_B", "SYNTHETIC_COMPILED_SOLUTION_A", "SYNTHETIC_VISIBLE_EXECUTION_A")
                changed_solution = run("SYNTHETIC_EVALUATOR_REPORT_A", "SYNTHETIC_COMPILED_SOLUTION_B", "SYNTHETIC_VISIBLE_EXECUTION_A")
                changed_history = run("SYNTHETIC_EVALUATOR_REPORT_A", "SYNTHETIC_COMPILED_SOLUTION_A", "SYNTHETIC_VISIBLE_EXECUTION_B")
                feedback = {"reflector_template": str(reflector_path.relative_to(root)),
                    "curator_template": str(curator_path.relative_to(root)),
                    "reflector_replace_target_counts": {key: reflector.count("{{" + key + "}}")
                        for key in ("test_report", "ground_truth_code", "execution_error")},
                    "curator_format_fields": sorted({field for _, field, _, _ in string.Formatter().parse(curator) if field}),
                    "evaluator_report_in_reflector_input": "SYNTHETIC_EVALUATOR_REPORT_A" in json.dumps(fixed["reflector"]),
                    "evaluator_report_in_curator_input": "SYNTHETIC_EVALUATOR_REPORT_A" in json.dumps(fixed["curator"]),
                    "report_change_affects_reflector_input": fixed["reflector"] != changed_report["reflector"],
                    "report_change_affects_curator_input_with_constant_synthetic_reflector_reply": fixed["curator"] != changed_report["curator"],
                    "compiled_solution_in_reflector_input": "SYNTHETIC_COMPILED_SOLUTION_A" in json.dumps(fixed["reflector"]),
                    "solution_change_affects_reflector_input": fixed["reflector"] != changed_solution["reflector"],
                    "solution_change_affects_curator_input_with_constant_synthetic_reflector_reply": fixed["curator"] != changed_solution["curator"],
                    "visible_history_change_affects_reflector_input": fixed["reflector"] != changed_history["reflector"],
                    "visible_history_change_affects_curator_input": fixed["curator"] != changed_history["curator"],
                    "no_model_request": True, "stop_before_curator_parse_or_playbook_write": fixed["expected_transport_stop"],
                    "boundary": "author methods and templates; inert superclass; synthetic world/history; intercepted transports",
                    "feedback_inputs_sha256": {"reflector": digest(fixed["reflector"]), "curator": digest(fixed["curator"])}}
                if agent_config.get("use_gt_code", False):
                    assert feedback["evaluator_report_in_reflector_input"] and feedback["compiled_solution_in_reflector_input"]
                    assert feedback["report_change_affects_reflector_input"] and feedback["solution_change_affects_reflector_input"]
                else:
                    assert not feedback["evaluator_report_in_reflector_input"] and not feedback["evaluator_report_in_curator_input"]
                    assert not feedback["compiled_solution_in_reflector_input"]
                    assert not feedback["report_change_affects_reflector_input"]
                    assert not feedback["report_change_affects_curator_input_with_constant_synthetic_reflector_reply"]
                assert feedback["visible_history_change_affects_reflector_input"] and feedback["visible_history_change_affects_curator_input"]
                record["feedback_render_audit"] = feedback
            result["configs"].append(record)
        except Exception as exc:
            result["errors"].append({"config": config_name, "class": type(exc).__name__,
                                     "message": "not saved: exceptions can contain raw template text"})
    used_paths.update("experiments/code/ace/" + name for name in
                      ("adaptation_react.py", "evaluation_react.py", "adaptation_agent.py"))
    for relative in sorted(used_paths):
        data = (root / relative).read_bytes()
        blob = hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()
        valid = relative in expected and blob == expected[relative]["git_blob_sha"] and len(data) == expected[relative]["size"]
        result["source_hashes"].append({"path": relative, "bytes": len(data),
                                      "git_blob_sha": blob, "exact_source_match": valid})
        if not valid:
            result["errors"].append({"path": relative, "class": "SourceProvenanceMismatch"})
    result["no_gt_feedback_control_flow"] = inspect_feedback_control_flow(root)
    result["passed"] = len(result["configs"]) == 5 and not result["errors"]
    result["correction"] = {"source_field_read_is_not_rendered_authority": True,
                            "default_generator_has_no_required_api_prior": result["passed"],
                            "default_no_gt_reflector_has_no_evaluator_report_content": result["passed"],
                            "with_gt_reflector_does_render_report_and_compiled_solution": result["passed"],
                            "native_no_gt_evaluator_call_still_occurs": True}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"passed": result["passed"], "configs": len(result["configs"]),
                      "source_files": len(result["source_hashes"]), "errors": len(result["errors"]),
                      "model_calls": 0, "benchmark_tasks_read": 0,
                      "default_required_api_prior": False,
                      "default_no_gt_report_in_reflector": False, "output": str(args.output)}))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
