# OACR G5 Bundle -> H2 Execution Bridge v1

**Date:** 2026-09-30  
**Status:** engineering execution bridge; no scientific rule change

## Purpose

The accepted G5 validation artifact freezes original Git commit identifiers. Some original commit objects are no longer reachable from live upstream refs. The executable-carrier recovery protocol reconstructs an execution-equivalent Git object graph and records an original-to-reconstructed commit map.

This bridge specifies how the existing prospective G5-H2 contract may execute on that frozen reconstructed carrier without changing its scientific identity.

## Frozen scientific identities

The following remain identified only by their **original** frozen SHAs:

- 46 H1-equivalent source pairs;
- 12 registered merge targets;
- 132 ordered target sequences per pair before H1 eligibility filtering.

All producer/verifier output continues to serialize original pair/target SHAs.

## Execution translation

Let

\[
m:c_{\rm original}\mapsto c_{\rm executable}
\]

be the carrier-recovery mapping.

Before a native Git operation, only the object identifier passed to Git is translated:

\[
c\mapsto m(c).
\]

The experimental record retains \(c\), not \(m(c)\), as the registered action/state identity.

The mapping may be used only if the executable carrier has first passed the full accepted G5 H1 replay gate:

\[
1152/1152\text{ cells reproduced},
\qquad
0\text{ signature mismatches}.
\]

## Unchanged H2 contract

The mapping does not alter:

- source pair membership;
- target membership;
- target ordering;
- H1 expected signatures;
- H1 continuation eligibility gate;
- deterministic persisted first-merge rule;
- H2 native outcome payload;
- divergence criterion;
- positive/negative interpretation.

A mapped carrier that changes any accepted H1 signature is rejected before H2 execution.

## Native first-step successor

When the first merge creates a new synthetic merge commit, its parents may be reconstructed commit objects rather than the unavailable original objects.

This is permitted because carrier acceptance already requires preservation of the exact registered H1 merge semantics, tree identity, ancestry relation, and merge-base structure on the frozen bank.

The generated successor commit is an execution state; its SHA is not a registered scientific outcome.

## Verification

Producer and independent verifier must receive:

1. the same accepted original G5 validation JSON;
2. the same frozen carrier bundle;
3. the same original-to-reconstructed mapping.

They independently translate original SHAs at execution time.

A verifier mismatch is a scientific/engineering audit event; it does not authorize changing the mapping, source pairs, target panel, or H2 rule after observing the result.

## Claim boundary

The bundle/mapping repair establishes reproducible executability of the original frozen contract. It does not add evidence for or against H2 divergence by itself.

Only a completed independent H2 replay on the accepted bundle can promote the existing producer zero to an independently verified natural Git H2 negative.
