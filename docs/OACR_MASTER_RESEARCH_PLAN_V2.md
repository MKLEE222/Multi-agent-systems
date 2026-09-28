# OACR Master Research Plan v2 — Post-R3/G5/M2 Audit

**Date:** 2026-09-28  
**Status:** current research plan after same-contract recovery and M2 second audit  
**Supersedes for planning:** `OACR_MASTER_RESEARCH_PLAN_V1.md`  
**Does not erase:** earlier protocols, checkpoints, failed designs, or red-team records.

## 1. Mother question

> **What distinctions must a computational representation preserve in order to remain adequate for the observations and native operations required by a system?**

The core direction remains:

[
	ext{native behavior}
ightarrow
	ext{required distinctions}
ightarrow
	ext{representation diagnosis}
ightarrow
	ext{identification}
ightarrow
	ext{representation redesign}.
]

OACR does not start from an internal feature and declare it meaningful.

---

## 2. Formal object

For a registered contract

[
mathcal C=(mathcal O,mathcal A,H,mathsf{Legal},mathsf{Cost}),
]

a frozen state bank (X), state distribution (mu), and implemented representation partition (R), let (O_{mathcal C}) be the operational partition induced by registered native behavior.

Directional mismatch is measured by:

[
U_{mathcal C}(R)=H(O_{mathcal C}mid R),
]

[
E_{mathcal C}(R)=H(Rmid O_{mathcal C}).
]

These are inherited partition-information quantities.

- (U=0): contract adequacy on the registered support.
- (U=E=0): representation and operational partitions match.
- This is partition-level matching, not physical storage minimality.

The inherited monotonicity theorem for nested operational partitions is background mathematics, not a paper novelty claim.

---

## 3. Revised claim architecture

### Claim A — contract-relative implemented adequacy

The adequacy of an implemented representation is defined relative to a declared native-operation contract, not by static fidelity alone.

**Status:** framework statement; theory inheritance must remain explicit.

### Claim B — directional mismatch exists in implemented systems

Under one frozen contract:

- a representation can be too coarse and omit distinctions required by native operations;
- a different representation of the same states can be too fine and preserve distinctions irrelevant to that contract.

**Status:** accepted in finite exact form through R3 and held-out G5.

### Claim C — operational demand depends on contract content, not merely breadth

For equal action-family cardinality, different action subsets can induce different operational partitions and different adequacy gaps.

The empirical target is therefore not a single (kmapsto U_k,E_k) curve.

The target is the structure over the action-subset lattice:

[
A'subseteq A
mapsto
O_{A'}.
]

Key observables include:

- distribution of (|O_{A'}|) at fixed (|A'|);
- distribution of (H(O_{A'}));
- (U/E) distributions for fixed representations;
- redundant versus refinement-generating operations;
- contract subsets that reproduce the full operational quotient.

**Status:** accepted as a developmental exact-carrier result on M2-R; natural Git clean rerun pending; fresh-carrier confirmation required.

### Claim D — operational quotient can be identifiable by a smaller action basis

For a fixed state bank and full action family (A), define a finite registered distinguishing basis size:

[
b(X,A)
=
min_{Ssubseteq A}
left{
|S|:
O_S=O_A
ight}.
]

This is a measurement target, not currently claimed as a new mathematical object.

The scientific question is:

> How much of the registered action family is actually needed to identify all distinctions required by the full contract?

**Status:** exploratory.

Current R3 post-hoc result:

[
b=13
quad	ext{for the 64-action panel.}
]

All 13 are indispensable by leave-one-out necessity and jointly sufficient.

This must be preregistered and prospectively tested on fresh carriers before promotion.

### Claim E — OACR can identify a compact sufficient state representation

The project must move from diagnosing (U/E) to finding a structural representation (phi(X)) that recovers the operational quotient without simply storing the outcome table.

Required distinction:

- a small **action probe basis** is not itself a state representation;
- a lookup table over observed operational signatures is not a structural representation;
- a candidate representation must be computed from the state prior to executing the evaluated outcomes.

**Status:** open.

### Claim F — diagnosis can guide representation redesign

Two constructive targets:

[
Rightarrow R^+
]

that reduces omission (U), and

[
Rightarrow R^-
]

that reduces excess (E) while preserving (U=0).

**Status:** open and still the strongest practical gate.

---

## 4. What M2 changed

M2-R v2 invalidates the weak research framing:

> more registered operations smoothly imply more representational information demand.

The theorem only gives refinement monotonicity under set inclusion.

Empirically, on R3:

- 46/64 singleton actions generate no new operational distinction;
- one singleton action generates 85 operational classes;
- the full family generates 101 classes;
- equal-cardinality pairs range from 1 to 88 classes;
- 51/64 actions are redundant with respect to the full operational partition;
- 13 actions form the exact minimum full-partition distinguishing basis.

Therefore action count is a contract index, not an equal-interval demand metric.

The new empirical focus is **which operations generate which distinctions**.

---

## 5. Evidence status

### Accepted finite-contract core

#### R3 exact relational
- 272 current-closure-equivalent states;
- one shared 64-action deletion contract;
- 101 full-contract operational classes;
- R0 under-refines;
- Rfull over-refines;
- Rsupport64 remains one class and fails to recover the quotient.

#### G5 natural Git
On held-out validation under one frozen 12-target native merge panel:
- 48 natural same-tree pairs;
- 2 required separations;
- 46 equivalent pairs;
- tree-only under-refines;
- commit identity over-refines;
- full-panel target-ancestry vector exactly matches the finite registered operational partition.

Boundary:
- finite panel;
- one repository;
- only two positive validation pairs;
- target selection deliberately uses discovery ancestry diversity;
- ancestry is structurally tied to the already-up-to-date component of merge behavior.

### Accepted M2-R developmental characterization

- raw-carrier reconstruction passed;
- 3,978 registered contracts independently recomputed;
- endpoint regression passed;
- raw matrix verified;
- native deletion spot/full-state cross-checks produced zero mismatch;
- strong action-content anisotropy observed.

### Pending M2-G acceptance

Only the clean-runtime rerun may be accepted.

### Learned evidence

L1 five-seed GRACE H=2 remains a negative diagnostic:
- no H0→H1 or H1→H2 refinement in the frozen tiny bank;
- routing/structural features over-refine.

This is scientifically useful but insufficient for broad learned-system claims.

---

## 6. Revised quantitative language

Delete from active paper planning:

- (log_2N) as a general information law;
- “representation burden” when only class entropy is measured;
- action count as an equal-scale measure of operational demand;
- monotonicity itself as empirical novelty.

Allowed language:

- operational class count;
- operational entropy under declared (mu);
- directional omission/excess information;
- action-subset lattice;
- refinement event;
- registered distinguishing action basis;
- physical burden only when bytes/dimension/runtime/update cost are separately measured.

---

## 7. Next critical experiments

### P1 — finish clean M2-G validation

Acceptance requires:

1. clean workflow logs;
2. Git 2.55.0;
3. frozen source HEAD;
4. endpoint regression;
5. 4,096-subset reconstruction;
6. independent verifier pass;
7. artifact hashes;
8. reproducibility against the diagnostic run at scientific-manifest level.

### P2 — freeze fresh M2b before new carrier outcomes

M2b must test contract-content structure prospectively.

Required:

- at least one fresh exact relational carrier/state bank;
- at least two additional mature Git repositories;
- carrier inclusion criteria frozen before native outcomes;
- fixed action-panel selection algorithm;
- exact lattice where action count permits;
- registered action-basis calculation;
- failure retention if action-content heterogeneity or sparsity does not recur.

The fresh test is not “does monotonicity hold?”
It is:

> Does operational demand remain strongly content-dependent, and can a compact distinguishing basis be identified prospectively?

### P3 — relational state-representation identification

R3 now has a known 101-class target.

Search for a pre-operation structural state representation (phi) satisfying:

[
U(phi)=0
]

with substantially lower excess than full asserted identity.

Candidate families must be mechanistically motivated and frozen before evaluation.

Potential families:
- deletion-sensitivity invariants;
- support-criticality structure;
- cut/redundancy signatures;
- provenance structures tied to deletion consequences.

Do not use the operational outcome vector itself as the representation.

### P4 — constructive relational redesign

If a compact (phi) is identified:

- augment closure-only representation with (phi);
- verify (U) decreases or reaches zero;
- compare physical representation cost if feasible;
- compress full identity toward (phi) and verify registered behavior preserved.

This can close diagnosis → design in one exact carrier.

### P5 — learned expansion

Do not tune the current five GRACE pairs until positive.

Instead:

1. expand collision density/state-bank scale under preregistered construction;
2. freeze H=1/H=2 action contracts;
3. add a materially different persistent write mechanism;
4. compute exact/categorical operational partitions where valid;
5. preserve negative outcomes.

A learned positive is not required by fiat.
A sufficiently broad negative result can itself constrain when internal mutable state matters operationally.

---

## 8. Paper architecture after the audit

### Block 1 — inherited theory and OACR audit object

- behavioral equivalence/minimal quotients acknowledged as mature;
- (U/E) decomposition acknowledged as inherited information theory;
- OACR contribution target: audit implemented representations under native mutating contracts.

### Block 2 — same-contract mismatch

- R3 exact controlled carrier;
- G5 natural held-out native carrier;
- coarse versus fine representation mismatch under the same contract.

### Block 3 — contract-content geometry

- M2 exact action-subset analysis;
- equal breadth does not imply equal operational demand;
- refinement-generating versus redundant operations;
- distinguishing action basis as an identification object.

This block must be fresh-carrier replicated before being framed as cross-system structure.

### Block 4 — learned boundary

- scaled learned evidence;
- positive or negative result retained;
- establishes whether the same audit object remains meaningful under learned persistent state.

### Block 5 — identification and construction

- structural sufficient representation;
- augmentation/compression intervention;
- physical cost only if actually measured.

This block is more important than adding additional witness counts.

---

## 9. Strong stopping condition

The first OACR paper is scientifically closed only when:

1. theory inheritance boundary is explicit;
2. same-contract directional mismatch survives exact and natural carriers;
3. contract-content structure is prospectively tested on fresh carriers;
4. learned persistent state receives a serious-scale test;
5. at least one nontrivial structural representation is identified or a principled impossibility/negative result is established;
6. at least one constructive redesign is executed, or the paper explicitly remains an audit/identification contribution;
7. every main numerical result is reconstructible from frozen artifacts.

Publication venue is not part of these validity conditions.
