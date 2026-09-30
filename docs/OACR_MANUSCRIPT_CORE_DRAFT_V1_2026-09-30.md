# OACR Manuscript Core Draft v1

**Working title:** *From Static Fidelity to Continuation Closure in Computational Representations*  
**Status:** manuscript prose draft; Sections 2 and 5 are intentionally written before the final Introduction and COMPOSE disposition  
**Date:** 2026-09-30

---

# 2. Operational adequacy under continuation contracts

## 2.1 Representations of persistent computational objects

A computational representation is often evaluated by what can be recovered from it at the present moment. For persistent systems, that criterion is incomplete. The same represented object may later be edited, deleted from, merged, revised, fine-tuned, rolled back, audited, or otherwise transformed. Two states that are indistinguishable under the current observation interface may therefore cease to be interchangeable when subjected to operations that the system is expected to support. Conversely, two internally distinct states may remain interchangeable under every registered operation of interest.

We formalize this distinction relative to a **continuation contract**. Let \(X\) denote the set of persistent system states and let

\[
R:X\rightarrow\mathcal R
\]

be an implemented representation. A continuation contract is written abstractly as

\[
\mathcal C
=
(\mathcal O,\mathcal A,H,\mathsf{Legal},\mathsf{Cost},\ldots),
\]

where \(\mathcal O\) specifies the registered observations, \(\mathcal A\) the registered state-changing operations, and \(H\) the registered horizon. Carrier-specific contracts may additionally include legality, cost, recovery, or other operational coordinates. We do not require every carrier to instantiate every coordinate.

The contract induces an operational behavior map

\[
B_{\mathcal C}:X\rightarrow\mathcal B_{\mathcal C},
\]

where \(B_{\mathcal C}(x)\) records exactly the registered continuation behavior of state \(x\) under \(\mathcal C\). The associated operational equivalence relation is

\[
x\sim_{\mathcal C}y
\iff
B_{\mathcal C}(x)=B_{\mathcal C}(y).
\]

The quotient

\[
O_{\mathcal C}=X/{\sim_{\mathcal C}}
\]

is the state partition required by the registered contract. It is not assumed to be the finest possible behavioral quotient, nor a universal semantic identity relation. It is the quotient needed for the declared observations, operations, and horizon.

The implemented representation similarly induces

\[
x\sim_Ry
\iff
R(x)=R(y),
\]

with partition \(P_R\).

The basic adequacy question is therefore not whether \(R\) uniquely identifies the internal state, but whether the distinctions induced by \(R\) match those required by \(O_{\mathcal C}\).

---

## 2.2 Directional representation error

A representation can fail in two opposite directions.

### Under-refinement

If

\[
R(x)=R(y)
\]

but

\[
B_{\mathcal C}(x)\neq B_{\mathcal C}(y),
\]

then \(R\) merges states that the registered continuation contract requires us to distinguish. We call this **under-refinement**.

We quantify the residual operational demand by

\[
U(R;\mathcal C)
=
H(O_{\mathcal C}\mid R).
\]

When

\[
U>0,
\]

the representation omits distinctions required by the contract.

### Over-refinement

If

\[
B_{\mathcal C}(x)=B_{\mathcal C}(y)
\]

but

\[
R(x)\neq R(y),
\]

then the representation preserves distinctions that are unnecessary under the registered contract. We call this **over-refinement**.

We quantify the excess distinction by

\[
E(R;\mathcal C)
=
H(R\mid O_{\mathcal C}).
\]

When

\[
E>0,
\]

the representation distinguishes states that the contract treats as operationally equivalent.

A representation is exact on a finite registered bank when

\[
U(R;\mathcal C)=0
\qquad\text{and}\qquad
E(R;\mathcal C)=0.
\]

This definition is deliberately symmetric. Evaluating only omission encourages the trivial solution of retaining complete internal state. Evaluating only compression risks collapsing distinctions that later operations require. The operational target is instead the contract-relative quotient itself.

---

## 2.3 Current state, operational state, and full identity

The key empirical configuration studied in this paper is

\[
R_{\rm current}
\prec
O_{\mathcal C}
\prec
R_{\rm full}.
\]

Here \(R_{\rm current}\) preserves the registered present but merges states whose future native behavior differs, whereas \(R_{\rm full}\) preserves every internal distinction and therefore separates states whose registered continuation remains identical.

This configuration matters for two reasons.

First, it rejects the idea that present-state fidelity is sufficient for a persistent representation. A state description can reproduce every currently registered observable consequence and still fail under a future operation.

Second, it rejects full internal identity as the default answer. Internal differences are not automatically operational requirements. If a distinction does not affect any continuation admitted by the contract, retaining it is representational excess relative to that contract.

The scientific question is therefore intermediate:

> Which distinctions are required to close the registered continuation dynamics?

---

## 2.4 WRITE as a first-order continuation operator

A one-step state-changing operation

\[
x\xrightarrow{a}x'
\]

provides the simplest continuation test. For a latent distinction \(d=(x,y)\) with equal current representation, define the action-specific activation indicator

\[
M(d,a)
=
\mathbf 1[
B_{\mathcal C_1}(x;a)
\neq
B_{\mathcal C_1}(y;a)
],
\]

where \(\mathcal C_1\) is a one-step registered contract.

This object is useful experimentally because it supports strong causal controls: the same states can be exposed to the same frozen operation panel, and the relevance of a latent distinction can be measured without changing the carrier or selecting actions from the observed outcome.

We treat WRITE as a **first-order generator** of continuation behavior rather than the full scientific object. A one-step contract can establish that a distinction hidden from the present becomes operationally necessary. It cannot establish that the same representation remains adequate once operations themselves alter later continuation semantics.

---

## 2.5 Composition and continuation interfaces

For multi-step systems, it is useful to distinguish the state from the interface that determines how the state can continue.

Let

\[
\Gamma_x(a)
\]

denote the carrier-relative continuation interface for candidate operation \(a\). Depending on the carrier, \(\Gamma\) may contain coordinates such as:

\[
\Gamma_x(a)
=
(
L_x(a),
E_x(a),
O_x(a),
I_x(a),
V_x(a)
),
\]

where \(L\) denotes legality or qualification, \(E\) enabledness or applicability, \(O\) registered outcome semantics, \(I\) invariants, and \(V\) viability or recoverability. The coordinate list is not universal; it is instantiated only where native semantics justify it.

A state-changing operation therefore acts on both the persistent state and the future interface:

\[
(x,\Gamma_x)
\xrightarrow{a}
(x',\Gamma_{x'}).
\]

This makes explicit the distinction between two phenomena:

1. applying more operations from a fixed operation domain;
2. applying an operation that changes the semantics, availability, or qualification of later operations.

The second phenomenon is the COMPOSE object relevant to this paper.

For a registered depth \(h\), write

\[
x\equiv_h y
\]

when the states are indistinguishable under the registered continuation interface through depth \(h\). A minimal delayed continuation failure has the form

\[
x\equiv_1 y
\qquad\text{but}\qquad
x\not\equiv_2 y.
\]

We do not claim that this depth-indexed equivalence construction is novel. Its role is to make representational demand explicit: a representation can be sufficient for every registered one-step continuation and still fail to close the next-step dynamics.

---

## 2.6 Relation to established theory

The formal ingredients above are closely related to mature theories of behavioral equivalence, contextual equivalence, bisimulation, state abstraction, predictive state, and strong preservation.

In particular, this paper does **not** claim to introduce:

- the idea that future behavior determines state equivalence;
- behavioral quotients or bisimulation;
- minimal sufficient predictive states;
- partition refinement;
- congruence under operators;
- full abstraction or representation independence;
- minimal strong-preserving abstractions.

These theories provide the mathematical language that makes OACR possible.

Our contribution is instead operational and representational. We use registered native transformation contracts to audit implemented computational representations in materially different carriers, quantify both omission and excess relative to the induced operational quotient, and use the resulting diagnosis to alter the representation itself. The empirical unit is not an abstract transition system alone, but a concrete representation paired with the native operations it is expected to support.

This distinction is important because the same internal difference can be necessary under one contract and irrelevant under another. Representation adequacy is therefore not treated as an intrinsic property of a state encoding. It is indexed by the continuation the representation is required to preserve.

---

# 5. From diagnosis to contract-gated representation redesign

## 5.1 Why diagnosis is not enough

A representation audit is scientifically limited if it can only report that a representation is too coarse or too fine. The stronger question is whether the operational mismatch can be converted into a representation transformation that survives native execution.

The relational carriers provide an exact setting in which this can be tested.

Let \(G\) be a shared base directed graph. Each augmented state has the form

\[
G+e,
\]

where

\[
e=(u,v)
\]

is an asserted edge that is redundant in the current transitive closure:

\[
(u,v)\in TC(G).
\]

All states therefore share the same current closure under the registered present interface.

The registered WRITE contract consists of a common set \(A\) of base-edge deletions. For each deletion \(f\in A\), the native outcome is the transitive closure after deleting \(f\).

The current closure representation collapses every state into one block. Full asserted-edge identity separates every augmented state. Neither matches the operational partition.

---

## 5.2 Contract-active distinctions

The central structural observation is that a redundant edge \(e=(u,v)\) matters only if the registered deletion contract can destroy the base reachability that currently makes \(e\) redundant.

Define

\[
\alpha_A(e)
=
\mathbf 1
\left[
\exists f\in A:
(u,v)\notin TC(G-f)
\right].
\]

If

\[
\alpha_A(e)=0,
\]

then every registered deletion preserves a base path from \(u\) to \(v\). Retaining the redundant edge cannot change any registered deletion outcome.

If

\[
\alpha_A(e)=1,
\]

then at least one registered deletion destroys the base path. In the augmented state, the retained redundant edge restores the reachability relation; in the base state, it does not. The distinction is therefore operationally necessary under the declared contract.

This yields a contract-gated representation:

\[
R_{\rm gate}(G+e)
=
\left(
G,\;
\begin{cases}
e,&\alpha_A(e)=1,\\
\varnothing,&\alpha_A(e)=0.
\end{cases}
\right).
\]

The construction uses the base graph, the declared action panel, and the current delta endpoint. It does not require selecting features from the augmented-state post-deletion outcome matrix.

---

## 5.3 Developmental exactness on R3

The developmental R3 bank contains:

- 272 states;
- 271 redundant augmented-edge states;
- 64 registered deletion actions.

The registered operational quotient contains

\[
101
\]

classes.

The closure-only representation has one class and therefore under-refines:

\[
U(R_{\rm current})=3.3914424817,
\qquad
E(R_{\rm current})=0.
\]

Full asserted-edge identity separates all 272 states and therefore over-refines:

\[
U(R_{\rm full})=0,
\qquad
E(R_{\rm full})=4.6960203596.
\]

The contract gate classifies:

- 100 augmented states as active;
- 171 as inactive.

The resulting representation has exactly

\[
101
\]

blocks and satisfies

\[
U(R_{\rm gate})=0,
\qquad
E(R_{\rm gate})=0.
\]

The representation was then executed, not merely compared at the partition level. Across

\[
272\times64=17{,}408
\]

registered state-action cells, native replay produced

\[
0
\]

mismatches.

An independent verifier reconstructed the gate and independently replayed all registered cells. A separate artifact-level audit also matched every stored replay cell against the accepted raw outcome matrix.

The same transform also reduces the declared per-state delta records from

\[
271
\]

to

\[
100,
\]

a carrier-specific reduction of

\[
63.10\%.
\]

We do not interpret this number as byte-optimal compression. It measures the physical record count under the declared shared-base-plus-delta encoding.

---

## 5.4 Prospective fresh confirmation on R4-building

The stronger test is whether the same contract-derived transform survives a prospectively frozen fresh carrier.

R4-building was frozen before augmented-state deletion outcomes were observed. It contains the same registered bank size:

- 272 states;
- 271 redundant augmented states;
- 64 registered deletion actions.

Its operational structure is materially different from R3.

The registered operational quotient contains only

\[
23
\]

classes.

The current-closure representation again has one block and under-refines:

\[
U(R_{\rm current})=0.7659699326,
\qquad
E(R_{\rm current})=0.
\]

Full asserted identity again over-refines:

\[
U(R_{\rm full})=0,
\qquad
E(R_{\rm full})=7.3214929087.
\]

The frozen contract gate identifies:

- 22 active augmented states;
- 249 inactive augmented states.

It induces exactly

\[
23
\]

representation blocks, equal to the registered operational partition:

\[
U(R_{\rm gate})=0,
\qquad
E(R_{\rm gate})=0.
\]

Native execution again matches every registered outcome:

\[
17{,}408/17{,}408
\]

cells reproduce exactly.

Under the declared delta-record encoding, the gate reduces retained per-state delta records from

\[
271
\]

to

\[
22,
\]

a carrier-specific reduction of

\[
91.88\%.
\]

The importance of the fresh result is not the compression percentage. It is that the structural rule was frozen before the fresh operational outcomes and still reached the exact operational quotient.

---

## 5.5 The representation-design interpretation

The same transform repairs both directional failures.

Starting from the current-closure representation:

\[
R_{\rm current}\prec O_A,
\]

the gate adds only the distinctions whose redundancy can be broken by the registered deletion contract.

Starting from full asserted identity:

\[
O_A\prec R_{\rm full},
\]

the gate removes delta identities that remain redundant under every registered action.

Thus, on the frozen carriers,

\[
R_{\rm gate}=O_A.
\]

This should not be read as a universal graph compression theorem. The result is stronger and narrower:

> Given a fixed native deletion contract and a shared-base single-redundant-edge state family, the contract determines exactly which currently redundant distinctions must remain represented for the registered future behavior to be preserved.

This is the constructive step that separates OACR from a collision catalogue. The operational quotient is not only measured after the fact; it guides a representation transformation whose behavior is then checked by native replay.

---

## 5.6 Why full state is not the default solution

One possible response to a continuation failure is to retain all internal state. That strategy guarantees that no internal distinction has been lost, but it answers a different question.

OACR asks for the distinctions required by the declared continuation contract.

The R3 and R4 results show that full identity can carry substantially more information than the contract requires:

\[
E(R_{\rm full})>0.
\]

At the same time, current closure carries too little:

\[
U(R_{\rm current})>0.
\]

The contract-gated representation occupies the intermediate point:

\[
R_{\rm current}
\prec
R_{\rm gate}
=
O_A
\prec
R_{\rm full}.
\]

This intermediate representation is the empirical object of interest. It preserves the object's registered ability to continue without treating every internal difference as part of its operational identity.

---

## 5.7 Limits of the constructive result

The exactness demonstrated here is finite and contract-specific.

We do not claim:

- universal minimality beyond the frozen bank;
- that redundant-edge gating is a general graph representation law;
- that the observed record reductions transfer across domains;
- that all operation families admit a simple structural certificate;
- that the same gate solves multi-step state-dependent qualification.

The result establishes a narrower but actionable principle:

> representation mismatch can be converted into a contract-derived structural repair, and that repair can be validated by exhaustive native execution on a finite registered carrier.

The COMPOSE experiments ask the next question: when the continuation interface itself changes under transformation, what additional distinctions are required to keep the representation closed?
