"""Executable OACR bridge verifier for the SQEC multistep-legality H1= -> H2+ mechanism.

This is a retrospective reproduction of an already executed controlled SQEC result.
It does not constitute a prospective natural COMPOSE experiment.
"""
from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sqec_core", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    core = Path(args.sqec_core).resolve()
    sys.path.insert(0, str(core))

    from dynamic_qualification_frontier import (  # type: ignore
        apply_qualification_event,
        initial_dynamic_snapshot,
    )
    from stochastic_multistep_legality import (  # type: ignore
        build_controlled_stochastic_legality_problem,
        compile_stochastic_legality_projection,
        project_stochastic_legality,
        solve_explicit_stochastic_policy_oracle,
        verify_stochastic_legality,
    )

    full = build_controlled_stochastic_legality_problem()
    projected = project_stochastic_legality(full)

    full0 = initial_dynamic_snapshot(full.model)
    proj0 = initial_dynamic_snapshot(projected.model)

    first_step_checks = []

    # All registered deterministic actions.
    for fopt, popt in zip(full.actions, projected.actions):
        if fopt.name != popt.name:
            raise RuntimeError("action catalogue mismatch")
        fpost = apply_qualification_event(full.model, full0, fopt.event)
        ppost = apply_qualification_event(projected.model, proj0, popt.event)
        same = (
            fpost.atom_statuses == ppost.atom_statuses
            and fpost.joint_state == ppost.joint_state
            and fopt.cost == popt.cost
        )
        first_step_checks.append({
            "kind": "action",
            "name": fopt.name,
            "same_immediate_transition": same,
        })

    # Every registered stochastic observation outcome is individually legal at H0
    # and has the same transition effect in full/projected representations.
    if len(full.observation.outcomes) != len(projected.observation.outcomes):
        raise RuntimeError("observation outcome catalogue mismatch")
    for fout, pout in zip(full.observation.outcomes, projected.observation.outcomes):
        if fout.label != pout.label:
            raise RuntimeError("observation label mismatch")
        fpost = apply_qualification_event(full.model, full0, fout.event)
        ppost = apply_qualification_event(projected.model, proj0, pout.event)
        same = (
            fpost.atom_statuses == ppost.atom_statuses
            and fpost.joint_state == ppost.joint_state
            and fout.probability == pout.probability
        )
        first_step_checks.append({
            "kind": "observation_outcome",
            "name": fout.label,
            "same_immediate_transition": same,
        })

    h1_equivalent = all(x["same_immediate_transition"] for x in first_step_checks)

    full_commit = next(x for x in full.actions if x.name == "commit-task")
    proj_commit = next(x for x in projected.actions if x.name == "commit-task")
    full_after_commit = apply_qualification_event(full.model, full0, full_commit.event)
    proj_after_commit = apply_qualification_event(projected.model, proj0, proj_commit.event)

    if full_after_commit.atom_statuses != proj_after_commit.atom_statuses:
        raise RuntimeError("shared commit does not reach the same latent state")

    full_obs = full.observation.outcomes[0].event
    proj_obs = projected.observation.outcomes[0].event

    full_second_legal = True
    full_second_error = None
    try:
        apply_qualification_event(full.model, full_after_commit, full_obs)
    except ValueError as exc:
        if "is illegal" not in str(exc):
            raise
        full_second_legal = False
        full_second_error = str(exc)

    projected_second_legal = True
    try:
        projected_second = apply_qualification_event(
            projected.model, proj_after_commit, proj_obs
        )
        projected_second_state = str(projected_second.joint_state)
    except ValueError as exc:
        projected_second_legal = False
        projected_second_state = str(exc)

    h2_divergent = (
        h1_equivalent
        and not full_second_legal
        and projected_second_legal
    )

    certificate = compile_stochastic_legality_projection(full)
    verified, verify_message = verify_stochastic_legality(full, certificate)
    oracle = solve_explicit_stochastic_policy_oracle(full)

    if certificate.replay_regret != Fraction(46, 5):
        raise RuntimeError(f"unexpected replay regret: {certificate.replay_regret}")
    if oracle.complete_trees_enumerated != 34:
        raise RuntimeError(
            f"unexpected explicit policy-tree count: {oracle.complete_trees_enumerated}"
        )

    payload = {
        "bridge": "OACR_SQEC_MULTISTEP_LEGALITY_DEPTH2_V1",
        "sqec_commit_expected": "1111368c37b8e00d04ade5456e3d59070465c3ff",
        "status": "PASS_CONTROLLED_D1_EQUAL_D2_DIVERGENT" if h2_divergent and verified else "FAIL",
        "H1_complete_registered_primitive_interface_equal": h1_equivalent,
        "H1_checks": first_step_checks,
        "shared_commit_successor_equal": (
            full_after_commit.atom_statuses == proj_after_commit.atom_statuses
        ),
        "H2_sequence": ["commit-task", "observe-qualified"],
        "full_H2_second_step_legal": full_second_legal,
        "full_H2_error": full_second_error,
        "projected_H2_second_step_legal": projected_second_legal,
        "projected_H2_second_step_state": projected_second_state,
        "H2_divergent": h2_divergent,
        "full_expected_objective": str(certificate.full_policy.expected_objective),
        "projected_policy_expected_objective": str(certificate.projected_policy.expected_objective),
        "projected_policy_full_replay_objective": str(certificate.projected_replay_objective),
        "replay_regret": str(certificate.replay_regret),
        "explicit_policy_trees_enumerated": oracle.complete_trees_enumerated,
        "certificate_verified": verified,
        "certificate_verifier_message": verify_message,
        "claim_boundary": {
            "prospective_OACR_discovery": False,
            "controlled_mechanism_reproduction": True,
            "natural_carrier_claim": False,
            "optimizer_novelty_claim": False,
        },
    }

    if payload["status"] != "PASS_CONTROLLED_D1_EQUAL_D2_DIVERGENT":
        raise RuntimeError(json.dumps(payload, indent=2))

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2))
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
