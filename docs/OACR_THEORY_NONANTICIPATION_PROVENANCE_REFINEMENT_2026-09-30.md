# OACR Theory Refinement — Non-Anticipation as Provenance Separation

Date: 2026-09-30

Status: **CORE CONCEPTUAL CORRECTION**

## 1. Correction

The phrase "non-anticipating" must **not** be interpreted as statistical or information-theoretic independence between construction inputs and verification outcomes.

That interpretation would be wrong for deterministic native systems.

In R4, for example, the base graph, candidate delta, registered deletion, and known reachability semantics may be sufficient to derive the correct future distinction from first principles. A successful theorem is supposed to exploit that structure.

The scientific requirement is instead:

\[
\boxed{
\text{no adaptive feedback from realized evaluation outcomes into the construction rule}
}
\]

The distinction is therefore about **provenance and protocol causality**, not impossibility of inference.

---

## 2. Frozen-constructor formulation

Let:

- \(D_{\rm dev}\) be all development evidence authorized before evaluation;
- \(\theta\) be the parameters, rule choices, thresholds, feature definitions, or theorem-derived constructor fixed from \(D_{\rm dev}\);
- \(X_{\rm eval}\) be the frozen evaluation state bank;
- \(\mathcal C_{\rm eval}\) be the frozen evaluation continuation contract;
- \(q\) be a predeclared construction-view map;
- \(Z_{\rm eval}=q(X_{\rm eval},\mathcal C_{\rm eval})\) be the authorized evaluation-time construction view;
- \(g_\theta\) be the frozen constructor;
- \(\kappa_{\rm eval}=g_\theta(Z_{\rm eval})\) be the proposed repair;
- \(Y_{\rm eval}\) be the native evaluation outcome matrix generated under the fixed native interpreter;
- \(O_{\rm eval}\) be the operational quotient derived from \(Y_{\rm eval}\).

A valid non-anticipating protocol requires that

\[
\theta,\;q,\;g_\theta
\]

are fixed without using \(Y_{\rm eval}\) or \(O_{\rm eval}\).

At evaluation time,

\[
\kappa_{\rm eval}
=
g_\theta(
q(X_{\rm eval},\mathcal C_{\rm eval})
)
\]

is generated before any adaptive revision from the realized native evaluation outcomes is allowed.

The fact that \(Z_{\rm eval}\) may mathematically predict \(Y_{\rm eval}\) is **not leakage**. That is precisely what a successful representation principle should do.

---

## 3. Provenance DAG

The intended causal/provenance structure is:

\[
D_{\rm dev}
\longrightarrow
(\theta,q,g)
\]

and independently

\[
(X_{\rm eval},\mathcal C_{\rm eval})
\longrightarrow
Z_{\rm eval}
\longrightarrow
\kappa_{\rm eval},
\]

while

\[
(X_{\rm eval},\mathcal C_{\rm eval},\mathcal N)
\longrightarrow
Y_{\rm eval}
\longrightarrow
O_{\rm eval}.
\]

The prohibited feedback edge is

\[
Y_{\rm eval}
\;\not\longrightarrow\;
(\theta,q,g,\kappa_{\rm eval})
\]

before the evaluation verdict is frozen.

Equivalently, after observing \(Y_{\rm eval}\), one may analyze failure, but any changed constructor belongs to a new development round and requires a fresh evaluation bank or explicitly downgraded authority.

---

## 4. What counts as leakage

Examples of prohibited evaluation feedback include:

1. selecting candidate features because they separate known evaluation collisions;
2. choosing actions because they are known to expose a desired evaluation mismatch;
3. changing thresholds after seeing evaluation closure;
4. defining a certificate directly from evaluation class labels;
5. discarding evaluation states whose outcomes weaken the claim;
6. modifying the constructor until the evaluation partition matches.

These operations create a path

\[
Y_{\rm eval}
\to
\text{construction choice}
\]

and therefore destroy confirmatory authority.

---

## 5. What does not count as leakage

The following are legitimate when frozen in advance:

1. using known native semantics to derive a theorem;
2. computing contract-visible structural predicates on evaluation inputs;
3. inferring future behavior from those predicates;
4. exactly predicting held-out outcomes from first principles;
5. applying a predeclared algorithm to each evaluation instance;
6. using the same frozen contract to produce both successful and failed predictions.

A perfect theoretical predictor is not circular merely because it predicts perfectly.

The issue is whether it was **fit to the realized evaluation answers**.

---

## 6. Three authority levels, revised

### Level 0 — outcome-fitted / oracle encoding

The representation rule is chosen using the realized evaluation quotient.

This establishes only ex post representability.

### Level 1 — development-fitted, evaluation-frozen

The constructor may be learned or selected using authorized development outcomes, but is frozen before a separate evaluation bank is revealed.

This establishes generalization of the repair rule across the declared split.

### Level 2 — theory/contract-derived, evaluation-frozen

The constructor is fixed from domain semantics, contract structure, and predeclared carrier primitives without fitting to augmented-state outcome labels.

It is then applied unchanged to the frozen evaluation bank.

R4 is a candidate Level-2 instance.

This hierarchy is about **how constructor choices obtain authority**, not whether the constructor can logically infer the evaluation result.

---

## 7. Relation to bidirectional repair

For bidirectional repair, the strongest confirmatory protocol requires the **same frozen certificate rule** to determine both:

\[
\Phi^+:
R_{\rm coarse}\to R_{\rm repaired}
\]

and

\[
\Phi^-:
R_{\rm fine}\to R_{\rm repaired},
\]

before evaluation outcomes are used for revision.

If both paths independently land on

\[
O_{\mathcal C}
\]

under native replay, the evidence is stronger than separately outcome-fitting each endpoint.

Thus non-anticipation and bidirectionality reinforce one another:

\[
\boxed{
\text{one frozen predictive certificate}
+
\text{two opposite repair directions}
+
\text{one held-out native quotient}
}
\]

is a particularly strong identification pattern.

---

## 8. Implication for the manuscript

Avoid statements such as:

> the constructor has no information about the verification outcomes.

That can be false in deterministic systems because permitted structural inputs may determine those outcomes.

Prefer:

> the construction rule and its admissible inputs were fixed without adaptive use of the realized evaluation outcomes; the rule was then applied to the frozen evaluation instances before native replay determined whether its predicted distinctions were exact.

This is both stronger scientifically and more defensible formally.

---

## 9. Implication for the future anti-circularity contribution

The anti-circularity section should be built around four objects:

1. **authority provenance** — where each design choice came from;
2. **freeze boundary** — when the constructor became immutable;
3. **evaluation feedback prohibition** — which realized outcomes cannot flow back into the current evaluation round;
4. **promotion rule** — any post-evaluation change becomes development and requires fresh confirmatory evidence.

This turns preregistration, forbidden reads, producer/verifier separation, matched sham controls, and independent replay into a single framework.

