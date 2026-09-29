# OACR-R4 Fast Producer Regression — Building — 2026-09-29

## Status

The performance optimization authorized in:

docs/OACR_R4_PRODUCER_ENGINEERING_OPTIMIZATION_2026-09-29.md

was checked against the already accepted frozen building artifact before use on a pending fresh carrier.

Accepted building artifact:

- workflow run: 36438278451;
- artifact: oacr-r4-v2-building;
- artifact ID: 11003190307.

## Regression identity checked

For every registered building state/action cell:

### Active Rgate state

Expected optimized compressed result:

original native outcome for the same state/action.

### Base or inactive Rgate state

Expected optimized compressed result:

the base state's native outcome for the same deletion action.

The frozen accepted artifact was checked across all:

\[
272\times64=17{,}408
\]

registered cells.

## Result

- active states: 22;
- inactive augmented states: 249;
- base state: 1;
- checked cells: 17,408;
- deviations: 0.

The frozen artifact's original and compressed outcome matrices also have the same manifest SHA256:

3e3fc97407f81e2f51ac6526c3c0c6217117a0991e0d2491e5cee87eeb9d57c8

This is consistent with the accepted exact partition/replay result.

## Consequence

The fast producer may be used as an engineering fallback for pending R4 clean reruns.

Final scientific acceptance still requires the unchanged independent verifier:

experiments/oacr_r4/verify_paginated_relational_redesign_v2.py

to return PASS on the newly produced raw pages/result artifact.
