# OACR-COMPOSE-L Recovery Hysteresis Engineering Record

**Date:** 2026-09-30  
**Scientific protocol:** \`docs/OACR_COMPOSE_L_RECOVERY_HYSTERESIS_PROTOCOL_V1_2026-09-30.md\`  
**Protocol commit:** \`e1d00a7bb57d30ef2d49eb667dbcd6fd7f0d1e8f\`

## 1. Initial workflow run

Run:

- \`36657010957\`;
- trigger issue: #62.

The workflow restored the frozen carrier cache and installed the frozen runtime.

It failed in the pre-execution compile/asset gate before producer invocation.

Observed environment paths contained an unintended leading backslash, e.g.

\`\\/home/runner/.../assets/scotus-bert\`.

The first failing command was:

\`test -s "$R1_SCOTUS_MODEL_DIR/config.json"\`.

For completed folds, the subsequent producer, verifier, and artifact-upload steps were skipped.

Therefore:

- no recovery candidate write was executed;
- no forward edit was executed;
- no counter-edit was executed;
- no future-write outcome was executed;
- no scientific outcome was exposed.

## 2. Cause

When the workflow YAML was created through the orchestration layer, GitHub expressions were escaped with an unintended leading backslash before the expression marker.

GitHub expanded the expression but retained the backslash.

This is workflow-string plumbing only.

## 3. Pre-outcome repair

Workflow-only correction commit:

\`b7d546ad06e02ebe7d9d7c4cdd08888e5f91df0e\`.

Repair:

- remove the unintended backslash before every GitHub expression.

Unchanged:

- all scientific protocol rules;
- carrier and official GRACE commit;
- fold definitions;
- future-bank construction;
- anchor-bank construction;
- sentinel construction;
- counterfactual-label rule;
- edit -> counter-edit recovery gate;
- future-write panel;
- positive/negative definitions.

Because the failure occurred before any producer invocation, the corrected run remains fully prospective.
