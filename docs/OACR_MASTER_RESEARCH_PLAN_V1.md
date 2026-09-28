# OACR Master Research Plan v1

**Date:** 2026-09-28  
**Status:** full-strength research program plan  
**Principle:** optimize for scientific closure and mother-problem coverage, not minimum publishability.

## 1. End-state research question

OACR asks:

> **What distinctions must a computational representation preserve in order to remain adequate for the observations and native operations required by a system?**

For a registered contract

\[
\mathcal C=(\mathcal O,\mathcal A,H,\mathsf{Legal},\mathsf{Cost}),
\]

the project compares:

1. the distinctions encoded by an implemented representation \(\rho\);
2. the distinctions required by registered future operational behavior.

The core methodological direction is:

\[
\text{native behavior}
\rightarrow
\text{required state separations}
\rightarrow
\text{candidate representation features}
\rightarrow
\text{representation redesign}.
\]

Not:

\[
\text{available internal feature}
\rightarrow
\text{declare it semantically important}.
\]

All carrier semantics remain governed by the native-first L0/L1/L2 discipline.

---

## 2. Full-strength claim architecture

### Claim A — Operational adequacy is contract-relative

Static fidelity alone is insufficient. Adequacy must be evaluated relative to the observations and native operations the representation is expected to support.

### Claim B — Implemented representations can under- or over-refine the required operational partition

For a frozen contract:

- **under-refinement:** the representation merges states whose registered future behavior differs;
- **over-refinement:** the representation distinguishes states whose registered future behavior remains equivalent.

The project does not claim to invent behavioral equivalence or minimal-state quotients; those are inherited from mature theory.

### Claim C — Operational demand grows with the contract

For nested action families and/or horizons, the required partition can only stay the same or refine:

\[
\equiv_{\mathcal C,H+1}\subseteq \equiv_{\mathcal C,H}.
\]

In finite exact settings, define:

\[
N_H=|X/\!\equiv_H|,
\]

and the corresponding representational information burden:

\[
I_H=\log_2 N_H.
\]

The empirical target is to measure how \(N_H\) and candidate representation adequacy change as the operation contract expands.

### Claim D — The adequacy structure transfers across heterogeneous systems without imposing one relation semantics

The shared object is the adequacy question, not a universal relation ontology.

### Claim E — OACR can guide representation design

A successful project should demonstrate both directions where possible:

- augment an under-refined representation with the missing operational distinction;
- quotient/compress an over-refined representation while preserving the registered contract.

Claim E is the strongest practical gate.

---

## 3. Current evidence baseline

### Learned routed system — W1 / GRACE + SCOTUS
- 8 current-read collision pairs;
- 0 one-step registered operational divergences;
- A2/A3 routing/structural features distinguish all 8;
- interpretation: observed internal distinctions over-refine the frozen one-step contract.

### Exact relational system — R1
- 64 exact current-closure collisions;
- 64/64 one-step deletion divergences;
- A1/A2/A3 each separate all required pairs;
- over-refinement not yet measurable because v1 contains only purposive positives.

### Exact native versioned system — G1
- 2 exact tree collisions;
- 2/2 native merge divergences;
- deterministic replay success.

### Natural native history — G2
- first 10,000 merges in public `git/git`;
- 29 natural tree-preserving candidates;
- first 16 executed under preregistered stopping rule;
- 16/16 valid natural operational-divergence witnesses.

### Cross-carrier necessity audit — N1
- distinguishes internal difference from operational necessity;
- W1 supplies over-refinement evidence;
- R1 supplies exact required separations.

---

## 4. Workstream T — Mother-level theory audit and formal core

### T1 — theorem/source ledger

For each neighboring theory family, extract the exact object, assumptions, theorem, and relation to OACR:

1. Myhill–Nerode / automata minimization;
2. bisimulation / coalgebra / behavioral equivalence;
3. computational mechanics causal states;
4. epsilon-transducers;
5. predictive state representations;
6. state abstraction in MDPs;
7. strong preservation / complete shells;
8. full abstraction / contextual equivalence;
9. representation independence / data refinement;
10. knowledge compilation;
11. dynamic complexity where cost/maintenance matters.

Every candidate OACR statement receives one status:

- **INHERITED**
- **DIRECT REFORMULATION**
- **GENUINE EXTENSION**
- **UNSUPPORTED — DELETE**

### T2 — formal OACR core

Formalize the smallest object that survives T1:

\[
\mathcal C=(\mathcal O,\mathcal A,H,\mathsf{Legal},\mathsf{Cost})
\]

plus representation map \(\rho\) and registered operational behavior.

Required theorem targets:

1. horizon monotonicity;
2. action-family monotonicity;
3. quotient/cardinality lower bound in finite exact settings;
4. finite-bank under-/over-refinement criteria;
5. relation between candidate feature partitions and the operational partition;
6. extension to stochastic or approximate observations if mathematically justified;
7. explicit boundary against existing minimal-state/bisimulation results.

### T3 — composition bridge

Only after the WRITE/operational core is stable, determine whether COMPOSE is naturally expressed by requiring operation-preserving maps:

\[
T\circ \Phi_a^A \approx \Phi_{\tau(a)}^B\circ T.
\]

Do not force COMPOSE into the first paper unless it strengthens rather than dilutes the core.

**T-gate:** no final paper claim is frozen before T1/T2 complete.

---

## 5. Workstream L — Learned representations at serious scale

The learned evidence must be a program, not one carrier.

### L1 — GRACE horizon experiment

Use official GRACE + SCOTUS/BERT.

Primary target:

\[
\equiv_0,\equiv_1,\equiv_2
\]

on the same frozen state banks and action alphabet.

Design target:

- 5–10 independent seeds;
- 8–16 persistent states per seed where feasible;
- 4–6 frozen materially distinct future actions per bank;
- complete registered branching through \(H=2\);
- optional \(H=3\) on reduced alphabets if computationally tractable;
- exact branch RNG control;
- frozen READ panel and legality/status semantics;
- prospective state/action selection, not witness hunting.

Outputs:

- partition sizes \(N_0,N_1,N_2\);
- first-horizon separation for each colliding pair;
- under-/over-refinement of routing/structural candidate features;
- negative result preserved if the quotient does not refine.

### L2 — second learned write ecology

Select only after L1/T2 reveal the unresolved adequacy question.

Hard requirement: mechanism must be materially different from routed external memory.

Candidate class:
- parameter-level editing;
- persistent adapter update;
- online/fine-tuning state.

Selection criteria:
1. real persistent state;
2. native write operator;
3. deterministic/reproducible registered action contract;
4. serious pretrained model;
5. feasible state collision / equivalence audit;
6. no measurement mutation.

Target scale:
- at least 2 model/task settings;
- multiple seeds/histories;
- horizon analysis where possible;
- both positive and negative state pairs.

### L3 — third learned ecology if needed by theory

Do not add for count alone.

Add only if L1/L2 leave a live alternative explanation, e.g.:
- effects depend on discrete memory versus parameter dynamics;
- effects depend on local editing versus optimizer-state history;
- action horizon behaves differently across representation families.

### L4 — prospective learned prediction

After a mechanism is characterized retrospectively:
- freeze a predictor of which state distinctions will be operationally required;
- run held-out states/actions before executing future writes;
- report TP/FP/FN/TN under the registered contract.

This is required before any strong empirical claim about a learned feature being a useful adequacy predictor.

---

## 6. Workstream R — Exact relational system

R1 remains a controlled exact carrier, not a proxy for all knowledge systems.

### R2 — complete the frozen candidate universe

On the current frozen graph:
- execute all 271 entailed-but-unasserted candidates under a separately frozen protocol;
- do not stop at positives;
- construct matched non-divergent controls where the same candidate feature changes but future behavior does not.

Measure for A1/A2/A3:
- required separations captured;
- under-refinement;
- over-refinement;
- feature precision relative to the registered operational partition.

### R3 — structural replication

Use independently frozen graph samples selected by pre-registered graph-structural criteria, not domain labels.

Purpose:
- determine whether R1 behavior depends on one specific topology;
- test how redundancy, path multiplicity, and deletion position affect the operational quotient.

### R4 — exact horizon analysis

For a manageable exact graph subset, enumerate deletion sequences to \(H=2\) or beyond.

Measure:

\[
N_0,N_1,N_2,\ldots
\]

and compare support/provenance refinements with the true finite operational partition.

---

## 7. Workstream G — Natural native versioned systems

### G3 — complete current `git/git` search window

Execute all 29 tree-preserving candidates found in the frozen first-10,000-merge window.

Do not change candidate definition.

### G4 — matched non-divergent controls

Construct/search natural controls that:
- share exact current tree;
- differ in ancestry/merge-base features;
- nevertheless have the same registered merge outcome.

This is necessary to test whether ancestry/merge-base features over-refine the actual merge contract.

### G5 — repository replication

Apply the same frozen search to 3–5 additional mature public repositories selected by pre-registered structural criteria:
- long merge history;
- sufficient two-parent merge count;
- stable public availability.

Repository identity is not itself the scientific variable; replication checks natural robustness.

### G6 — native horizon/composition extension

Only if supported by native semantics, test short merge/update sequences rather than single operations.

Do not label this “identity”, “provenance”, or “continuity” unless separately justified at L2.

---

## 8. Workstream M — Measurement law

This workstream converts witness collections into a quantitative representation science object.

For each carrier where feasible, compute:

1. \(N_H=|X/\!\equiv_H|\);
2. \(I_H=\log_2N_H\) in finite exact settings;
3. incremental demand:

\[
\Delta I_H=I_H-I_{H-1};
\]

4. change under action-family expansion;
5. under-/over-refinement rate of implemented representation features;
6. first failure horizon for candidate representations.

The core empirical question becomes:

> How quickly does the information required for operational adequacy grow as a system is asked to support a broader or deeper operation contract?

This is a central candidate for the paper’s general-law component.

---

## 9. Workstream D — Constructive representation design

The program should not stop at diagnosis.

### D1 — under-refinement repair

Choose a carrier with stable, prospective operational failures.

Construct:

\[
\rho^+=\rho+\text{minimal candidate distinction}
\]

and test whether registered under-refinement failures disappear.

Strong version:
- hold current READ quality fixed;
- improve future registered operational adequacy;
- measure added state/information cost.

### D2 — over-refinement compression

Choose a carrier where internal distinctions repeatedly fail to matter operationally.

Construct a quotient/compression:

\[
\rho^- = q\circ \rho
\]

that removes those distinctions while preserving registered behavior.

Strong version:
- reduce state size/complexity;
- preserve \(B_H\);
- verify no hidden degradation on held-out registered actions.

### D3 — bidirectional tradeoff

If both D1 and D2 succeed, quantify a Pareto frontier:

\[
\text{representation burden}
\quad\text{vs}\quad
\text{operational adequacy}.
\]

This would substantially strengthen OACR beyond a diagnostic framework.

---

## 10. Evidence architecture for the core paper

The first full OACR paper should aim to contain all of the following blocks:

### Block A — Theory inheritance and OACR formalization
- explicit nearest-theory reduction map;
- formal contract-relative adequacy object;
- exact theorems that genuinely survive novelty audit.

### Block B — Controlled exact systems
- R2/R3 relational;
- G1 exact native construction.

### Block C — Natural systems
- G2/G3/G4/G5 natural repository history;
- positive and matched negative evidence.

### Block D — Learned systems
- GRACE horizon study;
- second learned write ecology;
- prospective prediction.

### Block E — Quantitative law
- horizon/action-breadth partition refinement;
- operational information demand.

### Block F — Constructive intervention
- at least one under-refinement repair;
- ideally one over-refinement compression.

The paper is not considered scientifically closed merely because a venue threshold is reached.

---

## 11. Critical path and parallelization

### Critical path

\[
T1/T2
\rightarrow
L1
\rightarrow
L2
\rightarrow
D1/D2.
\]

Why:
- theory determines which learned distinctions are worth measuring;
- learned results determine the strongest intervention target.

### Parallel exact/native path

\[
R2/R3
\parallel
G3/G4/G5
\parallel
M\text{-tooling}.
\]

These can proceed while T/L experiments run.

### Later bridge

\[
T3/COMPOSE
\]

begins only after the first operational core is stable.

---

## 12. Decision gates

### Gate 1 — theory survival
If T1 shows OACR is only a renaming of one mature formal object, stop expansion and redefine the contribution before further experiments.

### Gate 2 — learned horizon
If GRACE remains fully equivalent through H=2 on sufficiently broad frozen banks, preserve the negative and move to L2; do not tune until a positive appears.

### Gate 3 — second learned ecology
If L2 produces the same partition behavior as L1, ask whether this is a meaningful cross-mechanism law. If it differs, explain the difference from native operation semantics.

### Gate 4 — feature minimality
No candidate feature is called necessary unless ablation/refinement creates under-refinement within a declared candidate family or a theorem establishes stronger necessity.

### Gate 5 — constructive value
If no representation intervention can be derived from OACR, the first paper remains a theory/diagnostic contribution and requires broader natural/learned evidence.

---

## 13. Full-strength target rather than minimum target

The program should be judged by closure, not count.

A strong stopping condition for the first major paper is:

- theory boundary fully audited;
- at least two materially different learned write ecologies;
- exact relational evidence with positives and controls;
- natural native-system evidence across multiple repositories;
- horizon/action-breadth analysis in at least two carriers;
- prospective prediction in at least one learned carrier;
- at least one successful constructive representation intervention;
- no unresolved semantics inflation from L1 to L2.

An exceptional version additionally has:
- both augmentation and compression interventions;
- a measurable cross-system operational-information law;
- a clean bridge into COMPOSE without diluting the WRITE/adequacy core.

---

## 14. Immediate execution order

**Now:**
1. T1 theory ledger.
2. L1 GRACE H=2 protocol.
3. G3 complete all 29 natural Git candidates.
4. G4 matched Git controls.
5. R2 all-candidate relational audit with negatives.
6. Build common partition/measurement tooling for \(N_H\), under-/over-refinement, and first-failure horizon.

**After those results:**
7. Select L2 learned carrier from the unresolved adequacy question.
8. Run L2 at serious scale.
9. Freeze prospective predictor.
10. Choose D1/D2 intervention targets.
11. Only then decide whether a third learned ecology or additional native carrier is scientifically necessary.

---

## 15. Provisional paper-strength targets

### Strong top-tier ML / representation paper
Requires:
- T1/T2 closed;
- L1 + L2;
- R2;
- G3/G4 plus repository replication;
- horizon law;
- at least one constructive intervention.

### Broader high-impact target
Requires everything above plus:
- cross-system operational-information scaling;
- prospective generalization;
- both under-refinement repair and over-refinement compression if feasible;
- evidence that OACR changes representation design decisions rather than merely redescribing known systems.

The project should not lower its target merely because an earlier publishable package becomes available.
