# OACR Learned COMPOSE Depth Audit — Existing L2b Assets

**Date:** 2026-09-29  
**Source run:** GitHub Actions \`36514834740\` — OACR L2b Fold Diverse Parameter FT H2  
**Status:** retrospective evidence audit; no new learned outcome generated

## 1. Purpose

After introducing the qualified-continuation depth ladder, inspect the already frozen L2b direct-parameter H2 experiment for any previously unrecognized

\[
H1\text{-equivalent} \rightarrow H2\text{-divergent}
\]

pair.

No learned protocol is modified by this audit.

## 2. Artifact inventory

The accepted L2b run produced artifacts for all eight deterministic folds:

- fold 0 — artifact 11012134712;
- fold 1 — artifact 11012755051;
- fold 2 — artifact 11012791240;
- fold 3 — artifact 11012976582;
- fold 4 — artifact 11013072418;
- fold 5 — artifact 11013439352;
- fold 6 — artifact 11014552167;
- fold 7 — artifact 11014088870.

All stored artifact-level verifiers passed their registered status checks.

## 3. Exact depth result

### Fold 0

Status: \`COMPLETE\`.

- retained states: 2;
- H0 task-collision pairs: 1;
- H1 task separations from H0: 1;
- H2 task separations from H1: 0.

The single pair is:

- base;
- anchor 688.

It is therefore a direct H1 positive:

\[
H0\text{-equivalent}
\rightarrow
H1\text{-distinct}.
\]

It is **not** a delayed COMPOSE witness.

The targeted native replay later independently reproduced the H0 collision and H1 separation under actions 51, 29, and 73.

### Folds 1--7

Each fold has status:

\`UNDERPOWERED_STATE_CONSTRUCTION\`.

Per fold:

- 509 anchor attempts executed;
- fewer than two retained H0-collision states;
- \`future_outcomes_executed = false\`.

Therefore these folds contain no H1 or H2 evidence and cannot be used as positive or negative COMPOSE results.

## 4. Verdict

The existing direct-parameter learned assets contain:

- one independently replayed learned H1 positive;
- zero registered delayed H2 positives;
- zero valid H2 negative folds beyond the separate GRACE L1b ecology.

Thus the learned branch does **not** already contain a hidden

\[
H1= \rightarrow H2+
\]

result.

A future COMPOSE-L design must be prospectively distinct and must not retune L2b merely to force such a witness.

## 5. Current learned control structure

The learned evidence map is now:

- GRACE L1b: \`D2=\` negative through the complete registered H2 panel on 224 H0-collision pairs;
- Finetune fold0: \`D1+\` positive, independently native replayed;
- Finetune folds1--7: H0 state-construction underpower;
- delayed learned COMPOSE: open.

This supplies both a stable negative and a first-order positive without yet answering whether a write can change the relevance of a later learned write.
