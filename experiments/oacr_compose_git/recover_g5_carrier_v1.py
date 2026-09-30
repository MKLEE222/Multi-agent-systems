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


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


def map_sha(mapping: dict, sha: str | None):
    if sha is None:
        return None
    return mapping.get(sha, sha)


def validate_structure(carrier_repo: Path, bank: dict, mapping: dict):
    targets = [x["target"] for x in bank["action_selection"]["targets"]]
    tree_mismatches = []
    ancestry_mismatches = []
    mergebase_mismatches = []
    tree_mismatch_count = 0
    ancestry_mismatch_count = 0
    mergebase_mismatch_count = 0
    for pi, row in enumerate(bank["pair_rows"]):
        for side, c, expected_anc, expected_mb in (
            ("A", row["A"], row["ancestry_vector_A"], row["mergebase_vector_A"]),
            ("B", row["B"], row["ancestry_vector_B"], row["mergebase_vector_B"]),
        ):
            mc = mapping[c]
            actual_tree = git(carrier_repo, "rev-parse", f"{mc}^{{tree}}").stdout.decode().strip()
            if actual_tree != row["tree"]:
                tree_mismatch_count += 1
                if len(tree_mismatches) < 50:
                    tree_mismatches.append({
                    "pair_index": pi, "side": side, "commit": c,
                    "mapped_commit": mc, "expected_tree": row["tree"],
                    "observed_tree": actual_tree,
                    })
            for ti, t in enumerate(targets):
                mt = mapping[t]
                anc = git(carrier_repo, "merge-base", "--is-ancestor", mt, mc, check=False).returncode == 0
                if anc != bool(expected_anc[ti]):
                    ancestry_mismatch_count += 1
                    if len(ancestry_mismatches) < 50:
                        ancestry_mismatches.append({
                        "pair_index": pi, "side": side, "target_index": ti,
                        "commit": c, "target": t, "expected": bool(expected_anc[ti]),
                        "observed": anc,
                        })
                p = git(carrier_repo, "merge-base", mc, mt, check=False)
                actual_mb = p.stdout.decode().strip() if p.returncode == 0 else None
                expected_mapped = map_sha(mapping, expected_mb[ti])
                if actual_mb != expected_mapped:
                    mergebase_mismatch_count += 1
                    if len(mergebase_mismatches) < 50:
                        mergebase_mismatches.append({
                        "pair_index": pi, "side": side, "target_index": ti,
                        "commit": c, "target": t,
                        "expected_original": expected_mb[ti],
                        "expected_mapped": expected_mapped,
                        "observed": actual_mb,
                        })
    return {
        "tree_mismatch_count": tree_mismatch_count,
        "tree_mismatch_count_sampled": len(tree_mismatches),
        "tree_mismatch_sample": tree_mismatches,
        "ancestry_mismatch_count": ancestry_mismatch_count,
        "ancestry_mismatch_count_sampled": len(ancestry_mismatches),
        "ancestry_mismatch_sample": ancestry_mismatches,
        "mergebase_mismatch_count": mergebase_mismatch_count,
        "mergebase_mismatch_count_sampled": len(mergebase_mismatches),
        "mergebase_mismatch_sample": mergebase_mismatches,
    }


def validate_h1(carrier_repo: Path, bank: dict, mapping: dict, repo_root: Path):
    mod = load_module(
        repo_root / "experiments/oacr_g5/run_same_contract_git_v1.py",
        "oacr_g5_original",
    )
    targets = [x["target"] for x in bank["action_selection"]["targets"]]
    mismatch_count = 0
    mismatch_sample = []
    cells = 0
    for pi, row in enumerate(bank["pair_rows"]):
        for side, c, expected in (
            ("A", row["A"], row["outcome_signatures_A"]),
            ("B", row["B"], row["outcome_signatures_B"]),
        ):
            mc = mapping[c]
            for ti, t in enumerate(targets):
                mt = mapping[t]
                observed = mod.execute_merge(carrier_repo, mc, mt)
                cells += 1
                if observed["signature"] != expected[ti]:
                    mismatch_count += 1
                    if len(mismatch_sample) < 50:
                        mismatch_sample.append({
                            "pair_index": pi,
                            "side": side,
                            "commit": c,
                            "mapped_commit": mc,
                            "target": t,
                            "mapped_target": mt,
                            "target_index": ti,
                            "expected": expected[ti],
                            "observed": observed["signature"],
                            "observed_payload": {
                                k: observed[k] for k in (
                                    "exit_code", "already_up_to_date",
                                    "merge_in_progress", "unmerged_paths",
                                    "index_tree", "tracked_delta_sha256",
                                )
                            },
                        })
    return cells, mismatch_count, mismatch_sample


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
    if len(required) != 108:
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
    if not set(required).issubset(mapping):
        missing = sorted(set(required) - set(mapping))
        raise RuntimeError(f"mapping does not cover required SHA set: {missing[:20]}")

    # Dedicated archival refs.
    for orig in required:
        git(carrier, "update-ref", f"refs/oacr/g5/{orig}", mapping[orig])

    structure = validate_structure(carrier, bank, mapping)

    mapping_path = out_dir / "original_to_reconstructed.json"
    mapping_path.write_text(json.dumps(mapping, indent=2, sort_keys=True))
    structural_report = {
        "protocol": PROTOCOL,
        "source_artifact_id": SOURCE_ARTIFACT_ID,
        "source_bank_sha256": bank_sha,
        "required_manifest_sha256": manifest_sha,
        "source_head": bank["source"]["source_head"],
        "stats": {**stats, "github_api_requests": api.requests},
        "required_original_commits": required,
        "structural_validation": structure,
    }
    (out_dir / "structural_report.json").write_text(json.dumps(structural_report, indent=2))
    (out_dir / "structural_report.sha256").write_text(
        sha256_file(out_dir / "structural_report.json") + "  structural_report.json\n"
    )
    structural_ok = (
        structure["tree_mismatch_count"] == 0
        and structure["ancestry_mismatch_count"] == 0
        and structure["mergebase_mismatch_count"] == 0
    )
    if not structural_ok:
        print(json.dumps({
            "status": "STRUCTURAL_RECOVERY_MISMATCH",
            "stats": structural_report["stats"],
            "structural_validation": {
                "tree_mismatch_count": structure["tree_mismatch_count"],
                "ancestry_mismatch_count": structure["ancestry_mismatch_count"],
                "mergebase_mismatch_count": structure["mergebase_mismatch_count"],
            },
        }, indent=2))
        raise SystemExit(3)

    cells, mismatch_count, mismatch_sample = validate_h1(carrier, bank, mapping, repo_root)
    expected_cells = len(bank["pair_rows"]) * 2 * 12
    complete_h1 = cells == expected_cells
    h1_ok = complete_h1 and mismatch_count == 0

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
        "structural_validation": structure,
        "h1_validation": {
            "cells_expected": expected_cells,
            "cells_replayed": cells,
            "complete": complete_h1,
            "mismatch_count": mismatch_count,
            "mismatch_sample": mismatch_sample,
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
        "h1_mismatches": mismatch_count,
        "structural_tree_mismatch_sampled": structure["tree_mismatch_count_sampled"],
        "structural_ancestry_mismatch_sampled": structure["ancestry_mismatch_count_sampled"],
        "structural_mergebase_mismatch_sampled": structure["mergebase_mismatch_count_sampled"],
        "bundle_created": h1_ok,
        "bundle_sha256": bundle_sha,
        "bundle_size_bytes": bundle_size,
    }, indent=2))
    if not h1_ok:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
