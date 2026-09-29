"""OACR-COMPOSE-G v2: outcome-blind structural preflight, no second merge."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "oacr_g5"))
sys.path.insert(0, str(HERE))

from run_same_contract_git_v1 import execute_merge, is_ancestor, merge_base, git  # noqa: E402
from run_depth2_git_v1 import deterministic_merge_commit  # noqa: E402

SOURCE_HEAD = "34f06850c16c7f7ac822b1adc71354f11b0f2ca3"


def context(repo: Path, head: str, target: str):
    return {
        "mergebase": merge_base(repo, head, target),
        "target_ancestor_head": is_ancestor(repo, target, head),
        "head_ancestor_target": is_ancestor(repo, head, target),
    }


def differs(a, b):
    return (
        a["mergebase"] != b["mergebase"]
        or a["target_ancestor_head"] != b["target_ancestor_head"]
        or a["head_ancestor_target"] != b["head_ancestor_target"]
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--g5_json", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    g5 = json.loads(Path(args.g5_json).read_text())
    if g5.get("protocol") != "OACR_G5_SAME_CONTRACT_GIT_V1" or g5.get("split") != "validation":
        raise RuntimeError("unexpected G5 artifact")
    if g5["source"]["source_head"] != SOURCE_HEAD:
        raise RuntimeError("G5 source head mismatch")
    if git(repo, "rev-parse", "HEAD").stdout.strip() != SOURCE_HEAD:
        raise RuntimeError("source checkout mismatch")

    targets = sorted(x["target"] for x in g5["action_selection"]["targets"])
    pair_bank = []
    for row in g5["pair_rows"]:
        if row["required_separation"]:
            continue
        if row["ancestry_vector_A"] != row["ancestry_vector_B"]:
            continue
        if not any(a != b for a, b in zip(row["mergebase_vector_A"], row["mergebase_vector_B"])):
            continue
        pair_bank.append(row)
    pair_bank.sort(key=lambda r: (r["A"], r["B"]))

    pair_results = []
    total_t1 = 0
    total_sequences = 0
    for row in pair_bank:
        a, b = row["A"], row["B"]
        materialized = []
        for t1 in targets:
            ma = execute_merge(repo, a, t1)
            mb = execute_merge(repo, b, t1)
            h1_ok = (
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
            if not h1_ok:
                continue

            a1 = deterministic_merge_commit(repo, a, t1)
            b1 = deterministic_merge_commit(repo, b, t1)
            if not a1["ok"] or not b1["ok"] or a1["tree"] != b1["tree"]:
                continue

            seqs = []
            for t2 in targets:
                if t2 == t1:
                    continue
                ca = context(repo, a1["commit"], t2)
                cb = context(repo, b1["commit"], t2)
                if ca["target_ancestor_head"] and cb["target_ancestor_head"]:
                    continue
                if differs(ca, cb):
                    seqs.append({
                        "t1": t1,
                        "t2": t2,
                        "intermediate_tree": a1["tree"],
                        "A1": a1["commit"],
                        "B1": b1["commit"],
                        "A1_t2_context": ca,
                        "B1_t2_context": cb,
                    })
            total_t1 += 1
            total_sequences += len(seqs)
            materialized.append({
                "t1": t1,
                "intermediate_tree": a1["tree"],
                "eligible_t2_sequences": seqs,
            })

        pair_results.append({
            "tree": row["tree"],
            "A": a,
            "B": b,
            "materializable_t1_count": len(materialized),
            "materialized_t1": materialized,
            "structurally_eligible_sequence_count": sum(
                len(x["eligible_t2_sequences"]) for x in materialized
            ),
        })

    pairs_with_t1 = sum(r["materializable_t1_count"] > 0 for r in pair_results)
    pairs_with_seq = sum(r["structurally_eligible_sequence_count"] > 0 for r in pair_results)
    summary = {
        "source_head": SOURCE_HEAD,
        "registered_targets": len(targets),
        "pair_bank": len(pair_bank),
        "pairs_with_materializable_t1": pairs_with_t1,
        "materializable_t1_total": total_t1,
        "pairs_with_structurally_eligible_sequence": pairs_with_seq,
        "structurally_eligible_sequences_total": total_sequences,
        "passes_H2_gate": pairs_with_seq >= 3 and total_sequences >= 8,
        "second_merge_outcomes_executed": 0,
    }
    payload = {
        "protocol": "OACR_COMPOSE_G_V2_STRUCTURAL_PREFLIGHT",
        "protocol_commit": "02d2b1143bf6254cbdb12ef773aff4a340f90ccf",
        "source": {
            "source_head": SOURCE_HEAD,
            "g5_artifact_sha256": "964a3ea6161705721cd3442ceb2c6401c490e69129158ce29fdf2f6151d2fdd7",
        },
        "registered_targets": targets,
        "summary": summary,
        "pairs": pair_results,
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
