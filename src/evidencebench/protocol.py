"""Verify a frozen data protocol without interpreting held-out label contents."""

import json
from pathlib import Path

from evidencebench.ingestion import digest


def verify_protocol(path: Path) -> dict:
    protocol = json.loads(path.read_text("utf-8"))
    for name, expected in protocol["files"].items():
        if digest(Path(name).read_bytes()) != expected:
            raise ValueError(f"frozen protocol artifact changed: {name}")
    return protocol
