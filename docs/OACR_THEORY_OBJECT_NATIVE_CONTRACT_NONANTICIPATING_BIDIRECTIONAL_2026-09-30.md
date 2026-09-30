# OACR Core Theory Object — Native-Contract, Non-Anticipating, Bidirectional Representation Repair

Date: 2026-09-30

Status: **CORE THEORY WORKING SPECIFICATION — not yet manuscript-authoritative**

This note sharpens the theoretical object that should distinguish OACR from Abstract Interpretation Repair, CEGAR, program repair, and ordinary representation minimization.

The target is not "more theorems." The target is a coherent object in which:

1. the required semantics are induced by a **native continuation contract**;
2. the repair constructor is **non-anticipating** with respect to the held-out native outcome partition;
3. both **under-refinement and over-refinement** are representation errors;
4. repair may therefore proceed from either a coarse or unnecessarily fine endpoint;
5. exact closure is accepted only after independent native replay.

---

## 1. Native-contract semantics

Let \(X\) be a finite registered state bank and let \(\mathcal N\) be a fixed native interpreter or executor.

A finite continuation contract is

\[
\mathcal C=(\mathcal O,\mathcal A,H,\Sigma),
\]

where:

- \(\mathcal O\) specifies registered present observations;
- \(\mathcal A\) is the registered native operation alphabet;
- \(H\) is the registered continuation horizon;
- \(\Sigma\) specifies the native outcome coordinates to compare.

The fixed native interpreter and contract induce a complete registered behavior map

\[
B_{\mathcal N,\mathcal C}:X\to\mathcal B_{\mathcal C}.
\]

Define the contract-relative operational equivalence

\[
x\sim_{\mathcal C} y
\iff
B_{\mathcal N,\mathcal C}(x)=B_{\mathcal N,\mathcal C}(y),
\]

and the operational quotient

\[
O_{\mathcal C}=X/{\sim_{\mathcal C}}.
\]

The quotient is not asserted to be universal system identity. It is the distinction structure required by the declared future-use contract on the registered bank.

---

## 2. Representation adequacy is a two-sided problem

Let an implemented representation

\[
R:X\to\mathcal R
\]

induce partition \(P_R\).

Using the manuscript convention,

\[
P\preceq Q
\]

means that \(P\) is coarser than or equal to \(Q\).

There are three qualitatively different cases.

### Under-refinement

\[
P_R\prec O_{\mathcal C}.
\]

The representation merges states whose registered native continuation differs.

### Over-refinement

\[
O_{\mathcal C}\prec P_R.
\]

The representation preserves distinctions that the registered contract does not use.

### Exact adequacy

\[
P_R=O_{\mathcal C}.
\]

Thus representation repair is not intrinsically a refinement problem. The target lies at a contract-relative point in the partition lattice.

---

## 3. Why bidirectionality is structural, not rhetorical

Suppose two available endpoint representations satisfy

\[
P_{\rm coarse}\preceq O_{\mathcal C}\preceq P_{\rm fine}.
\]

A contract-relative repair family may contain:

\[
\Phi^+:
P_{\rm coarse}\mapsto P'
\]

that introduces distinctions, and

\[
\Phi^-:
P_{\rm fine}\mapsto P''
\]

that removes distinctions.

The strongest form of bidirectional exact repair is:

\[
P'
=
P''
=
O_{\mathcal C}.
\]

This motivates the following object.

### Definition 1 — bidirectionally realizable quotient

An operational quotient \(O_{\mathcal C}\) is **bidirectionally realizable** within admissible repair families
\(\mathfrak F^+\) and \(\mathfrak F^-\) if there exist allowed repairs

\[
\Phi^+\in\mathfrak F^+,\qquad
\Phi^-\in\mathfrak F^-,
\]

such that

\[
P_{\Phi^+(R_{\rm coarse})}
=
P_{\Phi^-(R_{\rm fine})}
=
O_{\mathcal C}.
\]

This is stronger than the existence of an adequate representation somewhere in the lattice: the target must be reachable from both endpoint errors under the declared repair language.

---

## 4. Oracle repair is mathematically trivial

If a repair constructor is allowed to inspect \(O_{\mathcal C}\) directly, exact partition repair is not a meaningful scientific accomplishment.

Under the above partition order,

\[
P_{\rm coarse}\vee O_{\mathcal C}=O_{\mathcal C}
\]

and

\[
P_{\rm fine}\wedge O_{\mathcal C}=O_{\mathcal C},
\]

where \(\vee\) is common refinement and \(\wedge\) is common coarsening.

### Proposition 1 — quotient-visible bidirectional repair

For any

\[
P_{\rm coarse}\preceq O\preceq P_{\rm fine},
\]

if \(O\) is directly available to the constructor, exact correction from both endpoints exists trivially by joining the coarse endpoint with \(O\) and meeting the fine endpoint with \(O\).

This proposition is elementary. Its purpose is methodological: it shows that **exact closure by itself has almost no evidential value if the constructor has access to the target partition**.

Therefore OACR requires an information-authority constraint.

---

## 5. Information authority

Let

\[
Y_{\mathcal C}^{\rm verify}
\]

denote the held-out native outcome matrix whose equality classes determine \(O_{\mathcal C}\).

Let

\[
\mathcal I_{\rm construct}
\]

be the information that the repair constructor is explicitly authorized to inspect.

The authority boundary must distinguish:

### Contract-visible information

Examples:
- native operation names and parameters;
- base carrier structure;
- static dependency information;
- candidate representation coordinates;
- registered horizon and outcome schema;
- developmental diagnostics explicitly authorized by protocol.

### Verification-only information

Examples:
- held-out state-action outcome signatures;
- the final operational partition;
- labels derived from held-out outcomes that identify which features will succeed;
- post-hoc pair-specific action choices made because they expose a known mismatch.

---

## 6. Non-anticipating repair

### Definition 2 — non-anticipating constructor

A repair constructor is non-anticipating relative to an authority specification
\(\mathcal A_{\rm info}\) when

\[
\kappa
=
g(
R,
\mathcal C,
\mathcal I_{\rm construct}
)
\]

and \(g\) is not permitted to inspect

\[
Y_{\mathcal C}^{\rm verify},
\quad
O_{\mathcal C},
\]

or any derived object whose information content reveals the held-out target partition beyond what the authority specification explicitly permits.

The repaired representation is

\[
R'=\Phi(R,\kappa).
\]

Acceptance then requires independent native replay:

\[
B_{\mathcal N,\mathcal C}(R')
\]

against the frozen verification contract.

### Definition 3 — non-anticipating exact repair

A repair is a **non-anticipating exact repair** when:

1. its constructor satisfies Definition 2;
2. the native interpreter \(\mathcal N\) and contract \(\mathcal C\) remain fixed;
3. held-out replay establishes
   \[
   P_{R'}=O_{\mathcal C}.
   \]

This is the core OACR scientific object.

---

## 7. Why this differs from ordinary optimal representation selection

If the complete target quotient is supplied as part of the optimization input, choosing a small representation that separates its classes is a classical discernibility / test-set / reduct problem.

That literature is relevant, but it does not capture the main OACR identification condition.

OACR separates two questions:

### Ex post representability

Given \(O_{\mathcal C}\), can some admissible representation realize it?

### Ex ante contract-predictive repair

Given only the declared contract and authorized carrier structure, can a constructor predict which distinctions will be required, before the held-out native outcomes are revealed?

The second problem is strictly more appropriate to the empirical claim "the contract determines a repair principle."

A constructor that reads \(O_{\mathcal C}\) can always be evaluated as an encoding algorithm; it cannot by itself demonstrate contract-predictive representation design.

---

## 8. Native-contract repair as a prediction problem

Let a repair protocol expose:

\[
Z=(R,\mathcal C,\mathcal I_{\rm construct})
\]

before verification outcomes are revealed.

The hidden target is:

\[
T=O_{\mathcal C}.
\]

The constructor predicts a representation:

\[
\widehat R = g(Z).
\]

The native executor then reveals whether:

\[
P_{\widehat R}=T.
\]

This makes exact repair conceptually analogous to a structured prediction problem under a hard information constraint, except that the prediction target is an equivalence relation induced by future native operations rather than an externally labeled class.

The important distinction is:

\[
\text{construction success}
\neq
\text{post-hoc quotient encoding}.
\]

This viewpoint should become the theoretical foundation of the anti-circularity contribution.

---

## 9. A three-level notion of repair strength

The manuscript should distinguish three levels.

### Level 0 — oracle realizability

The constructor can inspect \(O_{\mathcal C}\).

Claim:
- only that the admissible representation family can encode the target.

Scientific strength:
- weak.

### Level 1 — diagnostic repair

The constructor may use audit witnesses or a designated development subset, but not the held-out verification outcomes.

Claim:
- a deficit identified on permitted evidence supports a repair that generalizes to the frozen verification contract.

Scientific strength:
- intermediate.

### Level 2 — contract-predictive repair

The constructor uses only contract-visible structure and carrier-native static information; the target held-out outcomes are fully withheld.

Claim:
- the repair principle predicts the required distinctions from the structure of future use.

Scientific strength:
- strongest.

R4 is a candidate Level-2 result:
- constructor-visible: base graph, registered deletions, candidate delta endpoint;
- forbidden: augmented-state outcome matrix and final quotient;
- acceptance: 17,408 held-out native cells.

SQEC must be classified separately according to exactly which information was used to define the relevant guard and sham control.

---

## 10. Theory target: non-anticipating bidirectional exactness

The highest-value theorem family would have the following shape.

### Target Theorem A — structural exactness

For a carrier class satisfying structural conditions \(S\), there exists a non-anticipating constructor

\[
g_S
\]

such that, for every registered instance in that class,

\[
P_{g_S(R_{\rm coarse})}
=
O_{\mathcal C}.
\]

The private-deletion-witness theorem currently under audit is a candidate instance.

### Target Theorem B — bidirectional convergence

Under additional admissibility conditions on the coarse and fine repair languages,

\[
P_{\Phi^+_{g_S}(R_{\rm coarse})}
=
P_{\Phi^-_{g_S}(R_{\rm fine})}
=
O_{\mathcal C}.
\]

This would elevate R4 from a symmetric empirical intervention to an instance of a genuine common-target theorem.

### Target Theorem C — failure of local repair under interaction

Construct a family in which every candidate distinction is locally inert or locally insufficient, yet combinations of distinctions affect the registered continuation.

Then no per-feature activity rule can guarantee exactness.

This counterexample theorem would define the boundary of the tractable graph result and prevent overgeneralization.

---

## 11. Comparison with Abstract Interpretation Repair

AIR asks how to refine an abstract domain to restore local completeness of a chosen abstract computation and proves conditions for optimal locally complete refinement.

OACR should not compete by theorem count.

The independent theoretical object is:

### AIR
- object: abstract domain;
- defect: local incompleteness / false alarms;
- direction: refinement of insufficient abstraction;
- target semantics: abstract computation/completeness condition;
- constructor may reason from the failed abstract computation;
- principal result: optimal locally complete refinement under stated conditions.

### OACR
- object: implemented persistent representation;
- defect: either under- or over-refinement relative to future native use;
- direction: refinement **or** coarsening;
- target semantics: quotient induced by a finite native continuation contract;
- constructor is governed by an explicit information-authority boundary;
- principal target: non-anticipating bidirectional exact repair or a certified boundary on when it is possible.

The strongest novelty claim should therefore be about the **joint object**:

\[
\boxed{
\text{native-contract semantics}
+
\text{two-sided adequacy}
+
\text{non-anticipating construction}
+
\text{bidirectional exactness}
}
\]

not any one component in isolation.

---

## 12. Comparison with CEGAR and program repair

### CEGAR

CEGAR starts from an abstraction, obtains a spurious counterexample, and refines the abstraction.

OACR differs in three ways:
1. over-refinement is also an error;
2. the target is induced by a registered family of native future operations, not only property verification;
3. the authority boundary explicitly controls how much of the outcome evidence the constructor may inspect.

### Program repair / Verifix

Program repair generally assumes a correctness target and modifies executable code until the target is satisfied.

OACR instead treats the **representation target itself** as contract-relative:

\[
\mathcal C
\mapsto
O_{\mathcal C},
\]

and asks which persistent distinctions must be retained or removed without changing the native executor.

---

## 13. Core acceptance tests for this theory object

Before manuscript promotion, all of the following must pass.

### Novelty
- [ ] No existing line already defines the same joint native-contract + two-sided + non-anticipating + bidirectional object.
- [ ] AIR comparison survives direct source-level reading.
- [ ] CEGAR / abstraction repair / state minimization / test-set literatures are explicitly separated.

### Formal correctness
- [ ] Partition order and join/meet notation are proof-checked.
- [ ] Information-authority definitions do not smuggle statistical independence claims into access-control semantics.
- [ ] "Non-anticipating" does not conflict with a well-established incompatible term in the closest literature.
- [ ] Bidirectional realizability is separated from uniqueness/minimality.

### Constructive content
- [ ] At least one nontrivial carrier class admits a proof of non-anticipating exactness.
- [ ] At least one counterexample class shows why local repair can fail.
- [ ] At least one natural carrier tests the theory outside the exact structural family.

---

## 14. Current best paper-level thesis

A candidate final thesis is:

> A persistent representation should not be judged by present recoverability or full internal identity, but by the distinctions required for its registered native continuation. Because this target can lie strictly between coarse observation and full identity, representation error is inherently two-sided. Exact repair is scientifically informative only when the required distinctions are constructed without access to the held-out outcome quotient. OACR therefore studies non-anticipating bidirectional repair: predicting, from a declared continuation contract and authorized carrier structure, the representation that independent native replay later confirms as operationally exact.

This paragraph is the current standard against which further theory and experiments should be judged.
