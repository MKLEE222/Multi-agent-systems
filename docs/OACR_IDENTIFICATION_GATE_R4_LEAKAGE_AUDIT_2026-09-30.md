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
