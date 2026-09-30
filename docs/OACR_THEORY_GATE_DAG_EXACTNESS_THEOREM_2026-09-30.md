# OACR Theory Gate — Exact Contract Quotient for One-Delta DAG Carriers

Date: 2026-09-30

Status: **CANDIDATE THEOREM — substantially stronger than the earlier private-witness condition; proof and prior-art audit required before manuscript promotion**

## 1. Main result

The earlier private-witness sufficient condition is stronger than necessary.

For the R3/R4 one-delta DAG carrier, exactness follows from a more general structural fact:

> under a shared singleton-deletion contract, every contract-active redundant delta is automatically operationally unique when outcomes expose the full post-action transitive closure.

This removes the previous empirical gap between “active relative to base” and “pairwise distinct among active states.”

---

## 2. Setup

Let \(G=(V,E)\) be a DAG.

Let

\[
D\subseteq TC(G)\setminus E
\]

be a registered family of currently redundant candidate edges.

The registered state bank is

\[
X=\{x_0\}\cup\{x_e:e\in D\},
\]

where

\[
x_0=G,
\qquad
x_e=G+e.
\]

Let

\[
A\subseteq E
\]

be a nonempty shared singleton-deletion contract.

For action \(f\in A\), define the native outcome as the full post-action transitive closure

\[
B_f(x)=TC(x-f).
\]

Define the full contract signature

\[
B_A(x)=\bigl(B_f(x)\bigr)_{f\in A}.
\]

Define the contract-active delta set

\[
D^+
=
\left\{
e=(u,v)\in D:
\exists f\in A,\;
(u,v)\notin TC(G-f)
\right\}.
\]

All remaining deltas \(D^-=D\setminus D^+\) are contract-inactive.

---

## 3. Lemma — injectivity of one-edge closure augmentation

### Lemma 1

Let \(H\) be a DAG and let

\[
e=(u,v),\qquad e'=(u',v')
\]

be two distinct edges such that

\[
e\notin TC(H),
\qquad
e'\notin TC(H),
\]

and both additions preserve acyclicity.

Then

\[
TC(H+e)\ne TC(H+e').
\]

### Direct proof

Assume for contradiction that

\[
TC(H+e)=TC(H+e').
\]

Because \(e=(u,v)\) belongs to \(TC(H+e')\) but not to \(TC(H)\), every \(u\leadsto v\) path witnessing that reachability in \(H+e'\) must use the newly added edge \(e'=(u',v')\).

Therefore, in \(H\),

\[
u\leadsto u'
\]

and

\[
v'\leadsto v,
\]

where equality at an endpoint is allowed.

Symmetrically, because \(e'\in TC(H+e)\setminus TC(H)\),

\[
u'\leadsto u
\]

and

\[
v\leadsto v'
\]

in \(H\).

Reachability in a DAG is antisymmetric. Hence

\[
u=u'
\]

and

\[
v=v',
\]

so \(e=e'\), contradicting distinctness.

Therefore

\[
TC(H+e)\ne TC(H+e').
\qquad\square
\]

### Classical boundary

This lemma is closely related to the classical uniqueness of transitive reduction for DAGs. It should not be claimed as an isolated graph-theoretic novelty. Aho, Garey, and Ullman (1972) established the transitive-reduction framework for directed graphs.

Its role in OACR is to close the representation-adequacy theorem below.

---

## 4. Theorem — exact operational quotient

### Theorem 1 — One-Delta DAG Contract Exactness

Under the setup above:

1. every inactive state \(x_e\), \(e\in D^-\), is operationally equivalent to the base state \(x_0\);
2. every active state \(x_e\), \(e\in D^+\), is operationally distinct from the base state;
3. every two distinct active states are operationally distinct;
4. therefore the operational partition is exactly

\[
O_A
=
\left\{
\{x_0\}\cup\{x_e:e\in D^-\}
\right\}
\cup
\left\{
\{x_e\}:e\in D^+
\right\};
\]

5. consequently,

\[
|O_A|=|D^+|+1.
\]

### Proof

#### Inactive states collapse to base

Take \(e=(u,v)\in D^-\).

By definition,

\[
(u,v)\in TC(G-f)
\]

for every \(f\in A\).

Thus \(e\) is still redundant after every registered deletion. Adding it cannot change the post-deletion reachability relation:

\[
TC((G+e)-f)=TC(G-f)
\]

for every \(f\in A\).

Hence

\[
B_A(x_e)=B_A(x_0).
\]

#### Every active state differs from base

Take \(e=(u,v)\in D^+\).

There exists \(f_e\in A\) such that

\[
(u,v)\notin TC(G-f_e).
\]

But \(x_e-f_e\) contains the direct edge \(e\), so

\[
(u,v)\in TC((G+e)-f_e).
\]

Therefore

\[
B_{f_e}(x_e)\ne B_{f_e}(x_0),
\]

and so

\[
B_A(x_e)\ne B_A(x_0).
\]

#### Distinct active states are automatically separated

Take distinct active deltas

\[
e,e'\in D^+.
\]

Choose any witness deletion \(f_e\in A\) for \(e\), and write

\[
H=G-f_e.
\]

We know

\[
e\notin TC(H).
\]

There are two cases.

**Case 1.**

\[
e'\in TC(H).
\]

Then \(e'\) remains redundant after \(f_e\), so

\[
TC(H+e')=TC(H),
\]

while

\[
TC(H+e)\ne TC(H).
\]

Therefore

\[
TC(H+e)\ne TC(H+e').
\]

**Case 2.**

\[
e'\notin TC(H).
\]

Both \(e\) and \(e'\) are nonredundant additions to the same DAG \(H\). By Lemma 1,

\[
TC(H+e)\ne TC(H+e').
\]

Thus in all cases the single action \(f_e\) separates \(x_e\) from \(x_{e'}\).

Therefore every active state is a singleton operational class.

Combining the three claims gives the stated quotient. \(\square\)

---

## 5. Corollary — exact contract-gated representation

Define the contract-gated representation

\[
R_{\rm gate}(x_0)=\bot,
\]

\[
R_{\rm gate}(x_e)=
\begin{cases}
\bot,&e\in D^-\\
e,&e\in D^+.
\end{cases}
\]

Then

\[
P_{R_{\rm gate}}=O_A.
\]

Thus the gate is not merely sound for individual delta necessity. It is exact for the entire registered carrier class.

---

## 6. Corollary — bidirectional exact repair

Define the coarse representation

\[
R_{\rm coarse}(x)=\bot
\]

for every state, and the full-delta representation

\[
R_{\rm full}(x_0)=\bot,
\qquad
R_{\rm full}(x_e)=e.
\]

Then

\[
P_{R_{\rm coarse}}
\preceq
O_A
\preceq
P_{R_{\rm full}}.
\]

The same contract-visible active-set certificate \(D^+\) induces:

### Additive repair

Starting from \(R_{\rm coarse}\), add exactly the identities of active deltas:

\[
R_{\rm coarse}
\xrightarrow{\Phi_A^+}
R_{\rm gate}.
\]

### Subtractive repair

Starting from \(R_{\rm full}\), delete exactly the identities of inactive deltas:

\[
R_{\rm full}
\xrightarrow{\Phi_A^-}
R_{\rm gate}.
\]

Therefore

\[
P_{\Phi_A^+(R_{\rm coarse})}
=
P_{\Phi_A^-(R_{\rm full})}
=
O_A.
\]

This is a genuine common-target result, not merely two empirical interventions that happened to agree.

---

## 7. Non-anticipation property

The active set

\[
D^+
=
\{e=(u,v):
\exists f\in A,\;
(u,v)\notin TC(G-f)\}
\]

is computable from:

- the base graph \(G\);
- the candidate delta set \(D\);
- the registered deletion contract \(A\).

It does not require:

- any augmented-state native outcome signature;
- the final operational partition;
- pairwise labels derived from the held-out outcome matrix.

Hence \(\Phi_A^+\) and \(\Phi_A^-\) are candidate **Level-2 contract-predictive repairs** under the OACR information-authority hierarchy.

The theorem therefore ties together the three intended OACR theory components:

\[
\boxed{
\text{native contract}
+
\text{non-anticipating construction}
+
\text{bidirectional exactness}
}
\]

within a nontrivial carrier class.

---

## 8. Relation to the earlier private-witness audit

The private-witness condition remains a valid stronger sufficient condition, and the frozen R4 artifact satisfies it for all 22 active deltas.

However, Theorem 1 shows that private witnesses are not required for exactness in the one-delta DAG/full-closure setting.

The earlier audit should therefore be retained as:
- a diagnostic strengthening observed in R4;
- not the main theoretical condition.

---

## 9. Finite-model sanity check

Before manuscript promotion, the theorem was sanity-checked by exhaustive enumeration over all topologically labelled DAGs through \(n=5\), all currently redundant one-edge deltas, and all nonempty subsets of base edges as singleton-deletion contracts.

Checked contract instances:

- \(n=3\): 3;
- \(n=4\): 288;
- \(n=5\): 41,301.

Total:

\[
41,592
\]

finite instances.

No violation of the theorem was found.

This is a proof-debugging check only; it is not evidence replacing the proof.

---

## 10. Why the theorem is narrower than universal OACR

The result depends critically on:

1. a DAG carrier;
2. one added redundant edge per augmented state;
3. singleton deletion actions applied to the shared base graph;
4. full post-action transitive closure as the native outcome coordinate.

The theorem does **not** automatically extend to:

- multiple simultaneous deltas;
- cyclic carriers before condensation;
- partial observation of post-action reachability;
- stochastic native execution;
- learned representations;
- action sequences whose later legality depends on earlier state changes;
- feature interactions in which two individually inert distinctions jointly matter.

Those failures are not nuisances. They define the next theoretical boundary to construct explicitly.

---

## 11. Immediate next theory task

Construct the smallest carrier in which the one-delta theorem fails after relaxing exactly one assumption.

Priority order:

1. multi-delta interaction under the same deletion contract;
2. partial native observation;
3. sequential actions with endogenous legality.

The preferred counterexample should establish:

\[
\text{local single-feature activity}
\not\Rightarrow
\text{global exact representation repair}
\]

once the one-delta separability assumption is removed.

That counterexample will make the positive theorem scientifically sharper.

---

## 12. Prior-art positioning

The graph-theoretic components must be positioned conservatively.

Relevant classical and adjacent lines include:
- transitive closure and transitive reduction;
- dynamic reachability under edge deletion;
- replacement paths and sensitivity oracles.

Aho, Garey, and Ullman (1972) define transitive reduction as a minimum-edge representation preserving reachability and establish the foundational relation between transitive reduction and transitive closure.

Recent dynamic-transitive-reduction work likewise treats redundant edges as those whose removal leaves an alternate directed path.

OACR novelty, if sustained, is not the graph lemma in isolation. It is the use of this structure to prove a **contract-induced, non-anticipating, bidirectional representation-repair theorem** whose target is the operational quotient generated by future native actions.

