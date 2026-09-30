# OACR Theory Gate — Contract Lattice, Coverage Structure, and Minimal Incremental Repair

Date: 2026-09-30

Status: **CANDIDATE THEOREM FAMILY — proof audit required before manuscript promotion**

This note derives consequences of the One-Delta DAG Contract Exactness theorem. The aim is to turn the phrase “action content matters more than action count” and the bidirectional repair observation into a formal contract-evolution theory.

The mathematical ingredients—coverage functions, submodularity, set cover, and Hamming edit distance—are classical. The candidate OACR contribution is the fact that, for the accepted native carrier class, the operational quotient and the exact persistent representation reduce *exactly* to this structure.

---

## 1. Setup

Use the one-delta DAG carrier:

- base DAG \(G=(V,E)\);
- redundant candidate deltas
  \[
  D\subseteq TC(G)\setminus E;
  \]
- registered states
  \[
  X=\{x_0\}\cup\{x_e:e\in D\};
  \]
- singleton deletion actions \(f\in E\);
- native outcome
  \[
  B_f(x)=TC(x-f).
  \]

For every deletion action \(f\), define its **activation set**

\[
W_f
=
\left\{
e=(u_e,v_e)\in D:
(u_e,v_e)\notin TC(G-f)
\right\}.
\]

Thus \(W_f\) is the set of currently redundant deltas that become operationally necessary under action \(f\).

For any finite contract \(A\subseteq E\), define

\[
D^+(A)
=
\left\{
e\in D:
\exists f\in A,\; e\in W_f
\right\}.
\]

Immediately,

\[
\boxed{
D^+(A)=\bigcup_{f\in A}W_f
}.
\]

---

## 2. Theorem — contract quotient is a coverage object

By the One-Delta DAG Contract Exactness theorem,

\[
O_A
=
\left\{
\{x_0\}\cup\{x_e:e\notin D^+(A)\}
\right\}
\cup
\left\{
\{x_e\}:e\in D^+(A)
\right\}.
\]

Hence

\[
\boxed{
|O_A|
=
1+
\left|
\bigcup_{f\in A}W_f
\right|
}.
\]

### Interpretation

The registered contract does not demand distinctions according to the **number** of actions. It demands distinctions according to the **union of the delta sets activated by their content**.

Two action panels with the same cardinality can therefore induce very different operational quotients.

Two different contracts \(A\) and \(B\) induce the same operational partition iff

\[
D^+(A)=D^+(B).
\]

Thus contract equivalence in this carrier is exactly activation-union equivalence.

---

## 3. Corollary — monotonicity under contract inclusion

If

\[
A\subseteq B,
\]

then

\[
D^+(A)\subseteq D^+(B).
\]

Therefore

\[
O_A\preceq O_B.
\]

Adding registered future actions can only refine the required operational distinction structure; removing actions can only coarsen it.

This is the native-carrier realization of contract monotonicity.

---

## 4. Corollary — operational block count is submodular

Define

\[
b(A)=|O_A|-1
=
\left|\bigcup_{f\in A}W_f\right|.
\]

Then \(b\) is a classical monotone coverage function and therefore submodular.

For

\[
A\subseteq B
\]

and \(g\notin B\),

\[
b(A\cup\{g\})-b(A)
=
\left|
W_g
\setminus
\bigcup_{f\in A}W_f
\right|,
\]

while

\[
b(B\cup\{g\})-b(B)
=
\left|
W_g
\setminus
\bigcup_{f\in B}W_f
\right|.
\]

Since

\[
\bigcup_{f\in A}W_f
\subseteq
\bigcup_{f\in B}W_f,
\]

we obtain diminishing returns:

\[
\boxed{
b(A\cup\{g\})-b(A)
\ge
b(B\cup\{g\})-b(B)
}.
\]

### Scientific interpretation

This formalizes the empirical observation that action **content** matters more than action count.

A single action can expose most of the contract-relevant distinctions, while many additional actions contribute nothing if their activation sets are already covered.

---

## 5. Exact representation family

Define the identity-gated representation family

\[
\mathfrak R_D
=
\{R_S:S\subseteq D\},
\]

where

\[
R_S(x_0)=\bot
\]

and

\[
R_S(x_e)=
\begin{cases}
e,&e\in S,\\
\bot,&e\notin S.
\end{cases}
\]

Thus \(S\) is exactly the subset of candidate delta identities retained by the persistent representation.

### Theorem — unique exact member

For a fixed contract \(A\),

\[
\boxed{
P_{R_S}=O_A
\iff
S=D^+(A)
}.
\]

### Proof

If an active delta

\[
e\in D^+(A)
\]

is omitted from \(S\), \(R_S\) merges \(x_e\) with the base class although the exactness theorem says \(x_e\) is a singleton operational class. The representation under-refines.

If an inactive delta

\[
e\notin D^+(A)
\]

is included in \(S\), \(R_S\) separates \(x_e\) from the base even though they are operationally equivalent. The representation over-refines.

Therefore exactness requires precisely

\[
S=D^+(A).
\]

Conversely, the contract gate with that set is exact by the earlier theorem. \(\square\)

### Consequence

Within the declared identity-gated repair language, the exact repaired representation is not merely sufficient; it is **unique**.

Across arbitrary encodings, uniqueness should only be claimed up to partition equivalence.

---

## 6. Minimal incremental repair under contract change

Define representation edit cost inside \(\mathfrak R_D\) by Hamming distance over retained delta records:

\[
c(R_S,R_T)
=
|S\triangle T|.
\]

Let \(A\) and \(B\) be two contracts.

Their unique exact representations are

\[
R^\star_A=R_{D^+(A)},
\qquad
R^\star_B=R_{D^+(B)}.
\]

Any exact update from the first contract to the second must end at \(R^\star_B\).

Therefore the minimum possible number of retained-delta record changes is

\[
\boxed{
c_{\min}(A\to B)
=
|D^+(A)\triangle D^+(B)|
}.
\]

The direct gate update attains this lower bound by:

- adding identities in
  \[
  D^+(B)\setminus D^+(A);
  \]
- removing identities in
  \[
  D^+(A)\setminus D^+(B).
  \]

Thus the contract-derived update is **edit-minimal within the declared representation family**.

### Nested expansion

If

\[
A\subseteq B,
\]

then

\[
D^+(A)\subseteq D^+(B),
\]

so

\[
c_{\min}(A\to B)
=
|D^+(B)\setminus D^+(A)|.
\]

Only newly demanded distinctions must be added.

### Nested contraction

For \(B\subseteq A\),

\[
c_{\min}(A\to B)
=
|D^+(A)\setminus D^+(B)|.
\]

Only distinctions no longer demanded by any remaining action must be removed.

---

## 7. Path independence / confluence under contract evolution

Because

\[
D^+(A)=\bigcup_{f\in A}W_f,
\]

the canonical exact representation for a contract depends only on the final action set \(A\), not on the order in which its actions were added.

For any ordering

\[
f_{\pi(1)},\ldots,f_{\pi(k)}
\]

of the same contract,

\[
D^+(\{f_{\pi(1)},\ldots,f_{\pi(k)}\})
=
\bigcup_{i=1}^k W_{f_{\pi(i)}}.
\]

Therefore incremental exact updates commute at the partition level.

More generally, after arbitrary additions and removals of contract actions, recomputing the active union yields the same exact representation for the same final contract.

### Candidate corollary — contract confluence

Within \(\mathfrak R_D\), exact incremental repair is path-independent:

\[
\boxed{
A_{\rm final}\text{ equal}
\Longrightarrow
R^\star_{\rm final}\text{ equal}
}
\]

regardless of the sequence of contract expansions and contractions, provided each update uses the frozen activation rule.

This gives a concrete form of bidirectional confluence.

---

## 8. Contract basis

For a full registered contract \(A\), call \(A'\subseteq A\) a **contract basis** when

\[
O_{A'}=O_A.
\]

In this carrier,

\[
A'\text{ is a contract basis}
\iff
\bigcup_{f\in A'}W_f
=
\bigcup_{f\in A}W_f.
\]

Thus, after the activation matrix is constructed, minimum-cardinality contract-basis selection is exactly a set-cover problem over the universe

\[
D^+(A)
\]

with action sets

\[
\{W_f:f\in A\}.
\]

This should be positioned as a classical optimization connection, not as a new set-cover theorem.

It supplies a precise language for empirical observations such as:

- many actions may be operationally redundant;
- a small subset can induce the same full quotient;
- action count alone is a poor proxy for future distinction demand.

---

## 9. Closed-form directional information gaps

Let

\[
n=|X|=|D|+1
\]

and

\[
m(A)=|D^+(A)|.
\]

The operational partition has:

- \(m(A)\) singleton active classes;
- one inactive/base class of size
  \[
  n-m(A).
  \]

Under the uniform state distribution:

### Coarse endpoint

For the constant current representation,

\[
E=0
\]

and

\[
U
=
H(O_A)
=
\log_2 n
-
\frac{n-m(A)}{n}
\log_2(n-m(A)).
\]

### Full endpoint

For the full identity representation,

\[
U=0
\]

and

\[
E
=
\frac{n-m(A)}{n}
\log_2(n-m(A)).
\]

Hence

\[
\boxed{
U_{\rm coarse}(A)+E_{\rm full}(A)=\log_2 n
}.
\]

The identity is a direct entropy-chain consequence and is not itself a novelty claim.

The useful carrier-specific consequence is that **all directional-gap values are completely determined by contract coverage \(m(A)\)**.

As the contract expands and activates more deltas:

\[
U_{\rm coarse}(A)
\]

increases, while

\[
E_{\rm full}(A)
\]

decreases.

The exact gate remains at

\[
U=E=0.
\]

This supplies a closed-form theoretical explanation of the accepted R3/R4 directional-gap pattern.

---

## 10. R3/R4 interpretation

### R3

With \(n=272\) and 100 active augmented states, the theorem predicts:

- 100 singleton active classes;
- one 172-state inactive/base class;
- total
  \[
  101
  \]
  operational classes.

This is exactly the accepted R3 partition structure.

### R4

With \(n=272\) and 22 active augmented states, the theorem predicts:

- 22 singleton active classes;
- one 250-state inactive/base class;
- total
  \[
  23
  \]
  operational classes.

This is exactly the accepted R4 partition structure.

Thus the accepted empirical partitions are instances of one common theorem rather than unrelated carrier measurements.

---

## 11. What this theorem family adds

The theory now has four linked layers:

### Layer 1 — exact quotient

\[
D^+(A)
\Longrightarrow
O_A.
\]

### Layer 2 — action-content geometry

\[
D^+(A)
=
\bigcup_{f\in A}W_f,
\]

giving monotonicity and submodularity.

### Layer 3 — unique exact representation

\[
R^\star_A
=
R_{D^+(A)}
\]

inside the declared repair language.

### Layer 4 — minimal bidirectional adaptation

\[
c_{\min}(A\to B)
=
|D^+(A)\triangle D^+(B)|
\]

with path-independent exact updates.

This is substantially stronger than merely stating that R4 admits additive and subtractive repair.

---

## 12. Boundary from the multi-delta counterexample

All results above rely on the one-delta-per-state separability regime.

When a state may contain multiple deltas, individual activation sets can become conditionally redundant. The four-node interaction counterexample already shows that:

\[
\text{retain every individually active delta}
\]

can over-refine the operational quotient.

Therefore the coverage theorem is **not** a universal OACR law.

The natural next object is a set-level contract closure that represents conditional implication among retained deltas.

---

## 13. Prior-art boundary

The following mathematics is classical and must be cited rather than claimed:

- coverage functions are monotone submodular;
- minimum set cover;
- finite closure systems and implicational bases;
- transitive closure and transitive reduction.

Relevant closure-system work studies canonical and minimum implicational bases, including the fact that optimum bases can be computationally hard. This literature is directly relevant once multi-delta interactions are represented as implications among candidate distinctions.

The candidate OACR novelty is the **native-contract interpretation and repair consequence**:

> a future-operation contract induces an exact activation geometry over persistent distinctions; in a separable native carrier this yields a canonical exact representation, minimum edit updates under contract change, and bidirectional path independence without observing the augmented-state outcome partition.

---

## 14. Acceptance tasks

- [ ] Proof-check the unique exact-member theorem.
- [ ] Proof-check edit minimality under the declared cost model.
- [ ] Verify the R3/R4 closed-form \(U/E\) values numerically from frozen artifacts.
- [ ] Extract the frozen R4 action activation matrix and verify the coverage formula for every singleton/pair/subcontract already recorded.
- [ ] Check whether the R4 empirical “one action creates most classes” statement exactly matches its activation-set cardinality.
- [ ] Audit submodularity/coverage terminology against standard literature.
- [ ] Do not promote “contract basis is NP-hard” for graph inputs unless graph-realizability of arbitrary set systems is separately proved.
