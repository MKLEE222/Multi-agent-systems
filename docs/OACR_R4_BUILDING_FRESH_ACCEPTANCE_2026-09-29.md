# OACR-R4 Building Fresh Acceptance — 2026-09-29

## Status

**ACCEPTED as the first prospectively registered fresh R4 carrier.**

Authoritative protocol:

docs/OACR_R4_V2_PAGINATED_REDESIGN_PROTOCOL.md

Protocol commit:

6795a534415e4f7270f2b25aca3522b653e413d3

Workflow run:

36438278451

Job:

oacr-r4-v2 (Q41176, building, building)

Artifact:

oacr-r4-v2-building

Artifact ID:

11003190307

The producer, independent verifier, and artifact upload all completed successfully.

## 1. Fresh carrier

Root:

Q41176 — building.

The carrier was not selected based on redesign outcome.

It was frozen in the R4 protocol before fresh augmented-state deletion outcomes.

Registered state/action rules were unchanged from the preregistration.

## 2. Structural bank

Registered:

- states: 272;
- augmented redundant-edge states: 271;
- deletion actions: 64.

Full registered operational partition:

\[
|O_A|=23.
\]

Operational entropy / future conditional demand:

\[
0.76596993255357\text{ bits}.
\]

## 3. Directional mismatch

Current-closure representation R0:

\[
U=0.7659699325535673,
\qquad
E=0.
\]

- representation blocks: 1;
- under-refinement pairs: 5,731.

Full asserted identity Rfull:

\[
U=0,
\qquad
E=7.321492908696782.
\]

- representation blocks: 272;
- over-refinement pairs: 31,125.

Thus the same frozen fresh contract reproduces the directional coarse/fine mismatch pattern prospectively.

## 4. Contract-gated redesign

Rgate classified:

- active augmented states: 22;
- inactive augmented states: 249;
- active fraction: 0.08118081180811808.

Rgate induced:

\[
23\text{ representation blocks}
=
23\text{ operational blocks}.
\]

Directional gaps:

\[
U(R_{\rm gate})=0,
\qquad
E(R_{\rm gate})=0.
\]

Pairwise mismatch:

- under-refinement: 0;
- over-refinement: 0.

Therefore the contract-gated representation exactly matches the registered operational quotient on this fresh carrier.

## 5. Native replay

All compressed representation state-action executions matched the original registered native outcomes.

\[
272\times64=17{,}408
\]

registered cells.

Replay mismatches:

\[
0.
\]

The independent verifier returned PASS.

## 6. Physical declared delta storage

Before gating:

\[
271\text{ delta-edge records}.
\]

After gating:

\[
22.
\]

Reduction:

\[
1-\frac{22}{271}
=
0.9188191881918819.
\]

Thus the declared per-state delta representation removes 91.88% of stored redundant-edge records on this carrier while preserving all registered native outcomes.

This is a carrier-specific physical record-count result, not a universal compression ratio.

## 7. Fresh action-content structure

Exact registered secondary analysis:

### Singletons

Among 64 single-action contracts:

- 59 induce one operational class;
- 4 induce two classes;
- 1 induces 20 classes.

Maximum singleton operational entropy:

\[
0.6621048471412936\text{ bits}.
\]

### Pairs

Across all

\[
\binom{64}{2}=2016
\]

two-action contracts:

- operational classes range from 1 to 21;
- median remains 1.

### Leave-one-out

Only 4/64 actions are indispensable for reproducing the full 23-class partition under leave-one-out.

The other 60 may be omitted individually without changing the full registered quotient.

## 8. Accepted interpretation

Building prospectively supports:

1. the theorem-driven contract-gated transform remains exactly adequate on a fresh carrier;
2. exact partition matching is not unique to the developmental R3 carrier;
3. full asserted identity remains massively over-refined relative to the native deletion contract;
4. action content remains highly anisotropic on this fresh carrier.

The cross-carrier R4 promotion gate still requires at least one additional fully verifier-passed fresh INCLUDED root.

No cross-carrier promotion is made from building alone.
