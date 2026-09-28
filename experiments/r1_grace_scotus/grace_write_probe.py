"""Instrumentation for GRACE WRITE-closure experiments.

Designed against Thartvigsen/GRACE commit
f674183f17a995d109e10ee6140d4c3e6d016115.

This module does NOT change GRACE's native write rule. It snapshots/restores
its persistent adapter state, records the exact routing geometry, projects the
iteration-0 structural update implied by the official code, and executes
future edits from exact common snapshots.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional
from contextlib import contextmanager
import copy
import random
import time

import numpy as np
import torch

DYNAMIC_FIELDS = ("keys", "values", "epsilons", "key_labels")


@contextmanager
def isolated_rng(seed: int):
    """Use a deterministic branch RNG without contaminating the outer run.

    GRACE cold-initializes candidate values with torch.rand. Paired pre/post
    branches therefore must see the same random stream; otherwise apparent
    future-write differences can be initialization noise.
    """
    py_state = random.getstate()
    np_state = np.random.get_state()
    torch_state = torch.random.get_rng_state()
    cuda_states = torch.cuda.get_rng_state_all() if torch.cuda.is_available() else None
    try:
        random.seed(seed)
        np.random.seed(seed % (2**32 - 1))
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
        yield
    finally:
        random.setstate(py_state)
        np.random.set_state(np_state)
        torch.random.set_rng_state(torch_state)
        if cuda_states is not None:
            torch.cuda.set_rng_state_all(cuda_states)


def value_delta_summary(before: AdapterSnapshot, after: AdapterSnapshot, tol: float = 1e-10) -> Dict[str, Any]:
    if not before.has_codebook or not after.has_codebook:
        return {
            "common_rows": 0, "changed_common_rows": [], "per_common_row_l2": [],
            "common_frobenius": None, "added_rows": (0 if not after.has_codebook else int(after.values.shape[0])),
        }
    old = before.values.detach().float().cpu()
    new = after.values.detach().float().cpu()
    n = min(old.shape[0], new.shape[0])
    if n:
        delta = new[:n] - old[:n]
        row_l2 = torch.linalg.vector_norm(delta, dim=1)
        changed = [int(i) for i, x in enumerate(row_l2) if float(x) > tol]
        fro = float(torch.linalg.vector_norm(delta).item())
        vals = [float(x) for x in row_l2]
    else:
        changed, fro, vals = [], 0.0, []
    return {
        "common_rows": int(n),
        "changed_common_rows": changed,
        "per_common_row_l2": vals,
        "common_frobenius": fro,
        "added_rows": int(max(0, new.shape[0] - old.shape[0])),
    }


def _resolve_path(root: Any, path: str) -> Any:
    path = path.replace("[", ".").replace("]", "")
    obj = root
    for part in path.split("."):
        if not part:
            continue
        obj = obj[int(part)] if part.isdigit() else getattr(obj, part)
    return obj


def get_adapter(editor: Any) -> Any:
    return _resolve_path(editor.model, editor.layer)


def _clone_label(x: Any) -> Any:
    return x.detach().clone() if torch.is_tensor(x) else copy.deepcopy(x)


@dataclass
class AdapterSnapshot:
    has_codebook: bool
    keys: Optional[torch.Tensor] = None
    values: Optional[torch.Tensor] = None
    epsilons: Optional[torch.Tensor] = None
    key_labels: Optional[List[Any]] = None


def snapshot_adapter(adapter: Any) -> AdapterSnapshot:
    if not hasattr(adapter, "keys"):
        return AdapterSnapshot(has_codebook=False)
    return AdapterSnapshot(
        has_codebook=True,
        keys=adapter.keys.detach().clone(),
        values=adapter.values.detach().clone(),
        epsilons=adapter.epsilons.detach().clone(),
        key_labels=[_clone_label(x) for x in adapter.key_labels],
    )


def restore_adapter(adapter: Any, snap: AdapterSnapshot) -> None:
    if not snap.has_codebook:
        for field in DYNAMIC_FIELDS:
            if field in adapter.__dict__:
                delattr(adapter, field)
        return
    adapter.keys = snap.keys.detach().clone().to(adapter.device)
    adapter.values = torch.nn.Parameter(
        snap.values.detach().clone().to(adapter.device), requires_grad=True
    )
    adapter.epsilons = snap.epsilons.detach().clone().to(adapter.device)
    adapter.key_labels = [_clone_label(x) for x in snap.key_labels]


def snapshot_summary(snap: AdapterSnapshot) -> Dict[str, Any]:
    if not snap.has_codebook:
        return {"nkeys": 0, "epsilons": []}
    return {
        "nkeys": int(snap.keys.shape[0]),
        "epsilons": [float(x) for x in snap.epsilons.detach().cpu().view(-1)],
    }


@torch.no_grad()
def capture_query(editor: Any, tokens: Dict[str, torch.Tensor]) -> torch.Tensor:
    """Capture the exact hidden query entering the registered GRACE adapter.

    For the SCOTUS carrier the adapter replaces layer[10].output.dense. The
    query is the input to that module, so same-input query coordinates are
    upstream of the persistent GRACE value replacement at that module. We
    nevertheless record and later verify query drift empirically rather than
    assuming it away.
    """
    adapter = get_adapter(editor)
    old_training = adapter.training
    adapter.training = False
    captured: Dict[str, torch.Tensor] = {}

    def hook(_module: Any, args: Any) -> None:
        hidden = args[0]
        token_to_edit = min(adapter.key_id, hidden.shape[1] - 1)
        captured["query"] = hidden[:, token_to_edit, :].detach().clone()

    handle = adapter.register_forward_pre_hook(hook)
    try:
        editor.model(**tokens)
    finally:
        handle.remove()
        adapter.training = old_training
    if "query" not in captured:
        raise RuntimeError("GRACE adapter query hook did not fire")
    return captured["query"]


@dataclass
class RouteProbe:
    has_codebook: bool
    nkeys: int
    nearest_key: Optional[int]
    distance: Optional[float]
    epsilon: Optional[float]
    retrieval_covered: Optional[bool]
    retrieval_margin: Optional[float]
    update_mode: str
    add_far_margin: Optional[float]
    same_label: Optional[bool]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _route_probe_from_parts(
    *,
    keys: Optional[torch.Tensor],
    epsilons: Optional[torch.Tensor],
    key_labels: Optional[List[Any]],
    init_epsilon: float,
    label_match_fn: Any,
    query: torch.Tensor,
    edit_label: Any,
) -> RouteProbe:
    if keys is None:
        return RouteProbe(False, 0, None, None, None, None, None, "init_key", None, None)
    dists = torch.cdist(keys.detach(), query.detach(), p=2).view(-1, len(query))
    smallest_distance, nearest_key = dists.min(0)
    if smallest_distance.numel() != 1:
        raise ValueError("route_probe currently requires batch size 1")
    idx = int(nearest_key.item())
    dist = float(smallest_distance.item())
    eps = float(epsilons[idx].detach().item())
    covered = dist <= eps
    same_label = bool(label_match_fn(edit_label, key_labels[idx]))
    far_threshold = float(init_epsilon) + eps
    if dist > far_threshold:
        mode = "add_far"
    elif not same_label:
        mode = "add_conflict_split"
    elif dist > eps:
        mode = "expand_same_label"
    else:
        mode = "reuse_same_label"
    return RouteProbe(
        True, int(keys.shape[0]), idx, dist, eps, covered, eps - dist,
        mode, dist - far_threshold, same_label,
    )


def route_probe(adapter: Any, query: torch.Tensor, edit_label: Any) -> RouteProbe:
    if not hasattr(adapter, "keys"):
        return _route_probe_from_parts(
            keys=None, epsilons=None, key_labels=None,
            init_epsilon=float(adapter.init_epsilon),
            label_match_fn=adapter.label_match,
            query=query, edit_label=edit_label,
        )
    return _route_probe_from_parts(
        keys=adapter.keys,
        epsilons=adapter.epsilons,
        key_labels=adapter.key_labels,
        init_epsilon=float(adapter.init_epsilon),
        label_match_fn=adapter.label_match,
        query=query,
        edit_label=edit_label,
    )


@dataclass
class GeometryProjection:
    mode: str
    keys: torch.Tensor
    epsilons: torch.Tensor
    key_labels: List[Any]


def project_structural_update(adapter: Any, snap: AdapterSnapshot, query: torch.Tensor, edit_label: Any) -> GeometryProjection:
    """Apply only GRACE's official iteration-0 key/radius/label geometry rule.

    Values are intentionally omitted because they do not enter GRACE's routing
    decision. Under the registered SCOTUS config (eps_expand=coverage), this
    projection should match the committed adapter's keys/epsilons exactly.
    """
    init_eps = float(adapter.init_epsilon)
    if not snap.has_codebook:
        return GeometryProjection(
            mode="init_key",
            keys=query.detach().clone(),
            epsilons=torch.tensor([init_eps], device=query.device, dtype=query.dtype),
            key_labels=[_clone_label(edit_label)],
        )

    keys = snap.keys.detach().clone().to(query.device)
    eps = snap.epsilons.detach().clone().to(query.device)
    labels = [_clone_label(x) for x in snap.key_labels]
    rp = _route_probe_from_parts(
        keys=keys, epsilons=eps, key_labels=labels,
        init_epsilon=init_eps, label_match_fn=adapter.label_match,
        query=query, edit_label=edit_label,
    )
    idx = rp.nearest_key
    if rp.update_mode == "add_far":
        keys = torch.vstack([keys, query.detach().clone()])
        eps = torch.cat([eps.view(-1), torch.tensor([init_eps], device=eps.device, dtype=eps.dtype)]).view(-1, 1)
        labels.append(_clone_label(edit_label))
    elif rp.update_mode == "add_conflict_split":
        keys = torch.vstack([keys, query.detach().clone()])
        eps = torch.cat([eps.view(-1), torch.tensor([init_eps], device=eps.device, dtype=eps.dtype)]).view(-1, 1)
        labels.append(_clone_label(edit_label))
        eps[idx] = float(rp.distance) / 2.0 - 1e-5
        eps[-1] = float(rp.distance) / 2.0
    elif rp.update_mode == "expand_same_label":
        # Registered config uses eps_expand=coverage.
        eps[idx] = float(rp.distance)
    elif rp.update_mode == "reuse_same_label":
        pass
    else:
        raise RuntimeError(f"Unknown GRACE route mode: {rp.update_mode}")
    return GeometryProjection(rp.update_mode, keys, eps, labels)



def _retrieval_signature_from_geometry(
    keys: Optional[torch.Tensor],
    epsilons: Optional[torch.Tensor],
    query: torch.Tensor,
) -> Dict[str, Any]:
    """Read-only nearest-key/coverage signature for one batch-size-1 query."""
    if keys is None or epsilons is None or int(keys.shape[0]) == 0:
        return {
            "nearest_key": None,
            "distance": None,
            "epsilon": None,
            "covered": False,
            "margin": None,
        }
    dists = torch.cdist(keys.detach(), query.detach(), p=2).view(-1, len(query))
    smallest_distance, nearest_key = dists.min(0)
    if smallest_distance.numel() != 1:
        raise ValueError("retrieval signature currently requires batch size 1")
    idx = int(nearest_key.item())
    dist = float(smallest_distance.item())
    eps = float(epsilons[idx].detach().item())
    return {
        "nearest_key": idx,
        "distance": dist,
        "epsilon": eps,
        "covered": bool(dist <= eps),
        "margin": eps - dist,
    }


def projected_route_preservation_certificate(
    adapter: Any,
    snap: AdapterSnapshot,
    future_query: torch.Tensor,
    edit_label: Any,
    protected_queries: List[torch.Tensor],
) -> Dict[str, Any]:
    """Project GRACE iteration-0 structure and audit protected retrieval routes.

    This is deliberately read-only: it never executes an edit and never mutates
    ``adapter``.  It implements the carrier certificate frozen in
    R1A_GRACE_STRUCTURAL_CERTIFICATE.md.

    ``preservation_certificate`` is true iff every protected query keeps the
    same (nearest-key, covered/uncovered) retrieval signature after the exact
    structural projection and no covered protected query consumes the value row
    that the future write would optimize.

    ``lost_indices`` reports the narrower failure-certificate precursor used by
    the prospective protocol: protected queries that are covered before the
    future write but uncovered after its structural projection.  Whether such a
    loss *forces* semantic failure is checked separately by testing the frozen
    no-retrieval fallback.
    """
    proj = project_structural_update(adapter, snap, future_query, edit_label)

    if snap.has_codebook:
        pre_keys = snap.keys.detach().to(future_query.device)
        pre_eps = snap.epsilons.detach().to(future_query.device)
    else:
        pre_keys = None
        pre_eps = None

    proj_keys = proj.keys.detach().to(future_query.device)
    proj_eps = proj.epsilons.detach().to(future_query.device)

    # GRACE trains the value selected by the future query *after* the
    # iteration-0 topology/radius update.  Because subsequent iterations freeze
    # structure, this row is the only value row that can receive gradient from
    # the registered batch-size-1 future edit.
    future_sig = _retrieval_signature_from_geometry(proj_keys, proj_eps, future_query)
    trained_value_index = future_sig["nearest_key"]

    pre_signatures: List[Dict[str, Any]] = []
    projected_signatures: List[Dict[str, Any]] = []
    changed_indices: List[int] = []
    lost_indices: List[int] = []
    gained_indices: List[int] = []
    trained_row_users: List[int] = []

    for i, q in enumerate(protected_queries):
        qd = q.detach().to(future_query.device)
        before = _retrieval_signature_from_geometry(pre_keys, pre_eps, qd)
        after = _retrieval_signature_from_geometry(proj_keys, proj_eps, qd)
        pre_signatures.append(before)
        projected_signatures.append(after)

        same_signature = (
            before["nearest_key"] == after["nearest_key"]
            and bool(before["covered"]) == bool(after["covered"])
        )
        if not same_signature:
            changed_indices.append(i)
        if bool(before["covered"]) and not bool(after["covered"]):
            lost_indices.append(i)
        if (not bool(before["covered"])) and bool(after["covered"]):
            gained_indices.append(i)
        if (
            bool(after["covered"])
            and trained_value_index is not None
            and after["nearest_key"] == trained_value_index
        ):
            trained_row_users.append(i)

    preservation = (len(changed_indices) == 0 and len(trained_row_users) == 0)
    return {
        "projection_mode": proj.mode,
        "trained_value_index": trained_value_index,
        "future_projected_route": future_sig,
        "pre_signatures": pre_signatures,
        "projected_signatures": projected_signatures,
        "changed_indices": changed_indices,
        "lost_indices": lost_indices,
        "gained_indices": gained_indices,
        "protected_uses_trained_row": bool(trained_row_users),
        "protected_trained_row_indices": trained_row_users,
        "preservation_certificate": bool(preservation),
    }


def geometry_matches_projection(adapter: Any, proj: GeometryProjection, atol: float = 1e-6) -> Dict[str, Any]:
    if not hasattr(adapter, "keys"):
        return {"match": False, "reason": "actual_missing_codebook"}
    key_match = adapter.keys.shape == proj.keys.shape and bool(torch.allclose(adapter.keys.detach(), proj.keys.to(adapter.keys.device), atol=atol, rtol=0))
    eps_match = adapter.epsilons.shape == proj.epsilons.shape and bool(torch.allclose(adapter.epsilons.detach(), proj.epsilons.to(adapter.epsilons.device), atol=atol, rtol=0))
    return {"match": key_match and eps_match, "keys_match": key_match, "eps_match": eps_match}


def _metric_scalar(metric_fn: Any, editor: Any, tokens: Dict[str, torch.Tensor]) -> float:
    with torch.no_grad():
        val = metric_fn(editor, tokens)
    if torch.is_tensor(val):
        return float(val.detach().cpu().mean().item())
    return float(val)


def evaluate_obligation_group(metric_fn: Any, editor: Any, toks: List[Dict[str, torch.Tensor]], threshold: float = 1.0) -> Dict[str, Any]:
    vals = [_metric_scalar(metric_fn, editor, t) for t in toks]
    return {
        "n": len(vals),
        "values": vals,
        "mean": (sum(vals) / len(vals) if vals else None),
        "min": (min(vals) if vals else None),
        "all_satisfied": (all(v >= threshold for v in vals) if vals else True),
        "n_failed": sum(v < threshold for v in vals),
    }


@dataclass
class BranchEditResult:
    candidate_id: str
    pre_metric: float
    post_metric: float
    route_before: Dict[str, Any]
    elapsed_seconds: float
    nkeys_before: int
    nkeys_after: int
    eps_before: List[float]
    eps_after: List[float]
    edit_loss: Optional[float]
    loss_trajectory: List[float]
    target_realized_under_registered_budget: bool
    selective_realized: Dict[str, bool]
    obligations_before: Dict[str, Any]
    obligations_after: Dict[str, Any]
    value_delta: Dict[str, Any]
    branch_seed: int

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def branch_future_edit(
    *,
    editor: Any,
    config: Any,
    metric_fn: Any,
    tokens: Dict[str, torch.Tensor],
    candidate_id: str,
    base_snapshot: AdapterSnapshot,
    success_threshold: float = 1.0,
    obligation_groups: Optional[Dict[str, List[Dict[str, torch.Tensor]]]] = None,
    branch_seed: int = 0,
) -> BranchEditResult:
    """Actually execute one future GRACE edit from an exact common state.

    Positive execution is a realizability witness under the registered budget.
    Failure is only a registered-budget failure, never an impossibility claim.
    """
    adapter = get_adapter(editor)
    restore_adapter(adapter, base_snapshot)
    obligation_groups = obligation_groups or {}

    pre_metric = _metric_scalar(metric_fn, editor, tokens)
    ob_before = {k: evaluate_obligation_group(metric_fn, editor, v, success_threshold) for k, v in obligation_groups.items()}
    query = capture_query(editor, tokens)
    route = route_probe(adapter, query, tokens["labels"])
    before = snapshot_adapter(adapter)
    before_summary = snapshot_summary(before)

    start = time.time()
    with isolated_rng(int(branch_seed)):
        editor.edit(config, tokens, batch_history=[])
    elapsed = time.time() - start

    post_metric = _metric_scalar(metric_fn, editor, tokens)
    ob_after = {k: evaluate_obligation_group(metric_fn, editor, v, success_threshold) for k, v in obligation_groups.items()}
    after = snapshot_adapter(adapter)
    after_summary = snapshot_summary(after)
    edit_loss = None
    if hasattr(editor, "loss"):
        try:
            edit_loss = float(editor.loss.detach().cpu().item())
        except Exception:
            pass
    loss_trajectory: List[float] = []
    if hasattr(editor, "losses"):
        for x in editor.losses:
            try:
                loss_trajectory.append(float(np.asarray(x).mean()))
            except Exception:
                pass

    target_realized = post_metric >= success_threshold
    selective = {
        name: bool(target_realized and stats["all_satisfied"])
        for name, stats in ob_after.items()
    }

    result = BranchEditResult(
        candidate_id=candidate_id,
        pre_metric=pre_metric,
        post_metric=post_metric,
        route_before=route.to_dict(),
        elapsed_seconds=elapsed,
        nkeys_before=before_summary["nkeys"],
        nkeys_after=after_summary["nkeys"],
        eps_before=before_summary["epsilons"],
        eps_after=after_summary["epsilons"],
        edit_loss=edit_loss,
        loss_trajectory=loss_trajectory,
        target_realized_under_registered_budget=bool(target_realized),
        selective_realized=selective,
        obligations_before=ob_before,
        obligations_after=ob_after,
        value_delta=value_delta_summary(before, after),
        branch_seed=int(branch_seed),
    )
    restore_adapter(adapter, base_snapshot)
    return result


def commit_anchor_write(editor: Any, config: Any, tokens: Dict[str, torch.Tensor], seed: int = 0) -> AdapterSnapshot:
    with isolated_rng(int(seed)):
        editor.edit(config, tokens, batch_history=[])
    return snapshot_adapter(get_adapter(editor))