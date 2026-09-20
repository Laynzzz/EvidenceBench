import importlib.util
import json
from pathlib import Path

import pytest


def load(name):
    path = Path("scripts") / f"{name}.py"
    assert path.exists(), "grounded answer preparation not implemented"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def example():
    return {
        "query_id": "q",
        "question": "Which models were compared?",
        "answerable": True,
        "answer_criteria": "SECRET_REFERENCE",
        "supporting_evidence": ["SECRET_ID"],
        "family_id": "f",
        "answer": "old",
        "citation_ids": ["p"],
        "status": "answered",
        "elapsed_ms": 1,
        "trace": {
            "packed_ids": ["p", "s"],
            "packed_evidence": {
                "E1": "Paper title\nThe baselines were SVM and logistic regression.",
                "E2": "Paper title\nA CNN was also evaluated.",
            },
        },
    }


def response():
    return {
        "answer": "SVM, logistic regression and CNN.",
        "citations": [
            {"evidence_id": "E1", "quote": "The baselines were SVM and logistic regression."},
            {"evidence_id": "E2", "quote": "A CNN was also evaluated."},
        ],
    }


def decision(m, row, value):
    payload = m.payloads_for([row])[0]
    return dict(
        query_id=row["query_id"],
        input_sha256=m.digest(m.canonical(payload)),
        raw=json.dumps(value),
        reason=None,
        generation_calls=1,
        output_tokens=70,
        elapsed_ms=10,
    )


def test_complete_multi_source_answer_is_allowed_without_claiming_entailment():
    c = load("grounded_answer_contract")
    result = c.parse(json.dumps(response()), example()["trace"]["packed_evidence"])
    assert result["answer"] == response()["answer"]
    assert result["evidence_ids"] == ["E1", "E2"]
    assert result["citation_check"] == "exact_quote_presence_only"
    assert not result["refused"]
    value = response()
    value["answer"] = "An unsupported interpretation."
    # Structural validation must not advertise semantic entailment.
    assert (
        c.parse(json.dumps(value), example()["trace"]["packed_evidence"])["citation_check"]
        == "exact_quote_presence_only"
    )


@pytest.mark.parametrize(
    "change",
    [
        "missing",
        "unknown_id",
        "invented_quote",
        "title_only",
        "duplicate_id",
        "too_long",
        "empty_answer_with_citations",
        "answer_without_citations",
        "whitespace_answer",
        "extra_key",
    ],
)
def test_invalid_answer_contract_rejected(change):
    c = load("grounded_answer_contract")
    value = response()
    if change == "missing":
        value.pop("answer")
    if change == "unknown_id":
        value["citations"][0]["evidence_id"] = "E8"
    if change == "invented_quote":
        value["citations"][0]["quote"] = "Random forests won."
    if change == "title_only":
        value["citations"][0]["quote"] = "Paper title"
    if change == "duplicate_id":
        value["citations"].append(value["citations"][0])
    if change == "too_long":
        value["answer"] = "word " * 81
    if change == "empty_answer_with_citations":
        value["answer"] = ""
    if change == "answer_without_citations":
        value["citations"] = []
    if change == "whitespace_answer":
        value = {"answer": "  ", "citations": []}
    if change == "extra_key":
        value["confidence"] = 0.9
    with pytest.raises(ValueError):
        c.parse(json.dumps(value), example()["trace"]["packed_evidence"])


def test_duplicate_json_keys_and_non_object_are_rejected():
    c = load("grounded_answer_contract")
    for raw in [
        "[]",
        '{"answer":"x","answer":"","citations":[]}',
        '{"answer":"x","citations":[{"evidence_id":"E1","quote":"a","quote":"b"}]}',
        '```json\n{"answer":"","citations":[]}\n```',
    ]:
        with pytest.raises(ValueError):
            c.parse(raw, example()["trace"]["packed_evidence"])
    assert c.parse('{"answer":"","citations":[]}', {})["refused"]


def test_payload_has_no_reference_or_old_answer_and_freezes_evidence():
    m, w = load("run_grounded_answer"), load("grounded_answer_worker")
    row = example()
    p = m.payloads_for([row])
    assert p[0]["evidence"] == row["trace"]["packed_evidence"]
    assert p[0]["question"] == row["question"]
    assert "SECRET" not in json.dumps(p)
    assert set(p[0]) == {"query_id", "question", "evidence"}
    w.validate(p, 1)
    p[0]["answer_criteria"] = "leak"
    with pytest.raises(ValueError):
        w.validate(p, 1)
    with pytest.raises(ValueError):
        m.payloads_for([row, row])


def test_merge_keeps_refusals_and_separates_invalid_output_from_refusal():
    m = load("run_grounded_answer")
    row = example()
    refused = {
        **example(),
        "query_id": "r",
        "status": "refused",
        "answer": "",
        "citation_ids": [],
        "trace": {"packed_ids": [], "packed_evidence": {}},
    }
    out = m.merge([row, refused], [decision(m, row, response())])
    assert out[1] == refused
    assert out[0]["citation_ids"] == ["p", "s"]
    assert out[0]["citation_check"] == "exact_quote_presence_only"
    bad = response()
    bad["citations"][0]["quote"] = "invented"
    d = decision(m, row, bad)
    assert m.merge([row], [d])[0]["status"] == "failure"
    d = decision(m, row, {"answer": "", "citations": []})
    assert m.merge([row], [d])[0]["status"] == "refused"
    d.update(raw="", reason="RuntimeError")
    assert m.merge([row], [d])[0]["status"] == "failure"
    with pytest.raises(ValueError):
        m.merge([row], [])
    d["generation_calls"] = True
    with pytest.raises(ValueError):
        m.merge([row], [d])


def test_durable_reservation_precedes_generation_and_survives_failure(tmp_path):
    m, w = load("run_grounded_answer"), load("grounded_answer_worker")

    def generate(payload, meter):
        meter.charge()
        assert json.loads((tmp_path / "usage.json").read_text())["reserved_tokens"] == 384
        raise RuntimeError("synthetic failure")

    w.evaluate(m.payloads_for([example()]), generate, tmp_path)
    d = json.loads((tmp_path / "decisions.jsonl").read_text())
    assert d["reason"] == "RuntimeError" and d["generation_calls"] == 1
    meter = w.Meter(tmp_path / "another.json", 1)
    meter.charge()
    with pytest.raises(ValueError):
        meter.charge()


def test_unapproved_worker_never_loads_model(tmp_path, monkeypatch):
    w = load("grounded_answer_worker")
    run = tmp_path / "attempt" / "runs" / "fake"
    run.mkdir(parents=True)
    (run / "config.json").write_text("{}")
    (run.parent.parent / "attempt.json").write_text('{"token":"wrong"}')
    (run.parent.parent / "authorization.json").write_text("{}")
    monkeypatch.setattr(w, "load_generator", lambda s: pytest.fail("must not load"))
    with pytest.raises(ValueError, match="approved"):
        w.run_worker(run, "right")


def test_new_gate_requires_improvement_over_saved_7b_and_preserves_old_gate():
    m = load("run_grounded_answer")
    prior = m.module("run_gpu_support_filter")
    base = prior.base_module()
    row = example()
    row.update(answer="SVM", answer_criteria="SVM", supporting_evidence=["p"])
    negative = {
        **row,
        "query_id": "n",
        "answerable": False,
        "answer": "",
        "status": "refused",
        "citation_ids": [],
        "supporting_evidence": [],
        "answer_criteria": "Unanswerable",
    }
    source = {"control": [row, negative], "constrained": [row, negative]}
    result = m.score(base, source, [row, negative], [row, negative])
    assert not result["gate"]["f1_exceeds_saved_7b"]
    assert len(result["gate"]) == 11
    assert not result["passes_development_gate"]
    refusal = {**row, "status": "refused", "answer": "", "citation_ids": []}
    result = m.score(base, source, [refusal, negative], [row, negative])
    assert result["candidate"]["upstream_citation_precision"] is None
    assert not result["gate"]["citation_precision_not_lower_than_saved_7b"]


def test_complete_synthetic_run_verifies_and_preserves_18_refusals(tmp_path, monkeypatch):
    m, w = load("run_grounded_answer"), load("grounded_answer_worker")
    prior = m.module("run_gpu_support_filter")
    base = prior.base_module()
    monkeypatch.setattr(prior, "base_module", lambda: base)
    original = []
    for i in range(50):
        row = example()
        row.update(
            query_id=str(i),
            question="Which résumé — 数据 models?",
            answerable=i < 38,
            answer_criteria="SVM",
            supporting_evidence=["p"],
        )
        if i >= 24:
            row.update(status="refused", answer="", citation_ids=[])
        if i >= 32:
            row["trace"] = {"packed_ids": [], "packed_evidence": {}}
        original.append(row)
    monkeypatch.setattr(m, "baseline_rows", lambda expected_run: original)
    monkeypatch.setattr(
        base, "original_rows", lambda: {"control": original, "constrained": original}
    )
    monkeypatch.setattr(base, "preflight", lambda: {"fixed": True})
    monkeypatch.setattr(base, "verify", lambda *args: None)
    normal = m.module
    monkeypatch.setattr(
        m, "module", lambda n: prior if n == "run_gpu_support_filter" else normal(n)
    )
    model_dir = tmp_path / "fake-model"
    model_dir.mkdir()
    payloads = m.payloads_for(original)
    snapshot = dict(
        inputs_sha256=m.digest(m.canonical(payloads)),
        deadline_seconds=1200,
        base_snapshot_sha256=m.digest(m.canonical({"fixed": True})),
        source_sha256={},
        model_sha256={},
        model_dir=str(model_dir),
        runtime={"synthetic": True},
        baseline_run="synthetic",
    )
    receipt = dict(
        status="approved",
        scope="grounded-answer-v1",
        snapshot_sha256=m.digest(m.canonical(snapshot)),
    )
    monkeypatch.setattr(m, "approval", lambda s, path=None: receipt)
    helpers = w.support()
    monkeypatch.setattr(helpers, "runtime_info", lambda: {"synthetic": True})
    monkeypatch.setattr(w, "support", lambda: helpers)
    monkeypatch.setenv("HF_HUB_OFFLINE", "1")
    monkeypatch.setenv("TRANSFORMERS_OFFLINE", "1")

    def generate(payload, meter):
        assert "数据" in payload["question"]
        meter.charge()
        return {"raw": json.dumps(response()), "output_tokens": 70}

    monkeypatch.setattr(w, "load_generator", lambda s: (generate, {"synthetic": True}))

    def supervise(root, run, token):
        w.run_worker(run, token)
        (root / "termination.json").write_bytes(
            m.canonical(dict(reason="process_exit", exit_code=0, elapsed_seconds=1))
        )
        return 0

    monkeypatch.setattr(m, "supervise", supervise)
    root = tmp_path / "attempt"
    verified = m.launch(snapshot, payloads, root)
    assert verified["usage"] == {"calls": 32, "call_limit": 32, "reserved_tokens": 12288}
    saved = [
        json.loads(line)
        for line in (Path(verified["run"]) / "predictions.jsonl").read_text("utf-8").splitlines()
    ]
    assert len(saved) == 50 and saved[32:] == original[32:]
    assert all(row["status"] == "answered" for row in saved[:32])
    with pytest.raises(FileExistsError):
        m.launch(snapshot, payloads, root)
    monkeypatch.setattr(base, "preflight", lambda: {"fixed": False})
    with pytest.raises(ValueError, match="scoring inputs"):
        m.verify(root, snapshot)
    monkeypatch.setattr(base, "preflight", lambda: {"fixed": True})
    (root / "termination.json").write_bytes(
        m.canonical(dict(reason="timeout", exit_code=124, elapsed_seconds=1200))
    )
    with pytest.raises(ValueError, match="supervisor"):
        m.verify(root, snapshot)


def test_approval_is_bound_to_new_scope_and_snapshot(tmp_path):
    m = load("run_grounded_answer")
    path = tmp_path / "authorization.json"
    record = dict(
        status="approved", scope="gpu-generation-v1", snapshot_sha256=m.digest(m.canonical({}))
    )
    path.write_text(json.dumps(record))
    with pytest.raises(ValueError):
        m.approval({}, path)
    record["scope"] = "grounded-answer-v1"
    record["snapshot_sha256"] = "wrong"
    path.write_text(json.dumps(record))
    with pytest.raises(ValueError):
        m.approval({}, path)


def test_baseline_report_cannot_select_an_unverified_run(monkeypatch, tmp_path):
    m = load("run_grounded_answer")
    monkeypatch.setattr(m, "read", lambda path: {"run": str(tmp_path / "other")})
    with pytest.raises(ValueError, match="verified prior run"):
        m.baseline_rows(expected_run=tmp_path / "verified")


@pytest.mark.parametrize(
    ("first", "second", "valid"), [(80, 40, True), (80, 41, False), (81, 1, False)]
)
def test_quote_word_boundaries(first, second, valid):
    c = load("grounded_answer_contract")
    q1, q2 = " ".join(["alpha"] * first), " ".join(["beta"] * second)
    evidence = {"E1": "Title\n" + q1, "E2": "Title\n" + q2}
    raw = json.dumps(
        {
            "answer": "Summary.",
            "citations": [{"evidence_id": "E1", "quote": q1}, {"evidence_id": "E2", "quote": q2}],
        }
    )
    if valid:
        assert not c.parse(raw, evidence)["refused"]
    else:
        with pytest.raises(ValueError):
            c.parse(raw, evidence)


@pytest.mark.parametrize("mutation", ["source", "runtime", "input"])
def test_changed_assets_rejected_before_load_and_worker_start_is_single_use(
    tmp_path, monkeypatch, mutation
):
    w = load("grounded_answer_worker")
    helpers = w.support()
    root = tmp_path / "attempt"
    run = root / "runs" / "fake"
    run.mkdir(parents=True)
    model_dir = tmp_path / "model"
    model_dir.mkdir()
    source = tmp_path / "source.py"
    source.write_text("original")
    (run / "inputs.json").write_bytes(helpers.encoded([]))
    snapshot = {
        "source_sha256": {str(source): helpers.sha(source)},
        "runtime": {"synthetic": True},
        "model_dir": str(model_dir),
        "model_sha256": {},
        "inputs_sha256": helpers.sha(run / "inputs.json"),
    }
    (run / "config.json").write_bytes(helpers.encoded(snapshot))
    h = helpers.sha(run / "config.json")
    (root / "attempt.json").write_bytes(helpers.encoded({"token": "one", "snapshot_sha256": h}))
    (root / "authorization.json").write_bytes(
        helpers.encoded({"status": "approved", "scope": "grounded-answer-v1", "snapshot_sha256": h})
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
    with pytest.raises(ValueError, match="changed"):
        w.run_worker(run, "one")
    with pytest.raises(FileExistsError):
        w.run_worker(run, "one")
