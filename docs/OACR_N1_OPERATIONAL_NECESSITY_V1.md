# OACR-N1 — Operational Necessity Criterion and Cross-Carrier Audit v1

**Date:** 2026-09-28  
**Status:** frozen methodological object; retrospective on OACR-W1/R1, prospective for later carriers

## 1. Why this object is needed

A hidden state distinction is not automatically an operationally necessary distinction.

OACR-W1 already provides a concrete warning: two GRACE states differed in registered routing/write-state information, yet under the eight registered future actions their post-write registered reads remained identical.

OACR-R1 provides the opposite case: two graph states had identical complete registered current closure, yet the same registered future deletion produced different complete post-write closures.

The next object must therefore distinguish:

1. a difference that merely exists internally;
2. a difference that some registered operation can expose;
3. a distinction that every representation adequate for that registered contract must preserve.

## 2. Registered contract

For a carrier, freeze a contract

\[
\mathcal C=(\mathcal O,\mathcal A,H),
\]

where:

- \(\mathcal O\) is the registered observation interface;
- \(\mathcal A\) is the registered action family;
- \(H\) is the registered action horizon.

This is an L1 experimental object under the OACR relation-semantics discipline. It does not claim to exhaust the carrier's full native/domain semantics.

Let

\[
\mathrm{Obs}_{\mathcal O}(z)
\]

be the complete registered observation signature of state \(z\).

## 3. Finite-horizon operational equivalence

Define recursively:

\[
B_0(z)=\mathrm{Obs}_{\mathcal O}(z).
\]

For deterministic registered actions,

\[
B_{h+1}(z)
=
\left(
B_0(z),
\left[
\operatorname{status}_a(z),
B_h(\Phi_a(z))
\right]_{a\in\mathcal A}
\right).
\]

Invalid, unavailable, or zero-write actions receive explicit status symbols; they are not silently dropped.

Then

\[
z\equiv_h z'
\iff
B_h(z)=B_h(z').
\]

For approximate learned observations, equality at the observation layer uses the preregistered tolerance. Action/status identities remain exact.

This is a registered finite-horizon behavioral equivalence, not a new general semantics theorem.

## 4. Pairwise operational necessity

If

\[
z\equiv_0 z'
\quad\text{but}\quad
z\not\equiv_H z',
\]

then any representation that is adequate for the frozen contract \(\mathcal C\) through horizon \(H\) must not identify those two states.

This is the core OACR necessity statement:

> the pair must be separated somehow.

It does **not** imply that one particular internal variable, provenance field, routing feature, support count, or history encoding is uniquely necessary.

## 5. Feature necessity must not be confused with pairwise necessity

For a candidate registered feature map \(F\):

### Under-refinement

\[
F(z)=F(z')
\quad\text{but}\quad
z\not\equiv_H z'.
\]

The feature map merges a pair that the operational contract requires to be separated.

### Over-refinement

\[
F(z)\neq F(z')
\quad\text{but}\quad
z\equiv_H z'.
\]

The feature distinguishes states even though the registered finite-horizon contract does not require that distinction.

### Contract-sufficiency on a finite bank

\[
F(z)=F(z')
\Longrightarrow
z\equiv_H z'
\]

for every evaluated pair in the frozen state bank.

This is finite-bank sufficiency only.

### Candidate-coordinate necessity

A coordinate of \(F\) is called necessary **within a declared candidate family** only if removing it introduces an under-refinement witness that was absent before.

This is an ablation result inside that candidate family, not a universal claim that all adequate representations must encode that variable explicitly.

## 6. Coarsest registered operational partition

Given a finite closed state bank and action family, iteratively refine the current-observation partition by registered successor behavior until either:

1. the horizon \(H\) is reached; or
2. the partition reaches a fixed point.

The resulting partition is the empirical target quotient for that frozen bank and contract.

Carrier features are evaluated against this behavioral partition rather than treated as ground truth.

This reverses the usual direction:

\[
\text{behavior required by the contract}
\rightarrow
\text{necessary state separations}
\rightarrow
\text{candidate representational features}.
\]

Not:

\[
\text{available internal feature}
\rightarrow
\text{declare it semantically necessary}.
\]

## 7. Retrospective audit registered for existing carriers

### OACR-W1 / GRACE + SCOTUS

Source artifact:

- workflow run: 36376047412
- artifact: `oacr-w1-v1`
- result SHA256: `60b3e4c4b3ca20134a242b21fc7b31cea46e88e076c3fa314b8f54fbedf2ab6b`

Registered first-pass audit:

- horizon: one future write;
- observations: the frozen W1 read family;
- actions: the eight frozen W1 future writes;
- candidate refinements: A1 native mode, A2 discrete route state, A3 projected structural effect.

This audit is retrospective because the necessity criterion was formulated after W1 completed.

### OACR-R1 / Wikidata-derived registered graph

Source artifact:

- workflow run: 36378905855
- artifact: `oacr-r1-v1`
- result SHA256: `e6aedbc7772e6b097c0ebc773dd628aea9285f146148bfad609f7aca776203af`
- raw carrier SHA256: `3d3852ff72382c171e3a5496336767809b9455541fa2604f7b6857a8e69457df`

Registered first-pass audit:

- horizon: one explicit edge deletion;
- observation: complete registered transitive closure;
- actions: each witness's frozen shared deletion;
- candidate refinements: A1 support multiplicity, A2 explicit support, A3 minimal support provenance.

This audit is also retrospective. R1 was intentionally constructed as a positive control, so it cannot establish prevalence or discover a naturally occurring necessity relation.

## 8. Required outputs

For each carrier report:

- number of current-observation collisions;
- number of required operational pair separations;
- under-refinement count for each candidate feature level;
- over-refinement count for each candidate feature level where evaluable;
- first candidate level that separates each required pair;
- pairs for which no candidate level explains the required separation.

## 9. Interpretation discipline

The strongest justified statements are of the form:

> Under registered contract \(\mathcal C\), this pair of states must be separated by any horizon-\(H\) adequate representation.

or:

> Candidate feature map \(F\) is sufficient / over-refined / under-refined on this frozen finite bank.

Do not write:

> Feature X is universally necessary.

unless a separate theorem proves that stronger claim.

## 10. How N1 selects the next carrier

The next carrier is **not** chosen to fill a theory category such as causal, temporal, provenance, or normative.

Instead, N1 asks which unresolved adequacy question remains after W1 and R1. A new carrier is selected only if its native operations can discriminate among competing explanations of that unresolved question.

Nearest theories may supply formal tools for that discrimination, but they do not determine the carrier semantics.
