# OACR-R4 Geographical-Feature Split-Stage Rerun Record — 2026-09-29

## Status

The frozen R4-v2 geographical-feature job in run 36438278451 completed the scientific producer but was cancelled during the independent verifier because the combined producer+verifier wall time exceeded the hosted-runner job limit.

This is an engineering completion failure, not a scientific protocol change.

## Observed producer result before cancellation

Frozen root:

Q618123 — geographical feature.

The producer completed and reported:

- status: INCLUDED;
- states: 272;
- operational blocks: 24;
- active augmented states: 23;
- inactive augmented states: 248;
- native replay mismatches: 0;
- Rgate exact partition match: true.

The verifier did not finish and the artifact upload step was skipped.

Therefore this root is not yet accepted.

## Allowed clean completion

Re-execute the **unchanged authoritative R4-v2 protocol** for the same frozen root, but split execution into two jobs:

1. producer + artifact upload;
2. independent verifier after downloading the producer artifact.

No scientific parameter changes are authorized.

Fixed authority remains:

docs/OACR_R4_V2_PAGINATED_REDESIGN_PROTOCOL.md

commit:

6795a534415e4f7270f2b25aca3522b653e413d3

The split-stage rerun must preserve:

- root Q618123;
- page size 2000;
- max pages 20;
- exact producer implementation;
- exact state/action selection;
- exact Rgate transform;
- exact verifier implementation.

Acceptance requires the second job verifier to return PASS.
