# OACR-COMPOSE-G v2 Structural Preflight Protocol

**Date:** 2026-09-29  
**Status:** frozen before any v2 second-merge outcome is executed  
**Supersedes only the v1 pair/sequence construction rule; carrier, source head, G5 H1 contract, and native merge semantics remain frozen**

## 1. Why v2 exists

COMPOSE-G v1 used only targets whose current merge base differed between the two endpoints and required two such targets to be real materializable one-step merges.

Clean verified v1 result:

- accepted G5 H1-equivalent pairs: 46;
- H1-equivalent pairs with merge-base differences: 39;
- selected pairs: 16;
- H1_NOT_COMPOSABLE: 16;
- H2 merges executed: 0.

Thus v1 is a construction/preflight underpower result, not a COMPOSE negative.

The failure identifies an unnecessary design restriction: the first action \(t_1\) need not itself be a merge-base-difference coordinate. Its scientific role is to create a new but currently equivalent history. The second target \(t_2\) is where that new history may alter future continuation.

## 2. Frozen source

Unchanged:

- repository: \`git/git\`;
- source HEAD: \`34f06850c16c7f7ac822b1adc71354f11b0f2ca3\`;
- accepted G5 validation artifact: run \`36385706858\`, artifact \`10954788549\`;
- same 48 natural validation pairs;
- same 12 registered G5 merge targets.

No new repository, head, pair bank, or target pool may be introduced in v2.

## 3. Pair bank

Use all accepted G5 validation pairs satisfying:

1. same current tree;
2. \`required_separation == false\` under the complete 12-target H1 contract;
3. identical target-ancestry vectors;
4. at least one differing current merge-base coordinate.

The expected preflight bank is 39 pairs.

No pair is selected using v2 second-merge outcomes because v2 preflight executes no second merge.

## 4. H1 materializable first actions

For every pair and every one of the 12 frozen targets \(t_1\), rerun the original G5 native one-step merge.

\(t_1\) is materializable iff on both pair endpoints:

- exit code is 0;
- no unmerged paths exist;
- \`MERGE_HEAD\` exists;
- a valid index tree exists;
- the complete native H1 signatures match;
- the two index trees are identical.

This is an H1 replay only.

For each materializable \(t_1\), create deterministic native merge commits \(A_1,B_1\) with the same metadata rule frozen in v1.

Require:

\[
tree(A_1)=tree(B_1).
\]

If the trees differ, the candidate is rejected before any v2 H2 execution.

## 5. Outcome-blind second-target structural scan

For every materialized \(A_1,B_1\) and every frozen target \(t_2\neq t_1\), compute only:

- \(mergebase(A_1,t_2)\);
- \(mergebase(B_1,t_2)\);
- whether \(t_2\) is an ancestor of \(A_1\) / \(B_1\);
- whether \(A_1\) / \(B_1\) is an ancestor of \(t_2\).

Do **not** execute:

\[
git\ merge\ t_2.
\]

A sequence \((A,B,t_1,t_2)\) is structurally eligible iff the post-step1 continuation context differs between \(A_1\) and \(B_1\) on at least one registered structural coordinate:

\[
mergebase(A_1,t_2)\neq mergebase(B_1,t_2),
\]

or one of the two ancestry-direction predicates differs.

Additionally reject the uninformative case in which \(t_2\) is already an ancestor of both \(A_1\) and \(B_1\).

This gate uses only history structure before the second merge outcome.

## 6. Preflight outputs

Report:

- number of 39-bank pairs reconstructed;
- number with at least one materializable \(t_1\);
- total materializable \(t_1\) count;
- number with at least one structurally eligible \((t_1,t_2)\);
- total structurally eligible sequences;
- per-sequence pair, \(t_1\), \(t_2\), intermediate tree, and structural context.

No second-merge signature is permitted in the artifact.

## 7. Gate to v2 H2 execution

Proceed to a separately frozen H2 protocol only if preflight yields:

- at least 3 distinct natural pairs with structurally eligible sequences;
- at least 8 eligible sequences total.

If the gate fails, retain the result as preflight underpower and do not execute H2 or replace the carrier.

## 8. Future deterministic H2 selection rule

If the gate passes, the later H2 protocol must choose sequences without looking at H2 outcomes.

Provisional rule to be frozen separately:

1. order eligible pairs lexicographically by \((A,B)\);
2. select up to 16 evenly spaced eligible pairs;
3. within each pair order eligible sequences lexicographically by \((t_1,t_2)\);
4. choose the first sequence.

This section does not itself authorize second-merge execution.

## 9. Boundary

A successful preflight is not a scientific COMPOSE positive. It only establishes that the native carrier contains outcome-blind, H1-equivalent history transitions whose post-step1 structural context for a later frozen target differs.

Scientific separation still requires a separately frozen native \(t_2\) merge and independent replay.
