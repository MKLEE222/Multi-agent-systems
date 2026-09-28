"""OACR M1: exact finite operational-partition utilities.

This module intentionally supports only exact equivalence. Approximate learned
observations require a separately registered relation; silently quantizing logits
or taking tolerance-connected components can destroy transitivity and is not
allowed here.
"""
from __future__ import annotations

import hashlib
import json
import math
from collections import defaultdict
from typing import Any, Callable, Dict, Hashable, Iterable, List, Mapping, Sequence, Tuple


def canonical_json(x: Any) -> str:
    return json.dumps(x, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def signature_id(x: Any) -> str:
    return hashlib.sha256(canonical_json(x).encode("utf-8")).hexdigest()


def partition_from_signatures(
    items: Iterable[Hashable],
    signature_fn: Callable[[Hashable], Any],
) -> List[List[Hashable]]:
    groups: Dict[str, List[Hashable]] = defaultdict(list)
    for item in items:
        groups[signature_id(signature_fn(item))].append(item)
    return sorted(
        [sorted(v, key=str) for v in groups.values()],
        key=lambda block: (len(block), [str(x) for x in block]),
    )


def block_index(partition: Sequence[Sequence[Hashable]]) -> Dict[Hashable, int]:
    out: Dict[Hashable, int] = {}
    for i, block in enumerate(partition):
        for x in block:
            if x in out:
                raise ValueError(f"item appears in multiple blocks: {x!r}")
            out[x] = i
    return out


def refinement_relation(
    candidate: Sequence[Sequence[Hashable]],
    required: Sequence[Sequence[Hashable]],
) -> Dict[str, Any]:
    """Compare candidate representation partition to required operational partition.

    candidate is under-refined if it merges any pair that required separates.
    candidate is over-refined if it separates any pair that required merges.
    """
    ci, ri = block_index(candidate), block_index(required)
    if set(ci) != set(ri):
        raise ValueError("candidate and required partitions must cover identical items")
    items = sorted(ci, key=str)
    under, over = [], []
    for i, a in enumerate(items):
        for b in items[i + 1 :]:
            c_same = ci[a] == ci[b]
            r_same = ri[a] == ri[b]
            if c_same and not r_same:
                under.append((a, b))
            elif (not c_same) and r_same:
                over.append((a, b))
    return {
        "items": len(items),
        "candidate_blocks": len(candidate),
        "required_blocks": len(required),
        "under_refinement_pairs": under,
        "over_refinement_pairs": over,
        "under_refinement_count": len(under),
        "over_refinement_count": len(over),
        "finite_bank_adequate": len(under) == 0,
        "partition_exact_match": len(under) == 0 and len(over) == 0,
    }


def information_burden_bits(partition: Sequence[Sequence[Hashable]]) -> float:
    """Cardinality lower bound log2(number of required equivalence classes)."""
    n = len(partition)
    if n < 1:
        raise ValueError("partition must contain at least one block")
    return math.log2(n)


def nested_partition_check(
    coarse: Sequence[Sequence[Hashable]],
    fine: Sequence[Sequence[Hashable]],
) -> Dict[str, Any]:
    """Check that every fine block is contained in one coarse block."""
    ci, fi = block_index(coarse), block_index(fine)
    if set(ci) != set(fi):
        raise ValueError("partitions must cover identical items")
    violations = []
    for block in fine:
        parents = {ci[x] for x in block}
        if len(parents) != 1:
            violations.append(list(block))
    return {
        "is_refinement": not violations,
        "violating_fine_blocks": violations,
        "coarse_blocks": len(coarse),
        "fine_blocks": len(fine),
        "coarse_information_bits": information_burden_bits(coarse),
        "fine_information_bits": information_burden_bits(fine),
        "delta_information_bits": (
            information_burden_bits(fine) - information_burden_bits(coarse)
        ),
    }


def first_failure_horizon(
    pair: Tuple[Hashable, Hashable],
    partitions_by_horizon: Mapping[int, Sequence[Sequence[Hashable]]],
) -> int | None:
    a, b = pair
    for h in sorted(partitions_by_horizon):
        idx = block_index(partitions_by_horizon[h])
        if idx[a] != idx[b]:
            return h
    return None


def behavior_signatures_exact(
    states: Sequence[Hashable],
    observations: Mapping[Hashable, Any],
    actions: Sequence[Hashable],
    successor: Callable[[Hashable, Hashable], Tuple[Any, Hashable]],
    horizon: int,
) -> Dict[int, Dict[Hashable, Any]]:
    """Construct exact finite-horizon signatures.

    successor(state, action) -> (status, next_state).
    All next states must have entries in observations.
    """
    sigs: Dict[int, Dict[Hashable, Any]] = {
        0: {s: ("OBS", observations[s]) for s in states}
    }
    all_states = set(states)

    for h in range(1, horizon + 1):
        current: Dict[Hashable, Any] = {}
        prev = sigs[h - 1]
        for s in states:
            branches = []
            for a in actions:
                status, nxt = successor(s, a)
                if nxt not in all_states:
                    raise ValueError(
                        f"successor state {nxt!r} is outside the registered closed bank"
                    )
                branches.append((a, status, prev[nxt]))
            current[s] = ("OBS", observations[s], "BRANCHES", branches)
        sigs[h] = current
    return sigs


def partitions_from_behavior_signatures(
    signatures_by_horizon: Mapping[int, Mapping[Hashable, Any]]
) -> Dict[int, List[List[Hashable]]]:
    return {
        h: partition_from_signatures(sig.keys(), lambda s, sig=sig: sig[s])
        for h, sig in signatures_by_horizon.items()
    }



def _entropy_probs(ps):
    return -sum(p * math.log2(p) for p in ps if p > 0.0)


def directional_information_gap(
    representation_partition: Sequence[Sequence[Hashable]],
    operational_partition: Sequence[Sequence[Hashable]],
    weights: Mapping[Hashable, float] | None = None,
) -> Dict[str, float]:
    """Directional partition mismatch in bits.

    U = H(O|R): operational information omitted by the representation partition.
    E = H(R|O): representation-class information in excess of the operational partition.

    The default distribution is uniform over registered items.
    These are class-label information quantities, not physical storage sizes.
    """
    ri = block_index(representation_partition)
    oi = block_index(operational_partition)
    if set(ri) != set(oi):
        raise ValueError("partitions must cover identical items")
    items = sorted(ri, key=str)
    if weights is None:
        p = {x: 1.0 / len(items) for x in items}
    else:
        if set(weights) != set(items):
            raise ValueError("weights must be specified for exactly the partition items")
        total = sum(float(weights[x]) for x in items)
        if total <= 0:
            raise ValueError("weights must have positive total mass")
        p = {x: float(weights[x]) / total for x in items}
        if any(v < 0 for v in p.values()):
            raise ValueError("weights must be nonnegative")

    pr = defaultdict(float)
    po = defaultdict(float)
    joint = defaultdict(float)
    for x in items:
        w = p[x]
        pr[ri[x]] += w
        po[oi[x]] += w
        joint[(ri[x], oi[x])] += w

    h_r = _entropy_probs(pr.values())
    h_o = _entropy_probs(po.values())
    h_joint = _entropy_probs(joint.values())
    h_o_given_r = h_joint - h_r
    h_r_given_o = h_joint - h_o
    mutual_information = h_r + h_o - h_joint
    return {
        "representation_entropy_bits": h_r,
        "operational_entropy_bits": h_o,
        "joint_entropy_bits": h_joint,
        "mutual_information_bits": mutual_information,
        "omission_U_bits": h_o_given_r,
        "excess_E_bits": h_r_given_o,
        "variation_of_information_bits": h_o_given_r + h_r_given_o,
        "adequate_almost_surely": abs(h_o_given_r) < 1e-12,
        "partition_match_almost_surely": (
            abs(h_o_given_r) < 1e-12 and abs(h_r_given_o) < 1e-12
        ),
    }
