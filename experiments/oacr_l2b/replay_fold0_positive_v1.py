"""Targeted independent native replay for the OACR-L2b fold-0 positive."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "r1_grace_scotus"))

import run_scotus_paired_closure as R  # noqa: E402

OFFICIAL_GRACE_COMMIT = "f674183f17a995d109e10ee6140d4c3e6d016115"
TARGET_PARAM_CONFIG = "bert.encoder.layer[10].output.dense.weight"
TARGET_PARAM_NAME = "bert.encoder.layer.10.output.dense.weight"
EXPECTED_SEED_IDS = [0, 14, 19, 22]
TARGET_ANCHOR_ID = 688
EXPECTED_FUTURE_IDS = [51, 29, 73]


def args():
    p = argparse.ArgumentParser()
    p.add_argument("--repo", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--device", default="cpu")
    return p.parse_args()


def load_cfg(repo: Path, device: str):
    from omegaconf import OmegaConf
    base = OmegaConf.load(repo / "grace/config/config.yaml")
    cfg = OmegaConf.create(OmegaConf.to_container(base, resolve=False))
    cfg.editor = OmegaConf.load(repo / "grace/config/editor/ft.yaml")
    cfg.experiment = OmegaConf.load(repo / "grace/config/experiment/scotus.yaml")
    cfg.model = OmegaConf.load(repo / "grace/config/model/scotus-bert.yaml")
    cfg.device = device
    cfg.wandb = False
    cfg.re_init_model = False
    cfg.dropout = 0.0
    model_dir = os.environ.get("R1_SCOTUS_MODEL_DIR")
    tokenizer_dir = os.environ.get("R1_SCOTUS_TOKENIZER_DIR")
    if model_dir:
        cfg.model.name = str(Path(model_dir).resolve())
    if tokenizer_dir:
        cfg.model.tokenizer_name = str(Path(tokenizer_dir).resolve())
    return cfg


def build_tokens(item, tokenizer, device):
    batch = {"text": [item["text"]], "labels": torch.tensor([item["labels"]])}
    return R.tensor_tokens(batch, tokenizer, device)


def get_target(editor):
    for n, p in editor.model.named_parameters():
        if n == TARGET_PARAM_NAME:
            return p
    raise RuntimeError("target parameter not found")


def snap(editor):
    return get_target(editor).detach().cpu().clone().contiguous()


def restore(editor, s):
    p = get_target(editor)
    with torch.no_grad():
        p.copy_(s.to(device=p.device, dtype=p.dtype))
    editor.model.zero_grad(set_to_none=True)


def tensor_hash(t):
    x = t.detach().cpu().contiguous()
    h = hashlib.sha256()
    h.update(str(tuple(x.shape)).encode())
    h.update(str(x.dtype).encode())
    h.update(x.numpy().tobytes())
    return h.hexdigest()


def current_hash(editor):
    return tensor_hash(snap(editor))


def native_write(editor, cfg, tokens):
    pre = R.acc(editor, tokens)
    if pre >= 1.0:
        return {
            "status": "ALREADY_SATISFIED_ZERO_WRITE",
            "target_realized": True,
            "pre_accuracy": pre,
            "post_accuracy": pre,
            "iterations": 0,
        }
    editor.edit(cfg, tokens, batch_history=[])
    post = R.acc(editor, tokens)
    return {
        "status": "EDIT_EXECUTED",
        "target_realized": bool(post >= 1.0),
        "pre_accuracy": pre,
        "post_accuracy": post,
        "iterations": int(len(getattr(editor, "losses", []))),
    }


def circular_indices(n, start):
    return list(range(start, n)) + list(range(0, start))


def label_balanced_by_rank(rows, n):
    groups = {}
    for r in rows:
        lab = int(r["item"]["labels"])
        groups.setdefault(lab, []).append(r)
    for lab in groups:
        groups[lab].sort(key=lambda x: (int(x["rank"]), int(x["idx"])))
    labels = sorted(groups)
    ptr = {lab: 0 for lab in labels}
    out = []
    while len(out) < n:
        progress = False
        for lab in labels:
            i = ptr[lab]
            if i < len(groups[lab]):
                out.append(groups[lab][i])
                ptr[lab] += 1
                progress = True
                if len(out) >= n:
                    break
        if not progress:
            break
    return out


def task_reads(editor, toks):
    strict = R.read_family_signatures(editor, toks)
    return [
        {
            "pred": int(x["pred"]),
            "target": int(x["target"]),
            "correct": bool(x["pred"] == x["target"]),
        }
        for x in strict
    ]


def reconstruct_once(repo: Path, device: str):
    from grace.editors.ft import Finetune
    from grace.models import Classifier

    cfg = load_cfg(repo, device)
    if str(cfg.model.inner_params[0]) != TARGET_PARAM_CONFIG:
        raise RuntimeError("unexpected target parameter config")
    if float(cfg.editor.edit_lr) != 1e-2 or int(cfg.n_iter) != 100:
        raise RuntimeError("unexpected FT budget")

    model = Classifier(cfg).to(device)
    editor = Finetune(cfg, model)
    dataset = R.load_scotus_edit_dataset()
    n = len(dataset)

    # Rebuild fold-0 base state exactly.
    obligations = []
    seed_ids = []
    last_seed_idx = None
    attempted = 0
    for rank, idx in enumerate(circular_indices(n, 0)):
        if attempted >= 1024 or len(seed_ids) >= 4:
            break
        item = dataset[idx]
        tok = build_tokens(item, editor.tokenizer, device)
        if R.acc(editor, tok) >= 1.0:
            continue
        attempted += 1
        before = snap(editor)
        w = native_write(editor, cfg, tok)
        old_ok = R.obligation_status(editor, obligations)["all_satisfied"]
        if w["target_realized"] and old_ok:
            obligations.append(tok)
            seed_ids.append(int(idx))
            last_seed_idx = int(idx)
        else:
            restore(editor, before)

    if seed_ids != EXPECTED_SEED_IDS:
        raise RuntimeError(f"seed reconstruction mismatch: {seed_ids}")
    if not R.obligation_status(editor, obligations)["all_satisfied"]:
        raise RuntimeError("seed obligations invalid")

    base = snap(editor)
    base_hash = tensor_hash(base)

    # Rebuild frozen 512-candidate bank.
    traversal = circular_indices(n, (last_seed_idx + 1) % n)
    bank = []
    for rank, idx in enumerate(traversal):
        if idx in seed_ids:
            continue
        item = dataset[idx]
        tok = build_tokens(item, editor.tokenizer, device)
        if R.acc(editor, tok) < 1.0:
            bank.append({
                "idx": int(idx),
                "rank": int(rank),
                "item": item,
                "tokens": tok,
            })
            if len(bank) >= 512:
                break

    future = label_balanced_by_rank(bank, 3)
    future_ids = [int(x["idx"]) for x in future]
    if future_ids != EXPECTED_FUTURE_IDS:
        raise RuntimeError(f"future-action reconstruction mismatch: {future_ids}")

    # Rebuild frozen sentinels: first 24 fold-order rows outside seeds and candidate bank.
    excluded = set(seed_ids) | {int(x["idx"]) for x in bank}
    sentinels = []
    for rank, idx in enumerate(circular_indices(n, 0)):
        if idx in excluded:
            continue
        item = dataset[idx]
        sentinels.append({
            "idx": int(idx),
            "rank": int(rank),
            "item": item,
            "tokens": build_tokens(item, editor.tokenizer, device),
        })
        if len(sentinels) >= 24:
            break
    if len(sentinels) != 24:
        raise RuntimeError("sentinel reconstruction failed")

    panel_tokens = list(obligations) + [x["tokens"] for x in future] + [x["tokens"] for x in sentinels]
    panel_manifest = (
        [{"kind": "seed", "dataset_index": i} for i in seed_ids]
        + [{"kind": "future", "dataset_index": int(x["idx"])} for x in future]
        + [{"kind": "sentinel", "dataset_index": int(x["idx"])} for x in sentinels]
    )

    restore(editor, base)
    base_h0 = task_reads(editor, panel_tokens)

    # Target anchor 688 from exact base.
    anchor_row = next((x for x in bank if int(x["idx"]) == TARGET_ANCHOR_ID), None)
    if anchor_row is None:
        raise RuntimeError("anchor 688 absent from frozen candidate bank")

    restore(editor, base)
    anchor_write = native_write(editor, cfg, anchor_row["tokens"])
    fixed_anchor = R.obligation_status(editor, obligations)
    anchor = snap(editor)
    anchor_hash = tensor_hash(anchor)
    anchor_h0 = task_reads(editor, panel_tokens)

    if not anchor_write["target_realized"]:
        raise RuntimeError("anchor 688 target not realized")
    if not fixed_anchor["all_satisfied"]:
        raise RuntimeError("anchor 688 violates protected obligations")
    if anchor_hash == base_hash:
        raise RuntimeError("anchor 688 does not change parameter state")
    if anchor_h0 != base_h0:
        raise RuntimeError("anchor 688 fails H0 C_task collision")

    by_future = {int(x["idx"]): x for x in future}
    branches = {}
    for aid in EXPECTED_FUTURE_IDS:
        action = by_future[aid]

        restore(editor, base)
        bw = native_write(editor, cfg, action["tokens"])
        bfix = R.obligation_status(editor, obligations)
        btask = task_reads(editor, panel_tokens)
        bhash = current_hash(editor)

        restore(editor, anchor)
        aw = native_write(editor, cfg, action["tokens"])
        afix = R.obligation_status(editor, obligations)
        atask = task_reads(editor, panel_tokens)
        ahash = current_hash(editor)

        meta_base = (bw["status"], bool(bw["target_realized"]), bool(bfix["all_satisfied"]))
        meta_anchor = (aw["status"], bool(aw["target_realized"]), bool(afix["all_satisfied"]))

        diffs = []
        for i, (ra, rb) in enumerate(zip(btask, atask)):
            if ra != rb:
                diffs.append({
                    "panel_index": i,
                    "panel_item": panel_manifest[i],
                    "base": ra,
                    "anchor": rb,
                })

        branches[str(aid)] = {
            "base_meta": {
                "status": bw["status"],
                "target_realized": bool(bw["target_realized"]),
                "fixed_all_satisfied": bool(bfix["all_satisfied"]),
                "fixed_n_failed": int(bfix["n_failed"]),
            },
            "anchor_meta": {
                "status": aw["status"],
                "target_realized": bool(aw["target_realized"]),
                "fixed_all_satisfied": bool(afix["all_satisfied"]),
                "fixed_n_failed": int(afix["n_failed"]),
            },
            "base_post_hash": bhash,
            "anchor_post_hash": ahash,
            "task_diff_count": len(diffs),
            "task_diffs": diffs,
            "h1_separates": bool(meta_base != meta_anchor or len(diffs) > 0),
        }

    return {
        "seed_ids": seed_ids,
        "future_ids": future_ids,
        "panel_manifest": panel_manifest,
        "base_hash": base_hash,
        "anchor_id": TARGET_ANCHOR_ID,
        "anchor_hash": anchor_hash,
        "h0_task_equal": base_h0 == anchor_h0,
        "base_h0": base_h0,
        "anchor_h0": anchor_h0,
        "branches": branches,
    }


def main():
    a = args()
    repo = Path(a.repo).resolve()
    out_path = Path(a.out).resolve()
    sys.path.insert(0, str(repo))
    os.chdir(repo)

    torch.manual_seed(0)
    np.random.seed(0)
    torch.use_deterministic_algorithms(True)

    r1 = reconstruct_once(repo, a.device)

    # Fresh second initialization.
    torch.manual_seed(0)
    np.random.seed(0)
    r2 = reconstruct_once(repo, a.device)

    deterministic_equal = (
        r1["seed_ids"] == r2["seed_ids"]
        and r1["future_ids"] == r2["future_ids"]
        and r1["panel_manifest"] == r2["panel_manifest"]
        and r1["base_hash"] == r2["base_hash"]
        and r1["anchor_hash"] == r2["anchor_hash"]
        and r1["base_h0"] == r2["base_h0"]
        and r1["anchor_h0"] == r2["anchor_h0"]
        and r1["branches"] == r2["branches"]
    )

    separating = [aid for aid, z in r1["branches"].items() if z["h1_separates"]]

    if not deterministic_equal:
        status = "FAIL_DETERMINISM"
    elif not r1["h0_task_equal"]:
        status = "FAIL_H0"
    elif not separating:
        status = "FAIL_H1"
    else:
        status = "PASS_POSITIVE_REPLAY"

    out = {
        "protocol": "OACR_L2B_FOLD0_TARGETED_NATIVE_REPLAY_V1",
        "official_grace_commit": OFFICIAL_GRACE_COMMIT,
        "status": status,
        "deterministic_two_reconstructions_equal": deterministic_equal,
        "replica_1": r1,
        "replica_2": r2,
        "separating_actions": separating,
    }

    p = out_path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(out, indent=2))
    print(json.dumps({
        "status": status,
        "deterministic_two_reconstructions_equal": deterministic_equal,
        "base_hash": r1["base_hash"],
        "anchor_hash": r1["anchor_hash"],
        "h0_task_equal": r1["h0_task_equal"],
        "separating_actions": separating,
        "branch_task_diff_counts": {
            aid: z["task_diff_count"] for aid, z in r1["branches"].items()
        },
    }, indent=2))

    if status != "PASS_POSITIVE_REPLAY":
        raise RuntimeError(status)


if __name__ == "__main__":
    main()
