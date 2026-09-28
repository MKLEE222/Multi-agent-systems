# OACR-G2 Protocol v1 — Natural Tree-Preserving Merge Witnesses

**Date:** 2026-09-28  
**Status:** preregistered natural-history search  
**Carrier:** public `git/git` repository, interpreted only through Git's native commit/tree/merge semantics

## 1. Motivation

OACR-G1 is an exact constructed positive control. The next hard gate is natural occurrence:

> Do naturally produced repository histories contain exact current-content collisions that require different future merge behavior?

G2 does not invent a semantic relation type. It searches native Git history for a structural configuration already produced by real repository development.

## 2. Natural candidate definition

Search the real repository history for a two-parent merge commit \(B\) with:

- first parent \(A\);
- second parent \(T\);
- exact tree equality:

\[
\operatorname{tree}(A)=\operatorname{tree}(B);
\]

- \(T\) is not already an ancestor of \(A\).

Such a commit is a **tree-preserving merge candidate**.

The current tracked content of \(A\) and \(B\) is therefore exactly identical, while \(B\)'s history contains \(T\) and \(A\)'s does not.

No candidate is created by OACR; the commit triple must already exist in the fetched public history.

## 3. Registered observation

[
A_0(z)=\operatorname{tree}(\operatorname{HEAD}(z)).
]

A0 equality is exact Git tree-object identity.

## 4. Registered action

For the candidate's natural second parent \(T\), execute the same native action:

[
\Phi_T(z)=\texttt{git merge --no-commit --no-ff }T.
]

Run once from \(A\) and once from \(B\), starting from clean checkouts.

Because \(T\) is a parent/ancestor of \(B\), merging \(T\) from \(B\) should be already up to date under Git's native semantics.

The branch from \(A\) is not required to have any particular outcome. It is accepted as an operational-necessity witness if its registered outcome differs from the branch from \(B\).

## 5. Registered outcome

Record:

- exit code;
- command output;
- already-up-to-date bit;
- merge-in-progress bit;
- unmerged path set;
- index tree where available;
- working-tree tracked-file content hash.

A candidate is a valid G2 witness iff:

1. pre-tree equality is exact;
2. target commit is identical;
3. checkouts are clean;
4. target is not an ancestor of A and is an ancestor of B;
5. same merge command is executed;
6. registered outcomes differ.

## 6. Search order and stopping rule

Repository:

`https://github.com/git/git.git`

Fetch the public repository using Git in the workflow and freeze:

- remote URL;
- fetched HEAD commit;
- Git version;
- search command.

Enumerate at most the first 10,000 merge commits returned by:

`git rev-list --merges --all --max-count=10000 --parents`

in Git's deterministic output order.

Test only two-parent merges.

Stop after 16 valid witnesses or after all enumerated candidates have been tested.

The first run is a purposive natural-witness search, not a prevalence estimate.

## 7. Anti-confounds

- Do not rewrite or synthesize commits.
- Do not change merge strategy or use historical recorded conflict resolutions.
- Do not use rerere.
- Start each branch test from a fresh reset/clean state.
- Disable user-level Git configuration that could alter merge behavior where practical.
- Record the exact source commit IDs and tree IDs.
- A failed/unsupported historical checkout is recorded and skipped, not converted into a witness.

## 8. Candidate refinements

For each valid pair record:

- A1: whether target is ancestor of HEAD;
- A2: merge-base identity;
- A3: parent-graph difference.

These features are explanatory candidates only.

## 9. Interpretation

A valid natural witness supports:

> In an actual public repository history, complete tracked-content equality did not suffice for the registered future merge contract.

It does not support:

- prevalence in Git repositories;
- a universal minimal history representation;
- broader semantic claims about provenance, identity, or cultural continuity.

## 10. Failure is informative

If no natural witness is found under the frozen search:

- G1 remains an exact native-system positive control;
- G2 reports zero natural witnesses for this repository/search window;
- the search window may later be expanded only in a separately registered run.
