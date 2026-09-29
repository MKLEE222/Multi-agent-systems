# OACR-COMPOSE-G v2 H2 Execution Protocol v1

**Date:** 2026-09-29  
**Status:** prospectively frozen before the v2 structural-preflight result is read and before any v2 second-merge outcome  
**Parent preflight:** \`docs/OACR_COMPOSE_G_V2_STRUCTURAL_PREFLIGHT_PROTOCOL_2026-09-29.md\`  
**Parent preflight run:** \`36569506953\`  
**Role:** native historical-state test of delayed continuation divergence

## 1. Authorization condition

This protocol authorizes second-merge execution **only if** the first complete artifact from parent preflight run \`36569506953\`:

1. is independently verifier-passed;
2. reports \`second_merge_outcomes_executed == 0\`;
3. reports \`passes_H2_gate == true\`, where the frozen gate is:
   - at least 3 distinct natural pairs with structurally eligible sequences;
   - at least 8 structurally eligible sequences total.

If any condition fails, H2 execution is blocked and this protocol produces no scientific outcome.

## 2. Frozen source and H1 contract

Unchanged from G5 / COMPOSE-G v2 preflight:

- repository: \`git/git\`;
- source HEAD: \`34f06850c16c7f7ac822b1adc71354f11b0f2ca3\`;
- accepted G5 validation run: \`36385706858\`;
- accepted G5 validation artifact: \`oacr-g5-validation-v1\`, artifact ID \`10954788549\`;
- same 48 natural validation pairs;
- same frozen 12-target merge alphabet;
- same native merge signature as G5.

No repository, pair, target, or current observation may be changed after this protocol.

## 3. Eligible pair/sequence universe

Use exactly the independently verified v2 preflight artifact.

A pair is H2-eligible iff its preflight row has at least one
\`eligible_t2_sequence\`.

No pair can be introduced from outside that verified preflight artifact.

A sequence is H2-eligible iff the preflight recorded all of the following before any second merge:

- the pair was G5 H1-equivalent;
- \(t_1\) was a shared materializable real merge on both endpoints;
- the H1 native signatures for \(t_1\) were identical;
- the two step-1 merge index trees were identical;
- deterministic merge commits \(A_1,B_1\) had identical trees;
- for frozen target \(t_2\neq t_1\), the post-step1 merge-base/ancestry context differed on at least one registered structural coordinate;
- \(t_2\) was not already an ancestor of both intermediate heads.

## 4. Frozen deterministic selection

This rule is frozen before the preflight result is read.

### Pair selection

1. order all H2-eligible pairs lexicographically by \((A,B)\);
2. if there are at most 16 eligible pairs, select all;
3. otherwise select 16 evenly spaced pairs using the same deterministic evenly-spaced index rule used elsewhere in OACR.

No pair replacement is allowed after second-merge outcomes are exposed.

### Sequence selection within pair

For each selected pair:

1. flatten all preflight-eligible sequences;
2. sort lexicographically by \((t_1,t_2)\);
3. select the first sequence.

Exactly one H2 sequence is executed per selected pair.

This is intentionally conservative. It prevents outcome-based search over the structurally eligible sequence set.

## 5. Mandatory pre-H2 replay

Before executing \(t_2\), independently reconstruct each selected sequence from the pinned repository and accepted G5 artifact.

For each selected \((A,B,t_1,t_2)\):

1. verify \(tree(A)=tree(B)\);
2. verify the complete accepted 12-target G5 H1 signatures of \(A,B\) were equal;
3. rerun \(t_1\) from \(A\) and \(B\);
4. require:
   - exit code 0 on both;
   - no unmerged paths;
   - \`MERGE_HEAD\` on both;
   - valid index tree on both;
   - identical complete H1 native signatures;
   - identical index trees;
5. materialize deterministic merge commits using the frozen v1 metadata rule;
6. require:
   \[
   tree(A_1)=tree(B_1);
   \]
7. independently recompute the preflight \(t_2\) merge-base/ancestry contexts and require exact match to the verified preflight artifact.

Any mismatch blocks H2 for that pair and is an implementation/integrity failure. The pair is not replaced.

## 6. Native H2 execution

Only after all checks above pass, from fresh checkouts of \(A_1\) and \(B_1\), execute:

\[
git\ merge\ --no\text{-}commit\ --no\text{-}ff\ t_2.
\]

Record the exact G5 native signature:

- exit code;
- already-up-to-date flag;
- merge-in-progress flag;
- unmerged path set;
- index tree when writable;
- tracked working-tree binary-diff hash.

Define:

\[
H2\_separated(A,B,t_1,t_2)
=
\mathbf 1[
signature(A_1,t_2)\neq signature(B_1,t_2)
].
\]

The H2 definition is frozen and cannot be redefined from explanatory structural coordinates after outcome.

## 7. Primary outcomes

Report:

- verified eligible-pair count;
- verified eligible-sequence count;
- selected-pair count;
- H2 executions attempted;
- H2 integrity failures;
- H2-separated count;
- H2-equivalent count;
- exact native signature coordinates responsible for each separation.

A positive witness must satisfy:

\[
\boxed{
\Sigma_1(A)=\Sigma_1(B)
}
\]

under the complete accepted G5 12-target H1 contract,

\[
tree(A_1)=tree(B_1),
\]

but:

\[
\boxed{
signature(A_1,t_2)\neq signature(B_1,t_2).
}
\]

This is the native Git instance of delayed continuation divergence.

## 8. Independent verifier

The verifier must independently reconstruct from:

- pinned \`git/git\` source;
- accepted G5 validation artifact;
- verified v2 structural-preflight artifact;
- this frozen selection rule.

It must independently:

1. reproduce eligible pair/sequence selection;
2. rerun H1 \(t_1\) checks;
3. recreate deterministic \(A_1,B_1\);
4. verify equal intermediate trees;
5. recompute the frozen structural context;
6. execute \(t_2\) from both intermediates;
7. recompute complete native H2 signatures.

Producer H2 signatures are not accepted without exact independent replay.

## 9. Outcome discipline

### Positive

At least one selected pair passes all integrity checks and has unequal H2 signatures.

Accepted scope:

> A natural same-tree history pair can be equivalent under the complete frozen one-step merge contract yet diverge after a shared first merge changes the historical context of a later merge.

### Zero positive

If all selected, integrity-valid H2 executions remain equivalent, retain a prospective negative for this deterministic selected-sequence protocol.

Do not:

- search additional eligible sequences after seeing zero positives;
- change pair selection;
- change target ordering;
- add new repositories;
- broaden the merge signature.

A later broader protocol would require a new scientific justification independent of this outcome.

## 10. Representation consequence

If a positive exists, the accepted G5 H1-sufficient representation may be tested at depth 2 without post-hoc redesign.

For any positive pair already merged by the accepted H1 representation:

\[
U_1=0
\]

on that pair under the H1 contract, while the observed H2 separation implies:

\[
U_2>0
\]

for the unchanged representation.

A depth-2 redesign/certificate is a separate later protocol and is not authorized here.

## 11. Boundaries

Even a positive does not establish:

- universal Git behavior;
- arbitrary-operation noncommutativity;
- qualification/authority semantics;
- learned-state transfer;
- cultural continuity.

Its role is a prospective native-history replication of the broader continuation mechanism, complementary to:

- relational deletion as compositionally closed negative/control;
- SQEC as controlled qualification-positive seed.
