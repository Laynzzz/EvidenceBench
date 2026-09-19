import numpy as np
import pytest

from evidencebench.retrieval import BM25Retriever
from evidencebench.schemas import ContentUnit


def corpus():
    return [
        ContentUnit(
            element_id=str(i),
            document_id="paper",
            family_id="paper",
            version="1",
            split="train",
            page=1,
            text=text,
            source_checksum="a" * 64,
            source_url="https://example.org/paper.pdf",
        )
        for i, text in enumerate(["query short", "query long answer passage"])
    ]


def test_reranking_preserves_candidates_and_uses_scores():
    from evidencebench.reranking import RerankingRetriever

    units = corpus()

    class Encoder:
        def predict(self, pairs, **kwargs):
            return np.array([len(passage) for _, passage in pairs])

    retriever = RerankingRetriever(BM25Retriever(units), units, Encoder(), candidate_k=2)
    hits = retriever.retrieve("query", {}, 2)
    assert [h.element_id for h in hits] == ["1", "0"]
    assert hits[0].rank == 1 and hits[0].reranker_score > hits[1].reranker_score
    assert hits[0].retrieval_score > 0


def test_reranking_rejects_nonfinite_scores():
    from evidencebench.reranking import RerankingRetriever

    class Encoder:
        def predict(self, pairs, **kwargs):
            return np.full(len(pairs), np.nan)

    units = corpus()
    retriever = RerankingRetriever(BM25Retriever(units), units, Encoder(), candidate_k=2)
    with pytest.raises(ValueError, match="scores"):
        retriever.retrieve("query", {}, 2)


def test_cached_bm25_exclusion_matches_rebuilt_index():
    units = corpus()
    cached = BM25Retriever(units).excluding({"1"})
    rebuilt = BM25Retriever([units[0]])
    assert cached.retrieve("query", {}, 10) == rebuilt.retrieve("query", {}, 10)


def test_training_pairs_are_nested_and_cannot_consume_dev_labels():
    from evidencebench.schemas import QueryExample
    from evidencebench.training import prepare_pairs

    units = corpus()
    query = QueryExample(
        query_id="q",
        text="query",
        split="train",
        family_id="paper",
        query_type="fixture",
        relevance={"1": 2},
        answerable=True,
        supporting_evidence=["1"],
        answer_criteria="answer",
        label_provenance="fixture",
        review_status="human-reviewed",
    )
    rows = prepare_pairs([query], units, count=1, negatives=1, seed=42, method="hard")
    assert [row["label"] for row in rows] == [1.0, 0.0]
    assert rows[0]["element_id"] == "1" and rows[1]["element_id"] == "0"
    with pytest.raises(ValueError, match="training"):
        prepare_pairs([query.model_copy(update={"split": "dev"})], units, 1, 1, 42, "hard")
