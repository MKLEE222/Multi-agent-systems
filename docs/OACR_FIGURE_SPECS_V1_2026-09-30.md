# OACR Figure Specifications v1

**Date:** 2026-09-30  
**Status:** manuscript figure authority before final rendering

## Figure 1 — From static fidelity to continuation closure

### Purpose

Make the mother problem legible in under 20 seconds without requiring any carrier-specific knowledge.

### Layout

Horizontal three-stage structure:

\[
\text{implemented representation}
\rightarrow
\text{registered native continuation}
\rightarrow
\text{operational quotient}
\]

Below it, show three vertical representation columns:

1. **Current representation**
   - few blocks;
   - merges states that later operations distinguish;
   - label: **under-refines**.

2. **Operational quotient**
   - intermediate blocks;
   - exactly the distinctions required by the registered contract;
   - label: **continuation-adequate**.

3. **Full internal identity**
   - many blocks;
   - preserves distinctions that never affect the contract;
   - label: **over-refines**.

Central relation:

\[
R_{\rm current}
\prec
O_{\mathcal C}
\prec
R_{\rm full}.
\]

Under the operational quotient, add the constructive arrow:

\[
\mathcal C
\rightarrow
\text{certificate}
\rightarrow
R_{\rm gate}.
\]

### Required annotation

Small footer:

> Behavioral quotient theory is inherited; OACR audits implemented representations against prospectively registered native contracts and tests representation repair by native replay.

### Avoid

- no Wikidata/Git/model-editing icons in Figure 1;
- no paper-specific numeric results;
- no COMPOSE tree;
- no claim of universal minimality.

---

## Figure 2 — Fresh R4-building directional mismatch and repair

### Purpose

Carry the strongest stable empirical result on one page.

### Three-column block diagram

#### Left — Current closure

Large single block containing all 272 states.

Label:

\[
|R_{\rm current}|=1
\]

\[
U_\mu=0.76597,\qquad E_\mu=0.
\]

Secondary label:

- 5,731 under-refinement pairs.

#### Center — Contract-gated / operational quotient

23 blocks.

Visually distinguish:

- 1 large inactive class containing base + 249 inactive augmented states;
- 22 active singleton or contract-distinct blocks as dictated by accepted partition.

Primary labels:

\[
|O_{\mathcal C}|=|R_{\rm gate}|=23
\]

\[
U_\mu=E_\mu=0.
\]

Below:

- 22 active deltas;
- 249 inactive deltas;
- 17,408 / 17,408 native replay cells exact.

#### Right — Full asserted identity

272 small blocks.

Label:

\[
|R_{\rm full}|=272
\]

\[
U_\mu=0,\qquad E_\mu=7.32149.
\]

Secondary label:

- 31,125 over-refinement pairs.

### Bottom repair strip

Show:

\[
271\text{ declared deltas}
\rightarrow
22\text{ retained deltas}
\]

with:

\[
91.88\%\text{ record reduction}
\]

and the qualification:

> under the declared shared-base + per-state-delta encoding.

### Main caption claim

> On the prospectively frozen R4-building carrier, current closure is too coarse and full asserted identity is too fine. A contract-derived gate retains only deltas whose current redundancy can be broken by a registered deletion, exactly matching the 23-class operational quotient and reproducing every native state-action outcome.

---

## Figure 3 — First-order activation across carriers

### Purpose

Show that hidden difference alone is neither necessary nor sufficient.

### Panel A — relational

Same current closure, latent redundant edge.

Three future writes:

- inert;
- inert;
- active.

Label:

\[
M(d,a)\in\{0,1\}.
\]

### Panel B — natural Git

Same current tree, different history.

Frozen merge targets:

- most held-out pairs remain equivalent;
- 2/48 require separation.

Label:

> history relevance is contract-relative.

### Panel C — learned

Same registered current task relation.

Future native edits 51 / 29 / 73 separate the accepted fold-0 pair.

Label:

> learned parameter difference becomes operational under registered update.

### Caption discipline

Do not imply prevalence or universal transfer.

---

## Figure 4 — When composition creates new demand

### Purpose

Distinguish sequence length from state-dependent continuation semantics.

### Panel A — fixed-domain deletion control

\[
d_A(e)=1
\quad\text{or}\quad
d_A(e)=\infty.
\]

R4-building:

- 22 depth-1 active;
- 249 inert under entire frozen action universe;
- 0 depth-2 activation.

### Panel B — learned negative control

GRACE L1b:

\[
224\text{ H0 collisions}
\]

\[
H0\to H1=0,\qquad H1\to H2=0.
\]

### Panel C — dynamic qualification

Root:

\[
\Gamma_1^{FULL}
=
\Gamma_1^{PROJECTED}.
\]

After common first action:

\[
\Gamma_2^{FULL}
\neq
\Gamma_2^{PROJECTED}.
\]

Visualize:

\[
\text{commit}
\rightarrow
\text{route CLOSED}
\rightarrow
\begin{cases}
FULL:\ observation\ illegal\\
PROJECTED:\ observation\ legal
\end{cases}
\]

### Panel D — pending learned recovery disposition

Reserve only after the prospective recovery run resolves.

If positive:

\[
\text{edit}
\rightarrow
\text{counter-edit}
\rightarrow
\text{present restored}
\rightarrow
\text{same future write diverges}.
\]

If strong negative:

show recovered parameter states with identical future response and label as boundary.

Do not force a positive layout.

---

## Rendering requirements

- Figure 1 and Figure 2 must work in grayscale.
- Partition blocks should be distinguishable by geometry/spacing, not color alone.
- Use one mathematical notation system throughout:
  - \(R_{\rm current}\)
  - \(O_{\mathcal C}\)
  - \(R_{\rm full}\)
  - \(R_{\rm gate}\)
  - \(U_\mu,E_\mu\).
- Avoid carrier screenshots.
- Captions must state finite-contract scope.
