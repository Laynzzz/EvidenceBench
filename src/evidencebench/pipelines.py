"""Construct shared retrievers from a verified corpus and pinned index."""

import json
from pathlib import Path
from typing import Any

from evidencebench.indexing import load_encoder, load_index
from evidencebench.ingestion import load_units
from evidencebench.retrieval import BM25Retriever, DenseRetriever, HybridRetriever, Retriever
from evidencebench.schemas import ContentUnit


def load_retrievers(
    config: dict[str, Any], include_dense: bool = True
) -> tuple[list[ContentUnit], dict[str, Retriever], dict[str, Any]]:
    corpus = Path(config["corpus"])
    units = load_units(corpus)
    metadata = json.loads((corpus / "manifest.json").read_text("utf-8"))
    lexical = BM25Retriever(units)
    retrievers: dict[str, Retriever] = {"bm25": lexical}
    if include_dense:
        vectors, index_meta = load_index(Path(config["index"]), units, metadata["fingerprint"])
        for field in ("model_id", "revision", "max_seq_length"):
            if config[field] != index_meta[field]:
                raise ValueError(f"query encoder/index configuration mismatch: {field}")
        encoder = load_encoder(config)
        dense = DenseRetriever(
            units,
            vectors,
            lambda text: encoder.encode_query(
                text, normalize_embeddings=True, show_progress_bar=False
            ),
        )
        retrievers.update(
            dense=dense, hybrid=HybridRetriever(lexical, dense, config.get("candidate_k", 50))
        )
        metadata["index_fingerprint"] = index_meta["fingerprint"]
    return units, retrievers, metadata
