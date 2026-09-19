import json
from types import SimpleNamespace

import pytest

from evidencebench.evaluation.fresh_comparison import (
    Budget,
    MeteredModel,
    compare_queries,
    summarize,
)
from evidencebench.schemas import RankedEvidence


def test_budget_persists_before_work_and_rejects_overrun_without_refund(tmp_path):
    budget = Budget(tmp_path / "usage.json", {"calls": 1})
    budget.charge("calls", 1)
    with pytest.raises(RuntimeError, match="budget"):
        budget.charge("calls", 1)
    assert json.loads((tmp_path / "usage.json").read_text())["used"] == {"calls": 1}
    with pytest.raises(FileExistsError):
        Budget(tmp_path / "usage.json", {"calls": 1})


def test_model_failure_still_consumes_call_and_reserved_tokens(tmp_path):
    class Broken:
        def generate(self, **kwargs):
            raise ValueError("synthetic model failure")

    budget = Budget(tmp_path / "usage.json", {"control_calls": 1, "reserved_tokens": 100})
    model = MeteredModel(Broken(), budget, "control", 100)
    with pytest.raises(ValueError):
        model.generate(max_new_tokens=100)
    assert budget.used == {"control_calls": 1, "reserved_tokens": 100}
    with pytest.raises(RuntimeError):
        model.generate(max_new_tokens=101)


def query(key="q", answerable=True):
    return SimpleNamespace(
        query_id=key,
        text="Synthetic question?",
        split="dev",
        family_id="paper",
        answerable=answerable,
        answer_criteria="SECRET REFERENCE",
        supporting_evidence=["gold"] if answerable else [],
    )


def test_paired_contexts_failures_and_refusals_keep_all_queries(tmp_path):
    calls = []

    class Retriever:
        pre = []

        def retrieve(self, text, filters, k):
            calls.append(("retrieve", text, filters, k))
            self.pre = [
                RankedEvidence(
                    element_id="gold", document_id="paper", page=1, rank=1, retrieval_score=1
                )
            ]
            return [self.pre[0].model_copy(update={"reranker_score": 4.0})]

    class Generator:
        last_output = ""

        def generate(self, text, packed):
            calls.append(("generate", text, dict(packed)))
            assert "SECRET REFERENCE" not in str((text, packed))
            return {
                "status": "answered",
                "answer": "source",
                "evidence_ids": ["E1"],
                "reason": None,
            }

    class Broken(Generator):
        def generate(self, text, packed):
            raise ValueError("synthetic generation failure")

    units = [SimpleNamespace(element_id="gold", text="Paper\nsource", family_id="paper")]
    rows = compare_queries(
        [query()],
        units,
        Retriever(),
        {"control": Generator(), "constrained": Broken()},
        lambda _: None,
        tmp_path,
        threshold=3.0,
    )
    assert len(rows["control"]) == len(rows["constrained"]) == 1
    assert rows["control"][0]["citation_ids"] == ["gold"]
    assert rows["constrained"][0]["status"] == "failure"
    assert len([c for c in calls if c[0] == "retrieve"]) == 1
    assert (
        rows["control"][0]["trace"]["packed_evidence"]
        == rows["constrained"][0]["trace"]["packed_evidence"]
    )
    refused = compare_queries(
        [query("r")],
        units,
        Retriever(),
        {"control": Generator(), "constrained": Generator()},
        lambda _: None,
        tmp_path / "refused",
        threshold=5.0,
    )
    assert all(r[0]["status"] == "refused" for r in refused.values())
    assert len([c for c in calls if c[0] == "generate"]) == 1


def test_test_split_rejected_before_retrieval_or_generation(tmp_path):
    q = query()
    q.split = "test"
    with pytest.raises(ValueError, match="development"):
        compare_queries([q], [], None, {}, lambda _: None, tmp_path, threshold=3.0)


def test_gate_fails_on_citation_regression_or_undefined_precision():
    def row(answer, cites):
        return dict(
            query_id="q",
            answerable=True,
            answer_criteria="gold answer",
            answer=answer,
            status="answered",
            citation_ids=cites,
            supporting_evidence=["gold"],
            elapsed_ms=1,
            trace={"pre_ids": ["gold"], "post_ids": ["gold"], "packed_ids": ["gold"]},
        )

    negative = {
        **row("", []),
        "query_id": "negative",
        "answerable": False,
        "supporting_evidence": [],
        "status": "refused",
    }
    result = summarize(
        {
            "control": [row("gold", ["gold"]), negative],
            "constrained": [row("gold answer", ["wrong"]), negative],
        }
    )
    assert result["constrained"]["answerable_token_f1"] > result["control"]["answerable_token_f1"]
    assert not result["passes_validation_gate"]
    result = summarize(
        {
            "control": [row("wrong", []), negative],
            "constrained": [row("gold answer", ["gold"]), negative],
        }
    )
    assert not result["passes_validation_gate"]
    assert summarize(
        {
            "control": [row("gold", ["gold"]), negative],
            "constrained": [row("gold answer", ["gold"]), negative],
        }
    )["passes_validation_gate"]


def test_reranker_failure_preserves_successful_pre_ranking(tmp_path):
    class BrokenRanker:
        pre = []

        def retrieve(self, *args):
            self.pre = [
                RankedEvidence(
                    element_id="gold", document_id="paper", page=1, rank=1, retrieval_score=1
                )
            ]
            raise ValueError("synthetic rerank failure")

    rows = compare_queries(
        [query()],
        [],
        BrokenRanker(),
        {"control": None, "constrained": None},
        lambda _: None,
        tmp_path,
        threshold=3,
    )
    assert rows["control"][0]["trace"]["pre_ids"] == ["gold"]
    assert all(r[0]["status"] == "failure" for r in rows.values())
