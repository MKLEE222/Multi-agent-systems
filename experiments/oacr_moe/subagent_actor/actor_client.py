#!/usr/bin/env python3
"""Send one JSON request on stdin to a native actor's local execution bridge."""
import argparse
import json
import socket
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--socket", required=True)
    args = parser.parse_args()
    payload = json.loads(sys.stdin.read())
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as conn:
        conn.settimeout(60)
        conn.connect(args.socket)
        conn.sendall(json.dumps(payload).encode() + b"\n")
        data = bytearray()
        while not data.endswith(b"\n"):
            part = conn.recv(65536)
            if not part:
                break
            data.extend(part)
    response = json.loads(data)
    print(json.dumps(response, ensure_ascii=False, indent=2))
    return 0 if response.get("status") != "bridge_error" else 1


if __name__ == "__main__":
    raise SystemExit(main())
