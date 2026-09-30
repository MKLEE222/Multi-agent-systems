# OACR-COMPOSE-L — Nearest-Neighbor Claim Boundary

**Date:** 2026-09-30  
**Status:** related-work boundary frozen before the first corrected recovery-hysteresis outcomes are inspected  
**Purpose:** prevent a learned positive from being overstated as a generic discovery of edit irreversibility or sequential interference

## 1. Reversibility is already a direct research object

Recent parametric knowledge-editing work explicitly studies edit -> revert behavior.

A particularly close 2026 study, *On Reversibility as Language Model Behavioral Property in Parametric Knowledge Editing*, defines behavioral reversibility without requiring exact parameter restoration. It applies an inverse edit and evaluates recovery of:

- the main edited fact;
- paraphrastic variants;
- neighborhood/locality behavior;
- broader stability.

It reports strong recovery on the edited fact while locality may recover only partially.

Therefore OACR-COMPOSE-L must **not** claim novelty for:

- using a counter-edit;
- behavioral recovery after an inverse edit;
- parameter inequality after behavioral recovery;
- residual locality disturbance after revert.

## 2. Sequential-edit interference is mature enough to be a neighbor

Existing sequential model-editing literature already reports that later edits can damage or attenuate previous edits.

Examples include:

- Li & Chu, *Can We Continually Edit Language Models? On the Knowledge Attenuation in Sequential Model Editing*, Findings ACL 2024;
- Lyu et al., *EvoEdit: Evolving Null-space Alignment for Robust and Efficient Knowledge Editing*, Findings ACL 2026;
- *Spectral Characterization and Mitigation of Sequential Knowledge Editing Collapse*, ACL 2026.

Therefore a result of the form:

> edit sequence order matters / repeated edits interfere

is not an OACR headline.

## 3. Explicit rollback also exists

Editing frameworks such as EasyEdit expose rollback/reversal functionality for some editors, including GRACE-style editing.

Selective edit-reversal work in 2026 also studies removing chosen parameter-edit effects while preserving others.

Therefore:

> an edit can be undone or selectively reversed

is also not the OACR contribution.

## 4. OACR-specific unresolved conditional

The learned experiment asks a more specific representation/continuation question.

Condition on a recovered state satisfying a frozen present-equivalence contract:

\[
R_{\rm now}(X_{\rm base})
=
R_{\rm now}(X_{\rm recovered}).
\]

Then apply the **same frozen future native write** \(w\) to both.

The OACR target is:

\[
R_{\rm now}(W_w(X_{\rm base}))
\ne
R_{\rm now}(W_w(X_{\rm recovered})).
\]

The scientific object is therefore not reversibility itself but **closure of a present-recovery representation under future update**.

Preferred wording if supported:

> A representation can certify recovery of the registered present while remaining insufficient to predict the response to a later common update.

## 5. Strong-result threshold

A headline learned result should preferably satisfy the preregistered R2+F2 tier:

- exact frozen task READ recovery;
- current diagnostic logits match within frozen tolerance;
- parameter state remains different;
- a common frozen future native write creates a primary task-level divergence;
- fresh targeted replay reproduces the result.

An R1-only positive remains useful but should be framed as a coarser operational witness.

## 6. What the cross-carrier paper can own

If the learned result is supported, the broader OACR contribution can be framed around the contrast:

- fixed-domain relational composition creates no new representational demand beyond H1;
- dynamic qualification in SQEC yields exact latent guard activation at H2;
- learned edit-recovery may preserve the registered present while failing to preserve future update response.

The recurring object is:

\[
\text{representation closure under state-dependent continuation}.
\]

That is broader than model editing and narrower than a claim that path dependence itself is new.
