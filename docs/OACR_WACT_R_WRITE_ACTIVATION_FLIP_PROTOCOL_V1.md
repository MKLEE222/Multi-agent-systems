# OACR-WACT-R v1 — Prospective WRITE-Activation Flip Protocol

**Date:** 2026-09-29  
**Status:** prospectively frozen before any augmented-state outcome on the WACT-R carrier panel  
**Role:** causal WRITE-contract experiment; successor to R3/R4/M2, not another compression benchmark.

## 1. Target claim

The experiment tests the following empirical statement:

> The operational necessity of a fixed internal distinction can flip solely because the declared future WRITE contract changes, even when the represented states and current READ observation are held fixed.

For a current-READ-equivalent pair \(x,y\), the desired witness has two nested contracts

\[
\mathcal W^- \subset \mathcal W^+
\]

that differ by exactly one native WRITE \(w^\*\), such that

\[
x \equiv_{\mathcal W^-} y
\]

but

\[
x \not\equiv_{\mathcal W^+} y.
\]

This is called a **WRITE-activation flip**.

The mature fact that future behavior induces an equivalence relation is not claimed as new. The empirical target is prospective causal realization and representation redesign in implemented native carriers.

## 2. Fresh carrier panel

Freeze the following eight Wikidata roots before any WACT-R augmented-state outcome is executed:

1. Q7397 — software
2. Q34379 — musical instrument
3. Q349 — sport
4. Q28640 — profession
5. Q11862829 — academic discipline
6. Q9143 — programming language
7. Q2095 — food
8. Q12136 — disease

No root may be replaced because of truncation, exclusion, weak activation, inconvenient results, or low compression.

## 3. Retrieval and inclusion

Use the authoritative R4-v2 retrieval discipline:

- ordered paginated WDQS retrieval;
- page size 2000;
- max pages 20;
- max 40,000 bindings;
- explicit page hashes and combined canonical edge hash;
- retrieval incompleteness retained as PAGINATION_TRUNCATED;
- WDQS non-transactional-snapshot limitation recorded.

Apply the same structural hygiene and inclusion gates as R4-v2:

- complete retrieval;
- prepared nodes >= 100;
- prepared asserted edges >= 128;
- redundant candidates >= 64;
- asserted edges available for >= 64 registered deletion actions.

WACT-R is underpowered for cross-carrier promotion if fewer than three roots are INCLUDED.

## 4. Frozen state family

For each included carrier let \(G\) be the prepared directed base graph.

Let

\[
C\subseteq TC(G)\setminus E(G)
\]

be redundant candidate edges.

Register:

- all candidates if \(|C|\le271\);
- otherwise 271 evenly spaced candidates under the same deterministic lexical ordering used by R4.

State family:

\[
X=\{G\}\cup\{G+e:e\in C\}.
\]

All states have the same registered current READ:

\[
READ(G)=READ(G+e)=TC(G).
\]

## 5. Frozen WRITE panel

Select 64 base asserted-edge deletion actions exactly as in R4-v2:

1. for every asserted base edge \(f\), compute base-only deletion impact

\[
J(f)=|TC(G)\triangle TC(G-f)|;
\]

2. sort by impact and lexical tie break;
3. choose 64 evenly spaced actions.

This action selection uses no augmented-state outcome.

## 6. WRITE-activation matrix

Before executing any augmented-state outcome, compute only from the base graph:

\[
M(e,f)
=
\mathbf 1[(u,v)\notin TC(G-f)]
\]

for candidate \(e=(u,v)\) and registered deletion \(f\).

Interpretation:

- \(M(e,f)=0\): write \(f\) leaves \(e\) transitively redundant;
- \(M(e,f)=1\): write \(f\) structurally activates the distinction carried by \(e\).

This is the same contract-active certificate used by T3, now resolved at the individual WRITE level.

For each distinction:

\[
k(e)=\sum_f M(e,f)
\]

is its WRITE-activation degree.

For each WRITE:

\[
g(f)=\sum_e M(e,f)
\]

is its distinction-activation load.

The matrix is frozen before augmented-state native replay.

## 7. Prospective causal witness selection

A candidate distinction \(e\) is eligible iff it has:

- at least one non-activating registered write;
- at least one activating registered write.

Thus:

\[
0<k(e)<64.
\]

Sort eligible candidates by:

1. activation degree \(k(e)\);
2. lexical edge identity.

Select up to 16 witnesses by deterministic even spacing through this ordered eligible list.

For every selected witness \(e\):

- \(f^-(e)\): first registered action in action-index order with \(M(e,f)=0\);
- \(f^+(e)\): first registered action in action-index order with \(M(e,f)=1\).

No augmented-state behavior is used for witness or action selection.

## 8. Contract intervention

For the fixed state pair

\[
(G,\;G+e)
\]

define:

### Inert contract

\[
\mathcal W^-_e=\{f^-(e)\}.
\]

### Activated contract

\[
\mathcal W^+_e=\{f^-(e),f^+(e)\}.
\]

The only intervention is adding one future native WRITE \(f^+(e)\).

The states, current READ, representation candidates, observation function, and native implementation remain unchanged.

## 9. Native causal replay

For every selected witness execute, from both \(G\) and \(G+e\):

1. \(f^-(e)\);
2. \(f^+(e)\).

Observe the complete post-deletion transitive closure exactly.

Registered causal prediction:

### Under the inert write

\[
TC(G-f^-)
=
TC((G+e)-f^-).
\]

### Under the activating write

\[
TC(G-f^+)
\neq
TC((G+e)-f^+).
\]

Therefore:

\[
G\equiv_{\mathcal W^-_e}G+e
\]

but

\[
G\not\equiv_{\mathcal W^+_e}G+e.
\]

Any violation triggers theory/implementation audit and blocks promotion.

## 10. Representation flip

For each witness compare two representations of the same pair.

### Under \(\mathcal W^-_e\)

Contract gating must erase \(e\):

\[
\phi_{\mathcal W^-}(G)
=
\phi_{\mathcal W^-}(G+e).
\]

The one-class representation should satisfy:

\[
U=E=0
\]

on this two-state contract because the states are operationally equivalent.

### Under \(\mathcal W^+_e\)

Contract gating must retain \(e\):

\[
\phi_{\mathcal W^+}(G)
\neq
\phi_{\mathcal W^+}(G+e).
\]

The two-class representation should again satisfy:

\[
U=E=0
\]

because the added WRITE makes the states operationally distinct.

Thus the sufficient representation changes while the underlying states do not.

## 11. Primary endpoints

Per carrier report:

1. number of eligible distinctions;
2. number of frozen causal witnesses;
3. native inert-write prediction failures;
4. native activating-write prediction failures;
5. number of exact representation flips;
6. number of witnesses with \(U=E=0\) under both nested contracts.

Cross-carrier promotion requires:

- at least 3 INCLUDED carriers;
- at least 32 total prospective witnesses;
- zero native causal prediction failures;
- zero representation-flip failures.

## 12. Secondary WRITE-activation spectrum

Report descriptively, without making a universal-law claim:

- distribution of \(k(e)\);
- fraction \(k(e)=0\);
- fraction \(k(e)=64\);
- distribution of \(g(f)\);
- fraction of writes with \(g(f)=0\);
- maximum activation load;
- top 10% and top 25% of writes' share of all activation events;
- Gini coefficient of \(g(f)\);
- relationship between base deletion impact \(J(f)\) and activation load \(g(f)\).

This tests whether representational relevance is concentrated in a small subset of WRITE content.

No concentration threshold is required for primary causal acceptance.

## 13. Nested-prefix diagnostic

Using the frozen action-index order, define prefixes

\[
A_k=\{f_1,\ldots,f_k\}.
\]

For every \(k=0,\ldots,64\), compute structurally:

\[
n_{\rm active}(A_k)
=
|\{e:\exists f\in A_k,\;M(e,f)=1\}|.
\]

Report the retention trajectory

\[
\rho_k=\frac{n_{\rm active}(A_k)}{|C|}.
\]

This is a diagnostic WRITE-retention curve.

Do not interpret action index \(k\) as an equal-interval operational-demand scale.

## 14. Boundaries

WACT-R does not claim novelty for:

- observational equivalence;
- bisimulation;
- contextual equivalence;
- Myhill–Nerode future equivalence;
- monotonicity under nested contracts;
- transitive-closure deletion sensitivity.

The target contribution is empirical and constructive:

> in implemented representations, the necessity of a concrete stored distinction can be prospectively switched by changing only the future native WRITE contract, and the required representation can be redesigned accordingly before executing the augmented-state outcomes.

## 15. Follow-on cross-system gate

If WACT-R passes, the same abstraction should be tested without changing its definition in:

1. Git merge/write contracts using natural same-tree pairs;
2. learned persistent-state editors using H0-collision pairs and frozen future-edit panels.

Only then may the paper promote a cross-system WRITE-activation claim.
