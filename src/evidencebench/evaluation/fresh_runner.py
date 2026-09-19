"""Preflight or explicitly approved, externally bounded fresh-validation comparison."""

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from uuid import uuid4

import yaml

from evidencebench.evaluation.fresh_comparison import (
    Budget,
    MeteredModel,
    compare_queries,
    summarize,
)
from evidencebench.ingestion import canonical, digest, load_units
from evidencebench.labels import read_labels, validate_labels
from evidencebench.protocol import verify_protocol
from evidencebench.reranking import checkpoint_hash
from evidencebench.tracking import create_run, run_lifecycle

ROOT = Path("artifacts/fresh-validation-v1")
CORPUS = Path("data/processed/qasper-fresh-v1")
LABELS = Path("data/labels/qasper-fresh-v1/dev.jsonl")
REPORT = Path("reports/fresh-dataset.json")
REPORT_HASH = "aca2f5068725c880747f2422fe980a17313293db99d01337805b02af47969cd2"
LIMITS = {
    "document_embeddings": 3161,
    "query_embeddings": 50,
    "reranker_pairs": 2500,
    "control_invocations": 50,
    "constrained_invocations": 50,
    "control_calls": 100,
    "constrained_calls": 50,
    "reserved_tokens": 13200,
}


def read(path):
    return json.loads(path.read_text("utf-8"))


def cached_model_files(model, kind):
    from huggingface_hub import try_to_load_from_cache

    required = ["config.json", "tokenizer_config.json", "tokenizer.json", "model.safetensors"]
    if kind == "retrieval":
        required += [
            "modules.json",
            "config_sentence_transformers.json",
            "sentence_bert_config.json",
            "1_Pooling/config.json",
            "vocab.txt",
            "special_tokens_map.json",
        ]
    elif kind == "generation":
        required += ["generation_config.json", "merges.txt", "vocab.json"]
    else:
        raise ValueError("unknown cached model kind")
    snapshot = None
    for name in required:
        path = try_to_load_from_cache(model["model_id"], name, revision=model["revision"])
        if not isinstance(path, str) or not Path(path).is_file():
            raise ValueError("required model artifact absent from cache")
        if name == "config.json":
            snapshot = Path(path).parent
    return {
        p.relative_to(snapshot).as_posix(): digest(p.read_bytes())
        for p in sorted(snapshot.rglob("*"))
        if p.is_file()
    }


def preflight():
    """Read-only integrity/cache checks. Never parse final-test labels or load a model."""
    verify_protocol(Path("data/manifests/release-lock.json"))
    if digest(REPORT.read_bytes()) != REPORT_HASH:
        raise ValueError("fresh dataset report checksum mismatch")
    report = verify_protocol(REPORT)
    units, queries = load_units(CORPUS), read_labels(LABELS)
    summary = validate_labels(queries, units)
    if (
        len(units) != 3161
        or len(queries) != 50
        or summary["unanswerable_count"] != 12
        or any(q.split != "dev" for q in queries)
    ):
        raise ValueError("fixed fresh validation roster mismatch")
    release = yaml.safe_load(Path("configs/release.yaml").read_text("utf-8"))
    ranker = release["reranker"]
    if checkpoint_hash(Path(ranker["checkpoint"])) != ranker["checkpoint_hash"]:
        raise ValueError("selected checkpoint mismatch")
    cached = {key: cached_model_files(release[key], key) for key in ("retrieval", "generation")}
    paths = sorted(Path("src/evidencebench").rglob("*.py")) + [
        Path("configs/release.yaml"),
        Path("docs/fresh-validation-proposal.md"),
        Path("docs/fresh-evaluation-protocol.md"),
        REPORT,
        Path("uv.lock"),
        Path("pyproject.toml"),
    ]
    return {
        "status": "ready_for_authorization",
        "split": "dev",
        "queries": 50,
        "paragraphs": 3161,
        "dataset_fingerprint": report["fingerprint"],
        "labels_sha256": digest(LABELS.read_bytes()),
        "limits": LIMITS,
        "deadline_seconds": 2700,
        "release": release,
        "cached_model_sha256": cached,
        "source_sha256": {p.as_posix(): digest(p.read_bytes()) for p in paths},
    }


def launch(root, snapshot, seconds=2700):
    root.mkdir(parents=True, exist_ok=False)
    token = uuid4().hex
    (root / "attempt.json").write_bytes(
        canonical({"token": token, "snapshot": snapshot, "consumes_single_attempt": True})
    )
    started = time.monotonic()
    process, reason, code = None, "spawn_failure", 1
    try:
        process = subprocess.Popen(
            [
                sys.executable,
                "-X",
                "utf8",
                "-m",
                "evidencebench.evaluation.fresh_runner",
                "--worker",
                token,
                "--worker-root",
                str(root),
            ],
            env={**os.environ, "HF_HUB_OFFLINE": "1", "TRANSFORMERS_OFFLINE": "1"},
        )
        code = process.wait(timeout=max(0, seconds - (time.monotonic() - started)))
        reason = "process_exit"
    except (subprocess.TimeoutExpired, KeyboardInterrupt) as exc:
        reason = "timeout" if isinstance(exc, subprocess.TimeoutExpired) else "interrupted"
        if process is not None:
            process.kill()
            process.wait()
        code = 124 if reason == "timeout" else 130
    finally:
        (root / "termination.json").write_bytes(
            canonical(
                {"reason": reason, "exit_code": code, "elapsed_seconds": time.monotonic() - started}
            )
        )
    return code


def claim_worker(root, token):
    attempt = read(root / "attempt.json")
    if token != attempt["token"]:
        raise ValueError("worker token mismatch")
    with (root / "worker.started").open("x", encoding="utf-8") as stream:
        stream.write(token)
    return attempt["snapshot"]


def execute(snapshot, root=ROOT):
    # Loading is deliberately confined to the approved worker, after all guards.
    from huggingface_hub import constants

    if not constants.HF_HUB_OFFLINE:
        raise RuntimeError("worker must start offline before importing model libraries")
    from evidencebench.generation import LocalGenerator
    from evidencebench.generation_spans import SpanGenerator
    from evidencebench.indexing import load_encoder, save_index
    from evidencebench.reranking import RerankingRetriever, load_cross_encoder
    from evidencebench.retrieval import BM25Retriever, DenseRetriever, HybridRetriever

    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    run, manifest = create_run(root / "runs", snapshot)
    budget = Budget(run / "usage.json", LIMITS)
    with run_lifecycle(run, manifest, 2700):
        units, queries = load_units(CORPUS), read_labels(LABELS)
        release = snapshot["release"]
        encoder = load_encoder(release["retrieval"])
        budget.charge("document_embeddings", len(units))
        vectors = encoder.encode_document(
            [u.text for u in units],
            batch_size=32,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        save_index(
            run / "index",
            units,
            vectors,
            {
                **release["retrieval"],
                "corpus": CORPUS.as_posix(),
                "index": (run / "index").as_posix(),
                "corpus_fingerprint": snapshot["dataset_fingerprint"],
            },
        )

        def encode_query(text):
            budget.charge("query_embeddings")
            return encoder.encode_query(text, normalize_embeddings=True, show_progress_bar=False)

        hybrid = HybridRetriever(
            BM25Retriever(units), DenseRetriever(units, vectors, encode_query), 50
        )

        class Capture:
            pre = []

            def retrieve(self, text, filters, k):
                self.pre = hybrid.retrieve(text, filters, k)
                return self.pre

        capture = Capture()
        ranker_model = load_cross_encoder(release["reranker"])

        class MeteredRanker:
            def predict(self, pairs, **kwargs):
                budget.charge("reranker_pairs", len(pairs))
                return ranker_model.predict(pairs, **kwargs)

        ranker = RerankingRetriever(capture, units, MeteredRanker(), 50)

        class Retrieval:
            @property
            def pre(self):
                return capture.pre

            def retrieve(self, text, filters, k):
                capture.pre = []
                return ranker.retrieve(text, filters, k)

        control = LocalGenerator(release["generation"])
        raw_model = control.model
        control.model = MeteredModel(raw_model, budget, "control", 100)
        # Same cached weights/tokenizer; the frozen generation methods differ.
        candidate = SpanGenerator.__new__(SpanGenerator)
        candidate.config = {
            **release["generation"],
            "variant": "constrained",
            "prompt_version": "short-source-span-v1",
        }
        candidate.model = MeteredModel(raw_model, budget, "constrained", 64)
        candidate.tokenizer = control.tokenizer
        rows = compare_queries(
            queries,
            units,
            Retrieval(),
            {"control": control, "constrained": candidate},
            budget.charge,
            run,
            release["generation"]["refusal_threshold"],
        )
        metrics = summarize(rows)
        (run / "metrics.json").write_bytes(canonical(metrics))
        manifest.update(
            status="complete",
            files={
                p.name: digest(p.read_bytes())
                for p in [
                    run / "control.jsonl",
                    run / "constrained.jsonl",
                    run / "usage.json",
                    run / "metrics.json",
                ]
            },
        )
    print(json.dumps({"run": run.as_posix(), "metrics": metrics, "usage": budget.used}))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--run-approved", action="store_true", help="Only after explicit new allowance"
    )
    mode.add_argument("--worker", help=argparse.SUPPRESS)
    parser.add_argument("--worker-root", type=Path, default=ROOT, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    if args.worker:
        snapshot = claim_worker(args.worker_root, args.worker)
        if snapshot != preflight():
            raise ValueError("preflight snapshot changed before execution")
        execute(snapshot, args.worker_root)
    elif args.run_approved:
        snapshot = preflight()
        raise SystemExit(launch(ROOT, snapshot))
    else:
        snapshot = preflight()
        print(
            json.dumps(
                {
                    "status": snapshot["status"],
                    "queries": snapshot["queries"],
                    "paragraphs": snapshot["paragraphs"],
                    "limits": snapshot["limits"],
                    "snapshot_sha256": digest(canonical(snapshot)),
                    "attempt_already_exists": ROOT.exists(),
                    "model_calls": 0,
                }
            )
        )


if __name__ == "__main__":
    main()
