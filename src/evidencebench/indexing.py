"""Pinned embedding inference and immutable local index interchange artifacts."""

import json
import re
import time
from pathlib import Path
from typing import Any

import numpy as np

from evidencebench.ingestion import canonical, digest, load_units
from evidencebench.schemas import ContentUnit
from evidencebench.tracking import environment


def save_index(
    root: Path, units: list[ContentUnit], vectors: Any, metadata: dict[str, Any]
) -> None:
    values = np.asarray(vectors, dtype=np.float32)
    if values.ndim != 2 or len(values) != len(units) or not np.isfinite(values).all():
        raise ValueError("invalid embedding matrix")
    if np.any(np.linalg.norm(values, axis=1) == 0):
        raise ValueError("zero embedding")
    root.mkdir(parents=True, exist_ok=False)
    np.save(root / "embeddings.npy", values, allow_pickle=False)
    manifest = {
        **metadata,
        "element_ids": [u.element_id for u in units],
        "dimension": values.shape[1],
        "embedding_count": len(values),
        "embeddings_hash": digest((root / "embeddings.npy").read_bytes()),
    }
    manifest["fingerprint"] = digest(canonical(manifest))
    (root / "manifest.json").write_bytes(canonical(manifest))


def load_index(
    root: Path, units: list[ContentUnit], corpus_fingerprint: str
) -> tuple[Any, dict[str, Any]]:
    metadata = json.loads((root / "manifest.json").read_text("utf-8"))
    content = {k: v for k, v in metadata.items() if k != "fingerprint"}
    if digest(canonical(content)) != metadata["fingerprint"]:
        raise ValueError("index manifest checksum mismatch")
    if metadata["corpus_fingerprint"] != corpus_fingerprint:
        raise ValueError("index belongs to a different corpus")
    if metadata["element_ids"] != [u.element_id for u in units]:
        raise ValueError("index element order mismatch")
    if digest((root / "embeddings.npy").read_bytes()) != metadata["embeddings_hash"]:
        raise ValueError("index embeddings checksum mismatch")
    return np.load(root / "embeddings.npy", allow_pickle=False), metadata


def load_encoder(config: dict[str, Any]) -> Any:
    if not re.fullmatch(r"[0-9a-f]{40}", config["revision"]):
        raise ValueError("model revision must be an immutable 40-character commit")
    import torch
    from sentence_transformers import SentenceTransformer

    torch.set_num_threads(config.get("cpu_threads", 4))
    model = SentenceTransformer(
        config["model_id"],
        revision=config["revision"],
        device=config.get("device", "cpu"),
        trust_remote_code=False,
    )
    model.max_seq_length = config.get("max_seq_length", 384)
    return model


def build_index(config: dict[str, Any]) -> dict[str, Any]:
    root, corpus = Path(config["index"]), Path(config["corpus"])
    if root.exists():
        raise FileExistsError(f"immutable index already exists: {root}")
    units = load_units(corpus)
    corpus_meta = json.loads((corpus / "manifest.json").read_text("utf-8"))
    started = time.perf_counter()
    encoder = load_encoder(config)
    vectors = encoder.encode_document(
        [u.text for u in units],
        batch_size=config.get("batch_size", 32),
        normalize_embeddings=True,
        show_progress_bar=False,
    )
    metadata = {
        **config,
        "corpus_fingerprint": corpus_meta["fingerprint"],
        "elapsed_seconds": time.perf_counter() - started,
        **environment(),
    }
    save_index(root, units, vectors, metadata)
    return json.loads((root / "manifest.json").read_text("utf-8"))
