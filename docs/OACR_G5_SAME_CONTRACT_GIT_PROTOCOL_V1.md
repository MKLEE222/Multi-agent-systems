# OACR-G5 Protocol v1 — Same-Contract Git Adequacy Matrix with Held-Out Validation

**Date:** 2026-09-28  
**Status:** preregistered natural same-contract experiment  
**Carrier:** public `git/git` frozen at `34f06850c16c7f7ac822b1adc71354f11b0f2ca3`

## 1. Purpose

G3 used pair-specific future targets and G4 contained only behaviorally equivalent controls.

G5 creates one shared native merge contract and evaluates both a discovery bank and a held-out validation bank of natural same-tree states.

The central question is:

> Under the same current-tree observation and the same global merge-action alphabet, which historical distinctions are actually required, and which over-refine the contract?

## 2. Natural state banks

Enumerate the first 20,000 commits in the frozen repository.

Group distinct commits by exact tree object ID.

From each group with at least two commits, choose the lexicographically first two commit IDs, yielding one natural same-tree pair per group.

Sort groups by tree ID.

Freeze:

- **discovery bank:** first 48 groups;
- **validation bank:** next 48 groups.

The validation bank is not used to select actions.

Every pair therefore has:

[
operatorname{tree}(A)=operatorname{tree}(B)
]

with distinct natural commit histories.

Across different groups, different tree IDs remain part of the registered current observation.

## 3. Outcome-blind shared action selection

Construct a candidate target pool from the unique second-parent commits of the first 256 two-parent merge commits in repository history order.

For each candidate target (T), inspect only the native ancestry relation on the **discovery** pairs and compute:

[
D(T)=#{(A,B): mathbf1[Tpreceq A]
eqmathbf1[Tpreceq B]}.
]

No merge operation is executed during action selection.

Sort targets by:

1. descending (D(T));
2. lexical target commit ID.

Freeze the first 12 targets as one global action alphabet:

[
mathcal A={T_1,ldots,T_{12}}.
]

This is a deliberate stress-test contract. Because action selection uses ancestry diversity on discovery states, F1 results on the discovery bank are selection-biased. The validation bank provides the prospective test.

## 4. Registered observation and action

Current READ:

[
O_0(z)=operatorname{tree}(operatorname{HEAD}(z)).
]

For every state and every target (T_k), execute from a clean checkout:

[
	exttt{git merge --no-commit --no-ff }T_k.
]

Record:

- exit code;
- already-up-to-date bit;
- merge-in-progress bit;
- unmerged path set;
- index tree when available;
- tracked working-tree binary-diff hash.

The H=1 operational signature is:

[
B_1(z)=
left(
O_0(z),
[operatorname{Outcome}(z,T_k)]_{k=1}^{12}
ight).
]

## 5. Candidate representation partitions

### R0 — current tree only

[
R_0(z)=operatorname{tree}(z).
]

### Rfull — full commit identity

[
R_{m full}(z)=operatorname{commitID}(z).
]

This is a deliberately fine proxy for full history identity.

### R1 — tree + target-ancestry vector

[
R_1(z)=
left(
operatorname{tree}(z),
[mathbf1(T_kpreceq z)]_{k=1}^{12}
ight).
]

### R2 — tree + merge-base vector

[
R_2(z)=
left(
operatorname{tree}(z),
[operatorname{mergebase}(z,T_k)]_{k=1}^{12}
ight).
]

All candidate representations are computed before executing merge outcomes for the evaluated split.

## 6. Directional adequacy gap

For discovery and validation separately, under a uniform distribution over registered states, compute:

[
U(R)=H(O_1mid R),
qquad
E(R)=H(Rmid O_1).
]

Also report exact pairwise under-/over-refinement counts.

The validation bank is the primary prospective result for R1/R2.

## 7. Required strong pattern

The strongest useful validation result has all of the following under the same 12-target contract:

1. some same-tree pairs are operationally separated;
2. some same-tree pairs remain operationally equivalent;
3. R0 has (U>0);
4. Rfull has (E>0);
5. an intermediate native feature such as R1 reduces both errors relative to the extremes.

This pattern is not assumed in advance.

## 8. Failure modes are retained

If the validation bank has only positives or only negatives, report that result.

If R1/R2 fail to improve the directional gap, retain the failure.

No action target is changed after merge outcomes are observed.

## 9. Boundaries

G5 is a natural finite-contract experiment on one repository.

It does not establish:
- universal minimality of ancestry or merge-base;
- prevalence across repositories;
- a general theory of identity/provenance;
- novelty of partition information measures.

A later replication must freeze the same selection algorithm on additional repositories.
