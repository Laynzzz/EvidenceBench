import importlib.util
import json
from pathlib import Path

import pytest


def load(name):
    path = Path("scripts") / f"{name}.py"
    assert path.exists(), "span-ID preparation not implemented"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def evidence():
    return {
        "E1": "Paper title\nWe compared SVM.  Logistic regression also ran.",
        "E2": "Another title\nThe best model was CNN.",
    }


def response():
    return {"answer": "SVM, logistic regression and CNN.", "span_ids": ["E1.S1", "E1.S2", "E2.S1"]}


def test_catalog_preserves_body_offsets_and_covers_all_words():
    c = load("span_id_answer_contract")
    text = "First sentence.\n\n" + " ".join(f"词{i}" for i in range(99)) + " incomplete"
    ev = {"E1": "Never cite this title\n" + text}
    catalog = c.catalog(ev)
    assert list(catalog) == ["E1.S1", "E1.S2", "E1.S3", "E1.S4"]
    for span in catalog.values():
        assert span["quote"] == text[span["start"] : span["end"]]
        assert 0 < len(span["quote"].split()) <= 40
        assert span["evidence_id"] == "E1"
    assert " ".join(s["quote"] for s in catalog.values()).split() == text.split()
    assert catalog == c.catalog(ev)
    assert c.catalog({"E1": "Title only"}) == {}


def test_selected_ids_produce_exact_quotes_and_unique_evidence_ids():
    c = load("span_id_answer_contract")
    parsed = c.parse(json.dumps(response()), evidence())
    assert parsed["evidence_ids"] == ["E1", "E2"]
    assert parsed["citations"] == [
        {"span_id": "E1.S1", "evidence_id": "E1", "quote": "We compared SVM."},
        {"span_id": "E1.S2", "evidence_id": "E1", "quote": "Logistic regression also ran."},
        {"span_id": "E2.S1", "evidence_id": "E2", "quote": "The best model was CNN."},
    ]
    assert parsed["citation_check"] == "exact_quote_presence_only"
    assert not parsed["refused"]
    assert c.parse('{"answer":"","span_ids":[]}', {})["refused"]


@pytest.mark.parametrize(
    "value",
    [
        {"answer": "x", "span_ids": ["E3.S1"]},
        {"answer": "x", "span_ids": ["E1.S1", "E1.S1"]},
        {"answer": "x", "span_ids": []},
        {"answer": "", "span_ids": ["E1.S1"]},
        {"answer": " x ", "span_ids": ["E1.S1"]},
        {"answer": " ".join(["x"] * 81), "span_ids": ["E1.S1"]},
        {"answer": "x", "span_ids": [True]},
        {"answer": "x", "span_ids": ["E1.S1"], "quote": "invented"},
        {"answer": "x", "span_ids": ["E1.S1"] * 4},
        [],
    ],
)
def test_invalid_contract_is_rejected(value):
    with pytest.raises(ValueError):
        load("span_id_answer_contract").parse(json.dumps(value), evidence())


def test_no_json_repair_or_semantic_claim():
    c = load("span_id_answer_contract")
    for raw in [
        "```json\n" + json.dumps(response()) + "\n```",
        json.dumps(response()) + "```",
        '{"answer":"x","answer":"","span_ids":[]}',
    ]:
        with pytest.raises(ValueError):
            c.parse(raw, evidence())
    assert (
        c.parse('{"answer":"Unknown meaning","span_ids":["E1.S1"]}', evidence())["citation_check"]
        == "exact_quote_presence_only"
    )


def test_messages_use_only_question_title_and_catalog():
    c = load("span_id_answer_contract")
    payload = {"query_id": "SECRET_ID", "question": "Which models?", "evidence": evidence()}
    c.validate_payloads([payload], 1)
    msg = c.messages(payload)
    assert "SECRET_ID" not in json.dumps(msg)
    content = json.loads(msg[1]["content"])
    assert content["question"] == payload["question"]
    assert content["evidence"]["E1"]["title"] == "Paper title"
    assert content["evidence"]["E1"]["spans"]["E1.S1"] == "We compared SVM."
    with pytest.raises(ValueError):
        c.validate_payloads([{**payload, "answer_criteria": "leak"}], 1)


def test_quote_budget_holds_without_model_copying():
    c = load("span_id_answer_contract")
    ev = {"E1": "Title\n" + " ".join(f"word{i}" for i in range(150))}
    p = c.parse(json.dumps({"answer": "Summary", "span_ids": ["E1.S1", "E1.S2", "E1.S3"]}), ev)
    assert sum(len(s["quote"].split()) for s in p["citations"]) == 120
    assert p["evidence_ids"] == ["E1"]
