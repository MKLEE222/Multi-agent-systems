#!/usr/bin/env python3
"""Inspect and execute author ACE runner interfaces without invoking a model.

This is a provenance/configuration/interface check, not an ACE task evaluation.
The pinned author source stays outside this repository. No task, gold answer,
database, test report, or credential value is read or copied by this program.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import json
import os
import re
import sys
import tomllib
from pathlib import Path
from types import SimpleNamespace


def blob_sha(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def extract_functions(path: Path, names: list[str], env: dict) -> dict:
    tree = ast.parse(path.read_text())
    nodes = [node for node in tree.body
             if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
             and node.name in names]
    if {node.name for node in nodes} != set(names):
        raise ValueError(f"Missing author functions in {path.name}")
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), "exec"), env)
    return env


def exercise_author_runner(root: Path) -> dict:
    """Run unmodified author's run_experiment function with inert boundary doubles."""
    loaded, solved = [], []
    class TaskDouble:
        @staticmethod
        def load(*, task_id):
            loaded.append(task_id)
    class AgentDouble:
        def __init__(self, kind):
            self.kind = kind
        def from_dict(self, config):
            self.config = dict(config)
            return self
        def solve_tasks(self, **kwargs):
            solved.append({"kind": self.kind, "config": self.config, **kwargs})
    def load_ids(dataset):
        if dataset != "train":
            raise AssertionError("This interface check must never request a test split")
        return ["INTERFACE_TRAIN_0", "INTERFACE_TRAIN_1", "INTERFACE_TRAIN_2"]
    env = {"Any": object, "Task": TaskDouble, "load_task_ids": load_ids,
           "StarAgent": AgentDouble("adaptation"), "Agent": AgentDouble("evaluation"),
           "BaseAgent": AgentDouble("non-ace")}
    extract_functions(root / "experiments/code/ace/run.py", ["run_experiment"], env)
    for run_type, expected in [("ace-adaptation", "adaptation"),
                               ("ace-evaluation", "evaluation"),
                               ("non-ace-evaluation", "non-ace")]:
        config = {"run_type": run_type, "agent": {"marker": "no-model"},
                  "dataset": "train", "sample_size": 2, "num_epochs": 2}
        env["run_experiment"]("INTERFACE_ONLY", config)
        assert solved[-1]["kind"] == expected
        assert solved[-1]["task_ids"] == ["INTERFACE_TRAIN_0", "INTERFACE_TRAIN_1"] * 2
    assert len(loaded) == 6
    return {"passed": True, "branches": 3, "task_loader_calls": len(loaded),
            "native_tasks_executed": 0, "model_calls": 0,
            "boundary": "author function; inert synthetic loader and agent doubles"}


def exercise_author_merge(root: Path) -> dict:
    """Execute original deterministic merge, without fabricating model output quality."""
    env = {"re": re, "json": json}
    extract_functions(root / "experiments/code/ace/utils.py", ["get_section_slug"], env)
    extract_functions(root / "experiments/code/ace/playbook.py",
                      ["parse_playbook_line", "get_next_global_id", "format_playbook_line",
                       "apply_curator_operations"], env)
    text = (root / "experiments/playbooks/appworld_initial_playbook.txt").read_text()
    section = next(line[2:].strip() for line in text.splitlines() if line.startswith("##"))
    initial = env["get_next_global_id"](text)
    # A generic interface sentinel; no AppWorld app/task-specific material.
    sentinel = "OACR_INTERFACE_SENTINEL_DO_NOT_TREAT_AS_LEARNED_EXPERIENCE"
    new, next_id = env["apply_curator_operations"](
        text, [{"type": "ADD", "section": section, "content": sentinel}], initial)
    before = [env["parse_playbook_line"](line) for line in text.splitlines()]
    before = [item for item in before if item]
    after = [env["parse_playbook_line"](line) for line in new.splitlines()]
    after = {item["id"]: item["content"] for item in after if item}
    assert all(after.get(item["id"]) == item["content"] for item in before)
    assert sentinel in new and next_id == initial + 1
    return {"passed": True, "old_bullets_preserved": len(before), "delta_additions": 1,
            "model_calls": 0, "not_a_learned_playbook": True}


def inspect_configs(root: Path) -> list[dict]:
    try:
        import _jsonnet
    except ImportError as exc:
        raise RuntimeError("Install the 6.5 MB preflight-only dependency jsonnet==0.21.0") from exc
    records = []
    for path in sorted((root / "experiments/configs").glob("ACE*.jsonnet")):
        compiled = json.loads(_jsonnet.evaluate_file(
            str(path), ext_vars={"APPWORLD_PROJECT_PATH": str(root)}))
        config, model_roles = compiled["config"], {}
        agent = config["agent"]
        for role in ("generator", "reflector", "curator"):
            if role + "_model_config" in agent:
                model = agent[role + "_model_config"]
                # Explicit allowlist prevents accidental credential disclosure.
                model_roles[role] = {key: model.get(key) for key in
                    ("name", "provider", "temperature", "seed", "use_cache", "max_retries")}
        path_checks = []
        for key, value in agent.items():
            if not key.endswith("file_path"):
                continue
            file = Path(value)
            is_output = key == "trained_playbook_file_path" and config["run_type"] == "ace-adaptation"
            path_checks.append({"field": key, "relative_path": str(file.relative_to(root)),
                                "kind": "output" if is_output else "input",
                                "exists": file.exists(),
                                "bytes": file.stat().st_size if file.exists() else None,
                                "required_input_ready": is_output or (file.exists() and file.stat().st_size > 0)})
        records.append({"config": path.name, "dataset": config.get("dataset"),
                        "run_type": config["run_type"], "agent_type": agent["type"],
                        "num_epochs": config.get("num_epochs", 1),
                        "use_gt_code": agent.get("use_gt_code", False),
                        "max_steps": agent.get("max_steps"), "model_roles": model_roles,
                        "paths": path_checks})
    return records


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--manifest", type=Path,
                        default=Path(__file__).with_name("author_ace_manifest_v1.json"))
    parser.add_argument("--require-model", action="store_true",
                        help="Fail with code 2 if original SambaNova model authorization is absent")
    args = parser.parse_args()
    root = args.source_root.resolve()
    manifest = json.loads(args.manifest.read_text())
    report = {"scope": "author source/config/runner preflight; not native task or model evaluation",
              "source_repository": manifest["source_repository"],
              "source_ref": manifest["source_ref"], "checks": {}, "errors": []}
    syntax, hashes, source_credential_literals = [], [], 0
    for item in manifest["files"]:
        path = root / item["path"]
        if not path.exists():
            report["errors"].append({"path": item["path"], "error": "missing"})
            continue
        data = path.read_bytes()
        ok = len(data) == item["size"] and blob_sha(data) == item["git_blob_sha"]
        hashes.append({"path": item["path"], "exact_git_blob_match": ok,
                       "sha256": hashlib.sha256(data).hexdigest()})
        if not ok:
            report["errors"].append({"path": item["path"], "error": "provenance mismatch"})
        if path.suffix == ".py":
            try:
                tree = ast.parse(data.decode())
                syntax.append(item["path"])
                for node in ast.walk(tree):
                    if isinstance(node, ast.keyword) and node.arg == "api_key" and isinstance(node.value, ast.Constant):
                        value = node.value.value
                        if isinstance(value, str) and value not in ("", "EMPTY", "your_key"):
                            source_credential_literals += 1
            except (SyntaxError, UnicodeError) as exc:
                report["errors"].append({"path": item["path"], "error": type(exc).__name__})
    report["checks"]["source_hashes"] = hashes
    report["checks"]["python_syntax"] = {"parsed_files": len(syntax)}
    report["checks"]["source_credential_literals"] = {
        "count": source_credential_literals, "values": "redacted; never used or printed"}
    version = tomllib.loads((root / "pyproject.toml").read_text())["project"]["version"]
    report["checks"]["appworld_version"] = {"observed": version, "expected": "0.1.4.dev0",
        "passed": version == "0.1.4.dev0", "not_current_0_2": True}
    if version != "0.1.4.dev0":
        report["errors"].append({"error": "wrong AppWorld version for pinned author runner"})
    try:
        report["checks"]["configs"] = inspect_configs(root)
        report["checks"]["config_inputs_ready"] = {
            item["config"]: all(path["required_input_ready"] for path in item["paths"])
            for item in report["checks"]["configs"]}
        report["checks"]["author_runner_interface"] = exercise_author_runner(root)
        report["checks"]["author_incremental_merge_interface"] = exercise_author_merge(root)
    except Exception as exc:
        # Error messages may contain source text; report only class, not arbitrary contents.
        report["errors"].append({"error": "interface/config check failed", "class": type(exc).__name__})
    required_api_paths = []
    for file in ("adaptation_react.py", "evaluation_react.py"):
        text = (root / "experiments/code/ace" / file).read_text()
        if "world.task.ground_truth.required_apis" in text:
            required_api_paths.append(file)
    # A source reference is not evidence that a value reaches the model. The
    # historical v1 output made that invalid inference; preserve its JSON as
    # history, and consult the separate actual-render audit for current claims.
    audit_path = Path(__file__).parent.parent / "prompt_authority_audit" / "AUTHOR_PROMPT_AUTHORITY_AUDIT_2026-10-02.json"
    audit_verified = False
    if audit_path.exists():
        audit = json.loads(audit_path.read_text())
        audit_verified = bool(audit.get("passed") and audit.get("source_ref") == manifest["source_ref"])
        audit_verified = audit_verified and all(
            (root / item["path"]).exists() and
            blob_sha((root / item["path"]).read_bytes()) == item["git_blob_sha"]
            for item in audit["source_hashes"])
    report["checks"]["feedback_permissions"] = {
        "authority_schema_revision": "actual-render-audit-2026-10-02",
        "source_reads_required_apis": required_api_paths,
        "actual_render_audit_verified_against_current_source": audit_verified,
        "required_api_hint_in_initial_prompt": False if audit_verified else None,
        "no_gt_dynamic_evaluation_report_in_reflector_prompt": False if audit_verified else None,
        "no_gt_compiled_solution_input": False if audit_verified else None,
        "authority_basis": "separate author-method synthetic-render audit, not source string detection",
        "test_split_not_read_by_this_preflight": True}
    credential_names = ["SAMBANOVA_API_KEY", "TOGETHER_API_KEY", "OPENAI_API_KEY"]
    modules = ["_jsonnet", "jinja2", "joblib", "litellm", "openai", "sambanova", "appworld"]
    report["checks"]["runtime"] = {"credential_presence": {
        key: bool(os.environ.get(key)) for key in credential_names},
        "module_presence": {name: importlib.util.find_spec(name) is not None for name in modules}}
    report["original_model_credential_present"] = bool(os.environ.get("SAMBANOVA_API_KEY"))
    report["model_endpoint_availability"] = "not_checked; no model requests in preflight"
    report["model_calls"] = 0
    report["native_tasks_executed"] = 0
    report["source_config_interfaces_passed"] = not report["errors"]
    report["execution_status"] = "model_blocked" if not report["original_model_credential_present"] else "not_invoked"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"source_config_interfaces_passed": report["source_config_interfaces_passed"],
                      "source_files": len(hashes), "python_files": len(syntax),
                      "model_credential_present": report["original_model_credential_present"], "model_calls": 0,
                      "native_tasks_executed": 0, "output": str(args.output)}))
    if report["errors"]:
        return 1
    if args.require_model and not report["original_model_credential_present"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
