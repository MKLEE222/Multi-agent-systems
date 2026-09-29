"""Fast developmental mirror for OACR-COMPOSE-G v3 H1 preflight.

Uses Git merge-tree + ancestry only. Diagnostic, never authoritative over the
native git-merge H1 preflight.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "oacr_g5"))

from run_same_contract_git_v1 import git, is_ancestor, natural_pair_banks  # noqa: E402
from preflight_endogenous_affordance_v3 import ambient_target_pool  # noqa: E402

SOURCE_HEAD = "34f06850c16c7f7ac822b1adc71354f11b0f2ca3"
HEX = re.compile(r"^[0-9a-f]{40,64}$")


def merge_tree_qualification(repo: Path, head: str, target: str):
    if is_ancestor(repo, target, head):
        return {"qualified": False, "reason": "already_up_to_date", "tree": None}
    p = git(repo, "merge-tree", "--write-tree", head, target, check=False)
    lines = [x.strip() for x in p.stdout.splitlines() if x.strip()]
    tree = lines[0] if lines and HEX.match(lines[0]) else None
    if p.returncode == 0 and tree:
        return {"qualified": True, "reason": "clean_real_merge", "tree": tree}
    return {
        "qualified": False,
        "reason": "conflict_or_merge_tree_failure",
        "tree": tree,
        "exit_code": p.returncode,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    repo = Path(args.repo).resolve()

    if git(repo, "rev-parse", "HEAD").stdout.strip() != SOURCE_HEAD:
        raise RuntimeError("source head mismatch")
    _, discovery, _, total_groups = natural_pair_banks(repo, 20000)
    targets = ambient_target_pool(repo)

    rows = []
    for idx, pair in enumerate(discovery):
        a, b = pair["A"], pair["B"]
        qa, qb = [], []
        target_rows = []
        for target in targets:
            ma = merge_tree_qualification(repo, a, target)
            mb = merge_tree_qualification(repo, b, target)
            if ma["qualified"]:
                qa.append(target)
            if mb["qualified"]:
                qb.append(target)
            target_rows.append({
                "target": target,
                "A": ma,
                "B": mb,
                "qualified_equal": ma["qualified"] == mb["qualified"],
                "qualified_tree_equal": (
                    (not ma["qualified"] and not mb["qualified"])
                    or (
                        ma["qualified"] and mb["qualified"]
                        and ma["tree"] == mb["tree"]
                    )
                ),
            })
        qa, qb = sorted(qa), sorted(qb)
        common = sorted(set(qa) & set(qb))
        tree_equal = all(
            r["A"]["tree"] == r["B"]["tree"]
            for r in target_rows
            if r["target"] in common
        )
        rows.append({
            "pair_index": idx,
            "tree": pair["tree"],
            "A": a,
            "B": b,
            "A_qualified_targets": qa,
            "B_qualified_targets": qb,
            "qualified_set_equal": qa == qb,
            "qualified_merge_tree_equal": tree_equal,
            "predicted_v3_H1_equivalent": qa == qb and tree_equal,
            "common_qualified_count": len(common),
        })

    candidates = [
        r for r in rows
        if r["predicted_v3_H1_equivalent"] and r["common_qualified_count"] > 0
    ]
    payload = {
        "protocol": "OACR_COMPOSE_G_V3_MERGE_TREE_DIAGNOSTIC_ONLY",
        "claim_status": "DIAGNOSTIC_ONLY_NATIVE_CONFIRMATION_REQUIRED",
        "source_head": SOURCE_HEAD,
        "ambient_targets": targets,
        "summary": {
            "same_tree_groups_available": total_groups,
            "development_pairs": len(rows),
            "ambient_targets": len(targets),
            "predicted_H1_equivalent": sum(r["predicted_v3_H1_equivalent"] for r in rows),
            "predicted_H1_equivalent_nonempty": len(candidates),
        },
        "candidate_pairs": candidates,
        "all_pairs": rows,
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2))
    print(json.dumps(payload["summary"], indent=2))


if __name__ == "__main__":
    main()
