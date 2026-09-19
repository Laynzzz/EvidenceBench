"""Validate quoted spans and references; this does not establish semantic relevance."""

import json
import re

from pydantic import Field

from evidencebench.chunking import normalize
from evidencebench.schemas import Record


class DraftAnswer(Record):
    answer: str = Field(max_length=2000)
    evidence_ids: list[str] = Field(max_length=3)


def validate_answer(raw: str, packed: dict[str, str], query: str = "") -> dict:
    draft = DraftAnswer.model_validate(json.loads(raw))
    if not draft.answer and not draft.evidence_ids:
        return {"answer": "", "evidence_ids": [], "refused": True}
    if not draft.answer or not draft.evidence_ids or set(draft.evidence_ids) - packed.keys():
        raise ValueError("invalid citation references")
    if len(set(draft.evidence_ids)) != len(draft.evidence_ids):
        raise ValueError("duplicate citation references")
    if draft.answer in {"Yes", "No"}:
        question = query.rsplit("', ", 1)[-1].strip()
        if not re.match(
            r"(?i)^(is|are|was|were|do|does|did|has|have|had|can|could|will|would|should)\b",
            question,
        ):
            raise ValueError("boolean answer requires a boolean question")
        return {
            **draft.model_dump(),
            "refused": False,
            "grounding_check": "citation_references_only",
        }
    if any(normalize(draft.answer) not in normalize(packed[key]) for key in draft.evidence_ids):
        raise ValueError("answer is not a quote in each cited passage")
    return {**draft.model_dump(), "refused": False, "grounding_check": "exact_quote"}
