import pytest


def test_quotes_must_come_from_cited_packed_evidence():
    from evidencebench.citations import validate_answer

    packed = {"E1": "The optimizer was Adam.", "E2": "We trained for ten epochs."}
    assert validate_answer('{"answer":"Adam", "evidence_ids":["E1"]}', packed)["answer"] == "Adam"
    with pytest.raises(ValueError, match="citation"):
        validate_answer('{"answer":"Adam", "evidence_ids":["E99"]}', packed)
    with pytest.raises(ValueError, match="quote"):
        validate_answer('{"answer":"Adafactor", "evidence_ids":["E1"]}', packed)
    with pytest.raises(ValueError, match="quote"):
        validate_answer('{"answer":"ten epochs", "evidence_ids":["E1"]}', packed)


def test_refusal_cannot_include_an_answer():
    from evidencebench.citations import validate_answer

    assert validate_answer('{"answer":"", "evidence_ids":[]}', {})["refused"]
    with pytest.raises(ValueError):
        validate_answer('{"answer":"unsupported", "evidence_ids":[]}', {})


def test_boolean_answers_require_citations_and_are_not_claimed_as_verified_quotes():
    from evidencebench.citations import validate_answer

    result = validate_answer(
        '{"answer":"Yes", "evidence_ids":["E1"]}',
        {"E1": "All identifying details were removed."},
        "In the paper 'Example', Is the data de-identified?",
    )
    assert result["grounding_check"] == "citation_references_only"
    with pytest.raises(ValueError, match="boolean"):
        validate_answer(
            '{"answer":"No", "evidence_ids":["E1"]}',
            {"E1": "Example"},
            "In the paper 'Example', What is the baseline?",
        )
