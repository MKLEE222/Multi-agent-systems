# OACR Neighbor Venue Map — 2026-09-30

## Purpose

Map the actual publication venues of OACR's nearest intellectual neighbors before selecting a target venue.

This document separates:

1. **historical/intellectual neighbors** — where the ideas OACR inherits were actually published;
2. **carrier-specific neighbors** — where related repair/editing evidence is published;
3. **current venue fit** — where the present paper identity most naturally sits;
4. **DH boundary** — what would have to change for a Digital Humanities venue to become natural.

---

## 1. Formal representation / abstraction neighbors

### Strong preservation

Francesco Ranzato and Francesco Tapparo,
**Strong Preservation as Completeness in Abstract Interpretation**.

Published at:

**ESOP 2004 — European Symposium on Programming.**

This is the closest neighbor for operator/language-relative refinement and strong preservation.

Follow-up:

Ranzato and Tapparo,
**Generalized Strong Preservation by Abstract Interpretation**.

Published in:

**Journal of Logic and Computation**, 17(1), 2007.

### Representation independence

John C. Mitchell,
**Representation Independence and Data Abstraction**.

Published at:

**POPL 1986 — ACM Symposium on Principles of Programming Languages.**

Amal Ahmed, Derek Dreyer, Andreas Rossberg,
**State-Dependent Representation Independence**.

Published at:

**POPL 2009.**

These papers establish the strongest formal precedent for internal representation differences being irrelevant when preserved by an operation interface.

### Counterexample-guided abstraction refinement

Clarke, Grumberg, Jha, Lu, Veith,
**Counterexample-Guided Abstraction Refinement**.

Published at:

**CAV 2000 — Computer Aided Verification.**

This is the closest generic neighbor to an audit/refine/reverify loop.

---

## 2. Representation capability / AI neighbor

Darwiche and Marquis,
**A Knowledge Compilation Map**.

Published in:

**JAIR — Journal of Artificial Intelligence Research**, 2002.

The key inherited idea is that representation quality can be evaluated by the queries and transformations a representation supports, not syntax alone.

---

## 3. Repair-methodology neighbors

The classic semantic / automated program-repair lineage is concentrated in software-engineering venues.

Examples:

- Le Goues et al., systematic automated program repair — **ICSE 2012**.
- Nguyen et al., SemFix — **ICSE 2013**.
- Mechtaev et al., DirectFix — **ICSE 2015**.
- Mechtaev et al., Angelix — **ICSE 2016**.
- anti-patterns in search-based program repair — **FSE 2016**.
- concolic program repair — **PLDI 2021**.

Thus "failure/certificate -> repair -> execution validation" is most at home historically in:

- **ICSE**
- **FSE**
- **PLDI**

rather than in an AI or DH venue.

---

## 4. Learned model-editing neighbors

The learned carrier has a different venue ecology.

Examples:

- Li & Chu, sequential knowledge attenuation — **Findings of ACL 2024**.
- Yang et al., Butterfly Effect of Model Editing — **Findings of ACL 2024**.
- Lyu et al., EvoEdit — **Findings of ACL 2026**.
- Zhang et al., spectral characterization of sequential-edit collapse — **ACL 2026 Long Papers**.
- Caddeo et al., behavioral reversibility — **Applied Sciences 2026**.

Therefore ACL/Findings is a natural home for a paper whose scientific object is **model editing**.

It is not the natural home for present OACR because learned editing is a carrier/control rather than the paper's central object.

---

## 5. Digital Humanities neighbor

Birnbaum & Spadini,
**Reassessing the locus of normalization in machine-assisted collation**.

Published in:

**Digital Humanities Quarterly 14(3), 2020.**

Its structure is important for comparison:

- starts from a recognized scholarly practice: textual collation;
- interrogates normalization as a scholarly/interpretive operation;
- uses computational pipeline structure to revise understanding of that practice;
- returns the computational argument to textual-scholarship consequences.

Current **Digital Scholarship in the Humanities** scope explicitly welcomes theoretical, methodological, experimental, and applied DH research, but states that AI/data-science research is out of scope when it lacks theoretical relevance or direct application to Digital Humanities.

Therefore present OACR, as currently written, is not naturally a DSH/DHQ paper.

A DH-target version would need a humanistic operation/claim to be a constitutive part of the evidence, not merely a motivation paragraph.

---

## 6. Current venue-fit map for OACR

Current paper identity:

**native-contract adequacy audit -> certificate-constrained bidirectional representation repair -> native closure verification**

### OOPSLA / PACMPL

Current scope explicitly covers practical and theoretical investigations of programming systems, languages, environments, modeling, design, implementation, generation, analysis, verification, testing, evaluation, maintenance, and reuse.

Why OACR could fit:

- representation is the scientific object;
- formal operator/contract semantics;
- fixed interpreter / representation object separation;
- constructive representation transformation;
- empirical native replay.

Risk:

- OACR is not centered on a programming language or conventional program abstraction;
- cross-carrier breadth must be presented as a general programming-systems representation problem.

2027 deadlines:

- Round 1: **14 October 2026**
- Round 2: **7 April 2027**

### PLDI

PLDI covers programming-language/programming-systems design, implementation, theory, applications, and performance.

Why OACR could fit:

- implemented representation transformation;
- compiler/interpreter distinction;
- native execution;
- formal + empirical design result.

Risk:

- current paper is less compiler/language-design-centric than typical PLDI work;
- must make the representation/interpreter methodology feel like a systems/programming abstraction contribution rather than a cross-domain framework.

2027 research-paper deadline:

**12 November 2026.**

### CAV

CAV is explicitly the flagship venue for theory and practice of computer-aided formal analysis, spanning theory, algorithms, implementation, and applications, including machine learning.

Why OACR could fit:

- strong-preservation / abstraction-refinement ancestry;
- formal adequacy criterion;
- certificate-constrained correction;
- independent verification.

Risk:

- OACR audits a representation rather than primarily verifying a system property;
- a stronger verifier/tool/algorithm presentation may be needed.

2027 submission deadline:

**20 January 2027.**

### FSE

FSE explicitly accepts theoretical, empirical, conceptual, and experimental software-engineering research, including:

- program analysis;
- model checking;
- program repair;
- program synthesis;
- software evolution;
- software engineering for AI.

Why OACR could fit:

- broadest natural home for the cross-carrier empirical + formal methodology;
- repair lineage is familiar;
- Git and learned-system carriers do not look anomalous here;
- replication package / native replay discipline is aligned with venue expectations.

Risk:

- must articulate a concrete software-engineering problem, not only a general representation philosophy.

### ICSE

Historically extremely natural for the repair lineage, including SemFix/Angelix.

But ICSE 2027's research-paper deadline was **30 June 2026**, so the 2027 cycle is already closed.

A later ICSE cycle remains conceptually plausible if the paper is framed as software-engineering methodology.

### TOSEM

A plausible journal home for a long, archival, cross-carrier methodology paper.

Strengths:

- specification/design/development/maintenance;
- methodologies, languages, data structures, algorithms;
- room for formal development plus large experimental/audit package.

Risk:

- slower journal path and less concentrated "one-shot" conference positioning.

### JAIR

Conceptually adjacent through knowledge compilation and representation sufficiency.

Current OACR fit is weaker than OOPSLA/FSE/CAV because:

- the paper is not primarily an AI representation-language result;
- two of the strongest carriers are relational / software-history rather than AI tasks.

### ACL / Findings

Not a natural target for current OACR.

Would become natural only if the learned editing/recovery experiment became the central scientific object and the relational/Git work became supporting theory.

### DHQ / DSH

Not a natural target for current OACR identity.

Would become natural only after a humanistic carrier makes scholarly interpretation, practice, authority, continuity, or claim formation part of the **main dependent variable**.

---

## 7. Cold-start venue conclusion

The nearest-neighbor publication ecology is not one venue but three layers:

### Formal ancestry
- POPL
- ESOP
- CAV
- Journal of Logic and Computation

### Constructive / repair methodology
- ICSE
- FSE
- PLDI
- potentially OOPSLA

### Learned carrier
- ACL / Findings

The current OACR paper combines the first two layers.

Therefore its most natural contemporary comparison set is:

[
oxed{
	ext{OOPSLA / FSE / CAV / PLDI}
}
]

rather than ACL or DH.

The strongest venue choice depends on manuscript emphasis:

- **representation semantics / programming abstractions** -> OOPSLA;
- **cross-carrier empirical methodology / repair** -> FSE;
- **formal audit/certificate/verification algorithm** -> CAV;
- **implemented representation transformation / programming systems** -> PLDI.

---

## 8. Domain-drift implication

This map confirms a substantive distinction in the research program.

The present OACR paper is a **computational-methodology branch** of the larger mother problem.

It should not be artificially relabeled as Digital Humanities simply because the mother question is humanistic.

A later DH paper should begin from the humanistic continuation problem itself and use OACR machinery as infrastructure, in the same way that the machine-assisted-collation literature begins from a textual-scholarly operation rather than from an abstract representation theorem.
