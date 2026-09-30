# OACR G5 Carrier Recovery Engineering Record

**Date:** 2026-09-30  
**Recovery protocol:** \`docs/OACR_G5_CARRIER_RECOVERY_PROTOCOL_V1_2026-09-30.md\`

## Initial recovery run

Run: \`36659549136\`.

Completed successfully:

- workflow checkout;
- implementation compile;
- accepted G5 validation artifact recovery;
- current full \`git/git\` clone.

The recovery producer then stopped immediately before any GitHub API/object reconstruction with:

\`RuntimeError: required SHA count changed: 108\`.

Cause:

- implementation contained an incorrect manually counted expectation of 104 unique required commit SHAs;
- exact accepted artifact audit gives:
  - 1 source head;
  - 12 targets;
  - 48 A commits;
  - 48 B commits;
  - source head overlaps one B commit;
  - 108 unique SHAs.

No object reconstruction, synthetic commit construction, H1 native replay, or bundle creation occurred in this run.

## Repair

Accepted validation JSON SHA-256:

\`964a3ea6161705721cd3442ceb2c6401c490e69129158ce29fdf2f6151d2fdd7\`.

Exact sorted required-SHA manifest SHA-256:

\`2f6289cc26d4d6c9c43891dcc9d8a8dbe7d09e431e6dd2dd4f254d37f4b39d8e\`.

Repairs:

- protocol correction commit: \`e58a1b1563aa1f6d1c2d098e598adf134362f9e5\`;
- producer correction commit: \`6d3d0335f0feb3bd1eda34567dea7ce7e306fd60\`.

The producer now validates both the accepted JSON digest and exact required-SHA manifest digest rather than relying on a hand-counted cardinality.

Scientific G5/H2 rules remain unchanged.
