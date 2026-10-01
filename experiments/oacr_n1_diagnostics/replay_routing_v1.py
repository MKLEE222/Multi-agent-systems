"""Observer-only retrospective routing replay of the recorded eight-unit smoke.

The inherited constructor is imported without modification. Diagnostic hooks
read activations and codebook entries, perform no random draws or state writes,
and must reproduce every recorded prediction before interpreting telemetry.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys

import torch

SOURCE_DIR = Path(__file__).resolve().parents[1] / "oacr_natural_learned"
sys.path.insert(0, str(SOURCE_DIR))
import run_n1_dev_only as runner

RUNNER_SHA256 = "928aa6434bc4b31fa2e011f15f2d0e1be05fe7a7e04b37df0332941d0b98e91b"
REFERENCE_SHA256 = "6d8267b2da83c30ba871cc02c34b97d6f858b0b6661611cf63d7be369c6a19c3"
VARIANTS = ("B0_base", "B1_predictive", "B2_sham", "A0_oracle")


def codebook_digest(adapter):
    digest = hashlib.sha256()
    for tensor in (adapter.keys, adapter.values, adapter.epsilons):
        digest.update(tensor.detach().cpu().contiguous().numpy().tobytes())
    for label in adapter.key_labels:
        if torch.is_tensor(label):
            digest.update(label.detach().cpu().contiguous().numpy().tobytes())
        else:
            digest.update(repr(label).encode())
    return digest.hexdigest()


class RoutingObserver:
    def __init__(self, adapter):
        self.adapter = adapter
        self.rows = []
        self.pending = None
        self.handles = []

    def before(self, module, args):
        with torch.no_grad():
            x = args[0]
            token = min(module.key_id, x.shape[1] - 1)
            q = x[:, token, :]
            distances = torch.cdist(module.keys, q, p=2).view(-1)
            closest = int(distances.argmin().item())
            radii = module.epsilons.reshape(-1)
            distance, radius = float(distances[closest]), float(radii[closest])
            # Registered T5 wo is an ordinary Linear. This diagnostic arithmetic
            # is not an extra native model forward and consumes no random draws.
            vanilla = torch.nn.functional.linear(x, module.layer.weight, module.layer.bias)
            self.pending = (vanilla, {
                "nearest_key": closest, "nearest_distance": distance,
                "nearest_radius": radius, "gate_active": distance <= radius,
                "auxiliary_selected": closest > 0,
                "auxiliary_active": closest > 0 and distance <= radius,
                "all_key_distances": distances.cpu().tolist(),
                "all_key_radii": radii.cpu().tolist(),
                "sequence_length": x.shape[1], "query_token": int(token),
                "replacement_mode": module.replacement,
                "copied_values_equal_base": bool(torch.equal(
                    module.values.detach(), module.values[0:1].detach().expand_as(module.values))),
            })

    def after(self, module, args, output):
        if self.pending is None:
            raise RuntimeError("observer lost pre-forward telemetry")
        vanilla, row = self.pending
        row["actual_chosen_key"] = int(module.chosen_key.reshape(-1)[0].item())
        row["output_change_l2"] = float(torch.linalg.vector_norm(output.detach() - vanilla).item())
        assert row["actual_chosen_key"] == row["nearest_key"]
        self.rows.append(row)
        self.pending = None

    def __enter__(self):
        self.handles = [self.adapter.register_forward_pre_hook(self.before),
                        self.adapter.register_forward_hook(self.after)]
        return self

    def __exit__(self, *args):
        for handle in self.handles:
            handle.remove()


def compare_reports(reference, replay):
    errors = []
    if reference["summary"] != replay["summary"]:
        errors.append("summary differs")
    if reference["units"] != replay["units"]:
        errors.append("unit results differ")
    return errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--grace_repo", required=True)
    parser.add_argument("--model_dir", required=True)
    parser.add_argument("--reference_report", required=True, type=Path)
    parser.add_argument("--replay_out", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    if hashlib.sha256((SOURCE_DIR / "run_n1_dev_only.py").read_bytes()).hexdigest() != RUNNER_SHA256:
        raise RuntimeError("inherited constructor changed")
    if hashlib.sha256(args.reference_report.read_bytes()).hexdigest() != REFERENCE_SHA256:
        raise RuntimeError("wrong reference report")
    if args.replay_out.resolve() == args.reference_report.resolve():
        raise RuntimeError("reference output is immutable")
    reference = json.loads(args.reference_report.read_text())
    assert reference["summary"]["complete_units"] == 8
    observed = []
    original_evaluate = runner.evaluate

    def evaluate(editor, queries):
        call = len(observed)
        adapter = runner.get_adapter(editor)
        before = codebook_digest(adapter)
        with RoutingObserver(adapter) as observer:
            result = original_evaluate(editor, queries)
        assert codebook_digest(adapter) == before, "native inference/observer mutated stored codebook"
        assert len(observer.rows) == len(result["rows"]), "expected one registered encoder call per query"
        observed.append({
            "unit_id": reference["units"][call // 4]["unit_id"],
            "variant": VARIANTS[call % 4],
            "queries": [{"criterion": row["criterion"], "prompt": row["prompt"],
                         "prediction": row["prediction"], "pass": row["pass"], "routing": telemetry}
                        for row, telemetry in zip(result["rows"], observer.rows)],
        })
        return result

    runner.evaluate = evaluate
    original_argv = sys.argv
    sys.argv = [str(SOURCE_DIR / "run_n1_dev_only.py"),
                "--manifest", args.manifest, "--grace_repo", args.grace_repo,
                "--model_dir", args.model_dir, "--out", str(args.replay_out),
                "--limit", "8", "--max_aux", "2", "--n_iter", "100", "--device", "cpu"]
    try:
        runner.main()
    finally:
        runner.evaluate = original_evaluate
        sys.argv = original_argv
    replay = json.loads(args.replay_out.read_text())
    errors = compare_reports(reference, replay)
    totals = {}
    for variant in VARIANTS:
        counts = Counter()
        distances = []
        for panel in observed:
            if panel["variant"] != variant:
                continue
            for query in panel["queries"]:
                row = query["routing"]
                counts["queries"] += 1
                counts["any_gate_active"] += row["gate_active"]
                counts["auxiliary_active"] += row["auxiliary_active"]
                counts["adapter_changed_output"] += row["output_change_l2"] > 0
                distances.append(row["nearest_distance"])
        totals[variant] = dict(counts, min_nearest_distance=min(distances), max_nearest_distance=max(distances))
    report = {
        "protocol": "OACR_N1_OBSERVER_ROUTING_REPLAY_V1",
        "authority": "retrospective development diagnosis; no new confirmatory outcomes",
        "evaluation_units_loaded": 0, "reference_run": 36824729008,
        "reference_report_sha256": REFERENCE_SHA256,
        "inherited_runner_sha256": RUNNER_SHA256,
        "replay_exact": not errors, "replay_errors": errors,
        "summary": totals, "observations": observed,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"replay_exact": not errors, "routing": totals}, indent=2))
    if errors:
        raise SystemExit("replay differs: telemetry has no failure-localization authority")


if __name__ == "__main__":
    main()
