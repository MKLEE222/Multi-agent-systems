# Operational Adequacy of Computational Representations

**Canonical project name:** Operational Adequacy of Computational Representations (OACR)

This repository contains experiments and formal work for the **WRITE** component of OACR.

OACR asks what distinctions a computational representation must preserve in order to support the observations and operations required by inquiry. The working decomposition is:

- **READ** — preservation of currently relevant consequences;
- **PROBE** — preservation of distinctions recoverable by admissible interventions;
- **WRITE** — preservation of admissible future transformation behavior;
- **COMPOSE** — preservation of operation semantics across translation, merge, fork, rollback, and related representation changes;
- **COMPUTE** — preservation under resource-bounded access and execution.

The current R1 target is official GRACE + SCOTUS/BERT, testing read-matched future-write divergence under a prediction -> execution -> blind validation protocol.

The previous working title **Computational Adequacy of Writable Representations** is retired. Experimental protocol identifiers and historical file names are retained when changing them would damage auditability.


## Active OACR program

- `docs/OACR_NEAREST_NEIGHBOR_COVERAGE_V1.md` — theory-neighbor coverage audit.
- `docs/OACR_SYSTEM_RELATION_TAXONOMY_V1.md` — system / relation / representation taxonomy used to select carriers by semantic coverage.
- `docs/OACR_W1_OPERATIONAL_CONGRUENCE_PROTOCOL_V1.md` — learned routed-memory congruence audit.
- `docs/OACR_R1_RELATIONAL_RETRACTION_PROTOCOL_V1.md` — exact relational/retraction audit on a Wikidata-derived subclass graph.

Carrier selection rule: a new experiment must add a materially different operation or relation semantics, not merely another benchmark for the same mechanism.


### Current exactness / necessity track

- `docs/OACR_N1_OPERATIONAL_NECESSITY_V1.md` — distinguishes pairwise operational necessity from feature under/over-refinement.
- `docs/OACR_NATIVE_CARRIER_AUDIT_V1.md` — native-first carrier selection after N1.
- `docs/OACR_G1_GIT_HISTORY_PROTOCOL_V1.md` — exact Git tree/history congruence positive control.
- `docs/OACR_G2_NATURAL_GIT_HISTORY_PROTOCOL_V1.md` — natural public-history witness search in `git/git`.
- `docs/OACR_RELATION_SEMANTICS_DISCIPLINE_V1.md` — L0/L1/L2 semantics discipline; nearest theories provide tools, not carrier meaning.
