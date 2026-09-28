# OACR-L1 Protocol v1 — Learned Horizon Refinement on Official GRACE + SCOTUS

**Date:** 2026-09-28  
**Status:** preregistered multi-seed horizon experiment  
**Carrier:** official GRACE commit `f674183f17a995d109e10ee6140d4c3e6d016115` + SCOTUS/BERT

## 1. Question

OACR-W1 found registered current-read collisions but no one-step operational divergence in its frozen bank.

L1 asks the sharper horizon question:

[
z_iequiv_0 z_j,qquad
z_iequiv_1 z_j,qquad
z_i
otequiv_2 z_j
]

can occur in the same serious learned writable carrier?

A positive is not required. If the states remain equivalent through (H=2), that negative is retained.

## 2. Frozen state bank per seed

For each registered global seed:

1. build four contract-preserving seed edits exactly as in W1;
2. freeze a natural error bank before anchor outcomes are inspected;
3. preselect at most one anchor candidate from each GRACE native route mode;
4. apply each selected anchor independently to the same base snapshot;
5. retain only anchor states whose target succeeds and whose common seed contract remains satisfied;
6. keep the base state plus the first three contract-valid anchor states in frozen anchor-selection order.

Maximum state-bank size: 4.

The anchor target itself is not included in the common READ contract.

## 3. Frozen observation family

[
mathcal O=
P_{m seed}cup A_{m future}cup S_{m sentinel}.
]

Per seed:

- 4 protected seed obligations;
- 3 frozen future-action targets;
- 16 deterministic non-anchor sentinels.

For every read record full logits/probabilities/prediction/target margin/CE using the existing W1 measurement path.

Pairwise read match uses:

[
mathrm{atol}=10^{-6},qquad
mathrm{rtol}=10^{-5}.
]

This tolerance relation is **not assumed transitive**. Therefore L1 reports pairwise (H)-equivalence first. A partition size (N_H) is reported only if the complete pairwise relation on that bank passes a transitivity audit.

## 4. Frozen action alphabet

Select exactly three future actions by the existing outcome-blind round-robin over base-state GRACE route modes.

Let:

[
mathcal A={a_1,a_2,a_3}.
]

The same target examples, budgets, optimizer, and action ordering are used for every initial state.

## 5. Complete branching to H=2

Execute:

- all three one-step branches;
- all nine ordered two-step sequences, with repetition allowed.

Thus each initial state is evaluated on:

[
3+3^2=12
]

registered action trajectories.

A target already satisfied at a branch node is encoded as:

`ALREADY_SATISFIED_ZERO_WRITE`

and is not silently removed.

After a first-step action, second-step execution proceeds regardless of whether protected obligations were damaged; the damage itself is part of the registered observation. This avoids conditioning the action tree on an outcome.

## 6. RNG and replay discipline

For a fixed seed:

- first-step RNG is a deterministic function of the action ID;
- second-step RNG is a deterministic function of the ordered action pair;
- the same branch RNG is used across all initial states for the same action sequence.

The experiment never searches RNG after observing outcomes.

## 7. Pairwise behavioral equivalence

### H=0

Two states are equivalent iff their complete root READ families match.

### H=1

They must be H=0 equivalent and, for every (ainmathcal A):

- branch status matches exactly;
- target-realization bit matches;
- common protected-contract satisfaction bit matches;
- complete post-action READ families match.

### H=2

They must be H=1 equivalent and satisfy the same conditions after every ordered pair ((a,b)inmathcal A^2).

Record first separation horizon in ({0,1,2,>2}).

## 8. Candidate internal refinements

For every initial state and every root action, reuse the W1 read-only GRACE structural audit.

Define state-level candidate feature signatures:

- **F1:** vector of root native update modes across the three actions;
- **F2:** F1 + action route identities/coverage + protected route signatures;
- **F3:** F2 + projected structural-effect certificates.

For each H=0 collision pair report whether F1/F2/F3:

- still merge a pair that becomes behaviorally separated by H=2 (**under-refinement**);
- separate a pair that remains behaviorally equivalent through H=2 (**over-refinement**).

No feature is called universally necessary.

## 9. Registered seeds and scale

Seeds:

[
{73,137,211,307,401}.
]

Per seed:

- seed edits: 4;
- seed scan limit: 512;
- candidate bank: 64;
- max states: 4;
- future actions: 3;
- sentinels: 16;
- GRACE native edit budget/config: unchanged from official frozen W1 runtime.

The five seeds are executed as independent workflow jobs. No seed is dropped because its scientific result is negative.

## 10. Outputs

Per seed:

- state-bank manifest;
- complete H=0/H=1/H=2 branch metadata;
- pairwise equivalence matrix;
- transitivity audit at each horizon;
- (N_H) only when the relation is transitive;
- first-separation distribution;
- F1/F2/F3 under-/over-refinement counts;
- duplicate state/action replay control.

Across seeds, a later aggregation step will report totals without pooling them into a prevalence estimate.

## 11. Interpretation

Strong positive:

[
exists i,j:quad z_iequiv_1z_jland z_i
otequiv_2z_j.
]

Strong negative:

No such pair is found across the entire frozen multi-seed bank.

Either outcome bears directly on the OACR horizon question.

L1 does not claim that GRACE defines all learned writable representations, and it does not tune the action alphabet after observing results.
