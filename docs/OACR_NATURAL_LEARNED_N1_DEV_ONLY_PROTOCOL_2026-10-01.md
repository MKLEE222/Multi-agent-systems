# OACR Natural Learned N1 Dev-Only Protocol

Date: 2026-10-01

Status: FROZEN DEV-ONLY EXECUTION PLAN

## Scope

This phase may access only the frozen 128-unit development manifest produced by N0.

The 512-unit evaluation manifest remains sealed and must not be loaded by N1 jobs.

## Compared constructors

### B0 — Base GRACE

Original frozen GRACE adaptor after the registered edit.

### B1 — Contract-predictive repair

A representation repair constructor may use only:

- edit metadata;
- subject/relation information;
- frozen construction-visible condition-query structure;
- declared GRACE representation state.

It may not use held-out test prompts, answers, future success labels, or evaluation feedback.

### B2 — Matched sham

Same representation edit budget as B1, but auxiliary representation additions are generated from matched irrelevant condition structure without future-contract relevance.

### A0 — Oracle diagnostic

Development-only diagnostic. It may inspect dev future outcomes only to estimate the oracle ceiling. It is not confirmatory evidence.

## Dev gates

D1: representation change

The repair must produce a non-trivial representation delta.

D2: future-contract improvement

The repaired representation must improve the frozen development continuation contract relative to B0.

D3: sham separation

Improvement must exceed the matched sham improvement.

No evaluation unlock occurs unless:

repair > sham

and

future closure improves.

## Evaluation authority

Any constructor, hyperparameter, threshold, or intervention-cost change after inspecting dev outcomes requires a new dev round. The evaluation bank remains sealed until a frozen constructor is promoted.
