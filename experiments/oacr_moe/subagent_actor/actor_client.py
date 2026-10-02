#!/usr/bin/env python3
"""Send one JSON request on stdin via a native actor's local file mailbox."""
import argparse
import json
from pathlib import Path
import sys
import time
import uuid


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mailbox", type=Path, required=True)
    args = parser.parse_args()
    payload = json.loads(sys.stdin.read())
    request_id = uuid.uuid4().hex
    temp = args.mailbox/(request_id+".tmp")
    request_path = args.mailbox/(request_id+".request.json")
    response_path = args.mailbox/(request_id+".response.json")
    temp.write_text(json.dumps(payload))
    temp.rename(request_path)
    deadline = time.monotonic()+60
    while not response_path.exists():
        if time.monotonic() > deadline:
            raise TimeoutError("Native bridge response timeout")
        time.sleep(0.05)
    response = json.loads(response_path.read_text())
    response_path.unlink()
    print(json.dumps(response, ensure_ascii=False, indent=2))
    return 0 if response.get("status") != "bridge_error" else 1


if __name__ == "__main__":
    raise SystemExit(main())
