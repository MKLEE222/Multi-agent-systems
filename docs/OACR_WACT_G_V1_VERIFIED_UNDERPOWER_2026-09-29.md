# OACR-WACT-G v1 Verified Underpower Record — 2026-09-29

## Status

WACT-G v1 is **verified preflight underpowered**.

No native git merge outcome was executed in either the original preflight or the clean verification rerun.

Original run:

36530321432

Clean preflight + independent verifier run:

36541670322

## Frozen repositories

- python/cpython @ 333071231d3a46cccc32d7f44b99328c3299d0b1
- curl/curl @ 657d7f18cf45b9191d9b8efcccd773cfa73b521a
- numpy/numpy @ 0fbafa8fce925c199df8375e20db2596e0e8e1ac
- openssl/openssl @ 1e369089f47c6c80a4d00c14cbee3a1300abe9da
- systemd/systemd @ 583679fe4924e0afbf4dffa861f8b7c6b7be87eb

## Reverified result

### cpython

- natural same-tree pairs: 34
- preflight pair bank: 34
- global second-parent target pool: 502
- eligible pairs: 0
- independent native ancestry spot-checks: 50
- status: PASS_PREFLIGHT_UNDERPOWERED_ELIGIBILITY

### curl

- natural same-tree pairs: 25
- target pool: 24
- structural gate fails before eligibility
- status: PASS_PREFLIGHT_UNDERPOWERED_STRUCTURAL

### numpy

- natural same-tree pairs: 2,623
- preflight pair bank: 256
- target pool: 511
- eligible pairs: 0
- independent native ancestry spot-checks: 50
- status: PASS_PREFLIGHT_UNDERPOWERED_ELIGIBILITY

### openssl

- natural same-tree pairs: 44
- preflight pair bank: 44
- target pool: 25
- eligible pairs: 6
- independent native ancestry spot-checks: 50
- status: PASS_PREFLIGHT_UNDERPOWERED_ELIGIBILITY

### systemd

- natural same-tree pairs: 566
- preflight pair bank: 256
- target pool: 512
- eligible pairs: 0
- independent native ancestry spot-checks: 50
- status: PASS_PREFLIGHT_UNDERPOWERED_ELIGIBILITY

## Independent verification method

The clean verifier does not use the producer's integer-bitset implementation for the primary recomputation.

It rebuilds:

- the 30,000-commit reachable bank;
- commit-to-tree mapping;
- natural same-tree pairs;
- the frozen second-parent target pool;
- target ancestry using explicit target-index set propagation.

It then spot-checks deterministic matrix cells with native:

git merge-base --is-ancestor

The underpower result reproduced.

## Diagnosis

The v1 failure is not evidence against WRITE activation.

The bottleneck is the inherited global target-pool constraint:

- target candidates were restricted to second parents of the first 512 two-parent merges;
- a natural same-tree pair had to find both a common-ancestor target and an asymmetric-ancestor target inside that shared global pool.

Large pair banks in numpy and systemd still produced zero eligible pairs, indicating that the global pool is a poor carrier for pair-specific causal intervention.

## Allowed successor

Because no native merge outcome has been executed, WACT-G v2 may change only the outcome-blind target construction.

The frozen repositories and heads remain unchanged.

The successor should select pair-specific targets directly from each pair's ancestry structure before any merge outcome:

- inert target from common ancestry;
- activating target from symmetric-difference ancestry.

No result-dependent repository replacement is allowed.
