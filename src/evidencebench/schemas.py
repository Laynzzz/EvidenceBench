"""Validated boundaries shared by data preparation, evaluation, and serving."""

import math
from datetime import date
from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator

Identifier = Annotated[str, Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9_.-]*$")]
Checksum = Annotated[str, Field(pattern=r"^[a-f0-9]{64}$")]
Split = Literal["train", "dev", "test"]


class Record(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, frozen=True)


class SourceDocument(Record):
    document_id: Identifier
    family_id: Identifier
    version: str = Field(min_length=1)
    url: HttpUrl
    sha256: Checksum
    retrieved_at: date
    page_count: int = Field(gt=0, le=250)
    split: Split
    license: str = Field(min_length=1)
    mime_type: Literal["application/pdf"] = "application/pdf"


class CorpusManifest(Record):
    sources: list[SourceDocument] = Field(min_length=1)

    @model_validator(mode="after")
    def check_sources(self) -> Self:
        for field in ("document_id", "sha256", "url"):
            values = [getattr(s, field) for s in self.sources]
            if len(set(values)) != len(values):
                raise ValueError(f"duplicate source {field}")
        families: dict[str, str] = {}
        for source in self.sources:
            if source.family_id in families and families[source.family_id] != source.split:
                raise ValueError(f"family crosses splits: {source.family_id}")
            families[source.family_id] = source.split
        return self


class ContentUnit(Record):
    element_id: Identifier
    document_id: Identifier
    family_id: Identifier
    version: str
    split: Split
    page: int = Field(gt=0)
    page_end: int | None = Field(default=None, gt=0)
    text: str = Field(min_length=1)
    section: str | None = None
    bbox: tuple[float, float, float, float] | None = None
    source_checksum: Checksum
    source_url: HttpUrl

    @model_validator(mode="after")
    def check_geometry(self) -> Self:
        if self.page_end is not None and self.page_end < self.page:
            raise ValueError("page range ends before its start")
        if self.bbox is not None:
            x0, top, x1, bottom = self.bbox
            if not all(math.isfinite(v) for v in self.bbox) or not (
                0 <= x0 < x1 and 0 <= top < bottom
            ):
                raise ValueError("invalid bounding box")
        return self


class QueryExample(Record):
    query_id: Identifier
    text: str = Field(min_length=1, max_length=2000)
    split: Split
    family_id: Identifier
    query_type: str = Field(min_length=1)
    relevance: dict[str, Literal[0, 1, 2]]
    answerable: bool
    answer_criteria: str = Field(min_length=1)
    supporting_evidence: list[str]
    label_provenance: str = Field(min_length=1)
    review_status: Literal["draft", "human-reviewed"]

    @model_validator(mode="after")
    def check_evidence(self) -> Self:
        positives = {key for key, grade in self.relevance.items() if grade == 2}
        if self.answerable and (not positives or not self.supporting_evidence):
            raise ValueError("answerable query requires supporting evidence")
        if not self.answerable and (positives or self.supporting_evidence):
            raise ValueError("unanswerable query cannot have direct supporting evidence")
        if not set(self.supporting_evidence) <= positives:
            raise ValueError("supporting evidence must have relevance grade 2")
        return self


class RankedEvidence(Record):
    element_id: str
    document_id: str
    page: int = Field(gt=0)
    page_end: int | None = Field(default=None, gt=0)
    rank: int = Field(gt=0)
    retrieval_score: float = Field(allow_inf_nan=False)
    reranker_score: float | None = Field(default=None, allow_inf_nan=False)
