# OACR Qualified Continuation / COMPOSE Bridge v0

**Date:** 2026-09-29  
**Status:** working scientific-architecture bridge; no new empirical claim is accepted by this document  
**Scope:** restores the broader OACR object after the WRITE-focused phase while preserving all frozen WRITE experiments and acceptance records

## 1. Why this bridge exists

The WRITE program established a useful depth-1 intervention object, but repeated red-team pressure gradually treated the future operation panel as exogenous and fixed. That restriction is experimentally valuable for causal identification; it is not the full OACR ontology.

The original OACR decomposition already separated:

- READ
- PROBE
- WRITE
- COMPOSE
- COMPUTE

and the system taxonomy already treated admissible operations, invariants, authority/provenance relations, and identity/continuity relations as part of the system semantics.

The present bridge therefore does **not** retract WACT, R3, G5, learned replay, U/E, or representation redesign. It places them inside a larger continuation object.

## 2. Minimal state-and-continuation object

Let \(X_t\) denote a persistent system state at time \(t\). For a candidate transformation \(a\), define a carrier-relative continuation interface

\[
\Gamma_{X_t}(a)
=
\bigl(
L_{X_t}(a),
E_{X_t}(a),
O_{X_t}(a),
I_{X_t}(a),
V_{X_t}(a)
\bigr),
\]

where coordinates are instantiated only when native semantics support them:

- \(L\): legality / qualification;
- \(E\): enabledness / applicability;
- \(O\): registered operational outcome;
- \(I\): invariant or obligation preserved/violated;
- \(V\): viability, recoverability, or future availability induced by the action.

The interface is deliberately broader than a permission set. In WACT-R, the primary changing coordinate is outcome sensitivity. In SQEC-like systems, legality and future qualification are central. In Git, ancestry/history can affect action status and later native operation semantics.

An action therefore acts on both the persistent state and its continuation interface:

\[
(X_t,\Gamma_{X_t})
\xrightarrow{a}
(X_{t+1},\Gamma_{X_{t+1}}).
\]

## 3. WRITE as a first-order generator

A WRITE experiment studies a depth-1 slice:

\[
X \xrightarrow{a} X'.
\]

WACT is retained as the causal instrument that asks whether a fixed latent distinction becomes operationally consequential under a controlled future-action regime.

The depth-1 target remains scientifically useful:

\[
X \equiv_0 Y
\quad\text{but}\quad
X \not\equiv_1 Y.
\]

This document does not demote existing depth-1 evidence. It stops treating depth 1 as the whole mother problem.

## 4. Minimal COMPOSE extension

COMPOSE enters only when a transformation changes the semantic environment of later transformations.

For a frozen action sequence \(a_1,\ldots,a_h\), let continuation equivalence to depth \(h\) be written provisionally as

\[
X \equiv_h Y.
\]

The exact formal definition may inherit standard behavioral/bisimulation machinery; novelty is not claimed for the equivalence construction itself.

The first high-value COMPOSE witness is:

\[
\boxed{
X \equiv_1 Y
\quad\land\quad
X \not\equiv_2 Y.
}
\]

Interpretation:

- current READ does not distinguish the states;
- registered one-step continuation does not justify preserving their latent difference;
- after a shared first transformation, a later transformation exposes a distinction that was previously continuation-inert.

This is provisionally called **delayed continuation divergence**.

COMPOSE-v1 is **not** authorized to expand into an unrestricted algebra of arbitrary-length histories. The first gate is the minimum depth-2 witness.

## 5. Stronger restoration witness

A stronger candidate result is a restoration/hysteresis form.

For a transformation history \(h\) and a restoration operation \(r\),

\[
O(r(h(X))) = O(X)
\]

and, ideally,

\[
\Gamma_1(r(h(X))) \cong \Gamma_1(X),
\]

while

\[
\Gamma_{\ge2}(r(h(X))) \not\cong \Gamma_{\ge2}(X).
\]

Informally:

> restoring the present, and possibly its immediate affordances, does not necessarily restore its future continuation structure.

This is a target, not an accepted result.

## 6. Relation to SQEC

OACR should absorb only the structural lesson needed here, not SQEC's complete evidence/decision semantics.

The reusable SQEC lesson is:

\[
\text{actions can update qualification, observation legality, recoverability, and future action availability.}
\]

SQEC already treats future qualification and recoverability as dynamic state coordinates and evaluates legal contingent policies over multiple steps. OACR contributes a different question:

> which distinctions must a computational representation preserve so that those continuation dynamics remain closed under the registered interface?

The bridge is therefore:

\[
\text{SQEC-style dynamic qualification}
\rightarrow
\text{WACT-style causal continuation intervention}
\rightarrow
\text{OACR representation necessity/redesign}.
\]

No subsystem-ownership claim is made between the projects.

## 7. Representation-closure target

Let \(R(X)\) be an implemented representation.

Depth-\(h\) adequacy requires that representation equality not merge states whose registered qualified continuation differs by depth \(h\).

A depth-1 representation may therefore be adequate even when it fails at depth 2:

\[
U_1(R)=0,
\qquad
U_2(R)>0.
\]

The constructive OACR target becomes:

\[
\text{delayed continuation divergence}
\rightarrow
\text{certificate}
\rightarrow
R_h
\rightarrow
\text{native sequence replay}.
\]

The desired refinement remains intermediate rather than full-state identity:

\[
R_{h-1}
\prec
R_h
\prec
R_{\mathrm{full}}
\]

whenever the carrier supports such a strict intermediate quotient.

## 8. Immediate evidence-audit order

Before designing a new COMPOSE experiment, audit existing assets for the following in order:

1. **SQEC multi-step legality / qualification artifacts**
   - look for states/policies equal under current and one-step projections but separated at a later legal continuation;
   - distinguish actual outcome from protocol/theory only.

2. **Git G1/G2/G5**
   - search existing same-tree pairs for same immediate native behavior but different later merge/rebase/cherry-pick continuation;
   - separately test whether a content-restoration construction already instantiates restoration without continuation restoration.

3. **Claim-Relative Representation**
   - inspect completed restoration/reinstatement/recoverability results;
   - do not count superseded-before-run protocols as evidence.

4. **Learned persistent state**
   - re-read existing H0/H1/H2 artifacts before launching a new panel;
   - search specifically for \(H1\)-equivalent but \(H2\)-divergent pairs.

Only if existing evidence fails these gates should a new COMPOSE-v1 protocol be frozen.

## 9. Experimental discipline

All existing acceptance rules remain binding:

- freeze before outcome;
- outcome-blind witness/action selection;
- distinguish scientific negative from engineering failure;
- preserve unfavorable results;
- independent verifier where the claim is consequential;
- native replay for accepted positive witnesses;
- do not reinterpret an already-exposed result as prospective.

Broadening the ontology must not lower the epistemic standard.

## 10. Planning consequence

The immediate scientific priority is no longer to maximize the count of independent depth-1 WRITE positives.

Priority becomes:

\[
\text{WRITE closure}
\rightarrow
\text{existing-asset depth audit}
\rightarrow
\text{minimal COMPOSE witness}
\rightarrow
\text{dynamic representation redesign}.
\]

WRITE remains the dominant first-order experimental layer. COMPOSE enters early only as the minimum necessary extension required to ask whether operations alter the future relevance and availability of later operations.
