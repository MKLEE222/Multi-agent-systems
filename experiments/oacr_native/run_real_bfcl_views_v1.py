"""Development replay of all 50 public BFCL base filesystem cases.

Reference actions are supplied one at a time by the verifier. Producers see only
the past public calls/receipts and the current proposed read, never initial state,
future actions or expected receipts. This is not a learned-agent score.
"""
from __future__ import annotations

import argparse
import ast
import collections
import hashlib
import importlib.util
import json
import re
import sys
import time
from pathlib import Path

from real_bfcl_views_v1 import DemandViews, FS_METHODS, IndexedViews, READS


def encode(x):
    return json.dumps(x, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def parse_call(text):
    p = ast.parse(text, mode="eval").body
    if not isinstance(p, ast.Call) or not isinstance(p.func, ast.Name) or p.args:
        raise ValueError("Replay requires literal keyword-only public reference calls")
    if any(k.arg is None for k in p.keywords):
        raise ValueError("Expanded arguments outside replay grammar")
    return p.func.id, {k.arg: ast.literal_eval(k.value) for k in p.keywords}


def decode_receipt(text):
    if text == "None":
        return None
    try:
        return json.loads(text)
    except (ValueError, TypeError):
        return text


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--freeze-commit", required=True)
    parser.add_argument("--config", type=Path, default=Path(__file__).with_suffix(".json"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not re.fullmatch(r"[0-9a-f]{40}", args.freeze_commit):
        raise ValueError("Require an actual pre-run GitHub freeze commit")
    config = json.loads(args.config.read_text())
    for rel, expected in config["source_hashes"].items():
        if digest(args.source_root / rel) != expected:
            raise ValueError(f"Source hash mismatch: {rel}")
    for rel, expected in config["implementation_hashes"].items():
        if digest(Path(__file__).parent / rel) != expected:
            raise ValueError(f"Frozen implementation hash mismatch: {rel}")
    sys.path[:0] = [str(args.source_root / "native_deps"), str(args.source_root)]
    from bfcl_eval.eval_checker.multi_turn_eval.multi_turn_utils import execute_multi_turn_func_call
    from bfcl_eval.eval_checker.multi_turn_eval.multi_turn_checker import multi_turn_checker
    from src.method.bm25 import BM25Method
    spec = importlib.util.spec_from_file_location("author_ama_tool", args.source_root / "ama_tool.py")
    author_tools = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(author_tools)
    questions = [json.loads(x) for x in (args.source_root / config["questions"]).read_text().splitlines()]
    # Only this verifier loads initial configurations and reference actions.
    answers = {x["id"]: x["ground_truth"] for x in
               map(json.loads, (args.source_root / config["answers"]).read_text().splitlines())}
    cases = [x for x in questions if "GorillaFileSystem" in x["involved_classes"]]
    if [x["id"] for x in cases] != config["case_ids"]:
        raise ValueError("Public metadata selection changed")
    totals = collections.Counter()
    methods = {m: collections.Counter() for m in ["indexed_classical", "demand_compiler"]}
    rows, cases_out, checks = [], [], []
    full_start = time.perf_counter_ns()
    for case in cases:
        cid, ground = case["id"], answers[case["id"]]
        history = []
        producers = {"indexed_classical": IndexedViews(history), "demand_compiler": DemandViews(history)}
        branch_calls = {m: [[] for _ in ground] for m in producers}
        paid_responses = {m: collections.Counter() for m in producers}
        peaks = {m: 0 for m in producers}
        timings = {m: collections.Counter() for m in producers}
        cs = {m: collections.Counter() for m in producers}
        for turn, calls in enumerate(ground):
            turn_requests = {m: collections.Counter() for m in producers}
            for call in calls:
                method, kwargs = parse_call(call)
                index = len(history)
                pending = {}
                if method in READS:
                    totals["native_read_requests"] += 1
                    for name, producer in producers.items():
                        start = time.process_time_ns()
                        pending[name] = producer.prepare(method, kwargs)
                        timings[name]["prepare_cpu_ns"] += time.process_time_ns() - start
                native, _ = execute_multi_turn_func_call([call], case["initial_config"],
                    case["involved_classes"], "observable_prefix_v1", cid)
                if len(native) != 1:
                    raise AssertionError("Unexpected native receipt count")
                receipt = decode_receipt(native[0])
                totals["producer_reference_calls"] += 1
                history.append({"index": index, "turn": turn, "method": method,
                                "args": kwargs, "receipt": receipt, "call": call})
                record = {"case_id": cid, "turn": turn, "index": index,
                          "method": method, "call": call, "native": receipt, "methods": {}}
                for name, producer in producers.items():
                    answer = pending.get(name)
                    skip = False
                    if answer is not None:
                        known = answer.response is not None
                        matches = answer.response == receipt if known else None
                        methods[name]["read_requests"] += 1
                        methods[name]["query_event_or_lookup_visits"] += answer.work
                        cs[name]["known" if known else "needs_native_evidence"] += 1
                        methods[name]["known" if known else "needs_native_evidence"] += 1
                        if known:
                            methods[name]["native_mismatches"] += not matches
                            predicted_text = json.dumps(answer.response)
                            turn_requests[name][predicted_text] += 1
                            # Official checker accepts earlier matching receipts. Do
                            # not skip a first-time derived output or inspect gold.
                            skip = paid_responses[name][predicted_text] >= turn_requests[name][predicted_text]
                        else:
                            turn_requests[name][native[0]] += 1
                        record["methods"][name] = {"known": known, "matches": matches,
                            "predicted": answer.response, "evidence_indices": answer.evidence,
                            "query_visits": answer.work, "skip_native_read": skip}
                    if not skip:
                        branch_calls[name][turn].append(call)
                        paid_responses[name][native[0]] += 1
                    else:
                        methods[name]["skipped_native_reads"] += 1
                        cs[name]["skipped_native_reads"] += 1
                    start = time.process_time_ns()
                    if method in FS_METHODS:
                        producer.observe(index, method, kwargs, receipt)
                    timings[name]["observe_cpu_ns"] += time.process_time_ns() - start
                    stored = len(encode({"common_visible_archive": history,
                                        "producer": producer.snapshot()}).encode())
                    peaks[name] = max(peaks[name], stored)
                if method in READS:
                    if record["methods"]["indexed_classical"]["known"] != record["methods"]["demand_compiler"]["known"]:
                        totals["coverage_disagreements"] += 1
                    # Execute the author's accessors without changing their code.
                    # This is accessor/witness diagnostics, not AMA-Agent scoring.
                    prefix = {"trajectory": [{"turn_idx": h["index"], "action": h["call"],
                                              "observation": json.dumps(h["receipt"])} for h in history[:-1]]}
                    prefix_text = json.dumps(prefix)
                    raw_context = author_tools.traj_get(prefix_text)
                    filenames = ([kwargs["file_name1"], kwargs["file_name2"]]
                                 if method == "diff" else [kwargs["file_name"]])
                    indices = sorted(set().union(*(author_tools.traj_find(prefix_text, f, mode="entity") for f in filenames)))
                    keyword_context = author_tools.traj_get(prefix_text, {"indices": indices})
                    bm25_context = ""
                    if prefix["trajectory"]:
                        bm = BM25Method(top_k=5)
                        memory = bm.memory_construction(raw_context)
                        visible_user_request = " ".join(str(m.get("content", "")) for m in case["question"][turn])
                        bm25_context = bm.memory_retrieve(memory, visible_user_request + "\nProposed native call: " + call)
                    selected = set(map(int, re.findall(r"^Turn (\d+):", bm25_context, re.M)))
                    witness = set(record["methods"]["demand_compiler"]["evidence_indices"])
                    record["author_accessors"] = {"full_prefix_bytes": len(raw_context.encode()),
                        "entity_bytes": len(keyword_context.encode()), "bm25_top5_bytes": len(bm25_context.encode()),
                        "entity_indices": indices, "bm25_indices": sorted(selected),
                        "compiler_witness_covered_by_entity": witness <= set(indices) if witness else None,
                        "compiler_witness_covered_by_bm25": witness <= selected if witness else None}
                    rows.append(record)
                totals["shared_archive_bytes_at_case_end"] = len(encode(history).encode())
        # Unchanged official checker on complete reference and filtered branches.
        case_checks = {}
        for label, proposed in {"reference_replay": ground, **branch_calls}.items():
            check = multi_turn_checker([[t] for t in proposed], ground, case,
                                       "multi_turn_base", f"view_check_{label}_{cid}")
            case_checks[label] = {"valid": check["valid"],
                                  "error_type": check.get("error_type"),
                                  "remaining_calls": sum(map(len, proposed))}
            checks.append({"case_id": cid, "branch": label, **case_checks[label]})
        case_result = {"case_id": cid, "reference_calls": sum(map(len, ground)),
            "filesystem_methods": dict(collections.Counter(h["method"] for h in history if h["method"] in FS_METHODS)),
            "conservative_directory_or_unknown_transfer": producers["indexed_classical"].ns.conservative,
            "official_checker": case_checks, "methods": {}}
        for name, producer in producers.items():
            update_visits = producer.work + producer.ns.work
            methods[name]["update_visits"] += update_visits
            methods[name]["summed_case_peak_bundle_bytes"] += peaks[name]
            methods[name].update(timings[name])
            case_result["methods"][name] = {**dict(cs[name]), **dict(timings[name]),
                "update_visits": update_visits, "peak_complete_bundle_bytes": peaks[name]}
        cases_out.append(case_result)
    totals["case_count"] = len(cases)
    totals["reference_turns"] = sum(len(answers[c["id"]]) for c in cases)
    totals.pop("shared_archive_bytes_at_case_end", None)
    ledger_text = "\n".join(encode(row) for row in rows) + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    ledger_path = args.output.with_suffix(".ledger.jsonl")
    ledger_path.write_text(ledger_text)
    result = {"status": "PASS" if all(x["valid"] for x in checks) and
              not any(v["native_mismatches"] for v in methods.values()) else "FAIL",
        "scope": "exposed-development reference-trajectory replay; not a model benchmark score",
        "freeze_commit": args.freeze_commit, "config_sha256": digest(args.config),
        "totals": dict(totals), "methods": {k: dict(v) for k, v in methods.items()},
        "official_checker_valid_cases": {b: sum(x["valid"] for x in checks if x["branch"] == b)
            for b in ["reference_replay", "indexed_classical", "demand_compiler"]},
        "author_accessor_scope": "unmodified AMA traj_get/traj_find and BM25; no graph/LLM sufficiency/agent replication",
        "ledger": {"path": ledger_path.name, "rows": len(rows), "sha256": digest(ledger_path)},
        "wall_time_ns_including_native_verification": time.perf_counter_ns() - full_start,
        "model_calls": 0, "new_theorem": False, "unique_advantage_established": False,
        "cases": cases_out}
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(encode({k: result[k] for k in ["status", "totals", "methods", "official_checker_valid_cases", "ledger"]}))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
