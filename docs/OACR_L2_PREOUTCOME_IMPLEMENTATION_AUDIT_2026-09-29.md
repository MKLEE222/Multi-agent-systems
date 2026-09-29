# OACR-L2 Pre-Outcome Implementation Audit — 2026-09-29

## Status

Performed after protocol/implementation commits and before any L2 future-write outcome is available.

Protocol:

docs/OACR_L2_PARAMETER_FT_H2_PROTOCOL_V1.md

Protocol commit:

addf75ddf9f9e963b65b92428a60dbb84965c72f

Producer:

experiments/oacr_l2/run_ft_h2_parameter_v1.py

Producer commit:

79664135d3c2be87ce5915d0c3544c235674136b

Verifier:

experiments/oacr_l2/verify_ft_h2_parameter_v1.py

Verifier commit:

3a2dd012caba3469988ead53d760cd1c36fb6f07

Workflow:

.github/workflows/oacr-l2-parameter-ft-h2.yml

Workflow commit:

8bed898a33f987ed38446bea67711b52c3654400

## 1. Official mechanism match

The implementation uses the official repository:

Thartvigsen/GRACE

commit:

f674183f17a995d109e10ee6140d4c3e6d016115

and imports:

grace.editors.ft.Finetune.

The official Finetune implementation:

- directly updates model parameters;
- freezes all parameters except the configured inner parameter;
- uses Adam;
- recreates optimizer state per native edit;
- uses edit_lr from the official FT config;
- terminates when the target prediction becomes correct or n_iter is exhausted.

L2 asserts:

- edit_lr = 1e-2;
- n_iter = 100;
- target parameter =
  bert.encoder.layer.10.output.dense.weight.

## 2. Carrier control

L2 reuses the same frozen SCOTUS/BERT assets as L1b:

- frozen SCOTUS-BERT model;
- bert-base-cased tokenizer;
- frozen SCOTUS test parquet;
- same official GRACE repository commit.

Thus the main mechanism contrast is:

GRACE routed external memory
versus
direct target-parameter persistence.

## 3. Persistent-state definition

Only the registered target tensor is allowed to change.

The implementation:

- snapshots the exact target tensor;
- hashes shape/dtype/bytes;
- restores exact tensor values before every branch;
- verifies restore hash;
- computes a whole-model hash over all non-target parameters before and after the run.

Any non-target parameter change invalidates the run.

Optimizer state is not persistent because the official Finetune editor creates a fresh Adam optimizer on every edit call.

## 4. Seeds

Workflow seeds match the protocol exactly:

1511, 1601, 1709, 1801, 1907, 2003, 2111, 2203.

They are disjoint from L1b seeds.

No outcome-dependent seed replacement is implemented.

## 5. Base-state construction

The implementation attempts four sequential contract-preserving native FT edits.

A seed edit is retained only when:

- the target becomes correct;
- all previous protected seed obligations remain correct.

Otherwise the exact target tensor is restored.

Failure is serialized as SEED_CONSTRUCTION_FAILURE with no future outcomes.

## 6. Anchor/future freeze

Natural errors are collected only after base-state construction.

Anchor candidates:

- 24;
- deterministic label-balanced round-robin;
- dataset-index order within label;
- frozen before any anchor write.

Future actions:

- 3;
- selected by the same deterministic rule;
- exclude all 24 frozen anchor IDs;
- frozen before anchor writes.

No H1/H2 outcome contributes to selection.

## 7. READ contracts

Primary C_task stores exact task behavior:

- predicted class;
- target class;
- correctness.

Diagnostic C_logit stores the full L1b-style score family.

The producer retains H0 states using C_task only, as preregistered.

C_logit is separately measured under atol=1e-6 / rtol=1e-5 and is not used to silently reject C_task-valid states.

## 8. H0 collision construction

Every anchor is executed from the exact same base target-tensor snapshot.

Retention requires:

- target realization;
- all protected seed obligations satisfied;
- exact C_task match to base;
- exact C_task match to every already retained state;
- parameter hash differs from base;
- capacity remains.

Maximum state bank:

base + five anchors = six states.

All 24 anchor outcomes are retained in the attempt ledger.

## 9. H1/H2 continuation

For every retained state:

- all three H1 actions are executed from the exact initial parameter snapshot;
- the resulting H1 parameter snapshot is preserved;
- all nine H2 ordered pairs are executed from the corresponding H1 successor.

The second write does not restart from root.

## 10. Behavioral equivalence

Primary task equivalence includes:

- native write status;
- target-realization bit;
- protected-obligation status;
- complete post-write C_task READ family.

H0/H1/H2 pairwise relations are explicitly computed.

Task-level transitivity is audited and any violation raises.

C_logit equivalence is computed separately under tolerance.

No connected-component repair is used for a non-transitive tolerance relation.

## 11. Representation audit

Registered state representations:

- P0: current task READ;
- Pfull: exact target-parameter tensor hash;
- Pdelta-norm: exact serialized L2 delta norm.

Pfull directly tests whether exact parameter identity retains distinctions that the registered future-write contract does not require.

Pdelta-norm is diagnostic only.

## 12. Determinism controls

Each valid seed requires duplicate replay of:

- base + first H1 action;
- first non-base state + first H1 action;
- base + first H2 ordered pair.

Duplicate equality requires:

- native meta-signature;
- exact task READ;
- exact/tolerance logit READ;
- exact resulting target-parameter hash.

Failure invalidates the seed.

## 13. Verifier

The verifier independently recomputes from the artifact:

- anchor/future disjointness;
- panel counts;
- state/pair identities;
- complete H1/H2 branch keys;
- pairwise C_task and C_logit relations;
- task transitivity;
- H1/H2 separation counts;
- H2 task operational partition;
- U/E and pairwise under/over-refinement for P0/Pfull/Pdelta-norm;
- duplicate control bits.

The verifier does not rerun native FT.

Any prospectively observed positive H1/H2 separation therefore still requires a targeted independent native replay before claim promotion.

## 14. Pre-outcome judgment

Implementation matches the frozen L2 scientific design closely enough to execute.

No scientific parameter change is authorized after outcomes.

Allowed future corrections are limited to documented engineering failures that occur before scientific interpretation and do not alter:

- seeds;
- carrier;
- FT mechanism;
- write budget;
- state/action selection;
- READ contracts;
- horizon;
- representation diagnostics.
