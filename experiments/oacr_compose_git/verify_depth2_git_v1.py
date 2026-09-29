"""Independent replay verifier for OACR-COMPOSE-G v1."""
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
        list(args), cwd=cwd, text=True, stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, env=env
    )
    if check and p.returncode != 0:
        raise RuntimeError(f"{' '.join(args)} failed ({p.returncode})\n{p.stdout}")
    return p


def fresh(repo: Path, head: str):
    run(repo, "git", "merge", "--abort", check=False)
    run(repo, "git", "reset", "--hard", "-q", head)
    run(repo, "git", "clean", "-fdq")
    run(repo, "git", "checkout", "-q", "--detach", head)


def merge_signature(repo: Path, head: str, target: str):
    fresh(repo, head)
    p = run(repo, "git", "merge", "--no-commit", "--no-ff", target, check=False)
    unmerged = sorted(x for x in run(
        repo, "git", "diff", "--name-only", "--diff-filter=U", check=False
    ).stdout.splitlines() if x)
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
        return None
    if run(repo, "git", "diff", "--name-only", "--diff-filter=U", check=False).stdout.strip():
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--result", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    repo = Path(args.repo).resolve()
    result = json.loads(Path(args.result).read_text())

    if run(repo, "git", "rev-parse", "HEAD").stdout.strip() != SOURCE_HEAD:
        raise RuntimeError("source head mismatch")

    failures = []
    checked = 0
    for row in result["results"]:
        if row["status"] not in {"H2_SEPARATED", "H2_EQUIVALENT"}:
            continue
        checked += 1
        a, b, t1, t2 = row["A"], row["B"], row["t1"], row["t2"]

        if run(repo, "git", "rev-parse", f"{a}^{{tree}}").stdout.strip() != run(
            repo, "git", "rev-parse", f"{b}^{{tree}}"
        ).stdout.strip():
            failures.append([a, b, "initial_tree_mismatch"])
            continue

        # Recheck every registered H1 target, not only t1/t2.
        for target in result["registered_targets"]:
            if merge_signature(repo, a, target)["signature"] != merge_signature(repo, b, target)["signature"]:
                failures.append([a, b, "H1_contract_mismatch", target])
                break

        a1 = make_step1(repo, a, t1)
        b1 = make_step1(repo, b, t1)
        if not a1 or not b1 or a1["tree"] != b1["tree"]:
            failures.append([a, b, "step1_replay_failure"])
            continue

        va = merge_signature(repo, a1["commit"], t2)
        vb = merge_signature(repo, b1["commit"], t2)
        observed = va["signature"] != vb["signature"]
        if observed != bool(row["H2_separated"]):
            failures.append([a, b, "H2_class_mismatch"])
        if va["signature"] != row["H2_A"]["signature"]:
            failures.append([a, b, "H2_A_signature_mismatch"])
        if vb["signature"] != row["H2_B"]["signature"]:
            failures.append([a, b, "H2_B_signature_mismatch"])

    payload = {
        "verifier": "OACR_COMPOSE_G_DEPTH2_V1_INDEPENDENT_REPLAY",
        "checked_H2_pairs": checked,
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
