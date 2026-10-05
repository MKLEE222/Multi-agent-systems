# Native cache response mechanism preflight

These are development interventions on an unmodified pinned MobiEdit model
component, not a reproduction of the full editor, optimizer, quantizer, factual
editing benchmark, or mobile measurements. No sealed evaluation manifest is read.
See the [executed verdict](../../docs/OACR_CACHE_RESPONSE_MECHANISM_EXPLORATION_2026-10-01.md).

The tiny and pretrained protocol files were saved before their respective runs.
The pretrained probes followed the tiny results. The rounding control was
specified after seeing pretrained numerical discrepancies and uses the same
probes; it is a retrospective diagnostic.

## Pinned inputs

- MobiEdit commit: `5a07b7906baa5457c15bd86cc012b1993ef6d3c6`.
- Model source git blob: `defdad8cd04a5366016b5b6185b014af24d1784f`.
- Python 3.12; Torch 2.5.1+cpu; Transformers 4.44.2; NumPy 1.26.4.
- Pretrained model: Qwen/Qwen2.5-0.5B, revision
  `060db6499f32faf8b98477b0a26969ef7d8b9987`.
- Full installed package versions and input/report hashes:
  [manifest](../../results/oacr_cache_zo/manifest.json) and
  [runtime freeze](../../results/oacr_cache_zo/runtime-freeze.txt).

The local dependencies are an explicit fixture environment, not the complete
official MobiEdit requirements. The source loader checks the git blob and runs
the official file under the matching Transformers package so its relative
imports resolve. Eager attention, CPU float32 and deterministic Torch
operations are used. Numeric equality is specific to the recorded environment.

## Reproduce from the repository root

Create a separate environment with the pinned core packages. Retrieve the
official repository with git, then export the source at the specified commit.
The pretrained runner additionally needs the six model/tokenizer files listed
in the report identity; download those at the pinned Hub revision. Model weights
are not vendored here.

```bash
git clone --filter=blob:none --no-checkout https://github.com/UbiquitousLearning/MobiEdit.git /tmp/oacr-mobiedit
git -C /tmp/oacr-mobiedit show 5a07b7906baa5457c15bd86cc012b1993ef6d3c6:server/mobiedit/easyeditor/models/rome/modeling_qwen2.py > /tmp/oacr-modeling-qwen2.py
python experiments/oacr_cache_zo/native_preflight_v1.py --source-file /tmp/oacr-modeling-qwen2.py --out /tmp/oacr-native-report.json
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 python experiments/oacr_cache_zo/pretrained_probe_v1.py --source-file /tmp/oacr-modeling-qwen2.py --model-dir /path/to/pinned-qwen25-05b --out /tmp/oacr-pretrained-report.json
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 python experiments/oacr_cache_zo/rounding_control_v1.py --source-file /tmp/oacr-modeling-qwen2.py --model-dir /path/to/pinned-qwen25-05b --previous-report /tmp/oacr-pretrained-report.json --out /tmp/oacr-rounding-report.json
```

The pretrained report records SHA-256 for all six input files. Match these
against the saved report before interpreting a new run as the same fixture.

## Read the saved evidence

The three `.json.gz` files are lossless, deterministic gzip copies of the
executed reports. The manifest provides raw and compressed hashes. For example:

```bash
python -m gzip -d -c results/oacr_cache_zo/native_preflight_v1.json.gz > /tmp/oacr-saved-native.json
```

The tiny raw report's `outside` and `last_layer` summaries overlap. Use the
manifest's mutually exclusive regions or the complete row records for counts.
Seeds, batch rows, perturbation directions and repeated calls are not independent
natural tasks. Timing includes diagnostic bookkeeping and is not a speed claim.

Verify report bytes, protocol/script identities, the linked numerical diagnostic,
and the mutually exclusive count summary without loading any model:

```bash
python experiments/oacr_cache_zo/verify_saved_evidence.py
```
