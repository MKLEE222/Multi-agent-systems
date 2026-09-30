# OACR Manuscript Core Draft v1

**Working title:** *From Static Fidelity to Continuation Closure in Computational Representations*  
**Status:** manuscript prose draft; Sections 2 and 5 are intentionally written before the final Introduction and COMPOSE disposition  
**Date:** 2026-09-30

---


# 1. Introduction

Persistent computational objects are rarely required only to represent what is true **now**. They are expected to continue: to be edited, merged, deleted from, revised, fine-tuned, audited, rolled back, or otherwise transformed. A representation can therefore be perfectly adequate for the present and still be inadequate for the object's registered future operations. Conversely, two internally distinct states can remain interchangeable under every transformation the system is expected to support.

This creates a representation-design problem that is easy to miss if adequacy is evaluated only by static fidelity:

> **Which distinctions must a persistent computational representation preserve so that the object can continue to support its registered future operations?**

The underlying mathematics of behavioral equivalence is mature. Strong-preservation results show how abstractions can be refined until they preserve a chosen language or operator family; representation-independence results characterize when different internal representations remain indistinguishable under an abstract interface; knowledge-compilation work compares representation languages by the queries and transformations they support. Our contribution is not to reintroduce those ideas under new terminology.

We study a different empirical starting point: an **implemented representation** already used by a persistent computational system, paired with a prospectively registered set of **native state-changing operations**. We ask whether the distinctions stored by the representation match the distinctions required by that continuation contract.

Let \(R\) be the partition induced by an implemented representation and \(O_{\mathcal C}\) the partition induced by native behavior under a registered continuation contract \(\mathcal C\). Two directional failures are possible.

A representation **under-refines** the contract when it merges states whose registered continuation differs. It **over-refines** when it preserves internal distinctions that make no difference to the registered continuation. On a frozen state bank with reference measure \(\mu\), we quantify these directions by

\[
U_\mu(R;\mathcal C)
=
H_\mu(O_{\mathcal C}\mid R)
\]

and

\[
E_\mu(R;\mathcal C)
=
H_\mu(R\mid O_{\mathcal C}).
\]

The empirical configuration of interest is therefore not merely a collision. It is the strict intermediate structure

\[
R_{\rm current}
\prec
O_{\mathcal C}
\prec
R_{\rm full},
\]

where the current representation is too coarse, full internal identity is too fine, and the continuation contract selects an intermediate set of distinctions.

We call the resulting experimental program **Operational Adequacy of Computational Representations (OACR)**. OACR combines four steps:

1. register a native continuation contract independently of the result;
2. audit an implemented representation for both under- and over-refinement;
3. identify operation-relative distinctions under same-contract and outcome-blind controls;
4. where possible, convert the audit into a representation transformation and validate the transformed representation by native replay.

Across exact relational, natural version-history, and learned parametric carriers, we find that present-state equality alone does not determine representational necessity. In exact relational carriers, currently redundant state distinctions split into two classes under a shared deletion contract: some are required by future operations, while others remain operationally irrelevant. Full identity therefore stores too much, while current closure stores too little.

The strongest result is constructive. From the registered deletion contract, without inspecting the augmented-state post-deletion outcome matrix, we derive a gate that retains only redundant edges whose redundancy can be broken by a registered action. On a developmental carrier and a prospectively frozen fresh carrier, the resulting representation matches the complete registered operational quotient exactly. On the fresh building carrier, the partition changes from one current block and 272 full-identity blocks to 23 operational blocks; the gated representation yields

\[
U_\mu=E_\mu=0
\]

and reproduces all

\[
17{,}408/17{,}408
\]

registered native outcomes while retaining only 22 of 271 declared per-state deltas.

We then ask when one-step adequacy remains adequate under composition. The answer is not "whenever the horizon becomes longer." In two exact relational deletion carriers, every distinction is either activated at depth one or remains inert under the entire frozen action universe. In a learned GRACE control, 224 current collisions remain equivalent through the complete registered depth-two panel. By contrast, a controlled dynamic-qualification system provides an exact mechanism in which the immediate continuation interface is preserved but a shared first transformation changes the legality of a later operation. This motivates a continuation-interface view in which operations may alter the semantics, qualification, or response of later operations.

The paper makes four contributions:

1. **A native-contract adequacy audit for implemented representations.** We formalize and measure directional under- and over-refinement relative to a registered continuation contract, while explicitly inheriting behavioral-equivalence and strong-preservation theory.
2. **Cross-carrier evidence that representational necessity is operation-relative.** Exact relational, natural version-history, and learned-state carriers provide positive and negative boundaries under same-contract native operations.
3. **A constructive audit-to-repair result.** A contract-derived structural gate reaches the exact registered operational quotient on relational carriers and survives exhaustive native replay, including a prospectively frozen fresh carrier.
4. **A bounded composition result.** Increasing action depth alone does not force new representational demand in the audited fixed-domain controls; delayed demand emerges in a controlled mechanism when an earlier transformation changes the continuation interface of a later one.

The scope is deliberately finite and contract-relative. We do not claim a universal minimal state representation, universal provenance necessity, or a new theory of behavioral equivalence. The target is narrower: determine what an implemented representation must preserve to keep supporting the transformations it is actually required to perform.


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

Let \(\mu\) be a reference distribution over the registered state bank. We quantify the residual operational demand by

\[
U_\mu(R;\mathcal C)
=
H_\mu(O_{\mathcal C}\mid R).
\]

When

\[
U_\mu>0,
\]

the representation omits distinctions required by the contract.

Unless otherwise stated, all finite-bank experiments use the empirical uniform measure over the frozen registered states. We additionally report pairwise under-refinement counts so that the existence of omitted distinctions does not depend on the entropy weighting chosen by \(\mu\).

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
E_\mu(R;\mathcal C)
=
H_\mu(R\mid O_{\mathcal C}).
\]

When

\[
E_\mu>0,
\]

the representation distinguishes states that the contract treats as operationally equivalent.

As with under-refinement, we also report pairwise over-refinement counts.

A representation is exact on a finite registered bank when

\[
U_\mu(R;\mathcal C)=0
\qquad\text{and}\qquad
E_\mu(R;\mathcal C)=0.
\]

This definition is deliberately symmetric. Evaluating only omission encourages the trivial solution of retaining complete internal state. Evaluating only compression risks collapsing distinctions that later operations require. The operational target is instead the contract-relative quotient itself.

---

## 2.3 Current state, operational state, and full identity

For two partitions \(P,Q\) over the same registered state bank, write

\[
P\preceq Q
\]

when \(P\) is **coarser than or equal to** \(Q\): every block of \(Q\) is contained in a block of \(P\). Write \(P\prec Q\) for strict coarsening.

The key empirical configuration studied in this paper is therefore

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

Strong-preservation results in abstract interpretation already show that an abstraction can be minimally refined until it is complete for a chosen specification language or family of semantic operators. Representation-independence results likewise study relations between internal representations that are preserved by the operations of an abstract interface. Knowledge-compilation work compares representation languages by the queries and transformations they support. We therefore treat all three as direct theoretical predecessors rather than weaker analogies.

Our contribution is instead operational and representational. We use registered **native transformation contracts** to audit already implemented computational representations in materially different carriers, quantify both omission and excess relative to the induced operational quotient, separate scientific negatives from construction/runtime failures under prospective controls, and use the resulting diagnosis to alter a representation whose behavior is then checked by native replay. The empirical unit is not an abstract transition system alone, but a concrete representation paired with the native operations it is expected to support.

This distinction is important because the same internal difference can be necessary under one contract and irrelevant under another. Representation adequacy is therefore not treated as an intrinsic property of a state encoding. It is indexed by the continuation the representation is required to preserve.


---

# 3. Experimental discipline under native operation contracts

## 3.1 Same-contract evaluation

A recurring source of false representational necessity is action selection that depends on the state pair being evaluated. If each pair is tested only with an operation chosen because it is known to expose that pair, then the experiment conflates two questions:

1. whether the representation omits an operationally relevant distinction;
2. whether the evaluator selected an operation specifically to make that distinction relevant.

We therefore separate **state construction** from the **registered operation contract** wherever possible. A same-contract experiment applies the same frozen action family to every state in the registered bank.

For a finite action set

\[
A=\{a_1,\ldots,a_m\},
\]

each state receives the same operational probe

\[
B_A(x)
=
\bigl(
B(x,a_1),\ldots,B(x,a_m)
\bigr).
\]

The induced quotient is therefore determined by a shared contract rather than pair-specific action selection.

This discipline is central to the R3/R4 relational studies and the G5 natural Git study.

---

## 3.2 Freeze before outcome

Every confirmatory experiment distinguishes quantities that may be chosen before outcome from quantities that are measured after outcome.

Examples of pre-outcome frozen objects include:

- carrier and source snapshot;
- state bank;
- operation family;
- observation signature;
- collision criterion;
- witness selection rule;
- stopping rule;
- success and underpower thresholds.

A result is not promoted from developmental to confirmatory status merely because the same code is rerun on a new machine. The carrier or selection rule must have been fixed before the relevant outcome was observed.

This distinction is especially important for representation redesign. A representation feature chosen after inspecting the full operational partition may reproduce the partition without demonstrating that the feature can be derived from the contract itself.

The contract-gated relational representation is therefore constructed from the base graph, the registered action set, and the current delta endpoint rather than from the augmented-state outcome table.

---

## 3.3 Native execution rather than surrogate labels

Whenever possible, operational equivalence is determined by the carrier's native transformation mechanism.

Examples include:

- graph deletion followed by exact transitive-closure recomputation;
- native Git merge execution;
- official Finetune editing of the declared model parameter;
- typed legality and transition execution in the controlled SQEC carrier.

Structural certificates may predict an outcome, but the accepted empirical result requires the native operation itself to agree with the certificate.

This prevents a circular evaluation in which the same abstraction both defines and verifies the claimed behavior.

---

## 3.4 Independent verification

A producer and a verifier answer different questions.

The producer constructs the registered states, executes the frozen contract, and records outcomes.

The verifier reconstructs the claim from an independently specified input boundary and checks:

- carrier identity;
- state/action registration;
- representation classification;
- native replay;
- operational signatures;
- \(U/E\) bookkeeping.

For consequential positive claims, a verifier should not merely hash or re-read producer output. It should recompute the relevant structure or replay the native operation from the frozen inputs.

We additionally distinguish:

- **artifact verification**, which checks a frozen run without revisiting mutable external sources;
- **fresh targeted replay**, which reinitializes the carrier and reconstructs a promoted witness independently.

---

## 3.5 Scientific negatives and engineering failures

A zero result is scientifically informative only when the registered experiment was actually executed with sufficient coverage.

We therefore distinguish three outcomes.

### Scientific negative

The registered carrier and action bank execute successfully, the preregistered power/coverage gate is met, and no qualifying separation is observed.

Example: GRACE L1b executes the full registered H2 panel over 224 H0 collision pairs and observes no separation.

### Structural or construction underpower

The experiment does not instantiate enough eligible states/actions to test the intended phenomenon.

Example: a Git target-construction protocol can fail because too few natural pairs admit both required action classes. This is not evidence that the phenomenon is absent.

### Engineering failure

The scientific contract is not reached because of runtime, path, artifact, repository-object, or verifier plumbing.

Engineering failures are repaired without changing the frozen scientific selection rules. If an outcome was already exposed before the failure, the repair record explicitly states which scientific quantities are now fixed and may no longer be altered.

This separation is necessary for the negative evidence in the paper to be interpretable.

---

## 3.6 Outcome-blind witness selection

When a contract contains many potential witnesses, promotion rules are defined before the relevant outcomes are inspected.

Typical deterministic rules include:

- lexical first eligible witness;
- evenly spaced selection over a frozen eligible list;
- lowest fold, then lowest anchor ID, then lowest action ID.

The purpose is not statistical randomization. It is to prevent choosing the witness with the most visually dramatic effect after observing the result matrix.

Full result matrices are retained even when only one witness is promoted for targeted replay.

---

## 3.7 Why this discipline is part of the scientific contribution

The paper's core object is contract-relative representation adequacy. That object is unusually vulnerable to definitional circularity:

- operations can be chosen to make a distinction matter;
- representations can be redesigned after inspecting the desired partition;
- hidden-state features can be declared necessary merely because they differ;
- external carriers can drift between discovery and verification.

The experimental discipline above is therefore not ancillary infrastructure. It is what makes the comparison

\[
P_R
\quad\text{vs.}\quad
O_{\mathcal C}
\]

empirically meaningful.

The same contract must be specified independently enough that an observed mismatch is evidence about the representation, rather than an artifact of how the evaluator constructed the test.

---


# 4. First-order WRITE evidence: when current equality is not enough

## 4.1 WRITE as a controlled first-order test

The simplest continuation failure occurs when two states are equivalent under the registered present interface but a common future transformation makes their difference operational.

For a latent distinction \(d=(x,y)\) and registered write \(a\), define

\[
M(d,a)
=
\mathbf 1[
B(x;a)\neq B(y;a)
].
\]

The same latent distinction may be inert under one write and active under another. This makes WRITE useful experimentally: it turns representational necessity into a state-by-action question rather than an intrinsic property of hidden state.

However, hidden-state difference alone is not evidence of necessity. A valid WRITE experiment must expose the compared states to the same registered operation contract or freeze the action selection independently of the observed separation.

## 4.2 Exact relational shared-contract evidence

The R3 relational bank contains 272 states that share the same current transitive closure. One state is the base graph; 271 states add a currently redundant asserted edge.

All states face the same 64 registered base-edge deletions.

The current closure representation therefore places all 272 states in one block. Yet the native deletion outcomes induce 101 operational classes. Relative to the frozen empirical uniform measure,

\[
U_\mu(R_{\rm current})=3.3914424817,
\qquad
E_\mu(R_{\rm current})=0.
\]

Full asserted-edge identity creates 272 blocks and moves the error in the opposite direction:

\[
U_\mu(R_{\rm full})=0,
\qquad
E_\mu(R_{\rm full})=4.6960203596.
\]

The same current graph semantics therefore support both conclusions:

- some currently redundant distinctions must be retained for future operations;
- many other currently redundant distinctions remain unnecessary under the same operation contract.

This is the first exact instance of

\[
R_{\rm current}
\prec
O_{\mathcal C}
\prec
R_{\rm full}.
\]

The prospectively frozen R4-building carrier reproduces the same qualitative pattern with substantially different operational geometry: 272 states collapse into 23 operational classes, with only 22 augmented states required by the registered deletion contract.

## 4.3 Action-specific activation

The relational WACT experiments ask a sharper question: for a fixed latent redundant-edge distinction, which registered writes actually make it matter?

The design separates the latent distinction from the action choice. Candidate states and action rules are frozen before the native outcomes used for acceptance. The resulting evidence shows that representational necessity is not determined by the existence of hidden provenance/support structure alone. It is indexed by the future operations that can make the distinction behaviorally consequential.

This motivates the contract-relative formulation used throughout the paper:

\[
\text{state difference}
\not\Rightarrow
\text{representational necessity}.
\]

Necessity requires a registered continuation in which the distinction changes native behavior.

## 4.4 Natural version-history evidence

Git provides a carrier in which current content and historical state are natively separated.

In the accepted G5 validation bank, 48 natural commit pairs have identical current trees and face the same 12-target merge panel. Two pairs require separation under at least one registered merge; 46 remain behaviorally equivalent under the complete panel.

A target-ancestry representation exactly matches this finite one-step partition.

The result supplies two boundaries at once.

First, equal current content does not guarantee equal future merge behavior.

Second, different histories do not automatically require distinct representations: most registered same-tree pairs in the held-out bank remain equivalent under the frozen merge contract.

We therefore use Git as natural evidence for **contract-relative historical relevance**, not for the stronger claim that history is intrinsically part of computational identity.

The prospective depth-two Git extension is reported only if its executable-carrier reconstruction and independent replay complete successfully; it is not required for the first-order claim.

## 4.5 Learned persistent-state evidence

The learned carrier supplies an important negative control before a positive witness.

In GRACE L1b, 64 learned states produce 224 pairs that collide under the registered current interface. The complete frozen panel contains four first-step actions and all 16 ordered second-step action pairs.

No pair separates at depth one, and no pair separates at depth two:

\[
H0\to H1=0,
\qquad
H1\to H2=0.
\]

Thus different learned parameter states do not become operationally relevant merely because the horizon is extended.

A separate Finetune fold-0 witness supplies the complementary positive. Two states are equal under the registered current task relation but separate under each of three frozen future edits (dataset IDs 51, 29, and 73). Two fresh reconstructions reproduce both the root collision and the action-level separations.

We treat this as a serious learned first-order witness, not a prevalence result. Because every tested future action separates the pair, it does not by itself establish selective or delayed compositional activation.

## 4.6 First-order conclusion

Across the three carrier types, the same principle survives while the native semantics differ:

\[
\boxed{
\text{representational necessity is indexed by registered continuation, not by hidden difference alone.}
}
\]

The relational carrier then allows the stronger constructive question: can the operation contract itself tell us which distinctions to keep?


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


### Proposition 1 — soundness of one-step contract gating

Consider a shared base graph \(G\), a currently redundant augmented edge \(e=(u,v)\) with \((u,v)\in TC(G)\), and a registered singleton-deletion contract \(A\subseteq E(G)\).

For the augmented state \(G+e\), define

\[
\alpha_A(e)
=
\mathbf 1[
\exists f\in A:
(u,v)\notin TC(G-f)
].
\]

Then:

1. if \(\alpha_A(e)=0\), for every registered deletion \(f\in A\),
   \[
   TC(G-f)=TC((G+e)-f);
   \]
2. if \(\alpha_A(e)=1\), there exists a registered deletion \(f\in A\) such that
   \[
   TC(G-f)\neq TC((G+e)-f).
   \]

**Proof sketch.** If \(\alpha_A(e)=0\), then after every registered deletion \(f\), the base graph still contains a path \(u\leadsto v\). Adding the direct edge \(e=(u,v)\) therefore introduces no new reachability relation beyond those already implied transitively; the two closures are equal. If \(\alpha_A(e)=1\), choose \(f\) for which \(u\not\leadsto v\) in \(G-f\). In \((G+e)-f\), the asserted edge \(e\) remains and directly restores \(u\leadsto v\), so the closures differ. \(\square\)

The proposition proves that the gate is **sound for deciding whether an individual redundant edge is operationally necessary under the frozen singleton-deletion contract**.

It does **not** prove that two distinct active augmented states must remain behaviorally distinct from each other. Exact equality

\[
R_{\rm gate}=O_A
\]

therefore remains an empirical result of R3/R4 native replay rather than a general graph theorem. This boundary is important: the structural certificate predicts which current deltas may be safely omitted, while the observed quotient exactness tests whether the retained active deltas over-refine one another.

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
