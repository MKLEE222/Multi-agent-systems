"""Structural-only preflight for OACR Natural Learned Evidence v1.

This program must not import or invoke any model/editor package.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

CRITERIA = (
    "Relation_Specificity",
    "Logical_Generalization",
    "Subject_Aliasing",
    "Compositionality_I",
    "Compositionality_II",
    "Forgetfulness",
)

DEV_QUOTA = {"recent": 64, "random": 32, "popular": 32}
EVAL_QUOTA = {"recent": 256, "random": 128, "popular": 128}
SEED = "OACR_NATURAL_LEARNED_RIPPLE_V1"


def norm_prompt(x: str) -> str:
    return re.sub(r"\s+", " ", str(x).strip().lower())


def h(*parts: str) -> str:
    return hashlib.sha256("\x1f".join(parts).encode("utf-8")).hexdigest()


def prompts_from_tests(blocks, field):
    out = []
    if not isinstance(blocks, list):
        return out
    for block in blocks:
        if not isinstance(block, dict):
            continue
        rows = block.get(field, [])
        if not isinstance(rows, list):
            continue
        for q in rows:
            if isinstance(q, dict) and isinstance(q.get("prompt"), str):
                out.append(q["prompt"])
    return out


def inspect_entry(entry, subset):
    edit = entry.get("edit", {}) if isinstance(entry, dict) else {}
    required = ("prompt", "subject_id", "relation", "target_id")
    metadata_ok = all(isinstance(edit.get(k), str) and edit.get(k).strip() for k in required)
    criteria_present = all(k in entry for k in CRITERIA) if isinstance(entry, dict) else False

    nonempty = 0
    cond = []
    tests = []
    per_criterion = {}
    for criterion in CRITERIA:
        blocks = entry.get(criterion, []) if isinstance(entry, dict) else []
        if isinstance(blocks, list) and blocks:
            nonempty += 1
        c = prompts_from_tests(blocks, "condition_queries")
        t = prompts_from_tests(blocks, "test_queries")
        cond.extend(c)
        tests.extend(t)
        per_criterion[criterion] = {
            "blocks": len(blocks) if isinstance(blocks, list) else 0,
            "condition_prompts": len(c),
            "test_prompts": len(t),
        }

    cond_norm = {norm_prompt(x) for x in cond if norm_prompt(x)}
    test_norm = [norm_prompt(x) for x in tests if norm_prompt(x)]
    heldout = [x for x in test_norm if x not in cond_norm]

    identity = {
        "subset": subset,
        "prompt": edit.get("prompt"),
        "subject_id": edit.get("subject_id"),
        "relation": edit.get("relation"),
        "target_id": edit.get("target_id"),
    }
    canonical = json.dumps(identity, sort_keys=True, ensure_ascii=False)
    unit_id = h(SEED, canonical)

    eligible = bool(
        metadata_ok
        and criteria_present
        and nonempty >= 3
        and len(cond_norm) >= 1
        and len(set(heldout)) >= 4
    )

    return {
        "unit_id": unit_id,
        "subset": subset,
        "relation": edit.get("relation"),
        "subject_id": edit.get("subject_id"),
        "target_id": edit.get("target_id"),
        "criteria_present": criteria_present,
        "nonempty_criteria": nonempty,
        "condition_prompt_count": len(cond_norm),
        "test_prompt_count": len(set(test_norm)),
        "heldout_test_prompt_count": len(set(heldout)),
        "condition_test_exact_overlap_count": len(set(test_norm) & cond_norm),
        "eligible": eligible,
        "per_criterion": per_criterion,
    }


def relation_round_robin(rows, quota, salt):
    groups = defaultdict(list)
    for row in rows:
        groups[row["relation"]].append(row)
    for rel in groups:
        groups[rel].sort(key=lambda x: h(SEED, salt, str(rel), x["unit_id"]))
    rels = sorted(groups, key=lambda r: h(SEED, salt, str(r)))
    idx = {r: 0 for r in rels}
    selected = []
    while len(selected) < quota:
        progress = False
        for rel in rels:
            i = idx[rel]
            if i < len(groups[rel]):
                selected.append(groups[rel][i])
                idx[rel] = i + 1
                progress = True
                if len(selected) == quota:
                    break
        if not progress:
            break
    return selected


def split_subset(rows, subset):
    eligible = [r for r in rows if r["eligible"]]
    dev = relation_round_robin(eligible, DEV_QUOTA[subset], f"{subset}:dev")
    dev_ids = {r["unit_id"] for r in dev}
    remaining = [r for r in eligible if r["unit_id"] not in dev_ids]
    eva = relation_round_robin(remaining, EVAL_QUOTA[subset], f"{subset}:eval")
    return dev, eva


def file_sha256(path):
    d = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            d.update(chunk)
    return d.hexdigest()


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ripple_dir", required=True)
    ap.add_argument("--mquake_dir", required=True)
    ap.add_argument("--out_dir", required=True)
    a = ap.parse_args()

    ripple = Path(a.ripple_dir)
    mquake = Path(a.mquake_dir)
    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    all_rows = []
    source = {}
    for subset in ("recent", "random", "popular"):
        path = ripple / "data" / "benchmark" / f"{subset}.json"
        rows = load_json(path)
        if not isinstance(rows, list):
            raise SystemExit(f"{path} is not a list")
        inspected = [inspect_entry(x, subset) for x in rows]
        all_rows.extend(inspected)
        source[subset] = {
            "entries": len(rows),
            "sha256": file_sha256(path),
            "eligible": sum(int(x["eligible"]) for x in inspected),
            "relations": len({x["relation"] for x in inspected if x["relation"]}),
            "all_six_criteria": sum(int(x["criteria_present"]) for x in inspected),
            "condition_prompts": sum(x["condition_prompt_count"] for x in inspected),
            "test_prompts": sum(x["test_prompt_count"] for x in inspected),
            "heldout_test_prompts": sum(x["heldout_test_prompt_count"] for x in inspected),
            "exact_overlap_prompts": sum(x["condition_test_exact_overlap_count"] for x in inspected),
        }

    duplicate_unit_ids = len(all_rows) - len({r["unit_id"] for r in all_rows})

    dev, eva = [], []
    for subset in ("recent", "random", "popular"):
        rows = [r for r in all_rows if r["subset"] == subset]
        d, e = split_subset(rows, subset)
        dev.extend(d)
        eva.extend(e)

    dev_ids = {x["unit_id"] for x in dev}
    eval_ids = {x["unit_id"] for x in eva}
    overlap = dev_ids & eval_ids

    mquake_path = mquake / "datasets" / "MQuAKE-CF-3k-v2.json"
    mquake_rows = load_json(mquake_path)
    mquake_ok = isinstance(mquake_rows, list) and len(mquake_rows) >= 1000

    eligible_total = sum(int(x["eligible"]) for x in all_rows)
    dev_relations = len({x["relation"] for x in dev})
    eval_relations = len({x["relation"] for x in eva})

    quota_ok = (
        Counter(x["subset"] for x in dev) == Counter(DEV_QUOTA)
        and Counter(x["subset"] for x in eva) == Counter(EVAL_QUOTA)
    )

    gate_checks = {
        "eligible_at_least_1024": eligible_total >= 1024,
        "development_size_128": len(dev) == 128,
        "evaluation_size_512": len(eva) == 512,
        "development_evaluation_disjoint": len(overlap) == 0,
        "development_relation_diversity_at_least_16": dev_relations >= 16,
        "evaluation_relation_diversity_at_least_24": eval_relations >= 24,
        "frozen_subset_quotas_exact": quota_ok,
        "duplicate_unit_ids_zero": duplicate_unit_ids == 0,
        "mquake_secondary_present_parseable": mquake_ok,
    }
    passed = all(gate_checks.values())

    manifest = {
        "protocol": "OACR_NATURAL_LEARNED_RIPPLE_N0_V1",
        "ripple_commit": "54f3b88af4895a3aacb580ec63ce7ae857185040",
        "mquake_commit": "fb43dadc2d8cd19d08ce81c63d957b59deb3f3cd",
        "grace_commit": "f674183f17a995d109e10ee6140d4c3e6d016115",
        "source": source,
        "eligible_total": eligible_total,
        "development": {
            "size": len(dev),
            "relations": dev_relations,
            "subset_counts": dict(Counter(x["subset"] for x in dev)),
            "unit_ids": [x["unit_id"] for x in dev],
        },
        "evaluation": {
            "size": len(eva),
            "relations": eval_relations,
            "subset_counts": dict(Counter(x["subset"] for x in eva)),
            "unit_ids": [x["unit_id"] for x in eva],
        },
        "development_evaluation_overlap": sorted(overlap),
        "duplicate_unit_ids": duplicate_unit_ids,
        "mquake_secondary": {
            "path": "datasets/MQuAKE-CF-3k-v2.json",
            "entries": len(mquake_rows) if isinstance(mquake_rows, list) else None,
            "sha256": file_sha256(mquake_path),
        },
        "gate_checks": gate_checks,
        "status": "PASS" if passed else "FAIL",
        "authority_note": "Structural-only preflight. No model/editor outcome is generated or read.",
    }
    (out / "preflight.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")

    selected = {x["unit_id"] for x in dev + eva}
    ledger = [
        {
            k: row[k]
            for k in (
                "unit_id",
                "subset",
                "relation",
                "subject_id",
                "target_id",
                "nonempty_criteria",
                "condition_prompt_count",
                "test_prompt_count",
                "heldout_test_prompt_count",
                "condition_test_exact_overlap_count",
            )
        }
        for row in all_rows
        if row["unit_id"] in selected
    ]
    (out / "selected_units_structural.json").write_text(
        json.dumps(ledger, indent=2, sort_keys=True), encoding="utf-8"
    )

    print(json.dumps(manifest, indent=2, sort_keys=True))
    if not passed:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
