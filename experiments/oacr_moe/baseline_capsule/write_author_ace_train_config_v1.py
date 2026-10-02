#!/usr/bin/env python3
"""Compile author's native ReAct train configuration with an isolated output path.

Does not call a model, create credentials, load tasks, or modify author Python.
Changing the backbone is a named author-method reproduction variant, not a
claim to reproduce the published model's scores.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--dest", type=Path, required=True,
                        help="A .jsonnet file in the full author source experiments/configs directory")
    parser.add_argument("--artifact-root", type=Path, required=True,
                        help="Private local output directory, separate from published playbooks")
    parser.add_argument("--model", default="DeepSeek-V3.1")
    parser.add_argument("--provider", choices=("sambanova", "together", "openai"), default="sambanova")
    parser.add_argument("--sample-size", type=int, default=1)
    parser.add_argument("--openai-base-url", default=None)
    args = parser.parse_args()
    if args.sample_size < 1:
        parser.error("sample-size must be positive")
    if args.dest.suffix != ".jsonnet":
        parser.error("dest must end in .jsonnet")
    import _jsonnet
    root = args.source_root.resolve()
    source = root / "experiments/configs/ACE_offline_no_GT_adaptation.jsonnet"
    config = json.loads(_jsonnet.evaluate_file(str(source), ext_vars={"APPWORLD_PROJECT_PATH": str(root)}))
    runner = config["config"]
    assert runner["dataset"] == "train" and runner["run_type"] == "ace-adaptation"
    assert runner["agent"]["type"] == "ace_adaptation_react"
    runner["sample_size"] = args.sample_size
    runner["num_epochs"] = 1
    agent = runner["agent"]
    agent["use_gt_code"] = False
    for role in ("generator", "reflector", "curator"):
        model_config = agent[role + "_model_config"]
        model_config["name"] = args.model
        model_config["provider"] = args.provider
        if args.openai_base_url:
            if args.provider != "openai":
                parser.error("openai-base-url requires provider=openai")
            model_config["base_url"] = args.openai_base_url
    artifact_root = args.artifact_root.resolve()
    artifact_root.mkdir(parents=True, exist_ok=True)
    agent["trained_playbook_file_path"] = str(artifact_root / "train_generated_playbook.txt")
    args.dest.parent.mkdir(parents=True, exist_ok=True)
    args.dest.write_text(json.dumps(config, indent=2) + "\n")
    print(json.dumps({"config": str(args.dest), "dataset": "train", "sample_size": args.sample_size,
                      "shared_model_roles": args.model, "provider": args.provider,
                      "use_gt_code": False, "required_api_prior": "retained from author source",
                      "per_task_evaluator_feedback": "retained from author source",
                      "native_tasks_executed": 0, "model_calls": 0}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
