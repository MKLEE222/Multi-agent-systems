# OACR-M2 v2 Rerun Record — 2026-09-28

## Status

Protocol repair and rerun were initiated before interpretation of any M2 v1 scientific outcome.

M2 v1 remains in repository history and is not overwritten.

## Audit sequence

1. Original M2 protocol frozen:
   - `docs/OACR_M2_NESTED_CONTRACT_TRAJECTORY_PROTOCOL_V1.md`
   - commit `8c9b1f7652ecef9d4a8c1f5c580554cd9d241f11`

2. Protocol audit identified:
   - single-chain order dependence;
   - insufficient raw artifact for independent recomputation;
   - uninformative `first adequate prefix`;
   - overly broad interpretation risk relative to action-family breadth.

3. Amendment frozen before inspection of M2 v1 scientific outcomes:
   - `docs/OACR_M2_PROTOCOL_AMENDMENT_V1.md`
   - commit `6c0e174df46f2a2b9796493a4798e895f649e3f3`

4. V2 implementations:
   - relational producer: `experiments/oacr_m2/run_relational_nested_contract_v2.py`
     - commit `54c92ed92ecf40e2df1f5af3a543d7912b4b3bb8`
   - Git producer: `experiments/oacr_m2/run_git_nested_contract_v2.py`
     - commit `1fc6ff367c7b2cc5ad997eba10949c04ce55d0fe`
   - independent artifact verifier: `experiments/oacr_m2/verify_m2_v2_artifact.py`
     - commit `5901ee9923f275004c14ff5fba70c5c73870231b`

5. V2 workflows:
   - relational: `.github/workflows/oacr-m2-r-v2.yml`
     - commit `caff8eca65c88b2a2d13c789329dfd4c526dd092`
   - Git: `.github/workflows/oacr-m2-g-v2.yml`
     - commit `914837f8bc0a2982ac1c52678760ce2e5771551c`

## Rerun triggers

- issue #25: `[OACR M2 R V2 RUN]`
- issue #26: `[OACR M2 G V2 RUN]`

Observed workflow runs:

- M2-R v2: run `36425222754`
- M2-G v2: run `36425245754`

At the time this record was written:

- environment/runtime setup had passed;
- producer steps were in progress;
- independent-verifier steps had not yet run;
- no v2 scientific result had been interpreted.

## V2 validity gate

A v2 result is valid only if all of the following pass:

1. source/runtime identity checks;
2. producer completes;
3. full-contract endpoint regression reproduces frozen R3/G5 values;
4. canonical nested-refinement audit passes;
5. complete raw manifests/signatures/outcome matrix are embedded in artifact;
6. manifest hashes are emitted;
7. the separate verifier reconstructs every analyzed operational partition and directional gap from the artifact alone;
8. verifier status is `PASS`;
9. artifact upload succeeds.

Failure of any gate is retained as a failed run and is not repaired by post-hoc result selection.
