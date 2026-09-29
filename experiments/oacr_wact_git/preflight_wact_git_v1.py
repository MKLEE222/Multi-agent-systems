"""Outcome-blind WACT-G preflight: same-tree pairs + ancestry activation only."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
from collections import defaultdict
from pathlib import Path


PROTOCOL = "OACR_WACT_G_PREFLIGHT_V1"
PROTOCOL_COMMIT = "f8541625b50b5104d60f8b55741e2e03ab31cb19"


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


def commit_tree_map(repo: Path, commits):
    out = {}
    chunk = 300
    for i in range(0, len(commits), chunk):
        xs = commits[i:i+chunk]
        p = git(repo, "show", "-s", "--format=%H %T", *xs)
        for line in p.stdout.splitlines():
            parts = line.split()
            if len(parts) == 2:
                out[parts[0]] = parts[1]
    return out


def same_tree_pairs(repo: Path):
    commits = [
        x for x in git(repo, "rev-list", "HEAD", "--max-count=30000").stdout.splitlines() if x
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
    return commits, pairs, pairs[:256]


def target_pool(repo: Path):
    lines = git(
        repo, "rev-list", "--merges", "HEAD", "--max-count=10000", "--parents"
    ).stdout.splitlines()
    targets = []
    seen = set()
    two_parent = 0
    for line in lines:
        p = line.split()
        if len(p) != 3:
            continue
        two_parent += 1
        t = p[2]
        if t not in seen:
            seen.add(t)
            targets.append(t)
        if two_parent >= 512:
            break
    return targets, two_parent


def ancestry_bitsets(repo: Path, targets):
    bit_of = {t: (1 << i) for i, t in enumerate(targets)}
    bits = {}
    lines = git(repo, "rev-list", "--topo-order", "--reverse", "--parents", "HEAD").stdout.splitlines()
    for line in lines:
        p = line.split()
        if not p:
            continue
        c = p[0]
        b = bit_of.get(c, 0)
        for parent in p[1:]:
            b |= bits.get(parent, 0)
        bits[c] = b
    missing = [t for t in targets if t not in bits]
    if missing:
        raise RuntimeError(f"target commits missing from reachable DAG: {len(missing)}")
    return bits


def first_target(targets, ba, bb, mode):
    for i, t in enumerate(targets):
        xa = bool(ba & (1 << i))
        xb = bool(bb & (1 << i))
        if mode == "both" and xa and xb:
            return t, i, xa, xb
        if mode == "xor" and xa != xb:
            return t, i, xa, xb
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--expected_head", required=True)
    ap.add_argument("--source", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    head = git(repo, "rev-parse", "HEAD").stdout.strip()
    if head != args.expected_head:
        raise RuntimeError(f"HEAD mismatch: {head} != {args.expected_head}")

    commits, all_pairs, pair_bank = same_tree_pairs(repo)
    targets, two_parent_seen = target_pool(repo)

    base = {
        "protocol": PROTOCOL,
        "protocol_commit": PROTOCOL_COMMIT,
        "source": args.source,
        "head": head,
        "git_version": git(repo, "--version").stdout.strip(),
        "commits_enumerated": len(commits),
        "same_tree_pairs_available": len(all_pairs),
        "pair_bank_size": len(pair_bank),
        "target_pool_size": len(targets),
        "two_parent_merges_scanned": two_parent_seen,
        "native_merge_outcomes_executed": False,
    }

    reasons = []
    if len(all_pairs) < 32:
        reasons.append("same_tree_pairs_lt_32")
    if len(targets) < 16:
        reasons.append("target_pool_lt_16")

    if reasons:
        base.update({
            "status": "PREFLIGHT_UNDERPOWERED",
            "exclusion_reasons": reasons,
            "eligible_pairs": 0,
            "selected_witnesses": [],
        })
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(json.dumps(base, indent=2))
        print(json.dumps(base, indent=2))
        return

    bits = ancestry_bitsets(repo, targets)

    eligible = []
    target_asymmetric_load = [0 for _ in targets]
    for p in pair_bank:
        ba = bits[p["A"]]
        bb = bits[p["B"]]
        inert = first_target(targets, ba, bb, "both")
        active = first_target(targets, ba, bb, "xor")
        asym_count = 0
        for i, _t in enumerate(targets):
            xa = bool(ba & (1 << i))
            xb = bool(bb & (1 << i))
            if xa != xb:
                asym_count += 1
                target_asymmetric_load[i] += 1
        if inert is not None and active is not None:
            eligible.append({
                **p,
                "inert_target": inert[0],
                "inert_target_index": inert[1],
                "activating_target": active[0],
                "activating_target_index": active[1],
                "activating_target_ancestor_A": active[2],
                "activating_target_ancestor_B": active[3],
                "asymmetric_target_count": asym_count,
            })

    if len(eligible) < 8:
        base.update({
            "status": "PREFLIGHT_UNDERPOWERED",
            "exclusion_reasons": ["eligible_pairs_lt_8"],
            "eligible_pairs": len(eligible),
            "selected_witnesses": [],
            "eligible_pair_rows": eligible,
        })
    else:
        selected = eligible if len(eligible) <= 16 else evenly_spaced(eligible, 16)
        base.update({
            "status": "INCLUDED",
            "eligible_pairs": len(eligible),
            "eligible_pair_fraction_of_bank": len(eligible) / len(pair_bank) if pair_bank else 0.0,
            "selected_witnesses": selected,
            "secondary": {
                "target_asymmetric_load": [
                    {"target_index": i, "target": t, "eligible_pair_asymmetry_count": target_asymmetric_load[i]}
                    for i, t in enumerate(targets)
                ],
                "selected_asymmetric_target_counts": [x["asymmetric_target_count"] for x in selected],
            },
        })

    p = Path(args.out)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(base, indent=2))
    print(json.dumps({
        "protocol": PROTOCOL,
        "source": args.source,
        "head": head,
        "status": base["status"],
        "same_tree_pairs_available": len(all_pairs),
        "pair_bank_size": len(pair_bank),
        "target_pool_size": len(targets),
        "eligible_pairs": base.get("eligible_pairs", 0),
        "selected_witnesses": len(base.get("selected_witnesses", [])),
        "native_merge_outcomes_executed": False,
    }, indent=2))


if __name__ == "__main__":
    main()
