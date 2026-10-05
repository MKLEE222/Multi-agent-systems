#!/usr/bin/env python3
"""Send one JSON start/execute/receipt_page/finish request to a native mailbox.

The 60-second wait is transport-only. The bridge owns the independent 1200-second
actor deadline, which starts at the first start request and never resets.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
import time
import uuid


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mailbox", type=Path, required=True)
    parser.add_argument("--communication-timeout", type=float, default=60.0)
    args = parser.parse_args()
    if args.communication_timeout <= 0:
        parser.error("communication timeout must be positive")
    payload = json.loads(sys.stdin.read())
    if not isinstance(payload, dict) or payload.get("op") not in {"start", "execute", "receipt_page", "finish"}:
        parser.error("stdin must be a JSON object with start, execute, receipt_page or finish op")
    if not args.mailbox.is_dir():
        print(json.dumps({"status": "bridge_error", "error_class": "MailboxNotReady"}))
        return 1
    if (args.mailbox / "terminated.txt").exists():
        print(json.dumps({"status": "actor_terminated", "grading_feedback": "withheld"}))
        return 0
    request_id = uuid.uuid4().hex
    temporary = args.mailbox / (request_id + ".tmp")
    request_path = args.mailbox / (request_id + ".request.json")
    response_path = args.mailbox / (request_id + ".response.json")
    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "w") as stream:
        stream.write(json.dumps(payload, ensure_ascii=False))
        stream.flush()
        os.fsync(stream.fileno())
    temporary.rename(request_path)
    deadline = time.monotonic() + args.communication_timeout
    while not response_path.exists():
        if (args.mailbox / "terminated.txt").exists():
            # Retain the request as private evidence. A deadline/termination is
            # never permission to reissue an execute request or restart a world.
            print(json.dumps({"status": "actor_terminated", "grading_feedback": "withheld"}))
            return 0
        if time.monotonic() >= deadline:
            print(json.dumps({"status": "bridge_error", "error_class": "CommunicationTimeout",
                              "retry_authorized": False}))
            return 1
        time.sleep(0.05)
    response = json.loads(response_path.read_text())
    response_path.unlink()
    print(json.dumps(response, ensure_ascii=False, indent=2))
    return 1 if response.get("status") == "bridge_error" else 0


if __name__ == "__main__":
    raise SystemExit(main())
