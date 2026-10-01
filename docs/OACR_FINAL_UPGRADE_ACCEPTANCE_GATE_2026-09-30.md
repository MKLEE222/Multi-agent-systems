# OACR Final Upgrade & Acceptance Gate

Original freeze: 2026-09-30
Current audit update: 2026-10-01
Status: FROZEN UPGRADE CRITERIA; CORE CLAIM PROMOTION REOPENED

This remains the sole upgrade acceptance gate. New work must close Theory,
Identification, or Natural Evidence. The original T/I/N requirements below remain
in force; the present update adds stronger execution and information-availability
obligations, not easier thresholds. Earlier progress judgments are retained in git
history (previous gate blob dc31a17f0bad50422391647c00eb520b21f57914) and do not
overrule this audit.

## Immediate decision: core work does not wait for the learned smoke

The existing GRACE/RippleEdits N1 dev smoke is an ancillary task-performance and
implementation branch. Let its pinned run complete without retrospective changes.
A positive smoke can support only the claim actually measured. It cannot validate
an operational quotient, satisfy the core theory gate, or unlock the 512-unit
evaluation bank automatically. A negative smoke cannot establish that the whole
learned representation family is impossible.

Core reference:
- docs/OACR_CORE_REPAIRABILITY_EXECUTION_UPGRADE_2026-10-01.md
- experiments/oacr_theory/contract_budget_audit_v1.py
- docs/OACR_CORE_BUDGET_AUDIT_RESULT_2026-10-01.json
- docs/OACR_BRFP_CORE_UPGRADE_EXECUTION_2026-10-01.md
- experiments/oacr_theory/available_source_repair_v1.py

## Current promotion status

### Theory

- T1 REOPENED: representation partitions may be incomparable, with U>0 and E>0
  simultaneously. Separate class exactness, native decoder correctness, and the
  cost objective that makes excess distinctions undesirable.
- T2/T4 QUALIFIED: canonical source-backed encoders and Hamming-optimal feature
  changes do not imply executable recovery from a genuinely erased coarse state.
  Statewise source witnesses and their storage/acquisition cost must be explicit.
- T3 WORKING CANDIDATE: original one-delta static exactness is preserved with its
  stated assumptions. A budgeted-deletion extension now supplies a restricted-cut
  compiler, an explicit decoder, and a residual-budget update with a no-resurrection
  proof. The same-input semantic baseline has now executed; cold proof review
  and independent-result/efficiency comparison remain open.
- T5 REOPENED: a checklist of different ingredients is not a novelty clearance.
  Include complete extensions AND restrictions (JACM 2000), observational
  completeness, automata/state abstraction, and fault-tolerant reachability.

### Identification

- Keep the existing I5 execution result as a methodological demonstration with
  its original retrospective/prospective labels; it is not independent novelty.
- I1-I4 REQUIRE EXECUTION-LEVEL RECHECK: no adaptive evaluation feedback, actual
  deployment information, permitted oracle/simulator calls, computational cost,
  and semantic validity are separate dimensions.
- An outcome-aware verified synthesis algorithm can be valuable. It does not
  establish outcome-independent discovery on the same target outcomes.
- A two-key test-visible heuristic is not a proven oracle ceiling.

### Natural evidence

- N0 retains its historical structural preflight result: frozen 128 development
  and 512 evaluation unit IDs. These are manifests, not completed model evidence.
- The present N1 runner measures future-query answer accuracy. It does not compute
  U/E over a declared state/representation/behavior bank and does not yet establish
  maintainable representation repair under subsequent native edits.
- Identical criterion names across units are not by themselves proof of an
  identical action panel or a shared cross-unit operational quotient.
- Raw unit-ID disjointness is not proof of statistical independence. Audit shared
  subjects, facts, prompts and source clusters before claiming independent units.
- No evaluation unlock until the scientific estimand, implementation invariants,
  hard controls, denominators and final constructor are frozen and reviewed.

## Added core execution requirements

### R1. Available-input repairability

Let Q be the target contract class and Z the full authorized per-instance repair
view. An unrestricted deterministic exact encoder exists iff equal Z implies
equal Q. If a coarse representation merges two different Q classes, no function
of that representation and shared contract alone can recover the distinction.

Any additive arrow must therefore name its statewise source witness W, retained
log, original assertion, or reacquisition procedure. Source-backed recompilation
and online recovery from a lossy state are different claims.

### R2. Encoder, decoder, updater

Require separately:

    ker(Enc) = ker(B_C)
    B_C(Dec(Enc(x))) = B_C(x)

For maintained representations, also establish an executable residual-contract
update, on the transition-closed reachable domain:

    Update_a(Enc_C(x)) = Enc_(C/a)(T_a(x)).

Account for remaining horizon and legality. Do not reset a finite horizon after
each action without proving a stronger stationary congruence.

### R3. Irreversibility and contract expansion

A safely dropped distinction under one contract can become required by a larger
contract. Path-independent recomputation from raw data does not imply reversible
online updates after destructive compression. Charge source availability and
reacquisition; do not secretly consult the full state.

### R4. Computational and scientific separation

A frozen exhaustive simulator may satisfy no-adaptive-feedback provenance. It is
not automatically a novel or efficient constructor. Report oracle/native calls,
compilation cost, storage, update cost, and replay cost separately.

### R5. Reference behavior versus task correctness

Preserving a native behavior quotient and changing answers toward task labels are
different estimands. Neither can be substituted for the other. A learned branch
must explicitly say which it tests.

## New executed core audit (not natural-system evidence)

Dependency-free reference implementation, executed locally on 2026-10-01:
- constructor: restricted min-cut via Edmonds-Karp;
- verifier path: deletion-set enumeration and BFS native reachability;
- all topologically labelled DAGs on 2 through 5 vertices;
- 182,104 graph/action-bank/budget contracts, zero quotient mismatches;
- 1,453,876 commuting one-step update checks;
- 6,234,453 state/failure decoder-replay checks;
- 6,234,453 residual no-resurrection checks;
- 256 small information-factorization cases;
- seven explicit counterexamples to overstrong interpretations.

Both code paths were authored in this audit. This is not independent human review,
not a formal proof assistant certificate, not a new natural replication, and not
millions of independent samples. General proof and novelty review remain open.

## Gate T — Theory (original substantive requirements retained)

### 2026-10-01 follow-up execution; thresholds unchanged

- Common-task competition: EC², EffECXtive and class information gain each use
  460 source queries on the same 138 exposed development worlds, matching the
  exact expected-optimal control and a simple structural short-span order. The
  new one-step selector uses 464 queries, versus 568/536 for the inherited orders.
  All nine methods return the same native physical representations and pass
  residual maintenance. Explicit model computation is legal and charged; cold
  implementation counts do not establish intrinsic or production cost superiority.
  The source-acquisition gain is not unique. Native public-task competition is
  specified but not yet run; T2/T5 and natural evidence remain open. See
  `docs/OACR_COMMON_ARENA_AND_PAPER_DIRECTION_2026-10-01.md`.
- Anti-circular algorithm extraction: a working multi-addition source-fiber and
  stopping-condition derivation now supports joint authorized acquisition and
  compilation. In 7,392 paired synthetic development configurations, adaptive
  acquisition completed 1,406 vs 1,328 for a static-demand ablation; all successful
  native and residual checks passed. A separately declared same-information
  optimal query-policy control uses 460 queries over 138 full-budget worlds,
  versus 568/536 for the fixed greedy orders. Public simulation is allowed and
  charged, not leakage. Query optimality, total-cost advantage and T2/T5 remain
  open; SBFE/SSSC must enter the nearest-neighbor comparison. See
  `docs/OACR_ANTICIRCULAR_ALGORITHM_PROMOTION_REVIEW_2026-10-01.md`.
- Available-source interface: 1,664 frozen development configurations using only
  an old exact label, public contracts and an authorized singleton membership
  source produced 938 exact repairs and 726 genuinely ambiguous unresolved
  branches. Native decoding and residual checks passed; no unauthorized, stale
  or over-budget producer queries. This executes an R1/R3/R4 reference interface,
  not T2/T5 or natural evidence. Initial source retention remains an explicit,
  unmeasured external prerequisite. See
  `docs/OACR_BRFP_CORE_UPGRADE_EXECUTION_2026-10-01.md`.
- Same-input comparison: standard residual-state partition refinement reproduces
  the compiler's partition on all 182,104 inherited contracts, with 11,761,605
  pair checks and 13,703,208 commuting transitions per implementation. This
  closes the missing implemented semantic baseline, **not T2/T5**. See
  `docs/OACR_SAME_INPUT_NEIGHBOR_COMPARISON_2026-10-01.md`.
- T3 extension candidate: conditioning each edge cut on the other persistent
  additions yields a least-subset compiler and residual updater in acyclic,
  base-edge-failure, full-reachability carriers. 940 multi-addition contracts
  passed synthetic checks; same-assistant proof and code, cold review open.
  Classical transitive reduction/mincut is load-bearing. See
  `docs/OACR_MULTI_DELTA_CONDITIONAL_CUT_CANDIDATE_2026-10-01.md`.
- N1 localization: exact observer replay found B1/sham gate activation 0/66;
  forced all-key gates changed all layer outputs and increased correctness from
  3/66 to 7/66, but all variants were identical, with gains and losses. This is
  retrospective task-performance diagnosis, with no semantic key advantage or
  quotient evidence. See `docs/OACR_N1_ROUTING_AND_GATE_VERDICT_2026-10-01.md`.
- Evaluation seal: unchanged at 512 units. Next constructor development is
  separately specified in `docs/OACR_NEXT_DEVELOPMENT_PROTOCOL_2026-10-01.md`.

### T1. Contract-Adequate Representation Repair

Define finite state bank X, continuation contract C, implemented representation R,
admissible representation/repair family F, and cost c. Define exact, minimal and
approximate repair. Cover both coarse-to-target and fine-to-target correction,
now also mixed/incomparable errors and the available-input constraint R1.

### T2. Nontrivial general theory

At least one load-bearing result: computational hardness, necessary-and-sufficient
existence, uniqueness up to partition equivalence, confluence/common target,
optimality, or an equivalent theorem family. Routine entropy identities and
renamed minimum-test-set results do not satisfy this gate.

### T3. Tractable structural class

Identify assumptions making exact repair tractable. State the theorem independently
of the observed outcome matrix. Include encoder, native decoder and, where claimed,
residual updater correctness. Do not turn finite enumeration into a proof.

### T4. Bidirectional repair

Characterize common target, reachability in the admissible repair language, and
failure under feature interactions. Distinguish source-backed design symmetry
from reversible operation under information loss and changing contracts.

### T5. Nearest-neighbor acceptance

Directly compare strong preservation, complete cores/shells, AIR, CEGAR,
Verifix/program repair, summary repair, observational completeness, state
minimization and relevant graph algorithms. A familiar reviewer must be able to
state the independent problem and result, not merely a combination of labels.

## Gate I — Identification / Anti-circularity

### I1. Information authority

Declare construction-visible data and verification-only outcomes, plus actual
per-state information still available at repair/deployment time.

### I2. Non-anticipation

Freeze constructor choices without adaptive use of the realized evaluation
outcomes. Do not misdescribe predictability from legal inputs as leakage or
claim statistical independence. Account separately for simulation/oracle access.

### I3. Audit/constructor narrative

Audit may diagnose; a separately permissioned constructor proposes; independent
native replay verifies. Do not imply that the audit synthesized a certificate
when the accepted implementation did not do so.

### I4. Unified identification framework

Retain same-contract comparison, freeze-before-outcome, forbidden reads,
outcome-blind selection, fixed interpreter, producer/verifier separation,
independent replay, and matched-cost sham controls. A common code bug can survive
a same-implementation verifier; inspect distinct implementation paths.

### I5. Executable circularity demonstration

Show that outcome-visible encoding can reproduce the target quotient. Contrast
with declared predictive construction. Preserve the original R4 demonstration's
retrospective status and SQEC's separate matched-control provenance.

## Gate N — Natural Evidence

### N1. Mature natural benchmark

Use a frozen established source such as RippleEdits, MQuAKE, CounterFact/ZsRE, or
another appropriate sequential/dependent-edit substrate.

### N2. Common continuation contract

Comparable states face the same predeclared operations, outcome schema and
weights. No pair-specific outcome-driven panel selection. Scope any unit-specific
contracts explicitly rather than silently pooling their equivalence classes.

### N3. Natural scale

Hundreds of genuinely independent or explicitly clustered evaluation units for
at least one learned carrier; preferably multiple editors and, if feasible,
model families. State the unit, cluster and conditional denominators separately.

### N4. Learned constructive repair

Require diagnosed inadequacy, a contract-relevant representational intervention,
a fixed native mechanism, and improvement on the declared semantic target.
Matched irrelevant/sham intervention is required; model replacement does not
count. Task accuracy alone is not operational quotient exactness.

### N5. Scientific negative boundary

A prospectively frozen failure must localize what failed: implementation,
optimization, constructor, representation budget/family, or stochastic execution.
A failed heuristic or non-optimized A0 control does not prove family-level
impossibility. No evaluation-tuned rescue or failed-unit removal.

## Existing evidence authority

The following are historical accepted claims, not new reruns in this audit:
- R4 building: 272 states, 64 actions, 17,408 native outcomes, 23 classes,
  22/271 retained deltas; maintain original protocol/replay authority.
- R3: developmental structural replication, not fresh confirmation.
- SQEC fixed-interpreter comparison: H1 mismatch 0, H2 mismatch 12;
  relevant repair 12 to 0; equal-cost sham 12 to 12.
- WACT-R 80/80: selection-conditioned denominator.
- GRACE 224 collision pairs: 64 underlying states, not 224 independent systems.
- Finetune single positive pair: mechanism witness, not natural-scale evidence.
- Later R4 roots retain their own acceptance artifacts; do not infer their
  acceptance solely from this gate's summary.

## Final identity and stop rule

Target contributions remain theory, identification and evidence, but publication
strength is not licensed by a progress percentage or a successful workflow.

Allowed final verdicts:
- UPGRADE PASS: all substantive T/I/N gates and added R1-R5 obligations pass.
- SCIENTIFIC PASS / UPGRADE INCOMPLETE: specifically delimited surviving claims
  pass their own tests; unresolved upgrades are not promoted.
- BLOCKED: a contradiction, leakage path or failed core replay invalidates a
  promoted claim. Specify the affected claim rather than erasing valid results.

No additional carrier, theorem, or experiment is authorized merely to increase
volume. Core improvement proceeds now, independently of the N1 smoke outcome.
