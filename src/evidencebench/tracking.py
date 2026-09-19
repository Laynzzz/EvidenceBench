"""Portable, immutable run records; model experiments may additionally log to MLflow."""

import importlib.metadata
import platform
import subprocess
import time
import zipfile
from contextlib import contextmanager
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
    source_files = [
        p
        for base in ("src", "scripts", "configs")
        for p in Path(base).rglob("*")
        if p.is_file() and p.suffix in {".py", ".yaml"}
    ]
    source_files += [Path(p) for p in ("pyproject.toml", "uv.lock") if Path(p).exists()]
    with zipfile.ZipFile(path / "source.zip", "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for source in sorted(source_files):
            archive.write(source, source.as_posix())
    manifest["source_archive_hash"] = digest((path / "source.zip").read_bytes())
    return path, manifest


def log_mlflow(run: Path, config: dict[str, Any], metrics: dict[str, Any]) -> str:
    import mlflow

    # Explicit local URI prevents ambient settings from contacting a remote tracker.
    mlflow.set_tracking_uri("sqlite:///mlflow.db")
    mlflow.set_experiment("evidencebench-local")
    with mlflow.start_run(run_name=run.name) as active:
        mlflow.log_params(
            {k: v for k, v in config.items() if isinstance(v, str | int | float | bool)}
        )
        mlflow.log_metrics({k: float(v) for k, v in metrics.items() if isinstance(v, int | float)})
        mlflow.log_artifacts(str(run), artifact_path="exported-run")
        return active.info.run_id


@contextmanager
def run_lifecycle(run: Path, manifest: dict, max_seconds: float):
    """Record all stage failures and cooperatively enforce elapsed time, including setup."""
    started = time.perf_counter()

    def check_deadline():
        if time.perf_counter() - started > max_seconds:
            raise TimeoutError("cooperative run time bound exceeded")

    manifest["status"] = "running"
    (run / "manifest.json").write_bytes(canonical(manifest))
    try:
        yield check_deadline
        check_deadline()
    except BaseException as exc:
        manifest.update(status="failed", error=type(exc).__name__)
        raise
    finally:
        manifest["total_elapsed_seconds"] = time.perf_counter() - started
        (run / "manifest.json").write_bytes(canonical(manifest))
