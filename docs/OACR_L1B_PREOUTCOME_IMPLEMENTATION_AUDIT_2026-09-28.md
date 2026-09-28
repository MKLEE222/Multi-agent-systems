# OACR-L1b Pre-Outcome Implementation Audit — 2026-09-28

## Status

This audit is performed after the L1b protocol and implementation were committed, but before any L1b scientific outcome has been inspected.

Protocol authority:

docs/OACR_L1B_COLLISION_DENSE_GRACE_H2_PROTOCOL_V1.md

commit:

694d42e92a152c09208d23d211942664306b335d

Implementation:

experiments/oacr_l1b/run_grace_h2_collision_dense_v1.py

Verifier:

experiments/oacr_l1b/verify_grace_h2_collision_dense_v1.py

Workflow:

.github/workflows/oacr-l1b-collision-dense-grace-h2.yml

## 1. Frozen seeds

Protocol:

\[
\{509,601,709,809,907,1009,1201,1409\}.
\]

Workflow matrix matches exactly.

No seed-dependent positive-result stopping rule exists.

## 2. Base persistent state

Implementation invokes the same contract-preserving seed-state constructor used by the earlier learned audits with:

- 4 seed edits;
- scan limit 1024;
- registered global seed.

Construction failure is serialized as:

SEED_CONSTRUCTION_FAILURE

with future_outcomes_executed=false.

It is not silently dropped.

## 3. Natural error census

After base construction, implementation collects the first registered candidate bank after the seed scan and enriches each natural error with native route information before anchor/future execution.

The route-mode census is frozen into the artifact.

## 4. Anchor selection

Implementation freezes anchor candidates before any anchor write.

Phase A:

- registered mode order is preserved;
- up to four candidates per mode;
- mode-specific structural sort is applied.

Phase B:

- farthest-first embedding diversity fill;
- outcome-blind;
- dataset-index tie break.

Selected anchor IDs are serialized.

## 5. Future-action selection

Future actions are selected after anchor IDs are frozen but before any anchor write.

The candidate pool excludes **all selected anchor IDs**, not merely anchors later retained.

Verifier requires:

- four unique future IDs;
- zero overlap with anchor IDs.

If four actions cannot be selected, artifact status is:

UNDERPOWERED_FUTURE_ACTIONS

and future_outcomes_executed=false.

## 6. Frozen READ panel

Panel includes:

- protected seed obligations;
- all four future actions;
- deterministic sentinels.

Sentinel exclusion includes:

- seed IDs;
- all frozen anchor-candidate IDs;
- all future-action IDs.

Base READ is measured once and state hash is checked before/after to ensure READ is non-mutating.

## 7. H0 state construction

Every anchor candidate is applied independently:

- adapter is explicitly restored to the same base snapshot before each anchor;
- anchor RNG is a deterministic function of global seed and anchor dataset ID;
- target realization is checked;
- protected contract is checked;
- complete frozen READ panel is compared with base;
- complete frozen READ panel is compared with every already retained state.

Thus retained states form an explicitly checked H0 collision clique.

Capacity is base + at most seven anchors.

All 24 attempts remain in the ledger even after capacity is reached.

If fewer than two states survive:

UNDERPOWERED_STATE_CONSTRUCTION

is retained with future_outcomes_executed=false.

## 8. H1 execution

For every retained state and every frozen action:

- restore exact initial snapshot;
- use the same H1 branch seed across all initial states for the same action;
- record branch status;
- record target-realization bit;
- record protected-contract bit;
- record complete READ family;
- record resulting state hash.

ALREADY_SATISFIED_ZERO_WRITE is explicit.

## 9. H2 execution

For every retained state:

- all four H1 successor snapshots are stored;
- every second action is executed from the corresponding H1 successor;
- all 16 ordered action pairs with repetition are present.

The second step is therefore a true sequential continuation and does not restart from the root state.

Verifier requires the complete 16-sequence key set for every retained state.

## 10. RNG discipline

H1 first-step seed:

deterministic function of global seed and first action ID.

H2 second-step seed:

deterministic function of global seed and ordered action pair.

The same registered sequence receives the same branch RNG across all initial states.

No RNG search is present after outcome observation.

## 11. Behavioral equivalence

H0:

complete READ-family equality under registered tolerances.

H1:

requires H0 plus equality of branch meta-signature and complete post-action READ family for every action.

H2:

requires H1 plus equality of branch meta-signature and complete post-H2 READ family for every ordered pair.

The protocol does not require internal post-state hashes to define behavioral equivalence.

This is correct: state hashes are determinism controls, not registered observable behavior.

## 12. Transitivity

Implementation explicitly constructs pairwise relations at H0/H1/H2 and performs a cubic transitivity audit.

Partition counts are only produced through the equivalence audit.

Verifier rejects any non-transitive horizon relation.

No tolerance-connected-component shortcut is used.

## 13. Candidate representation audit

F1/F2/F3 are measured on the frozen root states and frozen future actions.

Under-/over-refinement is computed only relative to registered H0 collision pairs and H2 behavioral equivalence.

No feature is promoted to universal necessity by implementation.

## 14. Determinism controls

Per retained seed the implementation requires:

- duplicate base + first H1 action;
- duplicate first non-base state + first H1 action when available;
- duplicate base + first registered H2 action pair.

Duplicate comparison includes:

- branch meta-signature;
- complete READ family;
- resulting state hash.

Any failure raises and invalidates the seed run.

## 15. Verifier coverage

The verifier checks, without rerunning GRACE:

- protocol identity;
- allowed underpowered/failure statuses;
- no future outcomes for underpowered/failure artifacts;
- unique/disjoint anchor/future IDs;
- complete anchor-attempt ledger;
- unique state IDs;
- complete pair identities;
- H0 clique;
- complete H1 action set;
- complete H2 16-sequence set;
- state/pair/branch counts;
- transitivity bits;
- duplicate-replay control bits;
- H1/H2 separation summary arithmetic.

## 16. Remaining boundary

The verifier is a structural artifact verifier, not a second independent native GRACE execution.

Therefore a successful L1b run provides:

- prospective learned-carrier execution;
- frozen branching and determinism controls;
- structural artifact audit.

It does not yet provide an independent second implementation of GRACE branch execution.

If L1b yields a scientifically consequential positive separation, an additional targeted native replay audit should be run before promotion.

## 17. Pre-outcome judgment

**Implementation matches the registered L1b scientific design closely enough to run without protocol amendment.**

No result-dependent code correction is authorized unless a future run reveals a pure engineering failure before scientific outcomes are produced.
