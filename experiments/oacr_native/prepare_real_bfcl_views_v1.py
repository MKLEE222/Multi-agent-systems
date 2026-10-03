"""Download hash-pinned public author inputs; no credentials or model calls."""
import argparse
import hashlib
import json
import urllib.request
from pathlib import Path


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dest", type=Path, required=True)
    p.add_argument("--config", type=Path,
                   default=Path(__file__).with_name("run_real_bfcl_views_v1.json"))
    args = p.parse_args()
    config = json.loads(args.config.read_text())
    for rel, url in config["source_urls"].items():
        target = args.dest / rel
        expected = config["source_hashes"][rel]
        if target.exists() and hashlib.sha256(target.read_bytes()).hexdigest() == expected:
            continue
        with urllib.request.urlopen(url, timeout=30) as response:
            data = response.read(4_000_001)
        if len(data) > 4_000_000 or hashlib.sha256(data).hexdigest() != expected:
            raise ValueError(f"Unverified source: {rel}")
        target.parent.mkdir(parents=True, exist_ok=True)
        tmp = target.with_suffix(target.suffix + ".download")
        tmp.write_bytes(data)
        tmp.replace(target)
        print(rel)


if __name__ == "__main__":
    main()
