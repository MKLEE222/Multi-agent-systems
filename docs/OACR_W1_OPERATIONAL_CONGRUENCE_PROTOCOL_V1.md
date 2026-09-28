# OACR-W1 Protocol v1 — Operational Congruence Refinement Audit

**Date:** 2026-09-28  
**Status:** preregistered first empirical protocol under OACR  
**Carrier:** official GRACE + SCOTUS/BERT  
**GRACE commit:** `f674183f17a995d109e10ee6140d4c3e6d016115`

## 1. Theory-led question

Let a writable representation state be (z), a declared observation family be (mathcal O), and a native write action be (a) with transition operator (Phi_a).

Define registered observational equivalence by

[
z equiv_{mathcal O,epsilon} z'
]

when every registered current read in (mathcal O) has matching full logits within the frozen tolerances.

The central question is whether this observational quotient is a congruence for the native write:

[
z equiv_{mathcal O,epsilon} z'
quadLongrightarrowquad
Phi_a(z) equiv_{mathcal O,epsilon} Phi_a(z')
]

for the same admissible action (a).

A counterexample is an **operational congruence violation**.

This protocol does not claim that observational equivalence should always be a congruence. It asks empirically which additional carrier-native distinctions are needed before the quotient becomes stable under the registered write family.

## 2. Why this is different from the previous R1 claim

The old R1 question was pairwise:

> can two read-matched states have different selective future-write outcomes?

OACR-W1 instead studies the abstraction itself:

1. construct multiple persistent states from different legal write histories;
2. freeze one common non-anchor observation contract;
3. apply the same future native writes to every state;
4. identify violations of action congruence;
5. refine the state abstraction using increasingly rich write-state information;
6. ask which refinement first separates each violating pair.

The outcome is therefore an empirical **refinement ladder**, not merely a collection of edit-interference examples.

## 3. State bank

From one frozen pretrained classifier and one contract-preserving GRACE seed state (z_0):

1. build (N_s) seed writes such that every registered seed obligation remains satisfied;
2. freeze a natural error bank before inspecting anchor outcomes;
3. choose at most one anchor from each native GRACE route mode:
   - `reuse_same_label`
   - `expand_same_label`
   - `add_conflict_split`
   - `add_far`;
4. independently apply each anchor to the same base snapshot (z_0);
5. retain only anchor states for which:
   - the anchor target is realized;
   - all common seed obligations remain satisfied.

The state bank is

[
mathcal Z = {z_0,z_{a_1},ldots,z_{a_m}}.
]

Anchor-specific targets are **not** part of the common observation contract because they intentionally distinguish the histories.

## 4. Frozen common observation family

Before any anchor outcome is inspected, freeze:

[
mathcal O
=
P_{mathrm{seed}}
cup
F_{mathrm{future}}
cup
S_{mathrm{sentinel}},
]

where:

- (P_{mathrm{seed}}) are common protected seed obligations;
- (F_{mathrm{future}}) are the same future write candidates that will later be applied to every state;
- (S_{mathrm{sentinel}}) is a deterministic set of non-anchor SCOTUS examples.

For every item in (mathcal O), record full logits, probabilities, prediction, target margin, and cross entropy.

Frozen read tolerances:

[
mathrm{atol}=10^{-6},qquad
mathrm{rtol}=10^{-5}.
]

The phrase **read matched** always means this finite registered family, never universal equality on all inputs.

## 5. Common future action family

Select future actions from the pre-anchor error bank by a deterministic, outcome-blind round-robin over their route modes.

For each action (ainmathcal A):

- use exactly the same target example in every state;
- use the same registered GRACE budget;
- use the same branch RNG seed in every state;
- treat an already satisfied target as a zero-write realization;
- otherwise execute the official native GRACE edit.

Primary common protected contract: (P_{mathrm{seed}}).

Secondary branch-local contract: (P_{mathrm{seed}}) plus that state's committed anchor, if any. The secondary contract is descriptive because different anchor states have different local commitments.

## 6. Primary outcome

For every pair ((z_i,z_j)) and action (a), compare the same registered observation family before and after the action.

A primary congruence violation is:

[
z_i equiv_{mathcal O,epsilon} z_j
]

but

[
Phi_a(z_i) 
otequiv_{mathcal O,epsilon} Phi_a(z_j).
]

Record the maximum post-write logit (L_infty) difference and which registered reads changed.

### Strong selective subtype

A stronger subtype additionally requires:

1. future target realized in both branches;
2. common protected seed obligations are all preserved in one branch and not the other.

This retains the previous selective-write witness as one interpretable subtype of the more general congruence failure.

## 7. Refinement ladder

For every state-action pair construct four registered abstractions.

### A0 — READ only

[
A_0(z,a)=F_{mathcal O}(z).
]

Two states collide at A0 iff their registered pre-action read families match.

### A1 — READ + native write mode

[
A_1(z,a)=
ig(A_0(z,a),,m_z(a)ig),
]

where (m_z(a)) is GRACE's iteration-0 route mode.

### A2 — READ + discrete routing state

Add:

- action nearest-key identity;
- action coverage bit;
- same-label bit;
- key count;
- protected queries' ((	ext{nearest key},	ext{covered})) signatures.

### A3 — READ + projected structural effect

Add the exact iteration-0 projection signature:

- changed protected indices;
- lost-support indices;
- gained-support indices;
- projected future trained value row;
- protected queries using that row;
- preservation-certificate bit.

A violation at level (A_k) means the registered abstraction still identifies two states whose post-write registered observations differ.

For every A0 violation, report the **first refinement level that separates the pair**. If A3 still collides, the current structural certificate is insufficient and the missing distinction becomes the next research target.

No claim of global sufficiency is permitted from absence of A3 violations in this finite audit.

## 8. Anti-confounds and hard failures

The run is invalid for interpretation if any of the following occurs:

1. wrong GRACE commit;
2. carrier asset manifest differs across branches;
3. observation changes the persistent adapter state;
4. restoring a snapshot changes its state hash;
5. same state + same action + same RNG seed is not reproducible in the duplicate-branch control;
6. anchor succeeds but violates the common seed contract — that anchor state is excluded;
7. query capture or route audit mutates state;
8. future action pools differ between states.

## 9. Registered first-run parameters

The first run is intentionally small and diagnostic:

- seed edits: 4
- seed scan limit: 512
- candidate bank: 48
- anchors per native mode: 1
- future actions: 8
- sentinel reads: 16
- global seed: 73
- device: CPU
- read tolerances: (10^{-6},10^{-5})

The goal is not prevalence estimation. It is to validate the theory-led object and determine whether the refinement ladder yields interpretable counterexamples on the official learned carrier.

## 10. Interpretation rules

- **A0 violation only:** current registered READ equivalence is not action-congruent.
- **A0 + A1 violation:** native mode label alone is insufficient.
- **A0 + A1 + A2 violation:** discrete route identity/coverage is insufficient.
- **A0 + A1 + A2 + A3 violation:** the current structural projection/certificate omits a write-relevant distinction.
- **A0 violations all separated by A3:** A3 is a carrier-specific candidate refinement for this registered run, not a theorem of representation adequacy.
- **No A0 collisions:** the observation family is too discriminating for this state bank; expand the state bank before weakening the observation contract.
- **A0 collisions but no violations:** this run provides no counterexample; expand actions/histories without changing the definition post hoc.

## 11. Relation to mature theory

This experiment is explicitly modeled after the mature distinction between observational equivalence and congruence under operations, and after strong-preservation/minimal-refinement ideas from abstract interpretation.

The empirical novelty target is not those general facts. It is whether and how those requirements manifest in a learned, persistent, native-write representation and which internal distinctions are empirically necessary to make the registered quotient stable under real writes.
