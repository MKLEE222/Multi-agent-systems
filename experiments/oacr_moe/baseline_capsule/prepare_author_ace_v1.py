#!/usr/bin/env python3
"""Download a small pinned ACE source subset for preflight, never model or data assets.

For full native AppWorld installation, use the author's complete git/LFS checkout.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import urllib.request
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dest", type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads(Path(__file__).with_name("author_ace_manifest_v1.json").read_text())
    args.dest.mkdir(parents=True, exist_ok=True)
    downloaded = reused = 0
    for item in manifest["files"]:
        target = args.dest / item["path"]
        def matches(data):
            return (len(data) == item["size"] and
                hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest() == item["git_blob_sha"])
        if target.exists() and matches(target.read_bytes()):
            reused += 1
            continue
        url = (f"https://raw.githubusercontent.com/{manifest['source_repository']}/"
               f"{manifest['source_ref']}/{item['path']}")
        try:
            with urllib.request.urlopen(url, timeout=30) as response:
                data = response.read(item["size"] + 1)
        except Exception as exc:
            print(json.dumps({"status": "download_blocked", "path": item["path"],
                              "class": type(exc).__name__}))
            return 1
        if not matches(data):
            print(json.dumps({"status": "hash_mismatch", "path": item["path"]}))
            return 1
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        downloaded += 1
    print(json.dumps({"status": "exact_pinned_subset_ready", "downloaded": downloaded,
                      "reused": reused, "model_bytes_downloaded": 0, "task_data_read": False}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
