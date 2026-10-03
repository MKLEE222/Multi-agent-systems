"""Independent native audit of the ordered operator and its working theorem.

Bitset failure replay, actual-world flips and subset certificates are verifier
only. The producer receives a SourcePort closure, never this world's edge set.
"""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import replace
import gzip
import hashlib
import itertools
import json
from pathlib import Path

from adaptive_source_compile_v1 import hidden_candidates, port
from available_source_repair_v1 import Contract, SourcePort, closure, failures, permission_set
from multi_delta_budget_audit_v1 import compile_multi, subsets
from ordered_source_compile_v1 import (Proof, check_proof, compile_from_source,
                                     receipt_payload, transport_paths)


def native_signature(c, additions, counts):
    outputs = []
    for failed in failures(c):
        outputs.append(closure(c.n, (c.graph - failed) | additions))
        counts["verifier_native_calls"] += 1
    return tuple(outputs)


def validate_receipts(c, known, unknown, actual, result, counts):
    prefix, answered = frozenset(), []
    for receipt in result.receipts:
        edge, proof = receipt.edge, receipt.proof
        assert edge in known | unknown and receipt.known == (edge in known)
        assert check_proof(c.n, c.graph | prefix, c.actions, c.budget, edge, proof)
        counts["proof_checks"] += 1
        if proof.kind == "paths":
            assert receipt.answer is None
            counts["robust_path_proofs"] += 1
            if c.budget:
                for action in c.actions:
                    shifted = transport_paths(proof, action)
                    assert check_proof(c.n, (c.graph - {action}) | prefix,
                                       c.actions - {action}, c.budget - 1, edge, shifted)
                    counts["residual_certificate_transports"] += 1
            broken = replace(proof, paths=((edge[0], edge[1]),) * (c.budget + 1))
            assert not check_proof(c.n, c.graph | prefix, c.actions, c.budget, edge, broken)
            counts["corrupted_proofs_rejected"] += 1
        else:
            counts["cut_proofs"] += 1
            assert not check_proof(c.n, c.graph | prefix, c.actions, c.budget,
                                   edge, replace(proof, source_side=frozenset()))
            counts["corrupted_proofs_rejected"] += 1
            if receipt.answer is not None:
                assert receipt.answer == (edge in actual)
                if not receipt.known:
                    answered.append((edge, receipt.answer))
                if receipt.answer:
                    prefix |= {edge}
    assert prefix == result.stored
    assert tuple(answered) == result.transcript


def check_full(c, known, unknown, actual, bank, verification, producer):
    observed = []
    result = compile_from_source(c.n, c.graph, c.actions, c.budget, known, unknown,
                                 port(actual, unknown, len(unknown), observed), "v1", producer)
    assert result.exact and result.transcript == tuple(observed)
    validate_receipts(c, known, unknown, actual, result, verification)
    reference = bank[actual]
    sensitive = frozenset(e for e in unknown if bank[actual ^ {e}] != reference)
    queried = frozenset(e for e, _ in result.transcript)
    assert queried == sensitive
    verification["pointwise_sensitive_set_checks"] += 1
    compatible = [known | extra for extra in subsets(unknown)
                  if all((e in known | extra) == answer for e, answer in result.transcript)]
    assert all(bank[b] == reference for b in compatible)
    verification["transcript_certificate_checks"] += 1
    essential_present = frozenset(e for e in actual if bank[actual - {e}] != reference)
    assert result.stored == essential_present and bank[result.stored] == reference
    verification["physical_least_subset_checks"] += 1
    # If these necessary coordinates form a sufficient transcript, every valid
    # certificate contains this unique minimum set. No DP or method label used.
    return result, sensitive


def exhaustive_audit(verification, producer):
    digest, contracts = hashlib.sha256(), 0
    for n in range(2, 5):
        edges = tuple((u, v) for u in range(n) for v in range(u + 1, n))
        for coloring in itertools.product(range(5), repeat=len(edges)):
            graph = frozenset(e for e, role in zip(edges, coloring) if role in (1, 2))
            actions = frozenset(e for e, role in zip(edges, coloring) if role == 2)
            known = frozenset(e for e, role in zip(edges, coloring) if role == 3)
            unknown = frozenset(e for e, role in zip(edges, coloring) if role == 4)
            for h in range(len(actions) + 1):
                c = Contract(n, graph, actions, h)
                bank = {b: native_signature(c, b, verification) for b in subsets(known | unknown)}
                contracts += 1
                for extra in subsets(unknown):
                    actual = known | extra
                    result, sensitive = check_full(c, known, unknown, actual, bank, verification, producer)
                    case = [n, coloring, h, sorted(actual), sorted(result.stored), sorted(sensitive)]
                    digest.update(json.dumps(case, separators=(",", ":")).encode() + b"\n")
    return {"contracts": contracts, "requests": producer["requests"],
            "streamed_case_sha256": digest.hexdigest(), "case_order": "n/coloring/h/subsets in fixed lexicographic order"}


def old_fixture_audit(fixtures, baseline_ledger, verification):
    producer, bounded, rows, per_fixture = Counter(), Counter(), [], []
    lookup = {(r["fixture"], tuple(map(tuple, r["world"]))):r for r in baseline_ledger
              if r["method"] == "structural_span"}
    for spec in fixtures:
        graph = frozenset(map(tuple, spec["graph"]))
        candidates = frozenset(map(tuple, spec["candidates"]))
        old = Contract(spec["n"], graph, frozenset(map(tuple, spec["old_actions"])), spec["old_budget"])
        new = Contract(spec["n"], graph, frozenset(map(tuple, spec["new_actions"])), spec["new_budget"])
        bank = {b: native_signature(new, b, verification) for b in subsets(candidates)}
        local = Counter()
        for actual in subsets(candidates):
            known = compile_multi(old.n, old.graph, old.actions, old.budget, actual)
            unknown = hidden_candidates(old, candidates, known, Counter())
            local_counts = Counter()
            result, sensitive = check_full(new, known, unknown, actual, bank, verification, local_counts)
            producer.update(local_counts)
            local.update(local_counts)
            reference = lookup[(spec["id"], tuple(sorted(actual)))]
            assert result.stored == frozenset(map(tuple, reference["stored_output"]))
            assert len(result.transcript) == len(reference["transcript"])
            verification["same_task_baseline_checks"] += 1
            permutation = {i: new.n - 1 - i for i in range(new.n)}
            relabel = lambda items: frozenset((permutation[u], permutation[v]) for u, v in items)
            other_observed = []
            other = compile_from_source(new.n, relabel(graph), relabel(new.actions), new.budget,
                                         relabel(known), relabel(unknown),
                                         port(relabel(actual), relabel(unknown), len(unknown), other_observed),
                                         "v1", Counter())
            assert other.exact and other.stored == relabel(result.stored)
            assert frozenset(e for e, _ in other.transcript) == relabel(sensitive)
            verification["vertex_relabeling_checks"] += 1
            for permissions, budget in itertools.product(("all", "none", "omit_first", "alternating"), range(len(candidates) + 1)):
                allowed = permission_set(permissions, candidates)
                observed = []
                counts = Counter()
                partial = compile_from_source(new.n, graph, new.actions, new.budget, known, unknown,
                                               port(actual, allowed, budget, observed), "v1", counts)
                assert partial.transcript == tuple(observed)
                assert partial.exact == (sensitive <= allowed and len(sensitive) <= budget)
                assert all(e in allowed for e, _ in partial.transcript) and len(partial.transcript) <= budget
                validate_receipts(new, known, unknown, actual, partial, verification)
                compatible = [known | extra for extra in subsets(unknown)
                              if all((e in known | extra) == a for e, a in partial.transcript)]
                behavior_classes = {bank[b] for b in compatible}
                if partial.exact:
                    assert len(behavior_classes) == 1 and bank[partial.stored] == bank[actual]
                else:
                    assert len(behavior_classes) > 1
                    assert partial.receipts[-1].edge in sensitive
                bounded["exact" if partial.exact else "unresolved"] += 1
                bounded["configurations"] += 1
                bounded["source_queries"] += counts["source_queries"]
                verification["bounded_feasibility_checks"] += 1
            rows.append({"fixture":spec["id"], "world": sorted(actual), "known": sorted(known),
                         "unknown": sorted(unknown), "stored": sorted(result.stored),
                         "transcript": result.transcript, "necessary_query_set": sorted(sensitive),
                         "receipts": receipt_payload(result.receipts), "counts": dict(local_counts)})
        per_fixture.append({"fixture":spec["id"], "counts":dict(local)})
    return {"full":dict(producer), "bounded":dict(bounded), "fixtures":per_fixture}, rows


def boundary_attacks(verification):
    # A single requested reachability pair is an OR of two independent branches.
    c = Contract(4, frozenset({(1, 3), (2, 3)}), frozenset(), 0)
    unknown = frozenset({(0, 1), (0, 2)})
    answer = lambda b: bool(closure(4, c.graph | b)[0] & (1 << 3))
    assert answer(unknown) and all(answer(unknown - {e}) for e in unknown)
    assert not answer(frozenset())
    # Complete three-vertex directed graph has redundant individual edges, but
    # deleting them jointly loses full reachability. Acyclicity is load-bearing.
    cyclic = frozenset((u, v) for u in range(3) for v in range(3) if u != v)
    complete = closure(3, cyclic)
    assert all(closure(3, cyclic - {e}) == complete for e in cyclic)
    assert closure(3, frozenset()) != complete
    try:
        compile_from_source(3, frozenset(), frozenset(), 0, frozenset(), cyclic,
                            port(cyclic, cyclic, len(cyclic), []), "v1", Counter())
    except ValueError:
        verification["cyclic_inputs_rejected"] += 1
    else:
        raise AssertionError("cyclic input accepted")
    observed = []
    source = SourcePort("v2", unknown, len(unknown), lambda e, v: observed.append(e))
    stale = compile_from_source(4, c.graph, c.actions, c.budget, frozenset(), unknown, source, "v1", Counter())
    assert not stale.exact and stale.reason == "stale_source" and not observed
    verification["stale_sources_rejected"] += 1
    return {"partial_observation": {"single_coordinate_sensitive_set_size":0, "minimum_certificate_size_at_this_world":1},
            "cyclic_full_observation": {"single_coordinate_sensitive_set_size":0, "zero_query_certificate_impossible":True}}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    folder = Path(__file__).parent
    paths = [Path(__file__), folder/"ordered_source_compile_v1.py", folder/"ordered_source_compile_v1.json",
             folder/"adaptive_source_compile_v1.json", folder/"available_source_repair_v1.py",
             folder/"adaptive_source_compile_v1.py", folder/"multi_delta_budget_audit_v1.py",
             folder/"contract_budget_audit_v1.py"]
    hashes = {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    verification, producer = Counter(), Counter()
    exhaustive = exhaustive_audit(verification, producer)
    fixtures = json.loads((folder/"adaptive_source_compile_v1.json").read_text())["fixtures"]
    baseline_path = folder.parent.parent/"docs/OACR_COMMON_ARENA_RESULT_2026-10-01.cases.json.gz"
    baseline_rows = json.loads(gzip.decompress(baseline_path.read_bytes()))
    hashes[baseline_path.name] = hashlib.sha256(baseline_path.read_bytes()).hexdigest()
    control, rows = old_fixture_audit(fixtures, baseline_rows, verification)
    boundaries = boundary_attacks(verification)
    assert hashes == {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths} | {
        baseline_path.name:hashlib.sha256(baseline_path.read_bytes()).hexdigest()}
    ledger = args.out.with_suffix(".cases.json.gz")
    data = gzip.compress(json.dumps(rows, sort_keys=True, separators=(",", ":")).encode(), mtime=0)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    ledger.write_bytes(data)
    result = {"protocol_id":"OACR_ORDERED_SOURCE_COMPILE_V1", "exhaustive":exhaustive,
              "exhaustive_producer":dict(producer), "old_fixture_control":control,
              "verification":dict(verification), "boundary_attacks":boundaries,
              "input_sha256":hashes, "case_ledger":{"file":ledger.name,"sha256":hashlib.sha256(data).hexdigest()},
              "status":"same-author proof debugging passed; independent proof review, novelty and natural task evidence open"}
    args.out.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print(json.dumps({k:result[k] for k in ("exhaustive", "old_fixture_control", "verification", "boundary_attacks", "status")},indent=2))


if __name__ == "__main__":
    main()
