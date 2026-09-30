"""OACR-COMPOSE-L v1: learned recovery hysteresis with native Finetune writes."""
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

PROTOCOL = "OACR_COMPOSE_L_RECOVERY_HYSTERESIS_V1"
PROTOCOL_COMMIT = "e1d00a7bb57d30ef2d49eb667dbcd6fd7f0d1e8f"
OFFICIAL_GRACE_COMMIT = "f674183f17a995d109e10ee6140d4c3e6d016115"
TARGET_PARAM_CONFIG = "bert.encoder.layer[10].output.dense.weight"
TARGET_PARAM_NAME = "bert.encoder.layer.10.output.dense.weight"


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--repo", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--fold", type=int, required=True, choices=range(8))
    p.add_argument("--future_bank", type=int, default=512)
    p.add_argument("--anchor_bank", type=int, default=256)
    p.add_argument("--future_actions", type=int, default=3)
    p.add_argument("--sentinels", type=int, default=32)
    p.add_argument("--max_recovered", type=int, default=4)
    p.add_argument("--read_atol", type=float, default=1e-6)
    p.add_argument("--read_rtol", type=float, default=1e-5)
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


def target_param(editor):
    for n, p in editor.model.named_parameters():
        if n == TARGET_PARAM_NAME:
            return p
    raise RuntimeError("target parameter not found")


def snap(editor):
    return target_param(editor).detach().cpu().clone().contiguous()


def restore(editor, state):
    p = target_param(editor)
    with torch.no_grad():
        p.copy_(state.to(device=p.device, dtype=p.dtype))
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


def hash_non_target(editor):
    h = hashlib.sha256()
    for n, p in editor.model.named_parameters():
        if n == TARGET_PARAM_NAME:
            continue
        x = p.detach().cpu().contiguous()
        h.update(n.encode())
        h.update(str(tuple(x.shape)).encode())
        h.update(str(x.dtype).encode())
        h.update(x.numpy().tobytes())
    return h.hexdigest()


def circular(n, start):
    return list(range(start, n)) + list(range(0, start))


def tokens_for(item, tokenizer, device, label=None):
    y = int(item["labels"]) if label is None else int(label)
    batch = {"text": [item["text"]], "labels": torch.tensor([y])}
    return R.tensor_tokens(batch, tokenizer, device)


def write(editor, cfg, toks):
    pre = R.acc(editor, toks)
    if pre >= 1.0:
        return {
            "status": "ALREADY_SATISFIED_ZERO_WRITE",
            "target_realized": True,
            "pre_accuracy": pre,
            "post_accuracy": pre,
            "iterations": 0,
        }
    editor.edit(cfg, toks, batch_history=[])
    post = R.acc(editor, toks)
    return {
        "status": "EDIT_EXECUTED",
        "target_realized": bool(post >= 1.0),
        "pre_accuracy": pre,
        "post_accuracy": post,
        "iterations": int(len(getattr(editor, "losses", []))),
    }


def reads(editor, toks):
    strict = R.read_family_signatures(editor, toks)
    task = [
        {
            "pred": int(x["pred"]),
            "target": int(x["target"]),
            "correct": bool(x["pred"] == x["target"]),
        }
        for x in strict
    ]
    return {"task": task, "logit": strict}


def logit_equal(a, b, atol, rtol):
    return bool(R.compare_read_family(a, b, atol, rtol)["strict_logits_matched"])


def label_balanced(rows, n):
    groups = {}
    for row in rows:
        groups.setdefault(int(row["label"]), []).append(row)
    for lab in groups:
        groups[lab].sort(key=lambda x: (x["rank"], x["idx"]))
    ptr = {lab: 0 for lab in groups}
    out = []
    for _ in range(10000):
        if len(out) >= n:
            break
        progressed = False
        for lab in sorted(groups):
            i = ptr[lab]
            if i < len(groups[lab]):
                out.append(groups[lab][i])
                ptr[lab] += 1
                progressed = True
                if len(out) >= n:
                    break
        if not progressed:
            break
    return out


def branch(editor, cfg, start, action_tokens, panel):
    restore(editor, start)
    before = current_hash(editor)
    w = write(editor, cfg, action_tokens)
    post_reads = reads(editor, panel)
    post = snap(editor)
    after = tensor_hash(post)
    restore(editor, start)
    if current_hash(editor) != before:
        raise RuntimeError("branch restore mismatch")
    return {**w, "post_reads": post_reads, "post_state_hash": after}


def write_artifact(path, obj):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2))
    print(json.dumps({
        "fold": obj.get("fold"),
        "status": obj.get("status"),
        "summary": obj.get("summary"),
    }, indent=2))


def main():
    a = parse_args()
    repo = Path(a.repo).resolve()
    os.chdir(repo)
    sys.path.insert(0, str(repo))

    torch.manual_seed(0)
    np.random.seed(0)
    torch.use_deterministic_algorithms(True)

    from grace.editors.ft import Finetune
    from grace.models import Classifier

    cfg = load_cfg(repo, a.device)
    if str(cfg.model.inner_params[0]) != TARGET_PARAM_CONFIG:
        raise RuntimeError("unexpected target parameter config")
    if float(cfg.editor.edit_lr) != 1e-2 or int(cfg.n_iter) != 100:
        raise RuntimeError("unexpected Finetune budget")

    editor = Finetune(cfg, Classifier(cfg).to(a.device))
    dataset = R.load_scotus_edit_dataset()
    n = len(dataset)
    fold_start = int(math.floor(a.fold * n / 8.0))
    traversal = circular(n, fold_start)

    labels = sorted(set(int(dataset[i]["labels"]) for i in range(n)))
    if labels != list(range(len(labels))):
        raise RuntimeError(f"dataset labels are not contiguous 0..K-1: {labels}")
    K = len(labels)
    if K < 2:
        raise RuntimeError("need at least two labels")

    base = snap(editor)
    base_hash = tensor_hash(base)
    non_target_before = hash_non_target(editor)

    # Freeze future bank from base-misclassified examples.
    future_bank = []
    for rank, idx in enumerate(traversal):
        item = dataset[idx]
        tok = tokens_for(item, editor.tokenizer, a.device)
        if R.acc(editor, tok) < 1.0:
            future_bank.append({
                "idx": int(idx), "rank": int(rank), "label": int(item["labels"]),
                "tokens": tok,
            })
            if len(future_bank) >= a.future_bank:
                break
    future = label_balanced(future_bank, a.future_actions)
    if len(future) < a.future_actions:
        write_artifact(a.out, {
            "protocol": PROTOCOL, "protocol_commit": PROTOCOL_COMMIT,
            "official_grace_commit": OFFICIAL_GRACE_COMMIT,
            "fold": a.fold, "status": "UNDERPOWERED_FUTURE_BANK",
            "future_bank_size": len(future_bank), "future_outcomes_executed": False,
        })
        return
    future_ids = [int(x["idx"]) for x in future]

    # Freeze anchor bank from base-correct examples, disjoint from future actions.
    anchor_bank = []
    future_set = set(future_ids)
    for rank, idx in enumerate(traversal):
        if idx in future_set:
            continue
        item = dataset[idx]
        tok = tokens_for(item, editor.tokenizer, a.device)
        if R.acc(editor, tok) >= 1.0:
            anchor_bank.append({
                "idx": int(idx), "rank": int(rank), "label": int(item["labels"]),
            })
            if len(anchor_bank) >= a.anchor_bank:
                break

    if len(anchor_bank) < a.anchor_bank:
        write_artifact(a.out, {
            "protocol": PROTOCOL, "protocol_commit": PROTOCOL_COMMIT,
            "official_grace_commit": OFFICIAL_GRACE_COMMIT,
            "fold": a.fold, "status": "UNDERPOWERED_ANCHOR_BANK",
            "anchor_bank_size": len(anchor_bank), "future_ids": future_ids,
            "future_outcomes_executed": False,
        })
        return

    # Freeze common sentinels outside future and anchor banks.
    excluded = future_set | {int(x["idx"]) for x in anchor_bank}
    sentinels = []
    for rank, idx in enumerate(traversal):
        if idx in excluded:
            continue
        item = dataset[idx]
        sentinels.append({
            "idx": int(idx), "rank": int(rank),
            "tokens": tokens_for(item, editor.tokenizer, a.device),
        })
        if len(sentinels) >= a.sentinels:
            break
    if len(sentinels) < a.sentinels:
        raise RuntimeError("could not freeze sentinel panel")

    common_panel = [x["tokens"] for x in future] + [x["tokens"] for x in sentinels]
    common_manifest = (
        [{"kind": "future", "dataset_index": int(x["idx"])} for x in future]
        + [{"kind": "sentinel", "dataset_index": int(x["idx"])} for x in sentinels]
    )

    restore(editor, base)
    read_hash_before = current_hash(editor)
    base_common_reads = reads(editor, common_panel)
    if current_hash(editor) != read_hash_before:
        raise RuntimeError("base common READ mutated state")

    attempts = []
    recovered = []

    for anchor in anchor_bank:
        if len(recovered) >= a.max_recovered:
            break
        idx = int(anchor["idx"])
        item = dataset[idx]
        y = int(item["labels"])
        ycf = (y + 1) % K
        anchor_true = tokens_for(item, editor.tokenizer, a.device, y)
        anchor_cf = tokens_for(item, editor.tokenizer, a.device, ycf)
        pair_panel = common_panel + [anchor_true]
        pair_manifest = common_manifest + [{"kind": "anchor", "dataset_index": idx}]

        restore(editor, base)
        base_pair_reads = reads(editor, pair_panel)

        fw = write(editor, cfg, anchor_cf)
        forward_hash = current_hash(editor)
        if not fw["target_realized"] or forward_hash == base_hash:
            attempts.append({
                "anchor_id": idx, "true_label": y, "counterfactual_label": ycf,
                "forward": fw, "forward_hash": forward_hash,
                "accepted": False, "reason": "FORWARD_FAILED",
            })
            continue

        cw = write(editor, cfg, anchor_true)
        recovered_state = snap(editor)
        recovered_hash = tensor_hash(recovered_state)
        if not cw["target_realized"]:
            attempts.append({
                "anchor_id": idx, "true_label": y, "counterfactual_label": ycf,
                "forward": fw, "counter": cw,
                "forward_hash": forward_hash, "recovered_hash": recovered_hash,
                "accepted": False, "reason": "COUNTER_TARGET_FAILED",
            })
            continue

        r1 = reads(editor, pair_panel)
        r2 = reads(editor, pair_panel)
        task_match = r1["task"] == base_pair_reads["task"] and r2["task"] == r1["task"]
        logit_match = logit_equal(r1["logit"], base_pair_reads["logit"], a.read_atol, a.read_rtol)
        finite = bool(torch.isfinite(recovered_state).all().item())
        hash_diff = recovered_hash != base_hash

        reason = "ACCEPTED"
        if not task_match:
            reason = "CURRENT_TASK_NOT_RESTORED"
        elif not hash_diff:
            reason = "PARAMETER_STATE_FULLY_RESTORED"
        elif not finite:
            reason = "NONFINITE_PARAMETER"

        attempt = {
            "anchor_id": idx,
            "true_label": y,
            "counterfactual_label": ycf,
            "forward": fw,
            "counter": cw,
            "forward_hash": forward_hash,
            "recovered_hash": recovered_hash,
            "current_task_restored": bool(task_match),
            "current_logit_restored": bool(logit_match),
            "parameter_differs_from_base": bool(hash_diff),
            "finite": finite,
            "accepted": reason == "ACCEPTED",
            "reason": reason,
        }
        attempts.append(attempt)

        if reason == "ACCEPTED":
            recovered.append({
                "state_id": f"recovered:{idx}",
                "anchor_id": idx,
                "snapshot": recovered_state,
                "parameter_hash": recovered_hash,
                "base_pair_reads": base_pair_reads,
                "root_reads": r1,
                "panel_manifest": pair_manifest,
                "anchor_tokens": anchor_true,
            })

    # Freeze state bank before any future branch is executed.
    future_outcomes_executed = bool(recovered)
    pair_results = []
    total_separations = 0
    selective_pairs = 0

    if recovered:
        by_future = {int(x["idx"]): x for x in future}
        for state in recovered:
            panel = common_panel + [state["anchor_tokens"]]
            per_action = []
            sep_count = 0
            for aid in future_ids:
                action = by_future[aid]
                base_branch = branch(editor, cfg, base, action["tokens"], panel)
                rec_branch = branch(editor, cfg, state["snapshot"], action["tokens"], panel)
                meta_base = (base_branch["status"], bool(base_branch["target_realized"]))
                meta_rec = (rec_branch["status"], bool(rec_branch["target_realized"]))
                sep = (
                    meta_base != meta_rec
                    or base_branch["post_reads"]["task"] != rec_branch["post_reads"]["task"]
                )
                sep_count += int(sep)
                total_separations += int(sep)
                diffs = []
                for i, (x, y) in enumerate(zip(
                    base_branch["post_reads"]["task"], rec_branch["post_reads"]["task"]
                )):
                    if x != y:
                        diffs.append({
                            "panel_index": i,
                            "panel_item": state["panel_manifest"][i],
                            "base": x,
                            "recovered": y,
                        })
                per_action.append({
                    "action_id": aid,
                    "separates": bool(sep),
                    "base_meta": {"status": base_branch["status"], "target_realized": bool(base_branch["target_realized"])},
                    "recovered_meta": {"status": rec_branch["status"], "target_realized": bool(rec_branch["target_realized"])},
                    "base_post_hash": base_branch["post_state_hash"],
                    "recovered_post_hash": rec_branch["post_state_hash"],
                    "task_differences": diffs,
                    "logit_equal": logit_equal(
                        base_branch["post_reads"]["logit"],
                        rec_branch["post_reads"]["logit"],
                        a.read_atol, a.read_rtol,
                    ),
                })
            selective = 0 < sep_count < len(future_ids)
            selective_pairs += int(selective)
            pair_results.append({
                "state_id": state["state_id"],
                "anchor_id": state["anchor_id"],
                "parameter_hash": state["parameter_hash"],
                "root_task_equal": state["root_reads"]["task"] == state["base_pair_reads"]["task"],
                "root_logit_equal": logit_equal(
                    state["root_reads"]["logit"], state["base_pair_reads"]["logit"],
                    a.read_atol, a.read_rtol,
                ),
                "future_separations": sep_count,
                "selective_future_response": selective,
                "actions": per_action,
            })

    non_target_after = hash_non_target(editor)
    non_target_unchanged = non_target_before == non_target_after
    if not non_target_unchanged:
        raise RuntimeError("non-target parameters changed")

    status = "COMPLETE" if recovered else "RECOVERY_STATE_UNDERPOWERED"
    obj = {
        "protocol": PROTOCOL,
        "protocol_commit": PROTOCOL_COMMIT,
        "official_grace_commit": OFFICIAL_GRACE_COMMIT,
        "fold": a.fold,
        "dataset_length": n,
        "fold_start": fold_start,
        "status": status,
        "base_parameter_hash": base_hash,
        "label_count": K,
        "future_ids": future_ids,
        "anchor_bank_ids": [int(x["idx"]) for x in anchor_bank],
        "sentinel_ids": [int(x["idx"]) for x in sentinels],
        "attempts": attempts,
        "recovered_states": [
            {
                "state_id": s["state_id"],
                "anchor_id": s["anchor_id"],
                "parameter_hash": s["parameter_hash"],
                "root_task_equal": s["root_reads"]["task"] == s["base_pair_reads"]["task"],
                "root_logit_equal": logit_equal(
                    s["root_reads"]["logit"], s["base_pair_reads"]["logit"],
                    a.read_atol, a.read_rtol,
                ),
                "panel_manifest": s["panel_manifest"],
            }
            for s in recovered
        ],
        "future_results": pair_results,
        "future_outcomes_executed": future_outcomes_executed,
        "non_target_unchanged": non_target_unchanged,
        "summary": {
            "anchor_candidates_attempted": len(attempts),
            "accepted_recovered_states": len(recovered),
            "current_logit_restored_states": sum(int(x["current_logit_restored"]) for x in attempts if x.get("accepted")),
            "future_branches": len(recovered) * len(future_ids),
            "future_separations": total_separations,
            "pairs_with_future_separation": sum(int(x["future_separations"] > 0) for x in pair_results),
            "selective_pairs": selective_pairs,
        },
    }
    write_artifact(a.out, obj)


if __name__ == "__main__":
    main()
