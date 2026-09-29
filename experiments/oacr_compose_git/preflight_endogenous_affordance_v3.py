"""OACR-COMPOSE-G v3 developmental H1 endogenous-affordance preflight.

No H2 transition is executed here.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "oacr_g5"))

from run_same_contract_git_v1 import execute_merge, git, natural_pair_banks  # noqa: E402

SOURCE_HEAD = "34f06850c16c7f7ac822b1adc71354f11b0f2ca3"
PROTOCOL_COMMIT = "93dfec441e1cf7927aa22771988c284d68b2ff26"


def ambient_target_pool(repo: Path, target_count: int = 96, merge_limit: int = 1024):
    lines = git(
        repo, "rev-list", "--merges", "--all", "--max-count=8000", "--parents"
    ).stdout.splitlines()
    targets = []
    seen = set()
    two_parent_seen = 0
    for line in lines:
        parts = line.split()
        if len(parts) != 3:
            continue
        two_parent_seen += 1
        target = parts[2]
        if target not in seen:
            seen.add(target)
            targets.append(target)
        if two_parent_seen >= merge_limit or len(targets) >= target_count:
            break
    if len(targets) < target_count:
        raise RuntimeError(
            f"ambient target pool underfilled: {len(targets)} < {target_count}"
        )
    return targets[:target_count]


def qualified(payload):
    return (
        payload["exit_code"] == 0
        and not payload["unmerged_paths"]
        and payload["merge_in_progress"]
        and payload["index_tree"] is not None
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--shard_index", type=int, required=True)
    ap.add_argument("--shards", type=int, default=8)
    args = ap.parse_args()

    if args.shards < 1 or not 0 <= args.shard_index < args.shards:
        raise RuntimeError("invalid shard")

    repo = Path(args.repo).resolve()
    source_head = git(repo, "rev-parse", "HEAD").stdout.strip()
    if source_head != SOURCE_HEAD:
        raise RuntimeError(f"source head mismatch: {source_head}")

    _, discovery, _, total_groups = natural_pair_banks(repo, 20000)
    if len(discovery) != 48:
        raise RuntimeError(f"unexpected discovery bank size: {len(discovery)}")
    targets = ambient_target_pool(repo)

    selected_pairs = [
        (idx, pair)
        for idx, pair in enumerate(discovery)
        if idx % args.shards == args.shard_index
    ]

    rows = []
    for idx, pair in selected_pairs:
        a, b = pair["A"], pair["B"]
        if git(repo, "rev-parse", f"{a}^{{tree}}").stdout.strip() != pair["tree"]:
            raise RuntimeError(f"A tree mismatch for pair {idx}")
        if git(repo, "rev-parse", f"{b}^{{tree}}").stdout.strip() != pair["tree"]:
            raise RuntimeError(f"B tree mismatch for pair {idx}")

        qa = []
        qb = []
        target_rows = []
        for target in targets:
            ma = execute_merge(repo, a, target)
            mb = execute_merge(repo, b, target)
            a_q = qualified(ma)
            b_q = qualified(mb)
            if a_q:
                qa.append(target)
            if b_q:
                qb.append(target)
            target_rows.append(
                {
                    "target": target,
                    "A_qualified": a_q,
                    "B_qualified": b_q,
                    "A_signature": ma["signature"],
                    "B_signature": mb["signature"],
                    "A_index_tree": ma["index_tree"],
                    "B_index_tree": mb["index_tree"],
                    "A_exit_code": ma["exit_code"],
                    "B_exit_code": mb["exit_code"],
                    "A_already_up_to_date": ma["already_up_to_date"],
                    "B_already_up_to_date": mb["already_up_to_date"],
                    "A_unmerged_count": len(ma["unmerged_paths"]),
                    "B_unmerged_count": len(mb["unmerged_paths"]),
                }
            )

        qa = sorted(qa)
        qb = sorted(qb)
        common = sorted(set(qa) & set(qb))
        signature_equal = all(
            row["A_signature"] == row["B_signature"]
            for row in target_rows
            if row["target"] in common
        )
        h1_equal = qa == qb and signature_equal
        rows.append(
            {
                "pair_index": idx,
                "tree": pair["tree"],
                "A": a,
                "B": b,
                "A_qualified_targets": qa,
                "B_qualified_targets": qb,
                "qualified_set_equal": qa == qb,
                "common_qualified_count": len(common),
                "qualified_signature_equal": signature_equal,
                "v3_H1_equivalent": h1_equal,
                "nonempty_common_action_set": bool(common),
                "target_rows": target_rows,
            }
        )

    summary = {
        "source_head": source_head,
        "same_tree_groups_available": total_groups,
        "development_bank_total": 48,
        "ambient_targets": len(targets),
        "shards": args.shards,
        "shard_index": args.shard_index,
        "pairs_in_shard": len(rows),
        "pairs_qualified_set_equal": sum(r["qualified_set_equal"] for r in rows),
        "pairs_v3_H1_equivalent": sum(r["v3_H1_equivalent"] for r in rows),
        "pairs_v3_H1_equivalent_nonempty": sum(
            r["v3_H1_equivalent"] and r["nonempty_common_action_set"] for r in rows
        ),
        "H2_outcomes_executed": 0,
    }
    payload = {
        "protocol": "OACR_COMPOSE_G_V3_ENDOGENOUS_AFFORDANCE_DEVELOPMENT_H1_PREFLIGHT",
        "protocol_commit": PROTOCOL_COMMIT,
        "ambient_target_rule": {
            "two_parent_merge_limit": 1024,
            "unique_second_parent_targets": 96,
            "order": "first occurrence in native rev-list --merges --all --parents order",
        },
        "ambient_targets": targets,
        "summary": summary,
        "pairs": rows,
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
