# OACR-L1b Protocol v1 — Collision-Dense Learned Horizon Audit

**Date:** 2026-09-28
**Status:** prospectively frozen before any L1b future-write outcome is inspected
**Carrier:** official GRACE commit f674183f17a995d109e10ee6140d4c3e6d016115 + frozen SCOTUS/BERT carrier
**Role:** replace the five-pair L1 diagnostic with a collision-dense, state-diverse learned audit without tuning for a positive result.

## 1. Why L1b is needed

L1 completed cleanly but produced only:

- 2 states per seed;
- 1 H0 collision pair per seed;
- one anchor candidate per seed;
- the same anchor dataset index 78;
- the same native anchor mode add_far;
- the same future action IDs 12, 15, 17.

All anchor attempts succeeded and preserved the seed contract.

Therefore the primary bottleneck was not write failure. It was **selection degeneracy**: the protocol selected at most one anchor per native mode, while the frozen candidate banks exposed only one mode.

L1b changes state/action sampling before any future-write outcome is inspected.

## 2. Registered seeds

Use eight new global seeds not used in L1:

\[
\{509,601,709,809,907,1009,1201,1409\}.
\]

No seed is dropped because its result is negative.

## 3. Base persistent state

Per seed:

- construct exactly 4 contract-preserving seed edits;
- scan limit: 1024;
- use the same rollback discipline as L1;
- freeze the resulting base adapter snapshot.

If 4 protected seed obligations cannot be constructed within the scan limit, the seed is an infrastructure/state-construction failure and is retained as such.

## 4. Natural error census

From the first index after the seed-construction scan, collect the first 512 natural model errors.

For every candidate, before any anchor or future-write execution:

- capture query embedding;
- native GRACE route mode;
- retrieval margin / add-far margin already exposed by the native probe;
- label;
- dataset index.

Report the complete route-mode census.

No candidate is removed because its mode is common.

## 5. Outcome-blind anchor-candidate selection

Freeze 24 candidate anchors from the 512-error census.

### Phase A — native-mode coverage

Registered native mode order:

1. reuse_same_label;
2. expand_same_label;
3. add_conflict_split;
4. add_far.

For each mode, take up to four candidates using the same mode-internal structural ordering as L1:

- reuse_same_label / expand_same_label: ascending absolute retrieval-margin distance to the native boundary;
- add_conflict_split: ascending absolute add-far margin;
- add_far: ascending add-far margin;
- dataset index tie-break.

### Phase B — query-space diversity fill

If fewer than 24 candidates were selected:

1. use all remaining census candidates;
2. initialize with the lowest dataset index if the selected set is empty;
3. repeatedly select the candidate maximizing its minimum Euclidean query-embedding distance to the already selected anchor set;
4. tie-break by dataset index;
5. stop at 24 or census exhaustion.

This phase is structural and outcome-blind.

All 24 IDs are frozen before any anchor write outcome is inspected.

## 6. Outcome-blind future-action selection

Future actions must be disjoint from **all 24 frozen anchor candidate IDs**, not merely from anchors that later survive.

From remaining census candidates, select exactly four actions.

### Phase A — mode coverage

Take at most one candidate from each registered native mode, in the same mode order and deterministic mode-internal ordering.

### Phase B — query-space diversity fill

If fewer than four were selected, fill by farthest-first query-embedding distance from the already selected future actions, tie-breaking by dataset index.

The same four action examples and ordering apply to every retained initial state within the seed.

If fewer than four disjoint future actions exist, the seed is underpowered and no action IDs are changed post hoc.

## 7. Frozen READ panel

Before any anchor write is executed, freeze:

- 4 protected seed obligations;
- the 4 future-action examples;
- 24 deterministic sentinels, chosen by ascending dataset index while excluding seed, all 24 anchor-candidate, and future-action IDs.

The anchor target itself is not added to the common READ panel.

For every panel item record the same full logits/probabilities/prediction/target margin/CE path as L1.

Pairwise read matching remains:

\[
\mathrm{atol}=10^{-6},
\qquad
\mathrm{rtol}=10^{-5}.
\]

## 8. H0 collision-clique state construction

Apply each of the 24 frozen anchor candidates **independently to the same base snapshot**, in frozen selection order.

An anchor state is eligible iff:

1. anchor target is realized;
2. all 4 protected seed obligations remain satisfied;
3. its complete frozen READ panel matches the base state;
4. its complete frozen READ panel matches every already retained state under the registered tolerance.

Retain states sequentially until reaching:

- base + 7 anchor states = maximum 8 states.

Thus every retained pair is explicitly checked as an H0 collision.

No future action is executed during state-bank construction.

Report for all 24 attempts:

- target realized;
- protected contract preserved;
- base READ match;
- all-retained-state READ match;
- retained/rejected reason;
- native anchor mode;
- state hash.

The construction acceptance rate is a primary diagnostic.

If fewer than two states survive, retain the seed as an underpowered learned construction; do not tune the tolerance or replace anchors.

## 9. Complete branching through H=2

Registered action alphabet size:

\[
|\mathcal A|=4.
\]

For every retained state execute:

- all four H=1 branches;
- all sixteen ordered H=2 sequences with repetition.

Thus each retained state has:

\[
4+4^2=20
\]

future-write trajectories.

ALREADY_SATISFIED_ZERO_WRITE remains an explicit branch status.

Second-step execution is not conditioned on first-step protected-contract success.

## 10. RNG discipline

For fixed global seed:

- anchor RNG: deterministic function of global seed and anchor dataset ID;
- H1 RNG: deterministic function of global seed and action ID;
- H2 RNG: deterministic function of global seed and ordered action pair.

The same branch RNG is used across all initial states for the same registered sequence.

No RNG is searched after observing an outcome.

## 11. Behavioral equivalence

### H0

Retained state bank is constructed as a complete pairwise H0 collision clique.

### H1

A pair remains equivalent iff for every action:

- branch status matches;
- target-realization bit matches;
- protected-contract satisfaction bit matches;
- complete post-action READ family matches.

### H2

Require H1 equivalence and the same conditions for all 16 ordered action pairs.

Report:

- pairwise equivalence matrices;
- first separation horizon;
- complete transitivity audit;
- partition counts \(N_H\) only if the corresponding relation is transitive.

No tolerance-connected-component shortcut is permitted.

## 12. Candidate internal representations

Retain L1 candidate feature families:

- F1: root native update-mode vector over four actions;
- F2: F1 + full root route/coverage + protected-route signatures;
- F3: F2 + projected structural-effect certificates.

For every H0 collision pair report:

- feature under-refinement if feature merges a pair separated by H1/H2;
- feature over-refinement if feature separates a pair behaviorally equivalent through H2.

No feature is declared universally necessary.

## 13. Determinism controls

Per seed require:

1. duplicate replay of base + first H1 action;
2. duplicate replay of first retained non-base state + first H1 action when such a state exists;
3. duplicate replay of base + first registered H2 action pair.

Each duplicate must match:

- branch status;
- target/protected status;
- complete registered READ family;
- resulting state hash.

Failure invalidates the seed run.

## 14. Scale and interpretation

Maximum per seed:

- 8 states;
- 28 H0 collision pairs;
- 4 actions;
- 20 action trajectories/state.

Across 8 seeds maximum:

- 64 states;
- 224 within-seed H0 collision pairs.

Actual achieved scale is reported, not assumed.

### Positive learned horizon evidence

Any prospectively registered H0 collision pair that separates at H1 or H2 is retained and audited.

### Negative learned horizon evidence

If no pair separates, report the negative together with:

- total H0 collision pairs;
- route-mode census;
- state-construction acceptance rate;
- action diversity;
- achieved branch count.

No positive result is required.

## 15. Boundaries

L1b still tests one learned write ecology: routed external memory in official GRACE.

It does not replace the requirement for a second materially different learned persistent-write mechanism.

L1b may establish a stronger negative or a prospective positive for this mechanism, but not a universal learned-representation law.
