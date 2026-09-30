# OACR Identification Gate — Executable R4 Leakage Counterexample

Date: 2026-09-30

Status: **I5 WORKING PASS on frozen R4 artifact**

Source:
- workflow run: 36438278451;
- artifact ID: 11003190307;
- states: 272;
- actions: 64;
- accepted operational blocks: 23.

The same frozen R4 bank was evaluated with three representation constructors.

| Constructor | Outcome access | Retained records | Representation blocks | U | E | Exact |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| A0 outcome oracle | Reads realized evaluation outcomes | 22 | 23 | 0 | 0 | yes |
| A2 contract-predictive | Base graph + candidate delta + frozen deletion contract only | 22 | 23 | 0 | 0 | yes |
| A2 matched inactive sham | Contract-visible structure only; same cost | 22 | 23 | 0.7556880439 | 0.7556880439 | no |

Additional checks:
- oracle retained set equals predictive retained set: **true**;
- predictive retained set equals the previously frozen R4 active-state set: **true**;
- sham/predictive retained-set overlap: **0**.

## Interpretation

The oracle result is deliberately not a success claim. It proves the methodological point:

\[
\boxed{\text{evaluation-outcome access can make exact repair trivial}}
\]

because the constructor can directly encode the distinctions already revealed by the evaluation quotient.

The predictive constructor reaches the same 22-record target without using augmented-state evaluation outcome labels. Its exactness therefore has a different authority provenance.

The sham constructor controls for both representation size and representation block count:

\[
|\kappa_{\rm predictive}|
=
|\kappa_{\rm sham}|
=
22,
\]

and both induce 23 representation blocks, yet only the contract-relevant constructor closes the operational quotient.

Thus the result cannot be attributed merely to:
- adding 22 delta records;
- increasing representation capacity;
- producing the same number of blocks.

It depends on selecting the contract-relevant distinctions.

## Authority consequence

This experiment cleanly separates:

### Ex-post encodability

\[
\text{A0 oracle}: U=E=0.
\]

This is weak evidence because the target was visible.

### Non-circular predictive exactness

\[
\text{A2 predictive}: U=E=0.
\]

This is stronger because the constructor is fixed by contract-visible structure.

### Matched irrelevant capacity

\[
\text{A2 sham}: U=E=0.7556880439.
\]

Same cost is insufficient without contract relevance.

## Reproducibility

Executable script:
- experiments/oacr_identification/r4_noncircular_leakage_demo_v1.py

Frozen result:
- docs/OACR_R4_NONCIRCULAR_LEAKAGE_DEMO_RESULT_2026-09-30.json

Local execution hashes from this audit:
- script SHA256 before repository formatting: 83be81b8755d6e2251bcf728d92d5109c2a7cc9c49f9ef40abca85af7aab537d;
- result SHA256: 22836b591b9879b67bc537d0ce866d6191e0045efe2cb1c4cc2ac562b7462e8e.

The repository version of the script may have formatting/comment cleanup and should receive a new canonical hash once a workflow-based verifier is added.


## Independent CI verification

Workflow:

- name: OACR R4 Noncircular Leakage Verification;
- successful run: 36734635683;
- head commit: 2c4938dc376f1e96a8d09152b1522a78624d9d6f;
- artifact ID: 11106427052;
- artifact digest:
  sha256:918a0e121d5923c28445cc6d582147f034d3b5070acf85b5644700b14bcd3d12.

The independent verifier reconstructed the graph, contract-predictive active set, outcome-oracle set, same-cost inactive sham, representation partitions, and both directional information gaps.

Verifier result:

- verified: true;
- error_count: 0;
- oracle_equals_predictive: true;
- predictive_equals_frozen_active_ids: true;
- sham_overlap_with_predictive: 0.

Recomputed outputs:

\[
A0_{\rm oracle}: U=E=0;
\]

\[
A2_{\rm predictive}: U=E=0;
\]

\[
A2_{\rm sham}: U=E=0.7556880438822081.
\]

All three use 22 retained records; all three induce 23 representation blocks.

Canonical CI output hashes:

- producer.json:
  93531353e80cf4c70844e9cc673a41d49a1c736c461c3be5dedf76f8bb0afda9;
- verifier.json:
  00fc8ba6aacda65d45f899f2a739d7de1f15d9313fa1f6e1f62a5b75fd5c7bf9.

The first CI attempt failed before scientific execution because the workflow passed a literal escaped repository variable to the GitHub artifact endpoint. Only workflow interpolation and runtime-version alignment were corrected; the scientific producer, verifier logic, and frozen result were not tuned in response to scientific outputs.

### I5 verdict

\[
\boxed{\text{PASS}}
\]

This is an executable methodological leakage demonstration with independent verification.

It remains retrospective with respect to the original R4-building discovery/acceptance and must not be described as a prospectively registered sham result.
