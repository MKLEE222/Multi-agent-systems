# OACR-SQEC Continuation Repair Acceptance — 2026-09-30

## Authority

Scientific protocol:

\`qualification_opportunity_compiler/01_protocol/OACR_SQEC_CONTINUATION_REPAIR_PROTOCOL_V1_20260930.md\`

Protocol commit:

\`83091035685b8d11fc1b293051285835d9c1feb7\`

Frozen SQEC source snapshot:

\`4f37a0af1c2cb44b2eb7eb1b187d96a2ebd34295\`

Exact vendored source manifest:

\`external/sqec_snapshot_4f37a0af/SNAPSHOT_MANIFEST.json\`

Main-repository acceptance run:

\`36666758877\`

Artifact:

- name: \`oacr-sqec-vendored-continuation-repair-v1\`
- artifact ID: \`11076199541\`
- artifact ZIP digest:
  \`sha256:90c3abe986174eec1b183764bc2a01f7db9944d95b6e4b54f36364fb825417b4\`

Producer JSON SHA-256:

\`ed07b826465cfff7e29413637b9cf62b5a5864fffe6a398b41f01786126eb474\`

Verifier JSON SHA-256:

\`2ba322724934d1e1e094d07b575b451e2488fc32433eded9dcb305718b8caaf0\`

## Execution boundary

The original SQEC-repository Actions job failed before runner assignment and executed zero workflow steps.

The accepted run therefore used a byte-identical vendored snapshot of the frozen SQEC source commit. Before execution, the workflow verified every vendored file against its original SQEC Git blob SHA.

No scientific family, representation, sequence, or acceptance rule changed.

## Frozen family

Eight variants:

\[
v\in\{0,\ldots,7\}.
\]

Predeclared delayed-guard positive controls:

\[
\{0,2,4,6\}.
\]

Predeclared no-divergence controls:

\[
\{1,3,5,7\}.
\]

Registered event alphabet:

- \`commit-task\`
- \`universal-remediation\`
- \`observe-qualified\`
- \`observe-unqualified\`

The complete continuation contract contains every ordered event sequence of length 1 and 2.

## Primary result

FULL vs PROJECTED:

\[
\boxed{
\text{H1 mismatches}=0
}
\]

across the complete frozen family.

At depth 2:

\[
\boxed{
\text{H2 mismatches}=8.
}
\]

All frozen positive-control variants satisfy the delayed-guard prediction; no frozen negative-control variant produces an unexpected H2 mismatch.

Thus the omitted guard is dormant under the registered root interface but becomes necessary after a common first action moves the guarded coordinate outside its allowed state.

## Constructive repair

GUARD-REPAIRED adds one frozen canonical rule:

\[
G_{\rm obs}
=
(
\texttt{s::observation-route},
\{ACTION\_OPEN,SATISFIED\}
).
\]

Across all eight variants and the complete registered depth-1/depth-2 continuation matrix:

\[
\boxed{
\text{FULL vs GUARD-REPAIRED mismatches}=0.
}
\]

The full typed event representation stores two observation-event precondition clauses; the repaired representation stores one shared canonical guard rule. This count is representation accounting, not a byte-optimality claim.

## Independent verification

Independent verifier result:

- \`verified = true\`
- variants: 8
- projected H1 mismatches: 0
- projected H2 mismatches: 8
- repaired depth<=2 mismatches: 0
- verifier mismatch count: 0

The verifier reconstructed the frozen family and recomputed every registered sequence signature rather than trusting producer signatures.

## Scientific interpretation

Accepted bounded claim:

> A representation can be exact for the registered immediate continuation interface yet fail under composition when a first transformation changes a coordinate that qualifies a later transformation. Adding the prospectively frozen state-dependent guard coordinate restores the complete registered depth-two continuation matrix.

This result supplies a second-substrate constructive OACR confirmation outside the relational graph carrier.

Not claimed:

- novelty of state-dependent guards;
- universal minimality;
- natural prevalence;
- necessity of qualification for every COMPOSE effect;
- byte-optimal compression.

## Paper role

This result upgrades the paper from:

\[
\text{graph audit}\rightarrow\text{graph repair}
\]

to:

\[
\boxed{
\text{native-contract audit}\rightarrow\text{representation repair}
}
\]

demonstrated in both:

1. exact relational deletion dynamics;
2. typed dynamic-qualification continuation.

The relational carrier provides exact under/over-refinement quotient matching; SQEC provides prospective delayed continuation failure and prospective repair under state-dependent qualification.
