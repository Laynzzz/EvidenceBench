import json

import pytest

from evidencebench.generation_selection import (
    ChoiceConstraint,
    build_options,
    resolve_choice,
)


def test_generator_constructs_json_and_honors_context_timeout(monkeypatch):
    import sys
    from contextlib import nullcontext
    from types import SimpleNamespace

    from evidencebench.generation_selection import SelectionGenerator

    monkeypatch.setitem(sys.modules, "torch", SimpleNamespace(inference_mode=nullcontext))

    class Tokens(list):
        shape = (1, 2)

    class Tokenizer:
        eos_token_id = 99

        def apply_chat_template(self, *args, **kwargs):
            return {"input_ids": Tokens([[88, 89]])}

        def encode(self, text, **kwargs):
            return [int(text)]

        def decode(self, tokens, **kwargs):
            return "".join(str(t) for t in tokens if t != 99)

    def generate(**kwargs):
        allowed = kwargs["prefix_allowed_tokens_fn"]
        assert allowed(0, [88, 89]) == [0, 1]
        assert allowed(0, [88, 89, 1]) == [99]
        assert kwargs["max_new_tokens"] == 2
        return [[88, 89, 1, 99]]

    generator = object.__new__(SelectionGenerator)
    generator.tokenizer = Tokenizer()
    generator.model = SimpleNamespace(generate=generate)
    generator.config = {"max_input_tokens": 20, "timeout_seconds": 20}
    packed = {"E1": "The baseline uses random assignment."}
    assert generator.generate("What baseline?", packed)["answer"] == packed["E1"]
    generator.config["max_input_tokens"] = 1
    assert generator.generate("What baseline?", packed)["reason"] == "no_eligible_options"
    generator.config["max_input_tokens"] = 20
    ticks = iter([0, 21])
    monkeypatch.setattr("evidencebench.generation_selection.time.perf_counter", lambda: next(ticks))
    assert generator.generate("What baseline?", packed)["reason"] == "generation_timeout"


def test_options_copy_only_body_sentences_with_correct_citations():
    packed = {
        "E1": "A paper title\nThe baseline assigns categories randomly. It reports macro F1.",
        "E2": "A paper title\nThe trained model uses a linear classifier.",
    }
    options = build_options("Which baseline was used?", packed)
    assert [o["evidence_id"] for o in options[:3]] == ["E1", "E2", "E1"]
    assert all(o["answer"] in packed[o["evidence_id"]] for o in options)
    assert not any("title" in o["answer"] for o in options)
    result = resolve_choice("1", options, packed, "Which baseline was used?")
    assert result["answer"] == "The baseline assigns categories randomly."
    assert result["evidence_ids"] == ["E1"]
    assert result["grounding_check"] == "exact_quote"


def test_boolean_options_have_source_sentence_and_open_questions_do_not():
    packed = {"E1": "This method uses pretrained word vectors."}
    options = build_options("Are pretrained vectors used?", packed)
    assert {o["answer"] for o in options} == {"Yes", "No"}
    assert all(o["support_quote"] == packed["E1"] for o in options)
    assert (
        resolve_choice("1", options, packed, "Are pretrained vectors used?")["grounding_check"]
        == "citation_references_only"
    )
    with pytest.raises(ValueError, match="boolean"):
        resolve_choice("1", options, packed, "Which vectors are used?")


def test_refusal_invalid_choice_and_no_fabricated_citation():
    packed = {"E1": "The method uses a linear classifier."}
    options = build_options("What method?", packed)
    assert resolve_choice("0", options, packed, "What method?")["refused"]
    for invalid in ["2", "-1", "1 extra", json.dumps({"choice": 1})]:
        with pytest.raises(ValueError):
            resolve_choice(invalid, options, packed, "What method?")
    with pytest.raises(ValueError):
        resolve_choice("1", options, {}, "What method?")


def test_no_partial_sentence_or_standalone_placeholder_options():
    packed = {"E1": "Title\nBIBREF5. " + "long " * 120 + ". A useful complete sentence follows."}
    options = build_options("What method?", packed)
    assert [o["answer"] for o in options] == ["A useful complete sentence follows."]


def test_constraint_allows_only_exact_paths_and_eos():
    constraint = ChoiceConstraint([[10], [11, 12], [11, 13]], prompt_length=2, eos_id=99)
    assert constraint(0, [88, 89]) == [10, 11]
    assert constraint(0, [88, 89, 11]) == [12, 13]
    assert constraint(0, [88, 89, 10]) == [99]
    with pytest.raises(ValueError, match="prefix"):
        constraint(0, [88, 89, 14])
