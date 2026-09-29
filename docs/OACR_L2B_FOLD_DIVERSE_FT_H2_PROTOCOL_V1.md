# OACR-L2b Protocol v1 — Fold-Diverse Parameter-State H2 Audit

**Date:** 2026-09-29  
**Status:** prospectively frozen before any L2b H1/H2 future-write outcome is inspected  
**Supersedes for learned parameter-state execution:** OACR_L2_PARAMETER_FT_H2_PROTOCOL_V1.md  
**Scientific mechanism unchanged:** official SCOTUS Finetune parameter editor.

## 1. Motivation

L2-v1 executed no H1/H2 future outcomes because all eight registered jobs failed to construct more than one H0 state.

Pre-future diagnostics showed:

- 192/192 anchor writes realized their target;
- 0/192 preserved the registered primary task READ panel;
- only 24/192 preserved all seed obligations;
- random seeds did not produce distinct carriers because official Finetune is deterministic under the frozen runtime.

Therefore L2b changes only H0 carrier coverage and candidate-search coverage.

It does not change the future contract or write mechanism.

## 2. Frozen mechanism

Use the same official repository and editor as L2-v1:

- Thartvigsen/GRACE commit f674183f17a995d109e10ee6140d4c3e6d016115;
- official grace.editors.ft.Finetune;
- frozen SCOTUS/BERT carrier assets;
- target parameter:
  bert.encoder.layer[10].output.dense.weight;
- Adam optimizer recreated per write;
- edit_lr = 1e-2;
- n_iter = 100;
- dropout = 0;
- CPU deterministic execution.

Only the target parameter may change.

## 3. Deterministic folds

Replace ineffective random seeds with eight deterministic dataset folds:

\[
f\in\{0,1,2,3,4,5,6,7\}.
\]

For dataset length N, define fold start:

\[
s_f=\left\lfloor\frac{fN}{8}\right\rfloor.
\]

All dataset scans use circular index order beginning at \(s_f\):

\[
s_f,s_f+1,\ldots,N-1,0,1,\ldots,s_f-1.
\]

No fold is replaced because of weak or inconvenient results.

The fold ID is not an RNG seed.

## 4. Base persistent state

Per fold construct four sequential contract-preserving native Finetune edits.

Traverse the fold's circular order.

A candidate is considered only if currently misclassified.

Commit the write only if:

1. target becomes correct;
2. all previously accepted seed obligations remain correct.

Otherwise restore the exact target-parameter tensor.

Stop when:

- four seed edits are accepted; or
- 1024 currently-misclassified seed candidates have been attempted; or
- one complete circular traversal is exhausted.

Failure is retained as:

SEED_CONSTRUCTION_FAILURE

with no H1/H2 future outcomes.

## 5. Frozen candidate bank

After base-state construction, continue circular traversal immediately after the last accepted seed index.

Freeze the first 512 currently misclassified examples satisfying:

- not one of the four seed IDs.

Candidate-bank membership is determined before any anchor-state write.

If fewer than 32 candidates exist:

UNDERPOWERED_CANDIDATE_BANK

with no H1/H2 execution.

## 6. Future actions

Before any H0 anchor-state write:

1. group the frozen candidate bank by target label;
2. order labels numerically;
3. order examples within label by circular traversal rank;
4. select three unique future actions by deterministic label-balanced round robin.

Freeze these three IDs.

They are removed from the H0 anchor-search bank.

No future-write outcome is executed during selection.

## 7. Sentinels and READ contracts

Keep L2-v1 READ definitions unchanged.

### Primary C_task

Per registered panel item:

- predicted class;
- target class;
- correctness.

Exact equality required.

### Diagnostic C_logit

- full logits;
- probabilities;
- target margin;
- cross entropy.

Tolerance:

- atol = 1e-6;
- rtol = 1e-5.

Frozen panel:

- four protected seed obligations;
- three frozen future actions;
- 24 deterministic sentinels.

Sentinels are selected before anchor-state writes from circular traversal order, excluding:

- seed IDs;
- all 512 candidate-bank IDs.

This prevents an eventual anchor candidate from also serving as a sentinel.

READ evaluation must not mutate model state.

## 8. Expanded H0 anchor scan

The H0 anchor-search bank is:

- all frozen candidate-bank items except the three future actions.

Order anchors by circular traversal rank.

For each anchor in that frozen order:

1. restore exact base target tensor;
2. execute one official Finetune write;
3. require target realization;
4. require all four protected seed obligations remain correct;
5. evaluate the frozen READ panel;
6. require exact C_task equality with base;
7. require exact C_task equality with every already retained state;
8. require parameter hash differs from base;
9. retain while capacity remains.

Maximum state bank:

- base + five non-base states = 6.

Stopping rule:

- if six states are reached, stop H0 anchor scanning;
- otherwise scan the entire frozen anchor-search bank.

Every attempted anchor before stopping is serialized with:

- target realization;
- protected-obligation status;
- task READ match;
- diagnostic logit match;
- parameter hash;
- parameter delta norm;
- retention reason.

No H1/H2 outcome contributes to H0 acceptance.

## 9. H1/H2 future contract

Unchanged from L2-v1.

For every retained state:

### H1

Execute each of the three frozen future actions from the exact initial parameter snapshot.

Record:

- native write status;
- target realization;
- protected obligations;
- C_task READ;
- C_logit READ;
- post-state parameter hash.

### H2

Execute all nine ordered pairs with repetition.

Second action must start from the corresponding H1 successor state.

## 10. Behavioral equivalence

Unchanged from L2-v1.

Primary operational equivalence uses C_task plus native status/obligation fields.

Diagnostic C_logit relation is separately measured.

Explicit symmetry/transitivity audit is required before any partition-level metric.

## 11. Representation diagnostics

Unchanged:

- P0 = current C_task READ;
- Pfull = exact target-parameter identity;
- Pdelta-norm = full-precision target-parameter L2 delta norm.

Report U/E and pairwise under-/over-refinement against valid H2 operational equivalence.

## 12. Determinism controls

Unchanged:

1. base + first H1 action;
2. first non-base + first H1 action when available;
3. base + first H2 ordered pair.

Require exact post-state parameter hash and matching registered behavior.

## 13. Aggregate interpretation thresholds

### Strong future negative

May be claimed only if:

- at least 4/8 folds are COMPLETE;
- aggregate H0 C_task collision pairs >= 30;
- all registered H1/H2 branches complete;
- all determinism controls pass;
- H1 separations = 0;
- H2 separations = 0.

### Positive

Any prospectively registered H0 pair separating at H1/H2 is an existence result, subject to targeted independent native replay before promotion.

### H0-visibility boundary

If fewer than 4 folds are COMPLETE despite exhaustive frozen anchor scans, and at least 1000 aggregate anchor attempts are executed with zero retained non-base C_task-collision states, classify L2b as:

PARAMETER_STATE_H0_VISIBILITY_BOUNDARY

This supports only:

> Under the registered rich current-task panel, native direct parameter writes were almost always immediately observable, preventing construction of hidden H0 state collisions.

It is not a future-write negative.

### Other underpower

If attempts are too few to reach the H0-visibility threshold, classify as state-construction underpower.

## 14. Comparison to GRACE

The intended contrast is:

- GRACE: abundant current-read collisions, no H1/H2 refinement in 224 registered pairs;
- Finetune: determine whether hidden current-read parameter collisions exist at all under the same carrier family, and if so whether future writes separate them.

Do not force both mechanisms into the same empirical outcome type.

Mechanism-relative observability is itself scientifically relevant.

## 15. Boundaries

L2b does not claim:

- population frequency over all parameter states;
- universal absence/presence of hidden parameter collisions;
- H=2 sufficiency;
- equivalence of GRACE and Finetune semantics;
- that current-read visibility implies representation adequacy under all contracts.

It is a controlled second learned ecology with much broader H0 construction coverage than L2-v1.
