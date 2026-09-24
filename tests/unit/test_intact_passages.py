import copy
import importlib.util
import json
from pathlib import Path

import pytest


def load(name):
    path = Path("scripts") / f"{name}.py"
    assert path.exists(), "intact-passage component not implemented"
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def payload():
    return dict(query_id="q", question="Which method?", evidence={"E1": "Title\n" + "a " * 600})


def test_intact_contract_preserves_body_and_frozen_prompt():
    new, old = load("intact_passage_contract"), load("span_id_answer_contract")
    p = payload()
    original = copy.deepcopy(p)
    new.validate_payloads([p], 1)
    rendered = new.messages(p)
    assert rendered[0]["content"] == old.SYSTEM
    assert len(new.catalog(p["evidence"])) == 15
    assert p == original
    sid, span = list(new.catalog(p["evidence"]).items())[-1]
    parsed = new.parse(json.dumps(dict(answer="a", span_ids=[sid])), p["evidence"])
    assert parsed["citations"][0]["quote"] == span["quote"]
    with pytest.raises(ValueError, match="clipped"):
        old.messages(p)


@pytest.mark.parametrize("mutation", ["labels", "too_long", "empty_body", "bad_alias", "duplicate"])
def test_intact_contract_rejects_bad_or_labelled_inputs(mutation):
    m = load("intact_passage_contract")
    p = payload()
    if mutation == "labels":
        p["answer_criteria"] = "SECRET"
    if mutation == "too_long":
        p["evidence"]["E1"] = "Title\n" + "a" * 4096
    if mutation == "empty_body":
        p["evidence"]["E1"] = "Title only"
    if mutation == "bad_alias":
        p["evidence"] = {"E2": "Title\nText."}
    rows = [p, p] if mutation == "duplicate" else [p]
    with pytest.raises(ValueError):
        m.validate_payloads(rows, len(rows))
