# OACR Theory Gate — Multi-Delta Native Contract as a Product Closure System

Date: 2026-09-30

Status: **CORE GENERALIZATION CANDIDATE — prior-art and proof audit required before manuscript promotion**

This note generalizes the one-delta exactness theorem without pretending that the componentwise gate remains exact.

The key object is not “higher-order interaction” in the abstract. Under the DAG deletion carrier, every registered native action induces a finite closure operator. A continuation contract therefore induces a vector of closure systems, and operational equivalence is equality of those action-indexed closures.

This gives a clean bridge from the exact one-delta regime to the multi-delta interaction regime.

---

## 1. Setup

Let:

- \(G=(V,E)\) be a DAG;
- \(U=TC(G)\) be the full base reachability relation;
- \(D\subseteq U\setminus E\) be a registered universe of currently redundant candidate deltas;
- a state be indexed by a delta set
  \[
  S\subseteq D;
  \]
- the native state be
  \[
  x_S=G+S;
  \]
- \(A\subseteq E\) be a registered singleton-deletion contract.

Because every candidate delta lies in \(TC(G)\), adding any subset \(S\subseteq D\) cannot create reachability outside \(U\).

---

## 2. Action-indexed closure operator

For each registered deletion action \(f\in A\), define

\[
\operatorname{cl}_f(T)
=
TC\bigl((G-f)\cup T\bigr)
\]

for any \(T\subseteq U\).

Since \(U=TC(G)\) is itself transitive and contains both \(G-f\) and \(T\), we have

\[
\operatorname{cl}_f(T)\subseteq U.
\]

### Proposition 1

For every \(f\in A\), \(\operatorname{cl}_f\) is a closure operator on \(U\):

1. **extensive**
   \[
   T\subseteq \operatorname{cl}_f(T);
   \]

2. **monotone**
   \[
   T\subseteq T'
   \implies
   \operatorname{cl}_f(T)
   \subseteq
   \operatorname{cl}_f(T');
   \]

3. **idempotent**
   \[
   \operatorname{cl}_f(
   \operatorname{cl}_f(T)
   )
   =
   \operatorname{cl}_f(T).
   \]

The proof follows directly from ordinary transitive-closure properties.

The mathematical notion of a finite closure operator is classical. OACR does not claim it.

---

## 3. Contract closure vector

Define the action-indexed contract closure vector

\[
\mathbf{Cl}_A(S)
=
\left(
\operatorname{cl}_f(S)
\right)_{f\in A}.
\]

Because the native outcome under action \(f\) is precisely

\[
B_f(x_S)
=
TC((G+S)-f)
=
\operatorname{cl}_f(S),
\]

we obtain:

### Theorem 1 — exact multi-delta operational characterization

For any two registered multi-delta states \(x_S,x_T\),

\[
\boxed{
x_S\sim_A x_T
\iff
\mathbf{Cl}_A(S)
=
\mathbf{Cl}_A(T)
}.
\]

Thus the operational quotient is exactly the kernel quotient of the contract closure vector.

This result is definitionally close to the native semantics, but it gives the correct mathematical object for the interaction regime: a product of action-indexed finite closure systems.

---

## 4. Conditional redundancy

For a context \(S\subseteq D\) and candidate delta \(e\in D\), define:

\[
e\text{ is contract-redundant given }S
\]

when

\[
\mathbf{Cl}_A(S\cup\{e\})
=
\mathbf{Cl}_A(S).
\]

Equivalently, for every action \(f\in A\),

\[
e\in \operatorname{cl}_f(S).
\]

This is **context-dependent redundancy**.

Write:

\[
e\preceq_A S
\]

for this implication relation.

The one-delta activity test asks only whether:

\[
e\preceq_A \varnothing.
\]

The multi-delta problem asks whether:

\[
e\preceq_A S
\]

for nonempty \(S\).

This is the precise point at which independent local activity stops being sufficient.

---

## 5. The four-node counterexample revisited

For:

\[
G:
a\to b\to c\to d,
\]

with:

\[
e_1=(a,c),
\qquad
e_2=(a,d),
\]

and deletion:

\[
f=(b,c),
\]

both deltas are active relative to the empty context:

\[
e_1\not\preceq_A\varnothing,
\qquad
e_2\not\preceq_A\varnothing.
\]

But:

\[
e_2\preceq_A\{e_1\}.
\]

Therefore:

\[
\mathbf{Cl}_A(\{e_1,e_2\})
=
\mathbf{Cl}_A(\{e_1\}).
\]

This is not merely a vague interaction effect.

It is a concrete **contract implication**:

\[
\boxed{
e_1\Rightarrow_A e_2
}
\]

under the registered future operation.

The full identity representation therefore over-refines the operational quotient.

---

## 6. Contract generators

For a registered state \(S\subseteq D\), call \(K\subseteq S\) a **contract generator** of \(S\) when

\[
\mathbf{Cl}_A(K)
=
\mathbf{Cl}_A(S).
\]

It is inclusion-minimal when no proper subset of \(K\) has the same contract closure vector.

It is cardinality-minimum when no smaller subset of \(S\) has the same vector.

### Interpretation

A contract generator is a subset of stored distinctions sufficient to reproduce the state's entire registered future native behavior.

This is a natural multi-delta analogue of the one-delta contract gate.

However, unlike the one-delta regime:

- minimal generators need not be unique;
- local activity need not identify a minimum generator;
- the globally minimum generator problem can be combinatorial.

This is exactly where classical finite closure-system and implicational-basis theory becomes relevant.

---

## 7. Prior-art boundary: closure systems and implicational bases

Finite closure systems have a long theory of:

- implicational bases;
- canonical bases;
- minimal generators;
- minimum and optimum bases;
- Horn representations.

This literature includes canonical representations and hardness results for some optimization notions.

Therefore OACR must not claim novelty for:
- the existence of closure operators;
- implicational bases;
- minimal generators in closure systems;
- generic hardness of minimum closure bases.

The OACR-specific object is instead the mapping:

\[
\boxed{
\text{native continuation contract}
\longrightarrow
\text{action-indexed closure family}
\longrightarrow
\text{persistent representation quotient}
}
\]

together with:
- two-sided adequacy;
- non-anticipating constructor authority;
- bidirectional repair from coarse and fine endpoints;
- native replay as final validation.

---

## 8. Two distinct interaction phenomena

The closure view separates two mechanisms that should not be conflated.

### A. Absorption / conditional redundancy

Distinct stored sets produce the same native behavior:

\[
S\ne T
\]

but

\[
\mathbf{Cl}_A(S)
=
\mathbf{Cl}_A(T).
\]

This creates over-refinement if the representation stores raw delta identity.

The four-node counterexample is of this type.

### B. Synergistic reachability

A group of deltas can create a native effect that is not produced by any member alone.

For action \(f\), define the singleton-effect union

\[
M_f(S)
=
\bigcup_{e\in S}
\operatorname{cl}_f(\{e\}).
\]

A genuine synergy occurs when

\[
\operatorname{cl}_f(S)
\supsetneq
M_f(S).
\]

This requires chains of added deltas to create additional reachability.

The one-delta theorem excludes both mechanisms by construction because registered states contain at most one delta.

A full multi-delta repair theory must handle both.

---

## 9. Separable regime

A registered multi-delta state family is **contract-separable** when, on that family:

1. no higher-order synergy changes the relevant closure vector beyond singleton effects;
2. the resulting union of singleton action signatures uniquely determines the operational class.

Under these conditions, a componentwise certificate can remain exact.

The one-delta DAG class is a strict special case in which separability is automatic.

This definition is currently a theory scaffold; the weakest useful necessary-and-sufficient formulation remains to be derived.

---

## 10. Native repair interpretation

The multi-delta theory now yields a hierarchy.

### One-delta separable class

\[
\text{activity union}
\to
\text{unique exact gate}
\to
\text{minimal bidirectional update}.
\]

### Multi-delta closure class

\[
\text{contract closure vector}
\to
\text{equivalence classes of delta sets}
\to
\text{contract generators}.
\]

The difficult object is no longer “which individual feature matters?”

It is:

\[
\boxed{
\text{which set of persistent distinctions generates the required contract closure?}
}
\]

That is the natural set-level extension of OACR.

---

## 11. Non-anticipation boundary

There are two different ways to use this theory.

### Oracle / evaluation replay

Directly compute every augmented state's full closure vector and encode it.

This proves representability but is weak evidence.

### Contract-derived constructor

Derive a frozen implication/certificate rule from:
- native semantics;
- base structure;
- registered action contract;
- authorized development information;

then apply it to evaluation states without adapting the rule to their realized evaluation labels.

The second is the OACR target.

The closure-system formalism does not remove the need for the provenance boundary; it makes explicit what an outcome-fitted constructor would be encoding.

---

## 12. Theory program enabled by this object

The next questions are now precise:

1. **Exact separability condition**  
   Characterize when the contract closure vector of a multi-delta state is determined compositionally by singleton certificates.

2. **Generator uniqueness**  
   Characterize when each operational class has a unique minimum contract generator.

3. **Interaction order**  
   Define the minimum premise size of a nontrivial contract implication:
   \[
   Q\Rightarrow_A e.
   \]
   One-delta local reasoning corresponds to order 1.

4. **Tractable subclasses**  
   Identify graph/contract structures for which the implication system has bounded premise size or another efficient basis.

5. **Bidirectional repair with interactions**  
   Starting from a coarse state representation, add a generator; starting from full delta identity, remove contract-implied distinctions. Determine when both procedures converge to partition-equivalent representations.

6. **Authority-aware learning**  
   For learned carriers, estimate a contract implication rule on development data, freeze it, and test whether it predicts held-out future equivalence without evaluation feedback.

These questions connect the structural theorem directly to the later anti-circularity and natural learned-system work.

---

## 13. Current theoretical spine

The theory now has a positive regime, a boundary, and a generalization:

\[
\boxed{
\begin{array}{c}
\text{one-delta DAG}\\
\Downarrow\\
\text{exact activation coverage}\\
\Downarrow\\
\text{unique minimal bidirectional repair}
\end{array}
}
\]

versus

\[
\boxed{
\begin{array}{c}
\text{multi-delta state}\\
\Downarrow\\
\text{contract implications / absorption / synergy}\\
\Downarrow\\
\text{product closure quotient and generator problem}
\end{array}
}
\]

This is a stronger theory story than attempting to present the R4 gate as a universal local rule.
