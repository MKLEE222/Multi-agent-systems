"""Existing methods compete on the same legal-input native maintenance task.

EC2/EffECXtive use their published objectives in the deterministic uniform case.
All generated models are derived from public semantics, never verifier labels.
The structural myopic selector is a development candidate, not a novelty claim.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import math
import time
from collections import Counter
from fractions import Fraction
from functools import lru_cache
from pathlib import Path

from adaptive_source_compile_v1 import demand, hidden_candidates, native_behavior, port, residual_verify
from available_source_repair_v1 import Contract
from contract_budget_audit_v1 import restricted_cut
from multi_delta_budget_audit_v1 import compile_multi, subsets
from optimal_source_policy_control_v1 import simulate


def class_counts(mask, labels):
    return Counter(labels[i] for i in range(len(labels)) if mask & (1 << i))


def cross_edges(mask, labels):
    sizes = class_counts(mask, labels)
    return (mask.bit_count() ** 2 - sum(n * n for n in sizes.values())) // 2


def ec2_gain(mask, positive, labels):
    yes, no = mask & positive, mask & ~positive
    count = mask.bit_count()
    # Original uniform prior edge weights are constant across all tests.
    # Do not renormalize each outcome's surviving edge weights separately.
    return (Fraction(cross_edges(mask, labels))
            - Fraction(yes.bit_count(), count) * cross_edges(yes, labels)
            - Fraction(no.bit_count(), count) * cross_edges(no, labels))


def literal_ec2_gain(mask, positive, labels):
    """Verifier only: expected cut of each literal cross-class edge."""
    vertices = [i for i in range(len(labels)) if mask & (1 << i)]
    outcomes = [(mask & positive, Fraction((mask & positive).bit_count(), len(vertices))),
                (mask & ~positive, Fraction((mask & ~positive).bit_count(), len(vertices)))]
    total = Fraction(0)
    for at, i in enumerate(vertices):
        for j in vertices[at + 1:]:
            if labels[i] != labels[j]:
                total += sum(prob for branch, prob in outcomes
                             if not (branch & (1 << i) and branch & (1 << j)))
    return total


def gini_purity(mask, labels):
    n = mask.bit_count()
    return Fraction(sum(v * v for v in class_counts(mask, labels).values()), n * n) if n else Fraction(0)


def entropy(mask, labels):
    n = mask.bit_count()
    return -sum((v / n) * math.log2(v / n) for v in class_counts(mask, labels).values()) if n else 0.0


def prepare_model(stored, lost, contract, method, counts):
    candidates = tuple(sorted(lost))
    worlds = tuple(stored | extra for extra in subsets(lost))
    counts["model_hypothesis_states"] += len(worlds)
    signatures = [simulate(contract, b, counts, phase="policy_compile") for b in worlds]
    label_map = {}
    labels = tuple(label_map.setdefault(sig, len(label_map)) for sig in signatures)
    positives = tuple(sum(1 << i for i, b in enumerate(worlds) if e in b) for e in candidates)
    initial = (1 << len(worlds)) - 1
    policy = {}

    @lru_cache(None)
    def optimal(mask):
        counts["dp_states"] += 1
        if len(class_counts(mask, labels)) == 1:
            policy[mask] = None
            return Fraction(0)
        best = None
        for j, positive in enumerate(positives):
            yes, no = mask & positive, mask & ~positive
            if not yes or not no:
                continue
            counts["dp_score_evaluations"] += 1
            expected = 1 + (yes.bit_count() * optimal(yes) + no.bit_count() * optimal(no)) / mask.bit_count()
            item = expected, j
            if best is None or item < best:
                best = item
        assert best is not None
        policy[mask] = best[1]
        return best[0]

    if method == "exact_expected_optimal":
        optimal(initial)
    encoded = json.dumps({"candidate_edges": candidates, "positive_masks": positives,
                          "class_labels": labels, "policy": sorted(policy.items())}, separators=(",", ":"))
    counts["policy_serialized_bytes"] += len(encoded.encode())
    return candidates, worlds, labels, positives, initial, policy


def select_model_query(mask, candidates, labels, positives, method, counts):
    best, selected = None, None
    for j, positive in enumerate(positives):
        yes, no = mask & positive, mask & ~positive
        if not yes or not no:
            continue
        counts["online_score_evaluations"] += 1
        if method == "published_ec2":
            score = ec2_gain(mask, positive, labels)
        elif method == "published_effecxtive":
            score = (Fraction(yes.bit_count(), mask.bit_count()) * gini_purity(yes, labels)
                     + Fraction(no.bit_count(), mask.bit_count()) * gini_purity(no, labels)
                     - gini_purity(mask, labels))
        elif method == "class_information_gain":
            score = (entropy(mask, labels) - yes.bit_count() / mask.bit_count() * entropy(yes, labels)
                     - no.bit_count() / mask.bit_count() * entropy(no, labels))
        else:
            raise ValueError(method)
        tolerance = 1e-12 if method == "class_information_gain" else 0
        if best is None or score > best + tolerance:
            best, selected = score, j
    assert selected is not None
    return selected


def execute(stored, lost, contract, source, method, counts):
    present, unknown, transcript = stored, lost, []
    model = None
    if method in {"published_ec2", "published_effecxtive", "class_information_gain", "exact_expected_optimal"}:
        model = prepare_model(stored, lost, contract, method, counts)
        candidates, _, labels, positives, mask, policy = model
        while len(class_counts(mask, labels)) > 1:
            j = policy[mask] if method == "exact_expected_optimal" else select_model_query(mask, candidates, labels, positives, method, counts)
            edge = candidates[j]
            answer = source.membership(edge, "v1")
            transcript.append((edge, answer))
            if answer:
                present = present | {edge}
            mask &= positives[j] if answer else ~positives[j]
    elif method == "full_source_rebuild":
        for edge in sorted(lost):
            answer = source.membership(edge, "v1")
            transcript.append((edge, answer))
            if answer:
                present = present | {edge}
    else:
        while True:
            need = demand(contract, present, unknown, counts)
            if not need:
                break
            if method == "structural_lex":
                edge = min(need)
            elif method == "structural_reverse":
                edge = max(need)
            elif method == "structural_span":
                edge = min(need, key=lambda e: (e[1] - e[0], *e))
            elif method == "structural_one_step":
                best, edge = None, None
                for candidate in sorted(need):
                    before = counts["demand_cut_requests"]
                    post = demand(contract, present | {candidate}, unknown - {candidate}, counts)
                    counts["selection_cut_requests"] += counts["demand_cut_requests"] - before
                    score = 1 + Fraction(len(need) - 1 - len(post), 2)
                    if best is None or score > best:
                        best, edge = score, candidate
            else:
                raise ValueError(method)
            answer = source.membership(edge, "v1")
            transcript.append((edge, answer))
            unknown = unknown - {edge}
            if answer:
                present = present | {edge}
    counts["final_compile_input_edges"] += len(present)
    stored_output = compile_multi(contract.n, contract.graph, contract.actions, contract.budget, present)
    counts["source_queries"] += len(transcript)
    return stored_output, tuple(transcript), model


def run(protocol, fixtures):
    methods = protocol["baselines"] + ["structural_one_step"]
    summary = {m: Counter() for m in methods}
    curves = {m: Counter() for m in methods}
    local_seconds = {m: 0.0 for m in methods}
    common, verification, rows, fixture_results = Counter(), Counter(), [], []
    for spec in fixtures:
        graph = frozenset(map(tuple, spec["graph"]))
        candidates = frozenset(map(tuple, spec["candidates"]))
        old = Contract(spec["n"], graph, frozenset(map(tuple, spec["old_actions"])), spec["old_budget"])
        new = Contract(spec["n"], graph, frozenset(map(tuple, spec["new_actions"])), spec["new_budget"])
        actuals = tuple(subsets(candidates))
        common["source_backed_initializations"] += len(actuals)
        initial = {b: compile_multi(old.n, old.graph, old.actions, old.budget, b) for b in actuals}
        signatures = {b: native_behavior(new, b, verification) for b in actuals}
        fibers = {}
        for b in actuals:
            fibers.setdefault(initial[b], []).append(b)
        lost = {r: hidden_candidates(old, candidates, r, common) for r in fibers}
        for r, fiber in fibers.items():
            assert {r | extra for extra in subsets(lost[r])} == set(fiber)
            verification["old_source_fiber_checks"] += 1
        local = {m: Counter() for m in methods}
        for actual in actuals:
            r = initial[actual]
            reference_rep = None
            for method in methods:
                observed, counts = [], Counter()
                source = port(actual, candidates, len(candidates), observed)
                restricted_cut.cache_clear()
                started = time.perf_counter()
                rep, transcript, model = execute(r, lost[r], new, source, method, counts)
                local_seconds[method] += time.perf_counter() - started
                cache = restricted_cut.cache_info()
                counts["all_cut_requests"] += cache.hits + cache.misses
                counts["cut_cache_misses"] += cache.misses
                assert transcript == tuple(observed)
                assert len(transcript) <= len(candidates)
                assert len({e for e, _ in transcript}) == len(transcript)
                assert all(e in candidates for e, _ in transcript)
                compatible = [b for b in fibers[r] if all((e in b) == a for e, a in transcript)]
                assert actual in compatible
                assert len({signatures[b] for b in compatible}) == 1
                assert native_behavior(new, rep, verification) == signatures[actual]
                residual_verify(new, rep, actual, verification)
                verification["successful_native_outputs"] += 1
                if reference_rep is None:
                    reference_rep = rep
                    # Verifier-only subset enumeration. Neither policies nor
                    # their models consume these observed native outcomes.
                    for alternate in subsets(actual):
                        sufficient = native_behavior(new, alternate, verification) == signatures[actual]
                        assert sufficient == (rep <= alternate)
                        verification["native_least_subset_checks"] += 1
                    verification["distinct_physical_rep_checks"] += 1
                assert rep == reference_rep
                if method == "published_ec2":
                    _, worlds, labels, positives, mask, _ = model
                    for edge, answer in transcript:
                        for positive in positives:
                            assert ec2_gain(mask, positive, labels) == literal_ec2_gain(mask, positive, labels)
                            verification["ec2_literal_edge_score_checks"] += 1
                        j = tuple(sorted(lost[r])).index(edge)
                        mask &= positives[j] if answer else ~positives[j]
                counts["requests"] += 1
                counts["retained_output_edge_records"] += len(rep)
                summary[method].update(counts)
                local[method].update(counts)
                for budget in range(len(candidates) + 1):
                    curves[method][str(budget) + "_requests"] += 1
                    curves[method][str(budget) + "_completed"] += len(transcript) <= budget
                rows.append({"fixture": spec["id"], "world": sorted(actual), "old_rep": sorted(r),
                             "method": method, "stored_output": sorted(rep),
                             "transcript": [[list(e), a] for e, a in transcript], "counts": dict(counts)})
        fixture_results.append({"fixture": spec["id"], "worlds": len(actuals),
                                "methods": {m: dict(c) for m, c in local.items()}})
    assert summary["structural_lex"]["source_queries"] == 568
    assert summary["structural_reverse"]["source_queries"] == 536
    assert summary["exact_expected_optimal"]["source_queries"] == 460
    return {"protocol_id": protocol["protocol_id"], "methods": {m: dict(c) for m, c in summary.items()},
            "budget_completion_curves": {m: dict(c) for m, c in curves.items()},
            "fixtures": fixture_results, "common_initialization": dict(common),
            "verification": dict(verification), "local_producer_seconds": local_seconds,
            "rows": rows, "physical_outputs_identical_across_methods": True,
            "native_mismatches_or_unauthorized_calls": 0,
            "native_correctness_scope": "all methods recover the same correct physical representation on all 138 development worlds and pass residual replay",
            "cost_scope": protocol["costs"],
            "novelty_status": "no novel algorithm advantage or external benchmark claim; same-input developmental competition with published-method implementations"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, default=Path(__file__).with_suffix(".json"))
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    protocol = json.loads(args.protocol.read_text())
    fixture = args.protocol.with_name(protocol["fixture_protocol"])
    files = [args.protocol, fixture, Path(__file__), *[Path(__file__).with_name(n) for n in
             ["adaptive_source_compile_v1.py", "available_source_repair_v1.py", "contract_budget_audit_v1.py",
              "multi_delta_budget_audit_v1.py", "optimal_source_policy_control_v1.py"]]]
    pinned = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    result = run(protocol, json.loads(fixture.read_text())["fixtures"])
    assert pinned == {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    ledger = args.out.with_suffix(".cases.json.gz")
    data = gzip.compress(json.dumps(result.pop("rows"), sort_keys=True, separators=(",", ":")).encode(), mtime=0)
    ledger.write_bytes(data)
    result["input_sha256"] = pinned
    result["case_ledger"] = {"file": ledger.name, "sha256": hashlib.sha256(data).hexdigest()}
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"out": str(args.out), "methods": {m:{k:c.get(k,0) for k in
                      ["requests","source_queries","all_cut_requests","model_hypothesis_states","policy_compile_simulated_native_calls","dp_states"]}
                      for m,c in result["methods"].items()}, "verification":result["verification"]}, indent=2))


if __name__ == "__main__":
    main()
