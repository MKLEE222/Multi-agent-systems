# OACR-G4 Protocol v1 — Natural Git Over-Refinement Controls

**Date:** 2026-09-28  
**Status:** preregistered natural control audit  
**Carrier:** frozen public `git/git` history at `34f06850c16c7f7ac822b1adc71354f11b0f2ca3`

## 1. Question

G2/G3 test current-tree equality with future merge divergence. G4 asks the complementary question:

> Do naturally occurring Git states with different histories but identical current trees sometimes remain behaviorally equivalent under a frozen native merge contract?

A positive control here is evidence that **full history can over-refine a finite registered merge contract**.

## 2. Frozen current observation

[
A_0(z)=operatorname{tree}(operatorname{HEAD}(z)).
]

Candidate pairs must have distinct commit IDs but exactly identical tree IDs.

## 3. Frozen action alphabet

Independently rediscover the tree-preserving merge candidates from the first 10,000 merge commits using the G2 structural rule, without executing merges.

Take the second-parent target commits from the first four such candidates in deterministic history order:

[
mathcal A={T_1,T_2,T_3,T_4}.
]

This action alphabet is frozen from repository structure, not pair outcomes.

## 4. Natural same-tree pair bank

Enumerate the first 20,000 commits from the frozen repository history.

Group commits by exact tree ID. For every group with at least two distinct commits, generate deterministic adjacent pairs after sorting by commit ID.

Take the first 32 pairs in deterministic tree-ID/pair order.

No commit is synthesized or rewritten.

## 5. Registered behavior

For each pair ((A,B)) and each (T_k), execute from fresh clean checkouts:

[
	exttt{git merge --no-commit --no-ff }T_k.
]

Record the same native outcome signature as G2:

- exit code;
- already-up-to-date;
- merge-in-progress;
- unmerged paths;
- index tree when available;
- tracked working-tree delta hash.

Two states are H=1 equivalent on the registered contract iff all four outcome signatures match.

## 6. Candidate feature families

### Ffull — full-history identity proxy

Distinct HEAD commit IDs / reachable histories separate every candidate pair by construction.

### F1 — target-ancestry vector

For each (T_k):

[
mathbf1[T_kpreceq HEAD].
]

### F2 — merge-base vector

Exact `git merge-base HEAD T_k` for each action.

Report whether F1/F2 separate:

- behaviorally required pairs;
- behaviorally equivalent pairs.

This directly exposes over-refinement.

## 7. Outputs

- number of same-tree groups/pairs available;
- 32-pair registered bank or all available if fewer;
- H=1 required-separation count;
- H=1 behaviorally equivalent control count;
- F1/F2 TP/FP/FN/TN against required separation;
- examples of natural over-refinement controls and required separations.

## 8. Boundary

This is a finite-contract natural control study.

It does not claim:
- that history is globally unnecessary when a pair is H=1 equivalent;
- that F1 or F2 is globally minimal;
- prevalence across Git repositories;
- any L2 claim about identity, provenance, or continuity.
