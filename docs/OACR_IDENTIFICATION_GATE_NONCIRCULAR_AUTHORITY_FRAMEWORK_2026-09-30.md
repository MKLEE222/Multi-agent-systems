# OACR Identification Gate — Non-Circular Authority and Provenance Framework

Date: 2026-09-30

Status: **CORE IDENTIFICATION SPECIFICATION — to be promoted only after executable leakage audit**

This document defines the second load-bearing object of OACR:

\[
\boxed{
\text{non-circular representation repair under explicit evidence authority}
}
\]

The aim is not merely to say that experiments were preregistered or independently verified. The aim is to formalize when a representation-repair result has confirmatory authority and when apparently exact repair is only a post-hoc encoding of observed outcomes.

---

## 1. Why exact repair alone is not enough

Let a frozen native continuation contract \(\mathcal C\) and native interpreter \(\mathcal N\) induce a verification outcome matrix

\[
Y^{\rm eval}_{\mathcal C}
\]

and operational quotient

\[
O^{\rm eval}_{\mathcal C}.
\]

If a repair constructor may inspect this quotient directly, then exact repair is weak evidence.

At the partition level, whenever

\[
P_{\rm coarse}
\preceq
O^{\rm eval}_{\mathcal C}
\preceq
P_{\rm fine},
\]

the oracle constructor can simply encode the target quotient.

Thus the scientific question is not:

> Can we construct a representation whose partition equals the observed quotient?

It is:

> Can a rule fixed without adaptive access to the realized evaluation outcomes predict the distinctions that the frozen native continuation later verifies as necessary and sufficient?

---

## 2. Evidence-authority tuple

Define an evaluation protocol by

\[
\Pi=
(
D_{\rm dev},
\Theta,
X_{\rm eval},
\mathcal C_{\rm eval},
q,
g_\Theta,
\mathcal N,
V
).
\]

Where:

- \(D_{\rm dev}\): all authorized development evidence;
- \(\Theta\): constructor choices fixed from authorized evidence;
- \(X_{\rm eval}\): frozen evaluation state bank;
- \(\mathcal C_{\rm eval}\): frozen evaluation continuation contract;
- \(q\): predeclared map from evaluation inputs to constructor-visible information;
- \(g_\Theta\): frozen repair/certificate constructor;
- \(\mathcal N\): fixed native interpreter/executor;
- \(V\): independent verification procedure.

The constructor receives

\[
Z_{\rm eval}
=
q(
X_{\rm eval},
\mathcal C_{\rm eval}
)
\]

and outputs

\[
\kappa_{\rm eval}
=
g_\Theta(Z_{\rm eval}).
\]

Only after \(\kappa_{\rm eval}\) is frozen is native replay used to generate

\[
Y^{\rm eval}_{\mathcal C}
\]

and

\[
O^{\rm eval}_{\mathcal C}.
\]

---

## 3. Provenance DAG

A confirmatory evaluation should obey the following allowed dependency graph:

\[
D_{\rm dev}
\longrightarrow
(\Theta,q,g_\Theta)
\]

\[
(X_{\rm eval},\mathcal C_{\rm eval})
\longrightarrow
Z_{\rm eval}
\longrightarrow
\kappa_{\rm eval}
\]

\[
(X_{\rm eval},\mathcal C_{\rm eval},\mathcal N)
\longrightarrow
Y^{\rm eval}_{\mathcal C}
\longrightarrow
O^{\rm eval}_{\mathcal C}.
\]

The key prohibited adaptive edge is

\[
\boxed{
Y^{\rm eval}_{\mathcal C}
\not\longrightarrow
(\Theta,q,g_\Theta,\kappa_{\rm eval})
}
\]

before the evaluation verdict is frozen.

This is a provenance restriction, not an information-theoretic independence claim.

A theorem-derived constructor may perfectly predict the evaluation outcome from permitted structural information. That is success, not leakage.

---

## 4. Freeze boundary

A valid evaluation round has a **freeze event**

\[
\tau_{\rm freeze}.
\]

Before \(\tau_{\rm freeze}\), authorized development is allowed.

After \(\tau_{\rm freeze}\), the following objects are immutable for that evaluation round:

- evaluation state inclusion/exclusion rule;
- action/continuation contract;
- representation feature definitions;
- constructor algorithm;
- thresholds and costs;
- native interpreter version;
- outcome coordinates;
- success/failure criteria.

The evaluation result becomes confirmatory only if no realized evaluation outcome feeds back into these choices before verdict registration.

---

## 5. Authority levels

### A0 — Oracle / outcome-fitted

Constructor choices use the realized evaluation quotient or labels derived from it.

Permitted claim:

> the target quotient is representable by the chosen representation family.

Not permitted:

> the contract predicted which distinctions were required.

### A1 — Development-fitted, evaluation-frozen

Constructor choices may use authorized development outcomes.

A separate evaluation bank/contract is frozen before evaluation outcomes are revealed.

Permitted claim:

> the repair rule generalizes from development to the declared evaluation distribution.

### A2 — Contract-derived, evaluation-frozen

Constructor choices are fixed from:
- native semantics;
- declared contract structure;
- carrier-native structural information;
- predeclared rules.

No augmented-state outcome labels are used to fit the constructor.

Permitted claim:

> the continuation contract and declared carrier structure predict the required representation distinctions.

R4 is a candidate A2 result.

### A3 — Independent cross-carrier confirmation

An already frozen repair principle is transferred to a new carrier or task family without changing the principle after seeing target-carrier evaluation outcomes.

This is the strongest empirical authority level currently envisioned, but it should only be used if a genuinely shared principle exists.

---

## 6. Leakage operations

The following operations create a forbidden path from realized evaluation outcomes back into the current evaluation round.

### Feature leakage
Choose or redefine a feature because it separates known evaluation failures.

### Action leakage
Select future operations because they expose a desired mismatch in the evaluation states.

### Threshold leakage
Tune a threshold after seeing evaluation closure.

### State leakage
Drop or replace evaluation states because their outcomes weaken the result.

### Certificate leakage
Derive the retained distinction set directly from evaluation operational-class labels.

### Iterative repair leakage
Repeatedly modify the constructor until the same evaluation bank closes.

### Narrative leakage
Promote a post-hoc exploratory statistic to a prospectively authorized confirmatory claim without downgrading its authority.

---

## 7. Promotion rule

Post-evaluation analysis is allowed.

However, once evaluation outcomes are inspected, any change to:

\[
(\Theta,q,g_\Theta,\mathcal C,X)
\]

creates a new development round.

The modified rule cannot retain the original evaluation bank as fresh confirmatory evidence.

It must either:

1. be tested on a new untouched evaluation bank; or
2. be explicitly labelled exploratory / retrospective.

This is the **authority promotion rule**.

---

## 8. Same-contract requirement

A representation comparison is strongest when all competing representations face the same:

- evaluation states;
- continuation contract;
- native interpreter;
- outcome coordinates;
- weighting scheme.

This prevents apparent superiority from being manufactured by representation-specific evaluation panels.

For representations \(R_1,\ldots,R_k\), comparison authority therefore requires:

\[
\mathcal C_1=\cdots=\mathcal C_k
\]

unless the difference in contract is itself the object being studied.

---

## 9. Matched sham control

A repair claim is stronger when the experiment distinguishes:

\[
\text{adding structure}
\]

from

\[
\text{adding contract-relevant structure}.
\]

Let \(\kappa_{\rm rel}\) be the predicted relevant repair and \(\kappa_{\rm sham}\) a matched-cost irrelevant repair.

A clean causal pattern is:

\[
c(\kappa_{\rm rel})
=
c(\kappa_{\rm sham}),
\]

but

\[
\Delta_{\rm rel}
>
\Delta_{\rm sham}.
\]

The SQEC B2/B3 contrast is a candidate instance:
- same-size rule addition;
- relevant guard closes the H2 mismatch;
- sham guard does not.

This control should be elevated from “ablation” to an identification device.

---

## 10. Independent verifier

Producer/verifier separation addresses implementation circularity.

The producer may:
- instantiate states;
- construct the proposed repair;
- run native outcomes.

The verifier should independently reconstruct:
- frozen inputs;
- state/action matrix;
- representation partition;
- operational quotient;
- mismatch counts;
- claimed hashes.

A producer-verifier match does not by itself prove non-circular feature selection, but it closes a different failure mode:

\[
\text{implementation self-confirmation}.
\]

OACR therefore separates:

1. **design circularity** — evaluation outcomes influence constructor choice;
2. **implementation circularity** — the same code path produces and certifies the result.

Both must be controlled.

---

## 11. Authority ledger

Every main empirical claim should carry an authority ledger with fields:

| Field | Meaning |
| --- | --- |
| Development evidence | What was seen before freeze |
| Freeze point | Commit / protocol / timestamp |
| Evaluation bank | Exact untouched states |
| Contract | Exact frozen operations |
| Constructor-visible inputs | What the rule may inspect |
| Forbidden inputs | What the rule may not inspect |
| Native interpreter | Fixed executor/version |
| Verification-only outputs | Outcomes revealed after construction |
| Sham/control | Matched irrelevant comparator if applicable |
| Independent verifier | Separate implementation / replay |
| Post-hoc analyses | Explicitly downgraded exploratory outputs |
| Promotion status | A0/A1/A2/A3 |

This ledger should exist for at least R4, SQEC, Git, and the future learned natural carrier.

---

## 12. R4 authority map

Candidate classification: **A2**.

### Constructor-visible
- frozen base DAG;
- candidate redundant edge endpoint;
- registered deletion contract;
- known reachability semantics.

### Forbidden for constructor fitting
- augmented-state native outcome matrix;
- final operational class labels;
- post-hoc subcontract success labels.

### Constructor
- retain delta iff some registered deletion destroys its base reachability.

### Verification
- independent replay over all 17,408 state-action cells.

### Theory upgrade
The one-delta exactness theorem now predicts that this A2 constructor realizes the exact operational quotient for the declared carrier class.

This is stronger than merely reporting that the gate happened to work on R4.

---

## 13. SQEC authority map

Candidate classification: **A1/A2 boundary; must be audited carefully before promotion**.

Known strengths:
- frozen compiler and executor;
- frozen event alphabet;
- complete registered sequence contract;
- relevant and sham guards have matched size;
- independent verifier reconstructs the matrix.

Open question:
- exactly which evidence was used to identify the relevant guard before the final confirmatory matrix?

The answer determines whether the result is A1 or A2.

No stronger authority label should be used until that provenance is reconstructed from commits/protocols.

---

## 14. Future learned-carrier authority map

The learned extension should be designed around the authority framework before any large run.

Recommended structure:

### Development
Use an explicit development split to:
- choose representation statistic;
- choose repair rule;
- choose thresholds;
- estimate any implication model.

### Freeze
Commit:
- benchmark subset rules;
- model/editor versions;
- shared continuation panels;
- intervention cost;
- sham intervention;
- success metrics.

### Evaluation
Apply the frozen constructor to untouched units.

### Verification
Measure future native/editing behavior only after interventions are frozen.

### Promotion
Any rule modification after evaluation requires a fresh held-out split.

This prevents the natural-scale expansion from becoming a large but circular benchmark exercise.

---

## 15. Executable leakage counterexample target

Identification Gate I5 requires an executable demonstration.

The preferred experiment is:

### Oracle constructor
Read the evaluation operational quotient and select exactly the distinctions needed to encode it.

Expected result:

\[
U=E=0.
\]

### Frozen predictive constructor
Use only contract-visible information.

Evaluate independently.

### Sham / wrong constructor
Use matched complexity without outcome-derived targeting.

The demonstration should make the central point obvious:

\[
\boxed{
\text{exact repair can be trivial under outcome access}
}
\]

while

\[
\boxed{
\text{exact repair under a frozen predictive rule is the substantive result}
}
\]

This should be shown on a carrier where the three constructors can be implemented cleanly, likely R4 first.

---

## 16. Identification theorem target

A useful formal statement is not a theorem claiming statistical unbiasedness.

Instead, define an **authority-preserving evaluation transformation**:

A transformation from development protocol to evaluation verdict is authority-preserving when no adaptive path from realized evaluation outcomes reaches the frozen constructor before verdict registration.

Then prove simple compositional properties:

- independent native replay preserves authority;
- independent verifier preserves authority;
- adding post-hoc analysis does not alter the original verdict if it is explicitly labelled exploratory;
- modifying the constructor after evaluation destroys freshness of the current evaluation bank;
- reusing the same evaluation bank after modification cannot restore A1/A2 authority.

These results are protocol semantics, not probabilistic guarantees.

Their value is to make the anti-circularity claim precise and auditable.

---

## 17. Main paper contribution candidate

The anti-circularity contribution should eventually be stated approximately as:

> Representation repair is particularly vulnerable to post-hoc circularity because the target partition can be read from the same future outcomes used to validate the repair. We therefore distinguish ex post quotient encoding from non-circular predictive repair using an explicit authority/provenance protocol: constructor choices are frozen before evaluation outcomes can adapt them, matched sham repairs isolate contract relevance from added capacity, and independent native replay plus independent verification certify closure. This framework turns preregistration and reproducibility into an identification condition for representation repair.

This is potentially a main contribution, not an appendix procedure.

---

## 18. Acceptance checklist

### Formal
- [ ] Authority tuple and freeze boundary are unambiguous.
- [ ] Provenance restriction is not misdescribed as statistical independence.
- [ ] A0/A1/A2/A3 labels have no hidden overlap.
- [ ] Promotion rule handles post-hoc theory development correctly.

### Empirical
- [ ] R4 authority ledger reconstructed from repository history.
- [ ] SQEC authority ledger reconstructed from repository history.
- [ ] Git authority ledger reconstructed.
- [ ] Future learned protocol frozen before natural-scale evaluation.

### Demonstration
- [ ] Executable oracle-leakage counterexample.
- [ ] Matched sham control.
- [ ] Independent verifier.
- [ ] Clear example where post-hoc adaptation forces authority downgrade.

### Writing
- [ ] Main text explains why exact closure is not sufficient evidence.
- [ ] Anti-circularity appears in contribution list.
- [ ] Engineering vocabulary is reduced; authority logic is foregrounded.
