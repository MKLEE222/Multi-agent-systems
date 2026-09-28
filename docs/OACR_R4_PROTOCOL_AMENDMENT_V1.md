# OACR-R4 Protocol Amendment v1 — Retrieval Completeness and Compute Feasibility

**Date:** 2026-09-28  
**Status:** frozen before any R4 carrier outcome is inspected  
**Amends:** OACR_R4_FRESH_RELATIONAL_REDESIGN_PROTOCOL_V1.md  
**Root list unchanged. Scientific state/action/redesign rules unchanged.**

## 1. Reason

The original R4 protocol used one ORDER BY query with LIMIT 2500 and treated a full page as TRUNCATED.

Before any R4 carrier result was inspected, this was identified as an avoidable infrastructure bottleneck for broad frozen roots. A carrier should not be excluded merely because its deterministic query needs more than one result page.

The amendment changes retrieval completeness and adds outcome-blind computational feasibility gates only.

## 2. Deterministic pagination

For each frozen root, use the same three-level P279 UNION query and the same:

ORDER BY ?child ?parent

Fetch pages with:

- page size 2500;
- OFFSET values 0, 2500, 5000, 7500;
- at most four pages.

Stop when a page contains fewer than 2500 bindings.

Freeze every raw JSON page byte-for-byte and record its SHA256.

The carrier is classified as RETRIEVAL_COMPLETE when a page with fewer than 2500 bindings is observed.

The carrier is classified as TRUNCATED_10000 only when all four pages contain exactly 2500 bindings.

A truncated carrier is retained in the audit record but excluded from primary R4 analysis without replacement.

## 3. Duplicate handling across pages

After all retrieved pages are frozen:

- concatenate bindings in page order;
- parse child-parent edges;
- remove duplicate asserted edges and self-loops exactly as in R1;
- continue with the original graph-hygiene protocol.

Pagination does not alter the root, depth, relation, or semantic selection rule.

## 4. Outcome-blind computational feasibility gates

Before any augmented-state native deletion outcome is executed, additionally require:

- prepared nodes <= 4000;
- prepared asserted edges <= 6000;
- complete base transitive-closure size <= 2,000,000.

These are compute-feasibility gates, not scientific success criteria.

A carrier exceeding a maximum gate is classified as COMPUTE_EXCLUDED and is not replaced.

The original minimum structural gates remain unchanged:

- prepared nodes >= 100;
- prepared asserted edges >= 128;
- redundant entailed-but-unasserted candidates >= 64;
- at least 64 asserted edges for the shared action panel.

## 5. Inclusion categories

Every frozen root receives exactly one top-level status:

- INCLUDED;
- TRUNCATED_10000;
- STRUCTURE_EXCLUDED;
- COMPUTE_EXCLUDED;
- RETRIEVAL_FAILED;
- IMPLEMENTATION_INVALID.

No status may trigger root replacement within R4 v1.

## 6. Confirmatory requirement

The primary R4 replication block still requires at least two INCLUDED roots.

If fewer than two are INCLUDED, R4 v1 is reported as underpowered rather than modified after outcome inspection.
