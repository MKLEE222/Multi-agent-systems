# OACR-COMPOSE-R v1 — Registered-Action Cut Depth Protocol

**Date:** 2026-09-29  
**Status:** prospectively frozen before any R4-building depth>1 registered-action cut scan or augmented-state two-write outcome  
**Role:** exact relational COMPOSE gate; minimum extension beyond WACT/WRITE

## 1. Motivation

The developmental R3 carrier was inspected exploratorily after the qualified-continuation bridge.

For each redundant candidate distinction \(e=(u,v)\), assign capacity:

- 1 to each of the 64 frozen registered deletion edges;
- a large sentinel capacity to every other asserted edge.

The minimum \(u\to v\) cut restricted to the registered action universe has the following developmental distribution:

- 100 candidates: cut size 1;
- 171 candidates: not disconnectable by any subset of the registered 64 actions;
- 0 candidates: finite cut size 2 or greater.

Therefore the R3 depth-1 operational quotient is already closed under arbitrary composition of the registered deletion universe: every distinction that can ever become active is already activated by at least one single registered write.

This developmental result is a negative/control and must not be used as a confirmatory COMPOSE claim.

## 2. Fresh target

Use the already frozen and prospectively accepted R4-building carrier:

- root Q41176 (building);
- 272 registered states;
- 271 redundant augmented-edge states;
- the already frozen 64 deletion actions;
- existing H1 outcomes may be used only to identify the accepted carrier and confirm the action/state contract.

No depth-2 or higher registered-action cut statistic for building may be inspected before this protocol is committed.

## 3. Structural depth certificate

For each redundant candidate \(e=(u,v)\), define the registered-action cut depth

\[
d_A(e)
=
\min\{
|F|:
F\subseteq A,\;
(u,v)\notin TC(G-F)
\},
\]

with

\[
d_A(e)=\infty
\]

when no subset of the registered action set \(A\) disconnects \(u\) from \(v\).

Operational meaning:

- \(d_A(e)=1\): WRITE-level active distinction; already detectable at H1.
- \(d_A(e)=2\): minimum COMPOSE witness; every single registered deletion leaves the distinction inert, but at least one two-write composition activates it.
- \(d_A(e)=k>2\): delayed activation first appears at depth \(k\).
- \(d_A(e)=\infty\): distinction is inert under every composition made solely from the registered action universe.

The cut is computed only on the base graph. No augmented-state depth-2 outcome is used to select candidates or action sequences.

## 4. Primary prospective question

Does the fresh building carrier contain any redundant distinction with

\[
d_A(e)=2?
\]

If yes, it supports the exact structural prediction

\[
G \equiv_1 G+e
\]

under the complete registered singleton action panel, while for a frozen minimum-cut pair \(\{f_1,f_2\}\),

\[
G \not\equiv_2 G+e.
\]

This is the minimum COMPOSE phenomenon:

> a distinction unnecessary for every registered one-step write becomes necessary only after composition of two registered writes.

## 5. Candidate/action selection

For every candidate \(e\):

1. compute \(d_A(e)\) with unit capacity on registered actions and sentinel capacity on all other asserted edges;
2. if \(d_A(e)=2\), recover all/one exact two-edge registered cut(s);
3. order eligible candidates lexically by candidate edge identity;
4. select up to 16 evenly spaced eligible candidates;
5. for each selected candidate choose the lexicographically first exact minimum registered cut \((f_1,f_2)\).

No augmented-state two-write outcome participates in selection.

If no \(d_A(e)=2\) candidate exists, report a clean COMPOSE-R depth-2 negative and do not alter the action panel or carrier.

## 6. Native exact replay

For each selected witness \(e\), execute on both \(G\) and \(G+e\):

### H1 controls

Delete \(f_1\) alone and compare complete transitive closure.

Delete \(f_2\) alone and compare complete transitive closure.

Both must remain equal:

\[
TC(G-f_i)=TC((G+e)-f_i),\quad i=1,2.
\]

### H2 composition

Starting from fresh copies, delete \(f_1\) and then \(f_2\) from both states and compare complete transitive closure:

\[
TC(G-\{f_1,f_2\})
\neq
TC((G+e)-\{f_1,f_2\}).
\]

Reverse order must produce the same final graph/closure, providing an order-control for this commutative relational carrier.

Any structural prediction failure blocks promotion and triggers implementation/theory audit.

## 7. Secondary full-depth summary

Report the exact distribution of \(d_A(e)\) over all 271 candidates:

- count at 1;
- count at 2;
- count at 3,4,... if present;
- count at infinity.

This is descriptive for the frozen carrier.

Do not claim a universal depth law from R3/building.

## 8. Representation consequence

If a depth-2 witness exists, compare:

- the accepted H1 contract-gated representation \(R_1\);
- a depth-2 gated representation \(R_2\) that retains a redundant delta iff \(d_A(e)\le2\).

The target pattern is

\[
U_1(R_1)=0
\]

for the H1 contract but

\[
U_2(R_1)>0
\]

for the H2 contract, while

\[
U_2(R_2)=0.
\]

Over-refinement \(E_2\) is reported exactly.

No minimality claim is made unless independently proved.

## 9. Boundaries

A positive result would establish a precise compositional activation mechanism in an exact relational carrier. It would **not** by itself establish:

- noncommutative COMPOSE;
- dynamic legality/qualification;
- history-dependent action availability;
- a cross-substrate law;
- cultural/institutional continuity.

Those require distinct carriers.

A negative result is scientifically valid and would show that, on the fresh building carrier and frozen action universe, depth-1 gating is already compositionally closed through depth 2 (or, if all finite cuts are size 1, through the entire registered deletion universe).

## 10. Acceptance discipline

- carrier and action panel are unchanged from accepted R4-building;
- no replacement based on depth result;
- structural certificate precedes augmented-state H2 replay;
- positive witnesses receive independent recomputation and native replay;
- zero eligible candidates are retained as a negative result.
