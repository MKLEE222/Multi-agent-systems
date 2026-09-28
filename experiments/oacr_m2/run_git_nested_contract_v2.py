"""OACR-M2-G v2: exact Git contract lattice with full recomputation artifacts."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "common"))

from operational_partition import (  # noqa: E402
    block_index,
    directional_information_gap,
    partition_from_signatures,
    refinement_relation,
)

SOURCE_HEAD = "34f06850c16c7f7ac822b1adc71354f11b0f2ca3"
EXPECTED_GIT_VERSION = "git version 2.55.0"
TOL = 1e-12
ENDPOINTS = {
    "discovery": {
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
        "R2_E": 0.9166666666666661,
    },
    "validation": {
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
    },
}


def canonical_json(x) -> str:
    return json.dumps(x, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha_obj(x) -> str:
    return hashlib.sha256(canonical_json(x).encode("utf-8")).hexdigest()


def frozen_env():
    return {
        **os.environ,
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": "/dev/null",
        "LC_ALL": "C.UTF-8",
        "LANG": "C.UTF-8",
        "TZ": "UTC",
    }


def run(cwd: Path, *args: str, check: bool = True):
    p = subprocess.run(
        list(args),
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=frozen_env(),
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
    sig = hashlib.sha256(canonical_json(payload).encode()).hexdigest()
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
    chosen = scored[:12]
    return [t for _, t in chosen], [
        {
            "action_index": i,
            "action_id": t,
            "target_commit": t,
            "discovery_ancestry_disagreements": score,
        }
        for i, (score, t) in enumerate(chosen)
    ]


def block_sizes(partition):
    return sorted((len(x) for x in partition), reverse=True)


def partition_assignment(partition, state_ids):
    canonical_blocks = sorted(
        [sorted(block, key=str) for block in partition],
        key=lambda block: [str(x) for x in block],
    )
    ci = {}
    for i, block in enumerate(canonical_blocks):
        for x in block:
            ci[x] = i
    return [ci[s] for s in state_ids]


def is_refinement(fine, coarse) -> bool:
    ci = {}
    for i, block in enumerate(coarse):
        for x in block:
            ci[x] = i
    return all(len({ci[x] for x in block}) == 1 for block in fine)


def approx(a, b, tol=1e-10):
    return abs(float(a) - float(b)) <= tol


def quantiles(values):
    xs = sorted(float(x) for x in values)
    if not xs:
        return {}
    def pick(q):
        if len(xs) == 1:
            return xs[0]
        pos = q * (len(xs) - 1)
        lo = math.floor(pos)
        hi = math.ceil(pos)
        if lo == hi:
            return xs[lo]
        return xs[lo] * (hi - pos) + xs[hi] * (pos - lo)
    return {
        "n": len(xs),
        "min": xs[0],
        "q25": pick(0.25),
        "median": pick(0.5),
        "q75": pick(0.75),
        "max": xs[-1],
    }


def diagnostics(rep_partition, op_partition):
    info = directional_information_gap(rep_partition, op_partition)
    pair = refinement_relation(rep_partition, op_partition)
    h_o = info["operational_entropy_bits"]
    h_r = info["representation_entropy_bits"]
    return {
        **info,
        "representation_blocks": len(rep_partition),
        "under_refinement_count": pair["under_refinement_count"],
        "over_refinement_count": pair["over_refinement_count"],
        "normalized_U_by_HO": (info["omission_U_bits"] / h_o) if h_o > TOL else 0.0,
        "normalized_E_by_HR": (info["excess_E_bits"] / h_r) if h_r > TOL else 0.0,
    }


def transition_summary(chain_rows, rep_names):
    out = {}
    for name in rep_names:
        adequate = [r["k"] for r in chain_rows if r["diagnostics"][name]["omission_U_bits"] <= TOL]
        inadequate = [r["k"] for r in chain_rows if r["diagnostics"][name]["omission_U_bits"] > TOL]
        zero_e = [r["k"] for r in chain_rows if r["diagnostics"][name]["excess_E_bits"] <= TOL]
        exact = [
            r["k"] for r in chain_rows
            if r["diagnostics"][name]["omission_U_bits"] <= TOL
            and r["diagnostics"][name]["excess_E_bits"] <= TOL
        ]
        interval = None
        if exact and exact == list(range(min(exact), max(exact) + 1)):
            interval = [min(exact), max(exact)]
        out[name] = {
            "first_inadequate_prefix": min(inadequate) if inadequate else None,
            "last_adequate_prefix": max(adequate) if adequate else None,
            "first_zero_excess_prefix": min(zero_e) if zero_e else None,
            "exact_match_prefixes": exact,
            "exact_match_interval": interval,
        }
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--split", choices=["discovery", "validation"], required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    git_version = git(repo, "--version").stdout.strip()
    if git_version != EXPECTED_GIT_VERSION:
        raise RuntimeError(f"Git version mismatch: {git_version}")
    source_head = git(repo, "rev-parse", "HEAD").stdout.strip()
    if source_head != SOURCE_HEAD:
        raise RuntimeError(f"source HEAD mismatch: {source_head}")

    git(repo, "config", "--local", "rerere.enabled", "false")
    git(repo, "config", "--local", "merge.conflictStyle", "merge")

    commits, discovery, validation, total_groups = natural_pair_banks(repo, 20000)
    targets, action_manifest = select_targets(repo, discovery)
    pairs = discovery if args.split == "discovery" else validation

    state_ids = []
    tree_of = {}
    state_manifest = []
    pair_manifest = []
    for pi, p in enumerate(pairs):
        pair_manifest.append({"pair_index": pi, **p})
        for side in ("A", "B"):
            c = p[side]
            state_ids.append(c)
            tree_of[c] = p["tree"]
            state_manifest.append({
                "state_index": len(state_manifest),
                "commit": c,
                "tree": p["tree"],
                "pair_index": pi,
                "pair_side": side,
                "split": args.split,
            })
    if len(set(state_ids)) != len(state_ids):
        raise RuntimeError("duplicate state endpoints")

    ancestry12 = {}
    mergebase12 = {}
    outcome_matrix = {}
    for c in state_ids:
        ancestry12[c] = tuple(is_ancestor(repo, t, c) for t in targets)
        mergebase12[c] = tuple(merge_base(repo, c, t) for t in targets)
        outcome_matrix[c] = [execute_merge(repo, c, t) for t in targets]

    rep_signatures = {
        "R0_fixed_current_tree": {c: tree_of[c] for c in state_ids},
        "Rfull_fixed_commit_identity": {c: c for c in state_ids},
        "R1_fixed12_tree_plus_ancestry": {
            c: [tree_of[c], list(ancestry12[c])] for c in state_ids
        },
        "R2_fixed12_tree_plus_mergebase": {
            c: [tree_of[c], list(mergebase12[c])] for c in state_ids
        },
    }
    reps = {
        name: partition_from_signatures(state_ids, lambda c, sigs=sigs: sigs[c])
        for name, sigs in rep_signatures.items()
    }

    def op_partition_for(indices):
        idxs = sorted(indices)
        return partition_from_signatures(
            state_ids,
            lambda c: (
                tree_of[c],
                tuple(outcome_matrix[c][i]["signature"] for i in idxs),
            ),
        )

    analysis = []
    by_k = defaultdict(list)
    for mask in range(1 << 12):
        idxs = [i for i in range(12) if mask & (1 << i)]
        op = op_partition_for(idxs)
        diag = {name: diagnostics(rep, op) for name, rep in reps.items()}
        pair_required = []
        op_bi = block_index(op)
        for p in pairs:
            pair_required.append(op_bi[p["A"]] != op_bi[p["B"]])
        row = {
            "contract_id": f"mask:{mask:03x}",
            "mask": mask,
            "k": len(idxs),
            "action_indices": idxs,
            "action_ids": [targets[i] for i in idxs],
            "operational_blocks": len(op),
            "operational_block_sizes": block_sizes(op),
            "operational_partition_assignment": partition_assignment(op, state_ids),
            "required_pair_separations": sum(pair_required),
            "behaviorally_equivalent_pairs": len(pair_required) - sum(pair_required),
            "diagnostics": diag,
        }
        analysis.append(row)
        by_k[len(idxs)].append(row)

    lattice_summary = []
    for k in range(13):
        rows = by_k[k]
        summary = {
            "k": k,
            "all_contracts_of_size_k": len(rows),
            "operational_blocks": quantiles([r["operational_blocks"] for r in rows]),
            "operational_entropy_bits": quantiles([
                next(iter(r["diagnostics"].values()))["operational_entropy_bits"]
                for r in rows
            ]),
            "required_pair_separations": quantiles([r["required_pair_separations"] for r in rows]),
            "representations": {},
        }
        for name in reps:
            ds = [r["diagnostics"][name] for r in rows]
            summary["representations"][name] = {
                "U_bits": quantiles([d["omission_U_bits"] for d in ds]),
                "E_bits": quantiles([d["excess_E_bits"] for d in ds]),
                "under_refinement_count": quantiles([d["under_refinement_count"] for d in ds]),
                "over_refinement_count": quantiles([d["over_refinement_count"] for d in ds]),
                "adequate_exact_subset_fraction": sum(
                    d["omission_U_bits"] <= TOL for d in ds
                ) / len(ds),
                "exact_match_exact_subset_fraction": sum(
                    d["omission_U_bits"] <= TOL and d["excess_E_bits"] <= TOL
                    for d in ds
                ) / len(ds),
            }
        lattice_summary.append(summary)

    canonical_rows = []
    previous_op = None
    previous_row = None
    refinement_failures = []
    for k in range(13):
        mask = (1 << k) - 1
        row = next(r for r in analysis if r["mask"] == mask)
        op = op_partition_for(range(k))
        if previous_op is not None and not is_refinement(op, previous_op):
            refinement_failures.append(k)
        row = dict(row)
        row["canonical_prefix"] = True
        row["delta_operational_blocks"] = (
            row["operational_blocks"] - previous_row["operational_blocks"]
            if previous_row is not None else 0
        )
        h_o = next(iter(row["diagnostics"].values()))["operational_entropy_bits"]
        prev_h_o = (
            next(iter(previous_row["diagnostics"].values()))["operational_entropy_bits"]
            if previous_row is not None else h_o
        )
        row["delta_operational_entropy_bits"] = h_o - prev_h_o
        row["diagnostics"] = {name: dict(d) for name, d in row["diagnostics"].items()}
        for name in reps:
            d = row["diagnostics"][name]
            pd = previous_row["diagnostics"][name] if previous_row is not None else d
            d["delta_U_bits"] = d["omission_U_bits"] - pd["omission_U_bits"]
            d["delta_E_bits"] = d["excess_E_bits"] - pd["excess_E_bits"]
        canonical_rows.append(row)
        previous_op = op
        previous_row = row

    if refinement_failures:
        raise RuntimeError(f"canonical nested refinement failed: {refinement_failures}")

    endpoint = canonical_rows[-1]
    target = ENDPOINTS[args.split]
    d0 = endpoint["diagnostics"]["R0_fixed_current_tree"]
    df = endpoint["diagnostics"]["Rfull_fixed_commit_identity"]
    d1 = endpoint["diagnostics"]["R1_fixed12_tree_plus_ancestry"]
    d2 = endpoint["diagnostics"]["R2_fixed12_tree_plus_mergebase"]
    endpoint_ok = (
        endpoint["operational_blocks"] == target["operational_blocks"]
        and endpoint["required_pair_separations"] == target["required_pairs"]
        and endpoint["behaviorally_equivalent_pairs"] == target["equivalent_pairs"]
        and approx(d0["omission_U_bits"], target["R0_U"])
        and approx(d0["excess_E_bits"], target["R0_E"])
        and approx(df["omission_U_bits"], target["Rfull_U"])
        and approx(df["excess_E_bits"], target["Rfull_E"])
        and approx(d1["omission_U_bits"], target["R1_U"])
        and approx(d1["excess_E_bits"], target["R1_E"])
        and approx(d2["omission_U_bits"], target["R2_U"])
        and approx(d2["excess_E_bits"], target["R2_E"])
    )
    if not endpoint_ok:
        raise RuntimeError(f"G5 {args.split} endpoint regression failed")

    weights = {s: 1.0 / len(state_ids) for s in state_ids}
    manifest_hashes = {
        "state_manifest_sha256": sha_obj(state_manifest),
        "pair_manifest_sha256": sha_obj(pair_manifest),
        "action_manifest_sha256": sha_obj(action_manifest),
        "representation_signatures_sha256": sha_obj(rep_signatures),
        "outcome_matrix_sha256": sha_obj(outcome_matrix),
        "weights_sha256": sha_obj(weights),
    }

    out = {
        "protocol": "OACR_M2_G_NESTED_CONTRACT_V2",
        "split": args.split,
        "amendment_commit": "6c0e174df46f2a2b9796493a4798e895f649e3f3",
        "source": {
            "remote": git(repo, "remote", "get-url", "origin").stdout.strip(),
            "source_head": source_head,
            "commits_enumerated": len(commits),
            "same_tree_groups_available": total_groups,
            "g5_run": 36385706858,
            "g5_checkpoint_commit": "5cc8baf1db8b66061032da6c99723a2956f98121",
        },
        "runtime_manifest": {
            "python": sys.version,
            "platform": platform.platform(),
            "git_version": git_version,
            "locale_LC_ALL": frozen_env()["LC_ALL"],
            "locale_LANG": frozen_env()["LANG"],
            "timezone": frozen_env()["TZ"],
            "git_config_nosystem": frozen_env()["GIT_CONFIG_NOSYSTEM"],
            "git_config_global": frozen_env()["GIT_CONFIG_GLOBAL"],
            "git_local_config": git(repo, "config", "--local", "--list").stdout.splitlines(),
            "github_sha": os.environ.get("GITHUB_SHA"),
        },
        "state_manifest": state_manifest,
        "pair_manifest": pair_manifest,
        "action_manifest": action_manifest,
        "weights": weights,
        "fixed_representation_signatures": rep_signatures,
        "state_action_outcomes": outcome_matrix,
        "manifest_hashes": manifest_hashes,
        "canonical_chain": {
            "rule": "immutable G5 target order: discovery ancestry disagreement desc, lexical tie break",
            "trajectory": canonical_rows,
            "transition_summary": transition_summary(canonical_rows, list(reps)),
        },
        "exact_contract_lattice": {
            "contract_count": len(analysis),
            "all_subsets_enumerated": True,
            "summary_by_k": lattice_summary,
            "contracts": analysis,
        },
        "checks": {
            "canonical_nested_refinement_failures": refinement_failures,
            "endpoint_regression_passed": endpoint_ok,
            "full_contract_operational_blocks": endpoint["operational_blocks"],
            "full_contract_required_pairs": endpoint["required_pair_separations"],
        },
    }

    p = Path(args.out)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(out, indent=2))
    print(json.dumps({
        "protocol": out["protocol"],
        "split": args.split,
        "manifest_hashes": manifest_hashes,
        "endpoint_regression_passed": endpoint_ok,
        "transition_summary": out["canonical_chain"]["transition_summary"],
        "exact_contract_count": len(analysis),
    }, indent=2))


if __name__ == "__main__":
    main()
