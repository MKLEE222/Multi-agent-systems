"""OACR-COMPOSE-G v3 developmental H2 endogenous-affordance search.

Consumes one frozen H1 preflight shard.  It executes H2 only for pairs that
already satisfy the v3 H1-equivalence gate.  Developmental output only.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "oacr_g5"))
sys.path.insert(0, str(HERE))

from run_same_contract_git_v1 import execute_merge, git  # noqa: E402
from run_depth2_git_v1 import deterministic_merge_commit  # noqa: E402

SOURCE_HEAD = "34f06850c16c7f7ac822b1adc71354f11b0f2ca3"
PROTOCOL_COMMIT = "93dfec441e1cf7927aa22771988c284d68b2ff26"


def qualified(payload):
    return (
        payload["exit_code"] == 0
        and not payload["unmerged_paths"]
        and payload["merge_in_progress"]
        and payload["index_tree"] is not None
    )


def scan_interface(repo: Path, head: str, targets):
    q = []
    rows = {}
    for target in targets:
        m = execute_merge(repo, head, target)
        is_q = qualified(m)
        if is_q:
            q.append(target)
        rows[target] = {
            "qualified": is_q,
            "signature": m["signature"],
            "index_tree": m["index_tree"],
            "exit_code": m["exit_code"],
            "already_up_to_date": m["already_up_to_date"],
            "unmerged_count": len(m["unmerged_paths"]),
        }
    return sorted(q), rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--h1_shard", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    h1 = json.loads(Path(args.h1_shard).read_text())
    if git(repo, "rev-parse", "HEAD").stdout.strip() != SOURCE_HEAD:
        raise RuntimeError("source checkout mismatch")
    if h1.get("protocol") != "OACR_COMPOSE_G_V3_ENDOGENOUS_AFFORDANCE_DEVELOPMENT_H1_PREFLIGHT":
        raise RuntimeError("unexpected H1 shard")
    if h1.get("protocol_commit") != PROTOCOL_COMMIT:
        raise RuntimeError("H1 protocol commit mismatch")
    if h1["summary"].get("H2_outcomes_executed") != 0:
        raise RuntimeError("H1 shard claims H2 execution")

    targets = h1["ambient_targets"]
    results = []
    for pair in h1["pairs"]:
        if not (
            pair["v3_H1_equivalent"]
            and pair["nonempty_common_action_set"]
        ):
            continue

        a, b = pair["A"], pair["B"]
        t1_candidates = sorted(pair["A_qualified_targets"])[:4]
        pair_rows = []

        h1_by_target = {row["target"]: row for row in pair["target_rows"]}
        for t1 in t1_candidates:
            frozen = h1_by_target[t1]
            if not (
                frozen["A_qualified"]
                and frozen["B_qualified"]
                and frozen["A_signature"] == frozen["B_signature"]
            ):
                raise RuntimeError(f"invalid frozen t1 eligibility: {pair['pair_index']} {t1}")

            a1 = deterministic_merge_commit(repo, a, t1)
            b1 = deterministic_merge_commit(repo, b, t1)
            if not a1["ok"] or not b1["ok"]:
                pair_rows.append({
                    "t1": t1,
                    "status": "STEP1_MATERIALIZATION_FAILURE",
                    "H2_interface_scanned": False,
                })
                continue

            current_read_equal = a1["tree"] == b1["tree"]
            if not current_read_equal:
                pair_rows.append({
                    "t1": t1,
                    "status": "STEP1_TREE_MISMATCH",
                    "A1_tree": a1["tree"],
                    "B1_tree": b1["tree"],
                    "H2_interface_scanned": False,
                })
                continue

            qa, ia = scan_interface(repo, a1["commit"], targets)
            qb, ib = scan_interface(repo, b1["commit"], targets)
            qset_diff = qa != qb
            common = sorted(set(qa) & set(qb))
            outcome_diff_targets = [
                target for target in common
                if ia[target]["signature"] != ib[target]["signature"]
            ]
            separated = qset_diff or bool(outcome_diff_targets)

            only_a = sorted(set(qa) - set(qb))
            only_b = sorted(set(qb) - set(qa))
            pair_rows.append({
                "t1": t1,
                "status": "H2_SEPARATED" if separated else "H2_EQUIVALENT",
                "A1_commit": a1["commit"],
                "B1_commit": b1["commit"],
                "intermediate_tree": a1["tree"],
                "current_read_equal": True,
                "A1_qualified_targets": qa,
                "B1_qualified_targets": qb,
                "qualification_set_diverges": qset_diff,
                "qualified_only_A": only_a,
                "qualified_only_B": only_b,
                "common_qualified_count": len(common),
                "outcome_divergence_targets": outcome_diff_targets,
                "H2_interface_scanned": True,
            })

        results.append({
            "pair_index": pair["pair_index"],
            "tree": pair["tree"],
            "A": a,
            "B": b,
            "initial_common_qualified_count": pair["common_qualified_count"],
            "t1_candidates": t1_candidates,
            "t1_results": pair_rows,
            "has_H2_separation": any(r["status"] == "H2_SEPARATED" for r in pair_rows),
        })

    summary = {
        "shard_index": h1["summary"]["shard_index"],
        "eligible_H1_pairs": len(results),
        "t1_attempts": sum(len(r["t1_results"]) for r in results),
        "step1_tree_mismatches": sum(
            x["status"] == "STEP1_TREE_MISMATCH"
            for r in results for x in r["t1_results"]
        ),
        "H2_interfaces_scanned": sum(
            bool(x.get("H2_interface_scanned"))
            for r in results for x in r["t1_results"]
        ),
        "H2_separated_t1": sum(
            x["status"] == "H2_SEPARATED"
            for r in results for x in r["t1_results"]
        ),
        "pairs_with_H2_separation": sum(r["has_H2_separation"] for r in results),
    }
    payload = {
        "protocol": "OACR_COMPOSE_G_V3_ENDOGENOUS_AFFORDANCE_DEVELOPMENT_H2",
        "protocol_commit": PROTOCOL_COMMIT,
        "source_head": SOURCE_HEAD,
        "ambient_targets": targets,
        "summary": summary,
        "results": results,
        "claim_status": "DEVELOPMENTAL_ONLY",
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
