"""CPU orchestration of one explicitly approved, isolated GPU support-filter run."""

import argparse
import importlib.util
import json
import math
import os
import subprocess
import time
from pathlib import Path
from uuid import uuid4

ROOT = Path("artifacts/gpu-support-v1")
GPU_PYTHON = Path("artifacts/gpu-support-env/Scripts/python.exe")
WORKER = Path("scripts/gpu_support_worker.py")
ASSETS = Path("reports/gpu-support-assets.json")
PROPOSAL = Path("docs/gpu-support-proposal.md")
APPROVAL = Path("reports/gpu-support-authorization.json")
LOCK = Path("configs/gpu-support-requirements.lock")


def base_module():
    spec = importlib.util.spec_from_file_location(
        "cpu_support_base", "scripts/run_support_filter.py"
    )
    base = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(base)
    return base


def worker_module():
    spec = importlib.util.spec_from_file_location("gpu_worker", WORKER)
    worker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(worker)
    return worker


def preflight():
    base, worker = base_module(), worker_module()
    original = base.preflight()
    base.verify(base.ROOT, original)
    assets = base.read(ASSETS)
    worker.verify_model_files(assets)
    runtime = json.loads(
        subprocess.check_output(
            [str(GPU_PYTHON), str(WORKER), "--inspect"],
            text=True,
            encoding="utf-8",
            timeout=60,
            env={**os.environ, "HF_HUB_OFFLINE": "1", "TRANSFORMERS_OFFLINE": "1"},
        )
    )
    if runtime != assets["runtime"] or runtime["torch"] != "2.10.0+cu128":
        raise ValueError("isolated CUDA runtime changed")
    rows = base.original_rows()["constrained"]
    payloads = [
        {"query_id": r["query_id"], "input": base.checker_input(r)}
        for r in rows
        if r["status"] == "answered"
    ]
    worker.validate_payloads(payloads, 28)
    sources = [
        Path(__file__).relative_to(Path.cwd()),
        WORKER,
        PROPOSAL,
        ASSETS,
        LOCK,
        Path("scripts/run_support_filter.py"),
    ]
    snapshot = {
        "scope": "gpu-support-v1",
        "model_id": "Qwen/Qwen2.5-7B-Instruct",
        "revision": "a09a35458c702b33eeacc393d103063234e8bc28",
        "model_dir": assets["model_dir"],
        "model_sha256": assets["model_sha256"],
        "runtime": runtime,
        "system_prompt": base.SYSTEM,
        "base_snapshot_sha256": base.digest(base.canonical(original)),
        "inputs_sha256": base.digest(base.canonical(payloads)),
        "limits": {"calls": 28, "reserved_tokens": 224, "max_new_tokens": 8},
        "deadline_seconds": 1200,
        "device": "cuda:0",
        "dtype": "bfloat16",
        "source_sha256": {p.as_posix(): worker.sha(p) for p in sources},
    }
    return snapshot, payloads


def approval(snapshot, path=APPROVAL):
    base = base_module()
    record = base.read(path)
    if (
        record.get("status") != "approved"
        or record.get("scope") != "gpu-support-v1"
        or record.get("snapshot_sha256") != base.digest(base.canonical(snapshot))
    ):
        raise ValueError("new exact-snapshot GPU approval required")
    return record


def merge(original, decisions):
    base = base_module()
    expected = [r["query_id"] for r in original if r["status"] == "answered"]
    if [d["query_id"] for d in decisions] != expected:
        raise ValueError("exact checked query roster/order required")
    lookup = {d["query_id"]: d for d in decisions}
    output = []
    for row in original:
        if row["status"] != "answered":
            decision = {
                "verdict": "NOT_APPLICABLE",
                "reason": None,
                "raw": "",
                "output_tokens": 0,
                "generation_calls": 0,
                "elapsed_ms": 0.0,
                "input_sha256": None,
            }
        else:
            decision = {k: v for k, v in lookup[row["query_id"]].items() if k != "query_id"}
            if set(decision) != {
                "verdict",
                "reason",
                "raw",
                "output_tokens",
                "generation_calls",
                "elapsed_ms",
                "input_sha256",
            }:
                raise ValueError("invalid decision fields")
            if (
                decision["input_sha256"] != base.digest(base.canonical(base.checker_input(row)))
                or decision["generation_calls"] not in (0, 1)
                or not isinstance(decision["output_tokens"], int)
                or not 0 <= decision["output_tokens"] <= 8
                or not math.isfinite(decision["elapsed_ms"])
                or decision["elapsed_ms"] < 0
            ):
                raise ValueError("invalid decision trace")
            if decision["verdict"] in {"SUPPORTED", "UNSUPPORTED"} and (
                decision["raw"] != decision["verdict"]
                or decision["generation_calls"] != 1
                or decision["output_tokens"] == 0
                or decision["elapsed_ms"] > 20000
                or decision["reason"]
                != ("unsupported" if decision["verdict"] == "UNSUPPORTED" else None)
            ):
                raise ValueError("invalid successful checker decision")
            if not decision["generation_calls"] and decision["output_tokens"]:
                raise ValueError("tokens without a call")
        output.append(base.transform(row, decision))
    return output


def supervise(root, run, token, seconds):
    base = base_module()
    started = time.monotonic()
    process, reason, code = None, "spawn_failure", 1
    try:
        process = subprocess.Popen(
            [str(GPU_PYTHON), str(WORKER), "--run", str(run), "--token", token],
            env={**os.environ, "HF_HUB_OFFLINE": "1", "TRANSFORMERS_OFFLINE": "1"},
        )
        code = process.wait(timeout=max(0, seconds - (time.monotonic() - started)))
        reason = "process_exit"
    except (subprocess.TimeoutExpired, KeyboardInterrupt) as exc:
        reason = "timeout" if isinstance(exc, subprocess.TimeoutExpired) else "interrupted"
        if process is not None:
            process.kill()
            process.wait()
        code = 124 if reason == "timeout" else 130
    finally:
        (root / "termination.json").write_bytes(
            base.canonical(
                {"reason": reason, "exit_code": code, "elapsed_seconds": time.monotonic() - started}
            )
        )
    return code


def worker_outputs(root, run, snapshot):
    base, worker = base_module(), worker_module()
    attempt, termination = base.read(root / "attempt.json"), base.read(root / "termination.json")
    h = base.digest(base.canonical(snapshot))
    if (
        attempt["snapshot_sha256"] != h
        or (root / "worker.started").read_text() != attempt["token"]
        or termination["reason"] != "process_exit"
        or termination["exit_code"] != 0
        or not 0 <= termination["elapsed_seconds"] <= snapshot["deadline_seconds"]
    ):
        raise ValueError("GPU supervisor did not complete successfully")
    approval(snapshot, root / "authorization.json")
    if (
        base.read(run / "config.json") != snapshot
        or worker.sha(run / "inputs.json") != snapshot["inputs_sha256"]
    ):
        raise ValueError("input/config mismatch")
    complete = base.read(run / "worker-complete.json")
    if complete["status"] != "complete" or complete["snapshot_sha256"] != h:
        raise ValueError("worker completion mismatch")
    for name in ("decisions.jsonl", "usage.json"):
        if worker.sha(run / name) != complete["files"][name]:
            raise ValueError("worker output checksum mismatch")
    decisions = [
        json.loads(line) for line in (run / "decisions.jsonl").read_text("utf-8").splitlines()
    ]
    current_base = base.preflight()
    if base.digest(base.canonical(current_base)) != snapshot["base_snapshot_sha256"]:
        raise ValueError("CPU base snapshot changed before scoring")
    base.verify(base.ROOT, current_base)
    source = base.original_rows()
    filtered = merge(source["constrained"], decisions)
    calls = sum(d["generation_calls"] for d in decisions)
    if (
        base.read(run / "usage.json")
        != {"calls": calls, "reserved_tokens": 8 * calls, "call_limit": 28}
        or calls > 28
    ):
        raise ValueError("GPU usage mismatch")
    return filtered, base.summarize(source["control"], source["constrained"], filtered)


def launch(snapshot, payloads, root=ROOT):
    base = base_module()
    record = approval(snapshot)
    root.mkdir(parents=True, exist_ok=False)
    token = uuid4().hex
    (root / "attempt.json").write_bytes(
        base.canonical(
            {
                "token": token,
                "snapshot_sha256": base.digest(base.canonical(snapshot)),
                "consumes_single_attempt": True,
            }
        )
    )
    (root / "authorization.json").write_bytes(base.canonical(record))
    run, manifest = base.create_run(root / "runs", snapshot)
    (run / "inputs.json").write_bytes(base.canonical(payloads))
    with base.run_lifecycle(run, manifest, 1200):
        code = supervise(root, run, token, 1200)
        if code:
            raise RuntimeError(f"GPU worker exited with code {code}; attempt consumed")
        filtered, metrics = worker_outputs(root, run, snapshot)
        (run / "predictions.jsonl").write_bytes(
            b"\n".join(base.canonical(r) for r in filtered) + b"\n"
        )
        (run / "metrics.json").write_bytes(base.canonical(metrics))
        manifest.update(
            status="complete",
            files={
                name: base.digest((run / name).read_bytes())
                for name in (
                    "predictions.jsonl",
                    "metrics.json",
                    "inputs.json",
                    "worker-complete.json",
                    "decisions.jsonl",
                    "usage.json",
                )
            },
        )
    return verify(root, snapshot)


def verify(root, snapshot):
    base, worker = base_module(), worker_module()
    for name, h in snapshot["source_sha256"].items():
        if worker.sha(Path(name)) != h:
            raise ValueError("approved GPU source changed")
    runs = list((root / "runs").iterdir())
    if len(runs) != 1:
        raise ValueError("exactly one GPU run required")
    run = runs[0]
    manifest = base.read(run / "manifest.json")
    if (
        manifest["status"] != "complete"
        or manifest["config"] != snapshot
        or manifest["config_hash"] != base.digest(base.canonical(snapshot))
        or manifest["source_archive_hash"] != worker.sha(run / "source.zip")
    ):
        raise ValueError("GPU run/source snapshot mismatch")
    for name in (
        "predictions.jsonl",
        "metrics.json",
        "inputs.json",
        "worker-complete.json",
        "decisions.jsonl",
        "usage.json",
    ):
        if worker.sha(run / name) != manifest["files"][name]:
            raise ValueError("saved checksum mismatch")
    filtered, metrics = worker_outputs(root, run, snapshot)
    predictions = [
        json.loads(line) for line in (run / "predictions.jsonl").read_text("utf-8").splitlines()
    ]
    if filtered != predictions or base.read(run / "metrics.json") != metrics:
        raise ValueError("GPU report recalculation mismatch")
    return {
        "status": "verified",
        "run": run.as_posix(),
        "metrics": metrics,
        "usage": base.read(run / "usage.json"),
        "supervisor": base.read(root / "termination.json"),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--run-approved", action="store_true")
    mode.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    snapshot, payloads = preflight()
    if args.run_approved:
        print(json.dumps(launch(snapshot, payloads)))
    elif args.verify:
        print(json.dumps(verify(ROOT, snapshot)))
    else:
        base = base_module()
        print(
            json.dumps(
                {
                    "status": "ready_for_authorization",
                    "snapshot_sha256": base.digest(base.canonical(snapshot)),
                    "checks": len(payloads),
                    "limits": snapshot["limits"],
                    "deadline_seconds": 1200,
                    "attempt_exists": ROOT.exists(),
                    "model_calls": 0,
                }
            )
        )


if __name__ == "__main__":
    main()
