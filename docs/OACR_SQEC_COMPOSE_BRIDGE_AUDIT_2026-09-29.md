# OACR / SQEC COMPOSE Bridge Audit — Multistep Legality

**Date:** 2026-09-29  
**Status:** retrospective controlled-mechanism reclassification; not a new prospective OACR outcome  
**Source project:** \`MKLEE222/qualification_opportunity_compiler\`

## 1. Question

Does an already executed SQEC result instantiate the OACR minimum COMPOSE pattern

\[
X \equiv_1 Y
\quad\land\quad
X \not\equiv_2 Y
\]

when the compared objects are a legality-complete representation and its legality-projected representation?

## 2. Source mechanism

The executed SQEC stochastic multistep-legality problem contains:

- state atom \`s::observation-route\`;
- action \`commit-task\`;
- observation \`observe-semantics\`;
- observation legality precondition requiring \`s::observation-route\` to be \`ACTION_OPEN\` or \`SATISFIED\`.

The initial model sets:

\[
s::observation\text{-}route = ACTION\_OPEN.
\]

The action \`commit-task\` changes:

\[
s::task\text{-}done \to SATISFIED
\]

and

\[
s::observation\text{-}route \to CLOSED.
\]

The projection used in the accepted experiment removes legality preconditions from actions/observation outcomes but leaves their transition effects unchanged.

## 3. Depth-1 equivalence at the initial state

At the initial state, the full observation precondition is satisfied because the route is \`ACTION_OPEN\`.

Therefore deleting the precondition does not change the immediate semantics of \`observe-semantics\`.

The other primitive actions have no relevant legality precondition removed by the projection.

For every registered primitive first step from the initial state:

- legality agrees;
- transition effects agree;
- action/observation costs agree.

Thus the full and projected objects agree on the complete registered depth-1 interface from the initial state.

In OACR notation, for this controlled primitive alphabet:

\[
X_{\rm full}\equiv_1 X_{\rm proj}.
\]

This statement is a structural consequence of the already frozen SQEC construction, not a newly selected post-hoc state pair.

## 4. Depth-2 divergence

Execute the shared first action:

\[
a_1 = commit\text{-}task.
\]

Both objects apply the same state transition, including:

\[
s::observation\text{-}route \to CLOSED.
\]

Now consider the second primitive:

\[
a_2 = observe\text{-}semantics.
\]

In the full legality-bearing object, \(a_2\) is illegal because the route is no longer \`ACTION_OPEN\` or \`SATISFIED\`.

In the projected object, the precondition has been deleted, so \(a_2\) remains executable.

Therefore:

\[
T_{a_1}(X_{\rm full})
\not\equiv_1
T_{a_1}(X_{\rm proj}),
\]

and hence:

\[
\boxed{
X_{\rm full}\equiv_1 X_{\rm proj}
\quad\land\quad
X_{\rm full}\not\equiv_2 X_{\rm proj}.
}
\]

The divergence is specifically in the legality/qualification coordinate of the continuation interface.

## 5. Existing executed consequence

The accepted SQEC audit reports:

- the full policy observes first at cost \(1/5\);
- with probability \(4/5\), the semantic route qualifies;
- with probability \(1/5\), it closes and universal remediation is used;
- expected full objective: \(4/5\).

Deleting legality preconditions lets the projected planner move commitment before observation without changing its projected value.

Native/full replay then encounters an illegal observation:

- replay cost: \(10\);
- regret: \(46/5\).

An independent enumerator checks all 34 finite contingent policy trees and matches the typed dynamic policy.

Thus the omitted coordinate is not merely syntactic: the depth-2 continuation failure has a registered decision/replay consequence.

## 6. OACR interpretation

This source result supports the controlled mechanism:

> a representation can be complete for the current state and every registered one-step transition while still be inadequate for a two-step continuation because the first transformation changes the qualification of the second.

Equivalently:

\[
U_1(R_{\rm projected})=0
\]

under the initial primitive interface, while

\[
U_2(R_{\rm projected})>0
\]

once composition is admitted.

This is the first exact controlled mechanism in the current evidence map that satisfies the intended D1= -> D2+ structure.

## 7. Boundaries

This is **not** promoted as the paper's natural headline result because:

1. the mechanism is controlled and explicitly constructed;
2. the result was developed under SQEC's evidence/qualification semantics, not prospectively as OACR-COMPOSE;
3. generic finite-state MDP/Bellman machinery absorbs the optimization once the legality-bearing state is supplied;
4. the novelty, if any, must therefore concern representation/continuation semantics and cross-carrier recurrence, not the optimizer.

It is nevertheless a valid mechanism witness and a strong design prior for the prospective natural Git test.

## 8. Cross-carrier role

Current intended division:

- **Relational deletion:** exact negative/control — depth-1 closure is already compositionally closed under the frozen deletion universe.
- **SQEC multistep legality:** exact controlled positive — depth-1 representation adequacy fails at depth 2 because action 1 changes action-2 qualification.
- **Git COMPOSE-G:** prospective natural test — ask whether the same abstract phenomenon recurs in native history-dependent merge semantics.
- **Learned persistent state:** later transfer test — ask whether sequential writes can change later write relevance without explicit symbolic legality rules.

This separation avoids forcing every substrate to exhibit the same local semantics while preserving one common continuation question.
