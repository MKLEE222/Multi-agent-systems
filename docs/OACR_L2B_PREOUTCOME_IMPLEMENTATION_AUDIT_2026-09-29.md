# OACR-L2b Pre-Outcome Implementation Audit — 2026-09-29

## Status

Performed after protocol, producer, verifier, and workflow commits, before any L2b H1/H2 outcome is inspected.

Protocol:
docs/OACR_L2B_FOLD_DIVERSE_FT_H2_PROTOCOL_V1.md

Protocol commit:
7d3e600ada83b46c8b00b80f751ddfe7154ba75d

Producer:
experiments/oacr_l2b/run_fold_diverse_ft_h2_v1.py

Producer commit:
f7764e55f795fff55ba571dbbfe00434cc34490e

Verifier:
experiments/oacr_l2b/verify_fold_diverse_ft_h2_v1.py

Verifier commit:
32b065bb64d32da66105b5904318171206f7ad8b

Workflow:
.github/workflows/oacr-l2b-fold-diverse-ft-h2.yml

Workflow commit:
ed33017a0889d329b8953e2ef9811479484611ce

## 1. Mechanism unchanged from L2-v1

The implementation still uses:

- official GRACE repository commit f674183f17a995d109e10ee6140d4c3e6d016115;
- official grace.editors.ft.Finetune;
- target parameter bert.encoder.layer.10.output.dense.weight;
- Adam;
- edit_lr = 1e-2;
- n_iter = 100;
- CPU deterministic execution;
- frozen SCOTUS/BERT model, tokenizer, and dataset assets.

No write-budget tuning was introduced after L2-v1 underpower.

## 2. Deterministic fold diversity

The ineffective random-seed axis is removed.

Eight folds are defined only from dataset length:

s_f = floor(f*N/8), f in {0,...,7}.

All scans follow circular dataset order from the fold start.

Thus carrier diversity comes from deterministic dataset location rather than RNG.

## 3. Base persistent state

Per fold:

- four contract-preserving native FT seed writes are required;
- seed candidates are traversed in circular order;
- only currently misclassified examples are attempted;
- failed/interfering writes restore the exact target tensor;
- at most 1024 misclassified seed candidates are attempted.

No H1/H2 outcome is used.

## 4. Frozen candidate bank and future actions

After base construction:

- continue traversal after the last accepted seed;
- freeze up to 512 currently misclassified examples;
- freeze three future actions by deterministic label-balanced selection;
- remove those future IDs from the H0 anchor-search bank.

All future IDs are frozen before any H0 anchor-state write.

## 5. Sentinels

Twenty-four sentinels are selected before anchor writes.

They exclude:

- seed IDs;
- every ID in the frozen 512 candidate bank.

Thus no anchor/future candidate is also a sentinel.

The primary C_task and diagnostic C_logit contracts remain unchanged from L2-v1.

## 6. Expanded H0 scan

Every frozen non-future candidate is considered in deterministic traversal order until either:

- six total states are retained; or
- the entire frozen anchor-search bank is exhausted.

Retention requires:

- target realization;
- all four seed obligations preserved;
- exact C_task match to base;
- exact C_task match to all retained states;
- changed target-parameter hash.

No future-write outcome participates in H0 selection.

The artifact records every attempted anchor before stopping and an explicit retention reason.

## 7. H1/H2 contract

Unchanged:

- 3 H1 native writes per retained state;
- all 9 ordered H2 action pairs with repetition;
- second action starts from the exact H1 successor.

Behavioral equivalence uses:

- native status;
- target realization;
- protected-obligation status;
- complete C_task READ family.

C_logit remains a stronger diagnostic only.

## 8. Representation audit

Unchanged:

- P0 current task READ;
- Pfull exact target-parameter hash;
- Pdelta-norm full-precision target delta norm.

Partition-level metrics require valid task-level equivalence.

## 9. Determinism controls

Unchanged:

- duplicate base H1;
- duplicate first non-base H1 when available;
- duplicate base H2.

Post-state target-parameter hash must match exactly.

## 10. Verifier coverage

The verifier independently checks from the artifact:

- fold identity;
- non-complete status discipline;
- candidate/future set consistency;
- panel counts;
- unique anchor attempts;
- retained-state/retained-attempt identity;
- complete H1/H2 key sets;
- pair set;
- task-equivalence reconstruction;
- task transitivity;
- operational partition;
- P0/Pfull/Pdelta-norm U/E;
- summary arithmetic;
- duplicate-replay control bits.

It does not rerun native FT.

A positive future separation still requires a targeted independent native replay before claim promotion.

## 11. Pre-outcome judgment

Implementation matches the L2b protocol closely enough to run.

No scientific parameter change is authorized after outcomes.

Any correction after execution must be classified explicitly as:

- engineering failure before scientific outcome; or
- a new successor protocol.

The current protocol may not be modified merely because H0 collisions remain rare or because H1/H2 outcomes are inconvenient.
