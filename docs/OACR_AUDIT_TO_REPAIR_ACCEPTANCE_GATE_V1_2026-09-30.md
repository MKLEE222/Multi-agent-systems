# OACR Audit -> Repair Acceptance Gate v1

**Date:** 2026-09-30  
**Authority:** \`audits/mother_problem_redesign_20260929/NATIVE_CONTRACT_AUDIT_TO_REPAIR_COLD_START_REVIEW_20260930.md\`  
**Status:** binding acceptance specification for the paper identity

## Target paper identity

The two-stage slogan

\[
\text{native-contract audit}
\rightarrow
\text{representation repair}
\]

is not sufficient for acceptance.

The accepted identity must be:

\[
\boxed{
\text{native-contract adequacy audit}
\rightarrow
\text{certificate-constrained bidirectional representation repair}
\rightarrow
\text{native closure verification}
}
\]

## Gate A — Unified repair formalism

Required manuscript objects:

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
\Phi_{\mathcal C,\kappa}:R\mapsto R'.
\]

A repair record must freeze:

- repair certificate \(\kappa\);
- repair information boundary \(\mathcal I_{\rm repair}\);
- native continuation contract \(\mathcal C\);
- representation transform \(\Phi\).

Acceptance obligations:

### O1 — closure

\[
U_\mu(R';\mathcal C)=0.
\]

### O2 — no excess for exact finite repair

\[
E_\mu(R';\mathcal C)=0.
\]

If exactness is not claimed, directional residuals must be reported instead.

### O3 — native-semantics invariance

The concrete/native executor and registered continuation contract are unchanged:

\[
\mathcal C'=\mathcal C.
\]

Only representation changes.

### O4 — frozen information boundary

Repair construction may use only preregistered information in \(\mathcal I_{\rm repair}\). Prohibited held-out native outcome matrices may not be inspected.

**Gate A passes only when the manuscript formalism and contribution language explicitly contain these objects and obligations.**

## Gate B — R4 bidirectional repair

No new scientific carrier is required.

Using the accepted R4-building result, the paper must instantiate both:

\[
\Phi_{\mathcal C}^{+}(R_{\rm current})
=
R_{\rm gate}
\]

and

\[
\Phi_{\mathcal C}^{-}(R_{\rm full})
=
R_{\rm gate}.
\]

Required accounting:

- additive direction:
  - current representation carries 0 per-state delta records;
  - repair adds the 22 contract-active deltas;
- subtractive direction:
  - full representation carries 271 per-state deltas;
  - repair removes the 249 contract-inactive deltas;
- both induce the same accepted 23-block partition;
- both reach
  \[
  U_\mu=E_\mu=0;
  \]
- all 17,408 registered native replay cells remain exact.

**Gate B passes only when this is written as one bidirectional correction result rather than two unrelated representation comparisons.**

## Gate C — SQEC fixed-interpreter representation repair

Required implementation architecture:

1. one fixed native transition executor;
2. one fixed compiler/interpreter from representation object to native event interface;
3. one explicit representation object that stores continuation-interface guard rules;
4. FULL / PROJECTED / REPAIRED differ only in the representation object;
5. the transition skeleton, state dynamics, event alphabet, sequence bank, executor, and registered continuation contract remain byte-identical across representations.

Direct mutation of native event semantics as the repair operation is not sufficient.

The clean confirmatory run must re-establish:

\[
mismatch_1(FULL,PROJECTED)=0
\]

and prospective delayed H2 divergence in the predeclared positive controls.

## Gate D — Matched SQEC repair baselines

Freeze and execute the same fresh family under four representation repairs:

### B0 — no repair

Projected representation contains no observation guard.

Required:

\[
mismatch_2(FULL,B0)>0.
\]

### B1 — full restore

Representation stores two separate per-observation-event guard clauses.

Required:

\[
mismatch_{\le2}(FULL,B1)=0.
\]

Representation accounting:

\[
cost(B1)=2\text{ guard clauses}.
\]

### B2 — shared canonical repair

Representation stores one shared guard rule referenced by both observation outcomes.

Required:

\[
mismatch_{\le2}(FULL,B2)=0.
\]

Representation accounting:

\[
cost(B2)=1\text{ shared rule}.
\]

### B3 — sham repair

Representation stores one same-size shared rule on a preregistered irrelevant coordinate/rule.

Required:

\[
mismatch_1(FULL,B3)=0
\]

and:

\[
mismatch_2(FULL,B3)>0.
\]

Thus adding arbitrary representation precision is insufficient.

### Independent verification

A separate verifier must reconstruct:

- all frozen variants;
- all representation objects;
- the complete depth \(\le2\) sequence bank;
- every native signature.

It must not trust producer outcome matrices.

**Gate D passes only if B0/B1/B2/B3 all satisfy their preregistered disposition and the independent verifier has zero verifier mismatches.**

## Gate E — certificate-selection challenge

**Strong-paper upgrade; not required for A–D acceptance.**

A frozen repair-candidate library contains the correct certificate and multiple irrelevant candidates.

A deterministic constructor may use only:

- the frozen continuation contract;
- declared static dependency information;
- the audit deficit class permitted by \(\mathcal I_{\rm repair}\).

It may not inspect held-out continuation outcomes.

Preferred target:

\[
\mathcal C+D
\rightarrow
\kappa_{\rm correct}
\rightarrow
R'.
\]

## Final acceptance condition

The paper identity is accepted only if:

\[
A\land B\land C\land D
\]

all pass.

At that point the safe one-sentence claim is:

> We audit implemented persistent representations against prospectively registered native transformation contracts, diagnose both missing and unjustified distinctions, and use contract-derived certificates to add or remove representation structure while leaving native operations fixed; the repaired representation is accepted only when it closes the registered continuation under independent native replay.

Do not claim generic repair synthesis unless Gate E is separately completed.
