# OACR-G1 Protocol v1 — Git Tree/History Operational Congruence

**Date:** 2026-09-28  
**Status:** preregistered exact native-system experiment  
**Carrier:** Git commit/tree representation and native merge operation

## 1. Question

Can two Git states have exactly the same complete tracked content tree while the same native future merge produces different registered behavior because their commit histories differ?

The experiment uses only Git's own persistent objects and merge semantics. No external relation ontology is imposed.

## 2. Registered state and observation

A state is a Git HEAD commit together with the repository object graph required by Git.

The registered READ abstraction is the complete HEAD tree object:

\[
A_0(z)=\operatorname{tree}(\operatorname{HEAD}(z)).
\]

Two states collide at A0 iff their tree object IDs are exactly identical.

This means every tracked path, mode, and blob reachable from HEAD is identical.

History/ancestry is deliberately not included in A0.

## 3. Registered operation

Freeze one target commit \(T\).

The registered native operation is:

\[
\Phi_T(z)=\texttt{git merge --no-commit --no-ff }T
\]

executed from a clean checkout of the state HEAD.

Record exactly:

- process exit code;
- stdout/stderr;
- whether Git reports already-up-to-date;
- whether a merge is in progress;
- unmerged index paths;
- working-tree hash after the command;
- index tree where available.

The same Git binary, repository object database, target commit, and command flags are used in both branches.

## 4. Exact construction A — conflict versus already-up-to-date

Create base commit \(O\) with one tracked file.

Create target \(T\) from \(O\), modifying that file to value `theirs`.

Create state \(A\) from \(O\), modifying the same file to value `ours`.

Create state \(B\) from \(T\), modifying the same file to value `ours`.

Therefore:

\[
\operatorname{tree}(A)=\operatorname{tree}(B)
\]

exactly.

But:

- \(T\) is not an ancestor of \(A\);
- \(T\) is an ancestor of \(B\).

Apply the same merge target \(T\):

- from \(A\), both sides changed the same line relative to the merge base, so the native merge is expected to conflict;
- from \(B\), the target is already an ancestor of HEAD, so Git is expected to report already up to date.

This is a one-step A0 operational-congruence violation if the exact pre-tree equality and divergent registered outcomes are observed.

## 5. Exact construction B — clean content divergence versus already-up-to-date

Create base \(O\) with two tracked files.

Create target \(T\) from \(O\), modifying file 1.

Create state \(A\) from \(O\), modifying file 2.

Create state \(B\) from \(T\), then restore file 1 to the base content while making the same file-2 modification as \(A\).

Again:

\[
\operatorname{tree}(A)=\operatorname{tree}(B).
\]

Apply the same merge target \(T\):

- from \(A\), Git should cleanly incorporate the target's file-1 change;
- from \(B\), \(T\) is already an ancestor, so the merge should be a no-op.

This construction is stronger than status-only divergence because the post-operation tracked content is expected to differ.

## 6. Candidate refinements

### A1 — target ancestry bit

Add:

\[
\mathbf 1[T\preceq \operatorname{HEAD}].
\]

### A2 — merge-base identity

Add the exact output of:

`git merge-base HEAD T`.

### A3 — reachable commit-parent subgraph

Add the reachable ancestry graph of HEAD and T within the constructed repository.

These are candidate refinements, not claimed universal minimal representations.

## 7. Validity conditions

Each witness is valid only if:

1. the two pre-state HEAD tree IDs are exactly equal;
2. working trees and indices are clean before the action;
3. the target commit object ID is identical across branches;
4. Git version is identical;
5. the merge command and flags are identical;
6. registered post-operation outcomes differ;
7. branch execution begins from fresh clean checkouts;
8. the result is reproducible on a duplicate execution.

## 8. First-run parameters

Run both registered constructions once, plus one duplicate replay of each branch.

No randomness is used.

Record:

- Git version;
- all commit IDs;
- all tree IDs;
- merge-base IDs;
- ancestry checks;
- exact command outputs;
- post-operation tree/index/conflict signatures.

## 9. Interpretation

If both constructions satisfy exact pre-tree equality and divergent merge behavior, then the result supports:

> Complete current tracked-content equality is insufficient for this registered native merge contract.

It also supports a pairwise operational necessity statement:

> Any representation adequate for the registered merge contract must distinguish each witnessed state pair somehow.

It does **not** support:

- history is universally necessary for all Git operations;
- commit ancestry is the unique minimal adequate encoding;
- merge behavior in arbitrary real repositories follows the same witness pattern;
- any claim about cultural or institutional continuity.

## 10. Native documentation anchor

Git documents merge-base as the best common ancestor used for merge reasoning. Git merge documents that changes since histories diverged are incorporated, true merges use 3-way merge, conflicts can stop the merge, and if all named commits are already ancestors of HEAD the command exits as already up to date.

Those documented native semantics motivate the experiment; the result itself is produced by the actual Git executable.
