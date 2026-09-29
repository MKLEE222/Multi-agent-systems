"""Independent verifier for outcome-blind OACR-WACT-G v1 preflight."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
from collections import defaultdict
from pathlib import Path

PROTOCOL = "OACR_WACT_G_PREFLIGHT_V1"


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
    lines = git(
        repo, "log", "--format=%H %T", "--max-count=30000", "HEAD"
    ).stdout.splitlines()
    for line in lines:
        parts = line.split()
        if len(parts) == 2:
            out[parts[0]] = parts[1]
    missing = [c for c in commits if c not in out]
    if missing:
        raise RuntimeError(f"missing tree mapping for {len(missing)} commits")
    return out


def reconstruct_pair_bank(repo: Path):
    commits = [
        x
        for x in git(
            repo, "rev-list", "HEAD", "--max-count=30000"
        ).stdout.splitlines()
        if x
    ]
    trees = commit_tree_map(repo, commits)
    groups = defaultdict(list)
    for c in commits:
        groups[trees[c]].append(c)
    pairs = []
    for tree in sorted(groups):
        cs = sorted(set(groups[tree]))
        if len(cs) >= 2:
            pairs.append({"tree": tree, "A": cs[0], "B": cs[1]})
    return commits, pairs, pairs[:256]


def reconstruct_target_pool(repo: Path):
    lines = git(
        repo,
        "rev-list",
        "--merges",
        "HEAD",
        "--max-count=10000",
        "--parents",
    ).stdout.splitlines()
    targets = []
    seen = set()
    two_parent = 0
    for line in lines:
        parts = line.split()
        if len(parts) != 3:
            continue
        two_parent += 1
        t = parts[2]
        if t not in seen:
            seen.add(t)
            targets.append(t)
        if two_parent >= 512:
            break
    return targets, two_parent


def reconstruct_target_ancestor_sets(repo: Path, targets):
    target_index = {t: i for i, t in enumerate(targets)}
    parents = {}
    order = []
    for line in git(
        repo, "rev-list", "--topo-order", "--reverse", "--parents", "HEAD"
    ).stdout.splitlines():
        parts = line.split()
        if not parts:
            continue
        c = parts[0]
        parents[c] = parts[1:]
        order.append(c)

    inherited = {}
    for c in order:
        s = set()
        for p in parents.get(c, []):
            s.update(inherited.get(p, set()))
        if c in target_index:
            s.add(target_index[c])
        inherited[c] = s

    missing = [t for t in targets if t not in inherited]
    if missing:
        raise RuntimeError(f"targets absent from reachable DAG: {len(missing)}")
    return inherited


def native_is_ancestor(repo: Path, target: str, endpoint: str) -> bool:
    p = git(repo, "merge-base", "--is-ancestor", target, endpoint, check=False)
    if p.returncode == 0:
        return True
    if p.returncode == 1:
        return False
    raise RuntimeError(
        f"merge-base --is-ancestor error {target} {endpoint}: {p.stdout}"
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--preflight", required=True)
    ap.add_argument("--expected_head", required=True)
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    x = json.loads(Path(args.preflight).read_text())
    if x.get("protocol") != PROTOCOL:
        raise RuntimeError(f"unexpected protocol: {x.get('protocol')}")

    head = git(repo, "rev-parse", "HEAD").stdout.strip()
    if head != args.expected_head or x.get("head") != args.expected_head:
        raise RuntimeError("HEAD mismatch")
    if x.get("native_merge_outcomes_executed") is not False:
        raise RuntimeError("preflight artifact claims native merge outcomes")

    commits, all_pairs, pair_bank = reconstruct_pair_bank(repo)
    targets, two_parent = reconstruct_target_pool(repo)

    if x["commits_enumerated"] != len(commits):
        raise RuntimeError("commit count mismatch")
    if x["same_tree_pairs_available"] != len(all_pairs):
        raise RuntimeError("same-tree pair count mismatch")
    if x["pair_bank_size"] != len(pair_bank):
        raise RuntimeError("pair bank count mismatch")
    if x["target_pool_size"] != len(targets):
        raise RuntimeError("target pool count mismatch")
    if x["two_parent_merges_scanned"] != two_parent:
        raise RuntimeError("two-parent merge count mismatch")

    structural_reasons = []
    if len(all_pairs) < 32:
        structural_reasons.append("same_tree_pairs_lt_32")
    if len(targets) < 16:
        structural_reasons.append("target_pool_lt_16")

    if structural_reasons:
        if x["status"] != "PREFLIGHT_UNDERPOWERED":
            raise RuntimeError("structurally underpowered repo not marked underpowered")
        if x.get("exclusion_reasons") != structural_reasons:
            raise RuntimeError("structural exclusion reasons mismatch")
        if x.get("eligible_pairs") != 0:
            raise RuntimeError("structural early-exit artifact has nonzero eligible pairs")
        print(json.dumps({
            "protocol": PROTOCOL,
            "source": x["source"],
            "status": "PASS_PREFLIGHT_UNDERPOWERED_STRUCTURAL",
            "same_tree_pairs_available": len(all_pairs),
            "target_pool_size": len(targets),
            "native_merge_outcomes_executed": False,
        }, indent=2))
        return

    anc = reconstruct_target_ancestor_sets(repo, targets)
    eligible = []
    asym_load = [0 for _ in targets]

    for pair in pair_bank:
        a_set = anc[pair["A"]]
        b_set = anc[pair["B"]]
        common = sorted(a_set & b_set)
        asym = sorted(a_set ^ b_set)
        for idx in asym:
            asym_load[idx] += 1
        if common and asym:
            inert_i = common[0]
            active_i = asym[0]
            eligible.append({
                **pair,
                "inert_target": targets[inert_i],
                "inert_target_index": inert_i,
                "activating_target": targets[active_i],
                "activating_target_index": active_i,
                "activating_target_ancestor_A": active_i in a_set,
                "activating_target_ancestor_B": active_i in b_set,
                "asymmetric_target_count": len(asym),
            })

    if x.get("eligible_pairs") != len(eligible):
        raise RuntimeError(
            f"eligible count mismatch: stored={x.get('eligible_pairs')} "
            f"recomputed={len(eligible)}"
        )

    expected_status = "INCLUDED" if len(eligible) >= 8 else "PREFLIGHT_UNDERPOWERED"
    if x["status"] != expected_status:
        raise RuntimeError(
            f"status mismatch: stored={x['status']} expected={expected_status}"
        )

    if expected_status == "PREFLIGHT_UNDERPOWERED":
        if x.get("exclusion_reasons") != ["eligible_pairs_lt_8"]:
            raise RuntimeError("eligibility underpower reason mismatch")
        stored_rows = x.get("eligible_pair_rows", [])
        if stored_rows != eligible:
            raise RuntimeError("eligible pair rows mismatch")
    else:
        selected = eligible if len(eligible) <= 16 else evenly_spaced(eligible, 16)
        if x.get("selected_witnesses") != selected:
            raise RuntimeError("selected witnesses mismatch")

    # Deterministic native ancestry spot-check across the matrix.
    cells = []
    if pair_bank and targets:
        pair_idxs = sorted(set(
            [0, len(pair_bank) // 4, len(pair_bank) // 2,
             (3 * len(pair_bank)) // 4, len(pair_bank) - 1]
        ))
        target_idxs = sorted(set(
            [0, len(targets) // 4, len(targets) // 2,
             (3 * len(targets)) // 4, len(targets) - 1]
        ))
        for pi in pair_idxs:
            pair = pair_bank[pi]
            for ti in target_idxs:
                target = targets[ti]
                for endpoint_key in ["A", "B"]:
                    endpoint = pair[endpoint_key]
                    native = native_is_ancestor(repo, target, endpoint)
                    recomputed = ti in anc[endpoint]
                    if native != recomputed:
                        raise RuntimeError(
                            f"native ancestry spot-check mismatch pair={pi} "
                            f"target={ti} endpoint={endpoint_key}"
                        )
                    cells.append((pi, ti, endpoint_key))

    print(json.dumps({
        "protocol": PROTOCOL,
        "source": x["source"],
        "status": (
            "PASS_INCLUDED"
            if expected_status == "INCLUDED"
            else "PASS_PREFLIGHT_UNDERPOWERED_ELIGIBILITY"
        ),
        "same_tree_pairs_available": len(all_pairs),
        "pair_bank_size": len(pair_bank),
        "target_pool_size": len(targets),
        "eligible_pairs": len(eligible),
        "native_ancestry_spot_checks": len(cells),
        "native_merge_outcomes_executed": False,
    }, indent=2))


if __name__ == "__main__":
    main()
