import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

import pytest


def load_runner():
    path = Path("scripts/run_claim_grounded.py")
    assert path.is_file(), "claim-grounded experiment runner is not implemented"
    spec = importlib.util.spec_from_file_location("claim_grounded_runner_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def baseline_rows():
    rows = []
    for i in range(50):
        active = i < 32
        answerable = i < 26 or 32 <= i < 44
        rows.append(
            {
                "query_id": f"q{i}",
                "question": f"What does source {i} say?",
                "family_id": f"paper-{i // 2}",
                "answerable": answerable,
                "answer_criteria": "SVM" if answerable else "",
                "supporting_evidence": ["p0"] if answerable else [],
                "status": "answered" if active else "refused",
                "reason": None if active else "insufficient_evidence",
                "answer": "old answer" if active else "",
                "citation_ids": ["p0"] if active else [],
                "trace": {
                    "packed_ids": ["p0"] if active else [],
                    "packed_evidence": {"E1": "Paper\nSVM is supported."} if active else {},
                },
            }
        )
    return rows


def decision(runner, payload, raw=None, reason=None, calls=1, output_tokens=20):
    return {
        "query_id": payload["query_id"],
        "input_sha256": runner.digest(runner.canonical(payload)),
        "raw": raw
        if raw is not None
        else json.dumps({"claims": [{"text": "SVM is supported.", "span_ids": ["E1.S1"]}]}),
        "reason": reason,
        "generation_calls": calls,
        "output_tokens": output_tokens if calls else 0,
        "elapsed_ms": 10.0,
    }


def test_payloads_are_exact_label_free_inputs_and_keep_all_18_refusals():
    runner = load_runner()
    rows = baseline_rows()

    payloads = runner.payloads_for(rows)

    assert len(payloads) == 32
    assert payloads[0] == {
        "query_id": "q0",
        "question": "What does source 0 say?",
        "evidence": {"E1": "Paper\nSVM is supported."},
    }
    assert all(set(payload) == {"query_id", "question", "evidence"} for payload in payloads)
    assert all("answerable" not in json.dumps(payload) for payload in payloads)
    with pytest.raises(ValueError, match="threshold refusal"):
        runner.payloads_for([*rows[:-1], {**rows[-1], "reason": "model_refusal"}])


def test_snapshot_covers_every_nonstandard_lifecycle_dependency():
    runner = load_runner()
    sources = {path.as_posix() for path in runner.SOURCE_PATHS}

    assert "src/evidencebench/tracking.py" in sources


def test_label_roster_uses_fresh_development_ids_independent_of_file_order(monkeypatch):
    runner = load_runner()
    rows = baseline_rows()
    labels = [
        SimpleNamespace(
            query_id=row["query_id"],
            text=row["question"],
            family_id=row["family_id"],
            answerable=row["answerable"],
            answer_criteria=row["answer_criteria"],
            supporting_evidence=row["supporting_evidence"],
        )
        for row in rows
    ]
    monkeypatch.setattr(runner, "read_labels", lambda _path: list(reversed(labels)))

    assert runner.LABELS_PATH.as_posix() == "data/labels/qasper-fresh-v1/dev.jsonl"
    runner._check_label_alignment(rows)


def test_merge_keeps_claim_mappings_and_failed_raw_output_and_preserves_refusals():
    runner = load_runner()
    rows = baseline_rows()
    payloads = runner.payloads_for(rows)
    decisions = [decision(runner, payload) for payload in payloads]
    decisions[1] = decision(
        runner,
        payloads[1],
        raw='{"claims":[{"text":"Unsupported.","span_ids":["E1.S9"]}]}',
    )
    decisions[2] = decision(runner, payloads[2], raw='{"claims":[]}')

    merged = runner.merge_predictions(rows, decisions)

    assert len(merged) == 50
    assert merged[0]["answer"] == "SVM is supported."
    assert merged[0]["citation_ids"] == ["p0"]
    assert merged[0]["trace"]["claim_to_span"][0]["span_ids"] == ["E1.S1"]
    assert merged[1]["status"] == "failure"
    assert merged[1]["trace"]["raw_generation"] == decisions[1]["raw"]
    assert merged[1]["trace"]["validation_error"] == "unknown source span ID"
    assert merged[2]["status"] == "refused"
    assert merged[32:] == rows[32:]


def test_development_gate_preserves_all_12_conditions_and_strict_span_id_cutoff():
    runner = load_runner()
    control = {
        "answerable_token_f1": 0.012025255446308078,
        "failure_count": 21,
        "missing_refusal_rate": 0.25,
        "unanswerable_count": 12,
        "upstream_citation_precision": 0.36363636363636365,
        "answered_count": 11,
    }
    baseline = {
        "answerable_token_f1": 0.07542449567049109,
        "failure_count": 0,
        "answered_count": 28,
    }
    saved_7b = {
        "answerable_token_f1": 0.12357810681224572,
        "upstream_citation_precision": 0.4583333333333333,
        "answered_count": 24,
    }
    saved_span = {"answerable_token_f1": 0.21408410287572385}
    candidate = {
        "answerable_token_f1": 0.2402,
        "failure_count": 0,
        "answered_count": 25,
        "missing_refusal_rate": 2 / 12,
        "unanswerable_count": 12,
        "unanswerable_answer_count": 2,
        "upstream_citation_precision": 0.46,
    }

    gates = runner.development_gate(candidate, control, baseline, saved_7b, saved_span)

    assert len(gates) == 12
    assert all(gates.values())
    equal_to_span_id = {**candidate, "answerable_token_f1": saved_span["answerable_token_f1"]}
    assert (
        runner.development_gate(equal_to_span_id, control, baseline, saved_7b, saved_span)[
            "f1_exceeds_saved_span_id"
        ]
        is False
    )


@pytest.mark.parametrize(
    "candidate,expected",
    [
        (
            {
                "failure_count": 0,
                "unanswerable_answer_count": 3,
                "upstream_citation_precision": 0.458333,
                "answered_count": 20,
            },
            True,
        ),
        (
            {
                "failure_count": 1,
                "unanswerable_answer_count": 3,
                "upstream_citation_precision": 0.5,
                "answered_count": 20,
            },
            False,
        ),
        (
            {
                "failure_count": 0,
                "unanswerable_answer_count": 4,
                "upstream_citation_precision": 0.5,
                "answered_count": 20,
            },
            False,
        ),
        (
            {
                "failure_count": 0,
                "unanswerable_answer_count": 3,
                "upstream_citation_precision": 0.45,
                "answered_count": 20,
            },
            False,
        ),
        (
            {
                "failure_count": 0,
                "unanswerable_answer_count": 3,
                "upstream_citation_precision": 0.5,
                "answered_count": 19,
            },
            False,
        ),
    ],
)
def test_experiment_b_requires_all_four_prespecified_safeguards(candidate, expected):
    runner = load_runner()

    assert runner.eligible_for_experiment_b(candidate) is expected


def test_no_cutoff_payloads_use_saved_top_three_complete_dev_paragraphs_for_all_50():
    runner = load_runner()
    rows = baseline_rows()
    units = {}
    expected_ids = {}
    for i, row in enumerate(rows):
        ranking = []
        for rank in range(1, 4):
            element_id = f"element-{i}-{rank}"
            units[element_id] = {
                "split": "dev",
                "text": f"Paper {i}\nSaved complete paragraph {rank}.",
            }
            ranking.append({"element_id": element_id, "rank": rank})
        row["trace"]["post_ranking"] = ranking
        expected_ids[row["query_id"]] = [item["element_id"] for item in ranking]

    payloads = runner.top_three_payloads(rows, units)
    decisions = [decision(runner, payload) for payload in payloads]
    merged = runner.merge_predictions(rows, decisions, payloads, replace_evidence=True)

    assert len(payloads) == len(merged) == 50
    assert all(len(payload["evidence"]) == 3 for payload in payloads)
    assert all(set(payload) == {"query_id", "question", "evidence"} for payload in payloads)
    for payload, row in zip(payloads, merged, strict=True):
        assert row["trace"]["packed_ids"] == expected_ids[row["query_id"]]
        assert row["citation_ids"] == [expected_ids[row["query_id"]][0]]
        assert row["answer"] == "SVM is supported."
        assert row["trace"]["packed_evidence"] == payload["evidence"]


def test_fake_full_run_checks_approval_deadline_budget_tampering_and_single_use(
    tmp_path, monkeypatch
):
    runner = load_runner()
    rows = baseline_rows()
    inputs = runner.payloads_for(rows)
    source_run = tmp_path / "prior-run"
    source_run.mkdir()
    (source_run / "manifest.json").write_text('{"source":"frozen"}', encoding="utf-8")
    baseline = {
        "run": source_run,
        "manifest": {},
        "rows": rows,
        "payloads": inputs,
        "report": {"metrics": {"synthetic": True}},
    }
    monkeypatch.setattr(runner, "load_baseline", lambda _path: baseline)
    monkeypatch.setattr(
        runner,
        "score_candidate",
        lambda *_args: {"candidate": {"answered_count": 32}, "gate": {"synthetic": True}},
    )

    helpers = runner.worker.support()
    monkeypatch.setattr(helpers, "runtime_info", lambda: {"synthetic": True})
    monkeypatch.setattr(helpers, "verify_model_files", lambda _snapshot: None)
    monkeypatch.setattr(runner.worker, "support", lambda: helpers)
    monkeypatch.setenv("HF_HUB_OFFLINE", "1")
    monkeypatch.setenv("TRANSFORMERS_OFFLINE", "1")
    generated = []

    def generate(payload, meter):
        meter.charge()
        generated.append(payload["query_id"])
        return {
            "raw": json.dumps({"claims": [{"text": "SVM is supported.", "span_ids": ["E1.S1"]}]}),
            "output_tokens": 5,
        }

    monkeypatch.setattr(
        runner.worker, "load_generator", lambda _snapshot: (generate, {"gpu": "synthetic"})
    )
    snapshot = {
        "scope": runner.contract.SCOPE,
        "limits": runner.contract.LIMITS,
        "deadline_seconds": 1200,
        "source_sha256": {},
        "baseline_source_sha256": {},
        "runtime": {"synthetic": True},
        "model_dir": str(tmp_path / "unused-model"),
        "model_sha256": {},
        "inputs_sha256": runner.digest(runner.canonical(inputs)),
        "baseline_run": str(source_run),
        "baseline_manifest_sha256": runner.digest((source_run / "manifest.json").read_bytes()),
    }
    receipt = {
        "status": "approved",
        "scope": runner.contract.SCOPE,
        "snapshot_sha256": runner.digest(runner.canonical(snapshot)),
        "limits": runner.contract.ALLOWANCE,
        "approval_text": "synthetic test authorization",
        "recorded_at_utc": "2026-10-10T00:00:00Z",
    }
    monkeypatch.setattr(runner.engine, "approval", lambda _snapshot: receipt)

    def supervise(root, run, token):
        runner.worker.run_worker(run, token)
        (root / "termination.json").write_bytes(
            helpers.encoded({"reason": "process_exit", "exit_code": 0, "elapsed_seconds": 1.0})
        )
        return 0

    monkeypatch.setattr(runner.engine, "supervise", supervise)
    root = tmp_path / "claim-attempt"

    result = runner.engine.launch(snapshot, inputs, root)

    assert result["status"] == "verified"
    assert result["usage"] == {"calls": 32, "reserved_tokens": 12288, "call_limit": 32}
    assert len(generated) == 32
    saved = [
        json.loads(line)
        for line in (Path(result["run"]) / "predictions.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
    ]
    assert saved[32:] == rows[32:]
    assert saved[0]["trace"]["claim_to_span"][0]["span_ids"] == ["E1.S1"]
    with pytest.raises(FileExistsError):
        runner.engine.launch(snapshot, inputs, root)
    assert len(generated) == 32

    termination = json.loads((root / "termination.json").read_text(encoding="utf-8"))
    (root / "termination.json").write_bytes(
        helpers.encoded({**termination, "elapsed_seconds": 1201})
    )
    with pytest.raises(ValueError, match="approved deadline"):
        runner.engine.verify(root, snapshot)
    (root / "termination.json").write_bytes(helpers.encoded(termination))

    run_path = Path(result["run"])
    (run_path / "inputs.json").write_text("[]", encoding="utf-8")
    with pytest.raises(ValueError, match="output checksum"):
        runner.engine.verify(root, snapshot)
