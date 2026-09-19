"""Compare primary-seed candidates; select from development only and export a proposal."""

import json
import shutil
from pathlib import Path

import yaml

from evidencebench.evaluation.answers import calibrate_threshold
from evidencebench.evaluation.metrics import paired_family_bootstrap, score_ranking
from evidencebench.evaluation.runner import evaluate
from evidencebench.ingestion import canonical
from evidencebench.labels import read_labels
from evidencebench.pipelines import load_retrievers
from evidencebench.protocol import verify_protocol
from evidencebench.reranking import RerankingRetriever, checkpoint_hash, load_cross_encoder
from evidencebench.tracking import log_mlflow


def main():
    verify_protocol(Path("data/manifests/qasper-protocol.json"))
    config = yaml.safe_load(Path("configs/qasper-retrieval.yaml").read_text("utf-8"))
    base = yaml.safe_load(Path("configs/reranker.yaml").read_text("utf-8"))
    units, systems, metadata = load_retrievers(config)
    models = {"untuned": base}
    failed_runs = []
    for path in sorted(Path("artifacts/training").glob("*/manifest.json")):
        manifest = json.loads(path.read_text("utf-8"))
        if manifest.get("status") != "complete":
            failed_runs.append(str(path.parent))
            continue
        run_config = manifest["config"]
        if run_config["smoke"] or run_config["seed"] != 42:
            continue
        name = f"trained-{run_config['query_count']}-{run_config['negative_method']}"
        if name in models:
            raise ValueError("ambiguous duplicate primary training run")
        models[name] = {
            **base,
            "checkpoint": manifest["checkpoint"],
            "checkpoint_hash": manifest["checkpoint_hash"],
        }
    for name, model_config in models.items():
        systems[name] = RerankingRetriever(
            systems["hybrid"], units, load_cross_encoder(model_config), 50
        )
    labels = read_labels(Path("data/labels/qasper-v1/dev.jsonl"))
    run = evaluate(
        labels,
        units,
        systems,
        Path("artifacts/runs"),
        metadata["fingerprint"],
        {"retrieval": config, "models": models, "index": metadata["index_fingerprint"]},
    )
    metrics = json.loads((run / "metrics.json").read_text("utf-8"))
    rows = [
        json.loads(line) for line in (run / "predictions.jsonl").read_text("utf-8").splitlines()
    ]
    lookup = {(r["system"], r["query_id"]): r for r in rows}
    comparisons = {}
    for name in models:
        pairs = [
            {
                "family_id": q.family_id,
                "baseline": score_ranking(
                    lookup["untuned", q.query_id]["predicted"], q.relevance, 10
                )["ndcg"],
                "candidate": score_ranking(lookup[name, q.query_id]["predicted"], q.relevance, 10)[
                    "ndcg"
                ],
            }
            for q in labels
            if q.answerable
        ]
        comparisons[name] = paired_family_bootstrap(pairs)
    eligible = [
        name
        for name in models
        if metrics[name]["failure_count"] == 0 and metrics[name]["p95_ms"] <= 1000
    ]
    if not eligible:
        raise ValueError(
            "No cross-encoder candidate meets the predeclared local latency/failure gate"
        )
    selected = max(eligible, key=lambda n: (metrics[n]["ndcg_at_10"], -metrics[n]["p95_ms"]))
    calibration = calibrate_threshold(
        [
            (lookup[selected, q.query_id]["evidence"][0]["reranker_score"], q.answerable)
            for q in labels
        ]
    )
    chosen = dict(models[selected])
    if "checkpoint" in chosen:
        destination = Path("artifacts/deployed") / chosen["checkpoint_hash"][:12]
        if not destination.exists():
            shutil.copytree(chosen["checkpoint"], destination)
        if checkpoint_hash(destination) != chosen["checkpoint_hash"]:
            raise ValueError("deployment copy changed checkpoint bytes")
        chosen["checkpoint"] = destination.as_posix()
    generation = yaml.safe_load(Path("configs/generation.yaml").read_text("utf-8"))
    generation["refusal_threshold"] = calibration["threshold"]
    proposal = {
        "release_id": "qasper-v1-dev-selected",
        "retrieval": config,
        "reranker": chosen,
        "generation": generation,
        "corpus_fingerprint": metadata["fingerprint"],
        "index_fingerprint": metadata["index_fingerprint"],
        "selection_run": run.as_posix(),
        "selected_system": selected,
        "selection_seed": 42,
        "selection_status": (
            "Development-selected proposal; answer evaluation and release freeze pending"
        ),
    }
    Path("configs/release-proposal.yaml").write_text(
        yaml.safe_dump(proposal, sort_keys=False), "utf-8"
    )
    report = {
        "run": run.as_posix(),
        "selected": selected,
        "metrics": metrics,
        "paired_family_intervals": comparisons,
        "calibration": calibration,
        "failed_training_runs": failed_runs,
        "selection_rule": (
            "Primary seed 42; nDCG@10 then latency; "
            "seed repeats assess sensitivity, not seed selection"
        ),
    }
    (run / "comparison.json").write_bytes(canonical(report))
    Path("artifacts/verification/development-selection.json").write_bytes(canonical(report))
    flat = {
        f"{system}.{key}": value
        for system, values in metrics.items()
        for key, value in values.items()
        if isinstance(value, int | float)
    }
    log_mlflow(run, {"purpose": "development model selection"}, flat)
    print(json.dumps({"run": str(run), "selected": selected, "calibration": calibration}))


if __name__ == "__main__":
    main()
