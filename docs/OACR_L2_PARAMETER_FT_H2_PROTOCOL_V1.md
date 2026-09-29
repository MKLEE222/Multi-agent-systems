# OACR-L2 Protocol v1 — Parameter-State H2 Audit on Official SCOTUS Finetune

**Date:** 2026-09-29  
**Status:** prospectively frozen before any L2 future-write outcome is inspected  
**Role:** second learned persistent-write ecology after the accepted L1b GRACE H2 negative.

## 1. Scientific contrast

L1b audited the official GRACE routed external-memory editor on the frozen SCOTUS/BERT carrier.

L2 keeps fixed:

- official GRACE repository commit: f674183f17a995d109e10ee6140d4c3e6d016115;
- frozen SCOTUS/BERT model assets;
- frozen SCOTUS edit split;
- BERT task semantics;
- the same targeted inner parameter location:
  bert.encoder.layer[10].output.dense.weight.

L2 changes the persistent write mechanism only:

- L1b: GRACE external routed key/value memory;
- L2: official GRACE repository Finetune editor, which directly updates the target model parameter.

This is a mechanism contrast, not a benchmark comparison.

## 2. Native parameter-write operator

Use the official implementation:

grace/editors/ft.py

with the official editor config:

grace/config/editor/ft.yaml

Frozen write settings:

- optimizer: Adam as implemented by the official editor;
- edit learning rate: 1e-2;
- maximum edit iterations: 100;
- batch size: 1;
- dropout: 0;
- only bert.encoder.layer[10].output.dense.weight requires gradient;
- optimizer state is recreated for every native write and is not persistent state.

A write terminates early exactly when the target prediction becomes correct, as in the official Finetune editor.

Persistent state is therefore the target parameter tensor after the write sequence.

## 3. Seeds

Use eight new seeds disjoint from L1b:

1511, 1601, 1709, 1801, 1907, 2003, 2111, 2203.

No seed may be replaced because of weak, null, inconvenient, or underpowered results.

## 4. Base persistent state

For each seed, construct a non-vacuous base parameter state through four sequential native Finetune edits.

A seed edit is committed only if:

1. the target example becomes correct;
2. all previously registered seed obligations remain correct.

Otherwise restore the exact target-parameter snapshot and continue scanning.

Registered limits:

- target seed edits: 4;
- seed scan limit: 1024.

Failure to build four contract-preserving seed edits is retained as:

SEED_CONSTRUCTION_FAILURE

with no future-write outcome execution.

## 5. State snapshot and determinism

The only mutable model parameter is the registered target tensor.

For every persistent state record:

- exact target-tensor SHA256;
- tensor shape/dtype;
- L2 distance from the base persistent tensor;
- maximum absolute delta from base.

The implementation must verify that all non-target model parameters remain byte-identical to their frozen values.

Before and after every branch:

- restore the exact target-tensor snapshot;
- verify tensor hash;
- clear gradients;
- use deterministic CPU execution;
- use dropout=0;
- use fresh native Adam optimizer per write.

Duplicate native replays are required for registered control branches.

## 6. Candidate bank

After base-state construction, scan forward from the last accepted seed index and freeze the first 512 natural errors.

No future-write outcome is executed before anchor/future IDs are frozen.

## 7. Anchor candidates

Freeze 24 anchor candidates from the candidate bank using deterministic label-balanced round-robin selection:

1. group natural errors by target label;
2. order labels numerically;
3. order rows within label by dataset index;
4. repeatedly take the next unused row from each label in order until 24 candidates are selected or the bank is exhausted.

This uses no persistent-write outcome.

All selected anchor IDs are frozen even if later anchor writes fail or do not enter the H0 bank.

## 8. Future actions

After anchor IDs are frozen and before any anchor write is executed, select three future actions from the remaining natural-error bank by the same deterministic label-balanced rule.

Requirements:

- three unique dataset IDs;
- zero overlap with all frozen anchor IDs.

If three actions cannot be selected:

UNDERPOWERED_FUTURE_ACTIONS

with no future-write outcome execution.

## 9. READ contracts

L2 registers two nested READ contracts.

### C_task — primary task-level contract

For every panel example record exactly:

- predicted class;
- target label;
- correctness bit.

Two reads match iff all registered task-level fields match exactly.

This is the primary cross-mechanism contract because it corresponds to the native classification behavior rather than exact internal score equality.

### C_logit — stronger diagnostic contract

Additionally record:

- full logits;
- full probabilities;
- target margin;
- target cross-entropy.

Use the same frozen numerical tolerances as L1b:

- atol = 1e-6;
- rtol = 1e-5.

C_logit refines C_task.

C_logit is diagnostic and may have fewer H0 collisions. A lack of C_logit collisions does not invalidate C_task.

## 10. Frozen READ panel

The panel contains:

1. four protected seed obligations;
2. all three future actions;
3. 24 deterministic sentinels.

Sentinels are selected after anchor/future IDs are frozen and exclude:

- seed IDs;
- all frozen anchor IDs;
- all future-action IDs.

Sentinels are chosen deterministically by ascending dataset index with label round-robin when possible.

READ evaluation must not mutate parameters.

## 11. H0 collision-state construction

Start with the base persistent parameter state.

For each frozen anchor candidate:

1. restore the exact base target tensor;
2. execute one native Finetune write;
3. require target realization;
4. require all four seed obligations remain correct;
5. evaluate the frozen READ panel;
6. require C_task equality with the base state;
7. require C_task equality with every already retained state;
8. retain until capacity is reached.

Capacity:

- base + at most five anchor states;
- maximum states per seed: 6.

All 24 anchor attempts remain in the artifact even after capacity is reached.

C_logit pairwise equality is recorded but is not required for C_task retention.

If fewer than two states survive:

UNDERPOWERED_STATE_CONSTRUCTION

with no H1/H2 execution.

## 12. Future branching

For every retained initial state execute the same three frozen future actions.

### H1

For each action:

- restore exact initial target-tensor snapshot;
- if target is already correct: ALREADY_SATISFIED_ZERO_WRITE;
- otherwise execute official Finetune edit;
- record target realization;
- record protected seed-obligation status;
- record C_task and C_logit READ families;
- record post-state tensor hash.

### H2

For every ordered pair with repetition:

\[
(a_i,a_j),\qquad i,j\in\{1,2,3\},
\]

execute the second action from the exact H1 successor of the first action.

Thus every initial state receives:

- 3 H1 branches;
- 9 complete H2 sequences.

No branch may restart from root for the second action.

## 13. Behavioral equivalence

### H0 under C_task

Retained states are pairwise task-READ equivalent by construction.

### H1

Two H0-collision states remain H1-equivalent iff for all three actions they match on:

- native status;
- target-realization bit;
- protected-obligation status;
- complete post-action C_task READ family.

### H2

They remain H2-equivalent iff H1-equivalent and for all nine ordered pairs they match on the same registered fields after the second action.

C_logit equivalence is computed separately as a stronger nested diagnostic relation.

## 14. Equivalence audit

For C_task and, where applicable, C_logit:

- compute all within-seed pairwise relations at H0/H1/H2;
- explicitly audit symmetry and transitivity;
- do not convert a non-transitive tolerance relation into connected components.

Partition-level U/E is only reported when the relation is a valid equivalence relation.

## 15. Representation diagnostics

Primary parameter-state representations:

### P0 — task READ only

The H0 task-level current observation.

### Pfull — exact target-parameter identity

Exact SHA256 of bert.encoder.layer[10].output.dense.weight.

This tests whether full parameter identity over-refines the operational partition.

### Pdelta-norm — scalar structural diagnostic

Exact floating-point L2 norm of the target-parameter delta from the seed base state, serialized at full precision.

This is diagnostic only and is not claimed as a sufficient representation.

For all representations report pairwise under-/over-refinement against valid H2 operational equivalence.

## 16. Determinism controls

Per valid seed require duplicate replay for:

1. base + first H1 action;
2. first non-base state + first H1 action when available;
3. base + first registered H2 ordered pair.

Duplicate equality requires:

- native meta-signature;
- complete task READ family;
- complete logit READ family within registered tolerance;
- exact post-state parameter hash.

Failure invalidates that seed run.

## 17. Scale interpretation

A valid seed may contain 2–6 retained states.

For interpreting an all-zero-separation result as a strong L2 negative, require aggregate:

- at least 6/8 valid seeds;
- at least 60 H0 C_task collision pairs;
- all registered H1/H2 branching complete;
- all determinism controls pass.

A positive separation is an existence result even if aggregate scale is below this negative-evidence threshold, but it still requires targeted independent native replay before promotion.

## 18. Primary questions

1. Do direct parameter states that are currently task-equivalent become distinguishable under future parameter writes?
2. If so, does first separation occur at H1 or only H2?
3. If not, does exact target-parameter identity substantially over-refine the registered operational partition?
4. How does this compare with the accepted GRACE external-memory negative under the same carrier family?

## 19. Outcome interpretation

### Positive

If any prospectively registered H0 C_task collision pair separates at H1/H2:

- retain all artifacts;
- independently native-replay every separating branch before claim promotion;
- do not extend horizon merely to generate more positives.

### Strong negative

If the scale threshold is met and no H1/H2 separation occurs:

- accept a second learned negative on a materially different persistent-state substrate;
- do not tune Finetune anchors/actions to seek a positive.

### Underpowered

If collision construction fails the scale threshold:

- classify as state-construction underpower;
- use only pre-future-write diagnostics to design any successor protocol.

## 20. Boundaries

L2 does not establish:

- universal parameter-editing behavior;
- that H=2 is sufficient in general;
- that exact parameter identity is never operationally necessary;
- a frequency estimate over arbitrary learned states;
- equivalence between GRACE and Finetune write semantics.

Its role is a controlled second learned ecology with the same carrier and target layer but a different persistent-state substrate.
