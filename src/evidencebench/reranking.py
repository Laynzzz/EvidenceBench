"""Pinned cross-encoder scoring shared by training evaluation and inference."""

import re
from pathlib import Path
from typing import Any

import numpy as np

from evidencebench.ingestion import canonical, digest
from evidencebench.retrieval import Retriever, validate_request
from evidencebench.schemas import ContentUnit, RankedEvidence


def checkpoint_hash(path: Path) -> str:
    files = {
        p.relative_to(path).as_posix(): digest(p.read_bytes())
        for p in sorted(path.rglob("*"))
        if p.is_file()
    }
    if not files:
        raise ValueError("empty checkpoint")
    return digest(canonical(files))


def load_cross_encoder(config: dict[str, Any]):
    import torch
    from sentence_transformers import CrossEncoder

    torch.set_num_threads(config.get("cpu_threads", 4))
    if "checkpoint" in config:
        path = Path(config["checkpoint"])
        if checkpoint_hash(path) != config["checkpoint_hash"]:
            raise ValueError("checkpoint checksum mismatch")
        return CrossEncoder(
            str(path),
            device=config.get("device", "cpu"),
            max_length=config.get("max_length", 384),
            local_files_only=True,
        )
    if not re.fullmatch(r"[a-f0-9]{40}", config["revision"]):
        raise ValueError("cross-encoder revision must be an immutable commit")
    return CrossEncoder(
        config["model_id"],
        revision=config["revision"],
        device=config.get("device", "cpu"),
        max_length=config.get("max_length", 384),
        trust_remote_code=False,
    )


class RerankingRetriever:
    def __init__(
        self,
        retriever: Retriever,
        units: list[ContentUnit],
        model: Any,
        candidate_k: int = 50,
        batch_size: int = 16,
    ):
        if not 1 <= candidate_k <= 100 or batch_size < 1:
            raise ValueError("invalid reranking bounds")
        self.retriever, self.model = retriever, model
        self.lookup = {u.element_id: u for u in units}
        self.candidate_k, self.batch_size = candidate_k, batch_size

    def retrieve(self, query: str, filters: dict[str, str], k: int) -> list[RankedEvidence]:
        validate_request(query, filters, k)
        hits = self.retriever.retrieve(query, filters, self.candidate_k)
        if not hits:
            return []
        pairs = [(query, self.lookup[h.element_id].text) for h in hits]
        scores = np.asarray(
            self.model.predict(
                pairs, batch_size=self.batch_size, show_progress_bar=False, convert_to_numpy=True
            )
        ).reshape(-1)
        if scores.shape != (len(hits),) or not np.isfinite(scores).all():
            raise ValueError("invalid reranker scores")
        ordered = sorted(zip(hits, scores, strict=True), key=lambda x: (-x[1], x[0].element_id))
        return [
            hit.model_copy(update={"rank": i + 1, "reranker_score": float(score)})
            for i, (hit, score) in enumerate(ordered[:k])
        ]
