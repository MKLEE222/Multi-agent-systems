# OACR G5 Carrier Recovery Protocol v1

**Date:** 2026-09-30  
**Status:** engineering/reproducibility protocol; scientific G5/H2 rules unchanged  
**Source artifact:** accepted G5 validation artifact ID 10954788549  
**Purpose:** convert frozen Git commit identifiers into a self-contained executable carrier

## 1. Problem

The accepted G5 artifact freezes:

- source head;
- 48 validation same-tree pairs;
- 12 merge targets;
- complete H1 native outcome signatures.

It did not freeze the Git object closure that made all referenced commits executable.

Some frozen commits were reachable from transient upstream refs at the original run but are no longer reachable from current \`git/git\` refs. Therefore:

\[
\text{frozen SHA identifiers}
\not\Rightarrow
\text{frozen executable carrier}.
\]

This is a reproducibility/archival defect, not a scientific result.

## 2. Recovery inputs

Use only:

1. accepted G5 validation JSON;
2. public GitHub low-level Git database API for \`git/git\`;
3. a current full clone as an object cache;
4. deterministic reconstruction code committed before validation.

No H2 outcome participates in carrier recovery.

## 3. Required original commit set

The required bank is the union of:

- G5 source head;
- all validation A commits;
- all validation B commits;
- all 12 frozen targets.

The current accepted artifact yields 104 unique required original commit SHAs.

## 4. Exact object recovery

For each required original commit \(c\):

### If the commit object already exists locally

Use identity mapping:

\[
m(c)=c.
\]

### If the commit object is unavailable

Query the low-level Git commit endpoint for:

- exact root tree SHA;
- ordered parent SHAs.

Recursively recover each unavailable parent until an existing local commit or already reconstructed commit is reached.

For every unavailable tree/blob object:

- fetch the exact Git tree/blob object through the low-level Git API;
- write it into the local object database;
- require the locally computed SHA to equal the upstream object SHA.

Thus file content and tree identity remain exact.

## 5. Synthetic commit rule

Unavailable commit objects need not preserve their original commit-object SHA.

Create a deterministic synthetic commit with:

- the **exact original tree SHA**;
- ordered parent list after original-to-reconstructed mapping;
- fixed reconstruction author/committer metadata;
- a fixed message containing the original SHA.

Record:

\[
m(c)=c_{\rm synthetic}.
\]

The recovery claim is not commit-object identity. It is preservation of:

- exact trees;
- exact parent topology up to graph isomorphism;
- ancestry relations;
- merge-base structure;
- native merge semantics.

## 6. Graph recovery boundary

Parent recursion is permitted only to restore the original ancestry topology needed by the frozen bank.

No parent edge may be added, removed, or reordered.

If the recursive unavailable-commit closure exceeds 5000 commits, abort with:

\`CARRIER_RECOVERY_TOO_LARGE\`

and redesign archival strategy before any H2 acceptance.

## 7. Mandatory H1 equivalence validation

Before the reconstructed carrier is accepted, replay the complete accepted G5 H1 validation matrix using mapped commits:

- all 48 validation pairs;
- all 12 frozen targets.

For every A/B-target cell, recompute the exact original G5 payload/signature.

Acceptance requires:

\[
\boxed{\text{H1 signature mismatches}=0}
\]

against the accepted artifact.

This validation tests that reconstruction preserves the native semantics already observed prospectively.

Any mismatch blocks carrier promotion.

## 8. Frozen bundle

Only after H1 exact validation passes:

1. create dedicated refs for all mapped required commits;
2. create a Git bundle containing those refs and their reachable object closure;
3. persist:
   - bundle;
   - original-to-reconstructed SHA map;
   - reconstruction manifest;
   - H1 replay validation report;
   - SHA-256 digests.

The bundle becomes the executable G5 carrier for future H2 verification.

## 9. H2 governance

Carrier reconstruction must not alter:

- the 46 H1-equivalent source pairs used by COMPOSE-G;
- the 12 target IDs;
- ordered H2 sequence set;
- H1 continuation gate;
- deterministic persisted first merge;
- H2 native outcome signature;
- divergence criterion.

H2 producer/verifier may translate frozen original SHAs through the accepted mapping before native execution.

## 10. Interpretation

If H1 exact validation passes, the reconstructed bundle is accepted as an execution-equivalent archival representation of the original G5 carrier under the registered merge contract.

Do not claim:

- byte-identical original commit objects for unavailable commits;
- preservation of commit metadata irrelevant to the registered merge semantics;
- universal equivalence outside the frozen G5 contract.

The purpose is reproducible native continuation semantics, not historical-metadata preservation.
