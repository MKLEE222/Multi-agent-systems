"""Bounded native interface audit; no official tasks or LLM calls.

All checking cat calls execute on backend copies and never reach the producer.
Third-party modules are unmodified and must match the pre-run source hashes.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import sys
from copy import deepcopy
from pathlib import Path

from file_binding_v1 import FileBindingReference


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fixture(node: dict) -> dict:
    def convert(value):
        if isinstance(value, str):
            return {"type": "file", "content": value}
        return {"type": "directory", "contents": {k: convert(v) for k, v in value.items()}}
    return {"root": {"root": convert(node)}}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--freeze-commit", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    config_path = Path(__file__).with_name("file_binding_v1.json")
    config = json.loads(config_path.read_text())
    source_root = args.source_root.resolve()
    for item in config["sources"]:
        if digest(source_root / item["local_path"]) != item["sha256"]:
            raise ValueError("Source hash mismatch: " + item["local_path"])
    sys.path.insert(0, str(source_root))
    mod = importlib.import_module("bfcl_eval.eval_checker.multi_turn_eval.func_source_code.gorilla_file_system")
    expected = source_root / config["sources"][0]["local_path"]
    if Path(mod.__file__).resolve() != expected.resolve():
        raise ValueError("Unexpected native module origin")

    def world(contents):
        obj = mod.GorillaFileSystem()
        obj._load_scenario(fixture(contents), long_context=False)
        return obj

    ledger = []
    counts = {"producer_events": 0, "known_checks": 0, "need_evidence_checks": 0,
              "unsupported_checks": 0, "native_mismatches": 0, "verifier_probe_calls": 0}
    summaries = []
    for case in config["cases"]:
        backend = world(case["initial"])
        memory = FileBindingReference()
        known, missing, unsupported = 0, 0, 0
        peak_bytes = 0
        for index, event in enumerate(case["events"]):
            method, call_args = event
            receipt = getattr(backend, method)(**call_args)
            memory.observe(method, deepcopy(call_args), deepcopy(receipt))
            counts["producer_events"] += 1
            checks = []
            for name in case["probes"]:
                prediction = memory.answer_cat(name)
                if prediction["status"] == "KNOWN":
                    actual = deepcopy(backend).cat(file_name=name)
                    counts["verifier_probe_calls"] += 1
                    counts["known_checks"] += 1
                    known += 1
                    if prediction["response"] != actual:
                        counts["native_mismatches"] += 1
                        raise AssertionError((case["id"], index, name, prediction, actual))
                elif prediction["status"] == "NEED_EVIDENCE":
                    counts["need_evidence_checks"] += 1
                    missing += 1
                else:
                    counts["unsupported_checks"] += 1
                    unsupported += 1
                checks.append({"name": name, **prediction})
            peak_bytes = max(peak_bytes, memory.stored_bytes())
            ledger.append({"case": case["id"], "step": index, "call": event,
                           "receipt": receipt, "checks": checks,
                           "representation_bytes": memory.stored_bytes()})
        summaries.append({"case": case["id"], "events": len(case["events"]),
                          "known": known, "need_evidence": missing,
                          "unsupported": unsupported, "peak_representation_bytes": peak_bytes})

    # Identical visible prefix and mutation receipt, different subsequent cat.
    left, right = world({"a": "value"}), world({"a": {}})
    prefix = [["pwd", {}], ["ls", {"a": True}], ["mv", {"source": "a", "destination": "b"}]]
    left_history, right_history = [], []
    pre_move = FileBindingReference()
    for method, kwargs in prefix:
        lv, rv = getattr(left, method)(**kwargs), getattr(right, method)(**kwargs)
        left_history.append(lv)
        right_history.append(rv)
        if method != "mv":
            pre_move.observe(method, kwargs, lv)
    assert left_history == right_history
    ambiguity = {"history": prefix, "receipts": left_history,
                 "move_preparation": pre_move.prepare_move("a"),
                 "left_next_cat": left.cat("b"), "right_next_cat": right.cat("b")}
    assert ambiguity["move_preparation"]["status"] == "NEED_EVIDENCE"
    assert ambiguity["left_next_cat"] != ambiguity["right_next_cat"]

    # A hidden writer violates the declared monitored-writer assumption.
    left, right = world({"a": "old"}), world({"a": "old"})
    for method, kwargs in [["pwd", {}], ["cat", {"file_name": "a"}]]:
        assert getattr(left, method)(**kwargs) == getattr(right, method)(**kwargs)
    right.echo(content="new", file_name="a")
    hidden_writer = {"left_next_cat": left.cat("a"), "right_next_cat": right.cat("a"),
                     "scope": "outside monitored-writer fragment"}
    assert hidden_writer["left_next_cat"] != hidden_writer["right_next_cat"]

    encoded = json.dumps(ledger, sort_keys=True, separators=(",", ":")).encode()
    result = {"status": "PASS", "claim": "classical adapter correctness on bounded native fixtures only",
              "freeze_commit": args.freeze_commit, "config_sha256": digest(config_path),
              "producer_sha256": digest(Path(__file__).with_name("file_binding_v1.py")),
              "auditor_sha256": digest(Path(__file__)), "sources": config["sources"],
              "counts": counts, "cases": summaries, "boundary_witnesses": {
                  "unknown_source_type": ambiguity, "unobserved_writer": hidden_writer},
              "ledger_sha256": hashlib.sha256(encoded).hexdigest(), "ledger": ledger,
              "limitations": config["limitations"]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k: result[k] for k in ["status", "freeze_commit", "counts", "ledger_sha256"]}))


if __name__ == "__main__":
    main()
