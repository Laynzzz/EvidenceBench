import pytest


def make_units():
    from evidencebench.schemas import ContentUnit

    base = dict(
        version="1",
        split="train",
        page=1,
        source_checksum="a" * 64,
        source_url="https://example.org/manual.pdf",
    )
    return [
        ContentUnit(
            element_id="a",
            document_id="a",
            family_id="backup",
            text="Encrypt backup files before storage",
            **base,
        ),
        ContentUnit(
            element_id="b",
            document_id="b",
            family_id="network",
            text="Monitor wireless network access points",
            **base,
        ),
        ContentUnit(
            element_id="c",
            document_id="c",
            family_id="backup",
            text="Restore backup files monthly",
            **base,
        ),
    ]


def test_bm25_ranks_matching_evidence_and_applies_explicit_filters():
    from evidencebench.retrieval import BM25Retriever

    retriever = BM25Retriever(make_units())
    assert retriever.retrieve("encrypt storage", {}, 2)[0].element_id == "a"
    assert retriever.retrieve("encrypt storage", {"family_id": "network"}, 2) == []
    assert retriever.retrieve("", {}, 2) == []
    assert retriever.retrieve("nonexistent", {}, 2) == []
    with pytest.raises(ValueError):
        retriever.retrieve("backup", {}, 0)
    with pytest.raises(ValueError):
        retriever.retrieve("backup", {"gold": "a"}, 2)


def test_fusion_uses_ranks_not_incompatible_scores_and_deduplicates():
    from evidencebench.retrieval import reciprocal_rank_fusion
    from evidencebench.schemas import RankedEvidence

    def hit(key, rank, score):
        return RankedEvidence(
            element_id=key, document_id=key, page=1, rank=rank, retrieval_score=score
        )

    result = reciprocal_rank_fusion(
        [[hit("a", 1, 1000), hit("b", 2, 1)], [hit("b", 1, 0.9), hit("c", 2, 0.8)]], k=3
    )
    assert [x.element_id for x in result] == ["b", "a", "c"]
    assert result[0].retrieval_score == pytest.approx(1 / 62 + 1 / 61)
    with pytest.raises(ValueError, match="duplicate"):
        reciprocal_rank_fusion([[hit("a", 1, 1), hit("a", 2, 1)]], k=2)


def test_dense_ranking_and_filters_use_query_vector_not_document_order():
    import numpy as np

    from evidencebench.retrieval import DenseRetriever

    retriever = DenseRetriever(
        make_units(),
        np.array([[1.0, 0.0], [0.0, 1.0], [0.8, 0.2]]),
        lambda query: np.array([0.0, 1.0]),
    )
    assert retriever.retrieve("wireless", {}, 3)[0].element_id == "b"
    assert all(
        x.element_id != "b" for x in retriever.retrieve("wireless", {"family_id": "backup"}, 3)
    )
    with pytest.raises(ValueError):
        DenseRetriever(make_units(), np.zeros((3, 2)), lambda q: np.ones(2))
