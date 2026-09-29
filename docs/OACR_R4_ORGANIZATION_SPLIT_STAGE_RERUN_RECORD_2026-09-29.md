# OACR-R4 Organization Split-Stage Rerun Record — 2026-09-29

## Status

The frozen R4-v2 organization job in run 36438278451 completed the scientific producer but was cancelled during the independent verifier because the combined producer+verifier wall time exhausted the hosted-runner job budget.

This is an engineering completion failure only.

## Producer result before cancellation

Frozen root:

Q43229 — organization.

Producer completed with:

- status: INCLUDED;
- states: 272;
- operational blocks: 26;
- active augmented states: 25;
- inactive augmented states: 246;
- active fraction: 0.09225092250922509;
- native replay mismatches: 0;
- Rgate exact partition match: true.

The independent verifier began but was cancelled before completion.

No artifact upload occurred, so the root is not yet accepted.

## Allowed clean completion

Re-execute the unchanged authoritative R4-v2 protocol for Q43229 using split stages:

1. producer + upload;
2. independent verifier in a second job after downloading the producer artifact.

Scientific authority remains:

docs/OACR_R4_V2_PAGINATED_REDESIGN_PROTOCOL.md

commit:

6795a534415e4f7270f2b25aca3522b653e413d3

No root, page, state, action, representation, or metric rule may change.

Acceptance requires verifier PASS.
