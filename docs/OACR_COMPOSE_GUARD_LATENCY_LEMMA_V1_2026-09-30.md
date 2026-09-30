# OACR COMPOSE — Guard-Latency Lemma v1

**Date:** 2026-09-30  
**Status:** formal bridge / bookkeeping lemma; no novelty claim for the generic transition-system fact  
**Purpose:** isolate the minimum mechanism behind the SQEC retrospective H1-equal / H2-different result

## 1. Setup

Let a continuation system contain:

- states \(X\);
- candidate operations \(a\in A\);
- an enabled/qualified guard
  \[
  g(x,a)\in\{0,1\};
  \]
- a state transition
  \[
  T(x,a);
  \]
- an immediate registered outcome
  \[
  O(x,a).
  \]

Consider a full system \(F\) and a projected representation/system \(P\).

Assume they begin from corresponding current states \(x_F,x_P\).

## 2. Depth-1 agreement conditions

Suppose that for every registered first action \(a\),

\[
g_F(x_F,a)=g_P(x_P,a),
\]

and whenever the action is enabled,

\[
O_F(x_F,a)=O_P(x_P,a)
\]

and the registered post-action observable state is equal.

Then the systems are equivalent under the registered immediate continuation interface:

\[
F \equiv_1 P.
\]

No claim is made that their full internal rule descriptions are identical.

## 3. Latent guard condition

Suppose there exist registered actions \(a_1,a_2\) such that:

1. \(a_1\) is enabled in both systems at the root;
2. executing \(a_1\) produces the same registered immediate outcome in both systems;
3. after the shared first transition,
   \[
   g_F(T_F(x_F,a_1),a_2)
   \ne
   g_P(T_P(x_P,a_1),a_2).
   \]

Then:

\[
F \not\equiv_2 P.
\]

Therefore:

\[
\boxed{
F\equiv_1P
\quad\land\quad
F\not\equiv_2P.
}
\]

## 4. Interpretation

The omitted distinction is not needed to answer:

> which registered actions are currently available, and what do they do immediately?

It becomes necessary only after a shared transformation moves the system into a state where the omitted guard-relevant coordinate matters.

Thus the representational demand is **latent at depth 1 and activated by composition**.

## 5. Representation corollary

Let \(R\) omit exactly the information required to update the future guard of \(a_2\) after \(a_1\), while preserving the complete registered depth-1 interface at the current state.

Then under a depth-indexed OACR audit it is possible to have:

\[
U_1(R)=0
\]

but

\[
U_2(R)>0.
\]

Hence:

> depth-1 operational sufficiency does not imply compositional closure when operations change future qualification/enabledness.

This is the representational consequence OACR needs; the transition-system lemma itself is not presented as a novel theorem.

## 6. SQEC instantiation

In the executed stochastic multistep legality example:

- \(a_1=\texttt{commit-task}\);
- \(a_2=\texttt{observe-semantics}\);
- the root observation-route coordinate is ACTION_OPEN;
- FULL and PROJECTED therefore both permit the observation initially;
- the common commit transition closes the observation route;
- FULL retains the observation precondition and therefore rejects the later observation;
- PROJECTED omitted the precondition and continues to permit it.

Thus the controlled SQEC result is an exact instantiation of the latent-guard condition.

## 7. Why relational deletion does not instantiate it

In the frozen R3/R4 deletion carriers:

- registered deletions do not modify the admissibility semantics of later registered deletions;
- the operation domain is fixed;
- delayed activation would have to arise only from accumulated reachability loss.

The exact registered-action cut audit found no finite activation depth greater than 1.

Therefore relational deletion serves as a useful control:

> composition without state-dependent guard/affordance change need not generate new representational demand.

## 8. Empirical target beyond the lemma

The strong empirical question is not whether the lemma is true by construction.

It is whether real/native persistent systems contain distinctions that satisfy its premises without those premises being manually encoded as the answer.

Priority carriers:

1. learned recovery/update dynamics;
2. native version-history operations with state-dependent later semantics;
3. future authority/qualification carriers.

The empirical paper should claim the observed mechanism and representation consequence, not novelty for the generic lemma.
