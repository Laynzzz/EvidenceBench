import copy
import importlib.util
import json
from pathlib import Path

import pytest


def load(name):
    path = Path("scripts") / f"{name}.py"
    assert path.exists(), "intact-passage runner not implemented"
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def example():
    full = "Title\n" + "a " * 600 + "The answer is SVM."
    units = {"p": {"split": "dev", "text": full}}
    row = dict(
        query_id="q",
        question="Which model?",
        status="answered",
        reason=None,
        answer="old",
        citation_ids=["p"],
        answerable=True,
        answer_criteria="SECRET",
        supporting_evidence=["p"],
        family_id="f",
        elapsed_ms=1,
        trace=dict(packed_ids=["p"], packed_evidence={"E1": full[:1000]}),
    )
    return row, units


def test_restoration_uses_same_ids_and_keeps_threshold_refusals():
    m = load("run_intact_passage")
    row, units = example()
    before = copy.deepcopy(row)
    refusal = dict(
        query_id="r",
        status="refused",
        reason="insufficient_evidence",
        trace=dict(packed_ids=[], packed_evidence={}),
    )
    restored = m.restore_rows([row, refusal], units)
    assert row == before and restored[1] == refusal
    assert restored[0]["trace"]["packed_ids"] == ["p"]
    assert restored[0]["trace"]["packed_evidence"]["E1"] == units["p"]["text"]
    p = m.engine.payloads_for(restored[:1])[0]
    assert "SECRET" not in json.dumps(p)
    assert p["evidence"]["E1"].endswith("The answer is SVM.")


@pytest.mark.parametrize("mutation", ["source", "nondev", "missing", "empty", "alias"])
def test_restoration_rejects_inconsistent_provenance(mutation):
    m = load("run_intact_passage")
    row, units = example()
    if mutation == "source":
        units["p"]["text"] = "Changed body"
    if mutation == "nondev":
        units["p"]["split"] = "test"
    if mutation == "missing":
        units.clear()
    if mutation == "empty":
        row["trace"] = dict(packed_ids=[], packed_evidence={})
    if mutation == "alias":
        row["trace"]["packed_evidence"] = {"E2": "Text"}
    with pytest.raises(ValueError):
        m.restore_rows([row], units)


def test_merge_resolves_tail_span_and_keeps_old_adapter_isolated():
    m, old = load("run_intact_passage"), load("run_span_id_answer")
    row, units = example()
    restored = m.restore_rows([row], units)
    p = m.engine.payloads_for(restored)[0]
    spans = m.contract.catalog(p["evidence"])
    sid = next(k for k, v in spans.items() if "SVM" in v["quote"])
    d = dict(
        query_id="q",
        input_sha256=m.digest(m.canonical(p)),
        raw=json.dumps(dict(answer="SVM", span_ids=[sid])),
        reason=None,
        generation_calls=1,
        output_tokens=20,
        elapsed_ms=10,
    )
    result = m.engine.merge(restored, [d])[0]
    assert result["answer"] == "SVM" and result["citation_ids"] == ["p"]
    assert "SVM" in result["answer_quotes"][0]["quote"]
    assert result["trace"]["packed_evidence"] == p["evidence"]
    with pytest.raises(ValueError):
        old.engine.payloads_for(restored)


def test_approval_is_bound_to_new_scope_hash_and_allowance(tmp_path):
    m = load("run_intact_passage")
    snapshot = {"scope": m.contract.SCOPE}
    good = dict(
        status="approved",
        scope=m.contract.SCOPE,
        limits=m.ALLOWANCE,
        snapshot_sha256=m.digest(m.canonical(snapshot)),
    )
    p = tmp_path / "approval.json"
    p.write_text(json.dumps(good))
    assert m.approval(snapshot, p) == good
    for key, value in [
        ("scope", "span-id-answer-v1"),
        ("snapshot_sha256", "bad"),
        ("limits", {**m.ALLOWANCE, "attempts": 2}),
    ]:
        p.write_text(json.dumps({**good, key: value}))
        with pytest.raises(ValueError):
            m.approval(snapshot, p)


def test_full_synthetic_lifecycle_records_restored_evidence_and_twelve_gates(tmp_path, monkeypatch):
    m, w = load("run_intact_passage"), load("intact_passage_worker")
    e = m.engine
    prior = e.module("run_gpu_support_filter")
    base = prior.base_module()
    monkeypatch.setattr(prior, "base_module", lambda: base)
    clipped = []
    for i in range(50):
        row, units = example()
        row.update(query_id=str(i), answerable=i < 38, answer_criteria="SVM")
        if i >= 24:
            row.update(status="refused", reason="model_refusal", answer="", citation_ids=[])
        if i >= 32:
            row["reason"] = "insufficient_evidence"
            row["trace"] = dict(packed_ids=[], packed_evidence={})
        clipped.append(row)
    restored = m.restore_rows(clipped, units)
    monkeypatch.setattr(e, "baseline_rows", lambda expected: restored)
    monkeypatch.setattr(m, "span_baseline_rows", lambda: clipped)
    monkeypatch.setattr(base, "original_rows", lambda: {"control": clipped, "constrained": clipped})
    monkeypatch.setattr(base, "preflight", lambda: {"fixed": True})
    monkeypatch.setattr(base, "verify", lambda *args: None)
    normal = e.module
    monkeypatch.setattr(
        e, "module", lambda n: prior if n == "run_gpu_support_filter" else normal(n)
    )
    payloads = e.payloads_for(restored)
    model = tmp_path / "model"
    model.mkdir()
    snapshot = dict(
        scope=m.contract.SCOPE,
        limits=m.LIMITS,
        deadline_seconds=1200,
        inputs_sha256=m.digest(m.canonical(payloads)),
        base_snapshot_sha256=m.digest(m.canonical({"fixed": True})),
        source_sha256={},
        model_sha256={},
        model_dir=str(model),
        runtime={"synthetic": True},
        baseline_run="synthetic",
    )
    receipt = dict(
        status="approved",
        scope=m.contract.SCOPE,
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
        assert len(payload["evidence"]["E1"]) > 1000
        assert "SECRET" not in json.dumps(payload)
        meter.charge()
        sid = next(
            k for k, v in m.contract.catalog(payload["evidence"]).items() if "SVM" in v["quote"]
        )
        return dict(raw=json.dumps(dict(answer="SVM", span_ids=[sid])), output_tokens=20)

    monkeypatch.setattr(w, "load_generator", lambda s: (generate, {"synthetic": True}))

    def supervise(root, run, token):
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
    assert len(result["metrics"]["gate"]) == 12
    assert result["metrics"]["gate"]["f1_exceeds_saved_span_id"]
    saved = [
        json.loads(s)
        for s in (Path(result["run"]) / "predictions.jsonl").read_text("utf-8").splitlines()
    ]
    assert len(saved) == 50 and saved[32:] == clipped[32:]
    assert all(r["trace"]["packed_evidence"]["E1"] == units["p"]["text"] for r in saved[:32])
    assert all(r["answer"] == "SVM" and "SVM" in r["answer_quotes"][0]["quote"] for r in saved[:32])
    with pytest.raises(FileExistsError):
        e.launch(snapshot, payloads, root)
    monkeypatch.setattr(m, "span_baseline_rows", lambda: list(reversed(clipped)))
    with pytest.raises(ValueError, match="roster"):
        e.verify(root, snapshot)
