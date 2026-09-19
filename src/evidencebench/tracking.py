"""Portable, immutable run records; model experiments may additionally log to MLflow."""

import importlib.metadata
import platform
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from evidencebench.ingestion import canonical, digest


def environment() -> dict[str, Any]:
    def git(*args: str) -> str:
        result = subprocess.run(["git", *args], capture_output=True, text=True, check=False)
        return result.stdout.strip() if result.returncode == 0 else "unavailable"

    return {
        "code_revision": git("rev-parse", "HEAD"),
        "git_status": git("status", "--porcelain"),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "dependencies": {p.metadata["Name"]: p.version for p in importlib.metadata.distributions()},
    }


def create_run(root: Path, config: dict[str, Any]) -> tuple[Path, dict[str, Any]]:
    run_id = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid4().hex[:10]
    path = root / run_id
    path.mkdir(parents=True, exist_ok=False)
    manifest = {
        "run_id": run_id,
        "started_at": datetime.now(UTC).isoformat(),
        "config_hash": digest(canonical(config)),
        "config": config,
        **environment(),
    }
    (path / "config.json").write_bytes(canonical(config))
    return path, manifest
