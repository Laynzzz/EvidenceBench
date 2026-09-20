"""Fixed-input GPU generator comparison; default mode is read-only preflight."""

import argparse
import copy
import importlib.util
import json
import math
from pathlib import Path
from uuid import uuid4

from evidencebench.generation_selection import is_boolean
from evidencebench.generation_spans import BOOLEAN_SYSTEM, SYSTEM, build_spans, resolve_span
from evidencebench.ingestion import canonical, digest

ROOT = Path("artifacts/gpu-generation-v1")
APPROVAL = Path("reports/gpu-generation-authorization.json")
PROPOSAL = Path("docs/gpu-generation-proposal.md")
WORKER = Path("scripts/gpu_generation_worker.py")


def module(name):
    path = Path("scripts") / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def read(path):
    return json.loads(path.read_text("utf-8"))


def payloads_for(rows):
    if len({r["query_id"] for r in rows}) != len(rows):
        raise ValueError("unique queries required")
    payloads = []
    for row in rows:
        packed = row["trace"]["packed_evidence"]
        ids = row["trace"]["packed_ids"]
        if set(packed) != {f"E{i}" for i in range(1, len(ids) + 1)} or len(set(ids)) != len(ids):
            raise ValueError("invalid packed evidence")
        if not packed:
            if row["status"] != "refused":
                raise ValueError("empty evidence must remain a refusal")
            continue
        boolean = is_boolean(row["question"])
        choices = ["UNKNOWN"] + (
            [f"{answer} | {alias}" for answer in ("Yes", "No") for alias in packed]
            if boolean
            else list(build_spans(packed))
        )
        evidence = "\n\n".join(f"[{key}] {text}" for key, text in packed.items())
        payloads.append(
            {
                "query_id": row["query_id"],
                "choices": choices,
                "system_prompt": BOOLEAN_SYSTEM if boolean else SYSTEM,
                "user_prompt": (
                    f"Question: {row['question']}\n\nEvidence:\n{evidence}\n\nShort answer:"
                ),
            }
        )
    return payloads


def preflight():
    prior = module("run_gpu_support_filter")
    old, _ = prior.preflight()
    prior.verify(prior.ROOT, old)
    base = prior.base_module()
    rows = base.original_rows()["constrained"]
    payloads = payloads_for(rows)
    module("gpu_generation_worker").validate(payloads, 32)
    sources = dict(old["source_sha256"])
    for path in (
        Path(__file__).relative_to(Path.cwd()),
        WORKER,
        PROPOSAL,
        Path("scripts/run_gpu_support_filter.py"),
    ):
        sources[path.as_posix()] = digest(path.read_bytes())
    snapshot = {
        k: old[k]
        for k in (
            "model_id",
            "revision",
            "model_dir",
            "model_sha256",
            "runtime",
            "base_snapshot_sha256",
            "device",
            "dtype",
        )
    }
    snapshot.update(
        scope="gpu-generation-v1",
        prior_gpu_snapshot_sha256=digest(canonical(old)),
        inputs_sha256=digest(canonical(payloads)),
        source_sha256=sources,
        deadline_seconds=1200,
        limits={"calls": 32, "max_new_tokens": 64, "reserved_tokens": 2048},
        protocol=(
            "same constrained span prompt, choices, 15 words, "
            "1536 input tokens, 20 seconds per query"
        ),
        gate="previous seven conditions plus F1 strictly exceeds saved constrained baseline",
    )
    return snapshot, payloads


def approval(snapshot, path=APPROVAL):
    record = read(path)
    if (
        record.get("status") != "approved"
        or record.get("scope") != "gpu-generation-v1"
        or record.get("snapshot_sha256") != digest(canonical(snapshot))
    ):
        raise ValueError("new exact-snapshot generation approval required")
    return record


def merge(rows, decisions):
    payloads = payloads_for(rows)
    if [d["query_id"] for d in decisions] != [p["query_id"] for p in payloads]:
        raise ValueError("exact generation decision roster/order required")
    lookup = {d["query_id"]: (d, p) for d, p in zip(decisions, payloads, strict=True)}
    result = []
    for original in rows:
        row = copy.deepcopy(original)
        if row["query_id"] not in lookup:
            result.append(row)
            continue
        d, p = lookup[row["query_id"]]
        if set(d) != {
            "query_id",
            "input_sha256",
            "raw",
            "reason",
            "generation_calls",
            "output_tokens",
            "elapsed_ms",
        }:
            raise ValueError("invalid generation trace fields")
        if (
            d["input_sha256"] != digest(canonical(p))
            or type(d["generation_calls"]) is not int
            or d["generation_calls"] not in (0, 1)
            or type(d["output_tokens"]) is not int
            or not 0 <= d["output_tokens"] <= 64
            or not math.isfinite(d["elapsed_ms"])
            or d["elapsed_ms"] < 0
        ):
            raise ValueError("invalid generation trace")
        if not isinstance(d["raw"], str) or (not d["generation_calls"] and d["output_tokens"]):
            raise ValueError("invalid raw output or usage")
        failure_reason = d["reason"]
        if failure_reason is None:
            if (
                d["raw"] not in p["choices"]
                or d["generation_calls"] != 1
                or not d["output_tokens"]
                or d["elapsed_ms"] > 20000
            ):
                raise ValueError("invalid successful generation")
            packed = row["trace"]["packed_evidence"]
            try:
                parsed = resolve_span(d["raw"], packed, row["question"], build_spans(packed))
            except ValueError as exc:
                failure_reason = "invalid_span_generation"
                row["trace"]["validation_error"] = str(exc)
        if failure_reason is None:
            aliases = {f"E{i}": key for i, key in enumerate(row["trace"]["packed_ids"], 1)}
            row.update(
                answer=parsed["answer"],
                citation_ids=[aliases[k] for k in parsed["evidence_ids"]],
                status="refused" if parsed["refused"] else "answered",
                reason="model_refusal" if parsed["refused"] else None,
                refused=parsed["refused"],
            )
            row.pop("grounding_check", None)
            if "grounding_check" in parsed:
                row["grounding_check"] = parsed["grounding_check"]
        else:
            if not isinstance(failure_reason, str) or not failure_reason:
                raise ValueError("failure reason required")
            row.update(answer="", citation_ids=[], status="failure", reason=failure_reason)
            row.pop("grounding_check", None)
            row.pop("refused", None)
        row.update(
            elapsed_ms=d["elapsed_ms"],
            generation_ms=d["elapsed_ms"],
            retrieval_ms=0,
            attempts=d["generation_calls"],
            output_tokens=d["output_tokens"],
            timing_scope="GPU generation only; historical cached retrieval excluded",
            gpu_generation=copy.deepcopy(d),
        )
        row["trace"]["raw_generation"] = d["raw"]
        result.append(row)
    return result


def score(base, source, candidate):
    old = base.summarize(source["control"], source["constrained"], candidate)
    old["baseline"] = old.pop("unfiltered")
    old["candidate"] = old.pop("filtered")
    old["gate"]["no_new_generation_failures"] = old["gate"].pop("no_new_checker_failures")
    old["gate"]["f1_exceeds_constrained_baseline"] = (
        old["candidate"]["answerable_token_f1"] > old["baseline"]["answerable_token_f1"]
    )
    old["passes_development_gate"] = all(old["gate"].values())
    return old


def outputs(root, run, snapshot):
    prior = module("run_gpu_support_filter")
    base = prior.base_module()
    for name, h in snapshot["source_sha256"].items():
        if digest(Path(name).read_bytes()) != h:
            raise ValueError("approved source changed")
    approval(snapshot, root / "authorization.json")
    attempt, termination = read(root / "attempt.json"), read(root / "termination.json")
    h = digest(canonical(snapshot))
    if (
        attempt["snapshot_sha256"] != h
        or (root / "worker.started").read_text("utf-8") != attempt["token"]
        or termination["exit_code"] != 0
        or termination["reason"] != "process_exit"
        or not 0 <= termination["elapsed_seconds"] <= 1200
    ):
        raise ValueError("generation supervisor failed")
    if (
        read(run / "config.json") != snapshot
        or digest((run / "inputs.json").read_bytes()) != snapshot["inputs_sha256"]
    ):
        raise ValueError("config/input changed")
    complete = read(run / "worker-complete.json")
    if complete["status"] != "complete" or complete["snapshot_sha256"] != h:
        raise ValueError("worker not complete")
    for name in ("decisions.jsonl", "usage.json"):
        if digest((run / name).read_bytes()) != complete["files"][name]:
            raise ValueError("worker checksum mismatch")
    current = base.preflight()
    if digest(canonical(current)) != snapshot["base_snapshot_sha256"]:
        raise ValueError("scoring inputs changed")
    base.verify(base.ROOT, current)
    source = base.original_rows()
    decisions = [
        json.loads(line) for line in (run / "decisions.jsonl").read_text("utf-8").splitlines()
    ]
    candidate = merge(source["constrained"], decisions)
    calls = sum(d["generation_calls"] for d in decisions)
    if calls > 32 or read(run / "usage.json") != {
        "calls": calls,
        "reserved_tokens": 64 * calls,
        "call_limit": 32,
    }:
        raise ValueError("generation budget mismatch")
    return candidate, score(base, source, candidate)


def verify(root, snapshot):
    runs = list((root / "runs").iterdir())
    if len(runs) != 1:
        raise ValueError("exactly one generation run required")
    run = runs[0]
    manifest = read(run / "manifest.json")
    if (
        manifest["status"] != "complete"
        or manifest["config"] != snapshot
        or manifest["config_hash"] != digest(canonical(snapshot))
        or manifest["source_archive_hash"] != digest((run / "source.zip").read_bytes())
    ):
        raise ValueError("generation manifest/source mismatch")
    for name in (
        "predictions.jsonl",
        "metrics.json",
        "inputs.json",
        "worker-complete.json",
        "decisions.jsonl",
        "usage.json",
    ):
        if digest((run / name).read_bytes()) != manifest["files"][name]:
            raise ValueError("output checksum mismatch")
    predictions, metrics = outputs(root, run, snapshot)
    if [
        json.loads(line) for line in (run / "predictions.jsonl").read_text("utf-8").splitlines()
    ] != predictions or read(run / "metrics.json") != metrics:
        raise ValueError("recomputed outputs differ")
    return {
        "status": "verified",
        "run": run.as_posix(),
        "metrics": metrics,
        "usage": read(run / "usage.json"),
        "supervisor": read(root / "termination.json"),
    }


def supervise(root, run, token):
    # Reuse the reviewed hard-timeout implementation in an isolated module instance.
    prior = module("run_gpu_support_filter")
    prior.WORKER = WORKER
    return prior.supervise(root, run, token, 1200)


def launch(snapshot, payloads, root=ROOT):
    receipt = approval(snapshot)
    root.mkdir(parents=True, exist_ok=False)
    token = uuid4().hex
    (root / "attempt.json").write_bytes(
        canonical(
            {
                "token": token,
                "snapshot_sha256": digest(canonical(snapshot)),
                "consumes_single_attempt": True,
            }
        )
    )
    (root / "authorization.json").write_bytes(canonical(receipt))
    base = module("run_gpu_support_filter").base_module()
    run, manifest = base.create_run(root / "runs", snapshot)
    (run / "inputs.json").write_bytes(canonical(payloads))
    with base.run_lifecycle(run, manifest, 1200):
        code = supervise(root, run, token)
        if code:
            raise RuntimeError(f"GPU generation exited {code}; attempt consumed")
        predictions, metrics = outputs(root, run, snapshot)
        (run / "predictions.jsonl").write_bytes(
            b"\n".join(canonical(r) for r in predictions) + b"\n"
        )
        (run / "metrics.json").write_bytes(canonical(metrics))
        manifest.update(
            status="complete",
            files={
                name: digest((run / name).read_bytes())
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


def main():
    p = argparse.ArgumentParser(description=__doc__)
    mode = p.add_mutually_exclusive_group()
    mode.add_argument("--run-approved", action="store_true")
    mode.add_argument("--verify", action="store_true")
    args = p.parse_args()
    snapshot, payloads = preflight()
    if args.run_approved:
        result = launch(snapshot, payloads)
    elif args.verify:
        result = verify(ROOT, snapshot)
    else:
        result = {
            "status": "ready_for_authorization",
            "snapshot_sha256": digest(canonical(snapshot)),
            "calls": len(payloads),
            "limits": snapshot["limits"],
            "attempt_exists": ROOT.exists(),
            "model_calls": 0,
        }
    print(json.dumps(result))


if __name__ == "__main__":
    main()
