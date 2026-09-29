# OACR-R4 Producer Engineering Optimization Record — 2026-09-29

## Status

This record authorizes a performance-only producer optimization for clean reruns of the already frozen R4-v2 protocol.

Scientific authority remains:

docs/OACR_R4_V2_PAGINATED_REDESIGN_PROTOCOL.md

commit:

6795a534415e4f7270f2b25aca3522b653e413d3

No root, retrieval rule, state bank, action panel, representation, metric, or verifier rule changes.

## 1. Bottleneck in the frozen producer

For every registered state/action cell, the v2 producer currently computes:

1. the original post-deletion closure;
2. the decoded Rgate post-deletion closure.

With 272 states and 64 actions this produces approximately:

\[
2\times272\times64=34{,}816
\]

closure computations, in addition to base/action setup.

This causes large fresh roots to approach the hosted-runner wall-time limit.

## 2. Exact Rgate identities

The frozen Rgate representation has only two decoded cases.

### Active delta state

If state G+e is contract-active, Rgate retains e.

Therefore the decoded graph is exactly the original graph:

\[
\mathrm{decode}(R_{\rm gate}(G+e))=G+e.
\]

For every registered action f, the compressed outcome is therefore literally identical to the already computed original outcome.

No second closure execution is needed in the producer.

### Base or inactive delta state

If state is base G or an inactive G+e, Rgate decodes to G.

The producer already computes and freezes for every registered deletion f:

\[
TC(G-f)
\]

as base_after[f] before any augmented-state outcome is executed.

Therefore the decoded compressed outcome for every base/inactive state is exactly the corresponding already-native-computed base_after[f] signature.

## 3. What remains executed

The optimized producer still executes the complete original state/action matrix:

\[
272\times64=17{,}408
\]

native deletion/closure computations for every INCLUDED carrier.

Thus operational partition, action-content analysis, and all original outcomes are still derived from full native execution.

Only duplicate compressed-side calculations are reused from exact graph identity or the already-native base-after-action result.

## 4. Independent verifier unchanged

The authoritative independent verifier remains:

experiments/oacr_r4/verify_paginated_relational_redesign_v2.py

It is not optimized by this change.

The verifier independently reconstructs:

- pages and combined carrier;
- state/action selection;
- active classification;
- original state/action outcomes;
- decoded compressed state/action outcomes;
- partition diagnostics and secondary analyses.

Therefore final acceptance still requires a full independent replay path.

## 5. Scientific interpretation

This optimization changes runtime only.

It must not be described as additional evidence.

Any clean rerun using the optimized producer is accepted only if the unchanged independent verifier returns PASS.
