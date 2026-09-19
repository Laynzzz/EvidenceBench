import math

import pytest


def test_metrics_match_hand_calculated_graded_example():
    from evidencebench.evaluation.metrics import score_ranking

    result = score_ranking(["noise", "b", "a"], {"a": 2, "b": 1, "c": 2}, k=3)
    assert result["recall"] == pytest.approx(2 / 3)
    assert result["mrr"] == 0.5
    assert result["ndcg"] == pytest.approx(
        (1 / math.log2(3) + 3 / 2) / (3 + 3 / math.log2(3) + 1 / 2)
    )


def test_missing_predictions_score_zero_and_unanswerable_is_separate():
    from evidencebench.evaluation.metrics import score_ranking

    assert score_ranking([], {"a": 2}, k=10) == dict(recall=0.0, mrr=0.0, ndcg=0.0)
    assert score_ranking(["a"], {}, k=10) is None
    with pytest.raises(ValueError, match="duplicate"):
        score_ranking(["a", "a"], {"a": 2}, k=10)


def test_bootstrap_pairs_on_family_and_is_seeded():
    from evidencebench.evaluation.metrics import paired_family_bootstrap

    rows = [
        {"family_id": "a", "baseline": 0.1, "candidate": 0.3},
        {"family_id": "a", "baseline": 0.2, "candidate": 0.4},
        {"family_id": "b", "baseline": 0.3, "candidate": 0.5},
    ]
    report = paired_family_bootstrap(rows, samples=100, seed=42)
    assert report["delta"] == pytest.approx(0.2)
    assert report["low"] == pytest.approx(0.2)
    assert report["high"] == pytest.approx(0.2)
    assert report["family_count"] == 2
    assert report == paired_family_bootstrap(rows, samples=100, seed=42)
