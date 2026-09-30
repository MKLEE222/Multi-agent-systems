# Native-Contract Audit -> Representation Repair: Cold-Start Review

**Date:** 2026-09-30  
**Mode:** hostile cold-start reviewer reconstruction  
**Question:** Is

\[
\text{native-contract audit}
\rightarrow
\text{representation repair}
\]

already a defensible paper identity, and what remains necessary to make it fully real rather than a post-hoc narrative over heterogeneous experiments?

---

## 1. Cold-start verdict

### Short answer

**The identity is scientifically viable, but the bare two-stage arrow is still under-specified and too close to mature abstraction-refinement / repair paradigms.**

The paper already has enough evidence to support:

\[
\boxed{
\text{native-contract audit}
\rightarrow
\text{certificate-constrained representation intervention}
\rightarrow
\text{native closure verification}
}
\]

in two substrates.

It does **not yet** fully support the stronger reading:

> the audit output itself generically synthesizes a repair.

That distinction must be made explicit.

### Recommended final identity

\[
\boxed{
\textbf{native-contract audit}
\rightarrow
\textbf{certificate-constrained representation repair}
\rightarrow
\textbf{native closure verification}
}
\]

with the secondary slogan:

> audit the distinctions an implemented representation lacks or unnecessarily stores; derive a repair from the frozen continuation contract without changing native semantics; replay the repaired representation under the same contract.

This formulation is both more accurate and more differentiated from CEGAR, strong-preservation refinement, and generic program repair.

---

## 2. What is already genuinely strong

### 2.1 The audit object is real and directional

The paper does not merely ask whether an abstraction is sound.

For a frozen native continuation contract \(\mathcal C\), the implemented representation partition \(P_R\) is compared with the empirical/native operational partition \(O_{\mathcal C}\).

Two distinct defects are measured:

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

Thus the desired representation can lie strictly between current/static fidelity and full identity:

\[
R_{\rm current}
\prec
O_{\mathcal C}
\prec
R_{\rm full}.
\]

This bidirectional diagnosis is a stronger paper identity than ordinary "refine until property holds."

### 2.2 R4 is a strong representation intervention

The R4 producer freezes:

- candidate states before augmented-state outcomes;
- action panel from base deletion impact only;
- the contract-gated delta representation from base graph + registered deletions + candidate endpoint.

The gate is computed before the augmented-state outcome matrix:

\[
\alpha_A(e)
=
\mathbf 1[
\exists f\in A:
e\notin TC(G-f)
].
\]

The original and compressed representations are then executed independently under the same native deletion contract.

On R4-building:

\[
|R_{\rm current}|=1,
\qquad
|O_{\mathcal C}|=23,
\qquad
|R_{\rm full}|=272,
\]

while:

\[
R_{\rm gate}=O_{\mathcal C},
\qquad
U_\mu=E_\mu=0,
\]

and:

\[
17{,}408/17{,}408
\]

native state-action cells replay exactly.

The declared per-state deltas drop:

\[
271\rightarrow22.
\]

This is not merely post-hoc quotient naming. It is a pre-outcome representation transformation followed by native replay.

### 2.3 SQEC provides a second prospective closure-repair substrate

The fresh eight-variant SQEC family is prospectively frozen.

FULL vs PROJECTED:

\[
mismatch_1=0,
\]

but:

\[
mismatch_2=8.
\]

The frozen canonical guard repair then yields:

\[
mismatch_{\le2}
(FULL,GUARD\text{-}REPAIRED)
=
0.
\]

The independent verifier reconstructs the full matrix with zero mismatch.

This establishes that a continuation-relevant representation coordinate can be dormant at H1, become necessary at H2, and restore closure when reintroduced.

---

## 3. The most important cold-start weakness

### 3.1 The causal arrow "audit -> repair" is not yet uniformly demonstrated

The two accepted repair substrates do not currently instantiate exactly the same causal dependency.

#### R4

The gate is derived from:

- base graph;
- frozen action contract;
- candidate redundant edge endpoint.

It is **not derived from the observed augmented-state audit outcome matrix**.

This is scientifically good because it prevents circularity.

But it means the precise workflow is:

\[
\text{audit establishes the deficit/excess problem}
\]

while independently:

\[
\text{contract structure}
\rightarrow
\text{repair certificate}
\rightarrow
R_{\rm gate}.
\]

Therefore the manuscript should not imply that \(U/E\) values themselves synthesize the gate.

#### SQEC

The frozen repair reattaches a canonical guard that was deliberately removed in PROJECTED.

That is a strong prospective intervention/control, but in its present implementation a hostile reviewer can describe it as:

> remove a known native precondition, then add the same precondition back.

This demonstrates **repair efficacy** and delayed continuation necessity.

It does not yet demonstrate generic audit-driven **repair discovery**.

### 3.2 Consequence

The paper should distinguish:

\[
\boxed{
\text{audit}
\Rightarrow
\text{repair obligation}
}
\]

from:

\[
\boxed{
\mathcal C
\Rightarrow
\text{repair certificate}
}
\]

and combine them as:

\[
(R,\mathcal C)
\xrightarrow{\rm audit}
D
\]

\[
(\mathcal C,D)
\xrightarrow{\rm certificate}
\kappa
\]

\[
(R,\kappa)
\xrightarrow{\Phi}
R'
\]

\[
R'
\xrightarrow{\rm native\ replay}
O_{\mathcal C}.
\]

This is a more defensible scientific workflow than pretending the repair is inferred from outcome labels alone.

---

## 4. Second major weakness: representation repair vs semantic repair

R4 clearly changes the representation while leaving the native deletion semantics fixed.

SQEC is more vulnerable.

In the current implementation:

- PROJECTED removes event preconditions;
- GUARD-REPAIRED reattaches event preconditions.

A reviewer can therefore ask whether the experiment repairs:

1. a **representation of the continuation interface**, or
2. the **transition semantics / specification itself**.

If the latter, the cross-substrate identity becomes:

\[
\text{representation repair}
+
\text{specification repair},
\]

which is weaker than the intended common method.

### Required closure

The SQEC carrier should be refactored conceptually and experimentally so that:

- a fixed native interpreter is unchanged;
- a representation object stores continuation-interface coordinates/rules;
- PROJECTED and REPAIRED differ only in that representation object;
- the same compiler/interpreter consumes both representations;
- the native contract is held fixed.

For example:

\[
R_{\rm full}
=
(\text{transition coordinates},
G_{\rm obs}^{(1)},
G_{\rm obs}^{(2)})
\]

\[
R_{\rm projected}
=
(\text{transition coordinates})
\]

\[
R_{\rm repaired}
=
(\text{transition coordinates},
G_{\rm obs}^{\rm shared}).
\]

Then a fixed compiler maps:

\[
R
\mapsto
\text{native event interface}.
\]

This would make the representation-level intervention explicit rather than inferred from direct event-dataclass mutation.

---

## 5. Third major weakness: no unified repair contract yet

The paper has a unified **audit formalism**, but not yet a unified formal **repair object**.

Introduce:

\[
\Phi_{\mathcal C,\kappa}:R\mapsto R'
\]

where:

- \(\mathcal C\) is the frozen continuation contract;
- \(\kappa\) is a carrier-native repair certificate;
- \(\Phi\) may add, remove, merge, or factor representation distinctions;
- the native transition semantics themselves are not changed.

A valid repair should satisfy four obligations.

### O1. Closure

\[
U_\mu(R';\mathcal C)=0.
\]

The repaired representation contains every distinction required by the contract.

### O2. No excess on an exact repair

For the exact finite-bank case:

\[
E_\mu(R';\mathcal C)=0.
\]

If exactness is not available, report the directional residual rather than claim repair completion.

### O3. Native-semantics invariance

\[
\mathcal C'=\mathcal C
\]

and the concrete/native executor is unchanged.

Only representation changes.

### O4. Frozen information boundary

Define explicitly the information available to repair construction:

\[
\mathcal I_{\rm repair}.
\]

The repair must not inspect held-out native outcomes prohibited by the protocol.

This is what turns "we found a better representation" into a reproducible methodology.

---

## 6. Fourth weakness: the SQEC repair needs matched repair baselines

Current SQEC demonstrates:

- no guard -> 8 H2 mismatches;
- shared frozen guard -> 0 mismatch.

That is enough for a mechanism positive.

It is weaker as a representation-repair result because there is no matched competing repair set.

Add, prospectively:

### B0. No repair

Expected:

\[
mismatch_2=8.
\]

### B1. Full restore

Restore both native observation-event guard clauses separately.

Expected:

\[
mismatch_{\le2}=0.
\]

Representation cost:

\[
2\text{ clauses}.
\]

### B2. Shared canonical repair

Current accepted repair.

Expected:

\[
mismatch_{\le2}=0.
\]

Representation cost:

\[
1\text{ shared rule}.
\]

### B3. Sham / irrelevant repair

Add one same-size rule on an irrelevant coordinate or an allowed-status set frozen to be non-corrective.

Expected:

\[
mismatch_2>0.
\]

This is important.

Without B3, "add one rule -> fixed" can still look tautological.

With B1/B2/B3, the result becomes:

> closure is restored by the contract-relevant representation coordinate, not merely by adding arbitrary precision.

Do not claim global minimality from this four-way baseline.

---

## 7. Fifth weakness: "repair" must be bidirectional, not just refinement

This is potentially the strongest distinction from CEGAR.

CEGAR normally starts coarse and **adds precision** to eliminate spurious counterexamples.

OACR's central exact configuration is:

\[
R_{\rm current}
\prec
O_{\mathcal C}
\prec
R_{\rm full}.
\]

Therefore the representation problem is intrinsically bidirectional:

### From current representation

\[
R_{\rm current}
\xrightarrow{\Phi^+_{\mathcal C}}
R_{\rm gate},
\]

adding distinctions required by continuation.

### From full identity

\[
R_{\rm full}
\xrightarrow{\Phi^-_{\mathcal C}}
R_{\rm gate},
\]

removing distinctions that the contract does not justify.

Both transformations meet at the same registered quotient:

\[
\Phi^+_{\mathcal C}(R_{\rm current})
=
\Phi^-_{\mathcal C}(R_{\rm full})
=
O_{\mathcal C}.
\]

This should become a named formal result / figure.

It is more distinctive than "refinement."

Recommended term:

**bidirectional contract repair**

or, if "repair" seems too software-engineering-specific:

**contract-relative representation correction**.

---

## 8. Closest-neighbor attack

### 8.1 Strong preservation

Strong-preservation theory already owns:

- operator/language-relative abstraction;
- completeness;
- minimal refinement;
- behavioral-equivalence quotients.

Therefore OACR cannot own the mathematical existence of \(O_{\mathcal C}\) or a minimal refinement toward it.

### 8.2 CEGAR

CEGAR already owns a loop of the form:

\[
\text{abstract verification}
\rightarrow
\text{counterexample}
\rightarrow
\text{precision refinement}
\rightarrow
\text{reverification}.
\]

This is the most dangerous conceptual neighbor for the new paper identity.

### 8.3 Program repair / synthesis

Program-repair and synthesis methods already own:

\[
\text{specification failure}
\rightarrow
\text{candidate change}
\rightarrow
\text{execution/test verification}.
\]

Therefore generic "audit -> repair -> verify" is not differentiating by itself.

### 8.4 Safe distinction

OACR must state all four:

1. the target of repair is the **persistent state representation**, not the program or verification abstraction;
2. the concrete/native executor and registered operation contract remain fixed;
3. error is directional:
   \[
   U_\mu\text{ and }E_\mu;
   \]
4. repair can both add missing distinctions and remove unjustified distinctions, and is accepted only by native continuation replay.

This is the defensible gap.

---

## 9. Minimum experiments required to fully own the identity

### Gate A — Unified repair formalism

**Mandatory manuscript/formal work.**

Define \(\kappa\), \(\Phi_{\mathcal C,\kappa}\), repair information boundary, and the four obligations in Section 2/5.

### Gate B — R4 bidirectional repair statement

**No new scientific run required.**

Using existing accepted matrices, explicitly show:

\[
\Phi^+_{\mathcal C}(R_{\rm current})
=
R_{\rm gate}
\]

and:

\[
\Phi^-_{\mathcal C}(R_{\rm full})
=
R_{\rm gate}.
\]

Report the edit counts in each direction.

### Gate C — SQEC representation/compiler separation

**Mandatory implementation clarification; new clean acceptance run recommended.**

Refactor so that the fixed executor consumes an explicit representation object and the repair changes only that object.

Scientific family and continuation contract remain unchanged.

### Gate D — SQEC matched repair baselines

**High-value prospective experiment.**

Freeze B0/B1/B2/B3 before execution.

Acceptance target:

- B0 fails at H2;
- B1 exact;
- B2 exact;
- B3 fails;
- fixed interpreter;
- independent verifier.

### Gate E — Certificate-selection challenge

**Strong-paper upgrade, not strictly required if B3 is strong.**

Give repair construction a frozen candidate library containing:

- the correct guard coordinate;
- multiple irrelevant coordinates/rules.

The constructor may use only the native contract / static dependency certificate, not held-out continuation outcomes.

Require deterministic selection of the correct repair rule.

This converts "we knew what to add back" into:

\[
\text{contract certificate}
\rightarrow
\text{repair selection}.
\]

---

## 10. What is *not* required

Do not add:

- another graph root solely for identity;
- arbitrary H3/H4 composition;
- another H1 learned positive;
- a generic program-repair benchmark;
- a universal synthesis algorithm;
- a proof of global minimality across all representation languages.

These would broaden scope without fixing the actual identity weakness.

---

## 11. Manuscript identity after the gates

### Too weak

\[
\text{native-contract audit}
\rightarrow
\text{representation repair}.
\]

This is too easy to read as CEGAR/APR.

### Recommended

\[
\boxed{
\text{native-contract adequacy audit}
\rightarrow
\text{certificate-constrained bidirectional representation repair}
\rightarrow
\text{native closure verification}
}
\]

### One-sentence paper claim

> We audit implemented persistent representations against prospectively registered native transformation contracts, diagnose both missing and unjustified distinctions, and use contract-derived certificates to add or remove representation structure while leaving native operations fixed; the repaired representation is accepted only when it closes the registered continuation under independent native replay.

---

## 12. Final cold-start judgment

The paper already has the evidence required to make **representation correction** a central contribution.

The remaining risk is not lack of phenomena.

It is a **causal/mechanistic identity gap**:

\[
\text{audit result}
\quad\not\equiv\quad
\text{repair derivation}.
\]

Close that gap with:

1. a unified repair operator;
2. explicit fixed-semantics representation repair in SQEC;
3. matched full/shared/sham repair baselines;
4. bidirectional R4 formulation.

If these are completed, the paper identity becomes substantially harder to collapse into either strong-preservation refinement, CEGAR, or generic program repair.


---

## 13. Closure addendum — 2026-09-30

**Cold-start acceptance status: CLOSED / PASS for mandatory Gates A–D.**

Authoritative acceptance record:

\`docs/OACR_AUDIT_TO_REPAIR_ACCEPTANCE_RECORD_2026-09-30.md\`

### Gate A

PASS.

The manuscript now contains:

- directional audit deficit \(D\);
- repair certificate \(\kappa\);
- repair information boundary \(\mathcal I_{\rm repair}\);
- repair operator \(\Phi_{\mathcal C,\kappa}\);
- O1–O4 repair obligations;
- explicit additive/subtractive bidirectional correction.

### Gate B

PASS.

Independent run:

\`36680594535\`

verified:

\[
0\rightarrow22
\]

additive delta repair and:

\[
271\rightarrow22
\]

subtractive repair by deleting 249 inactive deltas, both reaching the same 23-block target with:

\[
U_\mu=E_\mu=0
\]

and:

\[
17{,}408/17{,}408
\]

native replay cells exact.

### Gate C

PASS.

Fresh SQEC v2 uses:

- fixed transition skeleton;
- fixed compiler;
- fixed vendored native executor;
- explicit baseline-varying \`ContinuationRepresentation\` only.

Acceptance run:

\`36680880190\`.

### Gate D

PASS.

Matched baseline result:

\[
B0:\ H1=0,\ H2=12,\ cost=0
\]

\[
B1:\ H1=0,\ H2=0,\ cost=2
\]

\[
B2:\ H1=0,\ H2=0,\ cost=1
\]

\[
B3:\ H1=0,\ H2=12,\ cost=1.
\]

Independent verifier:

- verified = true;
- matrix mismatch count = 0;
- verifier mismatch count = 0.

The equal-cost B2/B3 contrast establishes that arbitrary added representation structure is insufficient; the contract-relevant continuation coordinate is required.

### Gate E

Not required for A–D acceptance and remains optional.

Do not claim generic repair synthesis.

### Accepted paper identity

\[
\boxed{
\textbf{native-contract adequacy audit}
\rightarrow
\textbf{certificate-constrained bidirectional representation repair}
\rightarrow
\textbf{native closure verification}
}
\]

The causal/mechanistic identity gap identified by this cold-start review is therefore closed under its own mandatory acceptance standard.
