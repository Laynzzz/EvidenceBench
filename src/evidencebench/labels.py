"""Label provenance, split validation, and train-only negative sampling."""

import random
from collections import Counter
from pathlib import Path
from typing import Any

from evidencebench.chunking import normalize
from evidencebench.retrieval import BM25Retriever
from evidencebench.schemas import ContentUnit, QueryExample


def read_labels(path: Path) -> list[QueryExample]:
    return [
        QueryExample.model_validate_json(line)
        for line in path.read_text("utf-8").splitlines()
        if line.strip()
    ]


def validate_labels(
    examples: list[QueryExample], units: list[ContentUnit], allow_drafts: bool = False
) -> dict[str, Any]:
    if not examples:
        raise ValueError("label set is empty")
    lookup = {u.element_id: u for u in units}
    family_splits: dict[str, str] = {}
    for unit in units:
        if unit.family_id in family_splits and family_splits[unit.family_id] != unit.split:
            raise ValueError("corpus family split mismatch")
        family_splits[unit.family_id] = unit.split
    ids, texts = set(), set()
    for query in examples:
        text = normalize(query.text).casefold()
        if query.query_id in ids or text in texts:
            raise ValueError(f"duplicate query ID/text: {query.query_id}")
        ids.add(query.query_id)
        texts.add(text)
        if query.family_id not in family_splits:
            raise ValueError(f"unknown query family: {query.family_id}")
        if family_splits[query.family_id] != query.split:
            raise ValueError(f"query family split mismatch: {query.query_id}")
        if query.split != "train" and not allow_drafts and query.review_status != "human-reviewed":
            raise ValueError(f"evaluation requires human-reviewed labels: {query.query_id}")
        for element_id, grade in query.relevance.items():
            if element_id not in lookup:
                raise ValueError(f"unknown evidence ID: {element_id}")
            unit = lookup[element_id]
            if (query.split == "train" or grade > 0) and unit.split != query.split:
                raise ValueError(f"evidence crosses query split: {query.query_id}")
        if any(lookup[key].family_id != query.family_id for key in query.supporting_evidence):
            raise ValueError("supporting evidence crosses query family")
    return {
        "query_count": len(examples),
        "splits": dict(Counter(q.split for q in examples)),
        "judgment_count": sum(len(q.relevance) for q in examples),
        "reviewed_evaluation_count": sum(
            q.split != "train" and q.review_status == "human-reviewed" for q in examples
        ),
        "unanswerable_count": sum(not q.answerable for q in examples),
        "family_count": len({q.family_id for q in examples}),
    }


def mine_negatives(
    query: QueryExample,
    units: list[ContentUnit],
    count: int = 4,
    seed: int = 42,
    method: str = "hard",
    lexical: BM25Retriever | None = None,
) -> list[str]:
    if query.split != "train" or count < 1 or method not in {"random", "hard"}:
        raise ValueError("negative mining requires a training query and valid sampler")
    validate_labels([query], units)
    if lexical is not None and {u.element_id for u in lexical.units} != {
        u.element_id for u in units if u.split == "train"
    }:
        raise ValueError("cached negative index must contain exactly the training corpus")
    # Contextual positives are excluded too. Human audit must still catch unjudged positives.
    excluded = {key for key, grade in query.relevance.items() if grade > 0}
    pool = [u for u in units if u.split == "train" and u.element_id not in excluded]
    if len(pool) < count:
        raise ValueError("not enough training-only negative candidates")
    rng = random.Random(seed)
    pool.sort(key=lambda u: u.element_id)
    rng.shuffle(pool)
    selected = []
    if method == "hard":
        retriever = lexical.excluding(excluded) if lexical is not None else BM25Retriever(pool)
        selected = [h.element_id for h in retriever.retrieve(query.text, {}, min(count, 100))]
    selected.extend(u.element_id for u in pool if u.element_id not in selected)
    return selected[:count]
