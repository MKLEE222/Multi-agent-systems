# OACR Identification Prior-Art Boundary

Date: 2026-09-30

Status: **BOUNDARY FROZEN FOR CLAIM DISCIPLINE**

The anti-circularity contribution must not claim novelty for generic ideas that are already established across statistics, machine learning, data mining, neuroscience, and preregistration methodology.

## 1. Established prior art that OACR must inherit, not rename

### Circular analysis / double dipping

Kriegeskorte et al., "Circular analysis in systems neuroscience: the dangers of double dipping," Nature Neuroscience 12, 535–540 (2009), DOI 10.1038/nn.2303.

Established point:

> using the same data for selection and selective analysis can create circular inference and distorted results.

OACR must not claim novelty for the general principle that selection and evaluation should be separated.

### Data leakage / learn-predict separation

Kaufman, Rosset, Perlich, and Stitelman, "Leakage in data mining: formulation, detection, and avoidance," KDD 2011 / extended TKDD 2012, DOI 10.1145/2020408.2020496 and 10.1145/2382577.2382579.

Established point:

> target information that should not legitimately be available to the modeler can leak into model construction; learn-predict separation is a general remedy.

OACR must not claim novelty for the generic concept of forbidden target information.

### Adaptive data analysis / holdout reuse

Dwork et al., "The reusable holdout: Preserving validity in adaptive data analysis," Science 349(6248), 636–638 (2015), DOI 10.1126/science.aaa9375.

Established point:

> repeated adaptive use of holdout feedback can overfit the holdout and undermine validity.

OACR must not claim that post-evaluation adaptation is a newly discovered threat.

### Preregistration in machine learning

Machine-learning preregistration has been explicitly advocated and trialed, including NeurIPS preregistration workshops.

A recent directly relevant methodological position is:

Michelle Vaccaro, "Position: Preregister Experiments with AI Agents," ICML 2026, PMLR 306.

Established point:

> model choice, prompts, settings, and outcome-contingent redesign create researcher degrees of freedom that can be controlled by preregistration.

OACR must not claim novelty for preregistration or freeze-before-evaluation as general methodology.

### Benchmark feedback and test-set overfitting

Ishida, Lodkaew, and Yamane, "CapBencher: Give Your LLM Benchmark a Built-in Alarm for Test-Set Overfitting," ICML 2026, PMLR 306.

Established point:

> even private or controlled benchmarks can be overfit through repeated feedback loops; benchmark design can include leakage/gaming alarms.

OACR must not claim novelty for the general observation that benchmark feedback can induce test-set overfitting.

---

## 2. What is specific to representation repair

OACR's narrower identification problem is structurally different from ordinary train/test leakage.

The same future native outcomes play two roles:

1. they define the operational target quotient
   \[
   O_{\mathcal C};
   \]
2. they are also used to judge whether a proposed representation repair is exact.

Therefore if the repair constructor is allowed to read those realized outcomes, it can directly encode the target quotient.

At the partition level:

\[
P_{\rm coarse}
\preceq
O_{\mathcal C}
\preceq
P_{\rm fine}
\]

and quotient-visible repair can trivially use:

\[
P_{\rm coarse}\vee O_{\mathcal C}
=
O_{\mathcal C},
\]

\[
P_{\rm fine}\wedge O_{\mathcal C}
=
O_{\mathcal C}.
\]

Thus:

\[
\boxed{
\text{exactness is not sufficient evidence of a predictive repair principle}
}
\]

when the exact target partition was available during construction.

This is the representation-repair-specific circularity that OACR should foreground.

---

## 3. OACR's candidate independent object

The anti-circularity contribution should be stated as the conjunction of:

\[
\boxed{
\text{native-contract target}
+
\text{representation repair}
+
\text{explicit constructor authority}
+
\text{bidirectional correction}
+
\text{native replay verification}
}
\]

not as "we preregister experiments."

The relevant object is:

> a repair constructor whose choices are frozen without adaptive use of the realized evaluation outcome quotient, then applied to a persistent representation whose adequacy is subsequently determined by the same frozen native continuation contract.

This becomes particularly meaningful because repair can proceed from either side:

\[
R_{\rm coarse}
\to
R^\star
\leftarrow
R_{\rm fine}.
\]

A single frozen certificate that correctly supports both additive and subtractive repair is stronger than two separately outcome-fitted corrections.

---

## 4. Why the provenance DAG matters

Generic train/test separation says:

\[
\text{training data}
\not\leftarrow
\text{test labels}.
\]

OACR needs a more structured dependency account because the constructor may legitimately inspect evaluation-instance structure and may even derive future behavior exactly from native semantics.

The forbidden object is not "information about the future" in the abstract.

The forbidden adaptive edge is:

\[
Y_{\rm eval}
\not\longrightarrow
(\Theta,q,g,\kappa)
\]

after the evaluation round is frozen.

Allowed:

\[
(X_{\rm eval},\mathcal C_{\rm eval})
\to
Z_{\rm eval}
\to
\kappa_{\rm eval}
\]

using a predeclared constructor.

This distinction prevents a false claim of statistical independence while preserving the actual anti-circularity condition.

---

## 5. What the executable R4 demo establishes

The frozen R4 anti-circularity demonstration gives:

\[
A0_{\rm oracle}: U=E=0,
\]

\[
A2_{\rm predictive}: U=E=0,
\]

\[
A2_{\rm sham}: U=E=0.7556880438822081.
\]

All use:

- 22 retained records;
- 23 representation blocks.

The methodological lesson is not that oracle repair is bad because it fails.

It succeeds perfectly.

That is precisely the point:

\[
\boxed{
\text{an outcome-aware constructor can look as exact as a predictive constructor}
}
\]

unless provenance authority is tracked.

The same-cost sham then shows that capacity/block count alone does not explain predictive exactness.

---

## 6. What SQEC adds

SQEC B2/B3 provides a prospective matched intervention:

\[
cost(B2)=cost(B3)=1.
\]

Only the contract-relevant B2 repair closes the registered H2 deficit.

This is stronger than a retrospective oracle demonstration because the relevant and sham repairs were frozen before v2 execution.

Thus R4 and SQEC play different roles:

- R4: formal oracle-triviality + historically frozen A2 constructor + executable retrospective leakage demonstration;
- SQEC: prospectively frozen relevant-vs-sham causal comparison under a fixed native interpreter.

---

## 7. What OACR should not claim

Do not claim:

- first framework to avoid circular evaluation;
- first use of preregistration in AI/ML;
- first formalization of data leakage;
- first separation of training/development and testing;
- first warning about adaptive benchmark overfitting;
- statistical unbiasedness merely from provenance freezing.

Do not call the authority framework a replacement for statistical generalization theory.

---

## 8. What OACR can plausibly claim if the full gate passes

A defensible formulation is:

> Existing work establishes the dangers of double dipping, target leakage, adaptive holdout reuse, and outcome-contingent experimental redesign. OACR addresses a representation-repair-specific form of circularity: the future native outcomes used for evaluation also induce the target operational quotient, so outcome-visible construction can encode the answer while appearing exactly repaired. We therefore make constructor authority explicit, separate frozen construction from verification-only native outcomes, and combine this provenance constraint with matched sham repairs and independent replay. This turns anti-circularity from a generic preregistration slogan into an auditable condition on contract-relative representation repair.

This wording inherits established methodology while preserving the narrower OACR contribution.
