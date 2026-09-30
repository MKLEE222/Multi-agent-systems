# OACR Theory Gate — Minimal Multi-Delta Interaction Counterexample

Date: 2026-09-30

Status: **COUNTEREXAMPLE ACCEPTED AT WORKING-THEORY LEVEL**

## 1. Purpose

The one-delta DAG exactness theorem proves that componentwise contract activity is sufficient when every augmented state contains at most one currently redundant delta.

This note shows that the result does **not** extend componentwise once states may contain multiple redundant deltas.

The counterexample is intentionally minimal and uses the same native semantics:

- DAG carrier;
- singleton base-edge deletion;
- full post-action transitive closure.

Thus the failure comes from **delta interaction**, not from changing the native executor or observation rule.

---

## 2. Base graph

Let the base DAG be the four-node chain

\[
a\to b\to c\to d.
\]

Let

\[
e_1=(a,c),
\qquad
e_2=(a,d).
\]

Both are redundant in the current base graph:

\[
e_1,e_2\in TC(G)\setminus E(G).
\]

Use the singleton deletion contract

\[
A=\{f\},
\qquad
f=(b,c).
\]

After deleting \(f\), the base graph is

\[
a\to b
\qquad
c\to d.
\]

Hence both \(e_1\) and \(e_2\) are individually contract-active:

\[
(a,c)\notin TC(G-f),
\]

\[
(a,d)\notin TC(G-f).
\]

A purely componentwise activity rule therefore marks both deltas as necessary.

---

## 3. Four registered states

Consider:

\[
x_0=G,
\]

\[
x_1=G+e_1,
\]

\[
x_2=G+e_2,
\]

\[
x_{12}=G+\{e_1,e_2\}.
\]

Under the sole registered action \(f=(b,c)\):

### Base

\[
TC(x_0-f)
=
\{a\to b,\;c\to d\}.
\]

### State \(x_1\)

Adding \(e_1=(a,c)\) restores

\[
a\to c
\]

and therefore also

\[
a\to d
\]

through \(c\to d\).

Thus

\[
TC(x_1-f)
=
\{a\to b,\;a\to c,\;a\to d,\;c\to d\}.
\]

### State \(x_2\)

Adding only \(e_2=(a,d)\) gives

\[
TC(x_2-f)
=
\{a\to b,\;a\to d,\;c\to d\}.
\]

### State \(x_{12}\)

Once \(e_1\) is present, \(e_2\) becomes redundant because

\[
a\to c\to d.
\]

Therefore

\[
TC(x_{12}-f)
=
TC(x_1-f).
\]

---

## 4. Operational quotient

The native operational partition is

\[
O_A
=
\{
\{x_0\},
\{x_2\},
\{x_1,x_{12}\}
\}.
\]

Thus

\[
|O_A|=3.
\]

But a componentwise representation that retains the identity of every individually active delta produces four blocks:

\[
\{x_0\},
\{x_1\},
\{x_2\},
\{x_{12}\}.
\]

It therefore over-refines the true operational quotient.

---

## 5. Result

\[
\boxed{
\text{individual contract activity}
\not\Rightarrow
\text{global exactness}
}
\]

once multiple deltas may coexist in the same state.

More specifically:

\[
e_1\text{ active},
\qquad
e_2\text{ active},
\]

but in the joint state,

\[
e_2
\]

is operationally absorbed by \(e_1\) under the registered action.

Therefore a representation repair rule that independently retains all locally active distinctions is not exact in the presence of interactions.

---

## 6. The theoretical boundary this creates

The positive theorem and this counterexample now form a clean pair.

### Positive regime

For one-delta-per-state DAG carriers:

\[
\text{local activity}
\Longrightarrow
\text{exact operational quotient}.
\]

### Interaction regime

For multi-delta states:

\[
\text{local activity}
\centernot\Longrightarrow
\text{exact operational quotient}.
\]

The missing object is a **set-level contract certificate** that accounts for conditional redundancy among simultaneously retained distinctions.

This is the natural next theory target.

---

## 7. Candidate generalization — conditional activity

For a state carrying delta set \(S\), a delta \(e\in S\) is conditionally active under action \(f\) only if removing \(e\) from that state's retained delta set changes the post-action native closure:

\[
TC((G+S)-f)
\ne
TC((G+(S\setminus\{e\}))-f).
\]

Unlike the one-delta activity test, this notion is context-dependent:

\[
\alpha(e;S,f)
\]

rather than

\[
\alpha(e;f).
\]

The counterexample has

\[
\alpha(e_2;\{e_2\},f)=1
\]

but

\[
\alpha(e_2;\{e_1,e_2\},f)=0.
\]

This demonstrates endogenous interaction among representation distinctions.

---

## 8. Scientific consequence

This counterexample prevents an overclaim that the R3/R4 local gate is a universal representation-repair principle.

Instead, the theoretical message becomes sharper:

> OACR identifies a tractable separable regime in which contract-visible local activity is exactly sufficient, and an interaction regime in which exact repair requires context-sensitive set-level reasoning.

This is preferable to claiming universal exactness because it yields both:
- a theorem-backed positive class;
- a minimal constructive boundary.

