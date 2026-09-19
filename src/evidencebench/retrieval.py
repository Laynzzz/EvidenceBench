"""Shared retrieval implementations with deterministic tie-breaking."""

import math
import re
from collections import Counter
from collections.abc import Callable, Sequence
from typing import Any, Protocol

import numpy as np

from evidencebench.schemas import ContentUnit, RankedEvidence


class Retriever(Protocol):
    def retrieve(self, query: str, filters: dict[str, str], k: int) -> list[RankedEvidence]: ...


def tokenize(text: str) -> list[str]:
    return re.findall(r"\w+", text.casefold())


def validate_request(query: str, filters: dict[str, str], k: int) -> None:
    if not 1 <= k <= 100 or len(query) > 2000:
        raise ValueError("query must be <= 2000 characters and k between 1 and 100")
    if filters.keys() - {"document_id", "family_id", "split"}:
        raise ValueError("unsupported metadata filter")


def matches(unit: ContentUnit, filters: dict[str, str]) -> bool:
    return all(getattr(unit, key) == value for key, value in filters.items())


def ranked(units: Sequence[ContentUnit], scores: Sequence[float], k: int) -> list[RankedEvidence]:
    rows = sorted(zip(units, scores, strict=True), key=lambda row: (-row[1], row[0].element_id))
    return [
        RankedEvidence(
            element_id=u.element_id,
            document_id=u.document_id,
            page=u.page,
            page_end=u.page_end,
            rank=i + 1,
            retrieval_score=float(score),
        )
        for i, (u, score) in enumerate(rows[:k])
    ]


class BM25Retriever:
    """Okapi BM25, positive Robertson IDF, k1=1.5 and b=0.75."""

    def __init__(self, units: list[ContentUnit], k1: float = 1.5, b: float = 0.75):
        if not units or k1 <= 0 or not 0 <= b <= 1:
            raise ValueError("invalid BM25 corpus/parameters")
        self.units, self.k1, self.b = units, k1, b
        self.terms = [Counter(tokenize(u.text)) for u in units]
        self.lengths = [sum(terms.values()) for terms in self.terms]
        self.avg_length = sum(self.lengths) / len(units)
        if not self.avg_length:
            raise ValueError("no searchable tokens")
        frequency = Counter(term for doc in self.terms for term in doc)
        self.frequency = frequency
        self.idf = {
            term: math.log(1 + (len(units) - count + 0.5) / (count + 0.5))
            for term, count in frequency.items()
        }

    def excluding(self, element_ids: set[str]):
        """Reuse token counts while exactly recomputing IDF/lengths after exclusions."""
        selected = [i for i, u in enumerate(self.units) if u.element_id not in element_ids]
        if not selected:
            raise ValueError("empty BM25 corpus after exclusions")
        result = object.__new__(BM25Retriever)
        result.units = [self.units[i] for i in selected]
        result.terms = [self.terms[i] for i in selected]
        result.lengths = [self.lengths[i] for i in selected]
        result.k1, result.b = self.k1, self.b
        result.avg_length = sum(result.lengths) / len(selected)
        removed = Counter(
            term
            for u, terms in zip(self.units, self.terms, strict=True)
            if u.element_id in element_ids
            for term in terms
        )
        result.frequency = self.frequency - removed
        result.idf = {
            term: math.log(1 + (len(selected) - count + 0.5) / (count + 0.5))
            for term, count in result.frequency.items()
        }
        return result

    def retrieve(self, query: str, filters: dict[str, str], k: int) -> list[RankedEvidence]:
        validate_request(query, filters, k)
        words = set(tokenize(query))
        candidates, scores = [], []
        for unit, terms, length in zip(self.units, self.terms, self.lengths, strict=True):
            if not matches(unit, filters):
                continue
            score = sum(
                self.idf.get(term, 0)
                * (terms[term] * (self.k1 + 1))
                / (terms[term] + self.k1 * (1 - self.b + self.b * length / self.avg_length))
                for term in words
            )
            if score > 0:
                candidates.append(unit)
                scores.append(score)
        return ranked(candidates, scores, k)


class DenseRetriever:
    """Exact cosine reference implementation; PostgreSQL uses the same vectors."""

    def __init__(self, units: list[ContentUnit], vectors: Any, encode_query: Callable[[str], Any]):
        values = np.asarray(vectors, dtype=np.float32)
        if values.ndim != 2 or len(values) != len(units) or not np.isfinite(values).all():
            raise ValueError("invalid embedding matrix")
        norms = np.linalg.norm(values, axis=1, keepdims=True)
        if np.any(norms == 0):
            raise ValueError("zero document embedding")
        self.units, self.vectors, self.encode_query = units, values / norms, encode_query

    def retrieve(self, query: str, filters: dict[str, str], k: int) -> list[RankedEvidence]:
        validate_request(query, filters, k)
        if not query.strip():
            return []
        vector = np.asarray(self.encode_query(query), dtype=np.float32)
        if vector.shape != (self.vectors.shape[1],) or not np.isfinite(vector).all():
            raise ValueError("invalid query embedding")
        norm = np.linalg.norm(vector)
        if norm == 0:
            raise ValueError("zero query embedding")
        scores = self.vectors @ (vector / norm)
        indices = [i for i, unit in enumerate(self.units) if matches(unit, filters)]
        return ranked([self.units[i] for i in indices], [float(scores[i]) for i in indices], k)


def reciprocal_rank_fusion(
    lists: list[list[RankedEvidence]], k: int = 20, constant: int = 60
) -> list[RankedEvidence]:
    if not 1 <= k <= 100 or constant < 0:
        raise ValueError("invalid fusion parameters")
    scores: dict[str, float] = {}
    evidence = {}
    for results in lists:
        seen = set()
        for position, hit in enumerate(results, 1):
            if hit.element_id in seen:
                raise ValueError("duplicate evidence in retrieval list")
            seen.add(hit.element_id)
            scores[hit.element_id] = scores.get(hit.element_id, 0) + 1 / (constant + position)
            evidence[hit.element_id] = hit
    ids = sorted(scores, key=lambda key: (-scores[key], key))[:k]
    return [
        evidence[key].model_copy(update={"rank": i + 1, "retrieval_score": scores[key]})
        for i, key in enumerate(ids)
    ]


class HybridRetriever:
    def __init__(self, lexical: Retriever, dense: Retriever, candidates: int = 50):
        self.lexical, self.dense, self.candidates = lexical, dense, candidates

    def retrieve(self, query: str, filters: dict[str, str], k: int) -> list[RankedEvidence]:
        validate_request(query, filters, k)
        depth = max(k, self.candidates)
        return reciprocal_rank_fusion(
            [
                self.lexical.retrieve(query, filters, depth),
                self.dense.retrieve(query, filters, depth),
            ],
            k=k,
        )
