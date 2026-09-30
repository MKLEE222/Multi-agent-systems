"""Recover a self-contained executable G5 Git carrier from the accepted artifact."""
from __future__ import annotations

import argparse
import base64
import hashlib
import importlib.util
import json
import os
import subprocess
import urllib.error
import urllib.request
from pathlib import Path

PROTOCOL = "OACR_G5_CARRIER_RECOVERY_V1"
SOURCE_ARTIFACT_ID = 10954788549
MAX_RECOVERED_COMMITS = 5000
FIXED_NAME = "OACR Carrier Recovery"
FIXED_EMAIL = "oacr-carrier@example.invalid"
FIXED_DATE = "2000-01-01T00:00:00+0000"


def run(cwd: Path, *args: str, check: bool = True, input_bytes: bytes | None = None, env_extra=None):
    env = {**os.environ, "GIT_CONFIG_NOSYSTEM": "1"}
    if env_extra:
        env.update(env_extra)
    p = subprocess.run(
        list(args),
        cwd=cwd,
        input=input_bytes,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=env,
    )
    if check and p.returncode != 0:
        raise RuntimeError(
            f"command failed ({p.returncode}): {' '.join(args)}\n"
            + p.stdout.decode("utf-8", "replace")
        )
    return p


def git(cwd: Path, *args: str, check: bool = True, input_bytes: bytes | None = None, env_extra=None):
    return run(cwd, "git", *args, check=check, input_bytes=input_bytes, env_extra=env_extra)


def object_type(repo: Path, sha: str):
    p = git(repo, "cat-file", "-t", sha, check=False)
    if p.returncode != 0:
        return None
    return p.stdout.decode().strip()


def sha256_file(path: Path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


class GitHubAPI:
    def __init__(self, token: str | None):
        self.token = token
        self.requests = 0

    def get_json(self, path: str):
        url = "https://api.github.com" + path
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "oacr-g5-carrier-recovery",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        req = urllib.request.Request(url, headers=headers)
        self.requests += 1
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "replace")
            raise RuntimeError(f"GitHub API {e.code} for {path}: {body[:1000]}") from e


def ensure_blob(repo: Path, api: GitHubAPI, sha: str, stats: dict):
    typ = object_type(repo, sha)
    if typ is not None:
        if typ != "blob":
            raise RuntimeError(f"expected blob {sha}, found {typ}")
        return
    d = api.get_json(f"/repos/git/git/git/blobs/{sha}")
    if d.get("encoding") != "base64":
        raise RuntimeError(f"unexpected blob encoding for {sha}: {d.get('encoding')}")
    raw = base64.b64decode(d["content"])
    got = git(repo, "hash-object", "-w", "--stdin", input_bytes=raw).stdout.decode().strip()
    if got != sha:
        raise RuntimeError(f"blob SHA mismatch expected={sha} got={got}")
    stats["blobs_recovered"] += 1


def ensure_tree(repo: Path, api: GitHubAPI, sha: str, stats: dict, seen: set[str]):
    typ = object_type(repo, sha)
    if typ is not None:
        if typ != "tree":
            raise RuntimeError(f"expected tree {sha}, found {typ}")
        return
    if sha in seen:
        return
    seen.add(sha)

    d = api.get_json(f"/repos/git/git/git/trees/{sha}")
    entries = d.get("tree", [])
    for e in entries:
        et = e["type"]
        es = e["sha"]
        if et == "blob":
            ensure_blob(repo, api, es, stats)
        elif et == "tree":
            ensure_tree(repo, api, es, stats, seen)
        elif et == "commit":
            # gitlink. mktree --missing permits an unavailable submodule commit.
            pass
        else:
            raise RuntimeError(f"unexpected tree entry type {et}")

    chunks = []
    for e in entries:
        name = e["path"].encode("utf-8", "surrogateescape")
        line = f"{e['mode']} {e['type']} {e['sha']}\t".encode() + name + b"\0"
        chunks.append(line)
    got = git(repo, "mktree", "-z", "--missing", input_bytes=b"".join(chunks)).stdout.decode().strip()
    if got != sha:
        raise RuntimeError(f"tree SHA mismatch expected={sha} got={got}")
    stats["trees_recovered"] += 1


def load_commit_meta(api: GitHubAPI, sha: str):
    d = api.get_json(f"/repos/git/git/git/commits/{sha}")
    if d.get("sha") != sha:
        raise RuntimeError(f"commit API SHA mismatch for {sha}")
    return {
        "sha": sha,
        "tree": d["tree"]["sha"],
        "parents": [p["sha"] for p in d.get("parents", [])],
    }


def recover_commit_mapping(repo: Path, api: GitHubAPI, required: list[str], stats: dict):
    mapping: dict[str, str] = {}
    meta: dict[str, dict] = {}

    # Iterative postorder DFS; recurse only through commit objects absent locally.
    for root in required:
        if root in mapping:
            continue
        stack: list[tuple[str, bool]] = [(root, False)]
        while stack:
            sha, expanded = stack.pop()
            if sha in mapping:
                continue

            typ = object_type(repo, sha)
            if typ is not None:
                if typ != "commit":
                    raise RuntimeError(f"expected commit {sha}, found {typ}")
                mapping[sha] = sha
                continue

            if not expanded:
                if sha not in meta:
                    meta[sha] = load_commit_meta(api, sha)
                    stats["missing_commit_objects"] += 1
                    if stats["missing_commit_objects"] > MAX_RECOVERED_COMMITS:
                        raise RuntimeError("CARRIER_RECOVERY_TOO_LARGE")
                stack.append((sha, True))
                for p in reversed(meta[sha]["parents"]):
                    if p not in mapping:
                        stack.append((p, False))
                continue

            m = meta[sha]
            parent_map = [mapping[p] for p in m["parents"]]
            ensure_tree(repo, api, m["tree"], stats, set())
            args = ["commit-tree", m["tree"]]
            for p in parent_map:
                args += ["-p", p]
            env = {
                "GIT_AUTHOR_NAME": FIXED_NAME,
                "GIT_AUTHOR_EMAIL": FIXED_EMAIL,
                "GIT_COMMITTER_NAME": FIXED_NAME,
                "GIT_COMMITTER_EMAIL": FIXED_EMAIL,
                "GIT_AUTHOR_DATE": FIXED_DATE,
                "GIT_COMMITTER_DATE": FIXED_DATE,
            }
            msg = f"OACR G5 carrier surrogate for {sha}\n".encode()
            synthetic = git(repo, *args, input_bytes=msg, env_extra=env).stdout.decode().strip()
            if git(repo, "rev-parse", f"{synthetic}^{{tree}}").stdout.decode().strip() != m["tree"]:
                raise RuntimeError(f"synthetic tree mismatch for {sha}")
            got_parents = git(repo, "show", "-s", "--format=%P", synthetic).stdout.decode().strip().split()
            if got_parents != parent_map:
                raise RuntimeError(f"synthetic parent mismatch for {sha}")
            mapping[sha] = synthetic
            stats["synthetic_commits_created"] += 1

    return mapping, meta


def load_h2_module(repo_root: Path):
    path = repo_root / "experiments/oacr_compose_git/run_g5_h2_v1.py"
    spec = importlib.util.spec_from_file_location("oacr_g5_h2", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


def validate_h1(carrier_repo: Path, bank: dict, mapping: dict, repo_root: Path):
    mod = load_h2_module(repo_root)
    targets = [x["target"] for x in bank["action_selection"]["targets"]]
    mismatches = []
    cells = 0
    for pi, row in enumerate(bank["pair_rows"]):
        for side, c, expected in (
            ("A", row["A"], row["outcome_signatures_A"]),
            ("B", row["B"], row["outcome_signatures_B"]),
        ):
            mc = mapping[c]
            for ti, t in enumerate(targets):
                mt = mapping[t]
                payload, _, _ = mod.merge_payload(carrier_repo, mc, mt, persist=False)
                cells += 1
                if payload["signature"] != expected[ti]:
                    mismatches.append({
                        "pair_index": pi,
                        "side": side,
                        "commit": c,
                        "mapped_commit": mc,
                        "target": t,
                        "mapped_target": mt,
                        "target_index": ti,
                        "expected": expected[ti],
                        "observed": payload["signature"],
                    })
                    if len(mismatches) >= 50:
                        return cells, mismatches
    return cells, mismatches


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True, help="full clone of git/git used as object cache")
    ap.add_argument("--bank", required=True, help="accepted G5 validation JSON")
    ap.add_argument("--repo_root", required=True, help="Multi-agent-systems checkout")
    ap.add_argument("--out_dir", required=True)
    args = ap.parse_args()

    carrier = Path(args.repo).resolve()
    bank_path = Path(args.bank).resolve()
    repo_root = Path(args.repo_root).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    bank = json.loads(bank_path.read_text())
    if bank.get("protocol") != "OACR_G5_SAME_CONTRACT_GIT_V1" or bank.get("split") != "validation":
        raise RuntimeError("wrong G5 bank")

    required = sorted(set(
        [bank["source"]["source_head"]]
        + [x["target"] for x in bank["action_selection"]["targets"]]
        + [r["A"] for r in bank["pair_rows"]]
        + [r["B"] for r in bank["pair_rows"]]
    ))
    if len(required) != 104:
        raise RuntimeError(f"required SHA count changed: {len(required)}")

    api = GitHubAPI(os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN"))
    stats = {
        "required_original_commits": len(required),
        "missing_commit_objects": 0,
        "synthetic_commits_created": 0,
        "trees_recovered": 0,
        "blobs_recovered": 0,
    }

    mapping, meta = recover_commit_mapping(carrier, api, required, stats)
    if set(mapping) != set(required):
        raise RuntimeError("mapping does not cover required SHA set")

    # Dedicated archival refs.
    for orig in required:
        git(carrier, "update-ref", f"refs/oacr/g5/{orig}", mapping[orig])

    cells, mismatches = validate_h1(carrier, bank, mapping, repo_root)
    if cells != len(bank["pair_rows"]) * 2 * 12:
        raise RuntimeError(f"incomplete H1 replay cells={cells}")
    h1_ok = len(mismatches) == 0

    mapping_path = out_dir / "original_to_reconstructed.json"
    mapping_path.write_text(json.dumps(mapping, indent=2, sort_keys=True))

    refs = [
        x.decode().strip()
        for x in git(carrier, "for-each-ref", "--format=%(refname)", "refs/oacr/g5/").stdout.splitlines()
    ]
    if len(refs) != len(required):
        raise RuntimeError(f"archival ref count mismatch {len(refs)}")

    bundle_path = out_dir / "g5_executable_carrier.bundle"
    if h1_ok:
        git(carrier, "bundle", "create", str(bundle_path), *refs)
        git(carrier, "bundle", "verify", str(bundle_path))
        bundle_sha = sha256_file(bundle_path)
        bundle_size = bundle_path.stat().st_size
    else:
        bundle_sha = None
        bundle_size = None

    report = {
        "protocol": PROTOCOL,
        "source_artifact_id": SOURCE_ARTIFACT_ID,
        "source_bank_sha256": sha256_file(bank_path),
        "source_head": bank["source"]["source_head"],
        "stats": {**stats, "github_api_requests": api.requests},
        "required_original_commits": required,
        "missing_commit_metadata": meta,
        "h1_validation": {
            "cells_replayed": cells,
            "mismatch_count": len(mismatches),
            "mismatch_sample": mismatches[:50],
            "accepted": h1_ok,
        },
        "bundle": {
            "created": h1_ok,
            "sha256": bundle_sha,
            "size_bytes": bundle_size,
            "ref_count": len(refs),
        },
    }
    (out_dir / "recovery_report.json").write_text(json.dumps(report, indent=2))
    (out_dir / "recovery_report.sha256").write_text(
        sha256_file(out_dir / "recovery_report.json") + "  recovery_report.json\n"
    )
    (out_dir / "mapping.sha256").write_text(
        sha256_file(mapping_path) + "  original_to_reconstructed.json\n"
    )
    if h1_ok:
        (out_dir / "bundle.sha256").write_text(bundle_sha + "  g5_executable_carrier.bundle\n")

    print(json.dumps({
        "required_original_commits": len(required),
        "missing_commit_objects": stats["missing_commit_objects"],
        "synthetic_commits_created": stats["synthetic_commits_created"],
        "trees_recovered": stats["trees_recovered"],
        "blobs_recovered": stats["blobs_recovered"],
        "github_api_requests": api.requests,
        "h1_cells_replayed": cells,
        "h1_mismatches": len(mismatches),
        "bundle_created": h1_ok,
        "bundle_sha256": bundle_sha,
        "bundle_size_bytes": bundle_size,
    }, indent=2))
    if not h1_ok:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
