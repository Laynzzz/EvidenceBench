"""Development-only runner; final-test execution stays disabled until release freeze exists."""

import json
import time
from pathlib import Path
from typing import Any

import numpy as np

from evidencebench.evaluation.metrics import score_ranking
from evidencebench.ingestion import canonical, digest
from evidencebench.labels import validate_labels
from evidencebench.retrieval import Retriever
from evidencebench.schemas import ContentUnit, QueryExample
from evidencebench.tracking import create_run


def aggregate(rows: list[dict[str, Any]]) -> dict[str, Any]:
    systems = sorted({r["system"] for r in rows})
    report = {}
    for system in systems:
        selected = [r for r in rows if r["system"] == system]
        metrics: dict[str, list[float]] = {
            "recall_at_5": [],
            "recall_at_10": [],
            "recall_at_20": [],
            "ndcg_at_10": [],
            "mrr": [],
        }
        for row in selected:
            if not row["answerable"]:
                continue
            for k in (5, 10, 20):
                values = score_ranking(row["predicted"], row["relevance"], k)
                if values is None:
                    raise ValueError("answerable row lacks judgments")
                metrics[f"recall_at_{k}"].append(values["recall"])
                if k == 10:
                    metrics["ndcg_at_10"].append(values["ndcg"])
                    metrics["mrr"].append(values["mrr"])
        report[system] = {
            key: float(np.mean(values)) if values else None for key, values in metrics.items()
        }
        report[system].update(
            {
                "query_count": len(selected),
                "answerable_count": sum(r["answerable"] for r in selected),
                "unanswerable_count": sum(not r["answerable"] for r in selected),
                "failure_count": sum(r["status"] != "ok" for r in selected),
                "p50_ms": float(np.quantile([r["elapsed_ms"] for r in selected], 0.5)),
                "p95_ms": float(np.quantile([r["elapsed_ms"] for r in selected], 0.95)),
            }
        )
    return report


def evaluate(
    examples: list[QueryExample],
    units: list[ContentUnit],
    retrievers: dict[str, Retriever],
    root: Path,
    corpus_fingerprint: str,
    provenance: dict[str, Any] | None = None,
    release_lock: Path | None = None,
) -> Path:
    split = "dev"
    if any(q.split != "dev" for q in examples):
        if release_lock is None or any(q.split != "test" for q in examples):
            raise ValueError(
                "only development evaluation enabled; final test requires release freeze"
            )
        from evidencebench.release import verify_final_lock

        verify_final_lock(release_lock, examples, corpus_fingerprint, list(retrievers), provenance)
        split = "test"
    if not retrievers:
        raise ValueError("no retrieval systems")
    counts = validate_labels(examples, units)
    labels = [q.model_dump(mode="json") for q in examples]
    config = {
        "split": split,
        "systems": sorted(retrievers),
        "corpus_fingerprint": corpus_fingerprint,
        "labels_hash": digest(canonical(labels)),
        "k": 20,
        "seed": 42,
        "provenance": provenance or {},
        "counts": counts,
    }
    run, manifest = create_run(root, config)
    rows = []
    lookup = {u.element_id for u in units}
    started = time.perf_counter()
    for query in examples:
        for name, retriever in retrievers.items():
            tick = time.perf_counter()
            hits, status, error = [], "ok", None
            try:
                hits = retriever.retrieve(query.text, {}, 20)  # Never pass a gold-family filter.
                ids = [h.element_id for h in hits]
                if len(set(ids)) != len(ids) or set(ids) - lookup:
                    raise ValueError("invalid retrieval references")
            except Exception as exc:
                status, error, hits = "failure", type(exc).__name__, []
            rows.append(
                {
                    "query_id": query.query_id,
                    "query": query.text,
                    "family_id": query.family_id,
                    "answerable": query.answerable,
                    "relevance": query.relevance,
                    "system": name,
                    "predicted": [h.element_id for h in hits],
                    "evidence": [h.model_dump(mode="json") for h in hits],
                    "status": status,
                    "error": error,
                    "elapsed_ms": (time.perf_counter() - tick) * 1000,
                }
            )
    predictions = b"\n".join(canonical(row) for row in rows) + b"\n"
    (run / "predictions.jsonl").write_bytes(predictions)
    (run / "labels.json").write_bytes(canonical(labels))
    (run / "metrics.json").write_bytes(canonical(aggregate(rows)))
    manifest.update(
        elapsed_seconds=time.perf_counter() - started,
        predictions_hash=digest(predictions),
        artifacts=["predictions.jsonl", "metrics.json", "labels.json", "config.json"],
    )
    (run / "manifest.json").write_bytes(canonical(manifest))
    return run


def recalculate(run: Path) -> dict[str, Any]:
    predictions = (run / "predictions.jsonl").read_bytes()
    manifest = json.loads((run / "manifest.json").read_text("utf-8"))
    if digest(predictions) != manifest["predictions_hash"]:
        raise ValueError("prediction checksum mismatch")
    return aggregate([json.loads(line) for line in predictions.splitlines()])
