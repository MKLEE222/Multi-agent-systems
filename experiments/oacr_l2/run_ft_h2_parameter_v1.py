"""OACR-L2 v1: H2 audit of official parameter-level Finetune on SCOTUS/BERT."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import sys
from contextlib import contextmanager
from itertools import combinations
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "r1_grace_scotus"))
sys.path.insert(0, str(HERE.parent / "common"))

import run_scotus_paired_closure as R  # noqa: E402
from operational_partition import (  # noqa: E402
    directional_information_gap,
    partition_from_signatures,
    refinement_relation,
)

PROTOCOL = "OACR_L2_PARAMETER_FT_H2_V1"
PROTOCOL_COMMIT = "addf75ddf9f9e963b65b92428a60dbb84965c72f"
OFFICIAL_GRACE_COMMIT = "f674183f17a995d109e10ee6140d4c3e6d016115"
TARGET_PARAM_CONFIG = "bert.encoder.layer[10].output.dense.weight"
TARGET_PARAM_NAME = "bert.encoder.layer.10.output.dense.weight"


def args():
    p = argparse.ArgumentParser()
    p.add_argument("--repo", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--seed", type=int, required=True)
    p.add_argument("--seed_edits", type=int, default=4)
    p.add_argument("--seed_scan_limit", type=int, default=1024)
    p.add_argument("--candidate_bank", type=int, default=512)
    p.add_argument("--anchor_candidates", type=int, default=24)
    p.add_argument("--future_actions", type=int, default=3)
    p.add_argument("--sentinel_reads", type=int, default=24)
    p.add_argument("--max_states", type=int, default=6)
    p.add_argument("--read_atol", type=float, default=1e-6)
    p.add_argument("--read_rtol", type=float, default=1e-5)
    p.add_argument("--device", default="cpu")
    return p.parse_args()


def load_ft_config(repo: Path, device: str):
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


def get_target_param(editor):
    found = None
    for n, p in editor.model.named_parameters():
        if n == TARGET_PARAM_NAME:
            found = p
            break
    if found is None:
        raise RuntimeError(f"target parameter not found: {TARGET_PARAM_NAME}")
    return found


def tensor_snapshot(editor):
    return get_target_param(editor).detach().cpu().clone().contiguous()


def restore_tensor(editor, snap):
    p = get_target_param(editor)
    with torch.no_grad():
        p.copy_(snap.to(device=p.device, dtype=p.dtype))
    editor.model.zero_grad(set_to_none=True)


def tensor_hash(t):
    x = t.detach().cpu().contiguous()
    h = hashlib.sha256()
    h.update(str(tuple(x.shape)).encode())
    h.update(str(x.dtype).encode())
    h.update(x.numpy().tobytes())
    return h.hexdigest()


def current_tensor_hash(editor):
    return tensor_hash(tensor_snapshot(editor))


def hash_non_target_params(editor):
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


def delta_stats(snap, base):
    d = (snap.float() - base.float()).view(-1)
    return {
        "l2": float(torch.linalg.vector_norm(d).item()),
        "l2_hex": float(torch.linalg.vector_norm(d).item()).hex(),
        "linf": float(torch.max(torch.abs(d)).item()) if d.numel() else 0.0,
    }


def task_read_family(editor, toks):
    out = []
    for t in toks:
        sig = R.read_signature(editor, t)
        out.append({
            "pred": int(sig["pred"]),
            "target": int(sig["target"]),
            "correct": bool(sig["pred"] == sig["target"]),
        })
    return out


def full_read_bundle(editor, toks):
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


def task_equal(a, b):
    return a == b


def logit_equal(a, b, atol, rtol):
    return bool(R.compare_read_family(a, b, atol, rtol)["strict_logits_matched"])


def canonical_json(x):
    return json.dumps(x, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def native_meta(x):
    return (
        x["status"],
        bool(x["target_realized"]),
        bool(x["fixed_all_satisfied"]),
    )


def build_tokens(item, tokenizer, device):
    batch = {"text": [item["text"]], "labels": torch.tensor([item["labels"]])}
    return R.tensor_tokens(batch, tokenizer, device)


def native_write(editor, cfg, tokens):
    pre = R.acc(editor, tokens)
    if pre >= 1.0:
        return {
            "status": "ALREADY_SATISFIED_ZERO_WRITE",
            "iterations": 0,
            "pre_accuracy": pre,
            "post_accuracy": pre,
            "target_realized": True,
        }
    editor.edit(cfg, tokens, batch_history=[])
    post = R.acc(editor, tokens)
    return {
        "status": "EDIT_EXECUTED",
        "iterations": int(len(getattr(editor, "losses", []))),
        "pre_accuracy": pre,
        "post_accuracy": post,
        "target_realized": bool(post >= 1.0),
    }


def build_seed_state(editor, cfg, dataset, tokenizer, device, target_n, scan_limit):
    accepted = []
    obligations = []
    scanned = 0
    max_idx = -1
    for idx in range(len(dataset)):
        if scanned >= scan_limit or len(accepted) >= target_n:
            break
        item = dataset[idx]
        tokens = build_tokens(item, tokenizer, device)
        if R.acc(editor, tokens) >= 1.0:
            continue
        scanned += 1
        before = tensor_snapshot(editor)
        w = native_write(editor, cfg, tokens)
        old_ok = R.obligation_status(editor, obligations)["all_satisfied"]
        if w["target_realized"] and old_ok:
            obligations.append(tokens)
            accepted.append({
                "idx": idx,
                "item": item,
                "tokens": tokens,
                "write": w,
                "post_state_hash": current_tensor_hash(editor),
            })
            max_idx = max(max_idx, idx)
        else:
            restore_tensor(editor, before)
    if len(accepted) < target_n:
        raise RuntimeError(
            f"Could only build {len(accepted)}/{target_n} contract-preserving FT seed edits "
            f"within scan limit {scan_limit}"
        )
    final = R.obligation_status(editor, obligations)
    if not final["all_satisfied"]:
        raise RuntimeError("Seed contract invalid after FT construction")
    return accepted, obligations, max_idx, final


def collect_errors(editor, dataset, tokenizer, device, start_idx, limit):
    rows = []
    for idx in range(start_idx, len(dataset)):
        item = dataset[idx]
        tokens = build_tokens(item, tokenizer, device)
        if R.acc(editor, tokens) < 1.0:
            rows.append({"idx": idx, "item": item, "tokens": tokens})
            if len(rows) >= limit:
                break
    return rows


def label_balanced(rows, n, excluded=None):
    excluded = set(excluded or [])
    groups: Dict[int, List[dict]] = {}
    for r in rows:
        if int(r["idx"]) in excluded:
            continue
        lab = int(r["item"]["labels"])
        groups.setdefault(lab, []).append(r)
    for lab in groups:
        groups[lab].sort(key=lambda x: int(x["idx"]))
    labels = sorted(groups)
    ptr = {lab: 0 for lab in labels}
    out = []
    while len(out) < n:
        progressed = False
        for lab in labels:
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


def sentinel_rows(dataset, tokenizer, device, excluded, n):
    rows = []
    for idx in range(len(dataset)):
        if idx in excluded:
            continue
        item = dataset[idx]
        rows.append({
            "idx": idx,
            "item": item,
            "tokens": build_tokens(item, tokenizer, device),
        })
        if len(rows) >= max(n * 8, n):
            break
    return label_balanced(rows, n)


def apply_action(
    editor,
    cfg,
    start_snap,
    action,
    protected_tokens,
    panel_tokens,
):
    restore_tensor(editor, start_snap)
    expected = tensor_hash(start_snap)
    if current_tensor_hash(editor) != expected:
        raise RuntimeError("target-tensor restore mismatch before branch")

    w = native_write(editor, cfg, action["tokens"])
    fixed = R.obligation_status(editor, protected_tokens)
    reads = full_read_bundle(editor, panel_tokens)
    post = tensor_snapshot(editor)
    post_hash = tensor_hash(post)

    restore_tensor(editor, start_snap)
    if current_tensor_hash(editor) != expected:
        raise RuntimeError("target-tensor restore mismatch after branch")

    serial = {
        **w,
        "fixed_all_satisfied": bool(fixed["all_satisfied"]),
        "fixed_n_failed": int(fixed["n_failed"]),
        "post_reads": reads,
        "post_state_hash": post_hash,
    }
    return serial, post


def pair_relation_task(a, b, action_ids):
    h0 = task_equal(a["root_reads"]["task"], b["root_reads"]["task"])
    h1 = h0 and all(
        native_meta(a["tree"]["h1"][aid]) == native_meta(b["tree"]["h1"][aid])
        and task_equal(
            a["tree"]["h1"][aid]["post_reads"]["task"],
            b["tree"]["h1"][aid]["post_reads"]["task"],
        )
        for aid in action_ids
    )
    h2 = h1 and all(
        native_meta(a["tree"]["h2"][f"{aid}>{bid}"])
        == native_meta(b["tree"]["h2"][f"{aid}>{bid}"])
        and task_equal(
            a["tree"]["h2"][f"{aid}>{bid}"]["post_reads"]["task"],
            b["tree"]["h2"][f"{aid}>{bid}"]["post_reads"]["task"],
        )
        for aid in action_ids
        for bid in action_ids
    )
    return h0, h1, h2


def pair_relation_logit(a, b, action_ids, atol, rtol):
    h0 = logit_equal(
        a["root_reads"]["logit"], b["root_reads"]["logit"], atol, rtol
    )
    h1 = h0 and all(
        native_meta(a["tree"]["h1"][aid]) == native_meta(b["tree"]["h1"][aid])
        and logit_equal(
            a["tree"]["h1"][aid]["post_reads"]["logit"],
            b["tree"]["h1"][aid]["post_reads"]["logit"],
            atol,
            rtol,
        )
        for aid in action_ids
    )
    h2 = h1 and all(
        native_meta(a["tree"]["h2"][f"{aid}>{bid}"])
        == native_meta(b["tree"]["h2"][f"{aid}>{bid}"])
        and logit_equal(
            a["tree"]["h2"][f"{aid}>{bid}"]["post_reads"]["logit"],
            b["tree"]["h2"][f"{aid}>{bid}"]["post_reads"]["logit"],
            atol,
            rtol,
        )
        for aid in action_ids
        for bid in action_ids
    )
    return h0, h1, h2


def transitivity_audit(state_ids, eq):
    violations = []
    for a in state_ids:
        for b in state_ids:
            for c in state_ids:
                if eq.get((a, b), False) and eq.get((b, c), False) and not eq.get((a, c), False):
                    violations.append([a, b, c])
    return violations


def partition_from_exact_signatures(states, fn):
    ids = [s["state_id"] for s in states]
    return partition_from_signatures(ids, lambda sid: fn(next(x for x in states if x["state_id"] == sid)))


def operational_task_signature(state, action_ids):
    return {
        "h0": state["root_reads"]["task"],
        "h1": {
            aid: {
                "meta": native_meta(state["tree"]["h1"][aid]),
                "reads": state["tree"]["h1"][aid]["post_reads"]["task"],
            }
            for aid in action_ids
        },
        "h2": {
            f"{aid}>{bid}": {
                "meta": native_meta(state["tree"]["h2"][f"{aid}>{bid}"]),
                "reads": state["tree"]["h2"][f"{aid}>{bid}"]["post_reads"]["task"],
            }
            for aid in action_ids
            for bid in action_ids
        },
    }


def representation_audit(states, op_partition):
    ids = [s["state_id"] for s in states]
    reps = {
        "P0_task_read": partition_from_signatures(
            ids, lambda sid: canonical_json(next(x for x in states if x["state_id"] == sid)["root_reads"]["task"])
        ),
        "Pfull_target_parameter_hash": partition_from_signatures(
            ids, lambda sid: next(x for x in states if x["state_id"] == sid)["parameter_hash"]
        ),
        "Pdelta_norm": partition_from_signatures(
            ids, lambda sid: next(x for x in states if x["state_id"] == sid)["delta_stats"]["l2_hex"]
        ),
    }
    out = {}
    for name, rep in reps.items():
        info = directional_information_gap(rep, op_partition)
        pair = refinement_relation(rep, op_partition)
        out[name] = {
            **info,
            "representation_blocks": len(rep),
            "under_refinement_count": pair["under_refinement_count"],
            "over_refinement_count": pair["over_refinement_count"],
        }
    return out


def duplicate_h1(editor, cfg, snap, action, protected, panel):
    a, _ = apply_action(editor, cfg, snap, action, protected, panel)
    b, _ = apply_action(editor, cfg, snap, action, protected, panel)
    return (
        native_meta(a) == native_meta(b)
        and a["post_reads"]["task"] == b["post_reads"]["task"]
        and logit_equal(a["post_reads"]["logit"], b["post_reads"]["logit"], 0.0, 0.0)
        and a["post_state_hash"] == b["post_state_hash"]
    )


def duplicate_h2(editor, cfg, snap, a1, a2, protected, panel):
    x1, xs = apply_action(editor, cfg, snap, a1, protected, panel)
    x2, _ = apply_action(editor, cfg, xs, a2, protected, panel)
    y1, ys = apply_action(editor, cfg, snap, a1, protected, panel)
    y2, _ = apply_action(editor, cfg, ys, a2, protected, panel)
    return (
        native_meta(x1) == native_meta(y1)
        and native_meta(x2) == native_meta(y2)
        and x1["post_reads"]["task"] == y1["post_reads"]["task"]
        and x2["post_reads"]["task"] == y2["post_reads"]["task"]
        and logit_equal(x1["post_reads"]["logit"], y1["post_reads"]["logit"], 0.0, 0.0)
        and logit_equal(x2["post_reads"]["logit"], y2["post_reads"]["logit"], 0.0, 0.0)
        and x1["post_state_hash"] == y1["post_state_hash"]
        and x2["post_state_hash"] == y2["post_state_hash"]
    )


def write_artifact(path, obj):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2))
    print(json.dumps({
        "protocol": obj.get("protocol"),
        "seed": obj.get("seed"),
        "status": obj.get("status"),
        "summary": obj.get("summary"),
    }, indent=2))


def main():
    a = args()
    repo = Path(a.repo).resolve()
    sys.path.insert(0, str(repo))
    os.chdir(repo)

    random.seed(a.seed)
    np.random.seed(a.seed)
    torch.manual_seed(a.seed)
    torch.use_deterministic_algorithms(True)

    from grace.editors.ft import Finetune
    from grace.models import Classifier

    cfg = load_ft_config(repo, a.device)
    if str(cfg.model.inner_params[0]) != TARGET_PARAM_CONFIG:
        raise RuntimeError(f"unexpected inner parameter: {cfg.model.inner_params[0]}")
    if float(cfg.editor.edit_lr) != 1e-2 or int(cfg.n_iter) != 100:
        raise RuntimeError("official FT budget mismatch")

    model = Classifier(cfg).to(a.device)
    editor = Finetune(cfg, model)
    dataset = R.load_scotus_edit_dataset()

    non_target_before = hash_non_target_params(editor)

    try:
        seed_rows, protected_tokens, max_idx, seed_contract = build_seed_state(
            editor,
            cfg,
            dataset,
            editor.tokenizer,
            a.device,
            a.seed_edits,
            a.seed_scan_limit,
        )
    except RuntimeError as exc:
        msg = str(exc)
        if not msg.startswith("Could only build ") and msg != "Seed contract invalid after FT construction":
            raise
        write_artifact(a.out, {
            "protocol": PROTOCOL,
            "protocol_commit": PROTOCOL_COMMIT,
            "official_grace_commit": OFFICIAL_GRACE_COMMIT,
            "seed": a.seed,
            "status": "SEED_CONSTRUCTION_FAILURE",
            "failure_message": msg,
            "future_outcomes_executed": False,
        })
        return

    base = tensor_snapshot(editor)
    base_hash = tensor_hash(base)

    bank = collect_errors(
        editor, dataset, editor.tokenizer, a.device, max_idx + 1, a.candidate_bank
    )
    anchors = label_balanced(bank, a.anchor_candidates)
    if len(anchors) < a.anchor_candidates:
        write_artifact(a.out, {
            "protocol": PROTOCOL,
            "protocol_commit": PROTOCOL_COMMIT,
            "official_grace_commit": OFFICIAL_GRACE_COMMIT,
            "seed": a.seed,
            "status": "UNDERPOWERED_ANCHOR_CANDIDATES",
            "anchor_candidates_found": len(anchors),
            "future_outcomes_executed": False,
        })
        return

    anchor_ids = [int(x["idx"]) for x in anchors]
    future = label_balanced(bank, a.future_actions, excluded=anchor_ids)
    if len(future) < a.future_actions:
        write_artifact(a.out, {
            "protocol": PROTOCOL,
            "protocol_commit": PROTOCOL_COMMIT,
            "official_grace_commit": OFFICIAL_GRACE_COMMIT,
            "seed": a.seed,
            "status": "UNDERPOWERED_FUTURE_ACTIONS",
            "anchor_ids": anchor_ids,
            "future_actions_found": len(future),
            "future_outcomes_executed": False,
        })
        return

    future_ids = [int(x["idx"]) for x in future]
    used_ids = set([int(x["idx"]) for x in seed_rows] + anchor_ids + future_ids)
    sent = sentinel_rows(
        dataset, editor.tokenizer, a.device, used_ids, a.sentinel_reads
    )
    if len(sent) < a.sentinel_reads:
        raise RuntimeError("could not freeze registered sentinel panel")

    panel_tokens = (
        list(protected_tokens)
        + [x["tokens"] for x in future]
        + [x["tokens"] for x in sent]
    )
    panel_manifest = (
        [{"kind": "seed", "dataset_index": int(x["idx"])} for x in seed_rows]
        + [{"kind": "future", "dataset_index": int(x["idx"])} for x in future]
        + [{"kind": "sentinel", "dataset_index": int(x["idx"])} for x in sent]
    )

    restore_tensor(editor, base)
    read_before = current_tensor_hash(editor)
    base_reads = full_read_bundle(editor, panel_tokens)
    read_after = current_tensor_hash(editor)
    if read_before != read_after:
        raise RuntimeError("base READ mutated parameter state")

    runtime = {
        "base": {
            "state_id": "base",
            "snapshot": base,
            "root_reads": base_reads,
            "parameter_hash": base_hash,
            "delta_stats": delta_stats(base, base),
            "anchor_id": None,
        }
    }
    attempts = []

    for anchor in anchors:
        restore_tensor(editor, base)
        before_hash = current_tensor_hash(editor)
        w = native_write(editor, cfg, anchor["tokens"])
        fixed = R.obligation_status(editor, protected_tokens)
        post = tensor_snapshot(editor)
        post_hash = tensor_hash(post)

        root_reads = None
        task_base_match = False
        task_all_retained = False
        logit_base_match = False
        if w["target_realized"] and fixed["all_satisfied"]:
            root_reads = full_read_bundle(editor, panel_tokens)
            task_base_match = task_equal(root_reads["task"], base_reads["task"])
            task_all_retained = task_base_match and all(
                task_equal(root_reads["task"], s["root_reads"]["task"])
                for s in runtime.values()
            )
            logit_base_match = logit_equal(
                root_reads["logit"], base_reads["logit"], a.read_atol, a.read_rtol
            )

        capacity = len(runtime) < a.max_states
        retained = bool(
            capacity
            and w["target_realized"]
            and fixed["all_satisfied"]
            and task_all_retained
            and post_hash != base_hash
        )

        sid = f"anchor:{int(anchor['idx'])}"
        attempts.append({
            "anchor_id": int(anchor["idx"]),
            "target_label": int(anchor["item"]["labels"]),
            "write": w,
            "protected_all_satisfied": bool(fixed["all_satisfied"]),
            "task_base_match": bool(task_base_match),
            "task_all_retained_match": bool(task_all_retained),
            "logit_base_match": bool(logit_base_match),
            "post_state_hash": post_hash,
            "capacity_available": bool(capacity),
            "retained": retained,
        })

        if retained:
            runtime[sid] = {
                "state_id": sid,
                "snapshot": post,
                "root_reads": root_reads,
                "parameter_hash": post_hash,
                "delta_stats": delta_stats(post, base),
                "anchor_id": int(anchor["idx"]),
            }

        restore_tensor(editor, base)
        if current_tensor_hash(editor) != before_hash:
            raise RuntimeError("anchor restore mismatch")

    if len(runtime) < 2:
        write_artifact(a.out, {
            "protocol": PROTOCOL,
            "protocol_commit": PROTOCOL_COMMIT,
            "official_grace_commit": OFFICIAL_GRACE_COMMIT,
            "seed": a.seed,
            "status": "UNDERPOWERED_STATE_CONSTRUCTION",
            "seed_edit_indices": [int(x["idx"]) for x in seed_rows],
            "anchor_ids": anchor_ids,
            "future_ids": future_ids,
            "anchor_attempts": attempts,
            "states": len(runtime),
            "future_outcomes_executed": False,
        })
        return

    action_map = {str(int(x["idx"])): x for x in future}
    action_ids = list(action_map)

    for sid, st in runtime.items():
        h1 = {}
        h1_snaps = {}
        for aid in action_ids:
            meta, snap = apply_action(
                editor,
                cfg,
                st["snapshot"],
                action_map[aid],
                protected_tokens,
                panel_tokens,
            )
            h1[aid] = meta
            h1_snaps[aid] = snap

        h2 = {}
        for aid in action_ids:
            for bid in action_ids:
                meta, _ = apply_action(
                    editor,
                    cfg,
                    h1_snaps[aid],
                    action_map[bid],
                    protected_tokens,
                    panel_tokens,
                )
                h2[f"{aid}>{bid}"] = meta

        st["tree"] = {"h1": h1, "h2": h2}

    states = list(runtime.values())
    state_ids = [s["state_id"] for s in states]

    pairs = []
    eq_task = {0: {}, 1: {}, 2: {}}
    eq_logit = {0: {}, 1: {}, 2: {}}
    for sid in state_ids:
        for h in (0, 1, 2):
            eq_task[h][(sid, sid)] = True
            eq_logit[h][(sid, sid)] = True

    for x, y in combinations(states, 2):
        t0, t1, t2 = pair_relation_task(x, y, action_ids)
        l0, l1, l2 = pair_relation_logit(
            x, y, action_ids, a.read_atol, a.read_rtol
        )
        for h, v in enumerate((t0, t1, t2)):
            eq_task[h][(x["state_id"], y["state_id"])] = v
            eq_task[h][(y["state_id"], x["state_id"])] = v
        for h, v in enumerate((l0, l1, l2)):
            eq_logit[h][(x["state_id"], y["state_id"])] = v
            eq_logit[h][(y["state_id"], x["state_id"])] = v

        first_sep = None
        if t0 and not t1:
            first_sep = "H1"
        elif t1 and not t2:
            first_sep = "H2"
        pairs.append({
            "state_a": x["state_id"],
            "state_b": y["state_id"],
            "task_equivalent": {"H0": t0, "H1": t1, "H2": t2},
            "logit_equivalent": {"H0": l0, "H1": l1, "H2": l2},
            "first_task_separation": first_sep,
            "same_parameter_hash": x["parameter_hash"] == y["parameter_hash"],
            "same_delta_norm": x["delta_stats"]["l2_hex"] == y["delta_stats"]["l2_hex"],
        })

    trans_task = {
        f"H{h}": transitivity_audit(state_ids, eq_task[h]) for h in (0, 1, 2)
    }
    trans_logit = {
        f"H{h}": transitivity_audit(state_ids, eq_logit[h]) for h in (0, 1, 2)
    }
    if any(trans_task[k] for k in trans_task):
        raise RuntimeError(f"task-equivalence transitivity failed: {trans_task}")

    op_partition = partition_from_exact_signatures(
        states, lambda s: canonical_json(operational_task_signature(s, action_ids))
    )
    rep_audit = representation_audit(states, op_partition)

    base_state = runtime["base"]
    duplicate = {
        "base_h1": duplicate_h1(
            editor,
            cfg,
            base_state["snapshot"],
            action_map[action_ids[0]],
            protected_tokens,
            panel_tokens,
        ),
        "nonbase_h1": None,
        "base_h2": duplicate_h2(
            editor,
            cfg,
            base_state["snapshot"],
            action_map[action_ids[0]],
            action_map[action_ids[0]],
            protected_tokens,
            panel_tokens,
        ),
    }
    nonbase = next((s for s in states if s["state_id"] != "base"), None)
    if nonbase is not None:
        duplicate["nonbase_h1"] = duplicate_h1(
            editor,
            cfg,
            nonbase["snapshot"],
            action_map[action_ids[0]],
            protected_tokens,
            panel_tokens,
        )

    if not duplicate["base_h1"] or not duplicate["base_h2"] or duplicate["nonbase_h1"] is False:
        raise RuntimeError(f"determinism control failure: {duplicate}")

    non_target_after = hash_non_target_params(editor)
    if non_target_after != non_target_before:
        raise RuntimeError("non-target model parameters changed")

    serial_states = []
    for s in states:
        serial_states.append({
            "state_id": s["state_id"],
            "anchor_id": s["anchor_id"],
            "parameter_hash": s["parameter_hash"],
            "delta_stats": s["delta_stats"],
            "root_reads": s["root_reads"],
            "tree": s["tree"],
        })

    h1_sep = sum(
        p["task_equivalent"]["H0"] and not p["task_equivalent"]["H1"]
        for p in pairs
    )
    h2_sep = sum(
        p["task_equivalent"]["H1"] and not p["task_equivalent"]["H2"]
        for p in pairs
    )

    out = {
        "protocol": PROTOCOL,
        "protocol_commit": PROTOCOL_COMMIT,
        "official_grace_commit": OFFICIAL_GRACE_COMMIT,
        "seed": a.seed,
        "status": "COMPLETE",
        "editor": {
            "name": "official_finetune",
            "target_parameter": TARGET_PARAM_NAME,
            "edit_lr": float(cfg.editor.edit_lr),
            "n_iter": int(cfg.n_iter),
            "optimizer": "Adam",
        },
        "registered_read": {
            "primary": "C_task",
            "diagnostic": "C_logit",
            "atol": a.read_atol,
            "rtol": a.read_rtol,
        },
        "seed_edit_indices": [int(x["idx"]) for x in seed_rows],
        "seed_contract": seed_contract,
        "anchor_ids": anchor_ids,
        "future_ids": future_ids,
        "panel_manifest": panel_manifest,
        "base_parameter_hash": base_hash,
        "non_target_parameter_hash_before": non_target_before,
        "non_target_parameter_hash_after": non_target_after,
        "anchor_attempts": attempts,
        "states": serial_states,
        "pairs": pairs,
        "task_transitivity": trans_task,
        "logit_transitivity": trans_logit,
        "representation_audit_h2_task": rep_audit,
        "duplicate_replay": duplicate,
        "summary": {
            "states": len(states),
            "h0_task_collision_pairs": len(pairs),
            "h1_task_separations_from_h0": int(h1_sep),
            "h2_task_separations_from_h1": int(h2_sep),
            "h2_task_operational_classes": len(op_partition),
            "parameter_identity_blocks": rep_audit["Pfull_target_parameter_hash"]["representation_blocks"],
            "parameter_identity_over_refinement_pairs": rep_audit["Pfull_target_parameter_hash"]["over_refinement_count"],
            "logit_h0_equivalent_pairs": sum(p["logit_equivalent"]["H0"] for p in pairs),
            "logit_h1_equivalent_pairs": sum(p["logit_equivalent"]["H1"] for p in pairs),
            "logit_h2_equivalent_pairs": sum(p["logit_equivalent"]["H2"] for p in pairs),
        },
    }

    write_artifact(a.out, out)


if __name__ == "__main__":
    main()
