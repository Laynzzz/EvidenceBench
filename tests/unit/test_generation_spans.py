import pytest

from evidencebench.generation_spans import SpanTrie, build_spans, resolve_span


def test_short_span_and_number_keep_source_provenance():
    packed = {
        "E1": "Paper title\nThe mean length was 12.7 words. Adam was used.",
        "E2": "Other title\nAdam was compared to another optimizer.",
    }
    spans = build_spans(packed)
    assert "12.7" in spans and "Adam" in spans
    assert "Paper title" not in spans
    result = resolve_span("Adam", packed, "Which optimizer?", spans)
    assert result["answer"] == "Adam" and result["evidence_ids"] == ["E1"]
    with pytest.raises(ValueError):
        resolve_span("RMSProp", packed, "Which optimizer?", spans)


def test_catalog_excludes_placeholders_and_cut_word_but_keeps_complete_short_spans():
    packed = {"E1": "Title\nWe used BIBREF16 and Adam optimiz"}
    spans = build_spans(packed, clipped_length=len(packed["E1"]))
    assert "Adam" in spans
    assert not any("BIBREF" in s or "optimiz" in s for s in spans)


def test_boolean_needs_boolean_question_and_valid_alias():
    packed = {"E1": "We used pretrained word embeddings."}
    assert (
        resolve_span("Yes | E1", packed, "Are pretrained vectors used?", {})["grounding_check"]
        == "citation_references_only"
    )
    for raw, query in [("Yes | E9", "Are vectors used?"), ("Yes | E1", "Which vectors?")]:
        with pytest.raises(ValueError):
            resolve_span(raw, packed, query, {})
    assert resolve_span("UNKNOWN", packed, "Which vectors?", {})["refused"]


def test_trie_supports_shared_prefix_terminal_and_invalid_path():
    trie = SpanTrie([[1], [1, 2], [3, 4]], prompt_length=2, eos_id=99)
    assert trie(0, [88, 89]) == [1, 3]
    assert trie(0, [88, 89, 1]) == [2, 99]
    assert trie(0, [88, 89, 3]) == [4]
    with pytest.raises(ValueError, match="prefix"):
        trie(0, [88, 89, 7])


def test_punctuation_normalization_does_not_change_decimal_values():
    packed = {"E1": "We set the threshold to .5 and measured 12.7 points."}
    spans = build_spans(packed)
    assert resolve_span('"12.7".', packed, "What score?", spans)["answer"] == "12.7"
    assert resolve_span(".5", packed, "What threshold?", spans)["answer"] == ".5"


def test_generator_runs_all_modes_and_keeps_context_and_timeout_guards(monkeypatch):
    import sys
    from contextlib import nullcontext
    from types import SimpleNamespace

    from evidencebench.generation_spans import SpanGenerator

    monkeypatch.setitem(sys.modules, "torch", SimpleNamespace(inference_mode=nullcontext))

    class Tokens(list):
        shape = (1, 2)

    class Tokenizer:
        eos_token_id = 99999

        def apply_chat_template(self, messages, **kwargs):
            self.messages = messages
            return {"input_ids": Tokens([[88, 89]])}

        def __call__(self, texts, **kwargs):
            self.ids = {text: i + 1 for i, text in enumerate(texts)}
            return {"input_ids": [[i] for i in self.ids.values()]}

        def decode(self, tokens, **kwargs):
            return "Adam"

    tokenizer = Tokenizer()

    def generate(**kwargs):
        if "prefix_allowed_tokens_fn" in kwargs:
            token = tokenizer.ids["Adam"]
            assert token in kwargs["prefix_allowed_tokens_fn"](0, [88, 89])
        return [[88, 89, 1, 99999]]

    generator = object.__new__(SpanGenerator)
    generator.tokenizer = tokenizer
    generator.model = SimpleNamespace(generate=generate)
    generator.config = {"variant": "plain", "max_input_tokens": 30, "timeout_seconds": 20}
    query = "In the paper 'A title', Which optimizer?"
    packed = {"E1": "A title\nWe used Adam for training."}
    for variant in ("plain", "constrained", "focused"):
        generator.config["variant"] = variant
        assert generator.generate(query, packed)["evidence_ids"] == ["E1"]
        question_line = tokenizer.messages[1]["content"].splitlines()[0]
        assert ("A title" not in question_line) == (variant == "focused")
    generator.config["max_input_tokens"] = 1
    assert generator.generate(query, packed)["reason"] == "context_limit"
    generator.config["max_input_tokens"] = 30
    ticks = iter([0, 21])
    monkeypatch.setattr("evidencebench.generation_spans.time.perf_counter", lambda: next(ticks))
    assert generator.generate(query, packed)["reason"] == "generation_timeout"
