import copy
import importlib.util
from pathlib import Path

import pytest


def module():
    path = Path("scripts/audit_gpu_answers.py")
    assert path.exists(), "offline audit not implemented"
    spec = importlib.util.spec_from_file_location("audit_gpu_answers", path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def rows():
    return [
        dict(
            query_id="a",
            family_id="paper",
            question="Which feature?",
            answerable=True,
            answer_criteria="TF-IDF",
            supporting_evidence=["gold"],
            answer="wrong words",
            status="answered",
            citation_ids=["other"],
            trace={
                "packed_ids": ["other", "gold"],
                "packed_evidence": {"E1": "Title\nwrong words", "E2": "Title\nTF-IDF"},
            },
        ),
        dict(
            query_id="b",
            family_id="paper2",
            question="Unknown?",
            answerable=False,
            answer_criteria="Unanswerable",
            supporting_evidence=[],
            answer="",
            status="refused",
            citation_ids=[],
            trace={"packed_ids": [], "packed_evidence": {}},
        ),
    ]


def test_separate_cited_from_available_evidence_and_oracle_is_diagnostic():
    m = module()
    r = m.analyze(rows(), [{"query_id": "a", "verdict": "UNSUPPORTED"}])
    case = r["cases"][0]
    assert case["citation_has_gold_id"] is False
    assert case["packed_has_gold_id"] is True
    assert case["source_span_match"] is True
    assert case["answer_f1"] == 0
    assert case["best_packed_span_f1"] == 1
    assert r["scope"] == "post-hoc diagnostic; no selection or revised scores"


@pytest.mark.parametrize("change", ["missing", "duplicate", "extra", "invalid_verdict"])
def test_exact_decision_roster(change):
    m = module()
    decisions = [{"query_id": "a", "verdict": "SUPPORTED"}]
    if change == "missing":
        decisions = []
    elif change == "duplicate":
        decisions *= 2
    elif change == "extra":
        decisions.append({"query_id": "b", "verdict": "SUPPORTED"})
    else:
        decisions[0]["verdict"] = "YES"
    with pytest.raises(ValueError):
        m.analyze(rows(), decisions)


def test_f1_uses_all_answerable_rows_and_keeps_original_rows_unchanged():
    m = module()
    original = rows()
    original[0]["answer"] = "TF-IDF"
    original[0]["citation_ids"] = ["gold"]
    refused = copy.deepcopy(original[0])
    refused.update(query_id="c", status="refused", answer="", citation_ids=[])
    original.append(refused)
    before = copy.deepcopy(original)
    r = m.analyze(original, [{"query_id": "a", "verdict": "UNSUPPORTED"}])
    assert r["removed_f1_contribution"] == 0.5
    assert r["original_f1"] == 0.5
    assert r["retained_f1"] == 0
    assert original == before


def test_duplicate_rows_and_invalid_citation_are_rejected():
    m = module()
    original = rows()
    with pytest.raises(ValueError):
        m.analyze(original + [original[0]], [])
    original[0]["citation_ids"] = ["missing"]
    with pytest.raises(ValueError):
        m.analyze(original, [{"query_id": "a", "verdict": "SUPPORTED"}])


def test_persist_never_overwrites_different_audit(tmp_path):
    m = module()
    p = tmp_path / "result.json"
    m.persist(p, {"v": 1}, False)
    m.persist(p, {"v": 1}, True)
    with pytest.raises(ValueError):
        m.persist(p, {"v": 2}, False)
    with pytest.raises(FileNotFoundError):
        m.persist(tmp_path / "missing", {}, True)
