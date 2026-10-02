#!/usr/bin/env python3
"""Boot the pinned author's native AppWorld train environment without a model.

Only native API metadata and current task status are read. No solution, evaluator,
test split, protected data content, or credentials are emitted. This is an
environment smoke, not ACE task performance or an agent run.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
import subprocess
import time
from pathlib import Path

AUTHOR_SHA = "9f3e92155345a9159f3a8b25abc334eeca05b545"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.source_root.resolve()
    sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    if sha != AUTHOR_SHA:
        parser.error("source HEAD differs from pinned author SHA")
    os.environ["APPWORLD_PROJECT_PATH"] = str(root)
    from appworld.common.path_store import path_store
    path_store.update_root(str(root))
    from appworld import AppWorld
    from appworld.task import load_task_ids

    train_ids = load_task_ids("train")
    if not train_ids:
        parser.error("native train split is empty")
    result = {
        "scope": "native author environment smoke; no ACE actor or task score",
        "source_ref": sha,
        "dataset": "train",
        "selection": "first native train manifest ID, independent of outcomes",
        "train_count": len(train_ids),
        "train_manifest_sha256": hashlib.sha256("\n".join(train_ids).encode()).hexdigest(),
        "selected_task_id_sha256": hashlib.sha256(train_ids[0].encode()).hexdigest(),
        "ground_truth_loaded": False,
        "task_evaluator_called": False,
        "model_calls": 0,
        "test_tasks_loaded": 0,
        "commands": [],
        "runtime_versions": {name: importlib.metadata.version(name) for name in
                             ("appworld", "appworld-experiments", "click", "typer", "pydantic", "sqlmodel")},
        "earlier_cli_failure": {"click": "8.5.0", "typer": "0.12.5",
                                "message": "Secondary flag is not valid for non-boolean flag",
                                "resolution": "pin click==8.1.8; no author Python changed"},
    }
    started = time.perf_counter()
    with AppWorld(task_id=train_ids[0], experiment_name="oacr_moe_native_environment_smoke",
                  load_ground_truth=False, random_seed=100, timeout_seconds=10) as world:
        for code in ("print(apis.api_docs.show_app_descriptions())",
                     "print(apis.supervisor.show_active_task())"):
            receipt = world.execute(code)
            okay = bool(receipt.strip()) and not receipt.startswith("Execution failed")
            result["commands"].append({"code": code, "nonempty_success_receipt": okay,
                "receipt_bytes": len(receipt.encode()),
                "receipt_sha256": hashlib.sha256(receipt.encode()).hexdigest()})
        result["native_interactions"] = len(world.environment_io)
    result["elapsed_seconds"] = time.perf_counter() - started
    result["status"] = "native_environment_ready" if all(
        row["nonempty_success_receipt"] for row in result["commands"]) else "native_command_failed"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: result[k] for k in ("status", "native_interactions", "model_calls",
                                           "ground_truth_loaded", "test_tasks_loaded")}))
    return 0 if result["status"] == "native_environment_ready" else 1


if __name__ == "__main__":
    raise SystemExit(main())
