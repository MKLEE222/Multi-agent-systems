"""OACR-M2-G v1: nested-contract adequacy trajectories on the frozen G5 natural Git carrier."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "common"))

from operational_partition import (  # noqa: E402
    directional_information_gap,
    partition_from_signatures,
    refinement_relation,
)

SOURCE_HEAD = "34f06850c16c7f7ac822b1adc71354f11b0f2ca3"
VALIDATION_ENDPOINT = {
    "operational_blocks": 50,
    "required_pairs": 2,
    "equivalent_pairs": 46,
    "R0_U": 0.04166666666666696,
    "R0_E": 0.0,
    "Rfull_U": 0.0,
    "Rfull_E": 0.958333333333333,
    "R1_U": 0.0,
    "R1_E": 0.0,
    "R2_U": 0.0,
    "R2_E": 0.8124999999999991,
}


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
        raise RuntimeError(f"command failed ({p.returncode}): {' '.join(args)}\n{p.stdout}")
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
        for x in git(repo, "diff", "--name-only", "--diff-filter=U", check=False).stdout.splitlines()
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
    return {"signature": sig, **payload}


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


def target_pool(repo: Path):
    lines = git(repo, "rev-list", "--merges", "--all", "--max-count=4000", "--parents").stdout.splitlines()
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


def select_targets(repo: Path, discovery_pairs):
    pool = target_pool(repo)
    endpoints = sorted({p["A"] for p in discovery_pairs} | {p["B"] for p in discovery_pairs})
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
    return [t for _, t in scored[:12]], [
        {"target": t, "discovery_ancestry_disagreements": score}
        for score, t in scored[:12]
    ]


def block_sizes(partition):
    return sorted((len(x) for x in partition), reverse=True)


def is_refinement(fine, coarse) -> bool:
    ci = {}
    for i, block in enumerate(coarse):
        for x in block:
            ci[x] = i
    return all(len({ci[x] for x in block}) == 1 for block in fine)


def approx(a, b, tol=1e-10):
    return abs(float(a) - float(b)) <= tol


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--split", choices=["discovery", "validation"], required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    source_head = git(repo, "rev-parse", "HEAD").stdout.strip()
    if source_head != SOURCE_HEAD:
        raise RuntimeError(f"source HEAD mismatch: {source_head}")
    git(repo, "config", "--local", "rerere.enabled", "false")
    git(repo, "config", "--local", "merge.conflictStyle", "merge")

    commits, discovery, validation, total_groups = natural_pair_banks(repo, 20000)
    targets, target_scores = select_targets(repo, discovery)
    pairs = discovery if args.split == "discovery" else validation

    states = []
    tree_of = {}
    for p in pairs:
        for side in ("A", "B"):
            c = p[side]
            states.append(c)
            tree_of[c] = p["tree"]
    if len(set(states)) != len(states):
        raise RuntimeError("duplicate state endpoints")

    ancestry12 = {}
    mergebase12 = {}
    outcomes12 = {}
    for c in states:
        ancestry12[c] = tuple(is_ancestor(repo, t, c) for t in targets)
        mergebase12[c] = tuple(merge_base(repo, c, t) for t in targets)
        outcomes12[c] = tuple(execute_merge(repo, c, t)["signature"] for t in targets)

    rep_sigs = {
        "R0_fixed_current_tree": {c: tree_of[c] for c in states},
        "Rfull_fixed_commit_identity": {c: c for c in states},
        "R1_fixed12_tree_plus_ancestry": {c: (tree_of[c], ancestry12[c]) for c in states},
        "R2_fixed12_tree_plus_mergebase": {c: (tree_of[c], mergebase12[c]) for c in states},
    }
    reps = {
        name: partition_from_signatures(states, lambda c, sigs=sigs: sigs[c])
        for name, sigs in rep_sigs.items()
    }

    rows = []
    previous_op = None
    refinement_failures = []
    first_adequate = {name: None for name in reps}
    first_match = {name: None for name in reps}

    for k in range(13):
        op_sig = {c: (tree_of[c], outcomes12[c][:k]) for c in states}
        op_partition = partition_from_signatures(states, lambda c, sig=op_sig: sig[c])
        if previous_op is not None and not is_refinement(op_partition, previous_op):
            refinement_failures.append(k)

        pair_rows = []
        for p in pairs:
            a, b = p["A"], p["B"]
            pair_rows.append(op_sig[a] != op_sig[b])
        required = sum(int(x) for x in pair_rows)
        equivalent = len(pair_rows) - required

        diag = {}
        for name, rep in reps.items():
            info = directional_information_gap(rep, op_partition)
            pair = refinement_relation(rep, op_partition)
            diag[name] = {
                "representation_blocks": len(rep),
                "under_refinement_count": pair["under_refinement_count"],
                "over_refinement_count": pair["over_refinement_count"],
                "U_bits": info["omission_U_bits"],
                "E_bits": info["excess_E_bits"],
                "adequate": info["adequate_almost_surely"],
                "partition_match": info["partition_match_almost_surely"],
            }
            if info["adequate_almost_surely"] and first_adequate[name] is None:
                first_adequate[name] = k
            if info["partition_match_almost_surely"] and first_match[name] is None:
                first_match[name] = k

        changed = previous_op is None or not (
            is_refinement(previous_op, op_partition) and is_refinement(op_partition, previous_op)
        )
        rows.append({
            "k": k,
            "operational_blocks": len(op_partition),
            "operational_block_sizes": block_sizes(op_partition)[:50],
            "required_pair_separations": required,
            "behaviorally_equivalent_pairs": equivalent,
            "changed_from_previous": bool(changed),
            "diagnostics": diag,
        })
        previous_op = op_partition

    if refinement_failures:
        raise RuntimeError(f"nested refinement failed at {refinement_failures}")

    endpoint_ok = True
    if args.split == "validation":
        end = rows[-1]
        d0 = end["diagnostics"]["R0_fixed_current_tree"]
        df = end["diagnostics"]["Rfull_fixed_commit_identity"]
        d1 = end["diagnostics"]["R1_fixed12_tree_plus_ancestry"]
        d2 = end["diagnostics"]["R2_fixed12_tree_plus_mergebase"]
        endpoint_ok = (
            end["operational_blocks"] == VALIDATION_ENDPOINT["operational_blocks"]
            and end["required_pair_separations"] == VALIDATION_ENDPOINT["required_pairs"]
            and end["behaviorally_equivalent_pairs"] == VALIDATION_ENDPOINT["equivalent_pairs"]
            and approx(d0["U_bits"], VALIDATION_ENDPOINT["R0_U"])
            and approx(d0["E_bits"], VALIDATION_ENDPOINT["R0_E"])
            and approx(df["U_bits"], VALIDATION_ENDPOINT["Rfull_U"])
            and approx(df["E_bits"], VALIDATION_ENDPOINT["Rfull_E"])
            and approx(d1["U_bits"], VALIDATION_ENDPOINT["R1_U"])
            and approx(d1["E_bits"], VALIDATION_ENDPOINT["R1_E"])
            and approx(d2["U_bits"], VALIDATION_ENDPOINT["R2_U"])
            and approx(d2["E_bits"], VALIDATION_ENDPOINT["R2_E"])
        )
        if not endpoint_ok:
            raise RuntimeError(f"G5 validation endpoint regression failed: {json.dumps(end, indent=2)}")

    out = {
        "protocol": "OACR_M2_G_NESTED_CONTRACT_V1",
        "split": args.split,
        "source": {
            "source_head": source_head,
            "commits_enumerated": len(commits),
            "same_tree_groups_available": total_groups,
            "g5_run": 36385706858,
            "g5_checkpoint_commit": "5cc8baf1db8b66061032da6c99723a2956f98121",
        },
        "action_selection": {
            "rule": "exact G5 discovery-only ancestry-disagreement ordering",
            "targets": target_scores,
        },
        "fixed_representations": list(reps),
        "trajectory": rows,
        "first_adequate_prefix": first_adequate,
        "first_exact_match_prefix": first_match,
        "checks": {
            "nested_refinement_failures": refinement_failures,
            "validation_endpoint_regression_passed": endpoint_ok if args.split == "validation" else None,
        },
    }

    p = Path(args.out)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(out, indent=2))
    print(json.dumps({
        "protocol": out["protocol"],
        "split": args.split,
        "prefixes": len(rows),
        "refinement_failures": refinement_failures,
        "endpoint_regression_passed": out["checks"]["validation_endpoint_regression_passed"],
        "first_adequate_prefix": first_adequate,
        "first_exact_match_prefix": first_match,
        "trajectory_summary": [
            {
                "k": r["k"],
                "O": r["operational_blocks"],
                "required_pairs": r["required_pair_separations"],
                "R0_U": r["diagnostics"]["R0_fixed_current_tree"]["U_bits"],
                "Rfull_E": r["diagnostics"]["Rfull_fixed_commit_identity"]["E_bits"],
                "R1_U": r["diagnostics"]["R1_fixed12_tree_plus_ancestry"]["U_bits"],
                "R1_E": r["diagnostics"]["R1_fixed12_tree_plus_ancestry"]["E_bits"],
            }
            for r in rows
        ],
    }, indent=2))


if __name__ == "__main__":
    main()
