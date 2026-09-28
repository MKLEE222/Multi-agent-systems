# OACR Claim / Evidence Roadmap v1

**Date:** 2026-09-28  
**Status:** planning checkpoint after W1, R1, N1, G1, and G2

## 1. Current empirical state

### W1 — official GRACE + SCOTUS/BERT
- 8 registered current-read collision pairs.
- 0 one-step registered operational divergences.
- A2/A3 internal routing/structural distinctions separated all 8 pairs.
- Current interpretation: internal difference can over-refine a registered operation contract.

### R1 — registered Wikidata-derived relational graph
- 64 exact current-closure collisions.
- 64/64 diverged under the same registered deletion.
- A1/A2/A3 separated all required pairs.
- Current interpretation: current semantic closure can under-refine a future deletion contract.

### G1 — exact native Git construction
- 2 exact pre-tree collisions.
- 2/2 diverged under the same native merge.
- One conflict-vs-no-op case and one clean-content-divergence-vs-no-op case.
- A1 target-ancestry and A2 merge-base separated both.

### G2 — natural public Git history
Frozen source:
- repository: https://github.com/git/git.git
- source HEAD: 34f06850c16c7f7ac822b1adc71354f11b0f2ca3
- Git: 2.55.0
- first 10,000 merge commits enumerated
- 9,997 two-parent merges
- 29 naturally occurring tree-preserving merge candidates
- first 16 candidates tested under the preregistered stopping rule
- 16/16 were valid natural operational-divergence witnesses
- A1 target-ancestry and A2 merge-base separated all 16

This establishes natural occurrence in this repository/search window. It is not a prevalence estimate because execution stopped after the first 16 valid witnesses.

## 2. Theoretical red-team

The following mathematical ideas are mature and must be inherited rather than claimed as OACR inventions:

1. future-continuation equivalence and minimal automata (Myhill–Nerode);
2. behavioral equivalence / bisimulation and state aggregation;
3. minimal sufficient predictive states and causal states;
4. predictive state representations and input–output causal-state transducers;
5. strong preservation / minimal refinement in abstract interpretation;
6. contextual equivalence / full abstraction / representation independence;
7. representation languages compared by supported queries, transformations, and computational cost (knowledge compilation).

Therefore OACR must **not** claim to invent:
- behavior-induced equivalence classes;
- minimal sufficient state representations in general;
- partition refinement / bisimulation;
- the idea that future behavior can distinguish currently similar states.

## 3. Candidate OACR contribution

The plausible OACR-specific object is a cross-system framework for **computational representations under native operation contracts**.

Given a registered contract

\[
\mathcal C=(\mathcal O,\mathcal A,H,\mathsf{Legal},\mathsf{Cost}),
\]

OACR compares:

1. the partition induced by an implemented representation \(\rho\);
2. the partition required by registered future operational behavior.

A representation is diagnosed as:

- **under-refined** when it merges a pair whose registered future behavior differs;
- **over-refined** when it separates a pair whose registered future behavior remains equivalent;
- **contract-adequate on a bank/horizon** when it has no observed under-refinement.

The novelty target is the **lifting and operationalization** of mature behavioral/minimal-state ideas across heterogeneous computational representations whose native operations may include writes, revisions, merges, rollback, composition, legality, and cost—not a new invention of behavioral equivalence itself.

## 4. Expected main claim — provisional

The strongest claim currently worth targeting is:

> **Static fidelity is not a sufficient criterion for computational representation adequacy. A representation must be evaluated relative to the native operations it is expected to support. Comparing the partition induced by a representation with the partition induced by registered future operational behavior reveals both under-refinement and over-refinement, and this diagnosis transfers across learned, relational, and versioned computational systems without imposing a common domain semantics.**

This claim is not yet closed because the learned-system side currently contains a negative/over-refinement result but no strong positive operational-necessity witness on a serious learned parametric carrier.

## 5. Claim ladder

### C0 — already supported
- internal state difference is not sufficient evidence of operational necessity;
- exact current observation/content equality can coexist with different future native behavior;
- this phenomenon occurs naturally in a public Git repository;
- exact registered relational closure can under-refine a deletion contract.

### C1 — next paper-level gate
Show both under- and over-refinement across at least three materially different native carriers, including:
- one serious learned parametric carrier;
- one exact symbolic/relational carrier;
- one naturally occurring native-system carrier.

### C2 — stronger theory/measurement gate
Show that increasing operation horizon or enlarging the registered action family systematically refines the required operational partition, and quantify the resulting representation-information burden.

### C3 — constructive gate
Use the OACR diagnosis to change a representation:
- remove over-refining state without losing the registered contract, or
- add the missing distinction that repairs an under-refining representation.

A successful constructive intervention would move OACR from a diagnostic framework toward a representation-design method.

### C4 — broad general-law gate
Demonstrate that the same contract-relative adequacy principle predicts representational failure/design needs across several naturally generated systems and learned systems, with nontrivial practical consequences.

This is the bar required before making unusually broad cross-domain claims.

## 6. Immediate next work

### Gate T — mother-level theory audit
Perform an explicit claim-by-claim comparison with:
- Myhill–Nerode / automata minimization;
- bisimulation / coalgebra;
- causal states / computational mechanics;
- epsilon-transducers;
- predictive state representations;
- state abstraction in MDPs;
- strong preservation / complete shells;
- full abstraction / representation independence;
- knowledge compilation.

Output:
- INHERITED theorem;
- OACR reformulation;
- genuine extension;
- unsupported novelty claim to delete.

No paper prose before this audit is complete.

### Gate G — finish natural Git characterization
Run a separately frozen completion over all 29 G2 tree-preserving candidates so that the entire candidate set in the first 10,000 merges is characterized.

Then create matched non-divergent controls to measure whether ancestry/merge-base features over-refine the registered merge contract.

### Gate L/H — learned horizon separation
Prioritize the existing official GRACE + SCOTUS carrier rather than inventing a new learned carrier merely to obtain a positive example.

The next learned experiment should freeze a small action alphabet and compare

\[
\equiv_0,\;\equiv_1,\;\equiv_2
\]

on the same persistent-state bank.

Primary target:
- find or rule out a pair that is current-read matched and one-step operationally equivalent but two-step operationally nonequivalent;
- preserve exact action ordering, branch RNG, legality/status, and observation contract;
- report the first horizon at which the behavioral quotient refines.

This directly tests the OACR horizon claim and uses the learned carrier where W1 already supplied a clean negative at horizon 1.

A ReLU rescaling experiment is demoted to an optional **known-theory positive control**. Path-SGD (NeurIPS 2015) already establishes that rescaling-equivalent ReLU networks compute the same function while ordinary gradient descent is not rescaling invariant and can move the two networks to different functions after one update. Therefore that phenomenon cannot be an OACR novelty claim.

### Gate D — design intervention
Choose at least one carrier where OACR yields an actionable repair:
- sufficient state augmentation;
- quotient/compression of over-refining state;
- or an operation-aware representation redesign.

## 7. Paper-strength assessment

### Current state
The project has:
- a coherent mother question;
- exact cross-system witnesses;
- a natural public-history result;
- a useful negative learned result;
- a disciplined semantics methodology.

But the mathematical core overlaps heavily with mature theories of behavioral equivalence and minimal sufficient state. The current package is therefore **not yet strong enough to rest on formal novelty alone**, and the learned-system evidence is not yet balanced.

### Strong main-track target
A credible strong paper requires Gate T + G and a convincing learned horizon result, plus at least one constructive or minimality result.

The paper would then contribute:
1. a disciplined cross-system adequacy framework;
2. a theory-grounded diagnostic of under/over-refinement;
3. exact and natural cross-system evidence;
4. a serious learned-system instantiation.

### Higher-impact target
To justify a substantially higher-impact claim, Gate D is important. A framework that not only diagnoses but **changes representation design correctly** is much stronger than a collection of separation witnesses.

The strongest eventual paper should therefore be built around:

\[
\text{theory inheritance}
+
\text{cross-system operational diagnosis}
+
\text{natural evidence}
+
\text{learned-system evidence}
+
\text{constructive intervention}.
\]

## 8. Claim discipline

Until Gate T is complete, do not claim:
- a new minimal-state theorem;
- a new behavioral equivalence;
- a new partition-refinement principle;
- universal necessity of ancestry, provenance, routing, or support counts;
- universal cross-system hierarchy.

Until Gate L is complete, do not claim that OACR has established operational under-refinement in serious learned parametric representations.

Until Gate D is complete, call OACR a framework/diagnostic theory, not a representation-construction method.


## 9. Additional nearest-neighbor correction

The mother-level quotient idea sits especially close to:

- predictive state representations: state represented by multi-step action-conditional predictions of future observations;
- computational mechanics causal states: histories grouped by equality of future conditional distributions, yielding minimal sufficient predictive states;
- epsilon-transducers: minimal input-output process models with external inputs;
- strong-preservation / complete-shell results: minimally refine an abstraction to preserve a specified language/operators;
- bisimulation/state abstraction: behavior-preserving state aggregation.

These are not peripheral citations. They define the strongest novelty boundary for OACR.

The paper must therefore make its contribution at the level of:
1. computational-representation adequacy rather than invention of behavioral state equivalence;
2. heterogeneous **native operation contracts** including state-mutating writes/merge/revision and registered legality/cost;
3. empirical diagnosis of implemented representations as under- or over-refined;
4. cross-system evidence without imposing a common domain relation semantics;
5. ideally, an intervention that changes representation design.
