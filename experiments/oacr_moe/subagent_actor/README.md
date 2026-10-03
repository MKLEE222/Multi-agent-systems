# Subagent-native AppWorld train smoke v2

Three independent cold subagents completed the first three IDs of the pinned native
train manifest. These are variants of **one scenario**: 3/3 task success, 6/6 native
tests, 16 code interactions and 131 API calls. This is execution feasibility, not a
complete ACE reproduction or an OCAR comparison.

See `docs/OACR_SUBAGENT_NATIVE_TASK_EXECUTION_2026-10-02.md` for the result and
`docs/OACR_SUBAGENT_NATIVE_TASK_PROTOCOL_2026-10-02.md` for the frozen protocol.
The executed bridge/client/freeze were committed before actors at
`faf4203d12578ebfd62169c9586907be11dc9033`. Do not edit these files and relabel
their existing results. `export_results.py` is a posthoc auditor, not a producer.

## Assets

- `freeze.json`: selected hashes, budget, native version, implementation hashes.
- `native_actor_bridge.py`, `actor_client.py`: file-mailbox native actor interface.
- `startup_failure_v1.json`: socket launch failure before any actor action.
- `task_{0,1,2}_summary.json`, `RESULT_2026-10-02.json`: public counts and hashes.
- `protected_traces.bundle.b64`: local author-format encrypted trace archive,
  excluded from GitHub upload. Automatic approval rejected external disclosure
  without explicit authorization for protected benchmark-derived traces. The
  public directory contains only code, aggregate counts, metadata and hashes.

The source is `ace-agent/ace-appworld@9f3e92155345a9159f3a8b25abc334eeca05b545`,
AppWorld 0.1.4.dev0, with its original downloaded data and licenses. Use the
compatible isolated environment recorded in `../baseline_capsule/`. The exact
subagent model version, sampling seed, token usage and billing are unavailable;
subagent model usage was nonzero.

## Interface

These commands illustrate the executed interface. Use a fresh checkout/data copy
and fresh output directories for a new experiment; the native experiment names
are fixed inside the frozen bridge. Never overwrite this run's freeze/results.
Set `APPWORLD_SOURCE`, `ACTOR_DIR`, `RUN_DIR` and `NATIVE_PYTHON` to absolute paths
for the pinned source, copied bridge directory, fresh output and isolated Python.

```bash
"$NATIVE_PYTHON" "$ACTOR_DIR/native_actor_bridge.py" \
  --source-root "$APPWORLD_SOURCE" --freeze "$RUN_DIR/freeze.json" --prepare
"$NATIVE_PYTHON" "$ACTOR_DIR/native_actor_bridge.py" \
  --source-root "$APPWORLD_SOURCE" --freeze "$RUN_DIR/freeze.json" \
  --index 0 --mailbox "$RUN_DIR/mailbox_0" \
  --private-root "$RUN_DIR/private" --summary "$RUN_DIR/task_0_summary.json"
```

The second command serves one actor until `finish`. In a separate process, the
actor requests its initial input, then submits its own code and finally terminates:

```bash
"$NATIVE_PYTHON" "$ACTOR_DIR/actor_client.py" --mailbox "$RUN_DIR/mailbox_0" <<'JSON'
{"op":"start"}
JSON
"$NATIVE_PYTHON" "$ACTOR_DIR/actor_client.py" --mailbox "$RUN_DIR/mailbox_0" <<'JSON'
{"op":"execute","code":"print(apis.api_docs.show_app_descriptions())"}
JSON
"$NATIVE_PYTHON" "$ACTOR_DIR/actor_client.py" --mailbox "$RUN_DIR/mailbox_0" <<'JSON'
{"op":"finish","reason":"actor_declared_finished"}
JSON
```

The example is an interface demonstration, not a task solver. Indices 1 and 2 use
separate worlds and mailboxes. The controller closes the actor endpoint before
calling the unchanged native evaluator once. Scores never return to actors.

After all three actors terminate, the exporter audits hashes/counters, creates
the author encrypted bundle and verifies restored event hashes. Run it only in a
clean export directory: the original packer matches directory-name substrings,
so stale verification/old archive folders can be included on repeated exports.

```bash
"$NATIVE_PYTHON" "$ACTOR_DIR/export_results.py" \
  --source-root "$APPWORLD_SOURCE" --private-root "$RUN_DIR/private" \
  --result-root "$RUN_DIR"
```

## Existing archive verification

The archive is retained locally, not committed. If separately authorized access
to that file is available, decode it to a private local file:

```bash
python - "$ACTOR_DIR/protected_traces.bundle.b64" "$RUN_DIR/traces.bundle" <<'PY'
import base64, hashlib, pathlib, sys
data = base64.b64decode(pathlib.Path(sys.argv[1]).read_text(), validate=False)
assert hashlib.sha256(data).hexdigest() == "1b771472153082345a6f9e41639ffa75b5a0abf14d35d8024e745ca244ae2044"
pathlib.Path(sys.argv[2]).write_bytes(data)
PY
```

Use the pinned author's `appworld.common.utils.unpack_bundle` and its
`appworld.common.constants.PASSWORD/SALT` in the isolated environment to unpack
into a private directory. Retain the included license/additional requirements;
do not publicly redistribute decrypted benchmark derivatives. The three restored
`subagent_private/events_{0,1,2}.jsonl` SHA256 values must match their public
summaries. These were checked after the executed export.
