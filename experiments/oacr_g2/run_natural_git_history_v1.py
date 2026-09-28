"""OACR-G2 v1: natural tree-preserving merge witnesses in git/git history."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple


def run(cwd: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    p = subprocess.run(
        list(args),
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={**os.environ, "GIT_CONFIG_NOSYSTEM": "1"},
    )
    if check and p.returncode != 0:
        raise RuntimeError(f"command failed ({p.returncode}): {' '.join(args)}\n{p.stdout}")
    return p


def git(cwd: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    return run(cwd, "git", *args, check=check)


def chunked(xs: List[str], n: int) -> Iterable[List[str]]:
    for i in range(0, len(xs), n):
        yield xs[i : i + n]


def commit_tree_map(repo: Path, commits: List[str]) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for chunk in chunked(sorted(set(commits)), 250):
        p = git(repo, "show", "-s", "--format=%H %T", *chunk)
        for line in p.stdout.splitlines():
            parts = line.split()
            if len(parts) == 2:
                out[parts[0]] = parts[1]
    return out


def is_ancestor(repo: Path, anc: str, desc: str) -> bool:
    p = git(repo, "merge-base", "--is-ancestor", anc, desc, check=False)
    if p.returncode not in (0, 1):
        raise RuntimeError(p.stdout)
    return p.returncode == 0


def merge_base(repo: Path, a: str, b: str) -> str:
    p = git(repo, "merge-base", a, b, check=False)
    if p.returncode != 0:
        return ""
    return p.stdout.strip()


def fresh(repo: Path, commit: str) -> None:
    git(repo, "merge", "--abort", check=False)
    git(repo, "reset", "--hard", "-q", commit)
    git(repo, "clean", "-fdq")
    git(repo, "checkout", "-q", "--detach", commit)
    if git(repo, "status", "--porcelain").stdout.strip():
        raise RuntimeError(f"dirty checkout at {commit}")


def post_delta_hash(repo: Path) -> str:
    p = git(repo, "diff", "--binary", "--no-ext-diff", "HEAD", check=False)
    return hashlib.sha256(p.stdout.encode()).hexdigest()


def execute_merge(repo: Path, head: str, target: str) -> Dict[str, Any]:
    fresh(repo, head)
    pre_tree = git(repo, "rev-parse", "HEAD^{tree}").stdout.strip()
    p = git(repo, "merge", "--no-commit", "--no-ff", target, check=False)
    output = p.stdout
    unmerged = sorted(
        x for x in git(repo, "diff", "--name-only", "--diff-filter=U", check=False).stdout.splitlines()
        if x
    )
    wt_delta = post_delta_hash(repo)
    write_tree = git(repo, "write-tree", check=False)
    index_tree = write_tree.stdout.strip() if write_tree.returncode == 0 else None
    merge_head = (repo / ".git" / "MERGE_HEAD").exists()

    signature_payload = {
        "exit_code": p.returncode,
        "already_up_to_date": "Already up to date." in output,
        "merge_in_progress": merge_head,
        "unmerged_paths": unmerged,
        "index_tree": index_tree,
        "tracked_delta_sha256": wt_delta,
    }
    signature = hashlib.sha256(
        json.dumps(signature_payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()

    result = {
        **signature_payload,
        "output": output,
        "pre_tree": pre_tree,
        "outcome_signature": signature,
    }
    git(repo, "merge", "--abort", check=False)
    git(repo, "reset", "--hard", "-q", head)
    git(repo, "clean", "-fdq")
    return result


def parent_graph(repo: Path, a: str, b: str, max_count: int = 5000) -> List[Dict[str, Any]]:
    p = git(repo, "rev-list", f"--max-count={max_count}", "--parents", a, b)
    rows = []
    for line in p.stdout.splitlines():
        parts = line.split()
        rows.append({"commit": parts[0], "parents": parts[1:]})
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--max_merges", type=int, default=10000)
    ap.add_argument("--max_witnesses", type=int, default=16)
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    # Neutralize user config that could affect merge behavior.
    git(repo, "config", "--local", "rerere.enabled", "false")
    git(repo, "config", "--local", "merge.conflictStyle", "merge")

    source_head = git(repo, "rev-parse", "HEAD").stdout.strip()
    git_version = git(repo, "--version").stdout.strip()
    remote = git(repo, "remote", "get-url", "origin").stdout.strip()

    revs = git(
        repo,
        "rev-list",
        "--merges",
        "--all",
        f"--max-count={args.max_merges}",
        "--parents",
    ).stdout.splitlines()

    parsed: List[Tuple[str, str, str]] = []
    first_parents: List[str] = []
    for line in revs:
        parts = line.split()
        if len(parts) != 3:
            continue
        b, a, t = parts
        parsed.append((b, a, t))
        first_parents.append(a)

    tree_map = commit_tree_map(repo, [x[0] for x in parsed] + first_parents)

    candidates = []
    for b, a, t in parsed:
        if tree_map.get(b) != tree_map.get(a):
            continue
        if is_ancestor(repo, t, a):
            continue
        if not is_ancestor(repo, t, b):
            continue
        candidates.append((b, a, t))

    witnesses = []
    skipped = []
    for b, a, t in candidates:
        if len(witnesses) >= args.max_witnesses:
            break
        try:
            a_tree = tree_map[a]
            b_tree = tree_map[b]
            if a_tree != b_tree:
                raise RuntimeError("candidate pre-tree mismatch")

            out_a = execute_merge(repo, a, t)
            out_b = execute_merge(repo, b, t)
            if out_a["pre_tree"] != out_b["pre_tree"]:
                raise RuntimeError("executed pre-tree mismatch")
            if not out_b["already_up_to_date"]:
                raise RuntimeError("B branch did not report already up to date")

            divergent = out_a["outcome_signature"] != out_b["outcome_signature"]
            if not divergent:
                skipped.append({
                    "merge_commit_B": b,
                    "first_parent_A": a,
                    "second_parent_T": t,
                    "reason": "same registered outcome",
                })
                continue

            a_mb = merge_base(repo, a, t)
            b_mb = merge_base(repo, b, t)
            witnesses.append({
                "merge_commit_B": b,
                "first_parent_A": a,
                "second_parent_T": t,
                "pre_tree_A": a_tree,
                "pre_tree_B": b_tree,
                "pre_tree_exact_match": True,
                "target_is_ancestor_of_A": False,
                "target_is_ancestor_of_B": True,
                "merge_base_A_target": a_mb,
                "merge_base_B_target": b_mb,
                "A1_ancestry_bit_separates": True,
                "A2_merge_base_separates": a_mb != b_mb,
                "branch_A": out_a,
                "branch_B": out_b,
                "registered_outcome_divergence": True,
                "parent_graph_sample": parent_graph(repo, a, t, 300),
            })
        except Exception as exc:
            skipped.append({
                "merge_commit_B": b,
                "first_parent_A": a,
                "second_parent_T": t,
                "reason": f"execution_error: {type(exc).__name__}: {exc}",
            })

    result = {
        "protocol": "OACR_G2_NATURAL_GIT_HISTORY_V1",
        "source": {
            "remote": remote,
            "source_head": source_head,
            "git_version": git_version,
            "search_command": f"git rev-list --merges --all --max-count={args.max_merges} --parents",
        },
        "registered_read": "exact HEAD tree object",
        "registered_action": "git merge --no-commit --no-ff <natural second parent>",
        "summary": {
            "merge_commits_enumerated": len(revs),
            "two_parent_merges": len(parsed),
            "tree_preserving_candidates": len(candidates),
            "valid_natural_witnesses": len(witnesses),
            "tested_until_stop": min(len(candidates), len(witnesses) + len(skipped)),
            "max_witnesses": args.max_witnesses,
            "A1_ancestry_bit_separates": sum(
                int(x["A1_ancestry_bit_separates"]) for x in witnesses
            ),
            "A2_merge_base_separates": sum(
                int(x["A2_merge_base_separates"]) for x in witnesses
            ),
        },
        "witnesses": witnesses,
        "skipped": skipped,
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2))
    print(json.dumps(result["summary"], indent=2))


if __name__ == "__main__":
    main()
