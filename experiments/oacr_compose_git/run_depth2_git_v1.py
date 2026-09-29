"""OACR-COMPOSE-G v1: prospective depth-2 native Git continuation test."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
G5 = HERE.parent / "oacr_g5"
sys.path.insert(0, str(G5))

from run_same_contract_git_v1 import (  # noqa: E402
    execute_merge,
    is_ancestor,
    merge_base,
    natural_pair_banks,
    select_targets,
    evaluate,
    git,
)

SOURCE_HEAD = "34f06850c16c7f7ac822b1adc71354f11b0f2ca3"


def evenly_spaced(items, k):
    if k >= len(items):
        return list(items)
    idxs = []
    for i in range(k):
        idx = round(i * (len(items) - 1) / (k - 1))
        if idx not in idxs:
            idxs.append(idx)
    if len(idxs) != k:
        for i in range(len(items)):
            if i not in idxs:
                idxs.append(i)
            if len(idxs) == k:
                break
        idxs = sorted(idxs)
    return [items[i] for i in idxs]


def run(cwd: Path, *args: str, check: bool = True, extra_env=None):
    env = {**os.environ, "GIT_CONFIG_NOSYSTEM": "1", **(extra_env or {})}
    p = subprocess.run(
        list(args),
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=env,
    )
    if check and p.returncode != 0:
        raise RuntimeError(f"command failed ({p.returncode}): {' '.join(args)}\n{p.stdout}")
    return p


def fresh(repo: Path, commit: str):
    run(repo, "git", "merge", "--abort", check=False)
    run(repo, "git", "reset", "--hard", "-q", commit)
    run(repo, "git", "clean", "-fdq")
    run(repo, "git", "checkout", "-q", "--detach", commit)
    if run(repo, "git", "status", "--porcelain").stdout.strip():
        raise RuntimeError(f"dirty checkout at {commit}")


def deterministic_merge_commit(repo: Path, head: str, target: str) -> dict:
    fresh(repo, head)
    p = run(repo, "git", "merge", "--no-commit", "--no-ff", target, check=False)
    unmerged = sorted(
        x for x in run(repo, "git", "diff", "--name-only", "--diff-filter=U", check=False).stdout.splitlines() if x
    )
    merge_in_progress = (repo / ".git" / "MERGE_HEAD").exists()
    wt = run(repo, "git", "write-tree", check=False)
    index_tree = wt.stdout.strip() if wt.returncode == 0 else None
    if p.returncode != 0 or unmerged or not merge_in_progress or not index_tree:
        run(repo, "git", "merge", "--abort", check=False)
        run(repo, "git", "reset", "--hard", "-q", head)
        return {
            "ok": False,
            "exit_code": p.returncode,
            "unmerged_paths": unmerged,
            "merge_in_progress": merge_in_progress,
            "index_tree": index_tree,
        }
    env = {
        "GIT_AUTHOR_NAME": "OACR COMPOSE",
        "GIT_AUTHOR_EMAIL": "oacr-compose@example.invalid",
        "GIT_COMMITTER_NAME": "OACR COMPOSE",
        "GIT_COMMITTER_EMAIL": "oacr-compose@example.invalid",
        "GIT_AUTHOR_DATE": "2000-01-01T00:00:00Z",
        "GIT_COMMITTER_DATE": "2000-01-01T00:00:00Z",
    }
    c = run(
        repo,
        "git", "-c", "core.hooksPath=/dev/null", "commit", "--no-gpg-sign",
        "-q", "-m", "OACR-COMPOSE-G step1",
        extra_env=env,
    )
    new_head = run(repo, "git", "rev-parse", "HEAD").stdout.strip()
    tree = run(repo, "git", "rev-parse", "HEAD^{tree}").stdout.strip()
    parents = run(repo, "git", "show", "-s", "--format=%P", "HEAD").stdout.strip().split()
    return {
        "ok": True,
        "commit": new_head,
        "tree": tree,
        "parents": parents,
        "precommit_index_tree": index_tree,
        "commit_output": c.stdout,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    repo = Path(args.repo).resolve()

    source_head = git(repo, "rev-parse", "HEAD").stdout.strip()
    if source_head != SOURCE_HEAD:
        raise RuntimeError(f"source head mismatch: {source_head}")

    commits, discovery, validation, total_groups = natural_pair_banks(repo, 20000)
    targets, target_scores = select_targets(repo, discovery, 12)
    h1 = evaluate(repo, validation, targets)
    rows = h1["pair_rows"]

    eligible = []
    for row in rows:
        if row["required_separation"]:
            continue
        if row["ancestry_vector_A"] != row["ancestry_vector_B"]:
            continue
        diff_targets = sorted(
            t for t, a, b in zip(targets, row["mergebase_vector_A"], row["mergebase_vector_B"])
            if a != b
        )
        if len(diff_targets) < 2:
            continue
        eligible.append({**row, "diff_targets": diff_targets})
    eligible.sort(key=lambda r: (r["A"], r["B"]))
    selected = evenly_spaced(eligible, 16)

    results = []
    for row in selected:
        a, b = row["A"], row["B"]
        h1_eligible = []
        for t in row["diff_targets"]:
            ma = execute_merge(repo, a, t)
            mb = execute_merge(repo, b, t)
            ok = (
                ma["exit_code"] == 0
                and mb["exit_code"] == 0
                and not ma["unmerged_paths"]
                and not mb["unmerged_paths"]
                and ma["merge_in_progress"]
                and mb["merge_in_progress"]
                and ma["index_tree"] is not None
                and ma["index_tree"] == mb["index_tree"]
                and ma["signature"] == mb["signature"]
            )
            if ok:
                h1_eligible.append({
                    "target": t,
                    "index_tree": ma["index_tree"],
                    "signature": ma["signature"],
                })

        base = {
            "tree": row["tree"],
            "A": a,
            "B": b,
            "diff_targets": row["diff_targets"],
            "h1_composition_eligible_targets": h1_eligible,
        }
        if len(h1_eligible) < 2:
            results.append({**base, "status": "H1_NOT_COMPOSABLE"})
            continue

        t1 = h1_eligible[0]["target"]
        t2 = h1_eligible[1]["target"]
        pre = {
            "mergebase_A_t2": merge_base(repo, a, t2),
            "mergebase_B_t2": merge_base(repo, b, t2),
            "t2_ancestor_A": is_ancestor(repo, t2, a),
            "t2_ancestor_B": is_ancestor(repo, t2, b),
            "A_ancestor_t2": is_ancestor(repo, a, t2),
            "B_ancestor_t2": is_ancestor(repo, b, t2),
        }

        a1 = deterministic_merge_commit(repo, a, t1)
        b1 = deterministic_merge_commit(repo, b, t1)
        if not a1["ok"] or not b1["ok"]:
            results.append({
                **base, "status": "STEP1_MATERIALIZATION_FAILURE",
                "t1": t1, "t2": t2, "A1": a1, "B1": b1,
            })
            continue
        if a1["tree"] != b1["tree"]:
            results.append({
                **base, "status": "STEP1_TREE_MISMATCH",
                "t1": t1, "t2": t2, "A1": a1, "B1": b1,
            })
            continue

        post = {
            "mergebase_A1_t2": merge_base(repo, a1["commit"], t2),
            "mergebase_B1_t2": merge_base(repo, b1["commit"], t2),
            "t2_ancestor_A1": is_ancestor(repo, t2, a1["commit"]),
            "t2_ancestor_B1": is_ancestor(repo, t2, b1["commit"]),
            "A1_ancestor_t2": is_ancestor(repo, a1["commit"], t2),
            "B1_ancestor_t2": is_ancestor(repo, b1["commit"], t2),
        }
        m2a = execute_merge(repo, a1["commit"], t2)
        m2b = execute_merge(repo, b1["commit"], t2)
        separated = m2a["signature"] != m2b["signature"]

        results.append({
            **base,
            "status": "H2_SEPARATED" if separated else "H2_EQUIVALENT",
            "t1": t1,
            "t2": t2,
            "pre_step1_t2_context": pre,
            "A1": a1,
            "B1": b1,
            "post_step1_t2_context": post,
            "H2_A": m2a,
            "H2_B": m2b,
            "H2_separated": separated,
        })

    summary = {
        "source_head": source_head,
        "commits_enumerated": len(commits),
        "same_tree_groups_available": total_groups,
        "registered_targets": len(targets),
        "validation_pairs": len(validation),
        "H1_equivalent_pairs": sum(not r["required_separation"] for r in rows),
        "H1_equivalent_mergebase_diff_pairs": len(eligible),
        "selected_pairs": len(selected),
        "H1_not_composable": sum(r["status"] == "H1_NOT_COMPOSABLE" for r in results),
        "step1_failures": sum(r["status"].startswith("STEP1_") for r in results),
        "H2_separated": sum(r["status"] == "H2_SEPARATED" for r in results),
        "H2_equivalent": sum(r["status"] == "H2_EQUIVALENT" for r in results),
    }
    payload = {
        "protocol": "OACR_COMPOSE_G_DEPTH2_V1",
        "protocol_commit": "449fcf31d4f102e43f14c207e562ce08f5c94c83",
        "source": {
            "remote": git(repo, "remote", "get-url", "origin").stdout.strip(),
            "source_head": source_head,
            "git_version": git(repo, "--version").stdout.strip(),
        },
        "target_scores": target_scores,
        "registered_targets": targets,
        "summary": summary,
        "results": results,
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
