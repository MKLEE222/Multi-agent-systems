# OACR-COMPOSE-G v1 — Natural Git Depth-2 Continuation Protocol

**Date:** 2026-09-29  
**Status:** prospectively frozen before any depth-2 merge outcome is inspected  
**Source bank:** accepted G5 held-out validation artifact  
**Role:** natural historical-state COMPOSE test

## 1. Scientific target

The G5 held-out validation bank already supplies natural same-tree commit pairs under one frozen 12-target merge panel.

Accepted H1 facts:

- 48 natural same-tree pairs;
- 2 pairs require H1 separation;
- 46 pairs are behaviorally equivalent under all 12 registered one-step merges.

Among the 46 H1-equivalent pairs, pre-H2 structural inspection shows:

- 39 pairs have different merge-base vectors across at least one registered target;
- all 39 retain identical target-ancestry vectors between pair endpoints;
- all 39 retain identical registered H1 merge outcome signatures between pair endpoints.

Thus the candidate bank contains latent historical structure that is **not required by the complete accepted H1 contract**.

The prospective question is:

\[
X \equiv_1 Y
\quad\text{but after a shared first merge}\quad
T_{t_1}(X) \not\equiv_1 T_{t_1}(Y)
\]

for a second registered merge target \(t_2\).

Equivalently:

\[
X \equiv_1 Y
\quad\land\quad
X \not\equiv_2 Y.
\]

## 2. Frozen source

Use exactly the accepted G5 validation source:

- remote: \`https://github.com/git/git.git\`;
- source HEAD: \`34f06850c16c7f7ac822b1adc71354f11b0f2ca3\`;
- validation artifact: \`oacr-g5-validation-v1\`;
- artifact ID: \`10954788549\`;
- original G5 run: \`36385706858\`;
- registered 12-target panel: unchanged.

No new repository, target pool, or current-state pair may be substituted based on H2 outcome.

## 3. Pair eligibility

A validation pair \((A,B)\) is eligible iff all of the following were established before this protocol:

1. \(tree(A)=tree(B)\);
2. \`required_separation == false\` in the accepted G5 artifact;
3. target-ancestry vectors are identical;
4. merge-base vectors differ for at least two registered targets.

The last condition is structural only and does not inspect any depth-2 execution.

Let

\[
D(A,B)=
\{t:
mergebase(A,t)\neq mergebase(B,t)
\}.
\]

Observed pre-H2 bank fact: every merge-base-different eligible pair has at least three differing target coordinates, so the two-target rule below is defined without outcome-based repair.

## 4. Pair selection

Order eligible pairs lexicographically by \((A,B)\).

If more than 16 are eligible, choose 16 evenly spaced pairs across that ordered list using the same deterministic evenly-spaced rule already used in OACR state/action selection.

No pair replacement is allowed after H2 outcomes are exposed.

A pair may be marked **H1_NOT_COMPOSABLE** only if the deterministic first-action eligibility rule below yields fewer than two eligible registered targets. Such a pair remains in the artifact and is not replaced.

## 5. First-action eligibility and selection

For each selected pair, iterate registered targets in lexical target-SHA order restricted to \(D(A,B)\).

For each target \(t\), rerun the original G5 native one-step merge from both \(A\) and \(B\) using:

\[
git\ merge\ --no-commit\ --no-ff\ t.
\]

A target is **composition-eligible** iff:

- both merges return exit code 0;
- neither side has unmerged paths;
- both sides produce a valid index tree;
- the two index trees are identical;
- the complete original G5 H1 signatures are identical.

This eligibility check is a re-execution of the already accepted H1 contract. It does not inspect any second action.

Choose:

- \(t_1\): lexicographically first composition-eligible target;
- \(t_2\): lexicographically second composition-eligible target.

If fewer than two such targets exist, classify the pair H1_NOT_COMPOSABLE.

## 6. Materializing the first transition

For each H1-composable selected pair:

1. checkout \(A\) or \(B\) in a fresh detached worktree;
2. execute the frozen merge \(t_1\) with \`--no-ff --no-commit\`;
3. verify the index-tree identity recorded above;
4. create a merge commit using deterministic metadata:
   - author/committer name: \`OACR COMPOSE\`;
   - author/committer email: \`oacr-compose@example.invalid\`;
   - author/committer date: \`2000-01-01T00:00:00Z\`;
   - commit message: \`OACR-COMPOSE-G step1\`.

The resulting commits are \(A_1\) and \(B_1\).

Acceptance condition at the intermediate state:

\[
tree(A_1)=tree(B_1).
\]

The commit IDs are expected to differ because their first parents differ; commit-ID difference is not itself an operational result.

## 7. Frozen second transition

From fresh checkouts of \(A_1\) and \(B_1\), execute:

\[
git\ merge\ --no-commit\ --no-ff\ t_2.
\]

Record the same native signature used in G5:

- exit code;
- already-up-to-date flag;
- merge-in-progress flag;
- unmerged path set;
- index tree when writable;
- tracked binary diff hash from HEAD.

Define H2 separation iff the complete native second-merge signatures differ.

A positive witness therefore has:

\[
tree(A)=tree(B),
\]

all 12 accepted H1 merge signatures equal,

\[
tree(A_1)=tree(B_1),
\]

but

\[
signature(A_1,t_2)\neq signature(B_1,t_2).
\]

## 8. Stronger continuation coordinates

For every H1-composable pair, also record before and after step 1:

- merge base with \(t_2\);
- whether \(t_2\) is an ancestor of the current head;
- whether current head is an ancestor of \(t_2\).

These coordinates are explanatory/certificate variables.

They are not allowed to redefine H2 separation after execution.

## 9. Primary outcomes

Report:

1. selected pairs;
2. H1_NOT_COMPOSABLE count;
3. H1-composable count;
4. H2-separated count;
5. H2-equivalent count;
6. exact native signature differences for each positive;
7. merge-base/ancestry transition certificate for each positive.

A zero-positive result is accepted and no pair/target retuning follows.

## 10. Independent verifier

A verifier must independently reconstruct from:

- the pinned \`git/git\` source HEAD;
- the accepted G5 artifact;
- this protocol's deterministic pair and target selection rules.

It must then rerun:

- H1 eligibility;
- deterministic merge-commit construction;
- H2 native merge signatures.

Producer-generated H2 signatures cannot be trusted without replay.

## 11. Claim boundary

A positive supports:

> natural same-tree Git histories can be equivalent under a complete registered one-step merge panel yet diverge after a shared merge changes the historical context of a later merge.

It does not by itself establish:

- a universal Git law;
- noncommutativity across arbitrary operations;
- authority/permission qualification;
- learned-system transfer;
- cultural continuity.

A negative remains informative because it tests whether the H1-excess merge-base distinctions become necessary under the first frozen depth-2 continuation regime.

## 12. Relation to OACR

If positive, this is the first natural candidate for:

\[
U_1(R)=0
\quad\text{but}\quad
U_2(R)>0
\]

for an H1-sufficient representation that omits historical distinctions relevant only after composition.

Representation redesign is a later phase and must not be post-hoc fit to the positive witness before a separate protocol is frozen.
