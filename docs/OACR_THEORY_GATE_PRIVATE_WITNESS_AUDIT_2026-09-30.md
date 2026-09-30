# OACR Theory Gate — Private-Witness Exactness Audit

Date: 2026-09-30

Status: **R4 PASS for candidate sufficient condition; theorem proof audit required before manuscript promotion**

## 1. Why this audit was opened

The current graph proposition proves an individual statement:

- an inactive redundant edge is behaviorally inert under every registered deletion;
- an active redundant edge differs from the base state under at least one registered deletion.

That statement alone does not prove that two different active deltas are operationally distinct. Therefore the equality

\[
P_{R_{\rm gate}}=O_{\mathcal C}
\]

was previously treated as an empirical R3/R4 fact.

The Theory Gate asks whether a carrier-level structural condition can guarantee the missing pairwise separation without reading the final augmented-state outcome partition.

## 2. Candidate condition — structural private deletion witness

Let \(G\) be a DAG, let \(A\subseteq E(G)\) be the registered singleton-deletion contract, and let \(D\) be a family of currently redundant candidate edges.

For a candidate delta

\[
e=(u_e,v_e)\in D,
\]

call a deletion \(f\in A\) a **private deletion witness** for \(e\) relative to active candidate set \(D^+\) when:

1. deletion \(f\) destroys the base reachability of \(e\):
   \[
   u_e\not\leadsto v_e \quad\text{in }G-f;
   \]
2. adding any other active candidate \(e'=(a,b)\in D^+\setminus\{e\}\) does not restore that reachability:
   \[
   u_e\not\leadsto v_e
   \quad\text{in }(G-f)+e'.
   \]

For a DAG this second check can be evaluated from the base post-deletion closure. Adding \(e'=(a,b)\) can restore \(u_e\leadsto v_e\) only if

\[
u_e\leadsto a
\quad\text{and}\quad
b\leadsto v_e
\]

in \(G-f\), allowing equality at either endpoint.

The condition depends on:
- the base graph;
- the frozen deletion alphabet;
- the registered candidate deltas.

It does **not** require the augmented-state native outcome matrix.

## 3. Candidate theorem

### Theorem PW — exactness under private witnesses

Consider the one-delta-per-state family consisting of a base state \(G\) and states \(G+e\) for \(e\in D\), where every \(e\in D\) is redundant in the current closure of \(G\).

Let

\[
D^+
=
\{e\in D:
\exists f\in A,\;
u_e\not\leadsto v_e\text{ in }G-f
\}
\]

be the contract-active deltas.

Assume every \(e\in D^+\) has a private deletion witness relative to \(D^+\).

Then:

1. every inactive state \(G+e\), \(e\notin D^+\), has the same registered operational signature as the base state \(G\);
2. every active state \(G+e\), \(e\in D^+\), differs operationally from the base state;
3. every two distinct active states \(G+e\) and \(G+e'\) are operationally distinct;
4. therefore the operational quotient has exactly
   \[
   |D^+|+1
   \]
   blocks;
5. the contract-gated representation that collapses all inactive deltas to the base representation and retains active-delta identity satisfies
   \[
   P_{R_{\rm gate}}=O_{\mathcal C}.
   \]

### Proof sketch

Item 1 is the existing inactive-edge soundness result: if the base retains \(u_e\leadsto v_e\) after every registered deletion, adding the direct redundant edge cannot change any registered transitive closure.

Item 2 follows because an active delta has some deletion \(f\) under which the base loses \(u_e\leadsto v_e\), while \(G+e\) retains the direct edge \(e\).

For item 3, choose a private witness \(f_e\) for active delta \(e=(u_e,v_e)\). Under \(f_e\), state \(G+e\) contains \(u_e\leadsto v_e\). By the private-witness condition, state \(G+e'\) for every other active \(e'\) does not restore \(u_e\leadsto v_e\). Their post-deletion closures therefore differ.

Items 4–5 follow immediately. \(\square\)

## 4. Frozen R4 audit

Source artifact:

- workflow run: 36438278451;
- artifact: oacr-r4-v2-building;
- artifact ID: 11003190307;
- accepted result hash recorded in the existing R4 manifest.

The frozen artifact was downloaded and the graph was reconstructed from its frozen combined.json, using the same SCC-condensation semantics as the registered producer.

The audit then used:
- the frozen 271 candidate states;
- the frozen 64 deletion actions;
- the accepted 22 active deltas;
- only base post-deletion reachability for the structural private-witness test.

### Result

\[
\boxed{22/22}
\]

active R4 deltas have at least one **structural private deletion witness**.

Witness counts:
- minimum per active delta: 1;
- maximum per active delta: 2.

As a separate verification-only check, all

\[
\boxed{22/22}
\]

active states also have at least one behavioral action coordinate on which their native outcome differs from the base and from every other active state's outcome.

Thus the candidate sufficient condition is not vacuous on R4: it explains the previously empirical fact that the 22 active deltas form 22 singleton operational classes while the base and 249 inactive deltas form the remaining class.

## 5. Scientific consequence

Before this audit, the strongest justified graph statement was:

> local activity predicts whether one redundant edge differs from the base, while exact equality of the gated representation and operational quotient remains an empirical R3/R4 result.

If Theorem PW survives formal proof review, the R4 statement can be strengthened to:

> R4 satisfies a contract-visible structural separability condition under which the local activity gate is provably exact; native replay then verifies that the implementation realizes the theorem's predicted quotient on all 17,408 registered cells.

This is substantially stronger because the exactness condition can be checked without using the augmented-state target outcome matrix for feature selection.

## 6. Prior-art boundary

The general problem of selecting a smallest family of attributes/tests that preserves discernibility is already well established:
- Minimum Test Set / Test Collection;
- rough-set attribute reducts;
- minimum keys / distinguishing attribute subsets.

Those literatures already contain NP-hardness results for minimum discernibility-preserving subsets. Therefore OACR must **not** claim that generic minimum-feature NP-hardness is itself a new theorem.

The stronger theoretical target is instead:

1. characterize the contract-induced representation-repair problem in native-transition terms;
2. identify structural conditions such as private deletion witnesses under which exact non-anticipating repair is tractable;
3. connect those conditions to bidirectional correction from coarse and fine endpoints;
4. prove which parts survive beyond the one-delta graph family.

## 7. Remaining acceptance steps

- [ ] Independently formalize and proof-check Theorem PW.
- [ ] Check whether a weaker condition than per-delta private witnesses suffices.
- [ ] Test the condition on R3 if the required frozen structural artifact is recoverable.
- [ ] Construct counterexamples:
  - active deltas with no private witnesses but still distinct;
  - active deltas that collide operationally;
  - feature interactions where local activity is insufficient.
- [ ] Compare the condition against known graph sensitivity / replacement-path / reachability-preserver results before novelty promotion.
- [ ] Only after these checks may the theorem enter the manuscript.
