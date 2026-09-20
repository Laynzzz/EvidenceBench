import importlib.util
import json
from pathlib import Path

import pytest


def load(name):
    path = Path(f"scripts/{name}.py")
    assert path.exists(), "GPU support preparation not implemented"
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def payload(key="q"):
    return {
        "query_id": key,
        "input": {
            "question": "Question?",
            "proposed_answer": "answer",
            "cited_evidence": {"E1": "source"},
        },
    }


def test_worker_payload_schema_rejects_labels_and_duplicate_queries():
    m = load("gpu_support_worker")
    m.validate_payloads([payload()], 1)
    bad = payload()
    bad["input"]["answer_criteria"] = "SECRET"
    with pytest.raises(ValueError):
        m.validate_payloads([bad], 1)
    with pytest.raises(ValueError):
        m.validate_payloads([payload(), payload()], 2)


def test_worker_meter_charges_before_failure_and_preserves_partial_usage(tmp_path):
    m = load("gpu_support_worker")
    meter = m.Meter(tmp_path / "usage.json", 1)
    meter.charge()
    assert json.loads((tmp_path / "usage.json").read_text())["calls"] == 1
    with pytest.raises(ValueError):
        meter.charge()
    assert json.loads((tmp_path / "usage.json").read_text())["reserved_tokens"] == 8
    with pytest.raises(FileExistsError):
        m.Meter(tmp_path / "usage.json", 1)


def test_decisions_keep_failure_distinct_from_unsupported(tmp_path):
    m = load("gpu_support_worker")
    calls = []

    def judge(p, meter):
        meter.charge()
        calls.append(p)
        if len(calls) == 2:
            raise RuntimeError("synthetic failure")
        return {"raw": "UNSUPPORTED", "output_tokens": 3}

    result = m.evaluate([payload("a"), payload("b")], judge, tmp_path)
    assert [x["verdict"] for x in result] == ["UNSUPPORTED", "FAILURE"]
    assert all(x["generation_calls"] == 1 for x in result)
    assert (tmp_path / "decisions.jsonl").read_text().count("\n") == 2


def test_prefix_allows_only_two_labels_and_eos():
    m = load("gpu_support_worker")
    fn = m.prefix_constraint([[3, 4], [5]], 2, 0)
    assert fn(0, [1, 1]) == [3, 5]
    assert fn(0, [1, 1, 3]) == [4]
    assert fn(0, [1, 1, 3, 4]) == [0]
    with pytest.raises(ValueError):
        fn(0, [1, 1, 8])


def test_merge_requires_exact_checked_roster_and_preserves_nonanswers():
    m = load("run_gpu_support_filter")
    base = m.base_module()
    rows = []
    for i, status in enumerate(["answered", "refused"]):
        rows.append(
            dict(
                query_id=str(i),
                status=status,
                answer="answer" if i == 0 else "",
                citation_ids=["c"] if i == 0 else [],
                trace={"packed_ids": ["c"], "packed_evidence": {"E1": "source"}},
                question="Question?",
            )
        )
    decision = {
        "query_id": "0",
        "input_sha256": base.digest(base.canonical(base.checker_input(rows[0]))),
        "verdict": "UNSUPPORTED",
        "reason": "unsupported",
        "raw": "UNSUPPORTED",
        "generation_calls": 1,
        "output_tokens": 3,
        "elapsed_ms": 1.0,
    }
    merged = m.merge(rows, [decision])
    assert [r["status"] for r in merged] == ["refused", "refused"]
    assert merged[1]["answer"] == rows[1]["answer"]
    with pytest.raises(ValueError):
        m.merge(rows, [])
    with pytest.raises(ValueError):
        m.merge(rows, [decision, decision])


def test_wrong_approval_snapshot_is_rejected(tmp_path):
    m = load("run_gpu_support_filter")
    p = tmp_path / "approval.json"
    p.write_text(
        json.dumps({"status": "approved", "scope": "gpu-support-v1", "snapshot_sha256": "wrong"})
    )
    with pytest.raises(ValueError):
        m.approval({"synthetic": True}, p)


def test_full_synthetic_worker_unicode_verification_and_timeout_rejection(tmp_path, monkeypatch):
    m, w = load("run_gpu_support_filter"), load("gpu_support_worker")
    base = m.base_module()
    monkeypatch.setattr(m, "base_module", lambda: base)
    original = []
    for i in range(50):
        answered = i < 28
        answerable = i < 22 or 28 <= i < 44
        original.append(
            dict(
                query_id=str(i),
                family_id=str(i),
                question="Which résumé — 数据?",
                status="answered" if answered else "refused",
                answer="reference" if answered else "",
                reason=None,
                citation_ids=["c"] if answered else [],
                answerable=answerable,
                answer_criteria="reference",
                supporting_evidence=["c"] if answerable else [],
                elapsed_ms=1,
                trace={
                    "packed_ids": ["c"],
                    "packed_evidence": {"E1": "Résumé — source 数据 reference"},
                },
            )
        )
    monkeypatch.setattr(
        base, "original_rows", lambda: {"control": original, "constrained": original}
    )
    payloads = [{"query_id": r["query_id"], "input": base.checker_input(r)} for r in original[:28]]
    monkeypatch.setattr(base, "preflight", lambda: {"fixed_base": True})
    monkeypatch.setattr(base, "verify", lambda *args: None)
    model_dir = tmp_path / "fake-model"
    model_dir.mkdir()
    snapshot = {
        "inputs_sha256": base.digest(base.canonical(payloads)),
        "deadline_seconds": 1200,
        "base_snapshot_sha256": base.digest(base.canonical({"fixed_base": True})),
        "source_sha256": {},
        "model_sha256": {},
        "model_dir": str(model_dir),
        "runtime": {"synthetic": True},
    }
    receipt = {
        "status": "approved",
        "scope": "gpu-support-v1",
        "snapshot_sha256": base.digest(base.canonical(snapshot)),
    }
    monkeypatch.setattr(m, "approval", lambda s, path=None: receipt)
    monkeypatch.setenv("HF_HUB_OFFLINE", "1")
    monkeypatch.setenv("TRANSFORMERS_OFFLINE", "1")
    monkeypatch.setattr(w, "runtime_info", lambda: {"synthetic": True})

    def judge(p, meter):
        assert "数据" in p["question"]
        meter.charge()
        return {"raw": "SUPPORTED", "output_tokens": 3}

    monkeypatch.setattr(w, "load_judge", lambda s: (judge, {"synthetic": True}))

    def supervise(root, run, token, seconds):
        w.run_worker(run, token)
        (root / "termination.json").write_bytes(
            base.canonical({"reason": "process_exit", "exit_code": 0, "elapsed_seconds": 1})
        )
        return 0

    monkeypatch.setattr(m, "supervise", supervise)
    root = tmp_path / "attempt"
    result = m.launch(snapshot, payloads, root)
    assert result["status"] == "verified"
    assert result["usage"]["calls"] == 28
    assert result["metrics"]["filtered"]["query_count"] == 50
    monkeypatch.setattr(base, "preflight", lambda: {"fixed_base": False})
    with pytest.raises(ValueError, match="base snapshot"):
        m.verify(root, snapshot)
    monkeypatch.setattr(base, "preflight", lambda: {"fixed_base": True})
    with pytest.raises(FileExistsError):
        m.launch(snapshot, payloads, root)
    (root / "termination.json").write_bytes(
        base.canonical({"reason": "timeout", "exit_code": 124, "elapsed_seconds": 1200})
    )
    with pytest.raises(ValueError, match="supervisor"):
        m.verify(root, snapshot)


def test_worker_requires_approval_before_model_loading(tmp_path, monkeypatch):
    w = load("gpu_support_worker")
    run = tmp_path / "root" / "runs" / "run"
    run.mkdir(parents=True)
    (run / "config.json").write_text("{}")
    (run.parent.parent / "attempt.json").write_text(
        json.dumps({"token": "wrong", "snapshot_sha256": "x"})
    )
    (run.parent.parent / "authorization.json").write_text("{}")
    monkeypatch.setattr(w, "load_judge", lambda s: pytest.fail("must not load"))
    with pytest.raises(ValueError, match="approved"):
        w.run_worker(run, "token")


def test_hard_timeout_kills_worker_and_subtracts_startup(tmp_path, monkeypatch):
    import subprocess

    m = load("run_gpu_support_filter")
    times = iter([10, 10.4, 11])
    monkeypatch.setattr(m.time, "monotonic", lambda: next(times))
    calls = []

    class Process:
        def wait(self, timeout=None):
            if timeout is not None:
                assert timeout == pytest.approx(0.6)
                raise subprocess.TimeoutExpired("fake", timeout)
            calls.append("wait")

        def kill(self):
            calls.append("kill")

    monkeypatch.setattr(m.subprocess, "Popen", lambda *a, **k: Process())
    assert m.supervise(tmp_path, tmp_path, "token", 1) == 124
    assert calls == ["kill", "wait"]


def test_exact_model_inventory_rejects_extra_checkpoint(tmp_path):
    w = load("gpu_support_worker")
    assert hasattr(w, "verify_model_files"), "exact model inventory verifier missing"
    p = tmp_path / "model-00001.safetensors"
    p.write_bytes(b"fake")
    snapshot = {"model_dir": str(tmp_path), "model_sha256": {p.name: w.sha(p)}}
    w.verify_model_files(snapshot)
    (tmp_path / ".cache").mkdir()
    (tmp_path / ".cache" / "metadata").write_text("allowed metadata")
    w.verify_model_files(snapshot)
    (tmp_path / "model.safetensors").write_bytes(b"wrong checkpoint")
    with pytest.raises(ValueError, match="inventory"):
        w.verify_model_files(snapshot)
