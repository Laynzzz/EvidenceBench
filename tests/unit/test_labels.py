import pytest
from test_retrieval import make_units


def example(**changes):
    from evidencebench.schemas import QueryExample

    values = dict(
        query_id="q",
        text="How should backup files be protected?",
        split="train",
        family_id="backup",
        query_type="fact",
        relevance={"a": 2},
        answerable=True,
        answer_criteria="Encrypt them",
        supporting_evidence=["a"],
        label_provenance="test-fixture",
        review_status="draft",
    )
    return QueryExample.model_validate(values | changes)


def test_labels_reject_missing_references_and_training_leakage():
    from evidencebench.labels import validate_labels

    with pytest.raises(ValueError, match="unknown"):
        validate_labels(
            [example(relevance={"missing": 2}, supporting_evidence=["missing"])], make_units()
        )
    units = make_units()
    units[0] = units[0].model_copy(update={"split": "dev"})
    with pytest.raises(ValueError, match="split"):
        validate_labels([example()], units)


def test_duplicate_query_text_and_unreviewed_evaluation_are_rejected():
    from evidencebench.labels import validate_labels

    with pytest.raises(ValueError, match="duplicate query"):
        validate_labels(
            [example(), example(query_id="q2", text="HOW should backup files be protected?")],
            make_units(),
        )
    units = [u.model_copy(update={"split": "dev"}) for u in make_units()]
    with pytest.raises(ValueError, match="human"):
        validate_labels([example(split="dev")], units)
    result = validate_labels([example(split="dev")], units, allow_drafts=True)
    assert result["reviewed_evaluation_count"] == 0
    assert result["query_count"] == 1


def test_negative_mining_never_uses_eval_content_or_known_positive():
    from evidencebench.labels import mine_negatives

    units = make_units()
    units[1] = units[1].model_copy(update={"split": "test"})
    negatives = mine_negatives(example(), units, count=1, seed=7, method="random")
    assert negatives == ["c"]
    assert mine_negatives(example(), units, count=1, seed=7, method="hard") == ["c"]
