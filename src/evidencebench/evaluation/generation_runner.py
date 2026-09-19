"""Development answer evaluation against frozen upstream human references."""

import argparse
import json
import time
from pathlib import Path

from evidencebench.evaluation.answers import answer_metrics
from evidencebench.ingestion import canonical, digest
from evidencebench.labels import read_labels
from evidencebench.protocol import verify_protocol
from evidencebench.serving.pipeline import load_runtime
from evidencebench.tracking import create_run, log_mlflow, run_lifecycle


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--release", type=Path, default=Path("configs/release-proposal.yaml"))
    parser.add_argument("--limit", type=int)
    parser.add_argument(
        "--summary", type=Path, default=Path("artifacts/verification/development-answers.json")
    )
    args = parser.parse_args(argv)
    verify_protocol(Path("data/manifests/qasper-protocol.json"))
    release = args.release
    pipeline = load_runtime(release)
    labels = read_labels(Path("data/labels/qasper-v1/dev.jsonl"))
    if args.limit:
        labels = labels[: args.limit]
    if any(q.split != "dev" for q in labels):
        raise ValueError("development labels only")
    run, manifest = create_run(
        Path("artifacts/answers"),
        {
            "split": "dev",
            "release_hash": digest(release.read_bytes()),
            "versions": pipeline.versions,
            "query_count": len(labels),
        },
    )
    rows = []
    with run_lifecycle(run, manifest, 1800):
        for index, query in enumerate(labels):
            started = time.perf_counter()
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
                "elapsed_ms": (time.perf_counter() - started) * 1000,
                "trace": getattr(pipeline, "last_trace", {}),
            }
            rows.append(row)
            with (run / "predictions.jsonl").open("ab") as stream:
                stream.write(canonical(row) + b"\n")
            print(f"dev answers {index + 1}/{len(labels)}: {result['status']}", flush=True)
        metrics = answer_metrics(rows)
        (run / "metrics.json").write_bytes(canonical(metrics))
        manifest.update(
            status="complete", predictions_hash=digest((run / "predictions.jsonl").read_bytes())
        )
        manifest["mlflow_run_id"] = log_mlflow(run, {"purpose": "development answers"}, metrics)
    args.summary.write_bytes(canonical({"run": run.as_posix(), "metrics": metrics}))
    print(json.dumps({"run": str(run), "metrics": metrics}))


if __name__ == "__main__":
    main()
