# OACR Continuation-Depth Formal Spine v0

**Date:** 2026-09-29  
**Status:** working formal scaffold; mature behavioral-equivalence machinery is treated as foundation, not novelty

## 1. Purpose

The WRITE-focused OACR experiments use a fixed one-step action panel. COMPOSE requires a horizon-indexed object that can express:

- current equivalence;
- one-step operational equivalence;
- delayed separation at depth 2 or later;
- state-dependent action legality / enabledness;
- representation adequacy as a function of continuation depth.

This document supplies only that scaffold.

## 2. Qualified transition system

Let a persistent system be

\[
\mathcal S=(X,O,\mathcal A,T),
\]

where:

- \(X\) is the latent persistent state space;
- \(O:X\to\mathcal Y\) is the registered current observation;
- \(\mathcal A(x)\) is the set of actions qualified/enabled under the registered continuation interface at \(x\);
- \(T(x,a)\) is the successor state for \(a\in\mathcal A(x)\).

Carrier-specific interfaces may include legality, enabledness, native status, invariants, recoverability, cost, or other registered coordinates. Those coordinates can be included in the action label/outcome signature without changing the recursion below.

## 3. Depth-h continuation signature

Define recursively:

\[
\Sigma_0(x)=O(x).
\]

For \(h\ge0\),

\[
\Sigma_{h+1}(x)
=
\left(
O(x),
\left\{
\bigl(a,\Sigma_h(T(x,a))\bigr):
a\in\mathcal A(x)
\right\}
\right),
\]

with any registered native action-status coordinates included in the branch label.

Two states are depth-h continuation-equivalent iff

\[
x\equiv_h y
\iff
\Sigma_h(x)=\Sigma_h(y).
\]

For stochastic carriers, equality is replaced by equality of the registered branch distributions/certificates. The finite deterministic form is the current primary scaffold.

## 4. Basic refinement property

Because \(\Sigma_h\) is recoverable by truncating \(\Sigma_{h+1}\),

\[
x\equiv_{h+1}y
\implies
x\equiv_h y.
\]

Therefore the operational partitions form a refinement chain:

\[
\Pi_0
\preceq
\Pi_1
\preceq
\Pi_2
\preceq
\cdots
\]

where \(\Pi_h\) is the partition induced by \(\Sigma_h\).

This is a foundational mathematical consequence, not an empirical discovery.

## 5. First-separation depth

For a currently equivalent pair define:

\[
d(x,y)
=
\min\{h\ge1:\Sigma_h(x)\neq\Sigma_h(y)\},
\]

with \(d(x,y)=\infty\) when no registered finite continuation separates the pair.

Interpretation:

- \(d=1\): WRITE-level separation;
- \(d=2\): minimum COMPOSE separation;
- \(d>2\): delayed continuation divergence;
- \(d=\infty\): inert under the declared continuation universe.

This lets different carriers share one measurement while retaining different local mechanisms.

## 6. Horizon-indexed representation adequacy

Let \(R\) be an implemented representation.

Define:

\[
U_h(R)=H(\Pi_h\mid R),
\]

\[
E_h(R)=H(R\mid \Pi_h).
\]

Interpretation remains unchanged:

- \(U_h>0\): representation merges states that the depth-h continuation contract requires apart;
- \(E_h>0\): representation preserves distinctions unnecessary for depth-h continuation.

Because \(\Pi_{h+1}\) refines \(\Pi_h\), for fixed \(R\):

\[
U_{h+1}(R)\ge U_h(R),
\]

and

\[
E_{h+1}(R)\le E_h(R).
\]

These monotonicities are mathematical consequences of partition refinement/conditioning and are sanity checks rather than empirical claims.

## 7. Minimal COMPOSE failure

The central target pattern is not merely that deeper horizons distinguish more states. It is a carrier where an implemented or operationally motivated representation is exact at H1:

\[
U_1(R)=0,
\qquad
E_1(R)=0
\]

or at least \(U_1(R)=0\),

while:

\[
U_2(R)>0.
\]

At the pair level:

\[
x\equiv_1 y
\quad\land\quad
x\not\equiv_2 y.
\]

The scientific content must come from **why** the first transformation changes later relevance/qualification, not from the generic refinement theorem.

## 8. Constructive closure target

If a depth-1 representation \(R_1\) fails at depth 2, seek a refinement \(R_2\) such that:

\[
U_2(R_2)=0
\]

while minimizing or eliminating:

\[
E_2(R_2).
\]

Preferred strict intermediate form:

\[
R_1
\prec
R_2
\prec
R_{\rm full}.
\]

Native sequence replay must verify that the refinement preserves every registered depth-2 branch.

## 9. Current carrier mapping

### Relational deletion

R3/R4 evidence currently indicates:

\[
d(e)\in\{1,\infty\}
\]

for the frozen registered deletion universes. Thus the H1 quotient is already compositionally closed for those carriers.

Role: exact WRITE positive + COMPOSE negative/control.

### SQEC multistep legality

Retrospective controlled mechanism:

\[
d=2
\]

for the legality-complete versus legality-projected object from the initial state.

Role: exact controlled proof that an H1-sufficient projection can fail after one action changes the qualification of the next.

### Natural Git G5 continuation

Prospective COMPOSE-G test asks whether accepted H1-equivalent natural same-tree pairs have:

\[
d=2
\]

under a frozen two-merge continuation.

Role: natural history-dependent confirmation if positive.

### Learned state

GRACE L1b supplies a registered H2 negative; Finetune fold0 supplies a registered H1 positive. Delayed learned separation remains open.

## 10. Novelty boundary

Do not claim novelty for:

- finite-horizon behavioral equivalence;
- partition refinement with horizon;
- bisimulation-style recursion;
- entropy monotonicity induced by finer operational partitions.

Potential paper-level novelty must lie in evidence that persistent-system histories/latent distinctions exhibit nontrivial first-separation structure under state-dependent continuation, plus a constructive representation consequence that survives native replay.
