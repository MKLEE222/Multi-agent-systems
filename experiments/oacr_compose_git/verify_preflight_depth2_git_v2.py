"""Independent verifier for OACR-COMPOSE-G v2 structural preflight.

This verifier reconstructs the frozen pair bank and every reported materializable
first action / structurally eligible second target without executing a second merge.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path

SOURCE_HEAD = "34f06850c16c7f7ac822b1adc71354f11b0f2ca3"


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


def merge_probe(repo: Path, head: str, target: str):
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


def materialize(repo: Path, head: str, target: str):
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


def context(repo: Path, head: str, target: str):
    return {
        "mergebase": merge_base(repo, head, target),
        "target_ancestor_head": is_ancestor(repo, target, head),
        "head_ancestor_target": is_ancestor(repo, head, target),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--g5_json", required=True)
    ap.add_argument("--preflight", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    g5 = json.loads(Path(args.g5_json).read_text())
    pf = json.loads(Path(args.preflight).read_text())
    fresh(repo, SOURCE_HEAD)

    failures = []
    if g5.get("protocol") != "OACR_G5_SAME_CONTRACT_GIT_V1" or g5.get("split") != "validation":
        failures.append("unexpected_g5_artifact")
    if pf.get("protocol") != "OACR_COMPOSE_G_V2_STRUCTURAL_PREFLIGHT":
        failures.append("unexpected_preflight_protocol")
    if pf.get("protocol_commit") != "02d2b1143bf6254cbdb12ef773aff4a340f90ccf":
        failures.append("protocol_commit_mismatch")
    if pf["summary"].get("second_merge_outcomes_executed") != 0:
        failures.append("second_merge_outcome_claim_nonzero")

    targets = sorted(x["target"] for x in g5["action_selection"]["targets"])
    if pf["registered_targets"] != targets:
        failures.append("target_manifest_mismatch")

    expected_pairs = []
    for row in g5["pair_rows"]:
        if row["required_separation"]:
            continue
        if row["ancestry_vector_A"] != row["ancestry_vector_B"]:
            continue
        if not any(a != b for a, b in zip(row["mergebase_vector_A"], row["mergebase_vector_B"])):
            continue
        expected_pairs.append((row["A"], row["B"]))
    expected_pairs.sort()

    observed_pairs = sorted((row["A"], row["B"]) for row in pf["pairs"])
    if observed_pairs != expected_pairs:
        failures.append("pair_bank_mismatch")

    recomputed_materializable = 0
    recomputed_pairs_with_t1 = 0
    recomputed_sequences = 0
    recomputed_pairs_with_seq = 0

    for row in pf["pairs"]:
        a, b = row["A"], row["B"]
        verified_t1 = 0
        verified_seq = 0

        expected_t1_set = []
        for candidate_t1 in targets:
            ca_probe = merge_probe(repo, a, candidate_t1)
            cb_probe = merge_probe(repo, b, candidate_t1)
            candidate_ok = (
                ca_probe["exit_code"] == 0 and cb_probe["exit_code"] == 0
                and not ca_probe["unmerged_paths"] and not cb_probe["unmerged_paths"]
                and ca_probe["merge_in_progress"] and cb_probe["merge_in_progress"]
                and ca_probe["index_tree"] is not None
                and ca_probe["index_tree"] == cb_probe["index_tree"]
                and ca_probe["signature"] == cb_probe["signature"]
            )
            if candidate_ok:
                ca1 = materialize(repo, a, candidate_t1)
                cb1 = materialize(repo, b, candidate_t1)
                if ca1 and cb1 and ca1["tree"] == cb1["tree"]:
                    expected_t1_set.append(candidate_t1)

        observed_t1_set = [item["t1"] for item in row["materialized_t1"]]
        if observed_t1_set != expected_t1_set:
            failures.append(f"materializable_t1_set_mismatch:{a}:{b}")

        for item in row["materialized_t1"]:
            t1 = item["t1"]
            ma = merge_probe(repo, a, t1)
            mb = merge_probe(repo, b, t1)
            ok = (
                ma["exit_code"] == 0 and mb["exit_code"] == 0
                and not ma["unmerged_paths"] and not mb["unmerged_paths"]
                and ma["merge_in_progress"] and mb["merge_in_progress"]
                and ma["index_tree"] is not None
                and ma["index_tree"] == mb["index_tree"]
                and ma["signature"] == mb["signature"]
            )
            if not ok:
                failures.append(f"materializable_t1_replay_failed:{a}:{b}:{t1}")
                continue

            a1 = materialize(repo, a, t1)
            b1 = materialize(repo, b, t1)
            if not a1 or not b1 or a1["tree"] != b1["tree"]:
                failures.append(f"step1_materialization_failed:{a}:{b}:{t1}")
                continue
            if a1["tree"] != item["intermediate_tree"]:
                failures.append(f"intermediate_tree_mismatch:{a}:{b}:{t1}")
            verified_t1 += 1

            expected_t2 = []
            for t2 in targets:
                if t2 == t1:
                    continue
                ca = context(repo, a1["commit"], t2)
                cb = context(repo, b1["commit"], t2)
                if ca["target_ancestor_head"] and cb["target_ancestor_head"]:
                    continue
                diff = (
                    ca["mergebase"] != cb["mergebase"]
                    or ca["target_ancestor_head"] != cb["target_ancestor_head"]
                    or ca["head_ancestor_target"] != cb["head_ancestor_target"]
                )
                if diff:
                    expected_t2.append((t2, ca, cb))
            observed = item["eligible_t2_sequences"]
            if [x["t2"] for x in observed] != [x[0] for x in expected_t2]:
                failures.append(f"eligible_t2_set_mismatch:{a}:{b}:{t1}")
            for obs, (_, ca, cb) in zip(observed, expected_t2):
                if obs["A1_t2_context"] != ca or obs["B1_t2_context"] != cb:
                    failures.append(f"t2_context_mismatch:{a}:{b}:{t1}:{obs['t2']}")
            verified_seq += len(expected_t2)

        if verified_t1 != row["materializable_t1_count"]:
            failures.append(f"materializable_count_mismatch:{a}:{b}")
        if verified_seq != row["structurally_eligible_sequence_count"]:
            failures.append(f"sequence_count_mismatch:{a}:{b}")

        recomputed_materializable += verified_t1
        recomputed_sequences += verified_seq
        recomputed_pairs_with_t1 += int(verified_t1 > 0)
        recomputed_pairs_with_seq += int(verified_seq > 0)

    s = pf["summary"]
    checks = {
        "pair_bank": len(expected_pairs),
        "pairs_with_materializable_t1": recomputed_pairs_with_t1,
        "materializable_t1_total": recomputed_materializable,
        "pairs_with_structurally_eligible_sequence": recomputed_pairs_with_seq,
        "structurally_eligible_sequences_total": recomputed_sequences,
    }
    for key, value in checks.items():
        if s.get(key) != value:
            failures.append(f"summary_mismatch:{key}")
    expected_gate = recomputed_pairs_with_seq >= 3 and recomputed_sequences >= 8
    if s.get("passes_H2_gate") != expected_gate:
        failures.append("gate_mismatch")

    payload = {
        "verifier": "OACR_COMPOSE_G_V2_STRUCTURAL_PREFLIGHT_INDEPENDENT",
        "pairs_checked": len(expected_pairs),
        "materializable_t1_recomputed": recomputed_materializable,
        "eligible_sequences_recomputed": recomputed_sequences,
        "passes_H2_gate_recomputed": expected_gate,
        "failure_count": len(failures),
        "failures": failures,
        "pass": not failures,
        "second_merge_outcomes_executed": 0,
    }
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(payload, indent=2))
    print(json.dumps(payload, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
