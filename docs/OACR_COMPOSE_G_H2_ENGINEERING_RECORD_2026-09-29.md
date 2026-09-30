# OACR-COMPOSE-G H2 Engineering Record

**Date:** 2026-09-29  
**Affected run:** 36579714789  
**Scientific protocol:** \`docs/OACR_COMPOSE_G_G5_H2_PROTOCOL_V1_2026-09-29.md\`  
**Protocol commit:** \`c38fa8b922dc2d11b5eb2e1b41e97e1ba72cf565\`

## Exposed producer outcome

The prospective producer completed successfully before the verifier failed:

- source pairs: 46;
- frozen targets: 12;
- registered ordered target pairs per source pair: 132;
- H2-eligible sequences after the frozen H1 gate: 176;
- H2 divergent sequences: 0;
- pairs with any H2 divergence: 0;
- H1 reproduction mismatches: 0.

Producer JSON SHA-256 printed by the run:

\`08e42fec19f7ae9e39e1d5d0937ae0fa8cfa45dbf8f1fb3a2a8c3eeb4f500045\`.

This outcome is now exposed and must not be used to alter carrier, pair, target, gate, or outcome rules.

## Verifier failure

The independent verifier failed before any H2 recomputation with:

\`RuntimeError: source head mismatch\`.

Cause:

- the producer deliberately performs detached checkouts for each frozen pair;
- after producer completion, the working repository remains detached at the last replayed pair head;
- the verifier incorrectly required the caller's current checkout to equal the frozen git/git source head before normalizing its own state.

This is an implementation precondition bug, not a scientific failure.

## Engineering-only correction

Verifier commit:

\`4fdebf6ad3732c8df5618c5f0289745b6b453175\`.

Correction:

- explicitly reset/checkout the verifier repository to the already frozen source head before verification;
- then assert that normalization succeeded.

Unchanged:

- 46 source pairs;
- 12 targets;
- 132 ordered target pairs per source pair;
- H1 gate;
- deterministic persisted-merge construction;
- H2 outcome signature;
- divergence criterion;
- full-sequence independent recomputation.

No scientific selection rule changed after the zero outcome was exposed.

## Acceptance rule

The producer zero is not accepted until an independent clean verifier recomputes the frozen matrix and agrees exactly.

A clean rerun may reproduce the producer under the unchanged protocol solely to regenerate the artifact and execute the repaired verifier.


## Second verifier engineering correction

Clean rerun \`36592660033\` reproduced the producer output exactly, including the same producer SHA-256:

\`08e42fec19f7ae9e39e1d5d0937ae0fa8cfa45dbf8f1fb3a2a8c3eeb4f500045\`.

The verifier then advanced past source-head normalization but failed on its first native \`git merge --no-commit --no-ff\` because Git 2.55 required an explicit committer identity in the clean runner environment.

This failure occurred before any independent H2 comparison.

Engineering correction commit:

\`7522889a3ae1347120161a59b62b41c43f7257b2\`.

Correction:

- set repository-local \`user.name\` and \`user.email\` to the same already-frozen deterministic identity used by the persisted merge construction.

Again unchanged:

- all scientific banks and action rules;
- H1 gate;
- H2 outcome contract;
- divergence criterion;
- producer code and exposed zero result.

A further clean rerun is permitted solely to complete independent replay.
