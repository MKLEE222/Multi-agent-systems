# OACR COMPOSE — SQEC Bridge Acceptance

**Date:** 2026-09-29  
**Status:** ACCEPTED as a retrospective controlled COMPOSE seed; not prospective discovery  
**Source semantics:** pre-existing SQEC multistep observation-legality model  
**Independent OACR checker commit:** \`59d2019cf27d9c6bfe98dd476e215c3f9c475ecb\`  
**CI workflow commit:** \`47dc9345f41e5288b005c2f6c151e5d25c9d78dd\`  
**Run:** \`36569169409\`  
**Artifact:** \`oacr-compose-sqec-bridge-v1\`, ID \`11033610627\`  
**Artifact digest:** \`sha256:6171f28737434adc78abc8439aa36c9b38a9fc7562475c73c7e49b9ed74c577d\`

## 1. State pair

The pre-existing SQEC controlled model contains the state

\[
X=(\text{task-done=ACTION\_OPEN},
\text{latent-semantics=UNKNOWN},
\text{observation-route=ACTION\_OPEN})
\]

and the reachable state

\[
Y=T_{\text{retain-observation-route}}(X)
\]

whose only relevant hidden difference is

\[
\text{observation-route}(Y)=SATISFIED.
\]

The registered READ is the joint claim-qualification state, whose route depends on task-done and latent-semantics. The observation-route coordinate controls legality of a later observation but is not itself a direct claim-state coordinate.

## 2. Frozen depth definition used by the checker

For this bridge audit, the one-step signature is

\[
\Sigma_1(S)
=
\left(
O(S),
A(S),
\{a\mapsto O(T_aS):a\in A(S)\}
\right),
\]

where:

- \(O(S)\) is the registered joint qualification READ;
- \(A(S)\) is the current legal primitive action set;
- only the READ after one primitive is included at depth 1;
- successor action availability belongs to depth 2.

This avoids counting a post-action inspection of the next action set as a one-step result.

## 3. Exact H1 equality

The independent checker reconstructs the SQEC transition semantics without importing SQEC producer helpers.

For both \(X\) and \(Y\):

Current READ:

\[
O(X)=O(Y)=\text{epistemically-open}.
\]

Current legal primitive set:

\[
A(X)=A(Y)=
\{\text{commit-task},
\text{observe-semantics},
\text{retain-observation-route}\}.
\]

One-step READs are identical for every primitive:

| primitive | READ from \(X\) | READ from \(Y\) |
|---|---|---|
| commit-task | epistemically-open | epistemically-open |
| observe-semantics | action-open | action-open |
| retain-observation-route | epistemically-open | epistemically-open |

Therefore:

\[
\boxed{\Sigma_1(X)=\Sigma_1(Y).}
\]

## 4. Exact H2 divergence

The checker exhaustively evaluates all

\[
3\times3=9
\]

ordered two-primitive sequences.

Exactly one sequence diverges:

\[
\boxed{
\text{commit-task}
\rightarrow
\text{observe-semantics}.
}
\]

From \(X\):

- commit-task closes observation-route;
- observe-semantics is then illegal;
- terminal registered READ remains epistemically-open.

From \(Y\):

- observation-route was already SATISFIED;
- commit-task preserves that satisfied coordinate;
- observe-semantics remains legal;
- the second step yields qualified.

Thus:

\[
\boxed{
\Sigma_1(X)=\Sigma_1(Y)
\quad\text{but}\quad
\Sigma_2(X)\neq\Sigma_2(Y).
}
\]

The hidden coordinate is operationally inert across the complete registered primitive boundary at depth 1, yet becomes necessary under composition.

## 5. Projection corollary

The pre-existing SQEC legality-projection result is consistent with the state-pair witness.

At the initial state, the observation precondition is satisfied, so deleting that precondition does not alter initial primitive availability. After commit-task, the full semantics makes observation illegal while the legality-blind projection still admits it.

This supplies a representation/interface corollary:

> a continuation-interface projection can be primitive-wise correct at the current state yet fail under composition because an earlier action changes the qualification of a later action.

The projection corollary is supporting evidence; the primary bridge witness is the same-semantics state pair above.

## 6. Scientific interpretation

Accepted:

> In the pre-existing controlled SQEC micro-world, two current states have the same registered READ, the same current legal primitives, and the same READ after every individual primitive, yet a shared two-step sequence separates them because the first action changes the legality of the second.

This is the first clean OACR bridge witness of delayed continuation divergence under the new depth definition.

## 7. Boundaries

Do not claim from this witness alone:

- natural prevalence;
- cross-substrate COMPOSE generality;
- novelty of transition composition, modal depth, or bisimulation theory;
- that qualification is the only source of COMPOSE;
- that every H1-equivalent pair eventually diverges;
- that the result is prospective.

The scientific value is mechanistic and architectural:

- it proves that the broader OACR object is nonempty;
- it separates the COMPOSE mechanism from the relational-deletion negative control;
- it supplies a concrete target for a prospective native-history replication.

## 8. Current cross-carrier contrast

Relational R3/R4:

\[
d_A(e)\in\{1,\infty\}
\]

under the frozen deletion universes: WRITE-active distinctions appear at H1; the rest remain inert under all registered deletion compositions.

SQEC controlled qualification:

\[
\Sigma_1(X)=\Sigma_1(Y),
\qquad
\Sigma_2(X)\neq\Sigma_2(Y).
\]

This supports the working hypothesis that delayed COMPOSE activation requires a carrier in which an earlier transformation can change the semantic/qualification interface of later transformations, rather than composition length alone.

## 9. Next gate

The next required result is prospective replication in a native persistent-history carrier, with Git as the first target.

The Git experiment must be frozen before any H2 native outcome and should begin from already accepted G5 D1-equivalent pairs rather than constructing a post-hoc H2-positive pair.
