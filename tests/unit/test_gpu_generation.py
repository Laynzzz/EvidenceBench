import importlib.util
import json
from pathlib import Path

import pytest


def load(name):
    path = Path("scripts") / f"{name}.py"
    assert path.exists(), "GPU generator preparation not implemented"
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def rows():
    return [
        dict(
            query_id="q",
            question="Which feature?",
            answerable=True,
            answer_criteria="SECRET",
            supporting_evidence=["secret"],
            status="answered",
            answer="old",
            citation_ids=["p"],
            elapsed_ms=5,
            trace={"packed_ids": ["p"], "packed_evidence": {"E1": "Title\nTF-IDF features"}},
        ),
        dict(
            query_id="r",
            question="Unknown?",
            status="refused",
            answer="",
            citation_ids=[],
            elapsed_ms=4,
            trace={"packed_ids": [], "packed_evidence": {}},
        ),
    ]


def test_payloads_preserve_prompt_and_never_include_reference_labels():
    m = load("run_gpu_generation")
    p = m.payloads_for(rows())
    assert len(p) == 1
    assert "SECRET" not in json.dumps(p)
    assert p[0]["choices"][0] == "UNKNOWN"
    assert "TF-IDF" in p[0]["choices"]
    assert (
        p[0]["user_prompt"]
        == "Question: Which feature?\n\nEvidence:\n[E1] Title\nTF-IDF features\n\nShort answer:"
    )


def test_merge_validates_source_span_and_preserves_empty_evidence_refusal():
    m = load("run_gpu_generation")
    original = rows()
    p = m.payloads_for(original)
    decision = dict(
        query_id="q",
        input_sha256=m.digest(m.canonical(p[0])),
        raw="TF-IDF",
        reason=None,
        generation_calls=1,
        output_tokens=4,
        elapsed_ms=50,
    )
    out = m.merge(original, [decision])
    assert out[0]["answer"] == "TF-IDF"
    assert out[0]["citation_ids"] == ["p"]
    assert out[1] == original[1]
    decision["raw"] = "unseen claim"
    with pytest.raises(ValueError):
        m.merge(original, [decision])
    with pytest.raises(ValueError):
        m.merge(original, [])


def test_refusal_and_failure_remain_distinct():
    m = load("run_gpu_generation")
    p = m.payloads_for(rows())
    d = dict(
        query_id="q",
        input_sha256=m.digest(m.canonical(p[0])),
        raw="UNKNOWN",
        reason=None,
        generation_calls=1,
        output_tokens=2,
        elapsed_ms=10,
    )
    assert m.merge(rows(), [d])[0]["status"] == "refused"
    d.update(raw="", reason="RuntimeError", output_tokens=0)
    assert m.merge(rows(), [d])[0]["status"] == "failure"


def test_worker_whitelist_trie_and_meter(tmp_path):
    w = load("gpu_generation_worker")
    p = load("run_gpu_generation").payloads_for(rows())
    w.validate(p, 1)
    p[0]["answer_criteria"] = "SECRET"
    with pytest.raises(ValueError):
        w.validate(p, 1)
    trie = w.Trie([[3, 4], [5]], 2, 0)
    assert trie(0, [1, 1]) == [3, 5]
    assert trie(0, [1, 1, 3]) == [4]
    assert trie(0, [1, 1, 3, 4]) == [0]
    with pytest.raises(ValueError):
        trie(0, [1, 1, 8])
    meter = w.Meter(tmp_path / "usage.json", 1)
    meter.charge()
    assert json.loads((tmp_path / "usage.json").read_text())["reserved_tokens"] == 64
    with pytest.raises(ValueError):
        meter.charge()


def test_worker_eval_durable_budget_and_failure(tmp_path):
    w = load("gpu_generation_worker")
    p = load("run_gpu_generation").payloads_for(rows())

    def fail(payload, meter):
        meter.charge()
        raise RuntimeError("fake")

    w.evaluate(p, fail, tmp_path)
    decision = json.loads((tmp_path / "decisions.jsonl").read_text())
    assert decision["reason"] == "RuntimeError"
    assert decision["generation_calls"] == 1


def test_wrong_approval_rejected(tmp_path):
    m = load("run_gpu_generation")
    path = tmp_path / "approval.json"
    path.write_text(
        json.dumps({"scope": "gpu-generation-v1", "status": "approved", "snapshot_sha256": "bad"})
    )
    with pytest.raises(ValueError):
        m.approval({}, path)


def test_full_fake_worker_and_verification_preserve_18_refusals(tmp_path, monkeypatch):
    m, w = load("run_gpu_generation"), load("gpu_generation_worker")
    prior = m.module("run_gpu_support_filter")
    base = prior.base_module()
    monkeypatch.setattr(prior, "base_module", lambda: base)
    original = []
    for i in range(50):
        packed = i < 32
        answered = i < 28
        original.append(
            dict(
                query_id=str(i),
                question="Which résumé — 数据?",
                family_id=str(i),
                answerable=i < 38,
                answer_criteria="référence",
                supporting_evidence=["p"] if i < 38 else [],
                status="answered" if answered else "refused",
                answer="référence" if answered else "",
                reason=None if answered else "evidence_threshold",
                citation_ids=["p"] if answered else [],
                elapsed_ms=1,
                trace={
                    "packed_ids": ["p"] if packed else [],
                    "packed_evidence": {"E1": "Title\nréférence"} if packed else {},
                },
            )
        )
    monkeypatch.setattr(
        base, "original_rows", lambda: {"control": original, "constrained": original}
    )
    monkeypatch.setattr(base, "preflight", lambda: {"fixed": True})
    monkeypatch.setattr(base, "verify", lambda *a: None)
    normal_module = m.module
    monkeypatch.setattr(
        m, "module", lambda name: prior if name == "run_gpu_support_filter" else normal_module(name)
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
    )
    receipt = dict(
        status="approved",
        scope="gpu-generation-v1",
        snapshot_sha256=m.digest(m.canonical(snapshot)),
    )
    monkeypatch.setattr(m, "approval", lambda s, path=None: receipt)
    helpers = w.support()
    monkeypatch.setattr(helpers, "runtime_info", lambda: {"synthetic": True})
    monkeypatch.setattr(w, "support", lambda: helpers)
    monkeypatch.setenv("HF_HUB_OFFLINE", "1")
    monkeypatch.setenv("TRANSFORMERS_OFFLINE", "1")

    def generate(p, meter):
        assert "数据" in p["user_prompt"]
        meter.charge()
        return dict(raw="référence", output_tokens=3)

    monkeypatch.setattr(w, "load_generator", lambda s: (generate, {"synthetic": True}))

    def supervise(root, run, token):
        w.run_worker(run, token)
        (root / "termination.json").write_bytes(
            m.canonical(dict(reason="process_exit", exit_code=0, elapsed_seconds=1))
        )
        return 0

    monkeypatch.setattr(m, "supervise", supervise)
    root = tmp_path / "attempt"
    result = m.launch(snapshot, payloads, root)
    assert result["status"] == "verified"
    assert result["usage"]["calls"] == 32
    run = Path(result["run"])
    saved = [
        json.loads(line) for line in (run / "predictions.jsonl").read_text("utf-8").splitlines()
    ]
    assert saved[32:] == original[32:]
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


def test_worker_rejects_unapproved_attempt_before_loading(tmp_path, monkeypatch):
    w = load("gpu_generation_worker")
    run = tmp_path / "attempt" / "runs" / "fake"
    run.mkdir(parents=True)
    (run / "config.json").write_text("{}")
    (run.parent.parent / "attempt.json").write_text(json.dumps({"token": "wrong"}))
    (run.parent.parent / "authorization.json").write_text("{}")
    monkeypatch.setattr(w, "load_generator", lambda s: pytest.fail("must not load"))
    with pytest.raises(ValueError, match="approved"):
        w.run_worker(run, "right")


def test_trie_matches_frozen_cpu_contract():
    from evidencebench.generation_spans import SpanTrie

    w = load("gpu_generation_worker")
    paths = [[3], [3, 4], [5, 6]]
    cpu, gpu = SpanTrie(paths, 2, 0), w.Trie(paths, 2, 0)
    for suffix in [[], [3], [3, 4], [5], [5, 6]]:
        assert gpu(0, [9, 9] + suffix) == cpu(0, [9, 9] + suffix)


def test_all_refusals_are_scored_as_failed_gate_not_verification_error():
    m = load("run_gpu_generation")
    original = rows()
    original[1].update(answerable=False, answer_criteria="Unanswerable", supporting_evidence=[])
    p = m.payloads_for(original)
    decision = dict(
        query_id="q",
        input_sha256=m.digest(m.canonical(p[0])),
        raw="UNKNOWN",
        reason=None,
        generation_calls=1,
        output_tokens=2,
        elapsed_ms=10,
    )
    candidate = m.merge(original, [decision])
    base = m.module("run_gpu_support_filter").base_module()
    result = m.score(base, {"control": original, "constrained": original}, candidate)
    assert result["candidate"]["answered_count"] == 0
    assert result["candidate"]["upstream_citation_precision"] is None
    assert not result["gate"]["citation_precision_not_lower"]
    assert not result["passes_development_gate"]


def test_eligible_but_invalid_answer_is_per_query_failure():
    m = load("run_gpu_generation")
    original = rows()
    original[0]["trace"]["packed_evidence"]["E1"] = "Title\nYes is a source word"
    p = m.payloads_for(original)
    assert "Yes" in p[0]["choices"]
    d = dict(
        query_id="q",
        input_sha256=m.digest(m.canonical(p[0])),
        raw="Yes",
        reason=None,
        generation_calls=1,
        output_tokens=2,
        elapsed_ms=10,
    )
    result = m.merge(original, [d])
    assert result[0]["status"] == "failure"
    assert result[0]["reason"] == "invalid_span_generation"
    assert result[1] == original[1]
