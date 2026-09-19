import pytest

from evidencebench.evaluation.development_audit import diagnose, reserve_families


def test_diagnosis_separates_context_absence_from_selection_and_duplicate_quotes():
    assert diagnose("cat", ["a"], {"a": "cat"}, ["g"]) == "gold_absent_from_context"
    assert diagnose("cat", ["a"], {"a": "cat", "g": "dog"}, ["g"]) == "gold_present_other_span"
    assert diagnose("cat", ["a"], {"a": "cat", "g": "cat"}, ["g"]) == "quote_also_in_gold"
    assert diagnose("cat", ["g"], {"g": "cat"}, ["g"]) == "gold_citation"


def test_boolean_is_not_treated_as_a_source_quote_and_no_gold_is_explicit():
    assert diagnose("Yes", ["a"], {"a": "Yes", "g": "Yes"}, ["g"]) == "boolean_wrong_citation"
    assert diagnose("cat", ["a"], {"a": "cat"}, []) == "unanswerable_answer"


def test_quote_matching_requires_whole_words_and_normalizes_whitespace():
    assert diagnose("cat", ["a"], {"a": "cat", "g": "category"}, ["g"]) == "gold_present_other_span"
    assert (
        diagnose("red cat", ["a"], {"a": "red cat", "g": "A red\ncat."}, ["g"])
        == "quote_also_in_gold"
    )


def test_unknown_citation_fails_instead_of_silently_classifying():
    with pytest.raises(ValueError, match="citation"):
        diagnose("cat", ["missing"], {"a": "cat"}, ["g"])


def test_reservation_is_disjoint_deterministic_and_excludes_previously_touched_families():
    first = reserve_families({"dev": ["a", "b", "c"], "test": ["d", "e"]}, {"b"}, 1, 1)
    second = reserve_families({"test": ["e", "d"], "dev": ["c", "b", "a"]}, {"b"}, 1, 1)
    assert first == second
    assert set(first["validation"]["primary"] + first["validation"]["fallback"]) == {"a", "c"}
    assert set(first["test"]["primary"] + first["test"]["fallback"]) == {"d", "e"}
    with pytest.raises(ValueError, match="overlap"):
        reserve_families({"dev": ["a"], "test": ["a"]}, set(), 1, 1)
    with pytest.raises(ValueError, match="enough"):
        reserve_families({"dev": ["a"], "test": ["b"]}, {"a"}, 1, 1)
