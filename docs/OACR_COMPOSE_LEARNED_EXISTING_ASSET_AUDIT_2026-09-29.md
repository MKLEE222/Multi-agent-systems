# OACR COMPOSE — Existing Learned-Asset Audit

**Date:** 2026-09-29  
**Status:** retrospective evidence reclassification; no new learned outcome executed  
**Source run:** OACR L2b fold-diverse FT H2, run \`36514834740\`  
**Purpose:** determine whether an already executed learned-state artifact contains a hidden H1-equivalent / H2-divergent pair.

## 1. Audit question

The minimum learned COMPOSE witness is

\[
X \equiv_1 Y
\quad\land\quad
X \not\equiv_2 Y.
\]

This audit re-reads the already frozen and executed L2b fold artifacts without changing:

- H0 collision construction;
- future-action IDs;
- READ contract;
- H1/H2 branching;
- equivalence definitions;
- parameter-write mechanism.

No native write is rerun for discovery.

## 2. Original L2b run

Original run:

\[
36514834740.
\]

Eight fold artifacts were produced:

| fold | artifact ID | original disposition |
|---:|---:|---|
| 0 | 11012134712 | COMPLETE |
| 1 | 11012755051 | UNDERPOWERED_STATE_CONSTRUCTION |
| 2 | 11012791240 | UNDERPOWERED_STATE_CONSTRUCTION |
| 3 | 11012976582 | UNDERPOWERED_STATE_CONSTRUCTION |
| 4 | 11013072418 | UNDERPOWERED_STATE_CONSTRUCTION |
| 5 | 11013439352 | UNDERPOWERED_STATE_CONSTRUCTION |
| 6 | 11014552167 | UNDERPOWERED_STATE_CONSTRUCTION |
| 7 | 11014088870 | UNDERPOWERED_STATE_CONSTRUCTION |

Every artifact-level verifier passed its registered disposition.

## 3. Fold 0

Fold 0 is the only fold with more than one retained H0 state.

Registered bank:

- states: 2;
- retained non-base states: 1;
- H0 task-collision pairs: 1.

Pair:

- base;
- anchor 688.

Registered future actions:

\[
[51,29,73].
\]

Original relation summary:

\[
H0\text{ pairs}=1,
\]

\[
H1\text{ separations from H0}=1,
\]

\[
H2\text{ separations from H1}=0.
\]

Thus the only learned H0 collision already separates at depth 1.

The independently native-replayed positive therefore remains a WRITE / depth-1 result, not a delayed COMPOSE result.

## 4. Folds 1--7

Each fold terminated with:

\[
UNDERPOWERED\_STATE\_CONSTRUCTION.
\]

No fold retained a non-base state satisfying the registered H0 C_task collision contract.

Therefore:

- no H0 pair exists;
- no H1 relation exists;
- no H2 future outcome was executed.

These folds cannot support either a positive or negative COMPOSE claim.

## 5. Learned evidence verdict

The existing learned assets contain:

### GRACE L1b

A prospective H2 negative boundary:

\[
224\text{ H0 collision pairs},
\qquad
H1\text{ separations}=0,
\qquad
H2\text{ separations}=0.
\]

Role:

> hidden routed-memory distinctions need not become relevant merely because writes are composed through depth 2.

### Parameter FT L2b fold 0

A prospectively discovered and independently replayed depth-1 positive:

\[
H0\text{-equivalent}
\rightarrow
H1\text{-different}.
\]

Role:

> direct parameter-state distinctions can be future-write relevant.

### Missing learned object

No existing learned artifact supports:

\[
\boxed{
H1\text{-equivalent}
\rightarrow
H2\text{-different}.
}
\]

This is a real evidence gap, not a missing reinterpretation.

## 6. Consequence for COMPOSE planning

Do not:

- relabel fold0 as COMPOSE;
- extend GRACE horizon merely to seek a positive;
- weaken the L2b READ panel post-hoc to manufacture collisions;
- change fold0 future actions after observing that all three separate at H1.

A new learned COMPOSE study would need a fresh protocol designed around state-dependent sequential-write semantics before outcomes.

## 7. Current cross-carrier map

| carrier | H1 | H2 / composition | role |
|---|---|---|---|
| relational deletion R3/R4 | positive distinctions at H1 | no new finite-depth distinctions under frozen deletion universe | exact compositionally closed control |
| SQEC controlled qualification | H1-equivalent state pair | H2 divergence under commit -> observe | exact controlled COMPOSE positive |
| Git inherited G5 panel | 46 H1-equivalent pairs | no shared materializable t1 under v2 preflight | verified action-affordance underpower |
| GRACE learned memory | H1-equivalent | H2-equivalent on 224 pairs | learned negative boundary |
| FT parameter fold0 | H1-separated | no new H2 refinement | learned depth-1 positive |

The next COMPOSE positive should therefore come from a fresh carrier/action-generation protocol, not from reinterpretation of the existing learned evidence.
