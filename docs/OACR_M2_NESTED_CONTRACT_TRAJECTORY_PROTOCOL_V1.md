# OACR-M2 Protocol v1 — Nested-Contract Adequacy Trajectories

**Date:** 2026-09-28  
**Status:** preregistered post-R3/G5 trajectory analysis; endpoint results at the full contracts are already known  
**Purpose:** test how fixed implemented representations move relative to the operational partition as one frozen native-operation contract is strengthened by nested action-family expansion.

## 1. Scientific role

R3 and G5 established the finite-contract same-bank pattern

\[
R_{\rm coarse}\prec O_{\mathcal C}\prec R_{\rm fine},
\]

and G5 validation additionally found a native intermediate representation whose partition exactly matched the registered finite operational partition.

M2 does **not** treat monotonicity itself as a novel empirical discovery. For nested contracts whose operational partitions refine deterministically, the T2 theorem already implies for every **fixed** representation partition \(R\):

\[
U_{\mathcal C'}(R)\ge U_{\mathcal C}(R),
\qquad
E_{\mathcal C'}(R)\le E_{\mathcal C}(R).
\]

The empirical objects in M2 are therefore:

1. where nontrivial operational refinements actually occur;
2. how quickly \(|O_{\mathcal C}|\), \(U\), and \(E\) change;
3. when a fixed intermediate representation first becomes adequate or exactly matched;
4. whether the same trajectory structure is reproducible across materially different carriers.

Because the full R3 and G5 endpoint outcomes were already observed before this protocol was frozen, M2 on those carriers is a **development/trajectory analysis**, not an independent confirmatory replication of the endpoint claims.

## 2. Anti-leakage rules

The following are frozen before M2 outcomes are inspected:

- state banks are unchanged from R3/G5;
- the full action sets are unchanged from R3/G5;
- nested contract order is determined without operation outcomes;
- representation partitions used in the primary analysis are computed once and remain fixed across all contract sizes;
- no target/action is added, removed, or reordered after trajectory outcomes are observed;
- any representation that changes with contract size is exploratory and may not be used to support the fixed-representation contract-expansion claim.

Every run must preserve:
- exact source identifiers/hashes;
- action order;
- per-prefix operational class counts;
- per-prefix \(U/E\);
- endpoint regression checks against the frozen R3/G5 full-contract results.

Any violation of nested partition refinement or endpoint regression invalidates the run.

## 3. M2-R — relational nested trajectory

### 3.1 State bank

Reuse the exact R3 state bank:

- base prepared graph \(G\);
- all 271 single redundant-edge augmentations;
- 272 states total;
- identical complete current transitive closure in every state.

### 3.2 Full action set

Reconstruct exactly the R3 64-edge shared deletion set:

1. rank every asserted base edge by base-graph deletion impact;
2. break ties lexically;
3. select the same 64 evenly spaced ranked edges used in R3.

### 3.3 Outcome-blind nested ordering

The 64 selected actions are reordered only for nested-prefix analysis using their **base ranked positions**, never augmented-state outcomes.

Deterministic maximin rule:

1. choose the selected action whose base rank is closest to the median selected rank; tie by lower base rank then lexical identity;
2. repeatedly choose the remaining action that maximizes its minimum absolute rank distance to the already selected actions;
3. break ties by lower base rank then lexical identity.

This produces a single frozen order \((a_1,\ldots,a_{64})\).

Define nested contracts

\[
\mathcal C_k=\{a_1,\ldots,a_k\},
\qquad k=0,\ldots,64.
\]

All 65 prefixes are measured. Anchor sizes \(k\in\{0,1,2,4,8,16,32,64\}\) are highlighted for reporting.

### 3.4 Fixed representation partitions

The primary M2-R analysis keeps the following partitions fixed for every \(k\):

- **R0-fixed:** complete current closure only;
- **Rfull-fixed:** complete asserted-edge identity;
- **Rsupport64-fixed:** the full 64-dimensional pre-deletion action-endpoint path-count vector from R3.

No prefix-specific support representation is primary.

### 3.5 Outputs

For every \(k\):

- operational class count and block-size profile;
- operational entropy under the same uniform state distribution;
- \(U_k(R)\), \(E_k(R)\), and partition-match/adequacy bits for every fixed representation;
- pairwise under-/over-refinement counts;
- whether \(O_k\) is a refinement of \(O_{k-1}\);
- whether the operational partition changed at that prefix.

The full \(k=64\) endpoint must reproduce R3:
- 101 operational classes;
- R0 \(U=3.391442481659308, E=0\);
- Rfull \(U=0, E=4.69602035959104\);
- Rsupport64 identical in adequacy gap to R0.

## 4. M2-G — natural Git nested trajectory

### 4.1 Source and state banks

Reuse G5 exactly:

- public `git/git` frozen at `34f06850c16c7f7ac822b1adc71354f11b0f2ca3`;
- first 48 natural same-tree groups as discovery;
- next 48 disjoint groups as validation;
- validation remains the primary prospective split relative to original G5 action selection.

### 4.2 Full action set and nested order

Reuse the exact G5 target-selection algorithm and its resulting 12-target order:

1. candidate targets are unique second parents from the frozen merge-history pool;
2. targets are scored only by ancestry disagreement on the discovery bank;
3. sort by descending discovery ancestry disagreement, then lexical target ID;
4. take the first 12.

The nested contracts are the immutable prefixes

\[
\mathcal C_k=\{T_1,\ldots,T_k\},
\qquad k=0,\ldots,12.
\]

No merge outcome is used to alter this order.

### 4.3 Fixed representation partitions

For each split, compute once from the full frozen 12-target panel and keep fixed for all \(k\):

- **R0-fixed:** current tree only;
- **Rfull-fixed:** commit identity;
- **R1-fixed12:** tree + full 12-target ancestry vector;
- **R2-fixed12:** tree + full 12-target merge-base vector.

This choice is deliberate. Using only the first \(k\) ancestry or merge-base coordinates would make the representation itself change with the contract and therefore cannot test the fixed-representation T2 trajectory.

### 4.4 Outputs

For every split and every \(k\):

- operational class count;
- required and behaviorally equivalent within-pair counts;
- \(U_k/E_k\) for all four fixed representations;
- pairwise under-/over-refinement;
- adequacy and exact-match bits;
- first \(k\) at which each representation becomes adequate;
- first \(k\) at which each representation exactly matches the operational partition, if any;
- nested refinement and endpoint-regression checks.

At \(k=12\), validation must reproduce G5:
- 50 operational classes;
- 2 required / 46 equivalent pairs;
- R0 \(U=0.04166666666666696,E=0\);
- Rfull \(U=0,E=0.958333333333333\);
- R1-fixed12 \(U=E=0\);
- R2-fixed12 \(U=0,E=0.8124999999999991\).

Discovery is reported for completeness but remains selection-biased for ancestry-based representation analysis.

## 5. Interpretation rules

### 5.1 What M2 can support on the existing carriers

M2 can characterize:

- the empirical shape and breakpoints of contract-driven operational refinement;
- how fixed coarse/fine/intermediate implemented representations move relative to that refinement;
- whether a representation is only adequate for weak contracts or remains adequate as demand expands.

### 5.2 What M2 cannot establish by itself

Because the full R3/G5 endpoint results predate this protocol, M2 on these carriers alone cannot establish a new general cross-system law.

In particular, do not claim from M2-R/G alone:

- universal scaling of \(U/E\);
- universal ancestry sufficiency;
- universal relational support structure;
- a new entropy theorem;
- a causal effect of contract size independent of carrier/action semantics.

## 6. Confirmatory replication gate

Before promoting the trajectory into a paper-level cross-system empirical law, freeze and run **M2b** on fresh carriers not used to choose the current representation hypotheses.

Minimum confirmatory target:

1. at least one independently frozen exact relational carrier or state bank;
2. at least two additional mature Git repositories selected by structural criteria without merge-outcome inspection;
3. the same nested-contract construction rule;
4. fixed representation definitions frozen before operation outcomes;
5. full artifact hashes and endpoint-independent failure retention.

The confirmatory question is not whether monotonicity holds mathematically. It is whether nontrivial refinement events, adequacy transitions, and representation burden trajectories recur under new native systems.

## 7. Relation to the mother problem

M2 advances the mother question from existence to demand structure:

> Which distinctions become necessary, and at what operational demand, when a representation is required to support progressively richer native operations?

This is the bridge from the already recovered finite-contract claim to OACR as a representation science program.

## 8. Failure retention

Retain and report all of the following without redesigning the protocol:

- no operational refinement over a long contract prefix;
- all refinement concentrated in one action;
- an intermediate representation that remains over-refined throughout;
- an intermediate representation that becomes under-refined;
- carrier-specific trajectory shapes;
- endpoint mismatch with R3/G5, which invalidates the run rather than being repaired post hoc.
