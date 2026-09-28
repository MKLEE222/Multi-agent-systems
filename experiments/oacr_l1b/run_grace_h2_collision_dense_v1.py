"""OACR-L1b v1: collision-dense H=0/1/2 learned horizon audit."""
from __future__ import annotations

import argparse
import itertools
import json
import math
import os
import random
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "oacr_w1"))
sys.path.insert(0, str(ROOT.parent / "r1_grace_scotus"))

import run_operational_congruence_v1 as W  # noqa: E402
import run_scotus_paired_closure as R  # noqa: E402
from grace_write_probe import (  # noqa: E402
    commit_anchor_write,
    get_adapter,
    isolated_rng,
    restore_adapter,
    snapshot_adapter,
)

MODES = ["reuse_same_label", "expand_same_label", "add_conflict_split", "add_far"]


def args():
    p = argparse.ArgumentParser()
    p.add_argument("--repo", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--seed", type=int, required=True)
    p.add_argument("--seed_edits", type=int, default=4)
    p.add_argument("--seed_scan_limit", type=int, default=1024)
    p.add_argument("--candidate_bank", type=int, default=512)
    p.add_argument("--anchor_candidates", type=int, default=24)
    p.add_argument("--anchors_per_mode", type=int, default=4)
    p.add_argument("--future_actions", type=int, default=4)
    p.add_argument("--sentinel_reads", type=int, default=24)
    p.add_argument("--max_states", type=int, default=8)
    p.add_argument("--read_atol", type=float, default=1e-6)
    p.add_argument("--read_rtol", type=float, default=1e-5)
    p.add_argument("--device", default="cpu")
    return p.parse_args()


def meta_signature(x: Dict[str, Any]) -> Tuple[Any, ...]:
    return (
        x["status"],
        bool(x["target_realized"]),
        bool(x["fixed_all_satisfied"]),
    )


def route_sort_key(x: Dict[str, Any]):
    mode = x["route"]["update_mode"]
    idx = int(x["idx"])
    if mode in {"reuse_same_label", "expand_same_label"}:
        return (abs(float(x["route"].get("retrieval_margin") or 0.0)), idx)
    if mode == "add_conflict_split":
        return (abs(float(x["route"].get("add_far_margin") or 0.0)), idx)
    return (float(x["route"].get("add_far_margin") or 0.0), idx)


def qvec(x: Dict[str, Any]) -> torch.Tensor:
    return x["query"].detach().cpu().float().view(-1)


def min_distance_to_selected(x: Dict[str, Any], selected: List[Dict[str, Any]]) -> float:
    if not selected:
        return float("inf")
    q = qvec(x)
    return min(
        float(torch.linalg.vector_norm(q - qvec(y)).item())
        for y in selected
    )


def farthest_fill(
    selected: List[Dict[str, Any]],
    pool: List[Dict[str, Any]],
    n: int,
) -> List[Dict[str, Any]]:
    out = list(selected)
    used = {int(x["idx"]) for x in out}
    remain = [x for x in pool if int(x["idx"]) not in used]
    if not out and remain:
        first = min(remain, key=lambda x: int(x["idx"]))
        out.append(first)
        used.add(int(first["idx"]))
        remain = [x for x in remain if int(x["idx"]) not in used]
    while len(out) < n and remain:
        scored = [
            (min_distance_to_selected(x, out), -int(x["idx"]), x)
            for x in remain
        ]
        _, _, chosen = max(scored, key=lambda z: (z[0], z[1]))
        out.append(chosen)
        used.add(int(chosen["idx"]))
        remain = [x for x in remain if int(x["idx"]) not in used]
    return out[:n]


def select_anchor_candidates(enriched, n: int, per_mode: int):
    selected = []
    used = set()
    phase_a = []
    for mode in MODES:
        cands = sorted(
            [x for x in enriched if x["route"]["update_mode"] == mode],
            key=route_sort_key,
        )
        for x in cands[:per_mode]:
            if int(x["idx"]) in used:
                continue
            selected.append(x)
            phase_a.append(int(x["idx"]))
            used.add(int(x["idx"]))
    selected = farthest_fill(selected, enriched, n)
    return selected, phase_a


def select_future_actions(enriched, exclude_ids: set, n: int):
    pool = [x for x in enriched if int(x["idx"]) not in exclude_ids]
    selected = []
    used = set()
    phase_a = []
    for mode in MODES:
        cands = sorted(
            [x for x in pool if x["route"]["update_mode"] == mode],
            key=route_sort_key,
        )
        if cands:
            x = cands[0]
            if int(x["idx"]) not in used:
                selected.append(x)
                phase_a.append(int(x["idx"]))
                used.add(int(x["idx"]))
        if len(selected) >= n:
            break
    selected = farthest_fill(selected, pool, n)
    return selected, phase_a


def apply_action(
    editor,
    cfg,
    start_snap,
    action,
    protected_tokens,
    read_panel_tokens,
    branch_seed,
):
    adapter = get_adapter(editor)
    restore_adapter(adapter, start_snap)
    expected = W.snapshot_hash(start_snap)
    if W.snapshot_hash(snapshot_adapter(adapter)) != expected:
        raise RuntimeError("restore mismatch before branch")

    pre_target = R.acc(editor, action["tokens"])
    if pre_target >= 1.0:
        status = "ALREADY_SATISFIED_ZERO_WRITE"
    else:
        status = "EDIT_EXECUTED"
        with isolated_rng(int(branch_seed)):
            editor.edit(cfg, action["tokens"], batch_history=[])

    post_target = R.acc(editor, action["tokens"])
    fixed = R.obligation_status(editor, protected_tokens)
    reads = R.read_family_signatures(editor, read_panel_tokens)
    post_snap = snapshot_adapter(adapter)
    post_hash = W.snapshot_hash(post_snap)

    restore_adapter(adapter, start_snap)
    if W.snapshot_hash(snapshot_adapter(adapter)) != expected:
        raise RuntimeError("restore mismatch after branch")

    serial = {
        "status": status,
        "branch_seed": int(branch_seed),
        "target_realized": bool(post_target >= 1.0),
        "fixed_all_satisfied": bool(fixed["all_satisfied"]),
        "post_reads": reads,
        "post_state_hash": post_hash,
    }
    return serial, post_snap


def reads_equal(a, b, atol, rtol):
    return bool(R.compare_read_family(a, b, atol, rtol)["strict_logits_matched"])


def read_compare(a, b, atol, rtol):
    return R.compare_read_family(a, b, atol, rtol)


def transitivity_audit(state_ids, eq):
    violations = []
    for a in state_ids:
        for b in state_ids:
            for c in state_ids:
                if eq[(a, b)] and eq[(b, c)] and not eq[(a, c)]:
                    violations.append([a, b, c])
                    if len(violations) >= 20:
                        return {"transitive": False, "violations_sample": violations}
    return {"transitive": not violations, "violations_sample": violations}


def count_blocks_if_equivalence(state_ids, eq):
    audit = transitivity_audit(state_ids, eq)
    if not audit["transitive"]:
        return None, audit
    seen = set()
    blocks = []
    for a in state_ids:
        if a in seen:
            continue
        block = [b for b in state_ids if eq[(a, b)]]
        for b in block:
            seen.add(b)
        blocks.append(sorted(block))
    return len(blocks), audit


def replay_equal(a, b, atol, rtol):
    return (
        meta_signature(a) == meta_signature(b)
        and reads_equal(a["post_reads"], b["post_reads"], atol, rtol)
        and a["post_state_hash"] == b["post_state_hash"]
    )


def replay_h1(editor, cfg, snap, action, protected_tokens, panel, seed):
    x, _ = apply_action(editor, cfg, snap, action, protected_tokens, panel, seed)
    y, _ = apply_action(editor, cfg, snap, action, protected_tokens, panel, seed)
    return replay_equal(x, y, 1e-6, 1e-5), x, y


def replay_h2(editor, cfg, snap, action_a, action_b, protected_tokens, panel, seed1, seed2):
    x1, xs = apply_action(editor, cfg, snap, action_a, protected_tokens, panel, seed1)
    x2, _ = apply_action(editor, cfg, xs, action_b, protected_tokens, panel, seed2)
    y1, ys = apply_action(editor, cfg, snap, action_a, protected_tokens, panel, seed1)
    y2, _ = apply_action(editor, cfg, ys, action_b, protected_tokens, panel, seed2)
    ok = replay_equal(x1, y1, 1e-6, 1e-5) and replay_equal(x2, y2, 1e-6, 1e-5)
    return ok, {"first_a": x1, "first_b": y1, "second_a": x2, "second_b": y2}


def main():
    a = args()
    repo = Path(a.repo).resolve()
    sys.path.insert(0, str(repo))
    os.chdir(repo)

    random.seed(a.seed)
    np.random.seed(a.seed)
    torch.manual_seed(a.seed)

    from grace.editors import GRACE
    from grace.models import Classifier

    cfg = R.load_config(repo, a.device)
    model = Classifier(cfg).to(a.device)
    editor = GRACE(cfg, model)
    dataset = R.load_scotus_edit_dataset()

    seed_rows, protected_tokens, max_idx, seed_contract = R.build_contract_preserving_seed_state(
        editor,
        cfg,
        dataset,
        editor.tokenizer,
        a.device,
        a.seed_edits,
        a.seed_scan_limit,
        a.seed,
    )
    seed_ids = [int(x["idx"]) for x in seed_rows]
    base = snapshot_adapter(get_adapter(editor))

    bank = R.collect_errors(
        editor,
        dataset,
        editor.tokenizer,
        a.device,
        max_idx + 1,
        a.candidate_bank,
    )
    enriched = R.enrich_routes(editor, bank)
    route_census = dict(Counter(x["route"]["update_mode"] for x in enriched))

    anchor_candidates, anchor_phase_a = select_anchor_candidates(
        enriched, a.anchor_candidates, a.anchors_per_mode
    )
    anchor_ids = {int(x["idx"]) for x in anchor_candidates}

    future, future_phase_a = select_future_actions(
        enriched, anchor_ids, a.future_actions
    )
    if len(future) != a.future_actions:
        raise RuntimeError(
            f"expected {a.future_actions} future actions, got {len(future)}"
        )
    future_ids = {int(x["idx"]) for x in future}

    sent = W.collect_sentinels(
        dataset,
        editor.tokenizer,
        a.device,
        set(seed_ids) | anchor_ids | future_ids,
        a.sentinel_reads,
    )

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

    # Freeze base READ once.
    restore_adapter(get_adapter(editor), base)
    before = W.snapshot_hash(snapshot_adapter(get_adapter(editor)))
    base_reads = R.read_family_signatures(editor, panel_tokens)
    after = W.snapshot_hash(snapshot_adapter(get_adapter(editor)))
    if before != after:
        raise RuntimeError("base READ mutated state")

    states = [{
        "state_id": "base",
        "snapshot": base,
        "kind": "base",
        "anchor_id": None,
        "anchor_mode": None,
        "root_reads": base_reads,
    }]
    retained_reads = {"base": base_reads}
    attempts = []

    for anchor in anchor_candidates:
        restore_adapter(get_adapter(editor), base)
        sd = R.derive_seed(a.seed, "oacr_l1b_anchor", anchor["idx"])
        post = commit_anchor_write(editor, cfg, anchor["tokens"], seed=sd)
        target = R.acc(editor, anchor["tokens"])
        fixed = R.obligation_status(editor, protected_tokens)
        post_hash = W.snapshot_hash(post)

        base_match = False
        all_retained_match = False
        root_reads = None
        base_cmp = None
        retained_cmps = {}

        if target >= 1.0 and fixed["all_satisfied"]:
            restore_adapter(get_adapter(editor), post)
            pre_read_hash = W.snapshot_hash(snapshot_adapter(get_adapter(editor)))
            root_reads = R.read_family_signatures(editor, panel_tokens)
            post_read_hash = W.snapshot_hash(snapshot_adapter(get_adapter(editor)))
            if pre_read_hash != post_read_hash:
                raise RuntimeError("anchor root READ mutated state")
            base_cmp = read_compare(
                root_reads, base_reads, a.read_atol, a.read_rtol
            )
            base_match = bool(base_cmp["strict_logits_matched"])
            all_retained_match = base_match
            if all_retained_match:
                for sid, reads in retained_reads.items():
                    cmp = read_compare(
                        root_reads, reads, a.read_atol, a.read_rtol
                    )
                    retained_cmps[sid] = {
                        "strict_logits_matched": bool(cmp["strict_logits_matched"]),
                        "max_logit_linf": cmp["max_logit_linf"],
                    }
                    if not cmp["strict_logits_matched"]:
                        all_retained_match = False
                        break

        capacity = len(states) < a.max_states
        eligible = bool(
            target >= 1.0
            and fixed["all_satisfied"]
            and base_match
            and all_retained_match
        )
        retained = bool(eligible and capacity)
        if not (target >= 1.0):
            reason = "target_not_realized"
        elif not fixed["all_satisfied"]:
            reason = "protected_contract_failed"
        elif not base_match:
            reason = "base_read_mismatch"
        elif not all_retained_match:
            reason = "retained_clique_read_mismatch"
        elif not capacity:
            reason = "capacity_reached"
        else:
            reason = "retained"

        attempt = {
            "anchor_id": int(anchor["idx"]),
            "mode": anchor["route"]["update_mode"],
            "seed": int(sd),
            "target_realized": bool(target >= 1.0),
            "fixed_preserved": bool(fixed["all_satisfied"]),
            "base_read_match": bool(base_match),
            "base_read_max_linf": (
                base_cmp["max_logit_linf"] if base_cmp is not None else None
            ),
            "all_retained_read_match": bool(all_retained_match),
            "retained_comparisons": retained_cmps,
            "eligible": eligible,
            "retained": retained,
            "reason": reason,
            "post_state_hash": post_hash,
        }
        attempts.append(attempt)

        if retained:
            sid = f"anchor:{anchor['idx']}"
            states.append({
                "state_id": sid,
                "snapshot": post,
                "kind": "anchor",
                "anchor_id": int(anchor["idx"]),
                "anchor_mode": anchor["route"]["update_mode"],
                "root_reads": root_reads,
            })
            retained_reads[sid] = root_reads

    if len(states) < 2:
        raise RuntimeError("fewer than two H0-collision states survived L1b construction")

    # Audit H0 clique directly.
    state_ids = [x["state_id"] for x in states]
    h0_clique_violations = []
    for x, y in itertools.combinations(state_ids, 2):
        if not reads_equal(
            retained_reads[x], retained_reads[y], a.read_atol, a.read_rtol
        ):
            h0_clique_violations.append([x, y])
    if h0_clique_violations:
        raise RuntimeError(f"H0 clique violations: {h0_clique_violations[:5]}")

    runtime = {}
    serial_states = []
    for st in states:
        feats = {}
        for act in future:
            feats[str(int(act["idx"]))] = W.measure_state_action(
                editor, st["snapshot"], act, protected_tokens
            )
        runtime[st["state_id"]] = {
            **st,
            "features": feats,
        }
        serial_states.append({
            "state_id": st["state_id"],
            "kind": st["kind"],
            "anchor_id": st["anchor_id"],
            "anchor_mode": st["anchor_mode"],
            "state_hash": W.snapshot_hash(st["snapshot"]),
        })

    action_map = {str(int(x["idx"])): x for x in future}
    action_ids = list(action_map)
    tree = {}

    for sid, st in runtime.items():
        one = {}
        one_snaps = {}
        for aid in action_ids:
            seed1 = R.derive_seed(a.seed, "oacr_l1b_h1", aid)
            meta, snap = apply_action(
                editor,
                cfg,
                st["snapshot"],
                action_map[aid],
                protected_tokens,
                panel_tokens,
                seed1,
            )
            one[aid] = meta
            one_snaps[aid] = snap

        two = {}
        for aid in action_ids:
            for bid in action_ids:
                seed2 = R.derive_seed(a.seed, "oacr_l1b_h2", aid, bid)
                meta, _ = apply_action(
                    editor,
                    cfg,
                    one_snaps[aid],
                    action_map[bid],
                    protected_tokens,
                    panel_tokens,
                    seed2,
                )
                two[f"{aid}>{bid}"] = meta
        tree[sid] = {"h1": one, "h2": two}

    # Determinism controls.
    aid0 = action_ids[0]
    seed1 = R.derive_seed(a.seed, "oacr_l1b_h1", aid0)
    base_h1_ok, _, _ = replay_h1(
        editor, cfg, runtime["base"]["snapshot"], action_map[aid0],
        protected_tokens, panel_tokens, seed1
    )

    nonbase = next((s for s in state_ids if s != "base"), None)
    nonbase_h1_ok = None
    if nonbase is not None:
        nonbase_h1_ok, _, _ = replay_h1(
            editor, cfg, runtime[nonbase]["snapshot"], action_map[aid0],
            protected_tokens, panel_tokens, seed1
        )

    bid0 = action_ids[0]
    seed2 = R.derive_seed(a.seed, "oacr_l1b_h2", aid0, bid0)
    base_h2_ok, _ = replay_h2(
        editor, cfg, runtime["base"]["snapshot"],
        action_map[aid0], action_map[bid0],
        protected_tokens, panel_tokens, seed1, seed2
    )

    if not base_h1_ok or nonbase_h1_ok is False or not base_h2_ok:
        raise RuntimeError("L1b duplicate replay control failed")

    eq_by_h = {h: {} for h in (0, 1, 2)}
    pair_rows = []

    def root_eq(x, y):
        return reads_equal(
            runtime[x]["root_reads"],
            runtime[y]["root_reads"],
            a.read_atol,
            a.read_rtol,
        )

    for x in state_ids:
        for y in state_ids:
            e0 = root_eq(x, y)
            e1 = e0
            if e1:
                for aid in action_ids:
                    bx, by = tree[x]["h1"][aid], tree[y]["h1"][aid]
                    if meta_signature(bx) != meta_signature(by) or not reads_equal(
                        bx["post_reads"], by["post_reads"], a.read_atol, a.read_rtol
                    ):
                        e1 = False
                        break
            e2 = e1
            if e2:
                for seq in sorted(tree[x]["h2"]):
                    bx, by = tree[x]["h2"][seq], tree[y]["h2"][seq]
                    if meta_signature(bx) != meta_signature(by) or not reads_equal(
                        bx["post_reads"], by["post_reads"], a.read_atol, a.read_rtol
                    ):
                        e2 = False
                        break
            eq_by_h[0][(x, y)] = e0
            eq_by_h[1][(x, y)] = e1
            eq_by_h[2][(x, y)] = e2

    def feature_sig(sid, level):
        f = runtime[sid]["features"]
        out = []
        for aid in action_ids:
            x = f[aid]
            if level == 1:
                out.append(x["action_route"]["update_mode"])
            elif level == 2:
                out.append({
                    "route": x["action_route"],
                    "protected": x["protected_route_signature"],
                })
            else:
                out.append({
                    "route": x["action_route"],
                    "protected": x["protected_route_signature"],
                    "projection": x["projection_signature"],
                })
        return json.dumps(out, sort_keys=True, separators=(",", ":"))

    for x, y in itertools.combinations(state_ids, 2):
        e0, e1, e2 = (eq_by_h[h][(x, y)] for h in (0, 1, 2))
        if not e0:
            first = 0
        elif not e1:
            first = 1
        elif not e2:
            first = 2
        else:
            first = None
        feats = {
            f"F{k}_equal": feature_sig(x, k) == feature_sig(y, k)
            for k in (1, 2, 3)
        }
        pair_rows.append({
            "state_a": x,
            "state_b": y,
            "equiv_h0": e0,
            "equiv_h1": e1,
            "equiv_h2": e2,
            "first_separation_horizon": first,
            **feats,
        })

    horizon = {}
    for h in (0, 1, 2):
        n, audit = count_blocks_if_equivalence(state_ids, eq_by_h[h])
        horizon[str(h)] = {
            "transitivity": audit,
            "N_h": n,
            "pairwise_equivalent_pairs": sum(
                int(r[f"equiv_h{h}"]) for r in pair_rows
            ),
        }

    feature_stats = {}
    h0pairs = [r for r in pair_rows if r["equiv_h0"]]
    for k in (1, 2, 3):
        key = f"F{k}_equal"
        feature_stats[f"F{k}"] = {
            "h0_collision_pairs": len(h0pairs),
            "under_refinement_pairs_at_h2": sum(
                int(r[key] and not r["equiv_h2"]) for r in h0pairs
            ),
            "over_refinement_pairs_at_h2": sum(
                int((not r[key]) and r["equiv_h2"]) for r in h0pairs
            ),
        }

    summary = {
        "seed": a.seed,
        "candidate_census_size": len(enriched),
        "route_mode_census": route_census,
        "anchor_candidates": len(anchor_candidates),
        "anchor_attempts": len(attempts),
        "anchor_eligible": sum(int(x["eligible"]) for x in attempts),
        "anchor_retained": sum(int(x["retained"]) for x in attempts),
        "states": len(state_ids),
        "actions": len(action_ids),
        "h0_collision_pairs": sum(int(r["equiv_h0"]) for r in pair_rows),
        "h1_separations_from_h0": sum(
            int(r["equiv_h0"] and not r["equiv_h1"]) for r in pair_rows
        ),
        "h2_separations_from_h1": sum(
            int(r["equiv_h1"] and not r["equiv_h2"]) for r in pair_rows
        ),
        "branch_trajectories_per_state": len(action_ids) + len(action_ids) ** 2,
        "total_branch_trajectories": len(state_ids) * (
            len(action_ids) + len(action_ids) ** 2
        ),
        "horizon": horizon,
        "feature_stats": feature_stats,
        "determinism": {
            "base_h1": base_h1_ok,
            "nonbase_h1": nonbase_h1_ok,
            "base_h2": base_h2_ok,
        },
    }

    out = {
        "protocol": "OACR_L1B_COLLISION_DENSE_GRACE_H2_V1",
        "protocol_commit": "694d42e92a152c09208d23d211942664306b335d",
        "official_grace_commit": "f674183f17a995d109e10ee6140d4c3e6d016115",
        "seed": a.seed,
        "read_match": {"atol": a.read_atol, "rtol": a.read_rtol},
        "seed_contract": seed_contract,
        "candidate_route_census": route_census,
        "anchor_selection": {
            "phase_a_ids": anchor_phase_a,
            "selected_ids": [int(x["idx"]) for x in anchor_candidates],
            "selected_modes": [x["route"]["update_mode"] for x in anchor_candidates],
        },
        "future_selection": {
            "phase_a_ids": future_phase_a,
            "selected_ids": [int(x["idx"]) for x in future],
            "selected_modes": [x["route"]["update_mode"] for x in future],
        },
        "panel_manifest": panel_manifest,
        "anchor_attempts": attempts,
        "states": serial_states,
        "action_ids": [int(x) for x in action_ids],
        "behavior_tree": tree,
        "pairs": pair_rows,
        "summary": summary,
    }

    p = Path(a.out)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(out, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
