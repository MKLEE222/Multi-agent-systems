"""One-pass development diagnostic, never a producer or confirmation test.

For each frozen unknown read, try a fixed panel of legal initial-content edits.
Only the verifier loads initial configurations. A counterworld is evidence of
insufficiency only if every earlier native FS receipt is unchanged and the next
receipt changes. Failure to find one means unclassified, never recoverability.
No frozen producer is edited, trained, or selected by these diagnostics.
"""
from __future__ import annotations

import argparse
import ast
import collections
import copy
import hashlib
import inspect
import json
import sys
import time
from pathlib import Path


PANEL_VERSION = "fixed-content-edits-v1"


def call_parts(call, cls):
    node = ast.parse(call, mode="eval").body
    name = node.func.id
    if not hasattr(cls, name):
        return name, None
    bound = inspect.signature(getattr(cls, name)).bind(None,
        *[ast.literal_eval(x) for x in node.args],
        **{k.arg: ast.literal_eval(k.value) for k in node.keywords})
    bound.arguments.pop("self")
    return name, dict(bound.arguments)


def file_nodes(scenario):
    out = []
    def walk(d, path):
        for name, item in d.items():
            p = path + (name,)
            if item["type"] == "file":
                out.append((p, item["content"]))
            else:
                walk(item["contents"], p)
    if "root" in scenario:
        for root_name, item in scenario["root"].items():
            walk(item["contents"], (root_name,))
    return out


def replace_content(scenario, path, content):
    result = copy.deepcopy(scenario)
    node = result["root"][path[0]]
    for name in path[1:]:
        node = node["contents"][name]
    node["content"] = content
    return result


def fixed_edits(content):
    # Applied to every initial file, independent of pending read or outcome.
    lines = content.splitlines()
    values = ["", "OCAR_DIAGNOSTIC", "OCAR_DIAGNOSTIC\n", content + "OCAR_DIAGNOSTIC",
              content + "\nOCAR_DIAGNOSTIC", "OCAR_DIAGNOSTIC\n" + content,
              content + "\n", content + "\n\n", "\n" + content,
              "\n".join(reversed(lines)), "\n".join(lines + lines),
              "\n".join(lines[1:]), "\n".join(lines[:-1])]
    return list(dict.fromkeys(v for v in values if v != content))


def replay(cls, scenario, parsed):
    fs = cls()
    fs._load_scenario(scenario, long_context=False)
    receipts = []
    for name, kwargs in parsed:
        if kwargs is None:
            receipts.append(None)  # Other independent classes are unchanged.
            continue
        try:
            receipts.append(getattr(fs, name)(**kwargs))
        except Exception as exc:
            receipts.append(f"Error during execution: {type(exc).__name__}: {exc}")
    return receipts


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    sys.path.insert(0, str(args.source_root))
    from bfcl_eval.eval_checker.multi_turn_eval.func_source_code.gorilla_file_system import GorillaFileSystem
    questions = {x["id"]: x for x in map(json.loads,
        (args.source_root / "data/BFCL_v4_multi_turn_base.json").read_text().splitlines())}
    answers = {x["id"]: x["ground_truth"] for x in map(json.loads,
        (args.source_root / "data/possible_answer/BFCL_v4_multi_turn_base.json").read_text().splitlines())}
    ledger_path = args.repo_root / "docs/OACR_REAL_BFCL_VIEWS_RESULT_2026-10-02.ledger.jsonl"
    ledger = [json.loads(x) for x in ledger_path.read_text().splitlines()]
    started = time.perf_counter()
    output = []
    native_runs = 0
    for row in ledger:
        if row["methods"]["demand_compiler"]["known"]:
            continue
        cid, index = row["case_id"], row["index"]
        calls = [c for t in answers[cid] for c in t][:index + 1]
        parsed = [call_parts(c, GorillaFileSystem) for c in calls]
        initial = questions[cid]["initial_config"]["GorillaFileSystem"]
        native = replay(GorillaFileSystem, initial, parsed)
        native_runs += 1
        assert native[-1] == row["native"], (cid, index, "native replay mismatch")
        fs_indices = [i for i, (_, kw) in enumerate(parsed[:-1]) if kw is not None]
        trials, prefix_matches, witness = 0, 0, None
        for path, old in file_nodes(initial):
            for new in fixed_edits(old):
                alternative = replay(GorillaFileSystem,
                    replace_content(initial, path, new), parsed)
                trials += 1
                native_runs += 1
                if all(native[i] == alternative[i] for i in fs_indices):
                    prefix_matches += 1
                    if alternative[-1] != native[-1]:
                        witness = {"changed_initial_file": "/".join(path),
                            "original_content": old, "alternative_content": new,
                            "original_read": native[-1], "alternative_read": alternative[-1],
                            "checked_prior_fs_receipts": len(fs_indices)}
                        break
            if witness:
                break
        output.append({"case_id": cid, "index": index, "call": calls[-1],
            "classification": "observational_insufficiency_witness" if witness else "no_witness_unclassified",
            "trials": trials, "prefix_matched_trials": prefix_matches, "witness": witness})
    result = {"scope": "exposed-development verifier diagnostic; no learned-agent or independent confirmation",
        "panel_version": PANEL_VERSION, "unknown_rows": len(output),
        "ledger_sha256": hashlib.sha256(ledger_path.read_bytes()).hexdigest(),
        "counts": dict(collections.Counter(r["classification"] for r in output)),
        "native_fs_replays": native_runs,
        "wall_seconds": time.perf_counter() - started, "rows": output}
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "rows"}, ensure_ascii=False, indent=2))
    print("Unclassified:")
    for row in output:
        if not row["witness"]:
            print(row["case_id"], row["index"], row["call"], row["trials"])


if __name__ == "__main__":
    main()
