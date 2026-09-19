import pytest
from pydantic import ValidationError


def test_family_versions_cannot_cross_splits(pdf_source):
    from evidencebench.schemas import CorpusManifest

    _, source = pdf_source
    other = dict(
        source,
        document_id="backup-v2",
        version="2",
        split="test",
        sha256="b" * 64,
        url="https://example.org/manual-v2.pdf",
    )
    with pytest.raises(ValueError, match="family"):
        CorpusManifest.model_validate({"sources": [source, other]})


def test_duplicate_source_rejected_even_under_a_different_id(pdf_source):
    from evidencebench.schemas import CorpusManifest

    _, source = pdf_source
    with pytest.raises(ValueError, match="duplicate"):
        CorpusManifest.model_validate({"sources": [source, dict(source, document_id="copy")]})


def test_invalid_page_and_checksum_rejected(pdf_source):
    from evidencebench.schemas import SourceDocument

    _, source = pdf_source
    with pytest.raises(ValidationError):
        SourceDocument.model_validate(dict(source, page_count=0))
    with pytest.raises(ValidationError):
        SourceDocument.model_validate(dict(source, sha256="not-a-checksum"))


def test_chunking_preserves_all_words_without_crossing_pages():
    from evidencebench.chunking import chunk_words

    words = [dict(text=str(i), x0=10, top=20, x1=20, bottom=30) for i in range(9)]
    chunks = chunk_words(words, max_words=4, overlap=1)
    assert [c[0] for c in chunks] == ["0 1 2 3", "3 4 5 6", "6 7 8"]
    assert chunks[0][1] == (10, 20, 20, 30)
    with pytest.raises(ValueError):
        chunk_words(words, max_words=4, overlap=4)


def test_query_cannot_claim_answerable_without_evidence():
    from evidencebench.schemas import QueryExample

    with pytest.raises(ValueError, match="evidence"):
        QueryExample.model_validate(
            dict(
                query_id="q1",
                text="How do backups work?",
                split="dev",
                family_id="backup",
                query_type="fact",
                relevance={},
                answerable=True,
                answer_criteria="Daily backups",
                supporting_evidence=[],
                label_provenance="agent-draft",
                review_status="draft",
            )
        )
