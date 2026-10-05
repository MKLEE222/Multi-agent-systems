"""Bounded proof review of existing OACR operators and closure boundary.

No natural/held-out evidence or novelty clearance. The closure target table is
public semantics; source bits are accessible to the policy only via queries.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path
import random

from available_source_repair_v1 import SourcePort
from ordered_source_compile_v1 import compile_from_source, check_proof, transport_paths


def masks(n):
    return range(1 << n)


def bits(mask):
    return [i for i in range(mask.bit_length()) if mask & (1 << i)]


def subset_masks(mask):
    return [x for x in range(mask + 1) if x & mask == x]


def policy(cl, n, source):
    """Read public closure table, never actual source bits directly."""
    positive, possible, queried = 0, (1 << n) - 1, []
    while cl[positive] != cl[possible]:
        extreme = [i for i in bits(possible)
                   if cl[possible ^ (1 << i)] != cl[possible]]
        candidates = [i for i in extreme if not positive & (1 << i)]
        assert candidates
        i = candidates[0]
        queried.append(i)
        if source(i):
            positive |= 1 << i
        else:
            possible ^= 1 << i
    return queried, cl[positive]


def closure_audit():
    counts, first_boundary = Counter(), None
    for n in range(1, 5):
        top = (1 << n) - 1
        for code in range(1 << top):
            closed = [x for x in range(top) if code & (1 << x)] + [top]
            family = set(closed)
            if any(a & b not in family for a in closed for b in closed):
                continue
            cl = []
            for source in masks(n):
                value = top
                for x in closed:
                    if source & x == source:
                        value &= x
                cl.append(value)
            generators = {x: [b for b in masks(n) if cl[b] == x] for x in closed}
            minimal = {x: [b for b in gen if not any(a != b and a & b == a for a in gen)]
                       for x, gen in generators.items()}
            unique = all(len(v) == 1 for v in minimal.values())
            complete_everywhere = True
            for actual in masks(n):
                sensitive = sum(1 << i for i in range(n) if cl[actual ^ (1 << i)] != cl[actual])
                compatible = [other for other in masks(n) if (actual ^ other) & sensitive == 0]
                complete = all(cl[other] == cl[actual] for other in compatible)
                complete_everywhere &= complete
                counts["source_sets"] += 1
                if not complete and first_boundary is None:
                    other = next(o for o in compatible if cl[o] != cl[actual])
                    first_boundary = {"n": n, "closed_sets": closed, "source": actual,
                                      "sensitive_mask": sensitive, "compatible_source": other,
                                      "closures": [cl[actual], cl[other]]}
                if unique:
                    transcript = []
                    def source(i):
                        transcript.append(i)
                        return bool(actual & (1 << i))
                    queried, target = policy(cl, n, source)
                    assert queried == transcript and target == cl[actual]
                    assert sum(1 << i for i in queried) == sensitive
                    counts["generic_pointwise_policy_checks"] += 1
            assert unique == complete_everywhere
            counts["unique_generation_iff_certificate_checks"] += 1
            counts["uniquely_generated" if unique else "not_uniquely_generated"] += 1
    return {"counts": dict(counts), "first_joint_ambiguity": first_boundary}


def subsets(edges):
    ordered = sorted(edges)
    for mask in range(1 << len(ordered)):
        yield frozenset(e for i, e in enumerate(ordered) if mask & (1 << i))


def reach(n, edges):
    """Fresh independent DFS native implementation; no flow/bitset imports."""
    adjacency = [[] for _ in range(n)]
    for u, v in edges:
        adjacency[u].append(v)
    output = set()
    for u in range(n):
        seen, queue = {u}, [u]
        while queue:
            for v in adjacency[queue.pop()]:
                if v not in seen:
                    seen.add(v)
                    queue.append(v)
        output.update((u, v) for v in seen if u != v)
    return frozenset(output)


def signature(n, graph, actions, h, actual):
    return tuple(reach(n, graph - failed | actual)
                 for failed in subsets(actions) if len(failed) <= h)


def port(actual, unknown, transcript):
    def query(e, epoch):
        assert epoch == "review_v1" and e in unknown and e not in [x for x, _ in transcript]
        answer = e in actual
        transcript.append((e, answer))
        return answer
    return SourcePort("review_v1", unknown, len(unknown), query)


def dag_audit(seed):
    rng, counts, digest = random.Random(seed), Counter(), hashlib.sha256()
    for case in range(60):
        n = 5 + case % 4
        edges = [(u, v) for u in range(n) for v in range(u + 1, n)]
        rng.shuffle(edges)
        unknown = frozenset(edges[:1 + case % 5])
        rest = edges[len(unknown):]
        graph = frozenset(e for e in rest if rng.randrange(3))
        known = frozenset(e for e in rest if e not in graph and rng.randrange(2))
        deletable = sorted(graph)
        rng.shuffle(deletable)
        actions = frozenset(deletable[:min(5, len(graph))])
        h = min(case % 3, len(actions))
        bank = {known | extra: signature(n, graph, actions, h, known | extra)
                for extra in subsets(unknown)}
        for actual, behavior in bank.items():
            transcript = []
            result = compile_from_source(n, graph, actions, h, known, unknown,
                                         port(actual, unknown, transcript), "review_v1", Counter())
            sensitive = frozenset(e for e in unknown if bank[actual ^ {e}] != behavior)
            assert result.exact and result.transcript == tuple(transcript)
            assert frozenset(e for e, _ in transcript) == sensitive
            assert signature(n, graph, actions, h, result.stored) == behavior
            assert all(signature(n, graph, actions, h, actual - {e}) != behavior for e in result.stored)
            assert all(other_behavior == behavior for other, other_behavior in bank.items()
                       if all((e in other) == a for e, a in transcript))
            prefix = frozenset()
            for receipt in result.receipts:
                assert check_proof(n, graph | prefix, actions, h, receipt.edge, receipt.proof)
                if receipt.proof.kind == "cut" and receipt.answer:
                    prefix |= {receipt.edge}
                counts["receipt_checks"] += 1
            mapping = lambda es: frozenset((n-1-u, n-1-v) for u, v in es)
            other_transcript = []
            mapped = compile_from_source(n, mapping(graph), mapping(actions), h,
                                         mapping(known), mapping(unknown),
                                         port(mapping(actual), mapping(unknown), other_transcript),
                                         "review_v1", Counter())
            assert mapped.exact and mapped.stored == mapping(result.stored)
            assert frozenset(e for e, _ in mapped.transcript) == mapping(sensitive)
            digest.update(json.dumps([case, sorted(actual), sorted(result.stored), sorted(sensitive)]).encode()+b"\n")
            counts["native_pointwise_and_relabel_checks"] += 1
        counts["public_configurations"] += 1
    return {"counts": dict(counts), "ledger_digest": digest.hexdigest()}


def transport_attack():
    n = 6
    graph = frozenset({(0,1), (1,2), (2,3), (4,5)})
    actions = frozenset({(0,1), (4,5)})
    b, e, f = (0,2), (0,3), (4,5)
    result = compile_from_source(n, graph, actions, 1, frozenset({b}), frozenset({e}),
                                 port(frozenset({b}), frozenset({e}), []), "review_v1", Counter())
    assert result.exact and result.stored == {b} and not result.transcript
    proof = next(r.proof for r in result.receipts if r.edge == e)
    moved = transport_paths(proof, f)
    post, remaining = graph - {f}, actions - {f}
    assert check_proof(n, post | {b}, remaining, 0, e, moved)
    canonical = compile_from_source(n, post, remaining, 0, frozenset({b}), frozenset(),
                                    port(frozenset({b}), frozenset(), []), "review_v1", Counter())
    assert canonical.exact and not canonical.stored
    assert not check_proof(n, post | canonical.stored, remaining, 0, e, moved)
    assert reach(n, post | {b}) == reach(n, post)
    return {"graph": sorted(graph), "actions": sorted(actions), "old_stored": [b],
            "omitted_unknown": e, "consumed_action": f, "old_paths": proof.paths,
            "transported_paths": moved.paths, "new_canonical_stored": [],
            "native_preserved": True, "valid_with_persistent_support": True,
            "valid_after_canonical_coarsening": False,
            "interpretation": "existing scoped transport is correct; stronger free-coarsening transport is false"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    protocol_path = Path(__file__).with_suffix(".json")
    protocol = json.loads(protocol_path.read_text())
    paths = [Path(__file__), protocol_path, Path(__file__).with_name("ordered_source_compile_v1.py"),
             Path(__file__).with_name("available_source_repair_v1.py"),
             Path(__file__).with_name("contract_budget_audit_v1.py")]
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    result = {"protocol": protocol["protocol_id"], "reviewed_commit": protocol["reviewed_commit"],
              "closure_audit": closure_audit(), "dag_audit": dag_audit(protocol["seed"]),
              "transport_attack": transport_attack(), "input_sha256": hashes,
              "status": "bounded proof debugging passed; prior-art and natural evidence gates open"}
    assert hashes == {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
