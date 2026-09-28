"""OACR-G5 v1: same-contract natural Git adequacy matrix with held-out validation."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Tuple

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "common"))

from operational_partition import (  # noqa: E402
    directional_information_gap,
    partition_from_signatures,
    refinement_relation,
)


def run(cwd: Path, *args: str, check: bool = True):
    p = subprocess.run(
        list(args),
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={**os.environ, "GIT_CONFIG_NOSYSTEM": "1"},
    )
    if check and p.returncode != 0:
        raise RuntimeError(
            f"command failed ({p.returncode}): {' '.join(args)}\n{p.stdout}"
        )
    return p


def git(cwd: Path, *args: str, check: bool = True):
    return run(cwd, "git", *args, check=check)


def chunks(xs, n):
    for i in range(0, len(xs), n):
        yield xs[i : i + n]


def commit_tree_map(repo: Path, commits: List[str]) -> Dict[str, str]:
    out = {}
    for ch in chunks(sorted(set(commits)), 250):
        p = git(repo, "show", "-s", "--format=%H %T", *ch)
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
    return p.stdout.strip() if p.returncode == 0 else ""


def fresh(repo: Path, commit: str):
    git(repo, "merge", "--abort", check=False)
    git(repo, "reset", "--hard", "-q", commit)
    git(repo, "clean", "-fdq")
    git(repo, "checkout", "-q", "--detach", commit)
    if git(repo, "status", "--porcelain").stdout.strip():
        raise RuntimeError(f"dirty checkout at {commit}")


def execute_merge(repo: Path, head: str, target: str) -> Dict[str, Any]:
    fresh(repo, head)
    p = git(repo, "merge", "--no-commit", "--no-ff", target, check=False)
    output = p.stdout
    unmerged = sorted(
        x
        for x in git(
            repo, "diff", "--name-only", "--diff-filter=U", check=False
        ).stdout.splitlines()
        if x
    )
    diff = git(repo, "diff", "--binary", "--no-ext-diff", "HEAD", check=False).stdout
    delta_sha = hashlib.sha256(diff.encode()).hexdigest()
    wt = git(repo, "write-tree", check=False)
    index_tree = wt.stdout.strip() if wt.returncode == 0 else None
    payload = {
        "exit_code": p.returncode,
        "already_up_to_date": "Already up to date." in output,
        "merge_in_progress": (repo / ".git" / "MERGE_HEAD").exists(),
        "unmerged_paths": unmerged,
        "index_tree": index_tree,
        "tracked_delta_sha256": delta_sha,
    }
    sig = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    git(repo, "merge", "--abort", check=False)
    git(repo, "reset", "--hard", "-q", head)
    git(repo, "clean", "-fdq")
    return {"signature": sig, "output": output, **payload}


def natural_pair_banks(repo: Path, max_commits: int = 20000):
    commits = [
        x
        for x in git(repo, "rev-list", "--all", f"--max-count={max_commits}").stdout.splitlines()
        if x
    ]
    tm = commit_tree_map(repo, commits)
    groups = defaultdict(list)
    for c in commits:
        if c in tm:
            groups[tm[c]].append(c)

    pairs = []
    for tree in sorted(groups):
        cs = sorted(set(groups[tree]))
        if len(cs) >= 2:
            pairs.append({"tree": tree, "A": cs[0], "B": cs[1]})

    if len(pairs) < 96:
        raise RuntimeError(f"need at least 96 same-tree groups, found {len(pairs)}")
    return commits, pairs[:48], pairs[48:96], len(pairs)


def target_pool(repo: Path, n: int = 256):
    lines = git(
        repo, "rev-list", "--merges", "--all", "--max-count=4000", "--parents"
    ).stdout.splitlines()
    targets = []
    seen = set()
    two_parent_seen = 0
    for line in lines:
        p = line.split()
        if len(p) != 3:
            continue
        two_parent_seen += 1
        t = p[2]
        if t not in seen:
            targets.append(t)
            seen.add(t)
        if two_parent_seen >= 256:
            break
    if len(targets) < 12:
        raise RuntimeError(f"target pool too small: {len(targets)}")
    return targets


def select_targets(repo: Path, discovery_pairs, n: int = 12):
    pool = target_pool(repo, 256)
    endpoints = sorted(
        {p["A"] for p in discovery_pairs} | {p["B"] for p in discovery_pairs}
    )
    cache = {}
    for t in pool:
        for c in endpoints:
            cache[(t, c)] = is_ancestor(repo, t, c)

    scored = []
    for t in pool:
        disagreement = sum(
            int(cache[(t, p["A"])] != cache[(t, p["B"])])
            for p in discovery_pairs
        )
        scored.append((disagreement, t))
    scored.sort(key=lambda x: (-x[0], x[1]))
    chosen = scored[:n]
    return [t for _, t in chosen], [
        {"target": t, "discovery_ancestry_disagreements": score}
        for score, t in chosen
    ]


def block_sizes(partition):
    return sorted((len(x) for x in partition), reverse=True)


def evaluate(repo: Path, pairs, targets):
    states = []
    tree_of = {}
    pair_rows = []
    for p in pairs:
        for side in ("A", "B"):
            c = p[side]
            states.append(c)
            tree_of[c] = p["tree"]

    if len(set(states)) != len(states):
        raise RuntimeError("registered state bank contains duplicate commit endpoints")

    ancestry_sig = {}
    mergebase_sig = {}
    outcomes = {}

    for c in states:
        ancestry_sig[c] = tuple(is_ancestor(repo, t, c) for t in targets)
        mergebase_sig[c] = tuple(merge_base(repo, c, t) for t in targets)
        out = []
        for t in targets:
            m = execute_merge(repo, c, t)
            out.append(m["signature"])
        outcomes[c] = tuple(out)

    op_sig = {c: (tree_of[c], outcomes[c]) for c in states}
    rep_sigs = {
        "R0_current_tree": {c: tree_of[c] for c in states},
        "Rfull_commit_identity": {c: c for c in states},
        "R1_tree_plus_ancestry_vector": {
            c: (tree_of[c], ancestry_sig[c]) for c in states
        },
        "R2_tree_plus_mergebase_vector": {
            c: (tree_of[c], mergebase_sig[c]) for c in states
        },
    }

    op_partition = partition_from_signatures(states, lambda c: op_sig[c])
    diagnostics = {}
    for name, sigs in rep_sigs.items():
        part = partition_from_signatures(states, lambda c, sigs=sigs: sigs[c])
        diagnostics[name] = {
            "representation_blocks": len(part),
            "representation_block_sizes": block_sizes(part)[:30],
            "pairwise": refinement_relation(part, op_partition),
            "information": directional_information_gap(part, op_partition),
        }

    for p in pairs:
        a, b = p["A"], p["B"]
        pair_rows.append(
            {
                **p,
                "required_separation": op_sig[a] != op_sig[b],
                "R1_separates": rep_sigs["R1_tree_plus_ancestry_vector"][a]
                != rep_sigs["R1_tree_plus_ancestry_vector"][b],
                "R2_separates": rep_sigs["R2_tree_plus_mergebase_vector"][a]
                != rep_sigs["R2_tree_plus_mergebase_vector"][b],
                "outcome_signatures_A": list(outcomes[a]),
                "outcome_signatures_B": list(outcomes[b]),
                "ancestry_vector_A": list(ancestry_sig[a]),
                "ancestry_vector_B": list(ancestry_sig[b]),
                "mergebase_vector_A": list(mergebase_sig[a]),
                "mergebase_vector_B": list(mergebase_sig[b]),
            }
        )

    return {
        "states": len(states),
        "pairs": len(pairs),
        "operational_blocks_H1": len(op_partition),
        "operational_block_sizes": block_sizes(op_partition)[:50],
        "required_pair_separations": sum(
            int(x["required_separation"]) for x in pair_rows
        ),
        "behaviorally_equivalent_pairs": sum(
            int(not x["required_separation"]) for x in pair_rows
        ),
        "diagnostics": diagnostics,
        "pair_rows": pair_rows,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--split", choices=["discovery", "validation"], required=True)
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    git(repo, "config", "--local", "rerere.enabled", "false")
    git(repo, "config", "--local", "merge.conflictStyle", "merge")

    source_head = git(repo, "rev-parse", "HEAD").stdout.strip()
    commits, discovery, validation, total_groups = natural_pair_banks(repo, 20000)
    targets, target_scores = select_targets(repo, discovery, 12)

    pairs = discovery if args.split == "discovery" else validation
    result = evaluate(repo, pairs, targets)

    out = {
        "protocol": "OACR_G5_SAME_CONTRACT_GIT_V1",
        "split": args.split,
        "source": {
            "remote": git(repo, "remote", "get-url", "origin").stdout.strip(),
            "source_head": source_head,
            "git_version": git(repo, "--version").stdout.strip(),
            "commits_enumerated": len(commits),
            "same_tree_groups_available": total_groups,
        },
        "action_selection": {
            "selection_bank": "discovery only",
            "target_pool_rule": "unique second parents among first 256 two-parent merges",
            "targets": target_scores,
        },
        "summary": {
            "split": args.split,
            "registered_targets": len(targets),
            **{k: v for k, v in result.items() if k != "pair_rows"},
        },
        "pair_rows": result["pair_rows"],
    }

    p = Path(args.out)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(out, indent=2))
    print(json.dumps(out["summary"], indent=2))


if __name__ == "__main__":
    main()
