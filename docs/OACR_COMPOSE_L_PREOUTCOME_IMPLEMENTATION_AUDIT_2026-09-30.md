# OACR-COMPOSE-L Recovery Hysteresis — Pre-outcome Implementation Audit

**Date:** 2026-09-30  
**Scientific protocol commit:** \`e1d00a7bb57d30ef2d49eb667dbcd6fd7f0d1e8f\`  
**Producer commit:** \`b01ec50a3e396bccb6ec75840811167609119025\`  
**Artifact verifier commit:** \`9bc6d31bc7981a6cb95b95446d2aff54b5ca5c7d\`  
**Corrected workflow commit:** \`b7d546ad06e02ebe7d9d7c4cdd08888e5f91df0e\`  
**Status:** audited before any producer invocation in the corrected prospective run

## 1. Outcome-blind construction

The producer freezes from the untouched base state, before any recovery candidate write:

1. 512 base-misclassified future-bank examples;
2. three deterministic label-balanced future action IDs;
3. 256 base-correct anchor candidate IDs;
4. 32 sentinels outside future and anchor banks.

No future write is executed during any of these selections.

## 2. Recovery path

For each anchor candidate the implementation:

1. restores the exact base target-parameter tensor;
2. applies native Finetune to the same text under deterministic counterfactual label
   \[
   y^+=(y+1)\bmod K;
   \]
3. requires the counterfactual target to be realized and the parameter hash to change;
4. without resetting, applies native Finetune to the same text under original label \(y\);
5. requires original target realization;
6. compares the complete pair-specific current task READ against the corresponding base READ;
7. requires recovered parameter hash to differ from base.

There is no custom inverse update, interpolation, direct optimizer reversal, or parameter restoration inside the recovery path.

## 3. State-bank freeze before future outcomes

A recovery candidate is retained using only:

- forward/counter-edit realization;
- current READ equality;
- parameter inequality;
- finite-tensor check;
- repeated non-mutating READ consistency.

The implementation scans until:

- four recovered states are retained; or
- all 256 frozen anchor candidates are exhausted.

Only **after** this loop finishes does the future-write loop begin.

Therefore no future response affects:

- whether a recovery state is accepted;
- which recovery states are retained;
- when state-bank construction stops.

## 4. Future probe

For every retained recovered state and the base state, the same three already frozen future writes are executed from exact pre-write tensors.

Primary separation uses only:

- native write status;
- target realization;
- exact task-level READ tuples.

Diagnostic logit equality is recorded separately and does not control the primary positive.

## 5. Artifact verifier boundary

The artifact verifier checks:

- protocol/commit identity;
- bank sizes and disjointness;
- accepted-attempt/recovered-state correspondence;
- exact root-task equality for recovered states;
- parameter hash inequality;
- future action IDs and branch counts;
- separation-count bookkeeping;
- non-target parameter invariance.

It is an artifact-structure verifier, not an independent native scientific replay.

Any positive requires the separately frozen targeted fresh native replay specified by the scientific protocol.

## 6. First workflow attempt

Initial run \`36657010957\` failed at the asset-path test before producer invocation because workflow expressions retained a leading backslash.

Thus no scientific outcome was exposed before this audit.

The corrected prospective run is triggered separately after workflow repair.

## 7. Governance

After the corrected run enters the producer:

- no future IDs may change;
- no anchor/sentinel rule may change;
- no recovery acceptance rule may change;
- no counterfactual-label rule may change;
- no primary separation metric may change;
- no fold may be replaced.

Any engineering failure is repaired separately and documented without altering these rules.
