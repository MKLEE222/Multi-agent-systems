"""Independent OACR COMPOSE checker for the pre-existing SQEC retained-route micro-world.

This checker is intentionally producer-independent.  It does not import SQEC
helpers.  It reconstructs only the frozen transition semantics needed to test
whether a hidden qualification coordinate is inert for every primitive at
depth 1 but consequential under a depth-2 composition.

Status: retrospective controlled bridge witness, not prospective discovery.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Tuple

ACTION_OPEN = "action-open"
SATISFIED = "satisfied"
UNKNOWN = "unknown"
CLOSED = "closed"

COMMIT = "commit-task"
OBSERVE = "observe-semantics"
RETAIN = "retain-observation-route"
ACTIONS = (COMMIT, OBSERVE, RETAIN)


@dataclass(frozen=True)
class State:
    task_done: str
    latent_semantics: str
    observation_route: str


def read(state: State) -> str:
    """Reconstruct the SQEC joint qualification state for the claim route.

    The registered claim route depends on task_done and latent_semantics.
    observation_route is a legality coordinate for the observation event, not
    a direct claim-route coordinate.
    """
    values = (state.task_done, state.latent_semantics)
    if CLOSED in values:
        return "blocked"
    if all(v == SATISFIED for v in values):
        return "qualified"
    if UNKNOWN in values:
        return "epistemically-open"
    return "action-open"


def legal_actions(state: State) -> Tuple[str, ...]:
    out = [COMMIT, RETAIN]
    if state.observation_route in (ACTION_OPEN, SATISFIED):
        out.append(OBSERVE)
    return tuple(sorted(out))


def apply(state: State, action: str) -> State:
    if action not in legal_actions(state):
        raise ValueError(f"illegal action {action}")

    if action == COMMIT:
        task = SATISFIED if state.task_done == ACTION_OPEN else state.task_done
        route = CLOSED if state.observation_route == ACTION_OPEN else state.observation_route
        return State(task, state.latent_semantics, route)

    if action == OBSERVE:
        latent = SATISFIED if state.latent_semantics == UNKNOWN else state.latent_semantics
        return State(state.task_done, latent, state.observation_route)

    if action == RETAIN:
        route = SATISFIED if state.observation_route == ACTION_OPEN else state.observation_route
        return State(state.task_done, state.latent_semantics, route)

    raise ValueError(action)


def sigma1(state: State) -> Dict:
    current_legal = legal_actions(state)
    return {
        "read": read(state),
        "legal_actions": list(current_legal),
        "one_step_read": {
            action: read(apply(state, action))
            for action in current_legal
        },
    }


def sequence_signature(state: State, sequence: Tuple[str, ...]) -> Dict:
    cur = state
    reads = [read(cur)]
    for action in sequence:
        if action not in legal_actions(cur):
            return {
                "legal": False,
                "failed_action": action,
                "reads": reads,
                "terminal_read": read(cur),
            }
        cur = apply(cur, action)
        reads.append(read(cur))
    return {
        "legal": True,
        "failed_action": None,
        "reads": reads,
        "terminal_read": read(cur),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    x = State(ACTION_OPEN, UNKNOWN, ACTION_OPEN)
    y = apply(x, RETAIN)

    s1_x = sigma1(x)
    s1_y = sigma1(y)
    assert read(x) == read(y) == "epistemically-open"
    assert legal_actions(x) == legal_actions(y) == tuple(sorted(ACTIONS))
    assert s1_x == s1_y

    pairs = []
    divergences = []
    for a1 in ACTIONS:
        for a2 in ACTIONS:
            seq = (a1, a2)
            sx = sequence_signature(x, seq)
            sy = sequence_signature(y, seq)
            row = {
                "sequence": list(seq),
                "x": sx,
                "y": sy,
                "diverges": sx != sy,
            }
            pairs.append(row)
            if sx != sy:
                divergences.append(row)

    target = next(
        row for row in divergences
        if row["sequence"] == [COMMIT, OBSERVE]
    )
    assert target["x"]["legal"] is False
    assert target["x"]["failed_action"] == OBSERVE
    assert target["y"]["legal"] is True
    assert target["y"]["terminal_read"] == "qualified"

    # Independent projection-side corollary: removing only the observation
    # precondition is invisible at the initial primitive boundary but makes
    # COMMIT -> OBSERVE spuriously executable.
    projection_corollary = {
        "initial_observation_precondition_satisfied": OBSERVE in legal_actions(x),
        "after_commit_full_observation_legal": OBSERVE in legal_actions(apply(x, COMMIT)),
        "after_commit_legality_blind_projection_observation_legal": True,
    }
    assert projection_corollary == {
        "initial_observation_precondition_satisfied": True,
        "after_commit_full_observation_legal": False,
        "after_commit_legality_blind_projection_observation_legal": True,
    }

    payload = {
        "protocol": "OACR_COMPOSE_SQEC_RETAINED_ROUTE_BRIDGE_V1",
        "status": "RETROSPECTIVE_CONTROLLED_BRIDGE_WITNESS",
        "source_semantics": {
            "repository": "MKLEE222/qualification_opportunity_compiler",
            "source_module": "02_core/multistep_observation_legality.py",
            "source_test": "02_core/test_multistep_observation_legality.py",
        },
        "state_x": asdict(x),
        "state_y": asdict(y),
        "hidden_difference": {
            "coordinate": "observation_route",
            "x": x.observation_route,
            "y": y.observation_route,
        },
        "sigma1_x": s1_x,
        "sigma1_y": s1_y,
        "sigma1_equal": s1_x == s1_y,
        "depth2_sequences_checked": len(pairs),
        "depth2_divergence_count": len(divergences),
        "depth2_divergences": divergences,
        "target_witness": target,
        "projection_corollary": projection_corollary,
        "accepted_interpretation": (
            "A hidden qualification coordinate can be inert under the complete "
            "registered primitive boundary at depth 1 yet determine whether a "
            "shared second operation is legal after a first operation."
        ),
        "boundary": [
            "controlled micro-world",
            "retrospective bridge reconstruction",
            "not a natural-carrier prevalence claim",
            "not a claim that composition or modal-depth equivalence is novel",
            "not yet a cross-substrate COMPOSE result",
        ],
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True))
    print(json.dumps({
        "sigma1_equal": payload["sigma1_equal"],
        "depth2_sequences_checked": payload["depth2_sequences_checked"],
        "depth2_divergence_count": payload["depth2_divergence_count"],
        "target_sequence": payload["target_witness"]["sequence"],
        "x_target_legal": payload["target_witness"]["x"]["legal"],
        "y_target_legal": payload["target_witness"]["y"]["legal"],
        "y_target_terminal_read": payload["target_witness"]["y"]["terminal_read"],
    }, indent=2))


if __name__ == "__main__":
    main()
