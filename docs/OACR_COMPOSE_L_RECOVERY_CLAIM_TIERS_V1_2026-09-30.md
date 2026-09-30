# OACR-COMPOSE-L Recovery Claim Tiers v1

**Date:** 2026-09-30  
**Status:** frozen before the first corrected prospective fold outcomes are inspected  
**Source protocol:** \`OACR_COMPOSE_L_RECOVERY_HYSTERESIS_V1\`

## 1. Why tiers are required

A task-level recovery criterion is sufficient for the protocol's primary operational relation, but a future divergence after only coarse label recovery can be challenged as residual current-state visibility.

Therefore positive outcomes must be stratified by how strongly the present has been restored.

The protocol is not changed. This document only constrains later claim language.

## 2. Tier R0 — target recovery only

Requirements:

- anchor original target realized after counter-edit.

This is **not** sufficient for an OACR recovery claim.

## 3. Tier R1 — registered task recovery

Requirements:

- complete frozen primary task READ equals base exactly;
- repeated READ is stable;
- recovered parameter hash differs from base.

If a common future write later separates the states, this supports:

> task-level present recovery does not guarantee recovery of the registered future-write response.

This is a valid operational witness but not automatically a headline hysteresis result.

## 4. Tier R2 — task + diagnostic-logit recovery

Requirements:

- all R1 conditions;
- complete frozen diagnostic logit READ matches base within the preregistered tolerance:
  - atol \(10^{-6}\);
  - rtol \(10^{-5}\).

If a common future write then produces a **primary task-level** divergence, classify as a **strong recovery-hysteresis witness**.

Preferred interpretation:

> Two learned states that are indistinguishable under the frozen current behavioral panel down to registered logit tolerance can respond differently to the same later native update.

This is the minimum tier recommended for a headline learned result.

## 5. Tier R3 — strengthened fresh-replay recovery

A later targeted replay may strengthen the current contract before claim promotion, but only prospectively.

Possible additions include:

- paraphrase-equivalent current queries;
- locality/neighborhood probes;
- a larger frozen sentinel bank;
- alternative non-mutating behavioral summaries.

These additions cannot retroactively upgrade the discovery artifact.

If used, they must be frozen before the fresh targeted replay.

## 6. Future divergence tiers

Separately classify the future response:

### F1
native status / target-realization difference only.

### F2
at least one exact primary task READ entry differs.

### F3
future task divergence is selective across the frozen future panel.

For a headline recovery-hysteresis result, prefer at least:

\[
R2 + F2.
\]

## 7. Governance

Do not:

- call an R1-only discovery "full behavioral restoration";
- infer parameter restoration;
- use current logit mismatch as evidence for future hysteresis;
- promote diagnostic-logit-only future differences as primary positives;
- choose the claim tier after inspecting which wording sounds strongest.

The tier is determined mechanically from stored artifact fields.
