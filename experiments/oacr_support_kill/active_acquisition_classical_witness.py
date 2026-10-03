#!/usr/bin/env python3
"""Exhaustive classical SBFE witness; no benchmark, model, or frozen input.

Psi = (x1 AND x2) OR (x3 AND x4), independent fair bits, unit query costs.
This verifies established decision-tree/certificate distinctions. It is not an
OCAR algorithm, performance claim, or official-task experiment.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
from functools import lru_cache
from itertools import combinations, permutations, product
import json
from pathlib import Path


UNKNOWN = -1
N = 4
WORLDS = tuple(product((0, 1), repeat=N))
PARTIALS = tuple(product((UNKNOWN, 0, 1), repeat=N))
ORDERS = tuple(permutations(range(N)))
EMPTY = (UNKNOWN,) * N


def psi(world: tuple[int, ...]) -> int:
    return int((world[0] == world[1] == 1) or (world[2] == world[3] == 1))


TRUTH_TABLE = {world: psi(world) for world in WORLDS}


@lru_cache(None)
def compatible(partial: tuple[int, ...]) -> tuple[tuple[int, ...], ...]:
    return tuple(
        world for world in WORLDS
        if all(value == UNKNOWN or value == world[i]
               for i, value in enumerate(partial))
    )


@lru_cache(None)
def truth_table_certificate(partial: tuple[int, ...]) -> int | None:
    """Universal quantification over compatible worlds; no DNF shortcut."""
    labels = {TRUTH_TABLE[world] for world in compatible(partial)}
    return next(iter(labels)) if len(labels) == 1 else None


def independent_dnf_certificate(partial: tuple[int, ...]) -> int | None:
    """Separate formula-specific certificate rule to cross-check semantics."""
    terms = ((0, 1), (2, 3))
    if any(all(partial[i] == 1 for i in term) for term in terms):
        return 1
    if all(any(partial[i] == 0 for i in term) for term in terms):
        return 0
    return None


def reveal(partial: tuple[int, ...], index: int, answer: int) -> tuple[int, ...]:
    assert partial[index] == UNKNOWN, "Only a hole may be queried."
    return partial[:index] + (answer,) + partial[index + 1:]


@lru_cache(None)
def expected_dp(partial: tuple[int, ...]) -> Fraction:
    if truth_table_certificate(partial) is not None:
        return Fraction(0)
    return min(
        Fraction(1) + sum(
            (expected_dp(reveal(partial, index, answer)) for answer in (0, 1)),
            Fraction(0),
        ) / 2
        for index, value in enumerate(partial) if value == UNKNOWN
    )


@lru_cache(None)
def minimax_dp(partial: tuple[int, ...]) -> int:
    if truth_table_certificate(partial) is not None:
        return 0
    return min(
        1 + max(minimax_dp(reveal(partial, index, answer)) for answer in (0, 1))
        for index, value in enumerate(partial) if value == UNKNOWN
    )


def expected_choice(partial: tuple[int, ...]) -> int:
    candidates = (
        (Fraction(1) + sum(
            (expected_dp(reveal(partial, index, answer)) for answer in (0, 1)),
            Fraction(0),
        ) / 2, index)
        for index, value in enumerate(partial) if value == UNKNOWN
    )
    return min(candidates)[1]


def minimax_choice(partial: tuple[int, ...]) -> int:
    return min(
        (1 + max(minimax_dp(reveal(partial, index, answer)) for answer in (0, 1)),
         index)
        for index, value in enumerate(partial) if value == UNKNOWN
    )[1]


def execute_policy(world: tuple[int, ...], choose) -> tuple[int, tuple[int, ...]]:
    partial = EMPTY
    steps = 0
    while truth_table_certificate(partial) is None:
        index = choose(partial)
        partial = reveal(partial, index, world[index])
        steps += 1
    assert truth_table_certificate(partial) == TRUTH_TABLE[world]
    assert independent_dnf_certificate(partial) == TRUTH_TABLE[world]
    return steps, partial


def execute_order(world: tuple[int, ...], order: tuple[int, ...]) -> int:
    partial = EMPTY
    steps = 0
    for index in order:
        if truth_table_certificate(partial) is not None:
            break
        partial = reveal(partial, index, world[index])
        steps += 1
    assert truth_table_certificate(partial) == TRUTH_TABLE[world]
    return steps


SUBSETS = tuple(subset for size in range(N + 1)
                for subset in combinations(range(N), size))


def offline_certificate_cost(world: tuple[int, ...]) -> int:
    """A lower bound with actual answers known in advance, not a legal policy."""
    for subset in SUBSETS:
        partial = tuple(world[i] if i in subset else UNKNOWN for i in range(N))
        if truth_table_certificate(partial) == TRUTH_TABLE[world]:
            return len(subset)
    raise AssertionError("The complete input must be a certificate.")


def batch_determines(subset: tuple[int, ...]) -> bool:
    """Every possible answer to this fixed batch must determine Psi."""
    signatures: dict[tuple[int, ...], int] = {}
    for world in WORLDS:
        signature = tuple(world[i] for i in subset)
        label = TRUTH_TABLE[world]
        if signature in signatures and signatures[signature] != label:
            return False
        signatures[signature] = label
    return True


def fraction_json(value: Fraction) -> dict[str, int | str]:
    return {"numerator": value.numerator, "denominator": value.denominator,
            "exact": str(value)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    certificates = {"0": 0, "1": 0, "ambiguous": 0}
    for partial in PARTIALS:
        semantic = truth_table_certificate(partial)
        assert semantic == independent_dnf_certificate(partial)
        certificates["ambiguous" if semantic is None else str(semantic)] += 1
        assert (expected_dp(partial) == 0) == (semantic is not None)
        assert (minimax_dp(partial) == 0) == (semantic is not None)

    order_results = []
    for order in ORDERS:
        costs = [execute_order(world, order) for world in WORLDS]
        order_results.append({"order": [i + 1 for i in order],
                              "expected_cost": fraction_json(Fraction(sum(costs), 16)),
                              "worst_cost": max(costs)})
    best_order = min(Fraction(row["expected_cost"]["numerator"],
                              row["expected_cost"]["denominator"])
                     for row in order_results)
    adaptive_costs = [execute_policy(world, expected_choice)[0] for world in WORLDS]
    minimax_costs = [execute_policy(world, minimax_choice)[0] for world in WORLDS]
    offline_costs = [offline_certificate_cost(world) for world in WORLDS]
    determining_batches = [subset for subset in SUBSETS if batch_determines(subset)]
    minimum_batch = min(map(len, determining_batches))

    assert len(WORLDS) == 16 and len(PARTIALS) == 81 and len(ORDERS) == 24
    assert expected_dp(EMPTY) == Fraction(sum(adaptive_costs), 16) == Fraction(21, 8)
    assert best_order == Fraction(25, 8)
    assert minimax_dp(EMPTY) == max(minimax_costs) == 4
    assert minimum_batch == 4
    assert set(offline_costs) == {2}

    result = {
        "schema": "oacr_support_kill_classical_witness_v1",
        "date": "2026-10-03",
        "classification": "classical_control_capability_witness",
        "not_claimed": ["OCAR gain", "new algorithm", "official-task experiment"],
        "inputs": {"formula": "(x1 AND x2) OR (x3 AND x4)",
                   "unknown_bits": 4, "query_cost_each": 1,
                   "true_probability_each": fraction_json(Fraction(1, 2)),
                   "distribution": "independent product", "query_legality": "holes only",
                   "positive_terminal": "all compatible worlds satisfy Psi",
                   "negative_terminal": "all compatible worlds falsify Psi"},
        "enumeration": {"worlds": len(WORLDS), "partial_observations": len(PARTIALS),
                        "fixed_orders": len(ORDERS), "batch_subsets": len(SUBSETS),
                        "certificate_counts": certificates,
                        "dnf_vs_truth_table_crosscheck": "all 81 states pass"},
        "results": {"optimal_adaptive_expected_cost": fraction_json(expected_dp(EMPTY)),
                    "optimal_fixed_order_expected_cost": fraction_json(best_order),
                    "optimal_minimax_cost": minimax_dp(EMPTY),
                    "minimum_determining_batch_cost": minimum_batch,
                    "offline_certificate_cost_all_worlds": sorted(set(offline_costs)),
                    "expected_offline_certificate_cost": fraction_json(Fraction(sum(offline_costs), 16)),
                    "fixed_order_to_adaptive_ratio": fraction_json(best_order / expected_dp(EMPTY)),
                    "all_world_positive_commit_feasible": False},
        "truth_table": [{"world": list(world), "Psi": TRUTH_TABLE[world],
                         "expected_optimal_policy_realized_cost": adaptive_costs[j],
                         "minimax_optimal_policy_realized_cost": minimax_costs[j],
                         "offline_certificate_cost": offline_costs[j]}
                        for j, world in enumerate(WORLDS)],
        "fixed_order_results": order_results,
        "checks": "all assertions passed",
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"out": str(args.out), "checks": result["checks"],
                      "results": result["results"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
