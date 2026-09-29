"""OACR-COMPOSE-G v2: prospective H2 native Git execution after verified structural preflight."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "oacr_g5"))
sys.path.insert(0, str(HERE))

from run_same_contract_git_v1 import execute_merge, is_ancestor, merge_base, git  # noqa: E402
from run_depth2_git_v1 import deterministic_merge_commit, evenly_spaced  # noqa: E402

SOURCE_HEAD = "34f06850c16c7f7ac822b1adc71354f11b0f2ca3"
PROTOCOL_COMMIT = "edc53ce6e1c762f4d72366da7d7eb9b6587512c2"
PREFLIGHT_PROTOCOL = "OACR_COMPOSE_G_V2_STRUCTURAL_PREFLIGHT"


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def context(repo: Path, head: str, target: str):
    return {
        "mergebase": merge_base(repo, head, target),
        "target_ancestor_head": is_ancestor(repo, target, head),
        "head_ancestor_target": is_ancestor(repo, head, target),
    }


def flatten_sequences(pair_row):
    seqs = []
    for m in pair_row["materialized_t1"]:
        for seq in m["eligible_t2_sequences"]:
            seqs.append({
                "t1": m["t1"],
                "t2": seq["t2"],
                "intermediate_tree": m["intermediate_tree"],
                "A1": seq["A1"],
                "B1": seq["B1"],
                "A1_t2_context": seq["A1_t2_context"],
                "B1_t2_context": seq["B1_t2_context"],
            })
    return sorted(seqs, key=lambda x: (x["t1"], x["t2"]))


def h1_ok(ma, mb):
    return (
        ma["exit_code"] == 0
        and mb["exit_code"] == 0
        and not ma["unmerged_paths"]
        and not mb["unmerged_paths"]
        and ma["merge_in_progress"]
        and mb["merge_in_progress"]
        and ma["index_tree"] is not None
        and ma["index_tree"] == mb["index_tree"]
        and ma["signature"] == mb["signature"]
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--g5_json", required=True)
    ap.add_argument("--preflight", required=True)
    ap.add_argument("--preflight_verify", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    g5_path = Path(args.g5_json)
    pf_path = Path(args.preflight)
    pfv_path = Path(args.preflight_verify)
    g5 = json.loads(g5_path.read_text())
    pf = json.loads(pf_path.read_text())
    pfv = json.loads(pfv_path.read_text())

    if git(repo, "rev-parse", "HEAD").stdout.strip() != SOURCE_HEAD:
        raise RuntimeError("source checkout mismatch")
    if g5.get("protocol") != "OACR_G5_SAME_CONTRACT_GIT_V1" or g5.get("split") != "validation":
        raise RuntimeError("unexpected G5 artifact")
    if g5["source"]["source_head"] != SOURCE_HEAD:
        raise RuntimeError("G5 source head mismatch")
    if pf.get("protocol") != PREFLIGHT_PROTOCOL:
        raise RuntimeError("unexpected preflight artifact")
    if pf["summary"].get("second_merge_outcomes_executed") != 0:
        raise RuntimeError("preflight claims second-merge outcome execution")
    if not pfv.get("pass") or pfv.get("failure_count") != 0:
        raise RuntimeError("preflight independent verifier did not pass")
    if pfv.get("second_merge_outcomes_executed") != 0:
        raise RuntimeError("preflight verifier reports second-merge outcome execution")
    if not pf["summary"].get("passes_H2_gate"):
        raise RuntimeError("H2 gate is false; second merge is not authorized")

    targets = sorted(x["target"] for x in g5["action_selection"]["targets"])
    if pf["registered_targets"] != targets:
        raise RuntimeError("preflight target manifest mismatch")

    eligible_pairs = [
        row for row in pf["pairs"]
        if row["structurally_eligible_sequence_count"] > 0
    ]
    eligible_pairs.sort(key=lambda row: (row["A"], row["B"]))
    selected_pairs = evenly_spaced(eligible_pairs, min(16, len(eligible_pairs)))

    g5_by_pair = {(row["A"], row["B"]): row for row in g5["pair_rows"]}
    results = []
    for pair in selected_pairs:
        a, b = pair["A"], pair["B"]
        seqs = flatten_sequences(pair)
        if not seqs:
            results.append({
                "A": a, "B": b, "status": "INTEGRITY_FAILURE",
                "failure": "selected_pair_has_no_eligible_sequence",
            })
            continue
        chosen = seqs[0]
        t1, t2 = chosen["t1"], chosen["t2"]
        failures = []

        g5_row = g5_by_pair.get((a, b))
        if g5_row is None:
            failures.append("pair_missing_from_g5")
        else:
            if g5_row["required_separation"]:
                failures.append("pair_not_h1_equivalent_in_g5")
            if g5_row["ancestry_vector_A"] != g5_row["ancestry_vector_B"]:
                failures.append("pair_ancestry_vector_mismatch")

        ta = git(repo, "rev-parse", f"{a}^{{tree}}").stdout.strip()
        tb = git(repo, "rev-parse", f"{b}^{{tree}}").stdout.strip()
        if ta != tb:
            failures.append("initial_tree_mismatch")

        # Full accepted G5 H1 contract replay.
        for target in targets:
            ma = execute_merge(repo, a, target)
            mb = execute_merge(repo, b, target)
            if ma["signature"] != mb["signature"]:
                failures.append(f"H1_contract_mismatch:{target}")
                break

        ma1 = execute_merge(repo, a, t1)
        mb1 = execute_merge(repo, b, t1)
        if not h1_ok(ma1, mb1):
            failures.append("selected_t1_not_materializable")

        a1 = deterministic_merge_commit(repo, a, t1)
        b1 = deterministic_merge_commit(repo, b, t1)
        if not a1["ok"] or not b1["ok"]:
            failures.append("step1_materialization_failure")
        elif a1["tree"] != b1["tree"]:
            failures.append("step1_tree_mismatch")
        elif a1["tree"] != chosen["intermediate_tree"]:
            failures.append("preflight_intermediate_tree_mismatch")

        if not failures:
            ca = context(repo, a1["commit"], t2)
            cb = context(repo, b1["commit"], t2)
            if ca != chosen["A1_t2_context"]:
                failures.append("preflight_A1_context_mismatch")
            if cb != chosen["B1_t2_context"]:
                failures.append("preflight_B1_context_mismatch")

        base = {
            "A": a,
            "B": b,
            "initial_tree": ta,
            "t1": t1,
            "t2": t2,
            "preflight_intermediate_tree": chosen["intermediate_tree"],
            "preflight_A1_t2_context": chosen["A1_t2_context"],
            "preflight_B1_t2_context": chosen["B1_t2_context"],
        }
        if failures:
            results.append({
                **base,
                "status": "INTEGRITY_FAILURE",
                "failures": failures,
                "H2_executed": False,
            })
            continue

        # First authorized second-merge outcome access for this selected pair.
        h2a = execute_merge(repo, a1["commit"], t2)
        h2b = execute_merge(repo, b1["commit"], t2)
        separated = h2a["signature"] != h2b["signature"]
        results.append({
            **base,
            "status": "H2_SEPARATED" if separated else "H2_EQUIVALENT",
            "A1_commit": a1["commit"],
            "B1_commit": b1["commit"],
            "intermediate_tree": a1["tree"],
            "H2_executed": True,
            "H2_A": h2a,
            "H2_B": h2b,
            "H2_separated": separated,
        })

    summary = {
        "source_head": SOURCE_HEAD,
        "verified_preflight_pairs": pf["summary"]["pair_bank"],
        "verified_eligible_pairs": len(eligible_pairs),
        "verified_eligible_sequences": pf["summary"]["structurally_eligible_sequences_total"],
        "selected_pairs": len(selected_pairs),
        "H2_integrity_failures": sum(r["status"] == "INTEGRITY_FAILURE" for r in results),
        "H2_executions": sum(bool(r.get("H2_executed")) for r in results),
        "H2_separated": sum(r["status"] == "H2_SEPARATED" for r in results),
        "H2_equivalent": sum(r["status"] == "H2_EQUIVALENT" for r in results),
    }
    payload = {
        "protocol": "OACR_COMPOSE_G_V2_H2_EXECUTION_V1",
        "protocol_commit": PROTOCOL_COMMIT,
        "source": {
            "source_head": SOURCE_HEAD,
            "g5_json_sha256": file_sha(g5_path),
            "preflight_json_sha256": file_sha(pf_path),
            "preflight_verify_sha256": file_sha(pfv_path),
        },
        "registered_targets": targets,
        "selection_rule": {
            "pair_order": "lexicographic_(A,B)",
            "pair_cap": 16,
            "pair_sampling": "all_if_le_16_else_evenly_spaced",
            "sequence_order": "lexicographic_(t1,t2)",
            "sequence_per_pair": 1,
        },
        "summary": summary,
        "results": results,
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
