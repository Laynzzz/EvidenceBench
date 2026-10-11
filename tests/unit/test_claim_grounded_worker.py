import importlib.util
import json
from pathlib import Path

import pytest


def load_worker():
    path = Path("scripts/claim_grounded_worker.py")
    assert path.is_file(), "claim-grounded isolated worker is not implemented"
    spec = importlib.util.spec_from_file_location("claim_grounded_worker_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def payloads(worker, count=32):
    return [
        {
            "query_id": f"q{i}",
            "question": f"What is answer {i}?",
            "evidence": {"E1": "Paper\nSVM is supported."},
        }
        for i in range(count)
    ]


def test_prompt_inspection_returns_exact_lengths_and_rejects_overflow():
    worker = load_worker()
    rows = payloads(worker)

    class Tokenizer:
        def __init__(self, length):
            self.length = length

        def apply_chat_template(self, messages, add_generation_prompt):
            assert add_generation_prompt is True
            assert messages[0]["role"] == "system"
            return list(range(self.length))

    lengths = worker.prompt_lengths(rows[:2], Tokenizer(777))

    assert lengths == [
        {"query_id": "q0", "input_tokens": 777},
        {"query_id": "q1", "input_tokens": 777},
    ]
    with pytest.raises(ValueError, match="2048"):
        worker.prompt_lengths(rows[:1], Tokenizer(2049))


def test_worker_rejects_wrong_scope_before_model_loading(tmp_path, monkeypatch):
    worker = load_worker()
    run = tmp_path / "attempt" / "runs" / "candidate"
    run.mkdir(parents=True)
    root = run.parent.parent
    helpers = worker.support()
    snapshot = {
        "scope": "span-id-answer-v1",
        "limits": worker.contract.LIMITS,
        "deadline_seconds": 1200,
        "source_sha256": {},
        "baseline_source_sha256": {},
        "runtime": {"synthetic": True},
        "model_dir": str(tmp_path / "model"),
        "model_sha256": {},
    }
    (run / "inputs.json").write_text("[]", encoding="utf-8")
    snapshot["inputs_sha256"] = helpers.sha(run / "inputs.json")
    (run / "config.json").write_bytes(helpers.encoded(snapshot))
    snapshot_hash = helpers.sha(run / "config.json")
    (root / "attempt.json").write_bytes(
        helpers.encoded({"token": "one", "snapshot_sha256": snapshot_hash})
    )
    (root / "authorization.json").write_bytes(
        helpers.encoded(
            {
                "status": "approved",
                "scope": "span-id-answer-v1",
                "snapshot_sha256": snapshot_hash,
                "limits": worker.contract.ALLOWANCE,
            }
        )
    )
    monkeypatch.setattr(
        worker, "load_generator", lambda snapshot: pytest.fail("wrong scope must reject first")
    )

    with pytest.raises(ValueError, match="exact approved claim-grounded"):
        worker.run_worker(run, "one")


def test_worker_runs_one_fake_call_per_input_and_consumes_single_attempt(tmp_path, monkeypatch):
    worker = load_worker()
    helpers = worker.support()
    run = tmp_path / "attempt" / "runs" / "candidate"
    run.mkdir(parents=True)
    root = run.parent.parent
    rows = payloads(worker)
    (run / "inputs.json").write_bytes(helpers.encoded(rows))
    model_dir = tmp_path / "model"
    model_dir.mkdir()
    snapshot = {
        "scope": worker.contract.SCOPE,
        "limits": worker.contract.LIMITS,
        "deadline_seconds": 1200,
        "source_sha256": {},
        "baseline_source_sha256": {},
        "runtime": {"synthetic": True},
        "model_dir": str(model_dir),
        "model_sha256": {},
        "inputs_sha256": helpers.sha(run / "inputs.json"),
    }
    (run / "config.json").write_bytes(helpers.encoded(snapshot))
    snapshot_hash = helpers.sha(run / "config.json")
    (root / "attempt.json").write_bytes(
        helpers.encoded(
            {"token": "one", "snapshot_sha256": snapshot_hash, "consumes_single_attempt": True}
        )
    )
    (root / "authorization.json").write_bytes(
        helpers.encoded(
            {
                "status": "approved",
                "scope": worker.contract.SCOPE,
                "snapshot_sha256": snapshot_hash,
                "limits": worker.contract.ALLOWANCE,
            }
        )
    )
    monkeypatch.setenv("HF_HUB_OFFLINE", "1")
    monkeypatch.setenv("TRANSFORMERS_OFFLINE", "1")
    monkeypatch.setattr(helpers, "runtime_info", lambda: {"synthetic": True})
    monkeypatch.setattr(helpers, "verify_model_files", lambda _snapshot: None)
    monkeypatch.setattr(worker, "support", lambda: helpers)
    calls = []

    def generate(payload, meter):
        meter.charge()
        calls.append(payload["query_id"])
        return {
            "raw": json.dumps({"claims": [{"text": "SVM.", "span_ids": ["E1.S1"]}]}),
            "output_tokens": 5,
        }

    monkeypatch.setattr(worker, "load_generator", lambda _snapshot: (generate, {"gpu": "fake"}))

    worker.run_worker(run, "one")

    usage = json.loads((run / "usage.json").read_text(encoding="utf-8"))
    assert len(calls) == 32
    assert usage == {"calls": 32, "reserved_tokens": 12288, "call_limit": 32}
    complete = json.loads((run / "worker-complete.json").read_text(encoding="utf-8"))
    assert complete["status"] == "complete"
    assert complete["files"]["decisions.jsonl"] == helpers.sha(run / "decisions.jsonl")
    assert "model" not in complete["hardware"]
    with pytest.raises(FileExistsError):
        worker.run_worker(run, "one")
    assert len(calls) == 32


def test_no_cutoff_worker_uses_its_separate_50_call_allowance(tmp_path, monkeypatch):
    worker = load_worker()
    helpers = worker.support()
    run = tmp_path / "attempt-b" / "runs" / "candidate"
    run.mkdir(parents=True)
    root = run.parent.parent
    spec = worker.contract.specification(worker.contract.NO_CUTOFF_SCOPE)
    rows = payloads(worker, 50)
    (run / "inputs.json").write_bytes(helpers.encoded(rows))
    model_dir = tmp_path / "model"
    model_dir.mkdir()
    snapshot = {
        "scope": worker.contract.NO_CUTOFF_SCOPE,
        "limits": spec["limits"],
        "deadline_seconds": spec["deadline_seconds"],
        "source_sha256": {},
        "baseline_source_sha256": {},
        "runtime": {"synthetic": True},
        "model_dir": str(model_dir),
        "model_sha256": {},
        "inputs_sha256": helpers.sha(run / "inputs.json"),
    }
    (run / "config.json").write_bytes(helpers.encoded(snapshot))
    snapshot_hash = helpers.sha(run / "config.json")
    (root / "attempt.json").write_bytes(
        helpers.encoded(
            {"token": "two", "snapshot_sha256": snapshot_hash, "consumes_single_attempt": True}
        )
    )
    (root / "authorization.json").write_bytes(
        helpers.encoded(
            {
                "status": "approved",
                "scope": worker.contract.NO_CUTOFF_SCOPE,
                "snapshot_sha256": snapshot_hash,
                "limits": spec["allowance"],
            }
        )
    )
    monkeypatch.setenv("HF_HUB_OFFLINE", "1")
    monkeypatch.setenv("TRANSFORMERS_OFFLINE", "1")
    monkeypatch.setattr(helpers, "runtime_info", lambda: {"synthetic": True})
    monkeypatch.setattr(helpers, "verify_model_files", lambda _snapshot: None)
    monkeypatch.setattr(worker, "support", lambda: helpers)
    calls = []

    def generate(payload, meter):
        meter.charge()
        calls.append(payload["query_id"])
        return {
            "raw": json.dumps({"claims": [{"text": "Supported.", "span_ids": ["E1.S1"]}]}),
            "output_tokens": 3,
        }

    monkeypatch.setattr(worker, "load_generator", lambda _snapshot: (generate, {"gpu": "fake"}))

    worker.run_worker(run, "two")

    usage = json.loads((run / "usage.json").read_text(encoding="utf-8"))
    assert len(calls) == 50
    assert usage == {"calls": 50, "reserved_tokens": 19200, "call_limit": 50}
    complete = json.loads((run / "worker-complete.json").read_text(encoding="utf-8"))
    assert complete["status"] == "complete"
