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


## Second recovery run

Run: \`36662958763\`.

The run completed:

- accepted artifact recovery;
- current full \`git/git\` clone;
- original-to-reconstructed commit mapping;
- structural validation invocation.

It then failed while constructing the structural report because the implementation referenced \`bank_sha\` and \`manifest_sha\` before initializing those variables in \`main\`.

The failure occurred **before** the 1152-cell H1 replay at \`validate_h1(...)\`.

Therefore the run did not expose a new H1 scientific result and did not establish carrier acceptance.

An intermediate mapping artifact was uploaded only because the workflow's artifact-upload step was unconditional; it is not an accepted executable carrier.

Engineering fix commit:

\`f18d06c1fc5080321e903ab89b77427c68da7948\`.

Repair only:

- initialize and validate the accepted-bank SHA-256;
- initialize and validate the exact required-SHA manifest SHA-256;
- carry those values into the structural/final reports.

No reconstruction rule, structural criterion, H1 replay rule, or H2 scientific rule changed.


## Third recovery run

Run: \`36664072593\`.

The run successfully completed:

- accepted G5 artifact recovery;
- full current \`git/git\` object-cache clone;
- original-to-reconstructed commit mapping;
- structural validation.

It then entered the 1152-cell H1 native replay and failed inside the historical G5 helper before producing a signature comparison:

\`UnicodeDecodeError: 'utf-8' codec can't decode byte ...\`

The historical helper executed:

\`git diff --binary --no-ext-diff HEAD\`

through \`subprocess.run(..., text=True)\`, then computed:

\`sha256(diff.encode())\`.

A replay cell emitted non-UTF-8 diff bytes, so Python's text decoder raised before the registered \`tracked_delta_sha256\` or H1 signature could be computed.

No H1 signature mismatch was observed before the exception.

Engineering repair commit:

\`3ebfb907eee70f2685486aa3196b9fbd884d3981\`.

Repair:

- reproduce the exact historical payload schema;
- hash \`git diff --binary\` stdout as raw bytes;
- decode only human-readable/status fields with surrogate-safe handling.

For every historical UTF-8-decodable diff, raw-byte SHA-256 is identical to the historical \`sha256(diff.encode())\` computation. The repair therefore extends the executor to byte-arbitrary Git content without changing the registered signature fields, source bank, action panel, or H1 acceptance criterion.

Carrier acceptance still requires 1152/1152 H1 cells and zero signature mismatches before bundle creation.
