# OACR-L2b Targeted Native Replay Protocol — Fold 0 Positive

**Date:** 2026-09-29  
**Status:** frozen after the prospectively registered L2b fold-0 positive was observed, before claim promotion  
**Role:** independent native replay of the discovered positive; not a second discovery experiment.

## 1. Trigger

L2b fold 0 produced one retained H0 task-collision pair:

- state A: base;
- state B: anchor:688.

The registered future actions were:

- dataset 51;
- dataset 29;
- dataset 73.

The artifact-level verifier reconstructed the stored relations and confirmed:

\[
H0=\text{equivalent},
\qquad
H1=\text{distinct}.
\]

Claim promotion requires an independent native replay.

## 2. Replay independence

The replay must not load:

- the original fold-0 parameter snapshots;
- the original branch outcome matrix;
- the original stored H1 READ families.

It may use only:

- the frozen SCOTUS/BERT assets;
- official GRACE repository commit f674183f17a995d109e10ee6140d4c3e6d016115;
- the frozen L2b fold-0 construction rules;
- the discovered IDs required for targeted replication.

## 3. Frozen IDs

Reconstruct fold 0 under the original L2b rules.

Expected base seed-edit IDs:

\[
[0,14,19,22].
\]

Target positive anchor:

\[
688.
\]

Registered future-action IDs:

\[
[51,29,73].
\]

These IDs are now replication targets and are not selected anew.

## 4. H0 replay

From the reconstructed fold-0 base parameter state:

1. record the frozen L2b C_task READ panel;
2. restore the exact base target tensor;
3. execute official Finetune write on anchor 688;
4. require target realization;
5. require all four protected seed obligations remain correct;
6. require target-parameter hash differs from base;
7. require the complete registered C_task READ family equals the base C_task READ family exactly.

Failure invalidates the positive replication.

C_logit equality is not required because L2b primary equivalence is C_task.

## 5. H1 replay

For each registered action in [51,29,73]:

1. restore exact base state;
2. execute the action with official Finetune;
3. record native status, target realization, protected obligations, complete C_task READ and target-parameter hash;
4. restore exact anchor-688 state;
5. execute the same action;
6. record the same fields.

For the positive to replicate, at least one action must produce a registered H1 behavioral difference.

Because the original artifact showed all three actions separating the pair, report replication status separately for each action.

## 6. Strong replay target

For each action report whether separation arises through:

- native write status;
- target-realization bit;
- protected-obligation status;
- one or more exact C_task READ entries.

Report the exact panel indices/dataset IDs whose task-level values differ.

No numerical tolerance is used for the primary replay decision.

## 7. Determinism

Run the entire reconstruction and H1 replay twice in the same job from fresh model/editor initialization.

Require for each reconstruction:

- same accepted base seed IDs;
- same base target-parameter hash;
- same anchor-688 target-parameter hash;
- same H0 task READ;
- same H1 branch target-parameter hashes;
- same H1 task READ families.

Any deterministic mismatch invalidates the replay.

## 8. Acceptance

### PASS_POSITIVE_REPLAY

Require:

- fold-0 base reconstructed exactly;
- anchor 688 reproduces an H0 C_task collision;
- at least one of actions 51/29/73 reproduces H1 separation;
- two independent fresh reconstructions agree exactly.

### FAIL_H0

Anchor 688 no longer reproduces the registered H0 collision.

### FAIL_H1

H0 collision reproduces but none of the three H1 actions separate.

### FAIL_DETERMINISM

Two fresh reconstructions differ.

## 9. Interpretation

PASS_POSITIVE_REPLAY supports promotion of the L2b fold-0 result to:

> a prospectively discovered and independently native-replayed existence result showing that two direct parameter states with identical registered current task behavior can require different operational distinctions after a future native parameter write.

It does not establish prevalence.

The remaining L2b folds continue to determine how sparse or recurrent this phenomenon is.
