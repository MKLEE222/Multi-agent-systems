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

Under the operational quotient, add the constructive pipeline:

\[
(R,\mathcal C)
\xrightarrow{\rm audit}
D
\xrightarrow{\rm certificate}
\kappa
\xrightarrow{\Phi}
R'
\xrightarrow{\rm native\ replay}
\text{closure}.
\]

Show two arrows into the repaired target:

\[
R_{\rm current}
\xrightarrow{\Phi^+}
R'
\xleftarrow{\Phi^-}
R_{\rm full}.
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

Show both correction directions:

\[
R_{\rm current}:
0\rightarrow22
\text{ per-state deltas}
\]

and:

\[
R_{\rm full}:
271\rightarrow22
\text{ per-state deltas}
\]

with:

- additive edits: 22;
- subtractive edits: 249;
- common target: 23 blocks;
- \(U_\mu=E_\mu=0\);
- 17,408/17,408 native replay cells exact.

Keep the 91.88% full-to-gated record reduction as secondary accounting, qualified as carrier-specific.

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

### Panel C — fixed-interpreter matched repair

Visualize one fixed skeleton/compiler/executor feeding five representation objects.

Reference FULL:

\[
cost=2,\qquad H1=0,\ H2=0.
\]

B0 — no guard:

\[
cost=0,\qquad H1=0,\ H2=12.
\]

B1 — full restore:

\[
cost=2,\qquad H1=0,\ H2=0.
\]

B2 — shared contract-relevant rule:

\[
cost=1,\qquad H1=0,\ H2=0.
\]

B3 — same-size sham rule:

\[
cost=1,\qquad H1=0,\ H2=12.
\]

Central visual claim:

\[
cost(B2)=cost(B3)
\]

but:

\[
closure(B2)\neq closure(B3).
\]

Caption:

> Under a fixed transition skeleton, compiler, and native executor, only the contract-relevant representation rule closes the delayed continuation deficit; equal-size sham precision does not.


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
