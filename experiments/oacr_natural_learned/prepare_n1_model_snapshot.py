"""Stage the inherited N1 checkpoint for offline legacy Transformers loading.

No benchmark inputs are accepted. The immutable revision was observed in the
failed run 36818820271; this changes transport, not the model or editor.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

MODEL_ID = "google/t5-small-ssm-nq"
MODEL_REVISION = "4371c64b6f65176f6663af43066bd094597b1116"
MODEL_FILES = (
    "config.json", "pytorch_model.bin", "spiece.model",
    "special_tokens_map.json", "tokenizer_config.json", "generation_config.json",
)


def file_digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_snapshot(directory: Path, provenance: dict) -> dict:
    if provenance.get("model_id") != MODEL_ID or provenance.get("revision") != MODEL_REVISION:
        raise ValueError("snapshot identity differs from the inherited N1 checkpoint")
    recorded = provenance.get("files", {})
    for name in MODEL_FILES:
        path = directory / name
        if not path.is_file() or path.stat().st_size == 0:
            raise ValueError(f"missing or empty checkpoint file: {name}")
        if recorded.get(name) != file_digest(path):
            raise ValueError(f"checkpoint digest mismatch: {name}")
    config = json.loads((directory / "config.json").read_text(encoding="utf-8"))
    if config.get("model_type") != "t5":
        raise ValueError("checkpoint is not the registered T5 model")
    return provenance


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", required=True, type=Path)
    args = parser.parse_args()
    from huggingface_hub import snapshot_download

    directory = args.out_dir.resolve()
    snapshot_download(
        repo_id=MODEL_ID, revision=MODEL_REVISION,
        allow_patterns=list(MODEL_FILES), local_dir=str(directory),
    )
    provenance = {
        "model_id": MODEL_ID, "revision": MODEL_REVISION,
        "files": {name: file_digest(directory / name) for name in MODEL_FILES},
        "revision_source": "GitHub Actions run 36818820271 model-resolution traceback",
    }
    validate_snapshot(directory, provenance)
    (directory / "oacr_snapshot_provenance.json").write_text(
        json.dumps(provenance, indent=2, sort_keys=True) + "\n", encoding="utf-8",
    )
    print(json.dumps(provenance, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
