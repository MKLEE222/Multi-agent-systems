# OACR M2 Second Audit — 2026-09-28

## Status

This audit is performed after the M2 protocol amendment and after the amended reruns began.

It separates:

1. **run validity** — whether the registered implementation and artifact chain are reproducible;
2. **scientific interpretation** — what the observed structure actually supports;
3. **paper strengthening** — which claims should be promoted, demoted, or redesigned.

No claim is promoted merely because a workflow reports success.

---

## 1. M2-R v2 validity audit

### Registered run

- workflow run: `36425222754`
- artifact: `oacr-m2-r-v2`
- artifact ID: `10970934464`

### Workflow gates

All registered gates completed successfully:

- frozen R1 artifact download;
- NetworkX `3.2.1` runtime assertion;
- producer compile;
- M2-R v2 producer;
- endpoint regression;
- independent artifact verifier;
- artifact upload.

Uploaded artifact ZIP SHA256 from Actions:

`0d2c4b0d160490168b0738bab4f998693f98ce692ae78dbc75dcdbe734f4436a`

Result JSON SHA256:

`5e5347958cab054e9905672411e55a76e96024f691daeaac97f9a0b5bcdf1ea0`

### Embedded manifest hashes

- state manifest:
  `40b698473f0e6617b0b12245eacbd556e51ab9e67d5477b8ba48698f7fc0aea7`
- action manifest:
  `3d97a09531352ebfdb305e34e35f22d7958d32fc696483cea8cd1ca9048c30ad`
- fixed representation signatures:
  `6af3d24034cab3a083e70b20d1195987e0797dd56658fbe4389166235c588db4`
- state-action outcome matrix:
  `a9b91b716628d4cde238612321b8ecd1c6c75f15d77a6aa014e30c7cfa95c44a`
- weights:
  `24e3a8ce0981336561c2f463cf86ccc3eb39aaffb242710493df092c50502d5b`

### Repository-independent verifier

The registered verifier reconstructed all **3,978** analyzed contracts from the embedded artifact and returned `PASS`.

A separate audit outside the repository verifier independently reconstructed all 3,978 registered contracts from the downloaded JSON and found:

- block-count mismatches: **0**;
- directional-gap mismatches: **0**.

### Native carrier cross-check

The frozen R1 Wikidata artifact was downloaded independently.

Raw carrier SHA256:

`3d3852ff72382c171e3a5496336767809b9455541fa2604f7b6857a8e69457df`

Independent reconstruction produced:

- 1,027 prepared nodes;
- 1,063 asserted edges;
- 1,334 transitive-closure edges.

All 272 registered states were reconstructed independently:

- current complete closure matched the frozen R0 signature for every state;
- full asserted-edge signature matched the frozen Rfull signature for every state.

Three representative actions were then re-executed natively from the frozen raw carrier across **all 272 states**:

1. dominant action `del:Q12040649>Q9190427`;
2. secondary action `del:Q1425572>Q590324`;
3. zero-effect action `del:Q1046055>Q188638`.

Stored versus independently recomputed post-deletion closure outcome mismatch count:

- dominant action: **0/272**;
- secondary action: **0/272**;
- zero-effect action: **0/272**.

The independently recomputed dominant singleton still yields 85 operational classes.
The independently recomputed dominant+secondary pair yields 88 operational classes.

### M2-R validity judgment

**ACCEPTED as a reproducible developmental carrier result.**

This does not make M2-R confirmatory for a general cross-system law, because R3 endpoint structure was known before M2 was conceived.

---

## 2. M2-R scientific audit

### Full endpoint

The full 64-action contract reproduces R3 exactly:

- 272 states;
- 101 operational classes;
- R0: `U = 3.391442481659308, E = 0`;
- Rfull: `U = 0, E = 4.69602035959104`;
- Rsupport64 has the same partition as R0.

### Fixed candidate representation result

Rsupport64 has **one representation class** across all 272 states.

Therefore it fails to recover any of the full-contract operational distinctions.

This remains useful negative evidence: a plausible current path-count support profile does not approximate the operational quotient on this carrier.

### Contract-content anisotropy

Exact singleton audit over all 64 actions:

- 46/64 singleton actions induce **1** operational class — no new distinction;
- 13/64 induce **2** classes;
- 3/64 induce **3** classes;
- 1/64 induces **4** classes;
- 1/64 induces **85** classes.

The dominant singleton:

`del:Q12040649>Q9190427`

alone induces:

- 85 classes;
- operational entropy about `2.865908782` bits.

The full 64-action contract has:

- 101 classes;
- operational entropy about `3.391442482` bits.

Thus the dominant singleton accounts descriptively for:

- 84 of the 100 class splits beyond the initial one-class partition;
- about 84.5% of the full operational entropy.

This is not evidence for a universal scaling law.
It is evidence that **action identity/content can dominate action count** on this carrier.

### Exact pair audit

All `C(64,2)=2016` action pairs were recomputed from the raw matrix.

Operational class counts range from:

[
1 quad 	ext{to} quad 88.
]

The median pair still induces only one operational class.

Therefore two contracts with equal breadth can impose radically different representational demands.

### Exact full-partition action basis — exploratory

Leave-one-action-out analysis of the full 64-action contract gives:

- 51 actions whose removal leaves the 101-class full partition unchanged;
- 13 actions whose removal strictly coarsens the full partition.

The same 13 indispensable actions, without any of the other 51, reconstruct the complete 101-class partition.

Therefore, for this frozen finite carrier and panel:

[
oxed{
	ext{minimum action subset reproducing the full operational partition has size }13
}
]

and every one of those 13 actions is individually necessary for reproducing the full partition.

This is a **post-hoc identification result** and is not promoted to a preregistered M2 claim.

Its scientific role is to motivate a separately frozen contract-basis / identification-complexity experiment.

---

## 3. M2-G v2 audit

### First amended Git rerun

Run `36425245754` used the corrected scientific producer and verifier, but the workflow applied:

`GIT_CONFIG_GLOBAL=/dev/null`

at job scope.

GitHub `actions/checkout` attempted to write its `safe.directory` entry and emitted:

`could not lock config file /dev/null: Permission denied`.

Although the checkout step and jobs ultimately reported success, this run contains an explicit setup error annotation.

### Acceptance judgment

**NOT ACCEPTED as the final M2-G v2 evidence run.**

Its artifacts may be used only for diagnostic cross-checking.

### Clean-runtime repair

A new workflow was created without modifying the scientific producer, protocol, or verifier:

- workflow: `.github/workflows/oacr-m2-g-v2-clean.yml`
- commit: `5b599f7402bf7fbc254414b20360b0ef9e0469be`

The read-only Git config isolation is now scoped only to source clone / experiment processes and no longer pollutes `actions/checkout`.

Clean rerun trigger:

- issue #27: `[OACR M2 G V2 CLEAN RUN]`
- run: `36427766717`

At audit-writing time:

- checkout: passed;
- Python setup: passed;
- Git `2.55.0` assertion: passed;
- frozen `git/git` checkout: passed;
- producer/verifier compile: passed;
- discovery and validation native executions: in progress.

No clean Git scientific result is accepted until producer, verifier, endpoint regression, artifact upload, and artifact-to-artifact reproducibility checks complete.

---

## 4. Diagnostic Git lattice structure — not yet accepted

The invalidated first amended Git run is used only to check what the clean rerun must reproduce.

Both discovery and validation diagnostic artifacts independently reconstruct all 4,096 action subsets with zero internal recomputation mismatch.

Within the frozen 12-target panel:

- full contract: 50 operational classes;
- 2/48 same-tree pairs require separation;
- 46/48 remain equivalent.

For both discovery and held-out validation diagnostic banks:

- only three singleton targets reproduce the full 50-class partition;
- the same three target IDs do so in both splits;
- the other nine singleton targets leave the tree-only 48-class partition unchanged.

The three singleton full-partition target IDs are:

1. `2a2e9cd7c7e23cb3fd1cf74157ce6df8b205226e`;
2. `691dc53e2a18a89f4fa51e943c35c5527e8f81af`;
3. `abb51c0535e1586de1bae4a84a3a8ecd65a364ba`.

This is not yet accepted because the clean rerun has not completed.

Even if reproduced, interpretation must retain the G5 selection boundary: targets were chosen using discovery ancestry disagreement, and the registered outcome includes an already-up-to-date component structurally related to ancestry.

---

## 5. Paper-level correction

M2 should **not** be framed as an empirical proof of the inherited monotonicity theorem

[
mathcal C' succeq mathcal C
Rightarrow
U_{mathcal C'}(R)ge U_{mathcal C}(R),
quad
E_{mathcal C'}(R)le E_{mathcal C}(R).
]

That theorem is inherited and a single nested curve mostly illustrates it.

The empirical object that survives the second audit is stronger and closer to the mother problem:

> **For a fixed number of registered operations, different operation sets can induce radically different required state distinctions. Operational adequacy depends on contract content, not merely contract breadth.**

This is currently an exact developmental result on R3.
Git clean replication is pending.

A second, still exploratory object is:

> **The full operational quotient may be identifiable by a much smaller distinguishing action basis than the registered full panel.**

This reconnects OACR to the question of identification complexity, but must be preregistered on fresh carriers before becoming a paper claim.

---

## 6. Revised paper-strength path

### Retain as core

1. same-contract directional mismatch:
   - coarse current representation can omit required operational distinctions;
   - full internal identity can retain contract-irrelevant distinctions.

2. strictly intermediate operational quotient:
   - established exactly in R3;
   - prospectively finite-contract matched by ancestry vector in G5 validation.

### Strengthen with M2-derived question

Replace the weak empirical slogan

> more operations imply more information demand

with the sharper research question

> **which operations generate new required distinctions, which are redundant, and what minimal operation family identifies the operational quotient?**

### Still required before closure

1. clean M2-G rerun acceptance;
2. fresh M2b carriers for contract-content / basis confirmation;
3. serious learned-system contract/horizon block;
4. representation identification on R3 that is not merely an action lookup table;
5. constructive representation augmentation/compression.

---

## 7. Current acceptance state

### Passed

- R3/G5 finite same-contract directional mismatch;
- R3 strict intermediate operational quotient;
- G5 held-out finite-contract ancestry match;
- M2-R v2 reproducibility and raw-artifact audit;
- M2-R action-content anisotropy as a developmental exact-carrier finding.

### Diagnostic / exploratory

- R3 exact 13-action distinguishing basis;
- invalidated first M2-G v2 lattice artifacts;
- Git singleton-basis structure from those invalidated artifacts.

### Pending

- clean M2-G v2 acceptance;
- fresh-carrier M2b;
- learned expansion;
- representation redesign.

The project should strengthen by improving identification and construction, not by inflating the inherited monotonicity theorem.
