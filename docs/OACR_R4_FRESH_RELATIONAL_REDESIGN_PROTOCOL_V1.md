# OACR-R4 Protocol v1 — Fresh Relational Contract-Gated Redesign Replication

**Date:** 2026-09-28  
**Status:** prospectively frozen before any R4 native-operation outcome is inspected  
**Role:** fresh-carrier confirmation of the contract-gated delta representation developed on R3.

## 1. Primary question

On independently retrieved relational carriers, does the theorem-driven transform

\[
\phi_A(G+e)=
\begin{cases}
\bot,& e\text{ remains redundant after every registered deletion},\\
e,& \text{otherwise}
\end{cases}
\]

remain exactly contract-adequate, and how much over-refinement / physical delta storage does it remove?

The theorem predicts adequacy on the registered single-redundant-edge state family.

The uncertain empirical quantities are:

- how many candidate deltas are contract-active;
- how many contract-active deltas remain behaviorally equivalent to each other;
- resulting excess \(E\);
- physical delta-record compression;
- action-content concentration.

## 2. Frozen root list

Retrieve five independent Wikidata P279 regions:

1. Q11173 — chemical compound;
2. Q618123 — geographical feature;
3. Q42889 — vehicle;
4. Q41176 — building;
5. Q43229 — organization.

Root identity is frozen before carrier outcomes.

No root may be replaced because its eventual result is weak, null, inconvenient, or structurally different.

## 3. Frozen retrieval template

For each root \(r\), retrieve asserted P279 edges through three subclass levels using the same union pattern as R1:

- direct child of root;
- child of direct child;
- child of grandchild.

Use:

- ORDER BY ?child ?parent;
- hard row limit: 2500;
- JSON response frozen byte-for-byte;
- raw response SHA256 recorded.

If the returned binding count is exactly 2500, classify the carrier as **TRUNCATED** and exclude it from primary quantitative comparison without replacement.

Retrieval failure after registered retries is reported as infrastructure failure, not scientific exclusion.

## 4. Graph hygiene

For each retrieved root:

1. remove duplicate edges and self-loops;
2. retain the component containing the root when present, otherwise largest weak component;
3. collapse nontrivial SCCs exactly as R1;
4. require a DAG after condensation.

Record:

- raw unique edges;
- prepared nodes;
- prepared asserted edges;
- SCC count;
- closure size;
- redundant entailed-but-unasserted edge count.

## 5. Outcome-blind structural inclusion gates

A non-truncated carrier enters the primary R4 analysis iff, before any augmented-state deletion outcome is executed:

- prepared nodes \(\ge 100\);
- prepared asserted edges \(\ge 128\);
- redundant entailed-but-unasserted candidates \(\ge 64\);
- at least 64 asserted edges are available for the shared action panel.

Failure of a structural gate is reported and the root is not replaced.

The primary replication block requires at least two roots to pass these gates.
If fewer than two pass, R4 is reported as underpowered and a new root protocol must be frozen separately rather than modifying this one.

## 6. Frozen state-bank rule

Let

\[
C=TC(G)\setminus E(G).
\]

If \(|C|\le 271\), use all candidates.

If \(|C|>271\):

1. sort candidates lexically by endpoint identity;
2. choose exactly 271 unique candidates at evenly spaced indices across that ordered list.

Create:

\[
X=\{G\}\cup\{G+e:e\in C_{\rm reg}\}.
\]

All state-bank selection occurs before any future deletion outcome is executed.

## 7. Frozen action-panel rule

For every asserted edge \(f\in E(G)\), compute from the **base graph only**:

\[
J(f)=|TC(G)\triangle TC(G-f)|.
\]

Sort by:

1. \(J(f)\);
2. lexical edge identity.

Select 64 unique asserted edges at evenly spaced indices.

This is exactly the R3 action-panel construction rule.

No augmented-state outcome may be used to choose actions.

## 8. Contract-gated representation

For every registered redundant edge

\[
e=(u,v),
\]

compute from base post-deletion reachability only:

\[
\alpha_A(e)
=
\mathbf 1
\left[
\exists f\in A:
(u,v)\notin TC(G-f)
\right].
\]

Encode:

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

The active classifier is frozen before augmented-state outcomes are executed.

## 9. Registered comparison representations

For every carrier compare:

### R0
Complete current transitive closure only.

### Rfull
Complete asserted-edge identity.

### Rgate
Shared base + optional contract-active redundant edge \(\phi_A\).

Primary metrics under uniform state weights:

\[
U=H(O_A\mid R),
\qquad
E=H(R\mid O_A).
\]

Also report exact pairwise under-/over-refinement.

## 10. Native replay

For every included carrier, every registered state, and every registered deletion:

1. execute from the original full state and record complete post-deletion closure;
2. decode Rgate to shared base plus optional retained delta;
3. execute the same deletion;
4. require exact closure equality.

All registered state-action cells must be preserved.

The theorem predicts exact replay.

Any mismatch invalidates the run and triggers an implementation/assumption audit rather than feature tuning.

## 11. Primary empirical quantities

Per carrier report:

1. \(|X|\);
2. full operational class count;
3. \(D(A)=H(O_A\mid O_0)\);
4. R0 \(U/E\);
5. Rfull \(U/E\);
6. Rgate \(U/E\);
7. active redundant-edge count;
8. inactive redundant-edge count;
9. active-edge fraction;
10. delta-edge record reduction;
11. whether Rgate exactly matches the operational partition;
12. number and sizes of active-edge equivalence groups if \(E(Rgate)>0\).

No minimum compression percentage is required for a carrier to be retained.

## 12. Secondary action-content analysis

For each included carrier:

- enumerate all 64 singleton action contracts;
- enumerate all \(\binom{64}{2}=2016\) action pairs;
- report operational class-count and conditional-demand distributions;
- compute leave-one-action-out effect on the full operational partition.

The panel-relative minimum action basis may be explored by exact or branch-and-bound search only after these frozen quantities are reported.

Any basis result is identified as related to mature characterization-set / testing ideas and is not claimed as a new general theorem.

## 13. Confirmatory interpretation

R4 can prospectively support:

- theorem-to-implementation transfer of contract-gated compression;
- fresh-carrier evidence that some full-state distinctions can be safely discarded relative to a declared native deletion contract;
- carrier-to-carrier variation in active support structure;
- whether exact partition matching on R3 was exceptional or recurrent.

R4 does not establish:

- universal minimality of Rgate;
- prevalence over all Wikidata classes;
- a natural historical process;
- a domain-independent compression percentage;
- a new graph-reachability theorem.

## 14. Failure retention

Retain all of the following:

- no root passes inclusion;
- only one root passes;
- zero inactive edges;
- Rgate has substantial excess \(E\);
- action demand is nearly uniform;
- one action dominates the quotient;
- retrieval truncation;
- runtime/replay mismatch.

No failed or weak carrier is replaced within this protocol.
