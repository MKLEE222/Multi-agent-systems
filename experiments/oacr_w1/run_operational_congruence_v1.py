"""OACR-W1 v1: operational congruence refinement audit on official GRACE + SCOTUS.

Theory-led question:
    Is the equivalence induced by a frozen current-read family a congruence for
    GRACE's native write operator?  If not, which carrier-native refinements
    first separate the violating states?

This is an empirical carrier audit, not a theorem of global representation
adequacy and not a prevalence estimator.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import random
import sys
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import run_scotus_paired_closure as R  # noqa: E402
from grace_write_probe import (  # noqa: E402
    capture_query,
    commit_anchor_write,
    get_adapter,
    isolated_rng,
    projected_route_preservation_certificate,
    restore_adapter,
    route_probe,
    snapshot_adapter,
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--repo", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--seed_edits", type=int, default=4)
    p.add_argument("--seed_scan_limit", type=int, default=512)
    p.add_argument("--candidate_bank", type=int, default=48)
    p.add_argument("--anchors_per_mode", type=int, default=1)
    p.add_argument("--future_actions", type=int, default=8)
    p.add_argument("--sentinel_reads", type=int, default=16)
    p.add_argument("--seed", type=int, default=73)
    p.add_argument("--read_atol", type=float, default=1e-6)
    p.add_argument("--read_rtol", type=float, default=1e-5)
    p.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    return p.parse_args()


def _tensor_bytes(x: torch.Tensor) -> bytes:
    return x.detach().cpu().contiguous().numpy().tobytes()


def snapshot_hash(snap: Any) -> str:
    h = hashlib.sha256()
    h.update(b"codebook=1" if snap.has_codebook else b"codebook=0")
    if not snap.has_codebook:
        return h.hexdigest()
    for name, tensor in (
        ("keys", snap.keys),
        ("values", snap.values),
        ("epsilons", snap.epsilons),
    ):
        h.update(name.encode())
        h.update(str(tuple(tensor.shape)).encode())
        h.update(str(tensor.dtype).encode())
        h.update(_tensor_bytes(tensor))
    h.update(b"labels")
    for label in snap.key_labels:
        if torch.is_tensor(label):
            h.update(str(tuple(label.shape)).encode())
            h.update(str(label.dtype).encode())
            h.update(_tensor_bytes(label))
        else:
            h.update(repr(label).encode())
    return h.hexdigest()


def choose_future_actions(enriched: List[Dict[str, Any]], exclude_ids: set, n: int):
    """Outcome-blind deterministic round-robin over base-state route modes."""
    modes = ["reuse_same_label", "expand_same_label", "add_conflict_split", "add_far"]
    groups = {}
    for mode in modes:
        groups[mode] = sorted(
            [x for x in enriched if x["idx"] not in exclude_ids and x["route"]["update_mode"] == mode],
            key=lambda x: int(x["idx"]),
        )
    chosen, used = [], set()
    cursor = 0
    while len(chosen) < n:
        progressed = False
        for mode in modes:
            if cursor < len(groups[mode]):
                row = groups[mode][cursor]
                if row["idx"] not in used:
                    chosen.append(row)
                    used.add(row["idx"])
                    progressed = True
                    if len(chosen) >= n:
                        break
        if not progressed:
            break
        cursor += 1
    if not chosen:
        raise RuntimeError("No future actions available after excluding anchors")
    return chosen


def collect_sentinels(dataset, tokenizer, device, exclude_ids: set, n: int):
    rows = []
    for idx in range(len(dataset)):
        if idx in exclude_ids:
            continue
        item = dataset[idx]
        batch = {"text": [item["text"]], "labels": torch.tensor([item["labels"]])}
        tokens = R.tensor_tokens(batch, tokenizer, device)
        rows.append({"idx": idx, "item": item, "tokens": tokens})
        if len(rows) >= n:
            break
    if len(rows) < n:
        raise RuntimeError(f"Could only construct {len(rows)}/{n} sentinel reads")
    return rows


def simplified_route(route: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "update_mode": route["update_mode"],
        "nearest_key": route["nearest_key"],
        "retrieval_covered": route["retrieval_covered"],
        "same_label": route["same_label"],
        "nkeys": route["nkeys"],
    }


def protected_route_signature(cert: Dict[str, Any]):
    return [
        {
            "nearest_key": x["nearest_key"],
            "covered": bool(x["covered"]),
        }
        for x in cert["pre_signatures"]
    ]


def projection_signature(cert: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "projection_mode": cert["projection_mode"],
        "changed_indices": list(cert["changed_indices"]),
        "lost_indices": list(cert["lost_indices"]),
        "gained_indices": list(cert["gained_indices"]),
        "trained_value_index": cert["trained_value_index"],
        "protected_trained_row_indices": list(cert["protected_trained_row_indices"]),
        "protected_uses_trained_row": bool(cert["protected_uses_trained_row"]),
        "preservation_certificate": bool(cert["preservation_certificate"]),
    }


def measure_state_action(editor, state_snapshot, action, protected_tokens):
    """Read-only action-conditioned structural measurement."""
    adapter = get_adapter(editor)
    restore_adapter(adapter, state_snapshot)
    before = snapshot_hash(snapshot_adapter(adapter))

    q_action = capture_query(editor, action["tokens"])
    route = route_probe(adapter, q_action, action["tokens"]["labels"]).to_dict()
    protected_queries = [capture_query(editor, t) for t in protected_tokens]
    cert = projected_route_preservation_certificate(
        adapter,
        state_snapshot,
        q_action,
        action["tokens"]["labels"],
        protected_queries,
    )

    after = snapshot_hash(snapshot_adapter(adapter))
    if before != after:
        raise RuntimeError("Read-only route/projection measurement mutated adapter state")

    return {
        "action_route": simplified_route(route),
        "protected_route_signature": protected_route_signature(cert),
        "projection_signature": projection_signature(cert),
    }


def execute_action(
    editor,
    cfg,
    state_snapshot,
    action,
    protected_tokens,
    local_committed_tokens,
    read_panel_tokens,
    branch_seed: int,
):
    """Execute one registered action and capture the common post-write observations."""
    adapter = get_adapter(editor)
    restore_adapter(adapter, state_snapshot)
    expected_hash = snapshot_hash(state_snapshot)
    if snapshot_hash(snapshot_adapter(adapter)) != expected_hash:
        raise RuntimeError("Snapshot restore hash mismatch before future action")

    pre_target = R.acc(editor, action["tokens"])
    pre_fixed = R.obligation_status(editor, protected_tokens)
    pre_local = R.obligation_status(editor, local_committed_tokens)

    if pre_target >= 1.0:
        status = "ALREADY_SATISFIED_ZERO_WRITE"
    else:
        status = "EDIT_EXECUTED"
        with isolated_rng(int(branch_seed)):
            editor.edit(cfg, action["tokens"], batch_history=[])

    post_target = R.acc(editor, action["tokens"])
    post_fixed = R.obligation_status(editor, protected_tokens)
    post_local = R.obligation_status(editor, local_committed_tokens)
    post_reads = R.read_family_signatures(editor, read_panel_tokens)
    post_snap = snapshot_adapter(adapter)
    post_hash = snapshot_hash(post_snap)

    restore_adapter(adapter, state_snapshot)
    if snapshot_hash(snapshot_adapter(adapter)) != expected_hash:
        raise RuntimeError("Snapshot restore hash mismatch after future action")

    return {
        "status": status,
        "branch_seed": int(branch_seed),
        "pre_target_accuracy": pre_target,
        "post_target_accuracy": post_target,
        "target_realized": bool(post_target >= 1.0),
        "pre_fixed": pre_fixed,
        "post_fixed": post_fixed,
        "fixed_selective_realized": bool(post_target >= 1.0 and post_fixed["all_satisfied"]),
        "pre_local": pre_local,
        "post_local": post_local,
        "local_selective_realized": bool(post_target >= 1.0 and post_local["all_satisfied"]),
        "post_reads": post_reads,
        "post_state_hash": post_hash,
    }


def eq_json(a: Any, b: Any) -> bool:
    return json.dumps(a, sort_keys=True, separators=(",", ":")) == json.dumps(
        b, sort_keys=True, separators=(",", ":")
    )


def first_separating_level(levels: Dict[str, bool]) -> str:
    for level in ("A1", "A2", "A3"):
        if not levels[level]:
            return level
    return "UNSEPARATED_THROUGH_A3"


def main() -> None:
    args = parse_args()
    repo = Path(args.repo).resolve()
    sys.path.insert(0, str(repo))
    os.chdir(repo)

    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)

    from grace.editors import GRACE
    from grace.models import Classifier

    cfg = R.load_config(repo, args.device)
    model = Classifier(cfg).to(args.device)
    editor = GRACE(cfg, model)
    dataset = R.load_scotus_edit_dataset()

    seed_rows, protected_tokens, max_idx, seed_contract = R.build_contract_preserving_seed_state(
        editor,
        cfg,
        dataset,
        editor.tokenizer,
        args.device,
        args.seed_edits,
        args.seed_scan_limit,
        args.seed,
    )
    seed_indices = [int(x["idx"]) for x in seed_rows]
    base_snapshot = snapshot_adapter(get_adapter(editor))
    base_hash = snapshot_hash(base_snapshot)

    # Freeze natural candidate bank and all experiment selections before any
    # anchor outcome is inspected.
    bank = R.collect_errors(
        editor,
        dataset,
        editor.tokenizer,
        args.device,
        max_idx + 1,
        args.candidate_bank,
    )
    enriched = R.enrich_routes(editor, bank)
    anchors = R.choose_anchors_by_native_mode(enriched, args.anchors_per_mode)
    anchor_ids = {int(x["idx"]) for x in anchors}
    future_actions = choose_future_actions(enriched, anchor_ids, args.future_actions)
    future_ids = {int(x["idx"]) for x in future_actions}

    sentinel_exclude = set(seed_indices) | anchor_ids | future_ids
    sentinels = collect_sentinels(
        dataset,
        editor.tokenizer,
        args.device,
        sentinel_exclude,
        args.sentinel_reads,
    )

    read_panel_tokens = (
        list(protected_tokens)
        + [x["tokens"] for x in future_actions]
        + [x["tokens"] for x in sentinels]
    )
    read_panel_manifest = (
        [{"kind": "seed_obligation", "dataset_index": int(x["idx"])} for x in seed_rows]
        + [{"kind": "future_action", "dataset_index": int(x["idx"])} for x in future_actions]
        + [{"kind": "sentinel", "dataset_index": int(x["idx"])} for x in sentinels]
    )

    # Build independent one-anchor states from the exact same base state.
    states = [
        {
            "state_id": "base",
            "kind": "base",
            "anchor_id": None,
            "anchor_mode": None,
            "snapshot": base_snapshot,
            "local_committed_tokens": list(protected_tokens),
        }
    ]
    anchor_attempts = []
    for anchor in anchors:
        restore_adapter(get_adapter(editor), base_snapshot)
        before_hash = snapshot_hash(snapshot_adapter(get_adapter(editor)))
        anchor_seed = R.derive_seed(args.seed, "oacr_w1_anchor", anchor["idx"])
        state_post = commit_anchor_write(editor, cfg, anchor["tokens"], seed=anchor_seed)
        anchor_target = R.acc(editor, anchor["tokens"])
        fixed_after = R.obligation_status(editor, protected_tokens)
        after_hash = snapshot_hash(state_post)
        committed = bool(anchor_target >= 1.0 and fixed_after["all_satisfied"])
        anchor_attempts.append(
            {
                "dataset_index": int(anchor["idx"]),
                "base_route_mode": anchor["route"]["update_mode"],
                "branch_seed": int(anchor_seed),
                "base_state_hash": before_hash,
                "post_state_hash": after_hash,
                "target_realized": bool(anchor_target >= 1.0),
                "fixed_contract_preserved": bool(fixed_after["all_satisfied"]),
                "committed": committed,
            }
        )
        if committed:
            states.append(
                {
                    "state_id": f"anchor:{anchor['idx']}",
                    "kind": "one_anchor",
                    "anchor_id": int(anchor["idx"]),
                    "anchor_mode": anchor["route"]["update_mode"],
                    "snapshot": state_post,
                    "local_committed_tokens": list(protected_tokens) + [anchor["tokens"]],
                }
            )

    restore_adapter(get_adapter(editor), base_snapshot)
    if snapshot_hash(snapshot_adapter(get_adapter(editor))) != base_hash:
        raise RuntimeError("Base state hash changed after anchor-state construction")
    if len(states) < 2:
        raise RuntimeError("No contract-preserving anchor state available for pairwise audit")

    # Freeze and audit current registered reads for every state.
    serial_states = []
    runtime_state = {}
    for st in states:
        restore_adapter(get_adapter(editor), st["snapshot"])
        before = snapshot_hash(snapshot_adapter(get_adapter(editor)))
        reads = R.read_family_signatures(editor, read_panel_tokens)
        after = snapshot_hash(snapshot_adapter(get_adapter(editor)))
        if before != after:
            raise RuntimeError("Registered READ measurement mutated adapter state")
        runtime_state[st["state_id"]] = {**st, "pre_reads": reads}
        serial_states.append(
            {
                "state_id": st["state_id"],
                "kind": st["kind"],
                "anchor_id": st["anchor_id"],
                "anchor_mode": st["anchor_mode"],
                "state_hash": before,
            }
        )

    action_records: Dict[str, Dict[str, Any]] = {}
    for action in future_actions:
        aid = str(int(action["idx"]))
        branch_seed = R.derive_seed(args.seed, "oacr_w1_future", action["idx"])
        per_state = {}
        for state_id, st in runtime_state.items():
            structural = measure_state_action(
                editor, st["snapshot"], action, protected_tokens
            )
            execution = execute_action(
                editor,
                cfg,
                st["snapshot"],
                action,
                protected_tokens,
                st["local_committed_tokens"],
                read_panel_tokens,
                branch_seed,
            )
            per_state[state_id] = {
                **structural,
                **execution,
            }
        action_records[aid] = {
            "dataset_index": int(action["idx"]),
            "base_route_mode": action["route"]["update_mode"],
            "branch_seed": int(branch_seed),
            "per_state": per_state,
        }

    # Duplicate-branch determinism control on the base state and first action.
    control_action = future_actions[0]
    control_seed = R.derive_seed(args.seed, "oacr_w1_future", control_action["idx"])
    c1 = execute_action(
        editor,
        cfg,
        base_snapshot,
        control_action,
        protected_tokens,
        protected_tokens,
        read_panel_tokens,
        control_seed,
    )
    c2 = execute_action(
        editor,
        cfg,
        base_snapshot,
        control_action,
        protected_tokens,
        protected_tokens,
        read_panel_tokens,
        control_seed,
    )
    c_reads = R.compare_read_family(
        c1["post_reads"], c2["post_reads"], args.read_atol, args.read_rtol
    )
    duplicate_control = {
        "action_id": int(control_action["idx"]),
        "same_post_state_hash": c1["post_state_hash"] == c2["post_state_hash"],
        "same_target_status": c1["target_realized"] == c2["target_realized"],
        "same_fixed_status": c1["fixed_selective_realized"] == c2["fixed_selective_realized"],
        "post_read_strict_match": c_reads["strict_logits_matched"],
        "post_read_max_linf": c_reads["max_logit_linf"],
    }
    duplicate_control["pass"] = bool(
        duplicate_control["same_post_state_hash"]
        and duplicate_control["same_target_status"]
        and duplicate_control["same_fixed_status"]
        and duplicate_control["post_read_strict_match"]
    )
    if not duplicate_control["pass"]:
        raise RuntimeError("Duplicate branch idempotence control failed")

    # Pairwise quotient/congruence audit.
    pairs = []
    level_summary = {
        level: {"collisions": 0, "post_read_violations": 0, "strong_selective_violations": 0}
        for level in ("A0", "A1", "A2", "A3")
    }
    state_ids = [x["state_id"] for x in serial_states]
    for aid, ar in action_records.items():
        for s1, s2 in itertools.combinations(state_ids, 2):
            st1, st2 = runtime_state[s1], runtime_state[s2]
            r1, r2 = ar["per_state"][s1], ar["per_state"][s2]

            pre_cmp = R.compare_read_family(
                st1["pre_reads"], st2["pre_reads"], args.read_atol, args.read_rtol
            )
            post_cmp = R.compare_read_family(
                r1["post_reads"], r2["post_reads"], args.read_atol, args.read_rtol
            )

            A0 = bool(pre_cmp["strict_logits_matched"])
            A1 = bool(
                A0
                and r1["action_route"]["update_mode"] == r2["action_route"]["update_mode"]
            )
            A2 = bool(
                A1
                and eq_json(r1["action_route"], r2["action_route"])
                and eq_json(
                    r1["protected_route_signature"], r2["protected_route_signature"]
                )
            )
            A3 = bool(
                A2
                and eq_json(
                    r1["projection_signature"], r2["projection_signature"]
                )
            )
            levels = {"A0": A0, "A1": A1, "A2": A2, "A3": A3}

            post_violation = bool(A0 and not post_cmp["strict_logits_matched"])
            strong_selective = bool(
                A0
                and r1["target_realized"]
                and r2["target_realized"]
                and r1["fixed_selective_realized"] != r2["fixed_selective_realized"]
            )

            for level, equal in levels.items():
                if equal:
                    level_summary[level]["collisions"] += 1
                    if not post_cmp["strict_logits_matched"]:
                        level_summary[level]["post_read_violations"] += 1
                    if strong_selective:
                        level_summary[level]["strong_selective_violations"] += 1

            pairs.append(
                {
                    "action_id": int(aid),
                    "state_a": s1,
                    "state_b": s2,
                    "pre_read_strict_match": pre_cmp["strict_logits_matched"],
                    "pre_read_max_linf": pre_cmp["max_logit_linf"],
                    "post_read_strict_match": post_cmp["strict_logits_matched"],
                    "post_read_max_linf": post_cmp["max_logit_linf"],
                    "abstraction_equal": levels,
                    "primary_congruence_violation": post_violation,
                    "strong_selective_violation": strong_selective,
                    "first_separating_refinement": (
                        first_separating_level(levels) if post_violation else None
                    ),
                    "a_target_realized": r1["target_realized"],
                    "b_target_realized": r2["target_realized"],
                    "a_fixed_selective": r1["fixed_selective_realized"],
                    "b_fixed_selective": r2["fixed_selective_realized"],
                    "a_action_route": r1["action_route"],
                    "b_action_route": r2["action_route"],
                    "a_projection_signature": r1["projection_signature"],
                    "b_projection_signature": r2["projection_signature"],
                }
            )

    summary = {
        "n_states": len(serial_states),
        "n_actions": len(future_actions),
        "n_pairs": len(pairs),
        "n_A0_collisions": level_summary["A0"]["collisions"],
        "n_primary_congruence_violations": sum(
            int(x["primary_congruence_violation"]) for x in pairs
        ),
        "n_strong_selective_violations": sum(
            int(x["strong_selective_violation"]) for x in pairs
        ),
        "refinement_levels": level_summary,
        "unseparated_A0_violations_through_A3": sum(
            int(
                x["primary_congruence_violation"]
                and x["first_separating_refinement"] == "UNSEPARATED_THROUGH_A3"
            )
            for x in pairs
        ),
    }

    out = {
        "protocol": "OACR_W1_OPERATIONAL_CONGRUENCE_REFINEMENT_V1",
        "official_grace_commit": "f674183f17a995d109e10ee6140d4c3e6d016115",
        "device": args.device,
        "global_seed": args.seed,
        "registered_read_match": {"atol": args.read_atol, "rtol": args.read_rtol},
        "registered_parameters": {
            "seed_edits": args.seed_edits,
            "seed_scan_limit": args.seed_scan_limit,
            "candidate_bank": args.candidate_bank,
            "anchors_per_mode": args.anchors_per_mode,
            "future_actions": args.future_actions,
            "sentinel_reads": args.sentinel_reads,
            "n_iter": int(cfg.editor.n_iter),
            "edit_lr": float(cfg.editor.edit_lr),
        },
        "seed_edit_indices": seed_indices,
        "seed_contract": seed_contract,
        "read_panel_manifest": read_panel_manifest,
        "anchor_attempts": anchor_attempts,
        "states": serial_states,
        "future_action_ids": [int(x["idx"]) for x in future_actions],
        "duplicate_branch_control": duplicate_control,
        "action_records": action_records,
        "pairs": pairs,
        "summary": summary,
    }

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
