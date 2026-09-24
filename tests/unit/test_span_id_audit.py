import importlib.util
from pathlib import Path

import pytest


def audit():
    p = Path("scripts/audit_span_id_evidence.py")
    assert p.exists(), "offline evidence audit not implemented"
    s = importlib.util.spec_from_file_location("audit", p)
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


def row():
    full = "Title\n" + "a " * 494 + "personal attack, racism and sexism."
    return dict(
        query_id="q",
        question="Which topics?",
        answerable=True,
        status="answered",
        reason=None,
        answer="perso",
        citation_ids=["g"],
        supporting_evidence=["g"],
        answer_quotes=[
            {"span_id": "E1.S1", "evidence_id": "E1", "quote": full[:1000].partition("\n")[2][-8:]}
        ],
        trace={
            "pre_ranking": [{"element_id": "g"}],
            "post_ranking": [{"element_id": "g", "reranker_score": 4.0}],
            "packed_ids": ["g"],
            "packed_evidence": {"E1": full[:1000]},
        },
    ), {"g": {"text": full, "split": "dev"}}


def test_actual_clipping_and_boundary_cut_are_distinct_from_semantics():
    m = audit()
    r, u = row()
    out = m.analyze([r], u)
    c = out["cases"][0]
    assert c["evidence_path"] == "gold_cited_semantics_unproven"
    assert c["passages"][0]["clipped"] and c["passages"][0]["cut_inside_alphanumeric_word"]
    assert c["passages"][0]["cited"] and c["passages"][0]["gold_id"]
    assert out["summary"]["clipped_passage_occurrences"] == 1
    assert c["passages"][0]["omitted_characters"] == len(u["g"]["text"]) - 1000
    assert "semantic_support" not in c


def test_refusal_causes_and_gold_ranks_are_preserved():
    m = audit()
    r, u = row()
    r.update(
        status="refused",
        reason="insufficient_evidence",
        answer="",
        citation_ids=[],
        answer_quotes=[],
    )
    r["trace"].update(packed_ids=[], packed_evidence={})
    c = m.analyze([r], u)["cases"][0]
    assert c["evidence_path"] == "threshold_blocks_top3_gold"
    assert c["post_first_gold_rank"] == 1 and c["pre_first_gold_rank"] == 1
    assert c["gold_in_post_top3"] == 1 and c["gold_in_packed"] == 0
    assert c["passages"] == []


def test_gold_absence_does_not_become_semantic_judgment():
    m = audit()
    r, u = row()
    r["supporting_evidence"] = ["other"]
    c = m.analyze([r], u)["cases"][0]
    assert c["evidence_path"] == "no_gold_in_retrieved_roster"
    assert c["post_first_gold_rank"] is None
    r.update(answerable=False, supporting_evidence=[])
    c = m.analyze([r], u)["cases"][0]
    assert c["evidence_path"] == "benchmark_unanswerable"


def test_reranking_and_citation_selection_losses_are_separate():
    m = audit()
    r, u = row()
    r["trace"]["pre_ranking"] = [{"element_id": x} for x in ["g", "b", "c", "d"]]
    r["trace"]["post_ranking"] = [
        {"element_id": x, "reranker_score": 4.0} for x in ["b", "c", "d", "g"]
    ]
    r["trace"].update(packed_ids=[], packed_evidence={})
    r.update(status="refused", reason="insufficient_evidence", citation_ids=[], answer_quotes=[])
    assert m.analyze([r], u)["cases"][0]["evidence_path"] == "gold_below_top3"
    r, u = row()
    r["citation_ids"] = []
    r["answer_quotes"] = []
    assert m.analyze([r], u)["cases"][0]["evidence_path"] == "gold_packed_but_not_cited"


@pytest.mark.parametrize(
    "mutation", ["duplicate_query", "altered_clip", "missing_unit", "wrong_alias", "nondev"]
)
def test_invalid_provenance_rejected(mutation):
    m = audit()
    r, u = row()
    rows = [r]
    if mutation == "duplicate_query":
        rows.append(r)
    if mutation == "altered_clip":
        r["trace"]["packed_evidence"]["E1"] = "Changed source"
    if mutation == "missing_unit":
        u = {}
    if mutation == "wrong_alias":
        r["trace"]["packed_evidence"] = {"E2": r["trace"]["packed_evidence"]["E1"]}
    if mutation == "nondev":
        u["g"]["split"] = "test"
    with pytest.raises(ValueError):
        m.analyze(rows, u)


def test_short_passage_and_punctuation_boundary_not_midword():
    m = audit()
    r, u = row()
    u["g"]["text"] = "Title\nA complete sentence."
    r["trace"]["packed_evidence"]["E1"] = u["g"]["text"]
    r["answer_quotes"] = []
    p = m.analyze([r], u)["cases"][0]["passages"][0]
    assert not p["clipped"] and not p["cut_inside_alphanumeric_word"]
