# OACR Checkpoint — 2026-09-28 v2

## 1. Status after same-contract reruns

The red-team concern was valid: R2 and G3 mixed strong-looking results with construction/action coupling.

R3 and G5 were therefore preregistered to require one shared operation contract per state bank, and G5 additionally used held-out validation.

All current runs completed successfully.

## 2. OACR-R3 — shared-contract exact relational matrix

**Run:** 36385544527  
**Artifact:** `oacr-r3-v1`  
**Artifact ID:** 10954033797  
**Artifact ZIP digest:** `sha256:0d631fd0436331d4aa02fa05c510efbb3e3fced140990f2932898741ba9ff29d`  
**Result JSON SHA256:** `f1e5b1f3d1af42256b0875928638506167ca69f0ce2af7f487fd2821d0911829`

Frozen state bank:
- 272 states = base graph + all 271 single redundant-edge augmentations;
- every state has exactly the same complete current registered transitive closure.

Frozen action contract:
- one global 64-edge deletion alphabet;
- action edges selected only from base-graph deletion impact before augmented-state outcomes were inspected.

Operational result:
- 101 exact H=1 operational classes;
- largest operational class contains 172/272 states;
- the remaining 100 states are singleton operational classes.

Therefore the exact operational partition is strictly intermediate:

[
1 < 101 < 272.
]

### Representation diagnostics

#### R0 — current closure only
- 1 representation class;
- under-refinement pairs: 22,150;
- over-refinement pairs: 0;
- U = H(O|R) = 3.391442481659308 bits;
- E = H(R|O) = 0.

R0 is genuinely too coarse for the shared deletion contract.

#### Rfull — complete asserted-edge identity
- 272 representation classes;
- under-refinement pairs: 0;
- over-refinement pairs: 14,706;
- U = 0;
- E = 4.69602035959104 bits.

Rfull is adequate but strongly over-refines the same shared contract.

#### Rsupport — 64 action-endpoint current path counts
- 1 representation class;
- same diagnostics as R0;
- U = 3.391442481659308;
- E = 0.

This simple support profile fails completely to recover the required operational distinctions.

### R3 interpretation

R3 directly establishes, on one exact controlled carrier and one shared contract, that:

1. complete current semantic closure can be too coarse;
2. complete asserted state identity can be too fine;
3. the operation-required partition lies strictly between them;
4. a plausible intermediate support-count representation can still be insufficient.

This result is not a natural-history prevalence result and does not identify a minimal structural encoding.

## 3. OACR-G5 — natural same-contract Git discovery + held-out validation

**Run:** 36385706858

Discovery artifact:
- `oacr-g5-discovery-v1`
- artifact ID 10954224696
- ZIP digest `sha256:218586a2ec5796e87f8b188ead39d9b447d239a78cd168d21188daffa5055739`
- result JSON SHA256 `0336c12f902c29aa49e5700d9f6f5da468149a393952aae44c1dddfbb20b41a4`

Validation artifact:
- `oacr-g5-validation-v1`
- artifact ID 10954788549
- ZIP digest `sha256:15de1a3d99c7f50a72c947f7b0572a80d871d056319124603c5a350187a46d29`

Design:
- public `git/git` frozen source;
- 48 natural same-tree discovery pairs;
- 48 disjoint natural same-tree validation pairs;
- one shared 12-target native merge action panel;
- target selection used ancestry structure on discovery only and no merge outcomes;
- validation did not participate in action selection.

### Discovery

96 states / 48 same-tree pairs:
- required pair separations: 2;
- behaviorally equivalent pairs: 46;
- exact H=1 operational classes: 50.

Representation results:
- tree only: U = 0.04166666666666696, E = 0, 2 under-refinement pairs;
- full commit identity: U = 0, E = 0.958333333333333, 46 over-refinement pairs;
- tree + target-ancestry vector: U = 0, E = 0, exact partition match;
- tree + merge-base vector: U = 0, E = 0.9166666666666661, 44 over-refinement pairs.

Discovery ancestry-vector exactness is selection-biased and is not a held-out claim.

### Held-out validation

96 states / 48 disjoint same-tree pairs:
- required pair separations: 2;
- behaviorally equivalent pairs: 46;
- exact H=1 operational classes: 50.

Representation results:
- tree only:
  - 48 classes;
  - under-refinement pairs: 2;
  - over-refinement pairs: 0;
  - U = 0.04166666666666696, E = 0.

- full commit identity:
  - 96 classes;
  - under-refinement: 0;
  - over-refinement: 46;
  - U = 0, E = 0.958333333333333.

- tree + target-ancestry vector:
  - 50 classes;
  - under-refinement: 0;
  - over-refinement: 0;
  - U = 0, E = 0;
  - exact match to the held-out operational partition.

- tree + merge-base vector:
  - 89 classes;
  - under-refinement: 0;
  - over-refinement: 39;
  - U = 0, E = 0.8124999999999991.

### G5 interpretation

This is the strongest current natural same-contract result.

On a held-out natural bank:

1. current tree equality is too coarse for some pairs;
2. full commit identity is too fine for most pairs;
3. the frozen target-ancestry vector exactly matches the finite registered operational partition;
4. merge-base retains substantial unnecessary detail.

Critical boundary:
- only 2/48 validation pairs require separation;
- the action panel was intentionally selected to stress ancestry diversity using discovery states;
- because `already-up-to-date` is part of the native merge outcome, target ancestry has a structurally privileged relationship to this contract.

Therefore G5 supports a prospective finite-contract result, not universal minimality of ancestry.

## 4. OACR-L1 — GRACE H=2 prospective horizon diagnostic

**Run:** 36383356207  
**Seeds:** 73, 137, 211, 307, 401  
**All five jobs:** success

Every seed produced:
- 2 contract-valid initial states;
- 1 H=0 collision pair;
- 3 registered actions;
- complete H=2 branching;
- transitive pairwise equivalence at H=0,1,2;
- N0 = N1 = N2 = 1;
- 0 H0-to-H1 separations;
- 0 H1-to-H2 separations.

Aggregate:
- 5 H=0 collision pairs;
- 0 separations at H=1;
- 0 separations at H=2.

Candidate features:
- F1 root update-mode vector: no over-refinement on the five pairs;
- F2 route/protected-route representation: over-refines 5/5;
- F3 route + projected structural-effect representation: over-refines 5/5.

Duplicate replay controls passed.

### L1 interpretation

This is a clean multi-seed negative, not a learned positive horizon result.

It strengthens W1:

> the registered GRACE routing/structural distinctions remained unnecessary through H=2 on every frozen pair tested.

However the state bank is smaller than the protocol's aspirational maximum:
- only 2 states per seed survived the contract-preserving construction;
- therefore only 5 total collision pairs were tested.

L1 is diagnostic evidence, not final learned-system scale.

## 5. What is genuinely stronger now

The previous same-contract gap has been closed in two carriers.

### Exact carrier

R3 has a coarse representation with U > 0, E = 0 and a fine representation with U = 0, E > 0 under the same exact shared deletion contract.

### Natural held-out carrier

G5 validation independently has the same pattern:
- tree only: U > 0, E = 0;
- commit identity: U = 0, E > 0;
- ancestry-vector representation: U = E = 0 on the frozen held-out finite contract.

This is substantially stronger than the earlier pair-specific witness design.

## 6. What is still not earned

Do not yet claim:

1. target ancestry is a universally minimal Git representation;
2. OACR has found the minimal relational representation in R3;
3. the GRACE learned carrier exhibits horizon-induced operational refinement;
4. U/E is itself a new information-theoretic construction;
5. the same quantitative law has been shown across broad learned systems;
6. OACR is already a representation-design method.

The next high-value gates are:

- replicate G5 prospectively on additional repositories and stronger/more diverse shared action panels;
- turn R3 into a constructive compression/augmentation problem;
- scale learned evidence beyond the five two-state GRACE pairs and add a second learned write ecology;
- test the contract-expansion trajectory (omission nondecreasing, excess nonincreasing) empirically with nested frozen contracts.
