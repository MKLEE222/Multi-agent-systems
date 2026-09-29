# OACR-COMPOSE-G v1 — G5 Natural Git H2 Continuation Protocol

**Date:** 2026-09-29  
**Status:** prospectively frozen before any two-merge outcome is executed on the G5 held-out validation pairs  
**Source bank:** accepted G5 validation artifact from run 36385706858  
**Scientific role:** natural-history COMPOSE test

## 1. Starting bank

Use only the already frozen G5 **validation** split.

The source artifact contains 48 natural same-tree commit pairs under one frozen 12-target merge panel.

Existing H1 result:

- 2 pairs are separated by at least one registered one-step merge;
- 46 pairs are behaviorally equivalent across the complete 12-target H1 panel.

The COMPOSE-G bank is exactly those 46 H1-equivalent pairs.

No pair may be added, replaced, or selected using H2 outcomes.

## 2. Primary question

Does there exist a natural same-tree pair \(A,B\) such that

\[
A \equiv_1 B
\]

under the complete frozen G5 H1 panel, but for an ordered pair of already frozen merge targets \((t_1,t_2)\),

\[
A \not\equiv_2 B?
\]

The intended mechanism is historical rather than current-content divergence:

> two commits can have the same current tree and the same complete registered one-step merge behavior, yet a common first merge can create history states whose later merge behavior differs.

## 3. Action universe

Reuse the exact 12 G5 targets already frozen before validation.

No new target is introduced.

For each of the 46 H1-equivalent pairs, consider every ordered pair

\[
(t_1,t_2),\qquad t_1\ne t_2,
\]

from the frozen 12-target set.

There are

\[
12\times 11=132
\]

registered H2 target sequences per pair before first-step eligibility filtering.

## 4. Native first-step persistence

The original G5 H1 runner used \`git merge --no-commit --no-ff\` and aborted after recording the one-step signature.

COMPOSE-G must instead persist the first transformation.

For each starting commit \(c\) and first target \(t_1\):

1. fresh detached checkout at \(c\);
2. execute native merge of \(t_1\);
3. if the merge is already up to date, retain the current HEAD as the H1 successor;
4. if the merge succeeds and creates staged tree changes, create a merge commit with:
   - fixed author name/email;
   - fixed committer name/email;
   - fixed author/committer timestamp;
   - fixed message derived only from registered target identity;
5. if the merge conflicts or cannot produce a valid index tree, mark that sequence H2-ineligible for both sides unless both sides satisfy the same eligibility rule.

The deterministic metadata prevents irrelevant wall-clock identity from entering the continuation state.

The persisted first-step commit identity itself is **not** an outcome metric.

## 5. H1 continuation gate

A sequence \((t_1,t_2)\) is eligible only if, on both members of the pair:

- first-step merge has no unmerged paths;
- a valid H1 successor state exists;
- the first-step registered operational signature is equal across A and B;
- the H1 successor tracked tree is equal across A and B.

This gate uses only first-step information.

If no sequence for a pair survives, retain the pair as H2-ineligible; do not replace it.

## 6. H2 native outcome

From each persisted H1 successor, execute native merge of \(t_2\) with the same observation contract as G5 H1:

- exit code;
- already-up-to-date status;
- merge-in-progress status;
- unmerged path set;
- index tree when writable;
- tracked delta hash relative to the persisted H1 HEAD.

Hash this payload to form the H2 operational signature.

The pair has delayed continuation divergence for \((t_1,t_2)\) iff:

\[
\text{sig}_{H2}(A;t_1,t_2)
\ne
\text{sig}_{H2}(B;t_1,t_2)
\]

after passing the H1 continuation gate.

## 7. Strong witness condition

A promoted COMPOSE-G witness must satisfy all of:

1. starting trees equal;
2. complete original 12-target H1 signatures equal;
3. chosen \(t_1\) H1 signatures equal;
4. persisted H1 successor trees equal;
5. H2 signatures under common \(t_2\) differ.

Thus the result cannot be explained by an already visible current-content difference or by an H1 behavioral difference.

## 8. Full outcome matrix

Execute the complete registered H2 sequence set subject only to the H1 continuation gate.

Report:

- total 46 source pairs;
- H2-eligible pairs;
- H2-eligible ordered sequences;
- pairs with at least one delayed divergence;
- total delayed-divergent sequences;
- H2 operational partition;
- per-pair activation count.

Positive and zero results are both accepted.

No target/pair retuning follows a zero result.

## 9. Independent verification

Verifier must independently reconstruct from:

- source repository at the frozen source head;
- the G5 validation pair list;
- the frozen 12 target list;
- the deterministic H1 persistence rule.

It must not trust producer H2 signatures.

For every promoted witness, independently replay both merge steps and verify all five strong-witness conditions.

## 10. Representation consequence

Existing G5 H1 exact representation is tree + frozen target-ancestry vector.

If H2 divergence exists among pairs not separated by that representation, then the H1-exact representation under-refines the H2 continuation quotient:

\[
U_1(R_{\rm ancestry})=0
\]

but

\[
U_2(R_{\rm ancestry})>0.
\]

A later redesign may add only the historical distinction(s) needed to close the H2 contract.

No redesign feature may be chosen from the H2 outcome before a separate development/validation split or preregistered structural rule is established.

## 11. Boundaries

A positive result would establish a natural Git instance of delayed continuation divergence.

It would not establish:

- universal Git history dependence;
- noncommutativity as the cause unless separately tested;
- learned-system transfer;
- cultural/institutional authority inheritance.

A negative result remains informative: the frozen G5 H1 quotient would have survived this registered two-merge continuation panel.

## 12. No contamination rule

The H2 experiment must not inspect any second-step native merge outcome before this protocol is committed.

The previously observed H1 artifact is legitimate input because the scientific question is explicitly conditional on H1 equivalence.
