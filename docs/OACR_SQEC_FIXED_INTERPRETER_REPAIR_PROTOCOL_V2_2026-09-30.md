# OACR-SQEC Fixed-Interpreter Representation Repair Protocol v2

**Date:** 2026-09-30  
**Status:** prospectively frozen before v2 execution  
**Acceptance authority:** \`docs/OACR_AUDIT_TO_REPAIR_ACCEPTANCE_GATE_V1_2026-09-30.md\`  
**Native SQEC source snapshot:** \`external/sqec_snapshot_4f37a0af/\`  
**Source commit:** \`4f37a0af1c2cb44b2eb7eb1b187d96a2ebd34295\`

## 1. Purpose

This protocol closes Gates C and D of the OACR audit-to-repair cold-start review.

The scientific question is no longer merely whether restoring a known guard can recover behavior.

It is whether a **fixed native interpreter** can consume different explicit continuation-representation objects while all of the following remain fixed:

- typed state-transition skeleton;
- event alphabet;
- native transition executor;
- registered sequence contract;
- state-update semantics;
- variant family.

Only the representation object may change.

## 2. Fresh confirmatory family

Freeze twelve deterministic variants:

\[
v\in\{0,\ldots,11\}.
\]

All variants share:

- route atom:
  \[
  \texttt{s::observation-route};
  \]
- task atom:
  \[
  \texttt{s::task-done};
  \]
- latent semantic atom:
  \[
  \texttt{u::latent-semantics};
  \]
- root observation route:
  \[
  ACTION\_OPEN;
  \]
- reference observation guard:
  \[
  \texttt{s::observation-route}
  \in
  \{ACTION\_OPEN,SATISFIED\};
  \]
- event alphabet:
  - \`commit-task\`;
  - \`universal-remediation\`;
  - \`observe-qualified\`;
  - \`observe-unqualified\`.

The post-\`commit-task\` route target is frozen as:

| variant | target | expected delayed-guard class |
|---:|---|---|
| 0 | CLOSED | positive |
| 1 | SATISFIED | negative |
| 2 | UNKNOWN | positive |
| 3 | ACTION_OPEN | negative |
| 4 | UNKNOWN | positive |
| 5 | SATISFIED | negative |
| 6 | CLOSED | positive |
| 7 | ACTION_OPEN | negative |
| 8 | CLOSED | positive |
| 9 | SATISFIED | negative |
| 10 | UNKNOWN | positive |
| 11 | ACTION_OPEN | negative |

Predeclared positive controls:

\[
\{0,2,4,6,8,10\}.
\]

Predeclared negative controls:

\[
\{1,3,5,7,9,11\}.
\]

No variant may be replaced after execution.

## 3. Fixed transition skeleton

For each variant, construct one transition skeleton containing:

- the compiled SQEC state model;
- \`commit-task\` transitions;
- \`universal-remediation\` transitions;
- observation outcome transitions;
- costs/probabilities carried only as native metadata.

The skeleton contains **no observation legality preconditions**.

The skeleton is identical across all representation baselines for the same variant.

## 4. Explicit representation object

A continuation representation is an immutable collection of stored guard rules.

Each guard rule contains:

- rule ID;
- guarded atom;
- frozen allowed-status set;
- event IDs to which the rule applies.

No transition function is stored in the repair object.

## 5. One fixed compiler/interpreter

Define one frozen compiler:

\[
Compile(\text{skeleton},R)
\rightarrow
\text{native event interface}.
\]

For every stored guard rule in \(R\), the compiler attaches the corresponding native SQEC precondition to the declared event IDs.

The compiler implementation is identical for FULL, B0, B1, B2, and B3.

Native sequence execution always uses the same SQEC function:

\[
\texttt{apply\_qualification\_event}.
\]

The repair operation therefore changes only \(R\), not the executor or transition skeleton.

## 6. Representation baselines

### Reference FULL

FULL stores two separate per-event clauses:

1. route guard for \`observe-qualified\`;
2. route guard for \`observe-unqualified\`.

Each uses:

\[
\texttt{s::observation-route}
\in
\{ACTION\_OPEN,SATISFIED\}.
\]

Representation cost:

\[
2\text{ stored guard rules}.
\]

### B0 — no repair

No observation guard rule is stored.

Cost:

\[
0.
\]

### B1 — full restore

Store the same two separate guard rules as FULL.

Cost:

\[
2.
\]

### B2 — shared canonical repair

Store exactly one shared rule:

\[
\kappa_{\rm route}
=
(
\texttt{s::observation-route},
\{ACTION\_OPEN,SATISFIED\},
\{\texttt{observe-qualified},\texttt{observe-unqualified}\}
).
\]

Cost:

\[
1.
\]

### B3 — sham repair

Store exactly one shared rule of the same representation cardinality as B2:

\[
\kappa_{\rm sham}
=
(
\texttt{s::task-done},
\{UNKNOWN,CLOSED,ACTION\_OPEN,SATISFIED\},
\{\texttt{observe-qualified},\texttt{observe-unqualified}\}
).
\]

Because every possible task status is allowed, the rule carries representation structure but imposes no corrective legality restriction.

Cost:

\[
1.
\]

The sham definition is frozen before v2 execution.

## 7. Repair information boundary

The repair information boundary is:

\[
\mathcal I_{\rm repair}^{SQEC}
=
\{
\text{native contract schema},
\text{declared guard atoms/status sets},
\text{static event-rule applicability},
\text{frozen variant manifest}
\}.
\]

The baseline repair representations are frozen directly by this protocol.

They may not inspect:

- v2 native outcome matrices;
- v2 H2 mismatch identities;
- v2 verifier output.

The v2 experiment is a matched causal repair comparison, not repair synthesis.

## 8. Registered continuation contract

Enumerate the complete event-sequence set of lengths 1 and 2 over the frozen four-event alphabet.

For each compiled representation and sequence, execute the same native transition executor.

Registered signature contains:

- legality of each executed prefix;
- first illegal step/event if any;
- final typed atom statuses when legal;
- final joint qualification state when legal;
- legal-prefix typed atom statuses when illegal.

## 9. Frozen acceptance predictions

### H1 invariance

For every baseline and every variant:

\[
mismatch_1(FULL,B_i)=0
\]

for:

\[
i\in\{0,1,2,3\}.
\]

Failure is scientific protocol failure.

### B0

Positive-control variants must diverge after \`commit-task\` followed by either observation outcome.

Expected aggregate:

\[
mismatch_2(FULL,B0)=12.
\]

Negative controls must not diverge.

### B1

\[
mismatch_{\le2}(FULL,B1)=0.
\]

### B2

\[
mismatch_{\le2}(FULL,B2)=0.
\]

### B3

The sham rule must not repair the delayed deficit.

Expected aggregate:

\[
mismatch_2(FULL,B3)=12.
\]

and:

\[
mismatch_1(FULL,B3)=0.
\]

Thus B2 and B3 store the same number of rules but only the contract-relevant rule closes continuation.

## 10. Native-semantics invariance checks

Producer and verifier must record and require equality of a transition-skeleton digest across FULL/B0/B1/B2/B3 for each variant.

They must also record one executor identifier:

\[
\texttt{dynamic\_qualification\_frontier.apply\_qualification\_event}.
\]

No baseline-specific executor is permitted.

## 11. Independent verifier

A separate verifier must independently reconstruct:

- all 12 variants;
- fixed transition skeletons;
- representation objects;
- the compiler;
- the complete sequence bank.

It must recompute all signatures from native execution without trusting producer matrices.

Acceptance requires:

- exact producer/verifier matrix equality;
- zero verifier mismatch;
- all preregistered baseline dispositions satisfied.

## 12. Gate-C acceptance

Gate C passes only if:

- the same skeleton digest is used across all five representation forms within each variant;
- the same compiler and executor are used;
- representation objects are the only baseline-varying inputs;
- H1 FULL/B0 equality is preserved;
- delayed positive/negative controls reproduce under the fixed interpreter.

## 13. Gate-D acceptance

Gate D passes only if:

\[
B0:\quad H1=0,\ H2=12;
\]

\[
B1:\quad H_{\le2}=0;
\]

\[
B2:\quad H_{\le2}=0;
\]

\[
B3:\quad H1=0,\ H2=12;
\]

and independent verification passes.

## 14. Interpretation

If accepted, the experiment supports:

> Under a fixed native interpreter and fixed transition skeleton, the continuation deficit is repaired by changing the stored continuation representation rather than the semantics. A same-size sham representation fails, while the contract-relevant shared guard closes the complete registered depth-two continuation matrix.

This establishes repair efficacy and representation-level causality.

It does not establish generic repair synthesis, global minimality, or natural prevalence.
