# OACR-SQEC Continuation Repair Protocol v1

**Date:** 2026-09-30  
**Status:** prospectively frozen before execution of the fresh confirmation family  
**Role:** second-substrate confirmatory audit -> repair result for OACR  
**Source semantics:** native SQEC typed dynamic-qualification transition system

## 1. Scientific question

Can an OACR-style representation repair close a multi-step continuation failure outside the relational graph carrier?

The controlled substrate is dynamic event legality.

Compare three representations of the same typed transition system:

1. **FULL** — native event transitions plus native state-dependent preconditions;
2. **PROJECTED** — same state coordinates and transitions, but event preconditions removed;
3. **GUARD-REPAIRED** — PROJECTED plus one canonical state-dependent observation-guard rule that is recompiled into the native event interface.

The intended contrast is:

\[
FULL \equiv_1 PROJECTED
\]

at the registered root interface, while for variants in which the common first action moves the guard coordinate outside the allowed set,

\[
FULL \not\equiv_2 PROJECTED.
\]

The repair target is:

\[
FULL \equiv_2 GUARD\text{-}REPAIRED.
\]

This is a confirmatory representation-closure result, not a novelty claim for guards, transition systems, or strong preservation.

## 2. Fresh family

Freeze eight deterministic variants indexed

\[
v\in\{0,\ldots,7\}.
\]

All variants share:

- one safeguard coordinate \`s::observation-route\`;
- one epistemic coordinate \`u::latent-semantics\`;
- the same root observation guard:
  \[
  s::observation-route
  \in
  \{ACTION\_OPEN,SATISFIED\};
  \]
- root status \`ACTION_OPEN\`;
- the same event alphabet:
  - \`commit-task\`;
  - \`universal-remediation\`;
  - \`observe-qualified\`;
  - \`observe-unqualified\`.

The only family coordinate relevant to delayed legality is the post-\`commit-task\` route status, frozen by variant:

| variant | post-commit route |
|---|---|
| 0 | CLOSED |
| 1 | SATISFIED |
| 2 | CLOSED |
| 3 | ACTION_OPEN |
| 4 | CLOSED |
| 5 | SATISFIED |
| 6 | CLOSED |
| 7 | ACTION_OPEN |

Thus variants 0/2/4/6 are predeclared delayed-guard positive controls; 1/3/5/7 are predeclared no-divergence controls for this mechanism.

No variant may be replaced after execution.

## 3. Native continuation contract

Enumerate the complete ordered event-sequence set of lengths 1 and 2 over the frozen four-event alphabet.

For each representation and sequence, execute the native SQEC transition semantics.

The registered sequence signature contains only:

- whether each step is legal;
- final typed atom statuses if the sequence remains legal;
- final qualification state if legal;
- the index/event at which illegality occurs otherwise.

Costs, policy optimization, and stochastic probabilities are excluded from this confirmation contract.

The purpose is continuation closure, not decision optimality.

## 4. H1 gate

For every variant, FULL and PROJECTED must match on the complete length-1 contract:

\[
\boxed{
mismatch_1(FULL,PROJECTED)=0.
}
\]

If any root H1 mismatch occurs, the family construction fails and no H2 claim is promoted.

This guarantees that the omitted guard rule is dormant at the registered root.

## 5. H2 delayed divergence

For predeclared positive-control variants 0/2/4/6:

- \`commit-task\` must be legal at step 1 in FULL and PROJECTED;
- after the common commit transition, \`observe-qualified\` and \`observe-unqualified\` must be illegal in FULL;
- the corresponding projected sequences must remain legal.

Therefore each positive-control variant must contain at least one H2 mismatch.

For no-divergence controls 1/3/5/7, post-commit route remains in the guard's allowed set, so this mechanism predicts no FULL/PROJECTED mismatch solely from the guard deletion.

Report the complete H2 mismatch matrix; do not report only the predeclared sequences.

## 6. Guard repair

The repair representation may add exactly one frozen coordinate:

\[
G_{\rm obs}
=
(
\text{atom}=\texttt{s::observation-route},
\text{allowed}=\{ACTION\_OPEN,SATISFIED\}
).
\]

This single canonical rule is shared by both observation outcomes.

The repair compiler may:

- take the projected transition/event representation;
- reattach the canonical guard to every registered observation outcome.

It may not inspect any FULL-vs-PROJECTED continuation mismatch to choose the coordinate or allowed statuses.

Acceptance requires, for all eight variants and every registered length-1 and length-2 sequence,

\[
\boxed{
mismatch_{\le2}(FULL,GUARD\text{-}REPAIRED)=0.
}
\]

## 7. Representation accounting

Report:

- number of native observation-event precondition clauses in FULL;
- number of canonical guard rules stored by GUARD-REPAIRED;
- H1 FULL/PROJECTED mismatches;
- H2 FULL/PROJECTED mismatches;
- H1/H2 FULL/GUARD-REPAIRED mismatches;
- per-variant mismatch counts;
- exact divergent sequences.

This accounting is descriptive. Do not claim byte-optimal compression.

## 8. Independent verifier

A separate verifier must reconstruct:

- the eight frozen variants;
- the three representation forms;
- the complete length≤2 sequence set;

and recompute every signature without trusting producer signatures.

Acceptance requires exact equality between verifier and producer matrices.

## 9. Interpretation

A successful run supports the bounded cross-substrate statement:

> A representation that is exact for the registered immediate interface can fail under composition when a first transformation changes a coordinate used to qualify a later transformation; adding the frozen state-dependent guard coordinate restores continuation closure.

It does not establish:

- novelty of state-dependent guards;
- a universal minimal representation;
- necessity of qualification for all COMPOSE effects;
- natural prevalence.

## 10. Relation to the earlier SQEC result

The earlier stochastic multistep legality audit remains retrospective mechanism evidence and includes a decision consequence (illegal replay/regret).

This fresh family serves a different role:

- prospectively frozen continuation contract;
- internal positive/negative controls;
- explicit representation intervention;
- exhaustive depth≤2 native replay;
- independent matrix verification.

It is the second-substrate constructive confirmation for the OACR paper.
