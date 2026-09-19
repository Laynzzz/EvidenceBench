import pytest


def test_token_f1_and_refusal_denominators():
    from evidencebench.evaluation.answers import answer_metrics, token_f1

    assert token_f1("The Adam optimizer", "Adam") == pytest.approx(2 / 3)
    rows = [
        {
            "answerable": True,
            "answer_criteria": "Adam",
            "status": "refused",
            "answer": "",
            "citation_ids": [],
            "supporting_evidence": ["a"],
            "elapsed_ms": 10,
        },
        {
            "answerable": False,
            "answer_criteria": "Unanswerable",
            "status": "refused",
            "answer": "",
            "citation_ids": [],
            "supporting_evidence": [],
            "elapsed_ms": 20,
        },
    ]
    metrics = answer_metrics(rows)
    assert metrics["answerable_token_f1"] == 0
    assert metrics["answer_coverage"] == 0
    assert metrics["false_refusal_rate"] == 1
    assert metrics["unanswerable_refusal_recall"] == 1


def test_threshold_uses_answerability_and_prefers_coverage_on_ties():
    from evidencebench.evaluation.answers import calibrate_threshold

    result = calibrate_threshold([(0.9, True), (0.8, True), (0.2, False), (0.1, False)])
    assert result["balanced_accuracy"] == 1
    assert 0.2 < result["threshold"] <= 0.8
