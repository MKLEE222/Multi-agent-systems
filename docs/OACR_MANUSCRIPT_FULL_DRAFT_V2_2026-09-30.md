# Native-Contract Adequacy Auditing and Bidirectional Repair of Persistent Computational Representations

# Abstract

A persistent computational representation must support future state-changing operations, not only reproduce the present observation. We study adequacy relative to a prospectively registered native continuation contract. On a frozen state bank, the contract induces an operational partition; conditional entropies measure distinctions omitted by an implemented representation and distinctions it retains without operational effect. Exact relational and natural Git carriers exhibit opposite failures of present equality and full internal identity under finite shared contracts; learned editing provides additional positive and negative continuation tests. The main constructive result uses a contract-derived certificate to repair a relational representation from either direction. On a fresh 272-state bank with 64 deletion actions, additive and subtractive repairs reach the same 23-class operational quotient, retain 22 of 271 candidate deltas, and reproduce all 17,408 native outcomes. A second, fixed-interpreter qualification carrier isolates delayed demand: removing a continuation guard preserves one-step behavior but creates 12 depth-two mismatches; a relevant one-rule repair closes them, while an equal-size sham rule does not. These results provide a native-execution workflow for auditing and repairing persistent representations under declared finite contracts.

**Keywords:** representation adequacy; operational equivalence; state abstraction; native transformation; bidirectional repair; continuation semantics

---

# 1. Introduction

Persistent computational objects are expected to survive change. A graph may lose an asserted edge, a repository may merge another history, and a learned model may receive another edit. The representation used at the present state must carry enough information for those later operations to behave as required. Present equality alone cannot establish that property: two states with the same current observation may respond differently to a common operation. Internal differences can also persist without changing any operation the system is required to support.

This paper asks a concrete representation-design question: **which distinctions must a persistent computational representation retain to support a registered family of future native operations?** The answer depends on the continuation contract. A representation may omit distinctions the contract needs, or store distinctions the contract never uses. Both errors matter when the goal is a representation that remains useful after transformation.

Behavioral equivalence and operator-relative preservation provide the formal foundation for this question [1–4]. Knowledge compilation likewise evaluates representations by the queries and transformations they support [5]. We use these foundations to audit implemented representations under prospectively registered native operation contracts. For a frozen state bank, let \(P_R\) be the partition induced by representation \(R\), and let \(O_{\mathcal C}\) be the partition induced by all observations and operations in contract \(\mathcal C\). Under a full-support reference distribution \(\mu\), the two directional gaps are

\[
U_\mu(R;\mathcal C)=H_\mu(O_{\mathcal C}\mid R),
\qquad
E_\mu(R;\mathcal C)=H_\mu(R\mid O_{\mathcal C}).
\]

\(U_\mu\) measures omitted operational distinctions; \(E_\mu\) measures retained distinctions with no effect under the registered contract. Exactness on the frozen bank requires both to vanish. The empirical configuration that motivates the study is a strict intermediate quotient:

\[
P_{R_{\rm current}}\prec O_{\mathcal C}\prec P_{R_{\rm full}},
\]

where \(\prec\) denotes strict coarsening. Current observation merges states that a future operation separates, while complete internal identity separates states whose registered continuation is identical.

We call the audit and repair workflow **Operational Adequacy of Computational Representations (OACR)**. The workflow registers the state bank and operation contract before outcomes are inspected, executes native transformations, measures the two adequacy gaps, derives a repair certificate within a frozen information boundary, and accepts a modified representation after independent native replay. Pair-specific action selection, outcome-driven feature choice, and producer-only verification are controlled explicitly.

Exact relational carriers provide the principal constructive evidence. In a developmental bank and a prospectively frozen fresh bank, 272 states have identical current transitive closure and face the same 64 base-edge deletions. The native operational partitions contain 101 and 23 classes, respectively. In the fresh bank, a contract-derived gate retains 22 active redundant-edge deltas and omits 249 inactive deltas. Additive repair from the one-block current representation and subtractive repair from full asserted-edge identity reach the same 23-block quotient. The repaired representation has \(U_\mu=E_\mu=0\) and reproduces all 17,408 registered native state-action outcomes.

Natural Git history and learned parametric editing test the first-order claim in different systems. A held-out bank of 48 same-tree Git pairs under one frozen 12-target merge panel contains two behaviorally separated pairs and 46 equivalent pairs. A learned Finetune pair has equal registered present behavior and separates under three frozen future edits, while a separate GRACE bank yields 224 present-collision pairs that remain equivalent through its complete depth-two panel. These results bound the claim: hidden history or parameters can matter, and their mere existence does not establish necessity.

Composition adds a second question. In fixed-domain relational deletion, every registered redundant-edge distinction is either active at depth one or remains inert under the frozen action universe. In a prospectively frozen dynamic-qualification family, a shared first transformation changes the later legality interface. Five representation forms run through one fixed compiler and native executor. Removing the relevant route guard preserves the complete one-step interface yet produces 12 depth-two mismatches. A one-rule contract-relevant repair closes all 12; an equal-size sham rule leaves all 12.

The contributions are: (i) a directional audit of implemented representations against registered native continuation contracts; (ii) same-contract evidence across relational, version-history, and learned carriers; (iii) certificate-constrained additive and subtractive representation repair with exhaustive native closure verification; and (iv) a bounded account of delayed demand when transformations change the continuation interface. The results concern finite registered contracts and their declared state banks. They establish an actionable representation methodology without requiring a universal state encoding.

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

### Proposition 0 — exactness of the directional information gaps

Let \(X_f\subset X\) be a finite registered state bank and let \(\mu\) have full support on \(X_f\). Let \(R\) and \(O_{\mathcal C}\) denote the random variables induced by the representation partition and operational partition on \(X_f\).

Then:

\[
U_\mu(R;\mathcal C)=0
\]

if and only if \(O_{\mathcal C}\) is a deterministic function of \(R\) on \(X_f\), equivalently the representation partition is at least as fine as the operational partition.

Likewise,

\[
E_\mu(R;\mathcal C)=0
\]

if and only if \(R\) is a deterministic function of \(O_{\mathcal C}\), equivalently the representation partition is no finer than the operational partition.

Therefore, under full support,

\[
U_\mu(R;\mathcal C)=E_\mu(R;\mathcal C)=0
\]

if and only if the two partitions are identical on the registered bank:

\[
P_R=O_{\mathcal C}.
\]

In all finite-bank experiments in this paper, \(\mu\) is the empirical uniform distribution and therefore has full support.

**Proof.** Conditional entropy \(H(Y\mid X)=0\) on a finite full-support space if and only if \(Y\) is a deterministic function of \(X\). Apply this once in each direction. Mutual functional determination is equivalent to equality of the induced equivalence classes. \(\square\)



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

OACR uses existing mathematics of behavioral equivalence and state abstraction. Strong preservation connects exact satisfaction of a chosen language with completeness of an abstraction and admits operator-relative refinement [1,2]. Representation independence studies when internal implementations remain indistinguishable through an abstract interface, including interfaces with mutable local state [3,4]. Knowledge compilation compares the capabilities and succinctness of representation languages under supported queries and transformations [5].

The present study starts from an implemented persistent representation and a native transformation contract. Its empirical object is the gap between the partition already stored by that implementation and the quotient induced by a registered continuation. This starting point creates two measurable design obligations: recover contract-required distinctions and remove distinctions whose persistence the contract cannot justify. The repair acts on the representation used by the carrier, while the native executor and operation contract remain fixed. Sections 3–6 test those obligations with frozen state banks, independent verification, and native execution.

Depth-indexed continuation equivalence also has established precedents in transition-system semantics and predictive-state constructions. Here it serves to identify when a representation adequate for immediate operations fails after an operation updates the interface governing a later one.

## 2.7 Certificate-constrained representation repair

An adequacy audit and a representation repair are related but distinct objects.

Let the audit operator return a directional deficit record

\[
\mathsf{Audit}_{\mathcal C,\mu}(R)
=
D
=
(
U_\mu(R;\mathcal C),
E_\mu(R;\mathcal C),
\mathcal W_U,
\mathcal W_E
),
\]

where \(\mathcal W_U\) and \(\mathcal W_E\) denote registered under- and over-refinement witnesses when available.

The audit does not by itself synthesize a repair. Instead, repair construction is constrained by a frozen information boundary

\[
\mathcal I_{\rm repair},
\]

which specifies exactly which carrier structure, contract metadata, static dependency information, and audit diagnostics may be used.

A carrier-native repair certificate is

\[
\kappa
\in
\mathcal K(
\mathcal C,
D,
\mathcal I_{\rm repair}
).
\]

The representation intervention is then written

\[
\Phi_{\mathcal C,\kappa}:R\mapsto R'.
\]

This notation deliberately separates three stages:

\[
(R,\mathcal C)
\xrightarrow{\rm audit}
D,
\]

\[
(\mathcal C,D,\mathcal I_{\rm repair})
\xrightarrow{\rm certificate}
\kappa,
\]

and

\[
(R,\kappa)
\xrightarrow{\Phi}
R'.
\]

A repair is accepted only after the same registered native continuation contract is replayed on \(R'\).

### Repair obligations

For the finite exact-repair setting used in the main constructive results, four obligations apply.

**O1 — closure.**

\[
U_\mu(R';\mathcal C)=0.
\]

The repaired representation contains every distinction required by the registered continuation.

**O2 — no excess.**

When exact finite repair is claimed,

\[
E_\mu(R';\mathcal C)=0.
\]

If exactness is not achieved, the residual directional error must be reported rather than hidden behind the word "repair."

**O3 — native-semantics invariance.**

The concrete executor and registered continuation contract remain fixed:

\[
\mathcal C'=\mathcal C.
\]

Only the representation or the representation object consumed by a fixed interpreter may change.

**O4 — frozen information boundary.**

The repair constructor may use only information declared in

\[
\mathcal I_{\rm repair}.
\]

Held-out native outcomes prohibited by the protocol may not be inspected to choose \(\kappa\).

These obligations distinguish representation correction from changing the task until the representation passes.

### Bidirectional correction

Repair is not synonymous with refinement.

If

\[
R_{\rm current}
\prec
O_{\mathcal C}
\prec
R_{\rm full},
\]

then the same contract can induce two representation corrections:

\[
\Phi_{\mathcal C,\kappa}^{+}
:
R_{\rm current}
\mapsto
R',
\]

which adds missing distinctions, and

\[
\Phi_{\mathcal C,\kappa}^{-}
:
R_{\rm full}
\mapsto
R',
\]

which removes distinctions the contract does not justify.

The strongest finite-bank result is therefore not merely "more precision":

\[
\boxed{
\Phi_{\mathcal C,\kappa}^{+}(R_{\rm current})
=
\Phi_{\mathcal C,\kappa}^{-}(R_{\rm full})
=
O_{\mathcal C}.
}
\]

We call this **bidirectional contract repair**.


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

The present manuscript uses the accepted one-step G5 validation result. A separate depth-two analysis is excluded from the accepted evidence.

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

**Table 1. Accepted carrier evidence under registered native contracts.** Each denominator and equivalence statement refers to its own frozen bank; rows are not pooled into a cross-carrier effect estimate.

| Carrier | Registered bank and contract | Accepted result | Evidential role |
| --- | --- | --- | --- |
| R3 relational | 272 states; shared 64 deletions | 101 operational classes; current \(U=3.39144,E=0\); full \(U=0,E=4.69602\) | Developmental exact audit and repair |
| R4 relational | 272 fresh states; shared 64 deletions | 23 operational classes; current \(U=0.76597,E=0\); full \(U=0,E=7.32149\) | Prospective exact confirmation |
| WACT-R | Five included roots; frozen deletion protocol | 80/80 strict witnesses; zero native causal failures | Action-specific activation |
| Git G5 | 48 held-out same-tree pairs; shared 12-target merge panel | 2 pairs separated; 46 equivalent | Natural finite-contract history boundary |
| GRACE L1b | 64 states; four H1 actions and 16 ordered H2 action pairs | 224 present-collision pairs; zero H1 or H2 separation | Learned negative boundary |
| Finetune fold 0 | One accepted present-collision pair; three frozen future edits | All three edits separate; two fresh reconstructions agree | Learned first-order positive witness |

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

**Table 2. Exact relational audit and contract-gated repair.** Bits use the empirical uniform measure on the frozen state bank. Delta reduction counts retained per-state records in the declared shared-base encoding.

| Carrier | Current blocks | Operational blocks | Full blocks | Active / inactive deltas | Gated \(U,E\) | Native replay | Retained deltas |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| R3 developmental | 1 | 101 | 272 | 100 / 171 | 0, 0 | 17,408 / 17,408 | 100 / 271 |
| R4 fresh building | 1 | 23 | 272 | 22 / 249 | 0, 0 | 17,408 / 17,408 | 22 / 271 |

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


## 5.6 Bidirectional contract repair on the fresh carrier

The accepted R4-building artifact allows the same target representation to be reached from opposite representation errors.

The frozen active-delta certificate contains exactly 22 augmented states. The remaining 249 augmented deltas are contract-inactive.

Starting from the current-closure representation, no per-state delta identity is retained. The additive correction is

\[
\Phi_{\mathcal C,\kappa}^{+}(R_{\rm current})
=
R_{\rm gate},
\]

implemented by adding exactly the 22 contract-active per-state deltas:

\[
0
\rightarrow
22
\text{ retained delta records}.
\]

Starting from full asserted identity, all 271 augmented deltas are retained. The subtractive correction is

\[
\Phi_{\mathcal C,\kappa}^{-}(R_{\rm full})
=
R_{\rm gate},
\]

implemented by removing the 249 contract-inactive deltas:

\[
271
\rightarrow
22
\text{ retained delta records}.
\]

Both interventions therefore terminate at the same representation:

\[
\boxed{
\Phi_{\mathcal C,\kappa}^{+}(R_{\rm current})
=
\Phi_{\mathcal C,\kappa}^{-}(R_{\rm full})
=
R_{\rm gate}
=
O_{\mathcal C}.
}
\]

The common target has 23 blocks and satisfies

\[
U_\mu=E_\mu=0.
\]

The accepted original and compressed outcome matrices have the same SHA-256 identity, and all

\[
17{,}408
\]

registered native state-action cells replay with zero mismatch.

The exact repair manifest is frozen independently of manuscript prose and identifies the 22 additive deltas, the 249-delta subtractive complement, the source artifact, and the registered state/action manifests.

This bidirectional result is important for positioning. OACR does not assume that representation improvement means monotonically adding precision. The same continuation contract can require adding distinctions to a coarse representation and deleting distinctions from an over-specified one.


## 5.7 Why full state is not the default solution

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

## 5.8 Limits of the constructive result

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



---

# 6. When composition creates new representational demand

## 6.1 Longer horizon is not the mechanism

A natural hypothesis is that hidden distinctions become more likely to matter simply because a representation is exposed to longer operation sequences.

The registered evidence rejects that explanation as a general account.

In the developmental R3 relational deletion carrier, every redundant distinction has one of two registered-action cut depths:

\[
d_A(e)=1
\]

or

\[
d_A(e)=\infty.
\]

One hundred distinctions are activated by at least one single registered deletion; 171 remain redundant even after removing the entire frozen 64-action universe.

The prospectively frozen R4-building carrier has the same qualitative structure:

- 22 distinctions with \(d_A=1\);
- 249 distinctions with \(d_A=\infty\);
- no distinction with \(d_A=2\).

Thus, in these carriers, composing registered deletions does not create a new layer of representational demand beyond WRITE.

The learned GRACE L1b control gives a separate negative boundary. Across 224 current collision pairs, no registered separation appears at depth one or under the complete registered depth-two panel.

Together these results motivate a stricter COMPOSE question:

> What must change between the first and second transformation for a distinction that is irrelevant to every registered immediate continuation to become necessary later?

## 6.2 Continuation interfaces

We represent the carrier-specific continuation interface at state \(x\) as

\[
\Gamma_x(a).
\]

Depending on the carrier, \(\Gamma_x(a)\) may contain:

- legality or qualification;
- enabledness or materializability;
- registered outcome semantics;
- invariant obligations;
- viability or recoverability;
- update-response behavior.

An operation acts on both the persistent state and the interface governing future operations:

\[
(x,\Gamma_x)
\xrightarrow{a}
(x',\Gamma_{x'}).
\]

The important distinction is therefore between:

1. composing more operations from a fixed domain whose semantics do not change; and
2. applying an operation that changes how later operations are qualified or interpreted.

A representation may be exact for the first step while failing to carry enough information to update \(\Gamma\).

## 6.3 Controlled delayed legality failure

The existing SQEC multistep-legality audit provides a controlled example.

FULL retains state-dependent observation preconditions.

PROJECTED removes only those preconditions while preserving:

- the root state;
- action transitions;
- observation transitions;
- costs;
- outcome probabilities;
- horizon.

At the root, the guarded observation route is open. FULL and PROJECTED therefore expose the same immediate registered event set, and every common first-step event has the same immediate transition semantics:

\[
\Gamma_1^{FULL}(x_0)
=
\Gamma_1^{PROJECTED}(x_0).
\]

Now execute the shared action

\[
a_1=\texttt{commit-task}.
\]

In both systems, the action closes the observation-route coordinate.

The difference appears only when the later observation is considered. FULL retained the rule that the observation is legal only while the route is ACTION_OPEN or SATISFIED. PROJECTED omitted that rule.

Hence:

\[
\Gamma_2^{FULL}(x_0)
\neq
\Gamma_2^{PROJECTED}(x_0).
\]

The omitted distinction is dormant under the immediate interface and becomes necessary only after the first transformation changes the guarded state coordinate.

The original SQEC decision audit also supplies a consequential replay: the projected policy commits before observation, then encounters an illegal observation when replayed in the full system, producing the registered failure-loss consequence. We treat that result as retrospective controlled mechanism evidence rather than a prospective OACR discovery.

## 6.4 Guard-latency interpretation

The controlled example can be summarized by a simple condition.

Suppose two representations agree on:

- which registered first actions are enabled;
- the immediate outcome of every registered first action.

Let a common first action \(a_1\) take both systems to corresponding successor states.

If a later action \(a_2\) has different qualification after that shared transition,

\[
g_F(T_F(x,a_1),a_2)
\neq
g_P(T_P(x,a_1),a_2),
\]

then one-step adequacy does not imply depth-two adequacy.

The mathematical fact itself is elementary and is not claimed as a novel theorem.

Its role is diagnostic:

> a representation can preserve the present continuation interface while omitting the rule needed to update that interface after transformation.

This is qualitatively different from merely accumulating more fixed-domain operations.

## 6.5 Fixed-interpreter matched representation repair

The first SQEC confirmation established delayed guard necessity and successful repair, but a stricter question remains: was the intervention genuinely a representation repair, or did it modify the transition semantics directly?

We therefore froze a new 12-variant family before execution and separated the transition skeleton from an explicit continuation-representation object.

For every variant, the following remain fixed:

- typed state model;
- state-transition skeleton;
- event alphabet;
- complete sequence bank of lengths one and two;
- one representation compiler;
- the native executor
  \[
  \texttt{apply\_qualification\_event}.
  \]

The skeleton itself contains no observation preconditions.

Only an immutable representation object varies. The fixed compiler maps that representation into native event preconditions before execution.

We compare five representation forms.

**FULL** stores two separate route-guard rules, one for each observation outcome.

**B0** stores no observation guard.

**B1** restores the two separate rules.

**B2** stores one shared canonical route guard applying to both observation outcomes.

**B3** stores one same-size sham rule applying to both observations but allowing every status of an irrelevant task coordinate.

Thus:

\[
cost(B2)=cost(B3)=1.
\]

Across the complete one-step contract, every baseline remains equivalent to FULL:

\[
mismatch_1(FULL,B_i)=0
\]

for all

\[
i\in\{0,1,2,3\}.
\]

At depth two, the preregistered outcomes are:

\[
\boxed{
mismatch_2(FULL,B0)=12,
}
\]

\[
\boxed{
mismatch_{\le2}(FULL,B1)=0,
}
\]

\[
\boxed{
mismatch_{\le2}(FULL,B2)=0,
}
\]

and:

\[
\boxed{
mismatch_2(FULL,B3)=12.
}
\]

The six preregistered delayed-guard positive variants account for the 12 B0/B3 mismatches; six no-divergence controls produce none.

An independent verifier reconstructs all 12 variants, all five representation objects, all 20 registered sequences per variant, and every native signature. It reports zero verifier mismatches and zero producer/verifier matrix mismatches.

The comparison isolates the representation-level cause.

Adding arbitrary representation structure is insufficient:

\[
B3\not\equiv_{\le2}FULL.
\]

Adding the contract-relevant continuation coordinate is sufficient:

\[
B2\equiv_{\le2}FULL.
\]

Because B2 and B3 have equal stored-rule cardinality, the result cannot be explained by representation size alone.

Together with the relational result, this gives the paper's constructive workflow:

\[
(R,\mathcal C)
\xrightarrow{\rm audit}
D
\]

\[
(\mathcal C,D,\mathcal I_{\rm repair})
\xrightarrow{\rm certificate}
\kappa
\]

\[
(R,\kappa)
\xrightarrow{\Phi}
R'
\]

followed by independent replay under the unchanged native contract.


**Table 3. Fixed-interpreter matched continuation repairs.** All 12 prospectively frozen variants use the same transition skeleton family, representation compiler, native executor, four-event alphabet, and complete 20-sequence contract per variant. Cost counts stored guard rules.

| Representation | Guard content | Cost | H1 mismatches | H2 mismatches |
| --- | --- | ---: | ---: | ---: |
| FULL | Separate route guards | 2 | 0 | 0 |
| B0 | No route guard | 0 | 0 | 12 |
| B1 | Restored separate guards | 2 | 0 | 0 |
| B2 | Shared contract-relevant guard | 1 | 0 | 0 |
| B3 | Equal-cost sham guard | 1 | 0 | 12 |

## 6.6 Composition conclusion

The evidence supports a bounded mechanism claim rather than a general depth law.

The accepted comparison has four parts:

- fixed-domain relational composition does not create delayed demand;
- a learned fixed-panel control remains equivalent through depth two;
- controlled dynamic qualification provides an exact delayed failure when a first action changes a later guard;
- fresh fixed-interpreter matched repairs show that the registered continuation rule, rather than rule count alone, closes the delayed interface.

The evidence supports a bounded mechanism statement: **increasing action depth alone does not force additional representational distinctions; demand can arise when a transformation changes the continuation interface governing later operations.** Dynamic qualification provides one exact mechanism within this scope.


---

# 7. Related work and theory inheritance

## 7.1 Strong preservation and abstract interpretation

Ranzato and Tapparo connect strong preservation with complete abstract interpretation and formulate minimal refinement relative to a specification language or operator family [1,2]. This gives OACR its nearest formal predecessor: adequacy is relative to what an abstraction must preserve. Our experiments take an existing representation and a prospectively registered native mutation contract as inputs, measure omissions and excess against the resulting finite operational quotient, and test repairs in the carrier's executor. The contract-gated graph result is a concrete realization under these empirical controls.

## 7.2 Representation independence and knowledge compilation

Representation independence formalizes when distinct implementations remain indistinguishable through an abstract interface [3]. State-dependent logical relations extend this perspective to mutable local state [4]. OACR uses the same operation-relative insight to audit the distinctions retained by one persistent representation across a frozen state bank. Its bidirectional gaps describe both missing distinctions and unnecessary ones.

Knowledge compilation maps representation languages against their supported queries, transformations, and succinctness [5]. OACR evaluates concrete persistent-state representations under native mutations. Its compression figures count retained per-state delta records in a declared encoding; they are not language-wide succinctness claims.

## 7.3 Refinement and automated repair

Counterexample-guided abstraction refinement uses a failure to refine a verifier's abstraction and repeat verification [6]. Automated program repair modifies candidate code and validates changes by tests or execution [7]. OACR shares the broad diagnose–modify–verify pattern. Its intervention target is the deployed state representation: on the accepted relational carrier, a certificate adds missing deltas from a coarse representation or removes inactive deltas from full identity, with both paths reaching the same finite quotient. The native executor and contract stay fixed. The dynamic-qualification experiment further compares a contract-relevant repair with an equal-size sham representation.

## 7.4 Sequential learned editing

Sequential model-editing studies already document knowledge attenuation and interference [8–10]. Behavioral reversibility after edit–revert procedures has also been studied [11]. The learned carrier in this paper tests a narrower contract-relative question: whether states that satisfy a frozen present-equivalence relation respond equally to the same future native edit. The accepted Finetune result is a single first-order witness; the GRACE panel supplies a complete negative boundary for its registered state bank and horizon. A broader recovered-present experiment is outside the accepted results reported here.

## 7.5 Version history and dynamic qualification

Git exposes content, ancestry, and merge behavior as separate native objects. G5 uses these facilities as a natural carrier: same-tree commit pairs face one held-out merge panel, yielding both required and unnecessary historical distinctions. The result is conditional on that finite target panel.

Dynamic legality also appears in planning, typestate, capabilities, and transition-system semantics. The SQEC carrier isolates a representation-level obligation: after a shared transformation updates a route coordinate, the representation must preserve the guard governing a later observation. A fixed compiler and executor, full and projected baselines, and an equal-size sham control locate the cause in the stored continuation rule.

Taken together, these neighboring literatures supply the formal vocabulary and several known mechanisms. OACR's contribution is the measured, native-contract path from an implemented representation through directional audit to verified structural repair across distinct carriers.

# 8. Limits and scope

OACR is a contract-relative audit framework, not a claim that one representation is intrinsically correct independent of its use.

First, every empirical quotient in this paper is finite and registered. The operational partition \(O_{\mathcal C}\) is induced by a declared observation/action/horizon contract on a frozen state bank. A representation that is exact for one contract may under-refine a richer future contract or over-refine a narrower one. We therefore do not interpret \(U_\mu=E_\mu=0\) as universal state minimality.

Second, the constructive graph result is structurally specific. Proposition 1 establishes when an individual currently redundant edge can be omitted safely under a singleton-deletion contract. The observed equality

\[
R_{\rm gate}=O_{\mathcal C}
\]

on R3 and R4 additionally requires the empirical fact that the retained active deltas do not over-refine one another. We do not promote that empirical exactness into a general graph theorem.

Third, cross-carrier evidence is intentionally heterogeneous. The relational carrier supports complete finite operational partitions and exact \(U_\mu/E_\mu\) accounting. The Git and learned carriers supply natural or high-cost native witnesses under smaller registered banks. The common claim is therefore a shared **audit object**, not equal statistical coverage or an identical state ontology across domains.

Fourth, the dynamic-qualification repair is controlled. It prospectively confirms delayed continuation failure and repair under a typed state-dependent guard, but it does not establish natural prevalence of such failures. The earlier stochastic SQEC result supplies a decision consequence; the fresh repair family supplies confirmatory continuation closure. Neither should be read as evidence that qualification is the only mechanism capable of producing COMPOSE effects.

Fifth, learned evidence remains contract- and model-specific. Sequential editing, path dependence, and reversibility are established research topics. The learned experiment in this paper is used only to test whether a preregistered present-recovery relation is closed under a later common native update. No claim is made about universal edit irreversibility, machine unlearning, or model-wide memory.

Sixth, the natural Git result is limited to the accepted G5 one-step merge panel. The selected 12 targets and 48 held-out pairs do not establish a general minimal representation of Git history.

Finally, the broader research program motivating OACR concerns persistent participants whose history, authority, membership, or identity may change under copy, merge, rollback, and related transformations. The present paper establishes a computational representation methodology. It does not by itself establish cultural, institutional, or personal continuity criteria.

---

# 9. Conclusion

A representation of a persistent computational object is not only a description of what the object is now. It is also a state from which the object must continue.

This paper operationalizes that requirement through registered native continuation contracts. Relative to such a contract, an implemented representation can fail in two directions: it can omit distinctions that future operations require, or preserve internal distinctions that never affect the registered continuation. The resulting target is neither static fidelity nor complete internal identity, but the intermediate operational quotient required by the contract.

The exact relational carriers make this structure explicit:

\[
R_{\rm current}
\prec
O_{\mathcal C}
\prec
R_{\rm full}.
\]

More importantly, the audit changes representation design. A contract-derived gate retains only currently redundant deltas whose redundancy can be broken by a registered deletion. On the prospectively frozen building carrier, the transform moves from one current block and 272 full-identity blocks to the exact 23-class operational quotient, reproduces all 17,408 native outcomes, and retains 22 of 271 declared deltas.

The continuation view also clarifies what composition adds. Longer action sequences do not automatically expose more hidden state: the registered relational deletion carriers and learned GRACE control provide direct counterexamples. New representational demand can instead arise when a transformation changes the continuation interface governing later transformations. In a fresh prospectively frozen dynamic-qualification family, five representation forms are interpreted by the same compiler and native executor. Removing the route guard produces no one-step mismatch but 12 depth-two mismatches. A one-rule contract-relevant repair restores the complete matrix, while a same-size sham rule leaves all 12 mismatches intact.

These results suggest a practical criterion for persistent computational representations:

> **Preserve the distinctions required to keep the registered continuation closed, and no more than the contract can justify.**

The criterion inherits its formal substrate from behavioral equivalence, strong preservation, and representation independence. OACR contributes the empirical and constructive workflow needed to apply that substrate to implemented state representations under native transformations: register the continuation contract, audit omission and excess, derive a certificate within a frozen information boundary, add or remove representation structure while leaving native semantics fixed, and accept the correction only after independent native closure verification.


---

# References

1. Ranzato, F., and Tapparo, F. “Strong Preservation as Completeness in Abstract Interpretation.” *Programming Languages and Systems (ESOP 2004)*, LNCS 2986, 18–32 (2004). [doi:10.1007/978-3-540-24725-8_3](https://doi.org/10.1007/978-3-540-24725-8_3).
2. Ranzato, F., and Tapparo, F. “Generalized Strong Preservation by Abstract Interpretation.” *Journal of Logic and Computation* 17(1), 157–197 (2007). [doi:10.1093/logcom/exl035](https://doi.org/10.1093/logcom/exl035).
3. Mitchell, J. C. “Representation Independence and Data Abstraction.” *POPL 1986*, 263–276 (1986). [doi:10.1145/512644.512669](https://doi.org/10.1145/512644.512669).
4. Ahmed, A., Dreyer, D., and Rossberg, A. “State-Dependent Representation Independence.” *POPL 2009*, 340–353 (2009). [doi:10.1145/1480881.1480925](https://doi.org/10.1145/1480881.1480925).
5. Darwiche, A., and Marquis, P. “A Knowledge Compilation Map.” *Journal of Artificial Intelligence Research* 17, 229–264 (2002). [doi:10.1613/JAIR.989](https://doi.org/10.1613/JAIR.989).
6. Clarke, E. M., Grumberg, O., Jha, S., Lu, Y., and Veith, H. “Counterexample-Guided Abstraction Refinement.” *Computer Aided Verification (CAV 2000)*, LNCS 1855, 154–169 (2000). [doi:10.1007/10722167_15](https://doi.org/10.1007/10722167_15).
7. Le Goues, C., Dewey-Vogt, M., Forrest, S., and Weimer, W. “A Systematic Study of Automated Program Repair: Fixing 55 out of 105 Bugs for $8 Each.” *ICSE 2012*, 3–13 (2012). [doi:10.1109/ICSE.2012.6227211](https://doi.org/10.1109/ICSE.2012.6227211).
8. Li, Q., and Chu, X. “Can We Continually Edit Language Models? On the Knowledge Attenuation in Sequential Model Editing.” *Findings of ACL 2024*, 5438–5455 (2024). [doi:10.18653/v1/2024.findings-acl.323](https://doi.org/10.18653/v1/2024.findings-acl.323).
9. Lyu, S. et al. “EvoEdit: Evolving Null-space Alignment for Robust and Efficient Knowledge Editing.” *Findings of ACL 2026*, 1520–1540 (2026). [doi:10.18653/v1/2026.findings-acl.75](https://doi.org/10.18653/v1/2026.findings-acl.75).
10. Zhang, C. et al. “Spectral Characterization and Mitigation of Sequential Knowledge Editing Collapse.” *ACL 2026*, 30009–30032 (2026). [doi:10.18653/v1/2026.acl-long.1384](https://doi.org/10.18653/v1/2026.acl-long.1384).
11. Caddeo, E., Sanguinetti, M., and Atzori, M. “On Reversibility as Language Model Behavioral Property in Parametric Knowledge Editing.” *Applied Sciences* 16(13), 6567 (2026). [doi:10.3390/app16136567](https://doi.org/10.3390/app16136567).
