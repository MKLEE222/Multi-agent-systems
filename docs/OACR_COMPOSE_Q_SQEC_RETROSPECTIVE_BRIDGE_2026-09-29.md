# OACR-COMPOSE-Q — SQEC Retrospective Bridge Result

**Date:** 2026-09-29  
**Status:** retrospective reinterpretation of an already executed SQEC controlled result; not prospective OACR discovery evidence  
**Source project:** \`MKLEE222/qualification_opportunity_compiler\`  
**Source result:** \`STOCHASTIC_MULTISTEP_LEGALITY_AND_POLICY_TREE_AUDIT_20260829.md\`

## 1. Question

Does the existing SQEC stochastic multistep legality example instantiate the minimal OACR COMPOSE condition

\[
\Gamma_1^{A}(X_0)=\Gamma_1^{B}(X_0)
\quad\text{but}\quad
\Gamma_2^{A}(X_0)\ne\Gamma_2^{B}(X_0)?
\]

The comparison is between:

- **FULL:** the native typed dynamic model with observation legality preconditions;
- **PROJECTED:** the exact projection used in the accepted SQEC audit, obtained only by deleting event legality preconditions while preserving the action/observation transitions, costs, stochastic outcomes, horizon, and initial state.

This is a representation/projection comparison, not a claim that the two systems have identical full internal descriptions.

## 2. Initial state

Both FULL and PROJECTED start from the same dynamic qualification snapshot.

The registered first-step choices are:

- \`commit-task\`;
- \`universal-remediation\`;
- \`observe-semantics\`;
- stop.

At the initial snapshot, the observation-route atom is \`ACTION_OPEN\`.

Therefore the observation precondition in FULL is satisfied at the initial state.

Hence FULL and PROJECTED have the same currently enabled first-step action/observation set.

## 3. One-step transition equality

The projection function \`project_stochastic_legality\` removes only \`preconditions\`.

It does **not** change:

- the transition relation of \`commit-task\`;
- the transition relation of \`universal-remediation\`;
- either stochastic observation-outcome transition;
- observation probabilities;
- costs;
- the initial qualification snapshot.

Therefore, for every first-step event that is enabled at the initial state, FULL and PROJECTED produce the same immediate post-event atom-status transition and the same immediate registered outcome distribution.

In particular, executing \`commit-task\` in either model:

- satisfies \`s::task-done\`;
- closes \`s::observation-route\`.

Thus the two representations are indistinguishable under the declared immediate interface.

This supports the retrospective depth-1 equality:

\[
\Gamma_1^{\rm FULL}(X_0)
=
\Gamma_1^{\rm PROJECTED}(X_0)
\]

when \(\Gamma_1\) records current enabledness and immediate transition/outcome semantics rather than dormant rule text.

## 4. Depth-2 divergence

After the common first transformation \`commit-task\`, the state coordinate

\[
s::observation-route
\]

is CLOSED in both models.

The later observation differs only because FULL retained its precondition and PROJECTED did not.

Therefore:

### FULL

\`observe-semantics\` is illegal after \`commit-task\`.

### PROJECTED

\`observe-semantics\` remains executable after \`commit-task\`.

Hence the common first transformation changes the future relevance of the omitted legality coordinate.

Formally:

\[
\Gamma_2^{\rm FULL}(X_0)
\ne
\Gamma_2^{\rm PROJECTED}(X_0).
\]

This is exactly the minimum compositional failure mode:

> a coordinate that is unnecessary to reproduce the present and all registered one-step transitions becomes necessary to reproduce which second-step continuations remain valid.

## 5. Consequential replay

The already accepted SQEC result supplies a consequential replay:

- FULL optimal policy observes first;
- projected policy moves commitment before observation;
- projected value remains unchanged inside the projection;
- replay in FULL encounters an illegal observation;
- replay objective becomes 10;
- replay regret is \(46/5\).

An independent enumerator checks all 34 finite contingent policy trees and matches the typed dynamic policy.

Thus the omitted coordinate is not only semantically different at depth 2; it changes a registered decision consequence under native replay.

## 6. Why this is stronger than current-permission mismatch

At the initial state:

- the observation is legal in both models;
- the first-step catalogue is the same;
- immediate event transitions are the same.

The failure appears only after a shared transformation changes the observation-route state.

Therefore the example is not reducible to:

> the representation forgot that an action is currently illegal.

Instead:

> the representation forgot a rule needed to update future action qualification after state change.

That is a genuine composition/closure failure.

## 7. OACR interpretation

Let \(R_{\rm proj}\) be the projection that omits legality preconditions.

Then:

\[
U_1(R_{\rm proj})=0
\]

under the immediate continuation contract, but:

\[
U_2(R_{\rm proj})>0
\]

under the two-step qualified-continuation contract.

Restoring the legality coordinate repairs the closure failure.

This gives a retrospective constructive bridge:

\[
\text{dynamic qualification}
\rightarrow
\text{delayed continuation divergence}
\rightarrow
\text{representation necessity}.
\]

## 8. Epistemic boundary

Accepted as retrospective mechanism evidence:

> The already executed SQEC controlled legality example is an exact instance in which omitting a legality coordinate preserves the initial enabled action set and all immediate transition semantics, yet fails after a shared first action because that action changes which second-step observation remains legal.

Not accepted from this reinterpretation alone:

- a prospective OACR COMPOSE discovery claim;
- cross-carrier prevalence;
- learned-system compositional activation;
- natural-system generality;
- universal minimality of the legality coordinate.

A fresh prospectively frozen replication is required before COMPOSE is promoted to the main OACR empirical claim.
