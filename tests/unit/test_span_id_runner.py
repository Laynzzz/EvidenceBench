import importlib.util
import json
from pathlib import Path

import pytest


def load(name):
    path = Path("scripts") / f"{name}.py"
    assert path.exists(), "span-ID runner not implemented"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def example():
    return dict(
        query_id="q",
        question="Which résumé — 数据 models?",
        answerable=True,
        answer_criteria="SECRET_REFERENCE",
        supporting_evidence=["SECRET_ID"],
        family_id="family",
        elapsed_ms=1,
        status="answered",
        answer="old",
        citation_ids=["p"],
        trace=dict(
            packed_ids=["p"],
            packed_evidence={"E1": "Title\nWe compared SVM. Logistic regression also ran."},
        ),
    )


def output():
    return {"answer": "SVM and logistic regression.", "span_ids": ["E1.S1", "E1.S2"]}


def test_adapter_isolation_and_label_free_inputs():
    m = load("run_span_id_answer")
    original = load("run_grounded_answer")
    assert original.ROOT != m.ROOT
    assert original.WORKER != m.engine.WORKER
    payload = m.engine.payloads_for([example()])[0]
    assert "SECRET" not in json.dumps(payload)
    assert payload["evidence"] == example()["trace"]["packed_evidence"]
    d = dict(
        query_id="q",
        input_sha256=m.digest(m.canonical(payload)),
        raw=json.dumps(output()),
        reason=None,
        generation_calls=1,
        output_tokens=25,
        elapsed_ms=10,
    )
    row = m.engine.merge([example()], [d])[0]
    assert row["citation_ids"] == ["p"]
    assert len(row["answer_quotes"]) == 2
    assert row["status"] == "answered"
    assert original.merge([example()], [d])[0]["status"] == "failure"
    d["raw"] = '{"answer":"x","span_ids":["E1.S999"]}'
    assert m.engine.merge([example()], [d])[0]["status"] == "failure"
    d["raw"] = '{"answer":"","span_ids":[]}'
    assert m.engine.merge([example()], [d])[0]["status"] == "refused"


def test_approval_requires_new_scope_exact_hash_and_bounds(tmp_path):
    m = load("run_span_id_answer")
    snapshot = {"scope": "span-id-answer-v1"}
    receipt = dict(
        status="approved",
        scope="span-id-answer-v1",
        snapshot_sha256=m.digest(m.canonical(snapshot)),
        limits=m.ALLOWANCE,
    )
    path = tmp_path / "approval.json"
    path.write_text(json.dumps(receipt))
    assert m.approval(snapshot, path) == receipt
    for key, value in [
        ("scope", "grounded-answer-v1"),
        ("snapshot_sha256", "wrong"),
        ("limits", {**m.ALLOWANCE, "attempts": 2}),
    ]:
        path.write_text(json.dumps({**receipt, key: value}))
        with pytest.raises(ValueError, match="approval"):
            m.approval(snapshot, path)


def test_no_approval_never_loads_worker(tmp_path, monkeypatch):
    w = load("span_id_answer_worker")
    run = tmp_path / "attempt" / "runs" / "fake"
    run.mkdir(parents=True)
    (run / "config.json").write_text("{}")
    (run.parent.parent / "attempt.json").write_text('{"token":"wrong"}')
    (run.parent.parent / "authorization.json").write_text("{}")
    monkeypatch.setattr(w, "load_generator", lambda s: pytest.fail("must not load model"))
    with pytest.raises(ValueError, match="approved"):
        w.run_worker(run, "right")


def test_complete_synthetic_run_one_attempt_and_all_frozen_rows(tmp_path, monkeypatch):
    m, w = load("run_span_id_answer"), load("span_id_answer_worker")
    e = m.engine
    prior = e.module("run_gpu_support_filter")
    base = prior.base_module()
    monkeypatch.setattr(prior, "base_module", lambda: base)
    rows = []
    for i in range(50):
        row = example()
        row.update(query_id=str(i), answerable=i < 38, answer_criteria="SVM")
        if i >= 24:
            row.update(status="refused", answer="", citation_ids=[])
        if i >= 32:
            row["trace"] = {"packed_ids": [], "packed_evidence": {}}
        rows.append(row)
    monkeypatch.setattr(e, "baseline_rows", lambda expected: rows)
    monkeypatch.setattr(base, "original_rows", lambda: {"control": rows, "constrained": rows})
    monkeypatch.setattr(base, "preflight", lambda: {"fixed": True})
    monkeypatch.setattr(base, "verify", lambda *args: None)
    normal = e.module
    monkeypatch.setattr(
        e, "module", lambda n: prior if n == "run_gpu_support_filter" else normal(n)
    )
    model_dir = tmp_path / "model"
    model_dir.mkdir()
    payloads = e.payloads_for(rows)
    snapshot = dict(
        scope="span-id-answer-v1",
        limits=m.LIMITS,
        deadline_seconds=1200,
        inputs_sha256=m.digest(m.canonical(payloads)),
        base_snapshot_sha256=m.digest(m.canonical({"fixed": True})),
        source_sha256={},
        model_sha256={},
        model_dir=str(model_dir),
        runtime={"synthetic": True},
        baseline_run="synthetic",
    )
    receipt = dict(
        status="approved",
        scope="span-id-answer-v1",
        limits=m.ALLOWANCE,
        snapshot_sha256=m.digest(m.canonical(snapshot)),
    )
    monkeypatch.setattr(e, "approval", lambda s, path=None: receipt)
    helpers = w.support()
    monkeypatch.setattr(helpers, "runtime_info", lambda: {"synthetic": True})
    monkeypatch.setattr(w, "support", lambda: helpers)
    monkeypatch.setenv("HF_HUB_OFFLINE", "1")
    monkeypatch.setenv("TRANSFORMERS_OFFLINE", "1")

    def generate(payload, meter):
        assert "数据" in payload["question"]
        meter.charge()
        assert json.loads((current_run[0] / "usage.json").read_text())["reserved_tokens"] >= 384
        return {"raw": json.dumps(output()), "output_tokens": 25}

    current_run = []
    monkeypatch.setattr(w, "load_generator", lambda s: (generate, {"synthetic": True}))

    def supervise(root, run, token):
        current_run.append(run)
        w.run_worker(run, token)
        (root / "termination.json").write_bytes(
            m.canonical(dict(reason="process_exit", exit_code=0, elapsed_seconds=1))
        )
        return 0

    monkeypatch.setattr(e, "supervise", supervise)
    root = tmp_path / "attempt"
    result = e.launch(snapshot, payloads, root)
    assert result["status"] == "verified"
    assert result["usage"] == dict(calls=32, call_limit=32, reserved_tokens=12288)
    assert len(result["metrics"]["gate"]) == 11
    saved = [
        json.loads(x) for x in (Path(result["run"]) / "predictions.jsonl").read_text().splitlines()
    ]
    assert len(saved) == 50 and saved[32:] == rows[32:]
    assert all(r["status"] == "answered" and r["citation_ids"] == ["p"] for r in saved[:32])
    with pytest.raises(FileExistsError):
        e.launch(snapshot, payloads, root)
    monkeypatch.setattr(base, "preflight", lambda: {"fixed": False})
    with pytest.raises(ValueError, match="scoring inputs"):
        e.verify(root, snapshot)


@pytest.mark.parametrize("mutation", ["scope", "source", "runtime", "input", "limits"])
def test_worker_rejects_tampering_before_loading(tmp_path, monkeypatch, mutation):
    m, w = load("run_span_id_answer"), load("span_id_answer_worker")
    helpers = w.support()
    run = tmp_path / "attempt" / "runs" / "fake"
    run.mkdir(parents=True)
    root = run.parent.parent
    source = tmp_path / "source.py"
    source.write_text("original")
    model = tmp_path / "model"
    model.mkdir()
    (run / "inputs.json").write_text("[]")
    snapshot = dict(
        scope="span-id-answer-v1",
        limits=m.LIMITS,
        deadline_seconds=1200,
        source_sha256={str(source): helpers.sha(source)},
        runtime={"synthetic": True},
        model_dir=str(model),
        model_sha256={},
        inputs_sha256=helpers.sha(run / "inputs.json"),
    )
    if mutation == "scope":
        snapshot["scope"] = "grounded-answer-v1"
    if mutation == "limits":
        snapshot["limits"] = {**m.LIMITS, "calls": 33}
    (run / "config.json").write_bytes(helpers.encoded(snapshot))
    h = helpers.sha(run / "config.json")
    (root / "attempt.json").write_bytes(helpers.encoded(dict(token="one", snapshot_sha256=h)))
    (root / "authorization.json").write_bytes(
        helpers.encoded(
            dict(
                status="approved", scope="span-id-answer-v1", snapshot_sha256=h, limits=m.ALLOWANCE
            )
        )
    )
    monkeypatch.setenv("HF_HUB_OFFLINE", "1")
    monkeypatch.setenv("TRANSFORMERS_OFFLINE", "1")
    monkeypatch.setattr(helpers, "runtime_info", lambda: {"synthetic": mutation != "runtime"})
    monkeypatch.setattr(w, "support", lambda: helpers)
    monkeypatch.setattr(w, "load_generator", lambda s: pytest.fail("must reject before loading"))
    if mutation == "source":
        source.write_text("changed")
    if mutation == "input":
        (run / "inputs.json").write_text("[{}]")
    with pytest.raises(ValueError):
        w.run_worker(run, "one")
