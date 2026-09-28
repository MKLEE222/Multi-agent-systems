# OACR-R4 Protocol Amendment v1 — Non-Authoritative Duplicate Record

**Date:** 2026-09-28  
**Current status:** **SUPERSEDED / NON-AUTHORITATIVE**  
**Historical commit:** 007ffb1773a26da2dce85f92f8f6ee92acca019b

This file was created after the authoritative R4-v2 paginated protocol had already been frozen at commit:

6795a534415e4f7270f2b25aca3522b653e413d3

and after the first R4-v2 workflow trigger had begun.

It proposed an alternative retrieval amendment using a different pagination schedule. That duplicate proposal must not govern any scientific execution.

## Authoritative R4-v2 protocol

The sole authority for R4-v2 fresh-carrier execution is:

docs/OACR_R4_V2_PAGINATED_REDESIGN_PROTOCOL.md

at commit:

6795a534415e4f7270f2b25aca3522b653e413d3

It freezes:

- the same five roots from R4-v1;
- 2,000-row pages;
- at most 20 pages;
- 40,000-row truncation gate;
- the original structural inclusion gates;
- the original state-bank rule;
- the R3 action-panel rule;
- the contract-gated representation;
- exact native replay;
- frozen secondary singleton/pair/leave-one-out analyses.

## Why this file is retained

The repository keeps this file, rather than deleting it, to make the duplicate-protocol mistake auditable.

No result may cite this file as an operative preregistration or protocol amendment.

The engineering correction after the first R4-v2 failure is separately recorded in:

docs/OACR_R4_V2_ENGINEERING_FAILURE_RECORD_2026-09-28.md

That correction changes only the explicit query ordering required to make pagination order machine-checkable. It does not change the scientific protocol.
