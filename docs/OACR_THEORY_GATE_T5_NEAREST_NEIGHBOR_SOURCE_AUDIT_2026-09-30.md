# OACR Theory Gate T5 — Source-Level Nearest-Neighbor Audit

Date: 2026-09-30

Status: **T5 WORKING PASS — manuscript integration and citation polishing pending**

This audit asks whether the current OACR theory object survives direct comparison with the strongest adjacent abstraction/refinement/repair lines.

The acceptance criterion is not that OACR has more theorems. It is that a reviewer familiar with these lines can identify an independent theoretical object without relying on carrier novelty or terminology changes.

# 1. Generalized strong preservation

Primary source:

Francesco Ranzato and Francesco Tapparo, "Generalized Strong Preservation by Abstract Interpretation," Journal of Logic and Computation 17(1), 157–197 (2007), DOI 10.1093/logcom/exl035.

Established result:

- a specification language \(L\) determines which semantic distinctions an abstract model must preserve;
- strong preservation is related precisely to completeness in abstract interpretation;
- minimally refining an abstract model to become strongly preserving can be formulated as domain refinement;
- the refined strongly preserving model exists and is characterized as a greatest fixed point;
- standard behavioral equivalences and partition-refinement algorithms fit this framework.

## Consequence for OACR claims

OACR must **not** claim novelty for:

- specification-relative state equivalence;
- the idea that an intermediate quotient may preserve exactly the distinctions needed by a semantic requirement;
- minimal refinement toward a sufficient abstract model;
- partition refinement as such.

## Residual OACR object

Strong preservation begins from a semantic language/property family whose truth must be preserved.

OACR instead takes an implemented persistent representation and a finite family of **future native operations** and defines:

\[
x\sim_{\mathcal C}y
\iff
B_{\mathcal N,\mathcal C}(x)
=
B_{\mathcal N,\mathcal C}(y).
\]

The research question is then not only whether an abstraction is too coarse for a language, but whether the deployed representation is:

\[
\text{too coarse},
\qquad
\text{exact},
\qquad
\text{or unnecessarily fine}
\]

for the declared future-use contract.

This distinction alone is not sufficient for novelty, but it remains an independent problem formulation when combined with the repair and authority objects below.

# 2. Abstract Interpretation Repair (AIR)

Primary source:

Roberto Bruni, Roberto Giacobazzi, Roberta Gori, and Francesco Ranzato, "Abstract Interpretation Repair," PLDI 2022, DOI 10.1145/3519939.3523453.

Established result:

- program verification via abstract interpretation may be locally incomplete and produce false alarms;
- AIR uses local completeness to repair abstract domains;
- its main result gives necessary and sufficient conditions for existence of an optimal locally complete refinement, the pointed shell;
- it defines forward and backward repair strategies along a given abstract computation.

AIR explicitly presents itself as an abstraction-repair analogue of CEGAR.

## Consequence for OACR claims

OACR must **not** say:

- AIR only diagnoses but does not repair;
- AIR lacks optimality theory;
- AIR has only one repair direction;
- refinement of a representation/domain toward a sufficient semantics is new.

AIR is a stronger theoretical neighbor than an ordinary related-work citation and should be treated as such.

## Residual OACR object

The meanings of "forward/backward" and "bidirectional" are different.

AIR's two strategies are alternative ways to **refine a locally incomplete abstract domain** along an abstract/concrete computation.

OACR's bidirectionality is between two representation errors:

\[
P_{\rm coarse}
\preceq
O_{\mathcal C}
\preceq
P_{\rm fine},
\]

with:

\[
R_{\rm coarse}
\xrightarrow{\Phi^+}
R^\star
\xleftarrow{\Phi^-}
R_{\rm fine}.
\]

The subtractive direction is not another search direction for refinement. It removes distinctions that have no effect under the future native contract.

The stronger independent OACR claim is therefore not "we repair abstractions in two directions." It is:

> a native continuation contract induces a two-sided adequacy target for an implemented persistent representation, and a frozen constructor may add or remove stored distinctions to reach the same operational quotient.

# 3. CEGAR

Primary source:

Edmund Clarke, Orna Grumberg, Somesh Jha, Yuan Lu, and Helmut Veith, "Counterexample-Guided Abstraction Refinement," CAV 2000, DOI 10.1007/10722167_15; extended JACM 2003.

Established result:

- an automatically generated abstraction may admit a spurious counterexample;
- the counterexample is analyzed;
- the abstraction is iteratively refined to remove the spurious behavior;
- counterexample feedback is intentionally part of the repair/refinement loop.

## Consequence for OACR claims

OACR must not claim novelty for:

- iterative abstraction refinement;
- using verification failures to identify insufficient distinctions;
- counterexample-driven improvement.

## Residual OACR object

CEGAR and OACR impose different authority semantics.

In CEGAR:

\[
\text{counterexample}
\to
\text{refinement}
\]

is the intended algorithm.

In the strongest OACR evaluation:

\[
Y_{\rm eval}
\not\to
(\Theta,q,g,\kappa)
\]

for the current confirmatory round.

This is not because outcome-guided repair is illegitimate in general. It answers a different scientific question:

> can contract-visible structure predict the distinctions required by future native execution before the held-out outcome quotient is allowed to adapt the constructor?

Therefore OACR should position non-anticipation as an **evaluation authority condition**, not as a criticism of CEGAR's algorithmic design.

# 4. Verifix

Primary source:

"Verifix: Verified Repair of Programming Assignments," ACM Transactions on Software Engineering and Methodology, DOI 10.1145/3510418.

Established result includes explicit theorems for:

- soundness of the repaired program relative to the reference output behavior;
- relative completeness of edge repair and conditional relative completeness of the overall repair;
- minimality of each edge repair under the MaxSMT/pMaxSMT repair space;
- global minimality only under additional optimal node/variable-alignment conditions.

## Consequence for OACR claims

Verifix is an upper-bound example of a repair paper with a clear correctness target, constructive algorithm, and explicit soundness/completeness/minimality theory.

OACR should not imply that "repair plus theorem" is itself distinctive.

## Residual OACR object

Verifix's target is supplied by the reference program and alignment/correctness relation.

OACR makes the **representation target** itself contract-relative:

\[
\mathcal C
\mapsto
O_{\mathcal C}.
\]

Its main theoretical question is which persistent distinctions are necessary and sufficient for future native use while the native executor remains fixed.

Thus:

\[
\text{Verifix: fixed correctness target}
\to
\text{program repair},
\]

whereas:

\[
\text{OACR: native future-use contract}
\to
\text{operational quotient}
\to
\text{representation adequacy/repair}.
\]

This distinction survives only if OACR keeps the operational-target derivation and two-sided representation error central.

# 5. SMT-based summary repair

Primary source:

Sepideh Asadi et al., "SMT-based verification of program changes through summary repair," Formal Methods in System Design 60, 350–380, DOI 10.1007/s10703-023-00423-0.

Established result:

- function summaries from prior program versions are reused for incremental bounded model checking;
- invalid summaries are repaired rather than simply discarded;
- repair can **weaken** summaries by removing broken conjuncts;
- if needed, summaries are **strengthened** by recomputing interpolants and adding missing information;
- the procedure uses summary-validation failures and SMT reasoning to drive repair;
- experiments on primarily Linux device-driver versions report an order-of-magnitude speedup over prior approaches.

## Important correction for OACR

This work means OACR cannot use the slogan:

> prior repair methods only add information, whereas we can both add and remove information.

That claim would be false.

Summary repair already contains explicit weakening and strengthening.

## Residual OACR object

The two works optimize different semantics.

Summary repair asks:

> how should an over-approximating verification summary be adapted after the program changes so that incremental safety verification remains reusable and efficient?

Repair is allowed to inspect the validation failure on the new program and react to it.

OACR asks:

> for a fixed native executor and declared future-operation contract, which distinctions should a persistent representation retain, and can a frozen constructor predict them before the held-out operational quotient feeds back into repair selection?

Thus the distinction is not additive versus subtractive repair.

It is:

\[
\boxed{
\text{verification-summary adaptation}
\quad\text{vs.}\quad
\text{non-anticipating contract-relative representation adequacy}
}
\]

together with an exact operational quotient and two-sided under/over-refinement criterion.

# 6. Comparison matrix

| Line | Primary object | Target semantics | Defect | Repair feedback | Direction | OACR residual distinction |
| --- | --- | --- | --- | --- | --- | --- |
| Strong preservation | Abstract model/domain | Specification language \(L\) | Not strongly preserving / incomplete | Semantic operators/language | Refinement | Future native-operation quotient over an implemented persistent representation; over-refinement also counted |
| AIR | Abstract domain | Local completeness along computation | False alarms/local incompleteness | Abstract/concrete computation | Optimal refinement; forward/backward strategies | Two-sided coarse/fine error and common operational target under explicit evaluation authority |
| CEGAR | Verification abstraction | Property/counterexample semantics | Spurious counterexample | Counterexample intentionally drives refinement | Refinement loop | Held-out outcome feedback is prohibited for a confirmatory constructor; different scientific question |
| Verifix | Student program | Reference-program equivalence/correctness | Incorrect implementation | Verification/MaxSMT | Program modification | Target representation quotient is induced by future native use; executor stays fixed |
| Summary repair | Function summaries | Incremental safety-verification summaries | Old summary invalid/imprecise after change | Summary-validation failure drives repair | Weakening + strengthening | Outcome-independent/frozen representation rule evaluated against future native quotient |

# 7. Candidate OACR independent theory object after this audit

No single component below is novel in isolation.

The object that still survives direct comparison is the conjunction:

\[
\boxed{
\text{native continuation contract}
+
\text{two-sided representation adequacy}
+
\text{non-anticipating constructor authority}
+
\text{bidirectional common-target repair}
+
\text{fixed native replay}
}
\]

In the one-delta DAG class, this object is constructive:

\[
D^+(A)
=
\bigcup_{f\in A}W_f
\]

determines:

- the exact operational quotient;
- the unique exact identity-gated representation;
- additive repair from the coarse endpoint;
- subtractive repair from the full endpoint;
- minimum record edits under contract change;
- path-independent incremental updates.

The multi-delta counterexample then proves that local activity is not universal and motivates the product-closure / contract-generator generalization.

# 8. T5 verdict

\[
\boxed{\text{WORKING PASS}}
\]

The independent object survives source-level nearest-neighbor comparison.

However manuscript promotion still requires:

1. direct citations and careful wording in Related Work;
2. no claim that bidirectionality alone is new;
3. no claim that minimal sufficient quotients alone are new;
4. no claim that outcome-guided refinement is methodologically invalid;
5. explicit acknowledgment that summary repair already weakens and strengthens summaries;
6. AIR to be treated as a primary theoretical neighbor, not a peripheral citation.

The target paper should say, in substance:

> OACR does not introduce the general ideas of semantic preservation, abstraction refinement, or bidirectional weakening/strengthening. It studies a different joint object: an implemented persistent representation judged against a prospectively declared native continuation contract, with both missing and unjustified distinctions treated as errors, and with confirmatory repair construction separated from the held-out native outcome quotient that later verifies exactness.
