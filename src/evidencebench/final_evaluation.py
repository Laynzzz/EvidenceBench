"""One frozen comparison; replay saved predictions for subsequent analysis."""

import json
import time
from datetime import UTC, datetime
from pathlib import Path

import yaml

from evidencebench.evaluation.answers import answer_metrics
from evidencebench.evaluation.runner import evaluate
from evidencebench.ingestion import canonical, digest
from evidencebench.labels import read_labels
from evidencebench.pipelines import load_retrievers
from evidencebench.protocol import verify_protocol
from evidencebench.reranking import RerankingRetriever, load_cross_encoder
from evidencebench.serving.pipeline import load_runtime
from evidencebench.tracking import create_run, log_mlflow, run_lifecycle

LOCK = Path("data/manifests/release-lock.json")
RELEASE = Path("configs/release.yaml")
TEST = Path("data/labels/qasper-v1/test.jsonl")
SYSTEMS = ["bm25", "dense", "hybrid", "untuned", "selected"]


def configuration():
    release = yaml.safe_load(RELEASE.read_text("utf-8"))
    base = yaml.safe_load(Path("configs/reranker.yaml").read_text("utf-8"))
    return release, {
        "retrieval": release["retrieval"],
        "models": {"untuned": base, "selected": release["reranker"]},
        "index": release["index_fingerprint"],
    }


def freeze():
    verify_protocol(Path("data/manifests/qasper-protocol.json"))
    release, provenance = configuration()
    paths = [p for root in ("src", "scripts") for p in Path(root).rglob("*.py")]
    paths += [
        RELEASE,
        Path("configs/reranker.yaml"),
        Path("uv.lock"),
        Path("pyproject.toml"),
        TEST,
        Path("data/manifests/qasper-protocol.json"),
    ]
    lock = {
        "created_at": datetime.now(UTC).isoformat(),
        "systems": SYSTEMS,
        "files": {p.as_posix(): digest(p.read_bytes()) for p in sorted(paths)},
        "corpus_fingerprint": release["corpus_fingerprint"],
        "provenance": provenance,
        "test_examples_hash": digest(
            canonical([q.model_dump(mode="json") for q in read_labels(TEST)])
        ),
        "policy": (
            "One final attempt. No model, prompt, threshold, scoring or data tuning after test."
        ),
    }
    with LOCK.open("xb") as stream:
        stream.write(canonical(lock))
    return LOCK


def run_final():
    lock = verify_protocol(LOCK)
    verify_protocol(Path("data/manifests/qasper-protocol.json"))
    release, provenance = configuration()
    if provenance != lock["provenance"]:
        raise ValueError("runtime configuration differs from frozen provenance")
    # All runtime comparison objects are constructed here from the hashed configs.
    # Callers cannot supply alternate retrievers under the same display names.
    ledger = Path("artifacts/final-attempt.json")
    ledger.parent.mkdir(exist_ok=True)
    with ledger.open("xb") as stream:
        stream.write(
            canonical(
                {
                    "status": "started",
                    "lock_hash": digest(LOCK.read_bytes()),
                    "started_at": datetime.now(UTC).isoformat(),
                }
            )
        )
    units, systems, metadata = load_retrievers(provenance["retrieval"])
    if (
        metadata["index_fingerprint"] != provenance["index"]
        or metadata["fingerprint"] != lock["corpus_fingerprint"]
    ):
        raise ValueError("loaded index/corpus differs from release freeze")
    for name, model_config in provenance["models"].items():
        systems[name] = RerankingRetriever(
            systems["hybrid"],
            units,
            load_cross_encoder(model_config),
            provenance["retrieval"]["candidate_k"],
        )
    labels = read_labels(TEST)
    ranking_run = evaluate(
        labels,
        units,
        systems,
        Path("artifacts/runs"),
        metadata["fingerprint"],
        provenance,
        release_lock=LOCK,
    )
    ledger.write_bytes(
        canonical(
            {
                "status": "ranking_complete",
                "ranking_run": ranking_run.as_posix(),
                "lock_hash": digest(LOCK.read_bytes()),
            }
        )
    )
    pipeline = load_runtime(RELEASE)
    answer_run, manifest = create_run(
        Path("artifacts/answers"),
        {
            "split": "test",
            "release_hash": digest(RELEASE.read_bytes()),
            "lock_hash": digest(LOCK.read_bytes()),
            "versions": pipeline.versions,
        },
    )
    rows = []
    with run_lifecycle(answer_run, manifest, 3600):
        for index, query in enumerate(labels):
            tick = time.perf_counter()
            try:
                result = pipeline.ask(query.text, {})
            except Exception as exc:
                result = {
                    "status": "failure",
                    "reason": type(exc).__name__,
                    "answer": "",
                    "citations": [],
                }
            row = {
                "query_id": query.query_id,
                "question": query.text,
                "family_id": query.family_id,
                "answerable": query.answerable,
                "answer_criteria": query.answer_criteria,
                "supporting_evidence": query.supporting_evidence,
                "citation_ids": [c["element_id"] for c in result["citations"]],
                **result,
                "elapsed_ms": (time.perf_counter() - tick) * 1000,
                "trace": getattr(pipeline, "last_trace", {}),
            }
            rows.append(row)
            with (answer_run / "predictions.jsonl").open("ab") as stream:
                stream.write(canonical(row) + b"\n")
            print(f"test answers {index + 1}/{len(labels)}: {result['status']}", flush=True)
        metrics = answer_metrics(rows)
        (answer_run / "metrics.json").write_bytes(canonical(metrics))
        manifest.update(
            status="complete",
            predictions_hash=digest((answer_run / "predictions.jsonl").read_bytes()),
        )
        manifest["mlflow_run_id"] = log_mlflow(
            answer_run, {"purpose": "frozen final answers"}, metrics
        )
    result = {
        "status": "complete",
        "ranking_run": ranking_run.as_posix(),
        "answer_run": answer_run.as_posix(),
        "lock_hash": digest(LOCK.read_bytes()),
    }
    ledger.write_bytes(canonical(result))
    return result


if __name__ == "__main__":
    import sys

    print(json.dumps(str(freeze()) if "--freeze" in sys.argv else run_final()))
