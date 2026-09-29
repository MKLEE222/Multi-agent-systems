"""Independent replay verifier for OACR-COMPOSE-G v2 H2 execution."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path

SOURCE_HEAD = "34f06850c16c7f7ac822b1adc71354f11b0f2ca3"
PROTOCOL_COMMIT = "edc53ce6e1c762f4d72366da7d7eb9b6587512c2"


def run(cwd: Path, *args: str, check=True, env_extra=None):
    env = {**os.environ, "GIT_CONFIG_NOSYSTEM": "1", **(env_extra or {})}
    p = subprocess.run(
        list(args), cwd=cwd, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env
    )
    if check and p.returncode != 0:
        raise RuntimeError(f"{' '.join(args)} failed ({p.returncode})\n{p.stdout}")
    return p


def fresh(repo: Path, head: str):
    run(repo, "git", "merge", "--abort", check=False)
    run(repo, "git", "reset", "--hard", "-q", head)
    run(repo, "git", "clean", "-fdq")
    run(repo, "git", "checkout", "-q", "--detach", head)


def is_ancestor(repo: Path, anc: str, desc: str) -> bool:
    p = run(repo, "git", "merge-base", "--is-ancestor", anc, desc, check=False)
    if p.returncode not in (0, 1):
        raise RuntimeError(p.stdout)
    return p.returncode == 0


def merge_base(repo: Path, a: str, b: str) -> str:
    p = run(repo, "git", "merge-base", a, b, check=False)
    return p.stdout.strip() if p.returncode == 0 else ""


def context(repo: Path, head: str, target: str):
    return {
        "mergebase": merge_base(repo, head, target),
        "target_ancestor_head": is_ancestor(repo, target, head),
        "head_ancestor_target": is_ancestor(repo, head, target),
    }


def merge_signature(repo: Path, head: str, target: str):
    fresh(repo, head)
    p = run(repo, "git", "merge", "--no-commit", "--no-ff", target, check=False)
    unmerged = sorted(
        x for x in run(
            repo, "git", "diff", "--name-only", "--diff-filter=U", check=False
        ).stdout.splitlines() if x
    )
    diff = run(repo, "git", "diff", "--binary", "--no-ext-diff", "HEAD", check=False).stdout
    wt = run(repo, "git", "write-tree", check=False)
    payload = {
        "exit_code": p.returncode,
        "already_up_to_date": "Already up to date." in p.stdout,
        "merge_in_progress": (repo / ".git" / "MERGE_HEAD").exists(),
        "unmerged_paths": unmerged,
        "index_tree": wt.stdout.strip() if wt.returncode == 0 else None,
        "tracked_delta_sha256": hashlib.sha256(diff.encode()).hexdigest(),
    }
    payload["signature"] = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    run(repo, "git", "merge", "--abort", check=False)
    run(repo, "git", "reset", "--hard", "-q", head)
    return payload


def make_step1(repo: Path, head: str, target: str):
    fresh(repo, head)
    p = run(repo, "git", "merge", "--no-commit", "--no-ff", target, check=False)
    if p.returncode != 0 or not (repo / ".git" / "MERGE_HEAD").exists():
        run(repo, "git", "merge", "--abort", check=False)
        return None
    if run(repo, "git", "diff", "--name-only", "--diff-filter=U", check=False).stdout.strip():
        run(repo, "git", "merge", "--abort", check=False)
        return None
    wt = run(repo, "git", "write-tree", check=False)
    if wt.returncode != 0 or not wt.stdout.strip():
        run(repo, "git", "merge", "--abort", check=False)
        return None
    env = {
        "GIT_AUTHOR_NAME": "OACR COMPOSE",
        "GIT_AUTHOR_EMAIL": "oacr-compose@example.invalid",
        "GIT_COMMITTER_NAME": "OACR COMPOSE",
        "GIT_COMMITTER_EMAIL": "oacr-compose@example.invalid",
        "GIT_AUTHOR_DATE": "2000-01-01T00:00:00Z",
        "GIT_COMMITTER_DATE": "2000-01-01T00:00:00Z",
    }
    run(
        repo, "git", "-c", "core.hooksPath=/dev/null", "commit",
        "--no-gpg-sign", "-q", "-m", "OACR-COMPOSE-G step1", env_extra=env
    )
    return {
        "commit": run(repo, "git", "rev-parse", "HEAD").stdout.strip(),
        "tree": run(repo, "git", "rev-parse", "HEAD^{tree}").stdout.strip(),
    }


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


def flatten_sequences(pair_row):
    out = []
    for m in pair_row["materialized_t1"]:
        for seq in m["eligible_t2_sequences"]:
            out.append({
                "t1": m["t1"],
                "t2": seq["t2"],
                "intermediate_tree": m["intermediate_tree"],
                "A1_t2_context": seq["A1_t2_context"],
                "B1_t2_context": seq["B1_t2_context"],
            })
    return sorted(out, key=lambda x: (x["t1"], x["t2"]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--g5_json", required=True)
    ap.add_argument("--preflight", required=True)
    ap.add_argument("--result", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    g5 = json.loads(Path(args.g5_json).read_text())
    pf = json.loads(Path(args.preflight).read_text())
    result = json.loads(Path(args.result).read_text())
    fresh(repo, SOURCE_HEAD)

    failures = []
    if run(repo, "git", "rev-parse", "HEAD").stdout.strip() != SOURCE_HEAD:
        failures.append("source_head_mismatch")
    if result.get("protocol") != "OACR_COMPOSE_G_V2_H2_EXECUTION_V1":
        failures.append("unexpected_result_protocol")
    if result.get("protocol_commit") != PROTOCOL_COMMIT:
        failures.append("protocol_commit_mismatch")
    if not pf["summary"].get("passes_H2_gate"):
        failures.append("preflight_gate_false_but_result_exists")

    targets = sorted(x["target"] for x in g5["action_selection"]["targets"])
    if result.get("registered_targets") != targets:
        failures.append("target_manifest_mismatch")

    eligible_pairs = [
        row for row in pf["pairs"]
        if row["structurally_eligible_sequence_count"] > 0
    ]
    eligible_pairs.sort(key=lambda row: (row["A"], row["B"]))
    selected_pairs = evenly_spaced(eligible_pairs, min(16, len(eligible_pairs)))
    expected_selection = []
    for pair in selected_pairs:
        seqs = flatten_sequences(pair)
        if not seqs:
            failures.append(f"selected_pair_missing_sequence:{pair['A']}:{pair['B']}")
            continue
        chosen = seqs[0]
        expected_selection.append((pair, chosen))

    observed_pairs = [(row["A"], row["B"]) for row in result["results"]]
    expected_pairs = [(p["A"], p["B"]) for p, _ in expected_selection]
    if observed_pairs != expected_pairs:
        failures.append("selected_pair_order_mismatch")

    checked = 0
    separated_count = 0
    equivalent_count = 0
    g5_by_pair = {(row["A"], row["B"]): row for row in g5["pair_rows"]}

    for observed, expected in zip(result["results"], expected_selection):
        pair, chosen = expected
        a, b = pair["A"], pair["B"]
        t1, t2 = chosen["t1"], chosen["t2"]

        if observed.get("status") == "INTEGRITY_FAILURE":
            failures.append(f"producer_integrity_failure:{a}:{b}")
            continue
        if observed.get("t1") != t1 or observed.get("t2") != t2:
            failures.append(f"sequence_selection_mismatch:{a}:{b}")
            continue

        g5row = g5_by_pair[(a, b)]
        if g5row["required_separation"]:
            failures.append(f"g5_h1_not_equivalent:{a}:{b}")
            continue

        ta = run(repo, "git", "rev-parse", f"{a}^{{tree}}").stdout.strip()
        tb = run(repo, "git", "rev-parse", f"{b}^{{tree}}").stdout.strip()
        if ta != tb:
            failures.append(f"initial_tree_mismatch:{a}:{b}")
            continue

        for target in targets:
            if merge_signature(repo, a, target)["signature"] != merge_signature(repo, b, target)["signature"]:
                failures.append(f"H1_contract_mismatch:{a}:{b}:{target}")
                break
        else:
            a1 = make_step1(repo, a, t1)
            b1 = make_step1(repo, b, t1)
            if not a1 or not b1 or a1["tree"] != b1["tree"]:
                failures.append(f"step1_replay_failure:{a}:{b}:{t1}")
                continue
            if a1["tree"] != chosen["intermediate_tree"]:
                failures.append(f"intermediate_tree_mismatch:{a}:{b}:{t1}")
            ca = context(repo, a1["commit"], t2)
            cb = context(repo, b1["commit"], t2)
            if ca != chosen["A1_t2_context"] or cb != chosen["B1_t2_context"]:
                failures.append(f"preflight_context_mismatch:{a}:{b}:{t1}:{t2}")
                continue

            va = merge_signature(repo, a1["commit"], t2)
            vb = merge_signature(repo, b1["commit"], t2)
            observed_sep = va["signature"] != vb["signature"]
            if observed_sep != bool(observed.get("H2_separated")):
                failures.append(f"H2_class_mismatch:{a}:{b}")
            if va["signature"] != observed["H2_A"]["signature"]:
                failures.append(f"H2_A_signature_mismatch:{a}:{b}")
            if vb["signature"] != observed["H2_B"]["signature"]:
                failures.append(f"H2_B_signature_mismatch:{a}:{b}")
            checked += 1
            separated_count += int(observed_sep)
            equivalent_count += int(not observed_sep)

    summary = result.get("summary", {})
    if summary.get("selected_pairs") != len(expected_selection):
        failures.append("summary_selected_pairs_mismatch")
    if summary.get("H2_executions") != checked:
        failures.append("summary_H2_execution_mismatch")
    if summary.get("H2_separated") != separated_count:
        failures.append("summary_H2_separated_mismatch")
    if summary.get("H2_equivalent") != equivalent_count:
        failures.append("summary_H2_equivalent_mismatch")

    payload = {
        "verifier": "OACR_COMPOSE_G_V2_H2_INDEPENDENT_REPLAY",
        "selected_pairs_recomputed": len(expected_selection),
        "checked_H2_pairs": checked,
        "H2_separated_recomputed": separated_count,
        "H2_equivalent_recomputed": equivalent_count,
        "failure_count": len(failures),
        "failures": failures,
        "pass": not failures,
    }
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(payload, indent=2))
    print(json.dumps(payload, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
