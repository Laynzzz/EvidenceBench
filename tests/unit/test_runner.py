import json

import pytest
from test_labels import example
from test_retrieval import make_units


def test_runner_records_failures_and_recalculates_metrics(tmp_path):
    from evidencebench.evaluation.runner import evaluate, recalculate
    from evidencebench.retrieval import BM25Retriever

    units = [u.model_copy(update={"split": "dev"}) for u in make_units()]
    labels = [example(split="dev", review_status="human-reviewed")]

    class Broken:
        def retrieve(self, query, filters, k):
            raise TimeoutError("deadline")

    run = evaluate(
        labels,
        units,
        {"bm25": BM25Retriever(units), "broken": Broken()},
        tmp_path,
        corpus_fingerprint="a" * 64,
    )
    report = json.loads((run / "metrics.json").read_text())
    # The shorter backup passage ranks first; the judged positive is second.
    assert report["bm25"]["ndcg_at_10"] == pytest.approx(0.6309297535714574)
    assert report["broken"]["ndcg_at_10"] == 0.0
    assert report["broken"]["failure_count"] == 1
    assert recalculate(run) == report
    assert (run / "manifest.json").is_file()


def test_runner_refuses_test_set_and_unreviewed_development(tmp_path):
    from evidencebench.evaluation.runner import evaluate
    from evidencebench.retrieval import BM25Retriever

    for split in ("dev", "test"):
        units = [u.model_copy(update={"split": split}) for u in make_units()]
        with pytest.raises(ValueError):
            evaluate(
                [example(split=split)],
                units,
                {"bm25": BM25Retriever(units)},
                tmp_path,
                corpus_fingerprint="a" * 64,
            )
