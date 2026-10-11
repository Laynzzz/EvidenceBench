"""Prepare, run once, or independently verify the claim-grounded GPU comparison."""

import argparse
import copy
import importlib.util
import json
import math
import os
import subprocess
import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "src"))

import numpy as np  # noqa: E402

from evidencebench.evaluation.answers import answer_metrics, token_f1  # noqa: E402
from evidencebench.evaluation.metrics import paired_family_bootstrap  # noqa: E402
from evidencebench.ingestion import canonical, digest  # noqa: E402
from evidencebench.labels import read_labels  # noqa: E402

ROOT = Path("artifacts/claim-grounded-v1")
ROOT_B = Path("artifacts/claim-grounded-no-cutoff-v1")
APPROVAL = Path("reports/claim-grounded-authorization.json")
APPROVAL_B = Path("reports/claim-grounded-no-cutoff-authorization.json")
READINESS = Path("reports/claim-grounded-readiness.json")
READINESS_B = Path("reports/claim-grounded-no-cutoff-readiness.json")
REPORT_A = Path("reports/claim-grounded-development.json")
REPORT_B = Path("reports/claim-grounded-no-cutoff-development.json")
BASELINE_REPORT = Path("reports/intact-passage-development.json")
PROTOCOL = Path("docs/answer-improvement-cycle4.md")
PROPOSAL = Path("docs/claim-grounded-proposal.md")
REVIEW = Path("reports/claim-grounded-input-review.json")
WORKER = Path("scripts/claim_grounded_worker.py")
GPU_PYTHON = Path("artifacts/gpu-support-env/Scripts/python.exe")
LABELS_PATH = Path("data/labels/qasper-fresh-v1/dev.jsonl")
SOURCE_PATHS = (
    Path("AGENTS.md"),
    Path("plan.md"),
    Path("configs/gpu-support-requirements.lock"),
    LABELS_PATH,
    PROTOCOL,
    PROPOSAL,
    REVIEW,
    Path("reports/intact-passage-development.json"),
    Path("reports/intact-passage-development.md"),
    Path("reports/span-id-answer-development.json"),
    Path("reports/gpu-generation-development.json"),
    Path("scripts/run_claim_grounded.py"),
    Path("scripts/claim_grounded_contract.py"),
    WORKER,
    Path("scripts/span_id_answer_contract.py"),
    Path("scripts/grounded_answer_contract.py"),
    Path("scripts/grounded_answer_worker.py"),
    Path("scripts/gpu_support_worker.py"),
    Path("scripts/run_grounded_answer.py"),
    Path("scripts/run_gpu_support_filter.py"),
    Path("scripts/run_support_filter.py"),
    Path("src/evidencebench/ingestion.py"),
    Path("src/evidencebench/labels.py"),
    Path("src/evidencebench/evaluation/answers.py"),
    Path("src/evidencebench/evaluation/metrics.py"),
    Path("src/evidencebench/tracking.py"),
)


def module(name):
    path = Path("scripts") / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


contract = module("claim_grounded_contract")
worker = module("claim_grounded_worker")
engine = module("run_grounded_answer")
original_engine_module = engine.module


def isolated_module(name):
    if name == "grounded_answer_contract":
        return contract
    if name == "grounded_answer_worker":
        return worker
    return original_engine_module(name)


engine.module = isolated_module
engine.ROOT = ROOT
engine.APPROVAL = APPROVAL
engine.PROPOSAL = PROPOSAL
engine.WORKER = WORKER


def read(path):
    return json.loads(Path(path).read_text("utf-8"))


def read_jsonl(path):
    return [json.loads(line) for line in Path(path).read_text("utf-8").splitlines()]


def payloads_for(rows):
    if len(rows) != 50 or len({row.get("query_id") for row in rows}) != 50:
        raise ValueError("exact 50-question baseline roster required")
    payloads, threshold_refusals = [], []
    for row in rows:
        trace = row.get("trace")
        if not isinstance(trace, dict):
            raise ValueError("baseline trace required")
        evidence, ids = trace.get("packed_evidence"), trace.get("packed_ids")
        if not isinstance(evidence, dict) or not isinstance(ids, list):
            raise ValueError("packed evidence and parent IDs required")
        if evidence:
            if (
                len(ids) != len(evidence)
                or len(set(ids)) != len(ids)
                or set(evidence) != {f"E{i}" for i in range(1, len(ids) + 1)}
            ):
                raise ValueError("invalid packed passage aliases")
            payloads.append(
                {
                    "query_id": row["query_id"],
                    "question": row["question"],
                    "evidence": copy.deepcopy(evidence),
                }
            )
        else:
            if (
                ids
                or row.get("status") != "refused"
                or row.get("reason") != "insufficient_evidence"
                or row.get("answer")
                or row.get("citation_ids")
            ):
                raise ValueError("empty evidence must remain an original threshold refusal")
            threshold_refusals.append(row["query_id"])
    contract.validate_payloads(payloads, contract.CALL_LIMIT)
    if len(threshold_refusals) != 18:
        raise ValueError("all 18 original threshold refusals must be preserved")
    return payloads


def top_three_payloads(rows, units):
    if len(rows) != 50 or len({row.get("query_id") for row in rows}) != 50:
        raise ValueError("exact 50-question baseline roster required")
    payloads = []
    for row in rows:
        ranking = row.get("trace", {}).get("post_ranking")
        if not isinstance(ranking, list) or len(ranking) < 3:
            raise ValueError("saved post-cutoff ranking must contain at least three rows")
        top = ranking[:3]
        ids = [item.get("element_id") for item in top]
        if (
            [item.get("rank") for item in top] != [1, 2, 3]
            or any(not isinstance(element_id, str) for element_id in ids)
            or len(set(ids)) != 3
        ):
            raise ValueError("saved top-three ranking is not stable and unique")
        evidence = {}
        for index, element_id in enumerate(ids, 1):
            unit = units.get(element_id)
            if (
                not isinstance(unit, dict)
                or unit.get("element_id", element_id) != element_id
                or unit.get("split") != "dev"
                or not isinstance(unit.get("text"), str)
                or not unit["text"].strip()
            ):
                raise ValueError("top-three source must be a complete development paragraph")
            evidence[f"E{index}"] = unit["text"]
        payloads.append(
            {"query_id": row["query_id"], "question": row["question"], "evidence": evidence}
        )
    contract.validate_payloads(payloads, 50)
    return payloads


def _check_label_alignment(rows):
    labels = read_labels(LABELS_PATH)
    if len(labels) != 50 or len(rows) != len(labels):
        raise ValueError("frozen development label roster changed")
    labels_by_id = {label.query_id: label for label in labels}
    query_ids = [row.get("query_id") for row in rows]
    if (
        len(labels_by_id) != len(labels)
        or len(set(query_ids)) != len(query_ids)
        or set(query_ids) != set(labels_by_id)
    ):
        raise ValueError("frozen development label roster changed")
    for row in rows:
        label = labels_by_id[row["query_id"]]
        if (
            row["question"] != label.text
            or row["family_id"] != label.family_id
            or row["answerable"] != label.answerable
            or row["answer_criteria"] != label.answer_criteria
            or row["supporting_evidence"] != label.supporting_evidence
        ):
            raise ValueError("saved predictions differ from frozen development labels")
    if sum(bool(row["answerable"]) for row in rows) != 38:
        raise ValueError("development answerability denominator changed")


def load_baseline(baseline_run, verify_files=True):
    run = Path(baseline_run).resolve()
    if not run.is_dir():
        raise FileNotFoundError(
            f"frozen intact-paragraph run is unavailable: {run}; pass --baseline-run"
        )
    report = read(BASELINE_REPORT)
    if report.get("status") != "verified" or Path(report["run"]).name != run.name:
        raise ValueError("current intact-paragraph report must identify the baseline run")
    manifest_path = run / "manifest.json"
    manifest = read(manifest_path)
    config = manifest["config"]
    if (
        manifest.get("status") != "complete"
        or config.get("scope") != "intact-passage-v1"
        or manifest.get("config_hash") != digest(canonical(config))
        or manifest.get("source_archive_hash") != digest((run / "source.zip").read_bytes())
        or report.get("snapshot_sha256") != manifest.get("config_hash")
    ):
        raise ValueError("frozen intact-paragraph run manifest does not verify")
    if verify_files:
        for name, expected_hash in manifest.get("files", {}).items():
            if digest((run / name).read_bytes()) != expected_hash:
                raise ValueError(f"frozen baseline output changed: {name}")
    rows = read_jsonl(run / "predictions.jsonl")
    _check_label_alignment(rows)
    payloads = payloads_for(rows)
    saved_inputs = read(run / "inputs.json")
    if saved_inputs != payloads:
        raise ValueError("latest 32 saved intact-paragraph inputs differ from predictions")
    if read(run / "metrics.json") != report["metrics"]:
        raise ValueError("saved baseline metrics differ from the verified report")
    return {
        "run": run,
        "manifest": manifest,
        "rows": rows,
        "payloads": payloads,
        "report": report,
        "config": config,
    }


def _baseline_file_hashes(source):
    run = source["run"]
    names = ["config.json", "decisions.jsonl", "inputs.json", "manifest.json", "metrics.json"]
    names += ["predictions.jsonl", "source.zip", "usage.json", "worker-complete.json"]
    return {str((run / name).resolve()): digest((run / name).read_bytes()) for name in names}


def _inspect_prompts(payloads, model_dir, gpu_python):
    if not gpu_python.is_file():
        raise FileNotFoundError(f"pinned CUDA Python runtime is unavailable: {gpu_python}")
    with tempfile.TemporaryDirectory(prefix="evidencebench-claim-preflight-") as temp:
        input_path = Path(temp) / "inputs.json"
        input_path.write_bytes(canonical(payloads))
        process = subprocess.run(
            [
                str(gpu_python),
                str(WORKER.resolve()),
                "--inspect",
                "--model-dir",
                str(model_dir),
                "--inputs",
                str(input_path),
            ],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=180,
            env={**os.environ, "HF_HUB_OFFLINE": "1", "TRANSFORMERS_OFFLINE": "1"},
        )
    result = json.loads(process.stdout)
    if len(result["prompt_lengths"]) != len(payloads):
        raise ValueError("tokenizer did not inspect the exact generation roster")
    if any(row["input_tokens"] > contract.MAX_INPUT_TOKENS for row in result["prompt_lengths"]):
        raise ValueError("prompt exceeds 2,048 tokens; do not silently truncate")
    return result


def preflight(baseline_run, gpu_python):
    source = load_baseline(baseline_run)
    prior_config = source["config"]
    payloads = source["payloads"]
    support = worker.support()
    support.verify_model_files(prior_config)
    inspection = _inspect_prompts(payloads, Path(prior_config["model_dir"]), gpu_python)
    if inspection["runtime"] != prior_config["runtime"]:
        raise ValueError("isolated CUDA runtime differs from the pinned prior run")
    sources = {}
    for path in SOURCE_PATHS:
        if not path.is_file():
            raise FileNotFoundError(f"snapshot source is missing: {path}")
        sources[path.as_posix()] = digest(path.read_bytes())
    span_prior = read("reports/span-id-answer-development.json")
    gpu_prior = read("reports/gpu-generation-development.json")
    prompt_lengths = inspection["prompt_lengths"]
    snapshot = {
        "scope": contract.SCOPE,
        "baseline_run": str(source["run"]),
        "baseline_manifest_sha256": digest((source["run"] / "manifest.json").read_bytes()),
        "baseline_source_sha256": _baseline_file_hashes(source),
        "baseline_metrics_sha256": {
            "reports/intact-passage-development.json": sources[
                "reports/intact-passage-development.json"
            ],
            "reports/span-id-answer-development.json": sources[
                "reports/span-id-answer-development.json"
            ],
            "reports/gpu-generation-development.json": sources[
                "reports/gpu-generation-development.json"
            ],
        },
        "cohort": {
            "questions": 50,
            "answerable": 38,
            "unanswerable": 12,
            "generated_inputs": 32,
            "preserved_threshold_refusals": 18,
        },
        "inputs_sha256": digest(canonical(payloads)),
        "messages_sha256": digest(canonical([contract.messages(payload) for payload in payloads])),
        "prompt_lengths": prompt_lengths,
        "model_id": prior_config["model_id"],
        "revision": prior_config["revision"],
        "model_dir": prior_config["model_dir"],
        "model_sha256": prior_config["model_sha256"],
        "runtime": inspection["runtime"],
        "device": "cuda:0",
        "dtype": "bfloat16",
        "limits": contract.LIMITS,
        "allowance": contract.ALLOWANCE,
        "deadline_seconds": 1200,
        "per_query_timeout_seconds": contract.TIMEOUT_SECONDS,
        "max_input_tokens": contract.MAX_INPUT_TOKENS,
        "protocol_sha256": sources[PROTOCOL.as_posix()],
        "selection_rule": (
            "retain all twelve existing gates, including F1 strictly above saved span-ID .214084; "
            "among passing candidates rank F1, citation precision, then fewer calls"
        ),
        "experiment_b_safeguards": {
            "failure_count": 0,
            "unanswerable_answer_count_at_most": 3,
            "citation_precision_at_least": 0.458333,
            "answered_count_at_least": 20,
        },
        "source_sha256": sources,
        "final_test_used": False,
        "training_runs": 0,
        "external_spend_usd": 0,
        "tokenizer_only_preflight": True,
        "gpu_python": str(gpu_python.resolve()),
        "saved_7b_comparison_sha256": gpu_prior["artifact_sha256"],
        "saved_span_id_comparison_sha256": span_prior["artifact_sha256"],
    }
    return snapshot, payloads


def _verified_experiment_a():
    frozen = read(READINESS)
    snapshot = frozen.get("snapshot")
    if frozen.get("scope") != contract.SCOPE or frozen.get("snapshot_sha256") != digest(
        canonical(snapshot)
    ):
        raise ValueError("frozen Experiment A readiness record is required before B")
    result = engine.verify(ROOT, snapshot)
    if not REPORT_A.is_file() or read(REPORT_A) != result:
        raise ValueError("saved Experiment A report differs from independently verified outputs")
    if not eligible_for_experiment_b(result["metrics"]["candidate"]):
        raise ValueError("Experiment A missed a safeguard; Experiment B must be skipped")
    return snapshot, result


def _dev_units(corpus_path):
    import pyarrow.parquet as pq

    rows = pq.read_table(corpus_path, filters=[("split", "=", "dev")]).to_pylist()
    units = {row["element_id"]: row for row in rows}
    if len(units) != len(rows):
        raise ValueError("development paragraph IDs must be unique")
    return units


def preflight_no_cutoff(baseline_run, gpu_python, corpus_path):
    experiment_a_snapshot, experiment_a_result = _verified_experiment_a()
    source = load_baseline(baseline_run)
    corpus_path = Path(corpus_path).resolve()
    if not corpus_path.is_file():
        raise FileNotFoundError(f"cached development paragraph corpus is required: {corpus_path}")
    payloads = top_three_payloads(source["rows"], _dev_units(corpus_path))
    inspection = _inspect_prompts(payloads, Path(source["config"]["model_dir"]), gpu_python)
    if inspection["runtime"] != source["config"]["runtime"]:
        raise ValueError("isolated CUDA runtime differs from the pinned prior run")

    sources = {}
    for path in SOURCE_PATHS:
        if not path.is_file():
            raise FileNotFoundError(f"snapshot source is missing: {path}")
        sources[path.as_posix()] = digest(path.read_bytes())
    for path in (READINESS, REPORT_A):
        sources[path.as_posix()] = digest(path.read_bytes())
    sources[str(corpus_path)] = digest(corpus_path.read_bytes())
    span_prior = read("reports/span-id-answer-development.json")
    gpu_prior = read("reports/gpu-generation-development.json")
    spec = contract.specification(contract.NO_CUTOFF_SCOPE)
    previously_blocked = [row for row in source["rows"] if not row["trace"]["packed_evidence"]]
    if (
        len(previously_blocked) != 18
        or sum(bool(row["answerable"]) for row in previously_blocked) != 12
    ):
        raise ValueError("the saved threshold-blocked 18-question group changed")
    run_a = Path(experiment_a_result["run"])
    if not run_a.is_absolute():
        run_a = Path.cwd() / run_a
    a_manifest = run_a / "manifest.json"
    a_predictions = run_a / "predictions.jsonl"
    snapshot = {
        "scope": contract.NO_CUTOFF_SCOPE,
        "experiment": "B: remove only the numerical relevance-score cutoff",
        "baseline_run": str(source["run"]),
        "baseline_manifest_sha256": digest((source["run"] / "manifest.json").read_bytes()),
        "experiment_a_readiness_sha256": digest(READINESS.read_bytes()),
        "experiment_a_result_sha256": digest(canonical(experiment_a_result)),
        "experiment_a_run_manifest_sha256": digest(a_manifest.read_bytes()),
        "experiment_a_predictions_sha256": digest(a_predictions.read_bytes()),
        "cohort": {
            "questions": 50,
            "answerable": 38,
            "unanswerable": 12,
            "generated_inputs": 50,
            "previously_threshold_blocked": 18,
            "previously_blocked_answerable": 12,
            "previously_blocked_unanswerable": 6,
        },
        "previously_blocked_query_ids": [row["query_id"] for row in previously_blocked],
        "inputs_sha256": digest(canonical(payloads)),
        "messages_sha256": digest(canonical([contract.messages(payload) for payload in payloads])),
        "prompt_lengths": inspection["prompt_lengths"],
        "model_id": source["config"]["model_id"],
        "revision": source["config"]["revision"],
        "model_dir": source["config"]["model_dir"],
        "model_sha256": source["config"]["model_sha256"],
        "runtime": inspection["runtime"],
        "device": "cuda:0",
        "dtype": "bfloat16",
        "limits": spec["limits"],
        "allowance": spec["allowance"],
        "deadline_seconds": spec["deadline_seconds"],
        "per_query_timeout_seconds": contract.TIMEOUT_SECONDS,
        "max_input_tokens": contract.MAX_INPUT_TOKENS,
        "protocol_sha256": sources[PROTOCOL.as_posix()],
        "selection_rule": (
            "retain all twelve existing gates, including F1 strictly above saved span-ID .214084; "
            "among passing candidates rank F1, citation precision, then fewer calls"
        ),
        "source_sha256": sources,
        "baseline_source_sha256": _baseline_file_hashes(source),
        "final_test_used": False,
        "training_runs": 0,
        "external_spend_usd": 0,
        "tokenizer_only_preflight": True,
        "gpu_python": str(Path(gpu_python).resolve()),
        "corpus_path": str(corpus_path),
        "saved_7b_comparison_sha256": gpu_prior["artifact_sha256"],
        "saved_span_id_comparison_sha256": span_prior["artifact_sha256"],
        "experiment_a_safeguards": experiment_a_result["metrics"]["candidate"],
        "experiment_a_snapshot_sha256": digest(canonical(experiment_a_snapshot)),
    }
    return snapshot, payloads


def approval(snapshot, path=None):
    specification = contract.specification(snapshot.get("scope"))
    if path is None:
        path = APPROVAL if snapshot["scope"] == contract.SCOPE else APPROVAL_B
    record = read(path)
    if (
        record.get("status") != "approved"
        or record.get("scope") != snapshot["scope"]
        or record.get("snapshot_sha256") != digest(canonical(snapshot))
        or record.get("limits") != specification["allowance"]
        or not isinstance(record.get("approval_text"), str)
        or not record["approval_text"].strip()
        or not isinstance(record.get("recorded_at_utc"), str)
    ):
        raise ValueError("new exact-snapshot claim-grounded approval required")
    return record


def merge_predictions(rows, decisions, payloads=None, replace_evidence=False):
    payloads = payloads_for(rows) if payloads is None else payloads
    contract.validate_payloads(payloads, len(payloads))
    if [decision.get("query_id") for decision in decisions] != [
        payload["query_id"] for payload in payloads
    ]:
        raise ValueError("generation query roster/order differs from saved inputs")
    payload_by_id = {payload["query_id"]: payload for payload in payloads}
    decision_by_id = {decision["query_id"]: decision for decision in decisions}
    result = []
    for original in rows:
        row = copy.deepcopy(original)
        query_id = row["query_id"]
        if query_id not in payload_by_id:
            result.append(row)
            continue
        decision = decision_by_id[query_id]
        if set(decision) != {
            "query_id",
            "input_sha256",
            "raw",
            "reason",
            "generation_calls",
            "output_tokens",
            "elapsed_ms",
        }:
            raise ValueError("invalid generation decision fields")
        payload = payload_by_id[query_id]
        if replace_evidence:
            top = row["trace"].get("post_ranking", [])[:3]
            row["trace"]["packed_ids"] = [item["element_id"] for item in top]
            row["trace"]["packed_evidence"] = copy.deepcopy(payload["evidence"])
            row["trace"]["claim_grounded_cutoff_removed"] = True
        calls, tokens, elapsed = (
            decision["generation_calls"],
            decision["output_tokens"],
            decision["elapsed_ms"],
        )
        if (
            decision["input_sha256"] != digest(canonical(payload))
            or type(calls) is not int
            or calls not in (0, 1)
            or type(tokens) is not int
            or not 0 <= tokens <= contract.MAX_NEW_TOKENS
            or type(elapsed) not in (int, float)
            or not math.isfinite(elapsed)
            or elapsed < 0
            or not isinstance(decision["raw"], str)
            or (not calls and (tokens or decision["raw"]))
            or (decision["reason"] is not None and not isinstance(decision["reason"], str))
        ):
            raise ValueError("invalid generation usage or input provenance")
        raw, reason = decision["raw"], decision["reason"]
        if calls == 0 and reason is None:
            reason = "no_generation_call"
        elif calls == 1 and elapsed > contract.TIMEOUT_SECONDS * 1000 and reason is None:
            reason = "timeout"
        parsed = None
        if reason is None:
            if calls != 1:
                reason = "no_generation_call"
            else:
                try:
                    parsed = contract.parse(raw, payload["evidence"])
                except ValueError as exc:
                    reason = "invalid_answer_contract"
                    row["trace"]["validation_error"] = str(exc)
        for key in ("grounding_check", "gpu_generation", "citation_check", "answer_quotes"):
            row.pop(key, None)
        if reason is None and parsed is not None:
            parent_ids = row["trace"]["packed_ids"]
            row.update(
                answer=parsed["answer"],
                citation_ids=[parent_ids[int(key[1:]) - 1] for key in parsed["evidence_ids"]],
                status="refused" if parsed["refused"] else "answered",
                reason="model_refusal" if parsed["refused"] else None,
                refused=parsed["refused"],
                citation_check=parsed["citation_check"],
                answer_quotes=parsed["citations"],
            )
            row["trace"]["claim_to_span"] = parsed["claim_to_span"]
        else:
            row.update(
                answer="", citation_ids=[], status="failure", reason=reason or "invalid_output"
            )
            row["trace"]["claim_to_span"] = []
        row.update(
            elapsed_ms=elapsed,
            generation_ms=elapsed,
            retrieval_ms=0,
            attempts=calls,
            output_tokens=tokens,
            timing_scope="GPU generation only; prior retrieval timings excluded",
            claim_grounded_generation=copy.deepcopy(decision),
        )
        row["trace"]["raw_generation"] = raw
        result.append(row)
    return result


def eligible_for_experiment_b(candidate):
    return (
        candidate["failure_count"] == 0
        and candidate["unanswerable_answer_count"] <= 3
        and candidate["upstream_citation_precision"] is not None
        and candidate["upstream_citation_precision"] >= 0.458333
        and candidate["answered_count"] >= 20
    )


def development_gate(candidate, control, baseline, saved_7b, saved_span):
    false_answers_allowed = round(control["missing_refusal_rate"] * control["unanswerable_count"])
    return {
        "f1_exceeds_control": candidate["answerable_token_f1"] > control["answerable_token_f1"],
        "failures_do_not_increase": candidate["failure_count"] <= control["failure_count"],
        "unanswerable_answers_do_not_increase": (
            candidate["unanswerable_answer_count"] <= false_answers_allowed
        ),
        "citation_precision_not_lower": candidate["upstream_citation_precision"] is not None
        and candidate["upstream_citation_precision"] >= control["upstream_citation_precision"],
        "retain_80_percent_f1": candidate["answerable_token_f1"]
        >= 0.8 * baseline["answerable_token_f1"],
        "retain_half_answers": candidate["answered_count"]
        >= math.ceil(0.5 * baseline["answered_count"]),
        "no_new_generation_failures": candidate["failure_count"] <= baseline["failure_count"],
        "f1_exceeds_constrained_baseline": (
            candidate["answerable_token_f1"] > baseline["answerable_token_f1"]
        ),
        "f1_exceeds_saved_7b": (candidate["answerable_token_f1"] > saved_7b["answerable_token_f1"]),
        "citation_precision_not_lower_than_saved_7b": (
            candidate["upstream_citation_precision"] is not None
            and candidate["upstream_citation_precision"] >= saved_7b["upstream_citation_precision"]
        ),
        "retain_80_percent_saved_7b_answers": candidate["answered_count"]
        >= math.ceil(0.8 * saved_7b["answered_count"]),
        "f1_exceeds_saved_span_id": (
            candidate["answerable_token_f1"] > saved_span["answerable_token_f1"]
        ),
    }


def _query_f1(row):
    if row["status"] != "answered":
        return 0.0
    references = row["answer_criteria"].split(" | Alternative human answer: ")
    return max(token_f1(row["answer"], reference) for reference in references)


def _paired_bootstraps(candidate, report):
    by_id = {row["query_id"]: row for row in candidate if row["answerable"]}
    references = report["paired_answerable_rows"]
    if set(by_id) != {row["query_id"] for row in references}:
        raise ValueError("paired uncertainty roster differs from frozen answerable queries")
    comparisons = {}
    for key, reference_key in (("vs_intact_paragraphs", "candidate"), ("vs_span_id", "baseline")):
        pairs = [
            {
                "query_id": prior["query_id"],
                "family_id": prior["family_id"],
                "baseline": prior[reference_key],
                "candidate": _query_f1(by_id[prior["query_id"]]),
            }
            for prior in references
        ]
        comparisons[key] = paired_family_bootstrap(pairs)
    return comparisons


def score_candidate(candidate, previous, decisions, usage, supervisor, baseline_report):
    metrics = answer_metrics(candidate)
    metrics.pop("p50_ms", None)
    metrics.pop("p95_ms", None)
    metrics["unanswerable_answer_count"] = sum(
        row["status"] == "answered" and not row["answerable"] for row in candidate
    )
    metrics["generated_refusal_count"] = sum(
        row["status"] == "refused" and row["query_id"] in {d["query_id"] for d in decisions}
        for row in candidate
    )
    elapsed = [d["elapsed_ms"] for d in decisions if d["generation_calls"]]
    metrics["generation_latency_ms"] = {
        "scope": "32 supplied-evidence calls; excludes model loading and historical refusals",
        "p50": float(np.quantile(elapsed, 0.5)) if elapsed else None,
        "p95": float(np.quantile(elapsed, 0.95)) if elapsed else None,
    }
    source_metrics = baseline_report["metrics"]
    comparators = {
        "control": source_metrics["control"],
        "constrained_baseline": source_metrics["baseline"],
        "intact_paragraphs": source_metrics["candidate"],
        "saved_7b": source_metrics["saved_7b_baseline"],
        "saved_span_id": source_metrics["saved_span_id_baseline"],
    }
    gates = development_gate(
        metrics,
        comparators["control"],
        comparators["constrained_baseline"],
        comparators["saved_7b"],
        comparators["saved_span_id"],
    )
    return {
        "candidate": metrics,
        "comparators": comparators,
        "gate": gates,
        "passes_development_gate": all(gates.values()),
        "experiment_b_eligible": eligible_for_experiment_b(metrics),
        "usage": {
            **usage,
            "actual_output_tokens": sum(d["output_tokens"] for d in decisions),
            "worker_elapsed_seconds": supervisor["elapsed_seconds"],
        },
        "paired_family_bootstrap": _paired_bootstraps(candidate, baseline_report),
        "uncertainty_scope": (
            "Descriptive paired paper-family bootstrap on repeatedly reused development data; "
            "not selection-adjusted or independent confirmation."
        ),
        "scope": "Offline claim-grounded candidate; deployed release unchanged",
    }


def outputs(root, run, snapshot):
    helpers = worker.support()
    for name, expected_hash in snapshot["source_sha256"].items():
        if helpers.sha(Path(name)) != expected_hash:
            raise ValueError("approved source changed")
    for name, expected_hash in snapshot["baseline_source_sha256"].items():
        if helpers.sha(Path(name)) != expected_hash:
            raise ValueError("frozen baseline changed")
    approval(snapshot, root / "authorization.json")
    attempt, termination = read(root / "attempt.json"), read(root / "termination.json")
    snapshot_hash = digest(canonical(snapshot))
    if (
        attempt.get("snapshot_sha256") != snapshot_hash
        or (root / "worker.started").read_text("utf-8") != attempt.get("token")
        or termination.get("exit_code") != 0
        or termination.get("reason") != "process_exit"
        or not 0 <= termination.get("elapsed_seconds", -1) <= snapshot["deadline_seconds"]
    ):
        raise ValueError("GPU supervisor did not complete the approved deadline")
    if (
        read(run / "config.json") != snapshot
        or helpers.sha(run / "inputs.json") != snapshot["inputs_sha256"]
    ):
        raise ValueError("approved config or generation inputs changed")
    complete = read(run / "worker-complete.json")
    if complete.get("status") != "complete" or complete.get("snapshot_sha256") != snapshot_hash:
        raise ValueError("worker completion record differs from approved attempt")
    for name in ("decisions.jsonl", "usage.json"):
        if helpers.sha(run / name) != complete["files"].get(name):
            raise ValueError("worker output checksum mismatch")
    decisions = read_jsonl(run / "decisions.jsonl")
    usage = read(run / "usage.json")
    previous = load_baseline(Path(snapshot["baseline_run"]))
    if (
        digest((previous["run"] / "manifest.json").read_bytes())
        != snapshot["baseline_manifest_sha256"]
    ):
        raise ValueError("baseline manifest differs from approved snapshot")
    payloads = read(run / "inputs.json")
    expected_payloads = (
        previous["payloads"]
        if snapshot["scope"] == contract.SCOPE
        else top_three_payloads(previous["rows"], _dev_units(Path(snapshot["corpus_path"])))
    )
    if payloads != expected_payloads:
        raise ValueError("generation inputs differ from the frozen experiment protocol")
    call_limit = contract.specification(snapshot["scope"])["limits"]["calls"]
    if len(decisions) != call_limit or [d.get("query_id") for d in decisions] != [
        p["query_id"] for p in payloads
    ]:
        raise ValueError("decision roster/order differs from approved inputs")
    calls = sum(d["generation_calls"] for d in decisions)
    if calls > call_limit or usage != {
        "calls": calls,
        "reserved_tokens": contract.MAX_NEW_TOKENS * calls,
        "call_limit": call_limit,
    }:
        raise ValueError("generation call or reserved-token accounting mismatch")
    is_no_cutoff = snapshot["scope"] == contract.NO_CUTOFF_SCOPE
    if is_no_cutoff:
        a_snapshot, a_result = _verified_experiment_a()
        if (
            digest(canonical(a_result)) != snapshot["experiment_a_result_sha256"]
            or digest(canonical(a_snapshot)) != snapshot["experiment_a_snapshot_sha256"]
            or not eligible_for_experiment_b(a_result["metrics"]["candidate"])
        ):
            raise ValueError("Experiment A changed or failed its four B safeguards")
    candidate = merge_predictions(
        previous["rows"], decisions, payloads, replace_evidence=is_no_cutoff
    )
    if [row["query_id"] for row in candidate] != [row["query_id"] for row in previous["rows"]]:
        raise ValueError("all-50 scoring roster changed")
    if not is_no_cutoff:
        for before, after in zip(previous["rows"], candidate, strict=True):
            if not before["trace"]["packed_evidence"] and before != after:
                raise ValueError("original threshold refusal changed")
    metrics = score_candidate(
        candidate, previous["rows"], decisions, usage, termination, previous["report"]
    )
    if is_no_cutoff:
        blocked_ids = set(snapshot["previously_blocked_query_ids"])
        blocked = [row for row in candidate if row["query_id"] in blocked_ids]
        blocked_metrics = answer_metrics(blocked)
        metrics["previously_blocked_18"] = {
            "query_ids": sorted(blocked_ids),
            "query_count": len(blocked),
            "answerable_count": sum(bool(row["answerable"]) for row in blocked),
            "unanswerable_count": sum(not bool(row["answerable"]) for row in blocked),
            "answered_count": blocked_metrics["answered_count"],
            "refusal_count": (
                blocked_metrics["query_count"]
                - blocked_metrics["answered_count"]
                - blocked_metrics["failure_count"]
            ),
            "failure_count": blocked_metrics["failure_count"],
            "unanswerable_answer_count": sum(
                row["status"] == "answered" and not row["answerable"] for row in blocked
            ),
            "answerable_token_f1": blocked_metrics["answerable_token_f1"],
        }
    return candidate, metrics


def supervise(root, run, token):
    prior = module("run_gpu_support_filter")
    prior.GPU_PYTHON = GPU_PYTHON
    prior.WORKER = WORKER
    snapshot = read(run / "config.json")
    return prior.supervise(root, run, token, snapshot["deadline_seconds"])


def launch(snapshot, payloads, root):
    record = engine.approval(snapshot)
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
    (root / "authorization.json").write_bytes(canonical(record))
    base = engine.module("run_gpu_support_filter").base_module()
    run, manifest = base.create_run(root / "runs", snapshot)
    (run / "inputs.json").write_bytes(canonical(payloads))
    deadline = snapshot["deadline_seconds"]
    with base.run_lifecycle(run, manifest, deadline):
        code = engine.supervise(root, run, token)
        if code:
            raise RuntimeError(f"GPU worker exited with code {code}; attempt consumed")
        predictions, metrics = engine.outputs(root, run, snapshot)
        (run / "predictions.jsonl").write_bytes(
            b"\n".join(canonical(row) for row in predictions) + b"\n"
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
    return engine.verify(root, snapshot)


engine.outputs = outputs
engine.supervise = supervise
engine.approval = approval
engine.launch = launch


def _readiness(snapshot, root, approval_path):
    return {
        "status": "ready_for_authorization",
        "prepared_at_utc": datetime.now(UTC).isoformat(),
        "prepared_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True, encoding="utf-8"
        ).strip(),
        "scope": snapshot["scope"],
        "snapshot_sha256": digest(canonical(snapshot)),
        "snapshot": snapshot,
        "model_calls": 0,
        "training_runs": 0,
        "final_test_used": False,
        "artifact_root_exists": root.exists(),
        "authorization_exists": approval_path.exists(),
    }


def freeze_readiness(snapshot, path, root, approval_path):
    if path.exists():
        raise FileExistsError(f"refusing to overwrite frozen readiness record: {path}")
    record = _readiness(snapshot, root, approval_path)
    temp = path.with_suffix(".tmp")
    temp.write_bytes(canonical(record))
    temp.replace(path)
    return record


def ensure_frozen(snapshot, path):
    record = read(path)
    if (
        record.get("scope") != snapshot["scope"]
        or record.get("snapshot_sha256") != digest(canonical(snapshot))
        or record.get("snapshot") != snapshot
    ):
        raise ValueError("current inputs or code differ from the frozen readiness snapshot")


def main(argv=None):
    global GPU_PYTHON
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-run", type=Path, required=True)
    parser.add_argument("--gpu-python", type=Path, default=GPU_PYTHON)
    parser.add_argument("--experiment", choices=("A", "B"), default="A")
    parser.add_argument("--corpus", type=Path)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--freeze", action="store_true")
    mode.add_argument("--run-approved", action="store_true")
    mode.add_argument("--verify", action="store_true")
    args = parser.parse_args(argv)
    GPU_PYTHON = args.gpu_python.resolve()
    if args.experiment == "A":
        snapshot, payloads = preflight(args.baseline_run, GPU_PYTHON)
        root, readiness_path, approval_path, result_path = ROOT, READINESS, APPROVAL, REPORT_A
    else:
        if args.corpus is None:
            parser.error("Experiment B requires --corpus pointing to the cached development units")
        snapshot, payloads = preflight_no_cutoff(args.baseline_run, GPU_PYTHON, args.corpus)
        root, readiness_path, approval_path, result_path = ROOT_B, READINESS_B, APPROVAL_B, REPORT_B
    if args.freeze:
        result = freeze_readiness(snapshot, readiness_path, root, approval_path)
    elif args.run_approved:
        ensure_frozen(snapshot, readiness_path)
        result = engine.launch(snapshot, payloads, root)
        result_path.write_bytes(canonical(result))
    elif args.verify:
        ensure_frozen(snapshot, readiness_path)
        result = engine.verify(root, snapshot)
    else:
        result = {
            "status": "ready_for_authorization",
            "snapshot_sha256": digest(canonical(snapshot)),
            "calls": len(payloads),
            "reserved_output_tokens": snapshot["limits"]["reserved_tokens"],
            "worker_deadline_seconds": snapshot["deadline_seconds"],
            "model_calls": 0,
            "artifact_root_exists": root.exists(),
            "readiness_exists": readiness_path.exists(),
            "approval_exists": approval_path.exists(),
        }
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
