# OACR Novelty / Inheritance Lock v1

**Date:** 2026-09-30  
**Status:** manuscript authority; claims below constrain Introduction, Related Work, Abstract, and reviewer response  
**Purpose:** prevent OACR from claiming mature ideas as formal novelty while isolating the paper-level contribution that the empirical program can own.

## 1. Direct theoretical predecessors

### 1.1 Strong preservation and abstract interpretation

Ranzato & Tapparo's strong-preservation program establishes that an abstraction can be refined until it is complete / strongly preserving for a chosen specification language or semantic operator family, and relates the refinement to familiar behavioral equivalences.

Therefore OACR does **not** claim novelty for:

- minimal refinement relative to an operator/language family;
- strongly preserving abstractions;
- the existence of behavioral quotients;
- bisimulation/simulation/stuttering as refinement targets;
- completeness as the mathematical condition behind preservation.

Primary references:

- Ranzato, F. & Tapparo, F. *Strong Preservation as Completeness in Abstract Interpretation*. ESOP 2004.
- Ranzato, F. & Tapparo, F. *Generalized Strong Preservation by Abstract Interpretation*. Journal of Logic and Computation 17(1), 2007.

### 1.2 Representation independence

Representation-independence work studies when different internal implementations remain indistinguishable to clients because a representation relation is preserved by the permitted operations.

State-dependent variants further allow the representation relation itself to depend on mutable local state.

Therefore OACR does **not** claim novelty for:

- operation-preserved representation relations;
- contextual equivalence of different internal implementations;
- state-dependent representation relations as a formal idea.

Primary references:

- Mitchell, J. *Representation Independence and Data Abstraction*. POPL 1986.
- Ahmed, A., Dreyer, D., Rossberg, A. *State-Dependent Representation Independence*. POPL 2009.

### 1.3 Knowledge compilation / transformation-support maps

Knowledge-compilation work compares representation languages by the queries and transformations they support, together with succinctness.

Therefore OACR does **not** claim novelty for:

- evaluating a representation by supported queries/transformations in the abstract;
- transformation-support tradeoffs between representation languages;
- compilation as a route to operationally useful target representations.

Primary reference:

- Darwiche, A. & Marquis, P. *A Knowledge Compilation Map*. JAIR 17, 2002.

### 1.4 Behavioral / contextual equivalence more broadly

Automata, process semantics, coalgebra, contextual equivalence, predictive-state/state-abstraction, and Myhill–Nerode-style constructions all precede OACR.

OACR must never use phrases equivalent to:

> future behavior defines the true state

as a novelty claim.

That is inherited mathematical infrastructure.

---

## 2. Paper-level contribution OACR can own

The contribution is a **method + evidence + intervention** package for implemented persistent computational representations.

### 2.1 Native-contract representation audit

Given:

- an implemented representation \(R\);
- a frozen native-operation contract \(\mathcal C\);
- a finite registered state bank with reference measure \(\mu\);

construct the operational partition \(O_{\mathcal C}\) from native execution and audit both:

\[
U_\mu(R;\mathcal C)
=
H_\mu(O_{\mathcal C}\mid R)
\]

and

\[
E_\mu(R;\mathcal C)
=
H_\mu(R\mid O_{\mathcal C}).
\]

The methodological distinction is that OACR audits a **pre-existing implemented representation against a prospectively registered native continuation contract**, rather than beginning from an abstract semantic language and synthesizing its strongly preserving abstraction.

### 2.2 Directional diagnosis rather than preservation-only success

OACR treats both failures as first-class empirical objects:

- under-refinement: distinctions missing from the representation;
- over-refinement: distinctions stored but unnecessary for the registered continuation.

The paper's central empirical pattern is therefore not simply "is the abstraction sound?" but:

\[
R_{\rm current}
\prec
O_{\mathcal C}
\prec
R_{\rm full}.
\]

### 2.3 Same-contract / outcome-blind causal discipline

OACR makes the operation contract part of the experiment:

- same action family across registered states where possible;
- carrier/action selection frozen before outcome;
- hidden-state difference alone is not treated as necessity;
- scientific negative is separated from action/construction underpower;
- native replay is distinguished from structural prediction.

This discipline is necessary because the evaluator can otherwise manufacture representational necessity by choosing pair-specific future operations.

### 2.4 Cross-carrier execution with carrier-native semantics

The common object is representation adequacy; the native semantics remain heterogeneous.

Examples:

- graph reachability under deletion;
- Git history under merge;
- learned parameter state under native Finetune updates;
- dynamic legality/qualification under typed multistep transitions.

The paper should claim a common **audit object**, not a universal shared state ontology.

### 2.5 Audit -> representation intervention

The strongest constructive contribution is not the existence of an operational quotient.

It is the prospective chain:

\[
\text{registered contract}
\rightarrow
\text{structural certificate}
\rightarrow
\text{representation transform}
\rightarrow
\text{native replay}.
\]

On the relational carriers, the transform is derived without inspecting augmented-state post-action outcomes, then tested against the complete registered outcome matrix.

This is the point at which the paper moves beyond applying an equivalence definition.

### 2.6 Continuation-interface mechanism contrast

OACR distinguishes:

- repeated fixed-domain operations that create no additional representational demand;
- transformations that change the semantics/qualification/response of later transformations.

COMPOSE novelty must not be stated as novelty of depth-indexed equivalence.

The empirical contribution is the mechanism contrast under frozen carriers.

---

## 3. Claims forbidden by this lock

Do not claim:

- "we introduce operational equivalence";
- "we show for the first time that future operations determine state";
- "we derive the minimal abstraction for a set of operators" as a general theoretical novelty;
- "we introduce state-dependent representation independence";
- "we show transformations matter for representation design" without specifying the native-contract audit/intervention contribution;
- "we discover sequential-edit path dependence";
- "we prove a universal optimal representation";
- "OACR quotient is the unique minimal representation" outside a fully specified finite partition result.

---

## 4. Introduction positioning

The Introduction should use the following contrast.

### Mature question

> Which abstraction preserves a chosen semantic language/operator family?

This is inherited from strong-preservation / equivalence theory.

### OACR question

> Given an implemented representation in a persistent computational system, which of its distinctions are actually required by the native transformations the system is expected to support, which required distinctions are missing, and can the audit be converted into an executable representation repair?

The empirical object begins with a representation already used by a system rather than an abstraction synthesized solely from a specification language.

---

## 5. Reviewer-response boundary

### "This is just strong preservation."

Response structure:

1. Agree that the mathematical preservation/refinement substrate is inherited.
2. Point to the different empirical problem:
   - implemented representations;
   - native operation contracts;
   - under- and over-refinement measurement;
   - prospective same-contract controls;
   - heterogeneous carriers.
3. Point to the intervention:
   - outcome-blind structural certificate;
   - representation repair;
   - exhaustive native replay;
   - fresh carrier confirmation.

Do not defend by pretending strong preservation is less general than it is.

### "This is just representation independence."

Response structure:

1. Agree that operation-preserved representation relations are established theory.
2. OACR is not a proof technique for two ADT implementations.
3. OACR audits which distinctions of a concrete persistent representation are required by a registered continuation contract and measures both missing and excess distinctions.

### "This is just knowledge compilation."

Response structure:

1. Agree that queries/transformations as representation-language capabilities are established.
2. OACR's unit is an implemented persistent state representation and its native mutation semantics, not a language-level compilation map.
3. The key empirical object is mismatch between current/full representations and an observed operational quotient, followed by carrier-native repair/replay.

---

## 6. Strong-paper novelty threshold

For a strong paper, at least the following package must be visible in the first two pages:

1. mature theory inherited explicitly;
2. implemented-representation audit problem stated independently;
3. directional \(U_\mu/E_\mu\) mismatch;
4. prospective fresh evidence that neither current nor full representation matches continuation demand;
5. constructive representation repair with native replay;
6. bounded composition result explaining when one-step adequacy may cease to be enough.

No single element above is sufficient as the paper's novelty claim.

The novelty is the integrated empirical/constructive program.
