# OACR-COMPOSE-G v3 — Endogenous Affordance Development Protocol

**Date:** 2026-09-29  
**Status:** developmental mechanism search only; no confirmatory claim may be made from this bank  
**Carrier:** pinned \`git/git\` at \`34f06850c16c7f7ac822b1adc71354f11b0f2ca3\`  
**Development bank:** the 48 G5 discovery same-tree pairs  
**Purpose:** determine whether a COMPOSE-native action generator is viable before freezing a fresh untouched validation bank.

## 1. Why a new study is justified

COMPOSE-G v2 did not execute any H2 merge.

Its verified result was:

\[
39\text{ H1-equivalent pairs}
\rightarrow
0\text{ shared materializable }t_1.
\]

The inherited 12-target G5 WRITE panel was therefore an inadequate carrier for the COMPOSE question.

This protocol does not retune that failed frozen experiment.

It starts a distinct developmental study whose scientific object is the state-dependent future action set itself.

## 2. Frozen ambient target universe

Construct a state-independent ambient candidate universe \(P\) from the pinned repository:

1. enumerate two-parent merge commits in native \`git rev-list --merges --all --parents\` order;
2. traverse the first 1,024 two-parent merge commits;
3. collect unique second-parent commit IDs in first-occurrence order;
4. retain the first 96 unique targets.

No pair state, merge outcome, H1 equality, or H2 result influences \(P\).

The size 96 is developmental and is not a paper-level constant.

## 3. Current qualified merge set

For state \(S\) and target \(t\in P\), execute the native primitive

\[
git\ merge\ --no\text{-}commit\ --no\text{-}ff\ t
\]

from a fresh detached checkout.

Define \(t\) as **qualified/materializable** at \(S\) iff:

- exit code is 0;
- no unmerged paths exist;
- \`MERGE_HEAD\` exists;
- \`git write-tree\` returns a valid tree.

This excludes:

- already-up-to-date no-op merges;
- conflicting merges;
- failed/non-materializable transitions.

Define the endogenous action set:

\[
\mathcal A_P(S)
=
\{t\in P:t\text{ is qualified at }S\}.
\]

For every qualified target record the full G5-style native signature:

- exit code;
- already-up-to-date flag;
- merge-in-progress flag;
- unmerged path set;
- index tree;
- tracked binary-diff hash.

## 4. Developmental H1-equivalence gate

For each of the 48 G5 discovery same-tree pairs \((A,B)\):

1. require
   \[
   tree(A)=tree(B);
   \]
2. compute \(\mathcal A_P(A)\) and \(\mathcal A_P(B)\);
3. retain the pair as **v3-H1-equivalent** only if
   \[
   \mathcal A_P(A)=\mathcal A_P(B);
   \]
4. for every target in the common qualified set, require identical complete native signatures.

Thus the pair has:

- same current READ;
- same currently qualified operation set under \(P\);
- same one-step native behavior for every qualified operation.

The protocol does not select actions merely because one particular target happens to match.

## 5. Developmental COMPOSE search

For every v3-H1-equivalent pair with nonempty common action set:

1. sort the common qualified targets lexicographically;
2. consider at most the first four targets as candidate first operations \(t_1\);
3. materialize deterministic native merge commits \(A_1,B_1\) using the already frozen OACR COMPOSE metadata;
4. require
   \[
   tree(A_1)=tree(B_1).
   \]
5. from each intermediate state, recompute the full endogenous action sets
   \[
   \mathcal A_P(A_1),\mathcal A_P(B_1)
   \]
   and the complete native signatures of every qualified target.

A developmental delayed-continuation witness exists if either:

### Qualification divergence

\[
\mathcal A_P(A_1)\neq\mathcal A_P(B_1).
\]

or, if the qualified sets remain equal:

### Outcome divergence

there exists a common qualified \(t_2\in P\) such that

\[
signature(A_1,t_2)\neq signature(B_1,t_2).
\]

This is exactly a failure of depth-1 closure under an endogenous continuation interface.

## 6. Search discipline

This is a developmental bank. The output may be used to decide whether the mechanism is viable and to design a later frozen validation rule.

It may **not** be cited as prospective evidence because:

- the discovery same-tree bank has been used previously;
- the first-four \(t_1\) cap and ambient pool size are developmental engineering choices;
- successful developmental sequences may inform the later hypothesis.

However:

- all failures are retained;
- no pair is replaced inside this run;
- all 48 discovery pairs are reported;
- the complete ambient target universe is persisted;
- no manual pair/target choice is permitted.

## 7. Fresh-validation condition

A confirmatory successor is authorized only if development establishes at least one exact delayed-continuation witness.

The validation study must then freeze, before any validation merge outcome:

- a fresh untouched same-tree pair bank;
- ambient target-generation rule;
- exact \(\mathcal A_P\) qualification rule;
- deterministic pair eligibility;
- deterministic \(t_1\) selection;
- H2 definition;
- independent verifier.

Recommended untouched bank:

> same-tree groups 97--144 from the same first-20,000-commit enumeration, because G5 used groups 1--96.

No developmental positive pair or sequence may be moved into validation.

## 8. Interpretation boundary

A developmental positive would establish only that Git can instantiate the mechanism.

The eventual confirmatory target is stronger:

> two natural histories with identical current content, identical currently qualified native merge set, and identical native behavior for every qualified merge can acquire different future merge affordances after the same first merge.

This directly operationalizes an endogenous future-operation space.

It is not a claim that Git merge theory or transition composition is itself novel.
