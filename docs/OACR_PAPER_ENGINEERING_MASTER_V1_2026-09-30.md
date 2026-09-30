# OACR Paper Engineering Master v1

**Date:** 2026-09-30  
**Status:** active manuscript-engineering control document  
**Scope:** defines paper identity, contribution order, evidence placement, result contingencies, and non-blocking dependencies

---

## 1. Paper identity

This is **not** a paper whose scientific identity is:

- "WRITE matters";
- "future behavior defines equivalence";
- "we discovered bisimulation / minimal state";
- "hidden state can affect future updates";
- "sequential model edits can interfere";
- "Git history can matter despite equal trees".

All of those are either too narrow or substantially covered by mature neighboring literatures.

The paper's stable identity is:

> **Native-contract adequacy auditing and certificate-constrained bidirectional repair of persistent computational representations. Computational representations should preserve the distinctions required by their registered continuation, but not distinctions the contract cannot justify; accepted repair changes representation structure while leaving native semantics fixed and is validated by independent native closure replay.**

WRITE is the dominant first-order experimental layer.

COMPOSE enters as the minimum extension needed when transformations can alter the semantics, qualification, or response of later transformations.

---

## 2. First-page problem statement

Recommended first-page mother question:

> **Which distinctions must a persistent computational representation preserve so that the object can continue to support its registered future operations?**

Equivalent operational formulation:

\[
\text{Given representation }R\text{ and continuation contract }\mathcal C,
\text{ which state distinctions are required by }\mathcal C?
\]

The paper should immediately distinguish three objects:

1. current representation partition \(R\);
2. registered continuation / operational partition \(O_{\mathcal C}\);
3. full internal-state identity \(R_{\rm full}\).

The central finite-contract phenomenon is:

\[
R_{\rm current}
\prec
O_{\mathcal C}
\prec
R_{\rm full}.
\]

The constructive target is a contract-derived representation \(R_{\rm gate}\) satisfying:

\[
R_{\rm gate}=O_{\mathcal C}
\]

on the frozen carrier, followed by exact native replay.

---

## 3. Stable paper thesis

The thesis that is already supportable independently of the pending learned-recovery outcome is:

> **Representation adequacy is contract-relative rather than a property of static fidelity alone. Across learned, relational, and version-history carriers, current equivalence can fail to preserve registered future operations, while internal/full-state distinctions can remain operationally irrelevant. On exact relational carriers, an operation-derived representation removes both forms of mismatch and reproduces every registered native outcome. Composition does not automatically create additional representational demand; delayed demand appears only in mechanisms where earlier transformations can change later continuation semantics.**

The final sentence should remain mechanism-qualified unless prospective COMPOSE positives broaden the evidence.

---

## 4. Contribution stack

### C1 — Operational adequacy measurement

Define a registered continuation contract

\[
\mathcal C=(\mathcal O,\mathcal A,H,\mathsf{Legal},\mathsf{Cost},\ldots)
\]

only with coordinates needed by the carrier.

Compare implemented representation partition \(R\) with the continuation-induced partition \(O_{\mathcal C}\).

Directional information gaps:

\[
U=H(O_{\mathcal C}\mid R)
\]

for under-refinement / omitted distinctions,

and

\[
E=H(R\mid O_{\mathcal C})
\]

for over-refinement / unnecessary distinctions.

Novelty discipline:

- behavioral equivalence itself is inherited;
- partition refinement/minimization is inherited;
- OACR contributes a disciplined cross-carrier **representation adequacy audit under native operation contracts** and its empirical/constructive use.

### C2 — Cross-carrier directional evidence

Use materially different native carriers to establish that static/current equality and full identity fail in opposite directions.

Main evidence:

- exact relational shared-contract carriers;
- natural native Git history;
- serious learned parametric carrier.

Do not force all carriers to share the same semantic relation.

### C3 — Certificate-constrained bidirectional representation repair

This is the strongest accepted constructive identity.

R3:

- 272 states;
- 64 registered deletions;
- 101 operational classes;
- closure-only \(U=3.3914\), \(E=0\);
- full asserted identity \(U=0\), \(E=4.6960\);
- contract-gated representation:
  \[
  U=E=0;
  \]
- 17,408/17,408 native replay cells exact;
- per-state delta records reduced by 63.10%.

Fresh R4-building:

- 272 states;
- 64 actions;
- 23 operational classes;
- current closure:
  \[
  U=0.76597,\ E=0;
  \]
- full asserted identity:
  \[
  U=0,\ E=7.32149;
  \]
- contract-gated representation:
  \[
  U=E=0;
  \]
- 17,408/17,408 exact native replay;
- declared delta records reduced by 91.88%.

Accepted bidirectional formulation:

\[
\Phi^+_{\mathcal C,\kappa}(R_{\rm current})
=
\Phi^-_{\mathcal C,\kappa}(R_{\rm full})
=
R_{\rm gate}
=
O_{\mathcal C}.
\]

On R4-building:

- additive correction: 0→22 per-state deltas;
- subtractive correction: 271→22 by removing 249 inactive deltas;
- both reach the same 23-block target;
- \(U_\mu=E_\mu=0\);
- 17,408/17,408 native replay cells exact.

The representation-repair identity is independently verified in run 36680594535.

### C4 — Continuation depth / COMPOSE mechanism contrast

Already stable evidence:

- R3/R4 registered relational deletion:
  - distinction is H1-active or inert under the whole frozen deletion universe;
  - no delayed finite activation depth >1 observed.
- GRACE L1b:
  - 224 H0 collisions;
  - no H0→H1 or H1→H2 separation under the complete frozen panel.
- SQEC controlled legality projection:
  \[
  \Gamma_1^{\rm full}
  =
  \Gamma_1^{\rm projected},
  \qquad
  \Gamma_2^{\rm full}
  \ne
  \Gamma_2^{\rm projected};
  \]
  native replay yields the registered legality failure / regret consequence.

Interpretation:

> **action depth alone does not generate representational demand. A scientifically meaningful COMPOSE effect requires a mechanism by which earlier transformations alter later continuation semantics.**

Fresh fixed-interpreter repair confirmation:

- 12 variants;
- one fixed transition skeleton, compiler, and native executor;
- FULL/B0/B1/B2/B3 differ only in explicit continuation-representation objects;
- B0: H1=0, H2=12;
- B1 full restore: exact;
- B2 one-rule contract-relevant repair: exact;
- B3 equal-cost sham rule: H1=0, H2=12;
- independent verifier mismatch count: 0.

Thus the paper can claim representation-level causal repair under fixed semantics, not merely guard restoration.

Prospective learned evidence now changes headline emphasis rather than the core repair identity.

---

## 5. Paper versions frozen before pending outcomes

### Version A — learned recovery positive

Trigger:

- at least one verified R2+F2 recovery-hysteresis witness;
- deterministic primary witness selected by frozen rule;
- two fresh targeted native replays pass.

Then the paper headline can be strengthened to:

> **A representation can certify recovery of the present while remaining insufficient to predict the response to a later common update.**

COMPOSE becomes a main result section.

The empirical mechanism contrast becomes:

1. fixed-domain relational deletion: no delayed demand;
2. controlled dynamic qualification: exact delayed demand;
3. learned recovery: current behavior restored, later common update diverges.

### Version B — learned recovery negative or underpowered

If strong negative:

- abundant accepted recovered states;
- complete future branches;
- zero future separation.

Then report it as a genuine boundary:

> parameter/history difference plus present recovery is not sufficient for continuation divergence under the frozen learned contract.

If recovery construction is underpowered:

- retain as construction boundary;
- do not rescue by weakening the recovery contract.

In either case, the paper remains publishable around:

1. contract-relative adequacy;
2. directional under/over-refinement;
3. exact cross-carrier WRITE evidence;
4. exact constructive redesign;
5. COMPOSE mechanism contrast with controlled SQEC positive and exact negative controls.

COMPOSE is then a bounded extension rather than the paper's headline.

---

## 6. Section architecture

### 1. Introduction

Goals:

- identify the representational problem in the first paragraph;
- distinguish current fidelity from continuation adequacy;
- show coarse-vs-full mismatch in one visual;
- state that OACR inherits behavioral equivalence rather than claiming to invent it;
- state constructive and empirical contributions.

Do **not** start with model editing, Wikidata, or Git.

The first page must read as a representation / information / computational-state paper.

### 2. Operational adequacy under continuation contracts

Define:

- persistent state;
- representation \(R\);
- registered continuation contract \(\mathcal C\);
- operational quotient \(O_{\mathcal C}\);
- \(U\), \(E\);
- depth-indexed continuation only as needed.

Explicit inheritance paragraph:

- contextual equivalence;
- bisimulation / coalgebra;
- predictive / causal state;
- strong preservation / abstract interpretation;
- representation independence.

State clearly:

> OACR's contribution is not the existence of behavioral quotients; it is the operation-contract audit of implemented computational representations, cross-carrier measurement, and representation intervention.

### 3. Experimental discipline and native contracts

Explain before results:

- same-contract discipline;
- freeze-before-outcome;
- outcome-blind action/witness selection;
- native replay;
- independent verifier;
- scientific negative vs engineering failure.

This section is important because many results depend on avoiding carrier/action-selection coupling.

### 4. First-order WRITE evidence

#### 4.1 Exact relational shared-contract mismatch
R3 / R4.

#### 4.2 Natural version-history mismatch
G5/G1/G2 as appropriate.

#### 4.3 Learned persistent-state evidence
Include:

- GRACE negative boundary;
- L2b fold0 native positive;
- do not overclaim prevalence.

Section message:

> neither hidden state difference nor current equality alone determines representational necessity; the operation contract does.

### 5. From diagnosis to representation redesign

This should be a major paper section, not appendix.

Lead with:

\[
R_{\rm current}\prec O_{\mathcal C}\prec R_{\rm full}.
\]

Then derive/define the contract-gated delta representation.

Present developmental R3 and fresh R4-building separately:

- exact partition match;
- \(U=E=0\);
- native replay;
- physical delta-record reduction.

This is the point at which OACR becomes more than a diagnostic taxonomy.

### 6. When composition creates new demand

Start from a negative proposition:

> composition alone is not enough.

Evidence:

- R3/R4 fixed-domain deletion closure;
- GRACE H2 negative.

Then introduce the continuation-interface mechanism:

\[
(X,\Gamma_X)\xrightarrow{a}(X',\Gamma_{X'}).
\]

Controlled SQEC bridge:

- root interface equal;
- shared first transformation;
- later legality differs.

Pending slot:

- learned recovery hysteresis;
- natural Git H2 only if independently accepted.

Do not promote Git just because producer repeatedly returned zero before carrier acceptance.

### 7. Related work / theory inheritance

Organize by what is inherited, not by domain:

1. behavioral/contextual equivalence;
2. state abstraction / predictive state;
3. abstract interpretation / strong preservation;
4. representation independence;
5. knowledge compilation / supported transformations;
6. sequential learned editing as a carrier literature.

The nearest-neighbor section must proactively delete fake novelty.

### 8. Limits and scope

Explicit limits:

- finite registered contracts;
- no universal minimality claim;
- no universal provenance necessity;
- no prevalence claims from selected natural banks;
- learned evidence is contract/fold limited;
- SQEC COMPOSE evidence is retrospective mechanism evidence;
- cultural/authority continuity is the broader program, not established by the present computational paper.

### 9. Conclusion

Return to:

> representation adequacy concerns what an object must preserve in order to continue under the operations it is expected to support.

---

## 7. Figure plan

### Figure 1 — OACR object

Single visual:

\[
\text{current representation}
\rightarrow
\text{registered continuation}
\rightarrow
\text{operational quotient}
\]

with coarse/full/gated representations.

Must make the paper legible without domain details.

### Figure 2 — Directional mismatch and repair

Three columns:

- current/closure representation: under-refines;
- full identity: over-refines;
- contract-gated: exact.

Use R4-building as the clean fresh example.

Show:

- 1 vs 23 vs 272 blocks;
- \(U/E\);
- 22 active vs 249 inactive deltas;
- 17,408 exact replay cells.

### Figure 3 — WRITE activation spectrum

Use WACT-R / learned example to show:

- same present;
- action-specific relevance;
- inert vs active distinctions.

Do not make this the mother figure.

### Figure 4 — COMPOSE mechanism contrast

Three panels:

A. relational deletion:
\[
d_A=1\text{ or }\infty
\]

B. SQEC latent guard:
\[
H1=,\ H2\ne
\]

C. learned recovery:
pending final disposition.

If learned is negative, panel C becomes a boundary/control rather than forcing a positive story.

---

## 8. Table plan

### Table 1 — Carrier / contract / representation / outcome

Columns:

- carrier;
- current representation;
- native operation contract;
- horizon;
- under-refinement;
- over-refinement;
- verifier;
- status.

### Table 2 — Constructive redesign

Rows:

- R3;
- R4-building;
- later fresh carriers if accepted.

Columns:

- states;
- actions;
- operational classes;
- active deltas;
- \(U/E\) before;
- \(U/E\) after;
- replay cells;
- physical record reduction.

### Table 3 — COMPOSE evidence ledger

Rows:

- R3;
- R4-building;
- GRACE L1b;
- SQEC;
- Git G5-H2;
- learned recovery.

Columns:

- H1 relation;
- H2 relation;
- mechanism;
- prospective/retrospective;
- scientific disposition.

---

## 9. Results that belong in main text

Definitely main text:

- R3/R4 directional mismatch;
- R4 fresh exact redesign;
- WACT / learned evidence sufficient to establish operation-relative relevance;
- fixed-domain COMPOSE negative;
- SQEC mechanism bridge;
- learned recovery if strong enough.

Appendix / supplement:

- long carrier-construction details;
- all individual WACT roots;
- full action matrices;
- engineering failure chronicles;
- Git carrier archival repair;
- individual checksums except authoritative acceptance table;
- extended formula derivations inherited from standard equivalence theory.

---

## 10. Non-blocking dependency policy

The following engineering debt must **not** block manuscript drafting:

### Git G5 carrier recovery

Role:

- supporting natural-history / H2 boundary;
- not required for C1–C3;
- only enters COMPOSE main evidence after executable-carrier + independent H2 acceptance.

Until then mark:

\`PENDING INDEPENDENT CARRIER ACCEPTANCE\`.

### Learned recovery run

Role:

- determines Version A vs Version B;
- only Section 6 and abstract/conclusion emphasis remain conditional.

Sections 1–5 and 7–8 can be written now.

### WACT-R full-root finalization

Use only verified accepted counts in prose.
Full root ledger can be updated later without changing the paper architecture.

---

## 11. Reviewer-risk register

### Risk 1 — "This is just bisimulation / Myhill–Nerode"

Defense:

- concede inheritance explicitly;
- contribution is implemented-representation adequacy audit under native contracts;
- directional U/E diagnosis;
- cross-carrier execution;
- constructive representation intervention.

### Risk 2 — "Your examples are hand-built"

Defense:

- fresh prospectively frozen R4 carrier;
- natural Git evidence where accepted;
- learned native editor;
- outcome-blind construction and verifier separation.

### Risk 3 — "Full state always solves this"

Defense:

- full state demonstrably over-refines;
- quantify \(E>0\);
- show contract-gated representation reaches exact operational quotient with fewer stored deltas.

### Risk 4 — "Longer horizon trivially distinguishes more"

Defense:

- exact R3/R4 deletion result rejects generic monotone-horizon story;
- GRACE H2 negative;
- COMPOSE section is about state-dependent continuation semantics, not sequence length.

### Risk 5 — "Learned effects are just sequential-edit interference"

Defense:

- do not claim path dependence is new;
- learned result, if positive, is framed as a representation-closure failure conditioned on present recovery.

### Risk 6 — "Cross-domain framework is too broad"

Defense:

- common object is contract-relative representation adequacy;
- domain semantics remain carrier-native;
- no universal carrier law;
- explicit finite-contract boundaries.

### Risk 7 — "This is just CEGAR / abstraction refinement"

Defense:

- concede the generic refine-and-reverify loop;
- OACR repairs the deployed persistent representation, not the verifier's abstraction;
- \(U_\mu/E_\mu\) make correction bidirectional rather than monotone precision addition;
- native executor and contract remain fixed;
- R4 verifies both additive and subtractive correction to the same quotient.

### Risk 8 — "SQEC just adds the known guard back"

Defense:

- v2 separates fixed transition skeleton from explicit representation object;
- one compiler and one native executor interpret every baseline;
- B2 and B3 have equal representation cost;
- only the contract-relevant B2 rule repairs H2;
- independent verifier reconstructs all matrices.

---

## 12. Writing order

Proceed now, in this order:

1. Section 2 — formal object and inheritance boundary.
2. Section 5 — constructive redesign; strongest stable result.
3. Section 3 — experimental discipline.
4. Section 4 — WRITE evidence.
5. Section 1 — introduction, after Sections 2/5 are stable.
6. Section 7 — related work.
7. Section 6 — COMPOSE, with pending learned/Git slots.
8. Abstract and conclusion last.

This avoids writing the introduction around a still-moving empirical headline.

---

## 13. Provisional title families

Do not freeze final title yet.

### Stable / conservative
**Operational Adequacy of Computational Representations Under Native Transformation Contracts**

### Stronger
**From Static Fidelity to Continuation Closure in Computational Representations**

### Accepted identity emphasis
**Native-Contract Adequacy Auditing and Bidirectional Repair of Persistent Computational Representations**

### Constructive alternative
**What Must a Representation Preserve to Keep Working? Contract-Relative Audit and Repair**

Final title depends on whether COMPOSE becomes a headline result.

---

## 14. Immediate paper-engineering tasks

### Now

- write formal Section 2;
- write constructive Section 5;
- build Figure 1 and Figure 2 specs;
- build Table 1 / Table 2 authoritative value ledger;
- rewrite claim/evidence roadmap around continuation rather than fixed WRITE.

### When learned recovery completes

- mechanically classify under frozen disposition;
- choose Version A or B;
- populate Section 6 panel C;
- update abstract claim strength.

### When Git carrier repair completes

- either accept H2 natural negative after independent replay;
- or leave Git H2 out of main claims and retain only accepted G1/G2/G5 H1 evidence.

No manuscript section waits on this engineering repair.
