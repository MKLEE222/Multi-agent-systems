# OACR-L2b Fold0 Targeted Replay Engineering Record — 2026-09-29

## Status

The first targeted replay run executed the scientific replay successfully but failed after the replay because the relative output path was resolved after the replay script changed working directory into the checked-out GRACE repository.

Scientific replay stdout reported:

- status: PASS_POSITIVE_REPLAY;
- deterministic_two_reconstructions_equal: true;
- H0 task equality reproduced;
- separating actions: 51, 29, 73;
- task-level branch difference counts: 3, 11, and 5 respectively.

The workflow then failed only when `sha256sum` looked for the replay JSON at the caller-relative path.

## Allowed repair

Change only the `--out` argument to an absolute `$GITHUB_WORKSPACE` path.

No change is authorized to:

- model/editor;
- frozen assets;
- seed IDs;
- anchor ID 688;
- future action IDs 51/29/73;
- READ contract;
- replay logic;
- deterministic double reconstruction;
- acceptance criteria.

The clean rerun is required solely to persist the already executed replay artifact and hash it successfully.
