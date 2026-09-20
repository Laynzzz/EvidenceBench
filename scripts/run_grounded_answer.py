"""Complete grounded-answer experiment; default mode is read-only preflight."""

import argparse
import copy
import importlib.util
import json
import math
from pathlib import Path
from uuid import uuid4

from evidencebench.ingestion import canonical, digest

ROOT = Path("artifacts/grounded-answer-v1")
APPROVAL = Path("reports/grounded-answer-authorization.json")
PROPOSAL = Path("docs/grounded-answer-proposal.md")
WORKER = Path("scripts/grounded_answer_worker.py")


def module(name):
    path = Path("scripts") / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def read(path):
    return json.loads(path.read_text("utf-8"))


def payloads_for(rows):
    if len({row["query_id"] for row in rows}) != len(rows):
        raise ValueError("unique queries required")
    payloads = []
    for row in rows:
        packed, ids = row["trace"]["packed_evidence"], row["trace"]["packed_ids"]
        if set(packed) != {f"E{i}" for i in range(1, len(ids) + 1)} or len(set(ids)) != len(ids):
            raise ValueError("invalid packed evidence")
        if not packed:
            if row["status"] != "refused":
                raise ValueError("empty evidence must remain a refusal")
            continue
        payloads.append(
            {
                "query_id": row["query_id"],
                "question": row["question"],
                "evidence": copy.deepcopy(packed),
            }
        )
    module("grounded_answer_contract").validate_payloads(payloads, len(payloads))
    return payloads


def baseline_rows(expected_run):
    run = Path(read(Path("reports/gpu-generation-development.json"))["run"])
    if run.resolve() != Path(expected_run).resolve():
        raise ValueError("baseline report must point to the verified prior run")
    return [
        json.loads(line) for line in (run / "predictions.jsonl").read_text("utf-8").splitlines()
    ]


def preflight():
    previous = module("run_gpu_generation")
    old, _ = previous.preflight()
    verified = previous.verify(previous.ROOT, old)
    rows = baseline_rows(verified["run"])
    if len(rows) != 50 or sum(bool(r["answerable"]) for r in rows) != 38:
        raise ValueError("frozen development cohort changed")
    payloads = payloads_for(rows)
    module("grounded_answer_worker").validate(payloads, 32)
    sources = dict(old["source_sha256"])
    for path in (
        Path(__file__).relative_to(Path.cwd()),
        WORKER,
        PROPOSAL,
        Path("scripts/grounded_answer_contract.py"),
        Path("reports/gpu-generation-development.json"),
        Path("reports/gpu-generation-ai-review.json"),
    ):
        sources[path.as_posix()] = digest(path.read_bytes())
    for path in Path(verified["run"]).iterdir():
        if path.is_file():
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
        scope="grounded-answer-v1",
        baseline_run=verified["run"],
        prior_gpu_snapshot_sha256=digest(canonical(old)),
        inputs_sha256=digest(canonical(payloads)),
        source_sha256=sources,
        deadline_seconds=1200,
        limits={"calls": 32, "max_new_tokens": 384, "reserved_tokens": 12288},
        protocol=(
            "complete answer <=80 words; 1-3 exact body quotes <=120 words total; "
            "2048 input tokens; 30 seconds per query; no retry"
        ),
        gate=(
            "previous eight conditions plus F1/precision/80-percent-answer retention "
            "versus saved 7B"
        ),
    )
    return snapshot, payloads


def approval(snapshot, path=APPROVAL):
    record = read(path)
    if (
        record.get("status") != "approved"
        or record.get("scope") != "grounded-answer-v1"
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
    contract = module("grounded_answer_contract")
    for original in rows:
        row = copy.deepcopy(original)
        if row["query_id"] not in lookup:
            result.append(row)
            continue
        d, payload = lookup[row["query_id"]]
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
            d["input_sha256"] != digest(canonical(payload))
            or type(d["generation_calls"]) is not int
            or d["generation_calls"] not in (0, 1)
            or type(d["output_tokens"]) is not int
            or not 0 <= d["output_tokens"] <= 384
            or type(d["elapsed_ms"]) not in (int, float)
            or not math.isfinite(d["elapsed_ms"])
            or d["elapsed_ms"] < 0
            or not isinstance(d["raw"], str)
            or (not d["generation_calls"] and (d["output_tokens"] or d["raw"]))
        ):
            raise ValueError("invalid generation trace")
        failure_reason = d["reason"]
        for key in (
            "grounding_check",
            "refused",
            "gpu_generation",
            "citation_check",
            "answer_quotes",
        ):
            row.pop(key, None)
        row["trace"].pop("validation_error", None)
        if failure_reason is None:
            if d["generation_calls"] != 1 or not d["output_tokens"] or d["elapsed_ms"] > 30000:
                raise ValueError("invalid successful generation")
            try:
                parsed = contract.parse(d["raw"], payload["evidence"])
            except ValueError as exc:
                failure_reason = "invalid_answer_contract"
                row["trace"]["validation_error"] = str(exc)
        if failure_reason is None:
            ids = row["trace"]["packed_ids"]
            row.update(
                answer=parsed["answer"],
                citation_ids=[ids[int(k[1:]) - 1] for k in parsed["evidence_ids"]],
                status="refused" if parsed["refused"] else "answered",
                reason="model_refusal" if parsed["refused"] else None,
                refused=parsed["refused"],
                citation_check=parsed["citation_check"],
                answer_quotes=parsed["citations"],
            )
        else:
            if not isinstance(failure_reason, str) or not failure_reason:
                raise ValueError("failure reason required")
            row.update(answer="", citation_ids=[], status="failure", reason=failure_reason)
        row.update(
            elapsed_ms=d["elapsed_ms"],
            generation_ms=d["elapsed_ms"],
            retrieval_ms=0,
            attempts=d["generation_calls"],
            output_tokens=d["output_tokens"],
            timing_scope="GPU generation only; historical cached retrieval excluded",
            grounded_generation=copy.deepcopy(d),
        )
        row["trace"]["raw_generation"] = d["raw"]
        result.append(row)
    return result


def score(base, source, candidate, previous):
    if [r["query_id"] for r in candidate] != [r["query_id"] for r in previous]:
        raise ValueError("comparison roster/order differs")
    result = module("run_gpu_generation").score(base, source, candidate)
    previous_score = module("run_gpu_generation").score(base, source, previous)["candidate"]
    current = result["candidate"]
    result["saved_7b_baseline"] = previous_score
    result["gate"].update(
        f1_exceeds_saved_7b=current["answerable_token_f1"] > previous_score["answerable_token_f1"],
        citation_precision_not_lower_than_saved_7b=(
            current["upstream_citation_precision"] is not None
            and previous_score["upstream_citation_precision"] is not None
            and current["upstream_citation_precision"]
            >= previous_score["upstream_citation_precision"]
        ),
        retain_80_percent_saved_7b_answers=current["answered_count"]
        >= math.ceil(0.8 * previous_score["answered_count"]),
    )
    result["passes_development_gate"] = all(result["gate"].values())
    return result


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
    previous = baseline_rows(snapshot["baseline_run"])
    candidate = merge(previous, decisions)
    calls = sum(d["generation_calls"] for d in decisions)
    if calls > 32 or read(run / "usage.json") != {
        "calls": calls,
        "reserved_tokens": 384 * calls,
        "call_limit": 32,
    }:
        raise ValueError("generation budget mismatch")
    return candidate, score(base, source, candidate, previous)


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
