# OACR-COMPOSE-L Positive Promotion Rule v1

**Date:** 2026-09-30  
**Status:** frozen while the first corrected prospective recovery-hysteresis producer run is still in progress and before any fold outcome is inspected  
**Source protocol:** \`OACR_COMPOSE_L_RECOVERY_HYSTERESIS_V1\`

## 1. Purpose

If the prospective 8-fold recovery-hysteresis run produces one or more future-response separations, the project must not choose the most visually dramatic witness for promotion.

This record freezes deterministic witness selection before outcome.

## 2. Eligible positive witness

A witness is eligible only if its producer artifact and structural verifier establish:

1. recovery state accepted under the frozen recovery gate;
2. root/current primary task READ exactly equals the corresponding base READ;
3. recovered target-parameter hash differs from base;
4. a frozen future action is executed from both exact pre-write states;
5. primary future relation separates by native status/target realization and/or exact task READ.

No diagnostic-logit-only difference is eligible for primary promotion.

## 3. Deterministic witness selection

Across all verified fold artifacts:

1. choose the numerically smallest fold containing at least one eligible future separation;
2. within that fold choose the numerically smallest \`anchor_id\` among recovered states with a separation;
3. for that anchor choose the numerically smallest frozen \`action_id\` whose future branch separates.

This yields one primary replication target:

\[
(f^\*,a^\*,w^\*).
\]

No severity, number of differing panel entries, logit magnitude, or parameter distance affects selection.

## 4. Fresh targeted replay requirement

Before any positive claim is promoted, a new targeted replay protocol must be committed.

The replay must:

- initialize a fresh model/editor;
- reconstruct the same base state from frozen model bytes;
- reconstruct the fold-specific future/anchor/sentinel banks by the original deterministic rules;
- reproduce the exact forward counterfactual edit and counter-edit for \(a^\*\);
- require root task READ recovery and parameter inequality again;
- execute the same frozen future action \(w^\*\) from base and recovered states;
- require the same primary future separation type.

It must not load producer parameter tensors.

Two fresh reconstructions are required for deterministic promotion.

## 5. Secondary positives

Other separating folds/anchors/actions remain in the full outcome matrix and may be reported descriptively.

They cannot replace the primary target if the deterministic primary replay fails.

A primary replay failure downgrades the discovery and triggers a scientific/engineering audit; it does not authorize selecting the next positive witness.

## 6. Zero-result handling

If the aggregate has zero future separations, this document has no effect on negative/underpower classification.

Those dispositions remain governed by the already frozen aggregate rules.
