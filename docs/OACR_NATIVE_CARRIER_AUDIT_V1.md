# OACR Native-Carrier Audit v1

**Date:** 2026-09-28  
**Purpose:** choose the next carrier from an unresolved OACR adequacy question, not from a pre-existing semantic taxonomy.

## 1. Unresolved question after N1

The first cross-carrier audit separates two facts:

- an internal distinction can exist without being required by the frozen operation contract (OACR-W1);
- a current-read collision can require separation under a registered future operation (OACR-R1).

The next question is therefore:

> Can a **native, non-neural computational system** exhibit an operationally necessary distinction that is neither injected as a relational support edge nor defined by a neighboring theory?

The desired carrier should expose the distinction through its own documented operation semantics.

## 2. Candidate systems inspected from native documentation

### Git

Native persistent state includes content trees and commit ancestry. `git merge-base` computes best common ancestors from the parent relation; `git merge` incorporates changes since histories diverged and uses a 3-way merge for true merges. If all named commits are already ancestors of HEAD, merge exits as already up to date.

This creates a direct native possibility:

- two HEAD commits can point to exactly the same complete tree;
- their ancestry relative to the same target commit can differ;
- the same native `git merge target` operation can therefore differ.

This tests whether a content snapshot alone is adequate for a history-sensitive native operation.

### Kubernetes

Native resource deletion consults `metadata.finalizers`; owner references and `blockOwnerDeletion` also alter garbage-collection behavior. Two objects that match on a restricted content/spec observation but differ in finalizer/ownership metadata can react differently to the same DELETE.

This is operationally clean, but a first experiment would depend strongly on what the observation interface excludes. Because finalizers are directly readable object metadata, it is a less stringent next test than Git's content-tree versus ancestry distinction.

### PostgreSQL

Native foreign-key schema controls future DELETE/UPDATE semantics through actions such as RESTRICT, NO ACTION, CASCADE, SET NULL, and SET DEFAULT. Two databases with identical table tuples but different constraint schemas can react differently to the same data-changing command.

Again, the result depends on registering a content-only observation that excludes schema. It is a useful later carrier but does not currently improve on the Git history case.

## 3. Selection for the next exact native-system experiment

The next carrier is **Git**, for one narrow reason:

> Git exposes a first-class native operation whose semantics depend on history/ancestry even when the complete current content tree is identical.

This selection is not because OACR needs to fill a "temporal", "provenance", or "identity" category. The carrier is selected because its native semantics directly tests the unresolved N1 question.

## 4. Boundary

The Git experiment will establish only an L1 native-system fact:

- complete tracked tree equality is insufficient for a registered merge contract in specific exact constructions.

It does not establish:

- a universal theorem about all history-sensitive systems;
- a semantic theory of identity or continuity;
- an analogy to cultural lineage;
- prevalence in real software repositories.

Those require separate evidence.
