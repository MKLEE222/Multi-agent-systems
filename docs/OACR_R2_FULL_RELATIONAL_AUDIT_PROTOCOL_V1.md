# OACR-R2 Protocol v1 — Full Relational Candidate and Control Audit

**Date:** 2026-09-28  
**Status:** preregistered exact audit on the frozen OACR-R1 carrier  
**Source carrier:** audit-complete OACR-R1 run 36378905855  
**Raw carrier SHA256:** `3d3852ff72382c171e3a5496336767809b9455541fa2604f7b6857a8e69457df`

## 1. Question

R1 deliberately selected positive witnesses. R2 asks a different question:

> Across the complete frozen set of entailed-but-unasserted candidate edges, how often do candidate representation refinements separate states that the registered future deletion actually requires to be separated, and how often do they over-refine?

This remains an L1 registered graph experiment, not a claim about full Wikidata semantics.

## 2. Frozen state pairs

Reconstruct the exact prepared graph (G) from the frozen raw R1 response using the same hygiene rules.

Enumerate the complete set

[
E_{mathrm{cand}}=TC(G)setminus E(G).
]

For every candidate (e=(u,v)), construct

[
G_0=G,qquad G_1=Gcup{e}.
]

Verify exactly:

[
TC(G_0)=TC(G_1).
]

All candidate pairs therefore collide under the complete registered current READ interface.

## 3. Frozen future action per candidate

For each candidate, enumerate all shortest (uleadsto v) paths and choose the lexicographically first path.

Let (f) be the first asserted edge on that path.

Apply the same registered action to both states:

[
mathrm{del}(f).
]

This rule is deterministic and is frozen before outcomes are inspected.

## 4. Required versus non-required separation

After deletion:

- **required separation / positive:** full registered closures differ;
- **non-required separation / control:** full registered closures remain equal.

No candidate is dropped because it is negative.

## 5. Candidate representation refinements

Evaluate:

- **A1:** complete current closure + exact support-path multiplicity for the candidate entailment;
- **A2:** complete current closure + whether the candidate entailment is explicitly asserted;
- **A3:** complete current closure + minimal shortest support sets for the candidate entailment.

For each level report:

- required pairs separated;
- required pairs still merged (under-refinement);
- non-required pairs separated (over-refinement);
- non-required pairs merged.

These are finite-pair diagnostics, not universal minimality results.

## 6. Outputs

Report:

- total candidate universe;
- positives;
- controls/non-divergent pairs;
- full post-closure symmetric-difference distribution;
- A1/A2/A3 confusion tables relative to required separation;
- examples of both required and non-required pairs;
- exact source hash and reconstructed graph sizes.

## 7. Interpretation discipline

R2 can establish whether a candidate feature is too coarse or too fine **for this frozen finite contract**.

R2 cannot establish:
- universal necessity of support counts/provenance;
- a prevalence statement about Wikidata editing;
- a domain-level statement about P279 beyond the registered L1 graph semantics.
