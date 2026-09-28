# OACR-T3 Note v1 — Contract-Gated Delta Sufficiency and Exactness

**Date:** 2026-09-28  
**Status:** theory note frozen independently of R4 fresh-carrier outcomes  
**Role:** separate theorem-protected adequacy of contract-gated deltas from carrier-specific exact partition matching.

## 1. Setting

Let G=(V,E) be a finite directed graph after the registered graph-hygiene transformation.

Let

\[
C \subseteq TC(G)\setminus E
\]

be a registered set of redundant candidate edges.

The state family is

\[
X=\{G\}\cup\{G+e:e\in C\}.
\]

Let the registered action family be deletion of base asserted edges:

\[
A\subseteq E.
\]

For f in A, the registered observation is the complete post-deletion transitive closure:

\[
B(G,f)=TC(G-f),
\]

\[
B(G+e,f)=TC((G+e)-f).
\]

The analysis is exact and finite.

## 2. Contract-active delta

For e=(u,v) in C define

\[
\alpha_A(e)
=
\mathbf 1
\left[
\exists f\in A:
(u,v)\notin TC(G-f)
\right].
\]

Equivalently, e is inactive iff it remains transitively redundant after every registered base deletion.

Define the contract-gated representation

\[
\phi_A(G)=\bot,
\]

\[
\phi_A(G+e)=
\begin{cases}
\bot,&\alpha_A(e)=0,\\
e,&\alpha_A(e)=1.
\end{cases}
\]

The representation stores one shared base graph plus an optional retained active delta.

## 3. Theorem 1 — inactive-delta erasure

### Statement

If \(\alpha_A(e)=0\), then for every registered deletion \(f\in A\),

\[
TC((G+e)-f)=TC(G-f).
\]

### Proof

Let \(e=(u,v)\).

\(\alpha_A(e)=0\) means:

\[
(u,v)\in TC(G-f)
\]

for every \(f\in A\).

Therefore after deletion f, e is already implied by reachability in G-f.

Adding an already implied edge cannot add a new reachability relation:

\[
TC((G-f)+e)=TC(G-f).
\]

Because e is not one of the base asserted deletion actions,

\[
(G+e)-f=(G-f)+e.
\]

Hence

\[
TC((G+e)-f)=TC(G-f).
\]

QED.

## 4. Corollary 1 — contract adequacy

For the registered state family X and action family A,

\[
U_A(\phi_A)=0.
\]

### Reason

- base state G is decoded exactly;
- active delta states are decoded exactly because e is retained;
- inactive delta states may be decoded as G by Theorem 1 without changing any registered outcome.

Thus the operational response signature is a deterministic function of \(\phi_A\).

This is a sufficiency statement, not a storage-minimality statement.

## 5. Active response signature

For every active candidate e define its complete registered response signature:

\[
\sigma_A(e)
=
\left(
TC((G+e)-f)
\right)_{f\in A}.
\]

Define the base signature:

\[
\sigma_A(\bot)
=
\left(
TC(G-f)
\right)_{f\in A}.
\]

Every inactive e has

\[
\sigma_A(e)=\sigma_A(\bot)
\]

by Theorem 1.

## 6. Theorem 2 — exact quotient criterion

The contract-gated representation matches the operational partition exactly,

\[
U_A(\phi_A)=E_A(\phi_A)=0,
\]

iff distinct retained active delta identities have distinct registered response signatures:

\[
e_1\neq e_2,
\quad
\alpha_A(e_1)=\alpha_A(e_2)=1
\]

implies

\[
\sigma_A(e_1)\neq\sigma_A(e_2).
\]

### Proof sketch

Theorem 1 already gives U=0.

Rgate uses:

- one shared representation class for base plus all inactive deltas;
- one distinct representation class per active delta identity.

The shared base/inactive class is one operational class because all have \(\sigma_A(\bot)\).

Therefore the only possible source of over-refinement is two distinct active delta identities with the same operational response signature.

Hence E=0 iff the active response map is injective.

QED.

## 7. Corollary 2 — source of excess

If two or more active deltas share the same complete response signature, Rgate remains adequate but over-refines:

\[
U_A(\phi_A)=0,
\qquad
E_A(\phi_A)>0
\]

under any state distribution assigning positive mass to at least two such identities.

Thus fresh-carrier Rgate excess is not a failure of the adequacy theorem.

It measures non-injectivity of active-delta identity relative to the registered contract.

## 8. Uniform-bank excess decomposition

Under a uniform distribution over the registered state bank, let active response-equivalence groups have sizes

\[
m_1,\ldots,m_k.
\]

The base plus inactive group contributes no Rgate excess because it is already represented by one shared marker.

All Rgate excess comes from active groups with \(m_i>1\).

Equivalently, E is the conditional entropy of retained active identity given its operational response class.

This is inherited conditional-entropy algebra, not a new information-theoretic theorem.

## 9. Physical delta-record reduction

Let

\[
|C|=n,
\qquad
n_{\rm active}=\sum_{e\in C}\alpha_A(e).
\]

The declared shared-base delta encoding stores:

- n delta-edge records before contract gating;
- \(n_{\rm active}\) delta-edge records after contract gating.

The physical record-count reduction is:

\[
1-\frac{n_{\rm active}}{n}.
\]

This is a concrete property of the declared representation format.

It is not a byte-optimality or computational-complexity claim.

## 10. R3 interpretation

On the frozen R3 bank:

\[
|C|=271,
\qquad
n_{\rm active}=100.
\]

The active response map is empirically injective on the frozen 64-action panel.

Therefore:

\[
|R_{\rm gate}|=|O_A|=101,
\]

\[
U=E=0.
\]

Theorem 1 explains why the 171 inactive deltas can be erased safely.

Theorem 2 identifies the additional carrier-specific condition responsible for exact minimal partition matching.

The 63.10% record reduction is therefore carrier-specific, while contract adequacy follows from the structural criterion.

## 11. Fresh-carrier prediction

R4 does not need exact matching to validate Theorem 1.

For every included fresh carrier, the theorem predicts:

\[
U_A(R_{\rm gate})=0
\]

and exact native replay.

The empirical questions are instead:

1. how many deltas are active?
2. how often are active response signatures non-injective?
3. how large is E?
4. how much delta-record compression is obtained?

A fresh carrier with U=0 and E>0 is fully consistent with the theorem and scientifically informative.

## 12. Boundary

This note does not claim novelty for:

- transitive-closure redundancy;
- deletion sensitivity;
- provenance/reachability maintenance;
- behavioral quotients;
- conditional entropy.

The OACR contribution target is the use of a contract-derived structural certificate to transform an implemented representation and then audit exact native behavior.

The theorem currently assumes:

- one optional redundant delta per registered state;
- deletion actions drawn from the base asserted-edge set;
- exact transitive-closure observation;
- finite exact state/action banks.

Multiple interacting deltas are an open extension and may not be inferred from this result.
