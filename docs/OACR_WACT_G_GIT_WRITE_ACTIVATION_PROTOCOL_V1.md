# OACR-WACT-G v1 — Git WRITE-Activation Preflight and Native Replay Protocol

**Date:** 2026-09-29
**Status:** prospectively frozen before any WACT-G native merge outcome
**Role:** cross-substrate replication of WRITE-activation after WACT-R.

## 1. Target phenomenon

For a natural same-tree commit pair A,B, hold the states and current READ fixed:

tree(A)=tree(B).

Select two native merge targets before executing merge outcomes:

- t-: ancestor of both A and B;
- t+: ancestor of exactly one of A,B.

Define nested WRITE contracts:

W- = {merge(t-)},

W+ = {merge(t-), merge(t+)}.

The causal prediction is:

A equivalent under W- to B,

but A not equivalent under W+ to B.

Thus the same historical distinction is unnecessary under the inert WRITE contract and required after adding one merge WRITE.

## 2. Frozen candidate repositories

No repository may be replaced because of weak eligibility or inconvenient results.

1. python/cpython — frozen head 333071231d3a46cccc32d7f44b99328c3299d0b1
2. curl/curl — frozen head 657d7f18cf45b9191d9b8efcccd773cfa73b521a
3. numpy/numpy — frozen head 0fbafa8fce925c199df8375e20db2596e0e8e1ac
4. openssl/openssl — frozen head 1e369089f47c6c80a4d00c14cbee3a1300abe9da
5. systemd/systemd — frozen head 583679fe4924e0afbf4dffa861f8b7c6b7be87eb

Only commits reachable from the frozen head are part of the carrier.

## 3. Outcome-blind preflight

The preflight executes no git merge command.

### 3.1 Same-tree pair bank

Enumerate the first 30,000 commits reachable from frozen head in rev-list order.
Map each commit to its exact tree object ID.
For every tree represented by at least two distinct commits:
- sort commit IDs lexically;
- take the first two as one natural same-tree pair.
Sort pairs by tree ID.

### 3.2 Target pool

Enumerate merge commits reachable from frozen head in native rev-list order.
From the first 512 two-parent merge commits, collect unique second-parent commit IDs in first-occurrence order.
Require at least 16 unique targets.

### 3.3 Ancestry matrix

For each same-tree pair p=(A,B) and target t compute only:

a_A(t) = 1[t ancestor-of A],
a_B(t) = 1[t ancestor-of B].

No merge is executed.

A pair is WACT-G eligible iff there exists:
- at least one target with a_A=a_B=1;
- at least one target with a_A != a_B.

## 4. Structural inclusion gate

A repository is INCLUDED for native replay iff:
- at least 32 natural same-tree pairs are available;
- target pool contains at least 16 unique targets;
- at least 8 WACT-G eligible pairs exist.

Otherwise retain it as PREFLIGHT_UNDERPOWERED.
No outcome-based replacement is allowed.

## 5. Prospective witness selection

For each INCLUDED repository:
1. sort eligible pairs by tree ID;
2. if <=16 eligible, select all;
3. otherwise select 16 evenly spaced pairs.

For every selected pair:

Inert target t- is the first target in frozen target-pool order that is ancestor of both endpoints.
Activating target t+ is the first target in frozen target-pool order that is ancestor of exactly one endpoint.

The pair and both targets are frozen before native merge outcomes.

## 6. Registered current READ

READ(z)=tree(z).
Every selected pair is current-READ equivalent by construction.

## 7. Native WRITE

From a clean detached checkout of state z, execute native merge with no-commit and no-ff.
Record the G5 native outcome fields:
- exit code;
- already-up-to-date bit;
- merge-in-progress bit;
- unmerged path set;
- index tree when available;
- tracked working-tree binary-diff hash.

Abort/reset/clean after every branch.

## 8. Causal predictions

### Inert target t-

Because t- is ancestor of both endpoints:
- both merges must report already-up-to-date;
- no merge remains in progress;
- no unmerged paths;
- current tree remains unchanged.

Because the endpoints have the same current tree, registered native outcomes must be identical.

Thus A and B are equivalent under W-.

### Activating target t+

Because t+ is ancestor of exactly one endpoint, exactly one branch must be already-up-to-date.
Therefore registered native outcome signatures must differ.

Thus A and B are not equivalent under W+.

Any violation is retained as a causal prediction failure.

## 9. Representation flip

Under W-, tree-only representation must exactly match the two-state operational partition: U=E=0.

Under W+, tree-only must under-refine: U>0.

Define activated representation:

R+(z) = (tree(z), 1[t+ ancestor-of z]).

For the selected two-state witness this representation must exactly match the operational partition: U=E=0.

Thus the required representation changes solely because one future WRITE is added.

## 10. Primary promotion gate

Cross-repository WACT-G promotion requires:
- at least 3 INCLUDED repositories;
- at least 32 total prospective witnesses;
- zero inert-target native prediction failures;
- zero activating-target native prediction failures;
- zero representation-flip failures.

The native WRITE outcome is not used for witness selection.

## 11. Secondary diagnostics

Per repository report:
- number of same-tree pairs;
- eligible-pair fraction;
- target-pool size;
- number of targets asymmetric for at least one selected pair;
- distribution of asymmetric-target counts per pair;
- concentration of pair activations across targets.

These are descriptive only.

## 12. Boundary

WACT-G does not claim novelty for Git ancestry, merge-base semantics, observational equivalence, contextual equivalence, or future-equivalence theory.

The contribution target is cross-substrate empirical causality:

> a fixed latent state distinction can be unnecessary under one native WRITE contract and become necessary when one additional future WRITE is admitted, with the required representation changing accordingly.

The Git result is cross-substrate evidence only if it survives fresh repositories and native merge replay.