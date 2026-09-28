# OACR Checkpoint — 2026-09-28

## Current mother object

**Operational Adequacy of Computational Representations (OACR)** asks which distinctions a computational representation must preserve for a declared observation/operation contract.

All carrier semantics are governed by the native-first relation-semantics discipline.

## Evidence status

### OACR-W1 — official GRACE + SCOTUS/BERT

Frozen result:

- 2 contract-valid persistent states;
- 8 common future writes;
- 8 current-read collisions;
- 0 registered one-step operational divergences;
- 0 strong selective divergences;
- A2/A3 routing/structural features distinguished the states despite no observed one-step behavioral requirement.

Interpretation: internal write-state difference is not itself evidence of operational necessity.

### OACR-R1 — registered Wikidata-derived graph

Audit-complete frozen carrier:

- raw response SHA256: `3d3852ff72382c171e3a5496336767809b9455541fa2604f7b6857a8e69457df`;
- 1027 prepared nodes;
- 1063 asserted edges;
- 1334 complete registered closure edges;
- 271 entailed-but-unasserted candidate pairs;
- 64/64 frozen exact current-closure collisions became divergent under the same registered deletion;
- all 64 required pairs were separated by A1/A2/A3 candidate refinements.

Interpretation: every witnessed pair must be separated by any representation adequate for that one-step registered deletion contract, but no particular feature encoding is shown uniquely necessary.

### OACR-N1 — operational necessity audit

Frozen methodological distinction:

- **pairwise necessity:** a current-observation collision that diverges under the registered future contract must be separated somehow;
- **feature under-refinement:** the feature still merges a required pair;
- **feature over-refinement:** the feature separates a pair whose registered future behavior remains equivalent.

Retrospective result:

- W1: 0 required separations; A2 and A3 each over-refine all 8 evaluated collisions.
- R1: 64 required separations; A1/A2/A3 each separate all 64; over-refinement cannot be assessed because R1 v1 is a purposive positive-control witness set.

### OACR-G1 — native Git tree/history congruence

Exact native-system run on Git 2.55.0:

- 2 exact pre-tree collisions;
- 2/2 registered merge divergences;
- 0 duplicate replay failures;
- target-ancestry bit separates 2/2;
- merge-base identity separates 2/2;
- one case yields conflict versus already-up-to-date;
- one case yields a clean post-content divergence versus already-up-to-date.

Interpretation: complete tracked-content equality is insufficient for the registered Git merge contract. Commit-history distinctions are pairwise operationally required in these exact constructions.

G1 is an exact native-system witness, not a prevalence study and not yet a real-repository observational result.

## What has changed conceptually

The project is no longer asking whether hidden state differences exist.

It now asks:

> Which state separations are demanded by the registered operational behavior, and which internal distinctions merely over-refine that requirement?

This reverses the evidence direction:

[
\text{registered behavior}
\rightarrow
\text{required separations}
\rightarrow
\text{candidate representation features}.
]

## Next hard gate

The next experiment should not add a theory category for its own sake.

It should test one of two unresolved questions:

1. **Natural occurrence:** do operationally necessary distinctions arise in real, naturally produced system histories rather than only in constructed positive controls?
2. **Minimality:** among multiple internal refinements that separate required pairs, which distinctions are genuinely needed for the native operation family rather than merely correlated with it?

A new carrier is justified only if its native semantics can resolve one of these questions more sharply than W1, R1, and G1.
