"""N1 dev-only execution scaffold.

This entrypoint intentionally contains no evaluation-bank loading.
The implementation of the frozen GRACE adaptor constructors is added behind
this interface.
"""

from pathlib import Path
import json


def load_dev_manifest(path: str):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if "evaluation" in data:
        raise RuntimeError("evaluation manifest access forbidden in N1 dev job")
    return data


def main():
    raise RuntimeError(
        "N1 execution scaffold created. Add frozen GRACE dev implementation before model execution."
    )


if __name__ == "__main__":
    main()
