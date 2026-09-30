# OACR Final Upgrade & Acceptance Gate

Date: 2026-09-30

Status: **FROZEN UPGRADE GATE**

This document is the sole acceptance gate for further OACR development. New work must close at least one of the three gates below. Work that does not contribute to Theory, Identification, or Natural Evidence is out of scope.


## Progress snapshot — 2026-09-30

### Theory Gate
- **T1: WORKING PASS.** Contract-relative exact repair is now formalized with coarse/fine endpoints and an explicit admissible repair family.
- **T2: PARTIAL PASS.** A theorem family now gives uniqueness inside the identity-gated representation family, edit-minimal contract updates, and path independence under contract evolution. Generic minimum-feature NP-hardness was rejected as non-novel prior art.
- **T3: CANDIDATE PASS, proof/prior-art audit pending.** The one-delta DAG carrier admits an exact theorem: contract-active redundant deltas form singleton operational classes; inactive deltas collapse with base; the contract gate exactly realizes the quotient.
- **T4: CANDIDATE PASS, proof/prior-art audit pending.** The same certificate yields additive and subtractive repair to one common target, with minimum Hamming record edits and path-independent updates as the contract expands or contracts. A four-node multi-delta counterexample proves the local rule does not extend universally.
- **T5: OPEN.** AIR / strong preservation / CEGAR / Verifix / summary-repair source-level positioning remains to be completed before manuscript promotion.

### Identification Gate
- **I1-I3: THEORY SPECIFIED, empirical promotion pending.** Non-anticipation is now defined as provenance/freeze separation: realized evaluation outcomes may not adapt the current constructor. It is not statistical independence from predictable outcomes.
- **I4-I5: OPEN.** Existing protocol devices still need to be unified into one formal identification framework and paired with an executable leakage counterexample.

### Natural Evidence Gate
- **N1-N5: NOT STARTED in this upgrade round.** No new learned-system experiment is authorized until the parallel task/head is clear and the theory object is stable.

### Frozen-theory audits completed
- R4: the contract-coverage formula matches **64/64 singleton**, **2016/2016 pair**, and **64/64 leave-one-out** registered subcontract results.
- R4: only **5/64** actions activate any candidate delta; the largest activates **19/22**, yielding 20 of 23 operational classes alone.
- R4 exploratory contract basis: unique minimum basis of **4** actions on the already frozen activation matrix.
- R3/R4 closed-form directional-gap equations reproduce the frozen reported \(U/E\) values to floating-point precision.


## Gate T — Theory

### T1. Contract-Adequate Representation Repair
Define the repair problem for a state bank (X), continuation contract (mathcal C), implemented representation (R), admissible representation family (mathcal F), and cost (c):

[
exists R'\in\mathcal F:\quad P_{R'}=O_{\mathcal C}.
]

Cover both coarse-to-target and fine-to-target correction.

### T2. Nontrivial general theory
Seek at least one load-bearing result of the following scale:
- computational hardness of minimum-cost exact adequacy repair;
- necessary-and-sufficient existence conditions;
- uniqueness up to partition equivalence;
- confluence/common-fixed-point conditions;
- or an equivalent theorem family.

Entropy identities and routine corollaries do **not** satisfy this gate.

### T3. Tractable structural class
Identify structural assumptions under which the general repair problem becomes exactly solvable. R3/R4 may instantiate such a class only if the theorem is stated independently of their observed outcome matrix.

### T4. Bidirectional repair as a formal object
Study
[
R_{\rm coarse}\xrightarrow{\Phi^+}R^\star\xleftarrow{\Phi^-}R_{\rm fine}
]
on the refinement lattice. Characterize when both directions reach the same operational quotient and when local feature interactions prevent this.

### T5. Nearest-neighbor acceptance
The final manuscript must directly distinguish OACR from:
- strong preservation / abstract interpretation;
- Abstract Interpretation Repair;
- CEGAR;
- verified/program repair such as Verifix and summary repair.

A reviewer familiar with those literatures must be able to state OACR's independent theoretical object in one paragraph.

## Gate I — Identification / Anti-circularity

### I1. Information-authority boundary
Separate construction-visible information
[
\mathcal I_{\rm construct}
]
from verification-only outcomes
[
Y_{\mathcal C}^{\rm verify}.
]

### I2. Non-anticipating repair
A valid constructor must satisfy
[
\kappa=f(\mathcal C,\mathcal I_{\rm construct}),
]
not
[
\kappa=f(\mathcal C,\mathcal I_{\rm construct},Y_{\mathcal C}^{\rm verify}).
]

### I3. Correct audit/constructor narrative
Do not require the audit outcome matrix to synthesize the certificate when the accepted carrier does not use it. Audit diagnoses; a separately permissioned constructor proposes; held-out native replay accepts or rejects.

### I4. Unified identification framework
Unify:
- same-contract evaluation;
- freeze-before-outcome;
- forbidden reads;
- outcome-blind witness selection;
- fixed interpreter;
- producer/verifier separation;
- independent replay;
- equal-cost sham repair.

### I5. Leakage counterexample
Provide at least one executable demonstration that outcome-aware feature construction can trivially or spuriously reproduce the operational partition, while the accepted constructor is forbidden from that information.

## Gate N — Natural Evidence

### N1. Mature learned benchmark
Prefer an established substrate such as RippleEdits, MQuAKE, EasyEdit-supported CounterFact/ZsRE/recent knowledge, or another benchmark with dependent/sequential edit structure.

### N2. Shared continuation contract
Comparable states must face the same frozen continuation panel. Pair-specific outcome-driven continuation selection is disallowed.

### N3. Natural scale
Raise at least one learned carrier to hundreds of independent evaluation units; preferably include multiple editors and, if feasible, more than one model family.

### N4. Learned constructive repair
Target:
[
\text{diagnosed inadequacy}
\rightarrow
\text{contract-relevant representation intervention}
\rightarrow
\text{fixed native editor/interpreter}
\rightarrow
\text{future closure improvement}.
]

A matched irrelevant/sham intervention is required. Replacing the editor with a stronger model does not count.

### N5. Scientific negative boundary
If exact learned repair fails under a prospectively frozen protocol, report the residual mismatch and localize the failure to the representation family, optimization, or native stochasticity. Do not tune until success.

## Existing evidence authority

- R4 remains the exact constructive centerpiece: 272 states, 64 actions, 17,408 native outcomes, 23 operational classes, 22/271 retained deltas.
- R3 remains developmental structural replication.
- SQEC fixed-interpreter repair remains the second controlled constructive carrier: H1 mismatch 0; H2 mismatch 12; relevant repair 12→0; equal-cost sham 12→12.
- WACT-R 80/80 is always reported as selection-conditioned.
- GRACE 224 collision pairs are always tied to 64 underlying states.
- Finetune single positive witness becomes mechanism evidence rather than the learned headline if Gate N succeeds.

## Final paper identity

The final manuscript should have three main contributions:

1. **Theory:** contract-relative representation adequacy and bidirectional repair.
2. **Identification:** non-anticipating / outcome-blind representation-repair methodology.
3. **Evidence:** exact structural repair, fixed-interpreter repair, and natural learned-system confirmation.

A cold reviewer must not summarize the paper merely as a collection of graph, Git, LLM, and SQEC experiments.

## Stop rule

Final verdict must be one of:

- **UPGRADE PASS** — Gates T, I, and N all pass.
- **SCIENTIFIC PASS / UPGRADE INCOMPLETE** — the current paper remains publishable but at least one upgrade gate does not pass.
- **BLOCKED** — a core contradiction, answer leakage, or failed independent replay invalidates a main claim.

No new carrier, theorem, or experiment is authorized unless it closes a gate above.
