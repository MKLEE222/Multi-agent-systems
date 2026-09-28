"""OACR-G1 v1: exact Git tree/history operational-congruence witnesses."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List


ENV = {
    **os.environ,
    "GIT_AUTHOR_NAME": "OACR",
    "GIT_AUTHOR_EMAIL": "oacr@example.invalid",
    "GIT_COMMITTER_NAME": "OACR",
    "GIT_COMMITTER_EMAIL": "oacr@example.invalid",
    "GIT_AUTHOR_DATE": "2001-01-01T00:00:00+00:00",
    "GIT_COMMITTER_DATE": "2001-01-01T00:00:00+00:00",
}


def run(cwd: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    p = subprocess.run(
        list(args),
        cwd=cwd,
        env=ENV,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if check and p.returncode != 0:
        raise RuntimeError(f"command failed ({p.returncode}): {' '.join(args)}\n{p.stdout}")
    return p


def git(cwd: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    return run(cwd, "git", *args, check=check)


def commit(cwd: Path, message: str) -> str:
    git(cwd, "add", "-A")
    git(cwd, "commit", "-q", "-m", message)
    return git(cwd, "rev-parse", "HEAD").stdout.strip()


def tree_id(cwd: Path, commit_id: str) -> str:
    return git(cwd, "rev-parse", f"{commit_id}^{{tree}}").stdout.strip()


def file_snapshot(cwd: Path) -> Dict[str, str]:
    files = git(cwd, "ls-files").stdout.splitlines()
    out = {}
    for rel in sorted(files):
        path = cwd / rel
        if path.exists() and path.is_file():
            out[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
        else:
            out[rel] = "<missing>"
    return out


def snapshot_hash(snapshot: Dict[str, str]) -> str:
    b = json.dumps(snapshot, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(b).hexdigest()


def merge_base(cwd: Path, head: str, target: str) -> str:
    return git(cwd, "merge-base", head, target).stdout.strip()


def is_ancestor(cwd: Path, anc: str, desc: str) -> bool:
    p = git(cwd, "merge-base", "--is-ancestor", anc, desc, check=False)
    if p.returncode not in (0, 1):
        raise RuntimeError(p.stdout)
    return p.returncode == 0


def reachable_parent_graph(cwd: Path, head: str, target: str) -> List[Dict[str, Any]]:
    revs = git(cwd, "rev-list", "--parents", head, target).stdout.splitlines()
    rows = []
    for line in revs:
        parts = line.split()
        rows.append({"commit": parts[0], "parents": parts[1:]})
    return sorted(rows, key=lambda x: x["commit"])


def fresh_checkout(cwd: Path, name: str, commit_id: str) -> None:
    # Clear any previous merge/index/worktree state.
    git(cwd, "merge", "--abort", check=False)
    git(cwd, "reset", "--hard", "-q", commit_id)
    git(cwd, "clean", "-fdq")
    git(cwd, "checkout", "-q", "-B", name, commit_id)
    if git(cwd, "status", "--porcelain").stdout.strip():
        raise RuntimeError("checkout is not clean")


def execute_merge(cwd: Path, head: str, target: str, replay_name: str) -> Dict[str, Any]:
    fresh_checkout(cwd, replay_name, head)
    pre_tree = git(cwd, "rev-parse", "HEAD^{tree}").stdout.strip()
    pre_status = git(cwd, "status", "--porcelain=v2").stdout

    p = git(cwd, "merge", "--no-commit", "--no-ff", target, check=False)
    output = p.stdout
    merge_head = cwd / ".git" / "MERGE_HEAD"
    unmerged = git(cwd, "diff", "--name-only", "--diff-filter=U", check=False).stdout.splitlines()
    wt = file_snapshot(cwd)
    wt_hash = snapshot_hash(wt)
    write_tree = git(cwd, "write-tree", check=False)
    index_tree = write_tree.stdout.strip() if write_tree.returncode == 0 else None
    status = git(cwd, "status", "--porcelain=v2", check=False).stdout

    result = {
        "exit_code": p.returncode,
        "output": output,
        "already_up_to_date": "Already up to date." in output,
        "merge_in_progress": merge_head.exists(),
        "unmerged_paths": sorted(unmerged),
        "pre_tree": pre_tree,
        "pre_status": pre_status,
        "index_tree": index_tree,
        "working_snapshot": wt,
        "working_snapshot_sha256": wt_hash,
        "post_status": status,
    }
    result["outcome_signature"] = hashlib.sha256(
        json.dumps(
            {
                "exit_code": result["exit_code"],
                "already_up_to_date": result["already_up_to_date"],
                "merge_in_progress": result["merge_in_progress"],
                "unmerged_paths": result["unmerged_paths"],
                "index_tree": result["index_tree"],
                "working_snapshot_sha256": result["working_snapshot_sha256"],
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode()
    ).hexdigest()

    # Restore before another branch is tested.
    git(cwd, "merge", "--abort", check=False)
    git(cwd, "reset", "--hard", "-q", head)
    git(cwd, "clean", "-fdq")
    return result


def build_conflict_case(root: Path) -> Dict[str, str]:
    repo = root / "conflict_case"
    repo.mkdir()
    git(repo, "init", "-q")
    git(repo, "config", "user.name", "OACR")
    git(repo, "config", "user.email", "oacr@example.invalid")

    (repo / "f.txt").write_text("base\n")
    o = commit(repo, "O")

    git(repo, "checkout", "-q", "-b", "target")
    (repo / "f.txt").write_text("theirs\n")
    t = commit(repo, "T")

    git(repo, "checkout", "-q", "-b", "stateA", o)
    (repo / "f.txt").write_text("ours\n")
    a = commit(repo, "A")

    git(repo, "checkout", "-q", "-b", "stateB", t)
    (repo / "f.txt").write_text("ours\n")
    b = commit(repo, "B")
    return {"repo": str(repo), "O": o, "T": t, "A": a, "B": b}


def build_clean_divergence_case(root: Path) -> Dict[str, str]:
    repo = root / "clean_case"
    repo.mkdir()
    git(repo, "init", "-q")
    git(repo, "config", "user.name", "OACR")
    git(repo, "config", "user.email", "oacr@example.invalid")

    (repo / "f1.txt").write_text("base1\n")
    (repo / "f2.txt").write_text("base2\n")
    o = commit(repo, "O")

    git(repo, "checkout", "-q", "-b", "target")
    (repo / "f1.txt").write_text("theirs1\n")
    t = commit(repo, "T")

    git(repo, "checkout", "-q", "-b", "stateA", o)
    (repo / "f2.txt").write_text("ours2\n")
    a = commit(repo, "A")

    git(repo, "checkout", "-q", "-b", "stateB", t)
    (repo / "f1.txt").write_text("base1\n")
    (repo / "f2.txt").write_text("ours2\n")
    b = commit(repo, "B")
    return {"repo": str(repo), "O": o, "T": t, "A": a, "B": b}


def audit_case(ids: Dict[str, str], case_name: str) -> Dict[str, Any]:
    repo = Path(ids["repo"])
    a_tree, b_tree = tree_id(repo, ids["A"]), tree_id(repo, ids["B"])
    if a_tree != b_tree:
        raise RuntimeError(f"{case_name}: A/B pre trees differ")

    a_ancestor = is_ancestor(repo, ids["T"], ids["A"])
    b_ancestor = is_ancestor(repo, ids["T"], ids["B"])
    a_mb = merge_base(repo, ids["A"], ids["T"])
    b_mb = merge_base(repo, ids["B"], ids["T"])

    a1 = execute_merge(repo, ids["A"], ids["T"], f"{case_name}_A_r1")
    a2 = execute_merge(repo, ids["A"], ids["T"], f"{case_name}_A_r2")
    b1 = execute_merge(repo, ids["B"], ids["T"], f"{case_name}_B_r1")
    b2 = execute_merge(repo, ids["B"], ids["T"], f"{case_name}_B_r2")

    if a1["outcome_signature"] != a2["outcome_signature"]:
        raise RuntimeError(f"{case_name}: A duplicate replay mismatch")
    if b1["outcome_signature"] != b2["outcome_signature"]:
        raise RuntimeError(f"{case_name}: B duplicate replay mismatch")

    divergence = a1["outcome_signature"] != b1["outcome_signature"]
    if not divergence:
        raise RuntimeError(f"{case_name}: no registered outcome divergence")

    return {
        "case": case_name,
        "commits": {k: v for k, v in ids.items() if k != "repo"},
        "pre_tree_a": a_tree,
        "pre_tree_b": b_tree,
        "pre_tree_exact_match": True,
        "target_is_ancestor_of_A": a_ancestor,
        "target_is_ancestor_of_B": b_ancestor,
        "merge_base_A_target": a_mb,
        "merge_base_B_target": b_mb,
        "A1_ancestry_bit_separates": a_ancestor != b_ancestor,
        "A2_merge_base_separates": a_mb != b_mb,
        "A3_parent_graph_A": reachable_parent_graph(repo, ids["A"], ids["T"]),
        "A3_parent_graph_B": reachable_parent_graph(repo, ids["B"], ids["T"]),
        "branch_A": a1,
        "branch_B": b1,
        "duplicate_replay_A_signature": a2["outcome_signature"],
        "duplicate_replay_B_signature": b2["outcome_signature"],
        "registered_outcome_divergence": divergence,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True)
    args = p.parse_args()

    work = Path(tempfile.mkdtemp(prefix="oacr-g1-"))
    try:
        conflict = audit_case(build_conflict_case(work), "conflict_vs_ancestor")
        clean = audit_case(build_clean_divergence_case(work), "clean_divergence_vs_ancestor")

        if not conflict["branch_A"]["unmerged_paths"]:
            raise RuntimeError("conflict case A did not produce an unmerged path")
        if not conflict["branch_B"]["already_up_to_date"]:
            raise RuntimeError("conflict case B was not already up to date")
        if clean["branch_A"]["exit_code"] != 0:
            raise RuntimeError("clean case A did not merge cleanly")
        if clean["branch_A"]["working_snapshot_sha256"] == clean["branch_B"]["working_snapshot_sha256"]:
            raise RuntimeError("clean case did not produce post-content divergence")
        if not clean["branch_B"]["already_up_to_date"]:
            raise RuntimeError("clean case B was not already up to date")

        result = {
            "protocol": "OACR_G1_GIT_TREE_HISTORY_CONGRUENCE_V1",
            "git_version": run(work, "git", "--version").stdout.strip(),
            "registered_read": "exact HEAD tree object",
            "registered_action": "git merge --no-commit --no-ff <same target>",
            "cases": [conflict, clean],
            "summary": {
                "cases": 2,
                "exact_pre_tree_collisions": 2,
                "registered_operational_divergences": 2,
                "A1_ancestry_bit_separates": sum(
                    int(x["A1_ancestry_bit_separates"]) for x in (conflict, clean)
                ),
                "A2_merge_base_separates": sum(
                    int(x["A2_merge_base_separates"]) for x in (conflict, clean)
                ),
                "duplicate_replay_failures": 0,
                "clean_post_content_divergence": (
                    clean["branch_A"]["working_snapshot_sha256"]
                    != clean["branch_B"]["working_snapshot_sha256"]
                ),
            },
        }

        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, indent=2))
        print(json.dumps(result["summary"], indent=2))
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    main()
