# OACR Naming Charter

**Canonical title:** **Operational Adequacy of Computational Representations**

**Acronym:** **OACR**

**Status:** frozen as the mother-project name on 2026-09-28.

## Mother question

What makes a computational representation adequate for the observations and operations required by inquiry?

OACR treats adequacy as relative to a declared observation/operation contract rather than as static information preservation alone.

## Working decomposition

\[
\mathrm{OACR}
=
\{\mathrm{READ},\mathrm{PROBE},\mathrm{WRITE},\mathrm{COMPOSE},\mathrm{COMPUTE}\}.
\]

- **READ:** which distinctions must be preserved for currently relevant consequences.
- **PROBE:** which distinctions must be preserved for admissible identification/intervention.
- **WRITE:** which distinctions must be preserved for admissible future transformations.
- **COMPOSE:** which distinctions and operation laws must survive translation, merge, fork, rollback, and related composition.
- **COMPUTE:** which distinctions and operations remain available under resource constraints.

## Naming rule

The former working title **Computational Adequacy of Writable Representations** is retired for the mother project.

“Writable representations” remains valid as a description of the WRITE subproblem and of particular carriers. Historical experiment IDs, protocol strings, artifact hashes, and filenames are not renamed when doing so would break reproducibility or audit trails.
