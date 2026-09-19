import copy
import importlib.util
import json
import math
from pathlib import Path

import pytest


@pytest.fixture
def audit():
    path = Path("scripts/audit_fresh_selection.py")
    assert path.exists(), "offline selection audit is not implemented"
    spec = importlib.util.spec_from_file_location("fresh_selection_audit", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def row(key, score, gold, pre, post, answer="gold", status="answered"):
    return {
        "query_id": key,
        "family_id": key,
        "answerable": bool(gold),
        "answer_criteria": "gold" if gold else "",
        "supporting_evidence": gold,
        "answer": answer,
        "citation_ids": post[:1] if status == "answered" else [],
        "status": status,
        "reason": None,
        "elapsed_ms": 1,
        "trace": {
            "pre_ids": pre,
            "post_ids": post,
            "post_ranking": [
                {"element_id": p, "reranker_score": score - i} for i, p in enumerate(post)
            ],
            "packed_ids": post[:3] if score >= 1 else [],
        },
    }


def records():
    return [
        row("a", 2, ["g1", "g2"], ["x", "y", "z", "g1", "g2"], ["g1", "x", "y", "z", "g2"]),
        row("b", 0, ["g3"], ["g3"], ["g3"], answer="", status="refused"),
        row("c", 2, [], ["n"], ["n"]),
    ]


def test_rank_audit_keeps_macro_denominators_and_threshold_loss(audit):
    rows = records()
    result = audit.analyze(rows, copy.deepcopy(rows), 1)
    assert result["ranking"]["pre"]["3"]["macro_recall"] == 0.5
    assert result["ranking"]["post"]["3"]["macro_recall"] == 0.75
    assert result["ranking"]["packed"]["macro_recall"] == 0.25
    assert result["ranking"]["post"]["3"]["binary_ndcg"] == pytest.approx(
        (1 / (1 + 1 / math.log2(3)) + 1) / 2
    )
    assert result["score_separation"]["auc"] == 0.25
    assert result["threshold_confusion"] == {
        "answerable_pass": 1,
        "answerable_refuse": 1,
        "unanswerable_pass": 1,
        "unanswerable_refuse": 0,
    }


def test_auc_ties_half_credit_and_single_class_undefined(audit):
    assert audit.auc([2, 1], [1, 0]) == 0.875
    assert audit.auc([], [1]) is None
    assert audit.auc([1], []) is None


def test_filter_replay_keeps_tied_scores_together_and_never_invents_answers(audit):
    rows = records()
    before = copy.deepcopy(rows)
    result = audit.analyze(rows, copy.deepcopy(rows), 1)
    replay = result["higher_threshold_replay"]
    assert len(replay) == 2
    assert [r["metrics"]["answered_count"] for r in replay] == [2, 0]
    assert replay[-1]["metrics"]["upstream_citation_precision"] is None
    assert not replay[-1]["passes_original_gate"]
    assert rows == before


@pytest.mark.parametrize(
    "corruption,message",
    [
        ("duplicate", "unique rankings"),
        ("nonfinite", "nonfinite"),
        ("different_pool", "identical candidate pools"),
        ("pair", "unpaired"),
    ],
)
def test_corrupt_rankings_or_unpaired_rows_rejected(audit, corruption, message):
    a, b = records(), records()
    if corruption == "duplicate":
        a[0]["trace"]["pre_ids"].append("g1")
    elif corruption == "nonfinite":
        a[0]["trace"]["post_ranking"][0]["reranker_score"] = float("nan")
    elif corruption == "different_pool":
        a[0]["trace"]["pre_ids"][0] = "other"
    else:
        b[0]["query_id"] = "different"
    if corruption != "pair":
        b = copy.deepcopy(a)
    with pytest.raises(ValueError, match=message):
        audit.analyze(a, b, 1)


def test_report_check_detects_tampering_without_overwriting(audit, tmp_path):
    p = tmp_path / "report.json"
    audit.persist(p, {"count": 3}, check=False)
    original = p.read_bytes()
    audit.persist(p, {"count": 3}, check=True)
    with pytest.raises(ValueError):
        audit.persist(p, {"count": 4}, check=False)
    assert p.read_bytes() == original
    with pytest.raises(ValueError):
        audit.persist(p, {"count": 4}, check=True)


@pytest.mark.parametrize("stage", ["preflight", "verification"])
def test_failed_verification_prevents_analysis_and_report_write(
    audit, tmp_path, monkeypatch, stage
):
    from evidencebench import ingestion, labels
    from evidencebench.evaluation import fresh_runner, fresh_verification

    (tmp_path / "manifest.json").write_text(json.dumps({"config": {"synthetic": True}}))
    monkeypatch.setattr(audit, "RUN", tmp_path)
    output = tmp_path / "audit.json"
    monkeypatch.setattr(audit, "OUTPUT", output)
    monkeypatch.setattr("sys.argv", ["audit_fresh_selection.py"])
    monkeypatch.setattr(fresh_runner, "preflight", lambda: {"synthetic": stage != "preflight"})
    monkeypatch.setattr(labels, "read_labels", lambda _: [])
    monkeypatch.setattr(ingestion, "load_units", lambda _: [])

    def reject(*args):
        raise ValueError("synthetic verification rejection")

    def unexpected(*args):
        pytest.fail("verification failure must prevent analysis")

    monkeypatch.setattr(fresh_verification, "verify_run", reject)
    monkeypatch.setattr(audit, "analyze", unexpected)
    with pytest.raises(ValueError, match="frozen run differs|synthetic verification rejection"):
        audit.main()
    assert not output.exists()
