"""Run R1 WRITE exploration on official GRACE + SCOTUS.

Expected environment: checkout of Thartvigsen/GRACE commit
f674183f17a995d109e10ee6140d4c3e6d016115 with the published model/data stack.

This runner does not alter GRACE's native editor. It creates exact persistent
snapshots, selects real candidate edits, commits real anchor writes, and tests
identical future writes before/after each anchor.
"""
from __future__ import annotations

import argparse
import json
import hashlib
import os
import random
import sys
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from grace_write_probe import (  # noqa: E402
    branch_future_edit,
    capture_query,
    commit_anchor_write,
    geometry_matches_projection,
    get_adapter,
    isolated_rng,
    project_structural_update,
    restore_adapter,
    route_probe,
    snapshot_adapter,
    snapshot_summary,
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--repo", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--seed_edits", type=int, default=4)
    p.add_argument("--candidate_bank", type=int, default=128)
    p.add_argument("--future_per_anchor", type=int, default=12)
    p.add_argument("--anchors_per_mode", type=int, default=1)
    p.add_argument("--seed_scan_limit", type=int, default=512)
    p.add_argument("--read_atol", type=float, default=1e-6)
    p.add_argument("--read_rtol", type=float, default=1e-5)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    return p.parse_args()


def load_config(repo: Path, device: str):
    from omegaconf import OmegaConf
    base = OmegaConf.load(repo / "grace/config/config.yaml")
    cfg = OmegaConf.create(OmegaConf.to_container(base, resolve=False))
    cfg.editor = OmegaConf.load(repo / "grace/config/editor/grace.yaml")
    cfg.experiment = OmegaConf.load(repo / "grace/config/experiment/scotus.yaml")
    cfg.model = OmegaConf.load(repo / "grace/config/model/scotus-bert.yaml")
    cfg.device = device
    cfg.wandb = False
    cfg.re_init_model = False
    cfg.dropout = 0.0
    # Bootstrap assets are downloaded with a modern Hub client, but the
    # registered GRACE runtime remains pinned to transformers==4.20.1.
    model_dir = os.environ.get("R1_SCOTUS_MODEL_DIR")
    tokenizer_dir = os.environ.get("R1_SCOTUS_TOKENIZER_DIR")
    if model_dir:
        cfg.model.name = str(Path(model_dir).resolve())
    if tokenizer_dir:
        cfg.model.tokenizer_name = str(Path(tokenizer_dir).resolve())
    return cfg


def load_scotus_edit_dataset():
    """Load the official SCOTUS test split from a frozen local parquet when set.

    This changes only transport, not examples or labels. It avoids legacy Hub
    redirect behavior in datasets/transformers while leaving the GRACE runtime
    and edit mechanism untouched.
    """
    parquet = os.environ.get("R1_SCOTUS_TEST_PARQUET")
    if not parquet:
        from grace.dataset import SCOTUS
        return SCOTUS(split="edit")
    import pyarrow.parquet as pq
    table = pq.read_table(str(Path(parquet).resolve()), columns=["text", "label"])
    data = table.to_pydict()
    rows = [{"text": x, "labels": int(y)} for x, y in zip(data["text"], data["label"])]
    class LocalSCOTUS:
        def __len__(self):
            return len(rows)
        def __getitem__(self, idx):
            return rows[idx]
    return LocalSCOTUS()


def tensor_tokens(batch, tokenizer, device):
    from grace.utils import tokenize_clf
    return tokenize_clf(batch, tokenizer, device)


def acc(editor, tokens) -> float:
    from grace.metrics import Accuracy
    with torch.no_grad():
        x = Accuracy(editor, tokens)
    return float(x.detach().cpu().item())


def derive_seed(global_seed: int, *parts: Any) -> int:
    msg = "|".join([str(global_seed), *[str(x) for x in parts]])
    return int(hashlib.sha256(msg.encode()).hexdigest()[:8], 16)


def read_signature(editor, tokens):
    """Registered current-read consequence for the SCOTUS pilot.

    We retain the full logit/probability vector, predicted class, target margin,
    and target cross-entropy. Strong WRITE witnesses require the pre/post-anchor
    signatures to match within a tolerance fixed before anchor outcomes.
    """
    import torch.nn.functional as F
    inputs = {k: v for k, v in tokens.items() if k != "labels"}
    with torch.no_grad():
        logits = editor(**inputs).logits.detach().float().view(-1)
    probs = torch.softmax(logits, dim=-1)
    target = int(tokens["labels"].view(-1)[0].item())
    pred = int(torch.argmax(logits).item())
    if logits.numel() > 1:
        mask = torch.ones_like(logits, dtype=torch.bool); mask[target] = False
        margin = float((logits[target] - logits[mask].max()).cpu().item())
    else:
        margin = float(logits[target].cpu().item())
    ce = float(F.cross_entropy(logits.view(1, -1), torch.tensor([target], device=logits.device)).cpu().item())
    return {
        "pred": pred, "target": target, "target_margin": margin, "cross_entropy": ce,
        "logits": [float(x) for x in logits.cpu()],
        "probs": [float(x) for x in probs.cpu()],
    }


def read_family_signatures(editor, toks):
    return [read_signature(editor, t) for t in toks]

def compare_read_family(a, b, atol: float, rtol: float):
    if len(a) != len(b):
        raise ValueError("read family size mismatch")
    pred_matched = all(x["pred"] == y["pred"] for x, y in zip(a, b))
    linfs = [_linf(x["logits"], y["logits"]) for x, y in zip(a, b)]
    strict = all(np.allclose(np.asarray(x["logits"]), np.asarray(y["logits"]), atol=atol, rtol=rtol) for x, y in zip(a, b))
    return {
        "predictions_matched": bool(pred_matched),
        "strict_logits_matched": bool(strict),
        "max_logit_linf": max(linfs) if linfs else 0.0,
        "per_item_logit_linf": linfs,
    }

def obligation_status(editor, toks):
    vals = [acc(editor, t) for t in toks]
    return {"n": len(vals), "values": vals, "all_satisfied": all(v >= 1.0 for v in vals), "n_failed": sum(v < 1.0 for v in vals)}


def build_contract_preserving_seed_state(editor, cfg, dataset, tokenizer, device, target_n: int, scan_limit: int, global_seed: int):
    """Build a non-vacuous base contract: every registered seed remains true.

    A candidate seed is committed only when it is realized AND all previously
    registered seed obligations remain satisfied after the write. Otherwise the
    exact adapter snapshot is restored and scanning continues.
    """
    obligations = []
    accepted = []
    max_idx = -1
    scanned = 0
    for idx in range(len(dataset)):
        if scanned >= scan_limit or len(accepted) >= target_n:
            break
        item = dataset[idx]
        batch = {"text": [item["text"]], "labels": torch.tensor([item["labels"]])}
        tokens = tensor_tokens(batch, tokenizer, device)
        if acc(editor, tokens) >= 1.0:
            continue
        scanned += 1
        base = snapshot_adapter(get_adapter(editor))
        seed = derive_seed(global_seed, "seed", idx)
        commit_anchor_write(editor, cfg, tokens, seed=seed)
        target_ok = acc(editor, tokens) >= 1.0
        old_ok = obligation_status(editor, obligations)["all_satisfied"]
        if target_ok and old_ok:
            obligations.append(tokens)
            accepted.append({"idx": idx, "item": item, "tokens": tokens, "branch_seed": seed})
            max_idx = max(max_idx, idx)
        else:
            restore_adapter(get_adapter(editor), base)
    if len(accepted) < target_n:
        raise RuntimeError(f"Could only build {len(accepted)}/{target_n} contract-preserving seed edits within scan limit {scan_limit}")
    final_status = obligation_status(editor, obligations)
    if not final_status["all_satisfied"]:
        raise RuntimeError("Seed contract invalid after construction")
    return accepted, obligations, max_idx, final_status


def collect_errors(editor, dataset, tokenizer, device, start_idx: int, limit: int):
    rows = []
    for idx in range(start_idx, len(dataset)):
        item = dataset[idx]
        batch = {"text": [item["text"]], "labels": torch.tensor([item["labels"]])}
        tokens = tensor_tokens(batch, tokenizer, device)
        if acc(editor, tokens) < 1.0:
            rows.append({"idx": idx, "item": item, "tokens": tokens})
            if len(rows) >= limit:
                break
    return rows


def enrich_routes(editor, rows):
    out = []
    for r in rows:
        q = capture_query(editor, r["tokens"])
        rp = route_probe(get_adapter(editor), q, r["tokens"]["labels"])
        out.append({**r, "query": q.detach().clone(), "route": rp.to_dict()})
    return out


def choose_anchors_by_native_mode(enriched, anchors_per_mode: int):
    """Select natural errors by the native update mode they would invoke now."""
    modes = ["reuse_same_label", "expand_same_label", "add_conflict_split", "add_far"]
    selected = []
    for mode in modes:
        cands = [x for x in enriched if x["route"]["update_mode"] == mode]
        # Prioritize candidates near a mode boundary to maximize informative geometry.
        if mode in {"reuse_same_label", "expand_same_label"}:
            cands.sort(key=lambda x: abs(float(x["route"]["retrieval_margin"] or 0.0)))
        elif mode == "add_conflict_split":
            cands.sort(key=lambda x: abs(float(x["route"]["add_far_margin"] or 0.0)))
        else:
            cands.sort(key=lambda x: float(x["route"]["add_far_margin"] or 0.0))
        for x in cands[:anchors_per_mode]:
            selected.append(x)
    if not selected:
        raise RuntimeError("No natural anchor found in any registered GRACE route mode")
    return selected


def select_future_pool(anchor, enriched, n: int):
    """Freeze a mixed future pool around one anchor query.

    This is carrier-native, not a claim of semantic relatedness. We include
    near same-label, near cross-label, and far queries because the official
    key/radius update rules predict different topology interactions there.
    """
    rows = [x for x in enriched if x["idx"] != anchor["idx"]]
    aq = anchor["query"].detach().cpu().view(-1)
    scored = []
    for x in rows:
        d = float(torch.linalg.vector_norm(aq - x["query"].detach().cpu().view(-1)).item())
        relation = "same_label" if x["item"]["labels"] == anchor["item"]["labels"] else "cross_label"
        scored.append((d, relation, x))
    same = sorted([z for z in scored if z[1] == "same_label"], key=lambda z: z[0])
    cross = sorted([z for z in scored if z[1] == "cross_label"], key=lambda z: z[0])
    far = sorted(scored, key=lambda z: z[0], reverse=True)
    each = max(1, n // 3)
    chosen = []
    used = set()
    for stratum, source in [("same_label_near", same), ("cross_label_near", cross), ("far", far)]:
        for d, relation, x in source:
            if x["idx"] in used:
                continue
            chosen.append({**x, "stratum": stratum, "distance_to_anchor": d})
            used.add(x["idx"])
            if sum(y["stratum"] == stratum for y in chosen) >= each:
                break
    return chosen[:n]


def query_fingerprint(q):
    b = q.detach().cpu().contiguous().numpy().tobytes()
    return hashlib.sha256(b).hexdigest()


def current_route(editor, row):
    q = capture_query(editor, row["tokens"])
    return route_probe(get_adapter(editor), q, row["tokens"]["labels"]).to_dict(), q


def branch_pool(editor, cfg, base_snapshot, selected, preexisting_obligations, committed_obligations, global_seed: int, anchor_id: Any):
    from grace.metrics import Accuracy
    rows = []
    for row in selected:
        restore_adapter(get_adapter(editor), base_snapshot)
        now_acc = acc(editor, row["tokens"])
        read_now = read_signature(editor, row["tokens"])
        route_now, q_now = current_route(editor, row)
        branch_seed = derive_seed(global_seed, "future", anchor_id, row["idx"])
        common = {
            "candidate_id": str(row["idx"]),
            "dataset_index": row["idx"],
            "label": int(row["item"]["labels"]),
            "stratum": row["stratum"],
            "distance_to_anchor": row["distance_to_anchor"],
            "current_accuracy": now_acc,
            "read_signature": read_now,
            "route_now": route_now,
            "query_norm": float(torch.linalg.vector_norm(q_now).detach().cpu().item()),
            "query_fingerprint": query_fingerprint(q_now),
            "branch_seed": int(branch_seed),
        }
        if now_acc >= 1.0:
            fixed = obligation_status(editor, preexisting_obligations)
            committed = obligation_status(editor, committed_obligations)
            common["status"] = "ALREADY_SATISFIED_ZERO_WRITE"
            common["zero_write_realized"] = True
            common["target_realized_under_registered_budget"] = True
            common["selective_realized"] = {
                "fixed_preexisting": bool(fixed["all_satisfied"]),
                "committed": bool(committed["all_satisfied"]),
            }
            common["obligations_zero_write"] = {"fixed_preexisting": fixed, "committed": committed}
            rows.append(common)
            continue
        res = branch_future_edit(
            editor=editor,
            config=cfg,
            metric_fn=Accuracy,
            tokens=row["tokens"],
            candidate_id=str(row["idx"]),
            base_snapshot=base_snapshot,
            success_threshold=1.0,
            obligation_groups={
                "fixed_preexisting": preexisting_obligations,
                "committed": committed_obligations,
            },
            branch_seed=branch_seed,
        )
        common["status"] = (
            "REALIZED_UNDER_REGISTERED_BUDGET"
            if res.target_realized_under_registered_budget
            else "UNREALIZED_UNDER_REGISTERED_BUDGET"
        )
        common["target_realized_under_registered_budget"] = bool(res.target_realized_under_registered_budget)
        common["selective_realized"] = res.selective_realized
        common["branch"] = res.to_dict()
        rows.append(common)
    restore_adapter(get_adapter(editor), base_snapshot)
    return rows


def _linf(xs, ys):
    return max((abs(float(a)-float(b)) for a,b in zip(xs,ys)), default=0.0)


def pair_rows(pre_rows, post_rows, read_atol: float, read_rtol: float, anchor_preserves_preexisting: bool):
    pre_map = {r["candidate_id"]: r for r in pre_rows}
    post_map = {r["candidate_id"]: r for r in post_rows}
    paired = []
    for cid in pre_map:
        a, b = pre_map[cid], post_map[cid]
        la, lb = a["read_signature"]["logits"], b["read_signature"]["logits"]
        read_matched = bool(np.allclose(np.asarray(la), np.asarray(lb), atol=read_atol, rtol=read_rtol))
        target_changed = bool(a["target_realized_under_registered_budget"] != b["target_realized_under_registered_budget"])
        fixed_changed = bool(a["selective_realized"]["fixed_preexisting"] != b["selective_realized"]["fixed_preexisting"])
        route_changed = a["route_now"]["update_mode"] != b["route_now"]["update_mode"]
        nearest_changed = a["route_now"]["nearest_key"] != b["route_now"]["nearest_key"]
        coverage_changed = a["route_now"]["retrieval_covered"] != b["route_now"]["retrieval_covered"]
        target_only = bool(read_matched and anchor_preserves_preexisting and target_changed)
        selective = bool(read_matched and anchor_preserves_preexisting and fixed_changed)
        paired.append({
            "candidate_id": cid,
            "pre": a,
            "post": b,
            "read_matched": read_matched,
            "read_logit_linf": _linf(la, lb),
            "read_prob_linf": _linf(a["read_signature"]["probs"], b["read_signature"]["probs"]),
            "read_margin_delta": float(b["read_signature"]["target_margin"] - a["read_signature"]["target_margin"]),
            "route_mode_changed": route_changed,
            "nearest_key_changed": nearest_changed,
            "coverage_changed": coverage_changed,
            "query_changed": a["query_fingerprint"] != b["query_fingerprint"],
            "target_budget_status_changed": target_changed,
            "fixed_selective_status_changed": fixed_changed,
            "candidate_read_matched_target_only_witness": target_only,
            "candidate_read_matched_selective_witness": selective,
            "strong_read_matched_write_witness": selective,
            "evidence_class": (
                "CANDIDATE_READ_MATCHED_SELECTIVE_DIVERGENCE" if selective else
                "CANDIDATE_READ_MATCHED_TARGET_ONLY_DIVERGENCE" if target_only else
                "READ_MATCHED_ROUTE_DIVERGENCE" if read_matched and (route_changed or nearest_changed or coverage_changed) else
                "READ_CHANGED" if not read_matched else
                "READ_MATCHED_NO_STRONG_DIVERGENCE"
            ),
        })
    return paired



def audit_mode_specific_mechanism(anchor_route, state_pre, paired):
    """Check route changes against exact structural consequences of anchor mode.

    These are implementation/mechanism invariants, not scientific claims. A
    violation blocks interpretation until explained.
    """
    mode = anchor_route["update_mode"]
    anchor_key = anchor_route["nearest_key"]
    violations = []
    for p in paired:
        pre = p["pre"]["route_now"]
        post = p["post"]["route_now"]
        changed = p["route_mode_changed"] or p["coverage_changed"]
        if p["query_changed"]:
            violations.append({"candidate_id": p["candidate_id"], "kind": "QUERY_DRIFT"})
            continue
        if mode == "reuse_same_label":
            if p["nearest_key_changed"] or changed:
                violations.append({"candidate_id": p["candidate_id"], "kind": "REUSE_TOPOLOGY_CHANGED"})
        elif mode == "expand_same_label":
            if p["nearest_key_changed"]:
                violations.append({"candidate_id": p["candidate_id"], "kind": "EXPAND_CHANGED_NEAREST_KEY"})
            elif changed and pre["nearest_key"] != anchor_key:
                violations.append({"candidate_id": p["candidate_id"], "kind": "EXPAND_CHANGED_UNAFFECTED_KEY"})
        elif mode == "add_far":
            if changed and not p["nearest_key_changed"]:
                violations.append({"candidate_id": p["candidate_id"], "kind": "ADD_FAR_CHANGED_WITHOUT_NEAREST_SWITCH"})
        elif mode == "add_conflict_split":
            explained = p["nearest_key_changed"] or pre["nearest_key"] == anchor_key
            if changed and not explained:
                violations.append({"candidate_id": p["candidate_id"], "kind": "CONFLICT_SPLIT_CHANGED_UNAFFECTED_REGION"})
    return {"mode": mode, "n_violations": len(violations), "violations": violations}

def main() -> None:
    args = parse_args()
    repo = Path(args.repo).resolve()
    sys.path.insert(0, str(repo))
    os.chdir(repo)
    random.seed(args.seed); np.random.seed(args.seed); torch.manual_seed(args.seed)

    from grace.editors import GRACE
    from grace.models import Classifier

    cfg = load_config(repo, args.device)
    model = Classifier(cfg).to(args.device)
    editor = GRACE(cfg, model)
    dataset = load_scotus_edit_dataset()

    # Build a non-vacuous real persistent memory: every registered seed edit
    # remains satisfied after the whole seed sequence. Failed/interfering seed
    # candidates are rolled back rather than silently registered as obligations.
    seed_rows, preexisting_obligations, max_idx, seed_contract = build_contract_preserving_seed_state(
        editor, cfg, dataset, editor.tokenizer, args.device, args.seed_edits, args.seed_scan_limit, args.seed
    )
    seed_indices = [x["idx"] for x in seed_rows]
    state_pre = snapshot_adapter(get_adapter(editor))

    # Freeze one natural future bank at z_i before any anchor outcomes are inspected.
    bank = collect_errors(editor, dataset, editor.tokenizer, args.device, max_idx + 1, args.candidate_bank)
    enriched = enrich_routes(editor, bank)
    anchors = choose_anchors_by_native_mode(enriched, args.anchors_per_mode)

    anchor_runs = []
    for anchor in anchors:
        restore_adapter(get_adapter(editor), state_pre)
        future = select_future_pool(anchor, enriched, args.future_per_anchor)
        pre_rows = branch_pool(
            editor, cfg, state_pre, future,
            preexisting_obligations=preexisting_obligations,
            committed_obligations=preexisting_obligations,
            global_seed=args.seed, anchor_id=anchor["idx"],
        )

        # Predict the exact structural key/radius update from the official rule.
        anchor_query_pre = capture_query(editor, anchor["tokens"])
        anchor_route_pre = route_probe(get_adapter(editor), anchor_query_pre, anchor["tokens"]["labels"]).to_dict()
        projection = project_structural_update(get_adapter(editor), state_pre, anchor_query_pre, anchor["tokens"]["labels"])

        fixed_read_pre = read_family_signatures(editor, preexisting_obligations)
        anchor_pre_acc = acc(editor, anchor["tokens"])
        anchor_seed = derive_seed(args.seed, "anchor", anchor["idx"])
        state_post = commit_anchor_write(editor, cfg, anchor["tokens"], seed=anchor_seed)
        anchor_post_acc = acc(editor, anchor["tokens"])
        anchor_preexisting_after = obligation_status(editor, preexisting_obligations)
        anchor_preserves_preexisting = bool(anchor_preexisting_after["all_satisfied"])
        fixed_read_post = read_family_signatures(editor, preexisting_obligations)
        fixed_read_cmp = compare_read_family(fixed_read_pre, fixed_read_post, args.read_atol, args.read_rtol)
        if anchor_post_acc < 1.0:
            # Honest carrier failure: keep record and do not treat as a committed state.
            anchor_runs.append({
                "anchor": {"dataset_index": anchor["idx"], "route_pre": anchor_route_pre},
                "status": "ANCHOR_UNREALIZED_UNDER_REGISTERED_BUDGET",
                "pre_accuracy": anchor_pre_acc,
                "post_accuracy": anchor_post_acc,
            })
            continue

        proj_check = geometry_matches_projection(get_adapter(editor), projection)
        anchor_query_post = capture_query(editor, anchor["tokens"])
        query_drift = float(torch.linalg.vector_norm(anchor_query_post - anchor_query_pre).detach().cpu().item())

        post_rows = branch_pool(
            editor, cfg, state_post, future,
            preexisting_obligations=preexisting_obligations,
            committed_obligations=preexisting_obligations + [anchor["tokens"]],
            global_seed=args.seed, anchor_id=anchor["idx"],
        )
        paired = pair_rows(pre_rows, post_rows, args.read_atol, args.read_rtol, anchor_preserves_preexisting)
        for pp in paired:
            pp["fixed_read_predictions_matched"] = fixed_read_cmp["predictions_matched"]
            pp["fixed_read_strict_logits_matched"] = fixed_read_cmp["strict_logits_matched"]
            pp["fixed_read_max_logit_linf"] = fixed_read_cmp["max_logit_linf"]
            pp["task_full_read_selective_witness"] = bool(pp["candidate_read_matched_selective_witness"] and fixed_read_cmp["predictions_matched"])
            pp["strict_full_read_selective_witness"] = bool(pp["candidate_read_matched_selective_witness"] and fixed_read_cmp["strict_logits_matched"])
            if pp["strict_full_read_selective_witness"]:
                pp["evidence_class"] = "STRICT_FULL_READ_SELECTIVE_DIVERGENCE"
            elif pp["task_full_read_selective_witness"]:
                pp["evidence_class"] = "TASK_FULL_READ_SELECTIVE_DIVERGENCE"

        mechanism_audit = audit_mode_specific_mechanism(anchor_route_pre, state_pre, paired)

        # Strong negative control: reuse_same_label makes no key/radius topology change.
        negative_control_expected = (anchor_route_pre["update_mode"] == "reuse_same_label")
        negative_control_violations = 0
        if negative_control_expected:
            negative_control_violations = sum(
                bool(x["route_mode_changed"] or x["nearest_key_changed"] or x["coverage_changed"])
                for x in paired
            )

        anchor_runs.append({
            "status": "COMMITTED",
            "anchor": {
                "dataset_index": anchor["idx"],
                "label": int(anchor["item"]["labels"]),
                "pre_accuracy": anchor_pre_acc,
                "post_accuracy": anchor_post_acc,
                "route_pre": anchor_route_pre,
                "query_drift_l2": query_drift,
                "branch_seed": int(anchor_seed),
                "preserves_preexisting_obligations": anchor_preserves_preexisting,
                "preexisting_obligations_after": anchor_preexisting_after,
                "fixed_preexisting_read_compare": fixed_read_cmp,
            },
            "state_pre": snapshot_summary(state_pre),
            "state_post": snapshot_summary(state_post),
            "projected_structural_mode": projection.mode,
            "projection_matches_actual": proj_check,
            "mechanism_audit": mechanism_audit,
            "negative_control_expected": negative_control_expected,
            "negative_control_route_violations": negative_control_violations,
            "pairs": paired,
        })

    out = {
        "protocol": "R1_GRACE_PAIRED_CLOSURE_V4_FULL_READ_SELECTIVE",
        "official_grace_commit": "f674183f17a995d109e10ee6140d4c3e6d016115",
        "device": args.device,
        "seed": args.seed,
        "seed_edit_indices": seed_indices,
        "seed_contract": seed_contract,
        "registered_read_match": {"atol": args.read_atol, "rtol": args.read_rtol},
        "registered_budget": {"n_iter": int(cfg.editor.n_iter), "edit_lr": float(cfg.editor.edit_lr)},
        "anchor_runs": anchor_runs,
    }
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2))

    committed = [x for x in anchor_runs if x.get("status") == "COMMITTED"]
    summary = {
        "out": str(out_path),
        "anchors_attempted": len(anchor_runs),
        "anchors_committed": len(committed),
        "route_mode_changes": sum(sum(bool(p["route_mode_changed"]) for p in x["pairs"]) for x in committed),
        "nearest_key_changes": sum(sum(bool(p["nearest_key_changed"]) for p in x["pairs"]) for x in committed),
        "coverage_changes": sum(sum(bool(p["coverage_changed"]) for p in x["pairs"]) for x in committed),
        "negative_control_violations": sum(int(x["negative_control_route_violations"]) for x in committed),
        "mechanism_audit_violations": sum(int(x["mechanism_audit"]["n_violations"]) for x in committed),
        "anchors_preserving_preexisting": sum(bool(x["anchor"]["preserves_preexisting_obligations"]) for x in committed),
        "read_matched_pairs": sum(sum(bool(p["read_matched"]) for p in x["pairs"]) for x in committed),
        "candidate_read_matched_selective_witnesses": sum(sum(bool(p.get("candidate_read_matched_selective_witness", False)) for p in x["pairs"]) for x in committed),
        "task_full_read_selective_witnesses": sum(sum(bool(p.get("task_full_read_selective_witness", False)) for p in x["pairs"]) for x in committed),
        "strict_full_read_selective_witnesses": sum(sum(bool(p.get("strict_full_read_selective_witness", False)) for p in x["pairs"]) for x in committed),
        "candidate_read_matched_target_only_witnesses": sum(sum(bool(p.get("candidate_read_matched_target_only_witness", False)) for p in x["pairs"]) for x in committed),
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()