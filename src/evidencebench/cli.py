"""Reproducible batch commands. Run from the repository root."""

import argparse
import json
import sys
from pathlib import Path

import yaml

from evidencebench.ingestion import build_corpus, load_units


def main() -> None:
    parser = argparse.ArgumentParser(prog="evidencebench")
    commands = parser.add_subparsers(dest="command", required=True)
    build = commands.add_parser("build", help="Build a new immutable corpus directory")
    build.add_argument("--config", type=Path, required=True)
    build.add_argument("--output", type=Path)
    build.add_argument("--no-fetch", action="store_true")
    inspect = commands.add_parser("inspect", help="Resolve evidence to source PDF pages")
    inspect.add_argument("--corpus", type=Path)
    inspect.add_argument("--run", type=Path)
    inspect.add_argument("--query-id")
    inspect.add_argument("--document")
    inspect.add_argument("--page", type=int)
    index = commands.add_parser("index", help="Build a pinned dense index")
    index.add_argument("--config", type=Path, default=Path("configs/retrieval.yaml"))
    search = commands.add_parser("search", help="Inspect retrieval without evaluating labels")
    search.add_argument("--config", type=Path, default=Path("configs/retrieval.yaml"))
    search.add_argument("--corpus", type=Path)
    search.add_argument("--query", required=True)
    search.add_argument("--system", choices=["bm25", "dense", "hybrid"], default="bm25")
    search.add_argument("--k", type=int, default=5)
    evaluate_parser = commands.add_parser("evaluate", help="Run reviewed development baselines")
    evaluate_parser.add_argument("--config", type=Path, default=Path("configs/evaluation.yaml"))
    evaluate_parser.add_argument("--split", choices=["dev", "test"], default="dev")
    evaluate_parser.add_argument(
        "--suite",
        choices=["retrieval-baselines", "rerankers", "answers", "release"],
        default="retrieval-baselines",
    )
    training = commands.add_parser(
        "train", help="Train with training-only pairs and development selection"
    )
    training.add_argument("--config", type=Path, default=Path("configs/training.yaml"))
    training.add_argument("--smoke", action="store_true")
    training.add_argument("--query-count", type=int)
    training.add_argument("--negative-method", choices=["random", "hard"])
    recalc = commands.add_parser("recalculate", help="Recompute metrics from saved predictions")
    recalc.add_argument("--run", type=Path, required=True)
    labels = commands.add_parser(
        "validate-labels", help="Check references, splits, and review status"
    )
    labels.add_argument("--labels", type=Path, required=True)
    labels.add_argument("--corpus", type=Path, default=Path("data/processed/nist-v1"))
    labels.add_argument("--allow-drafts", action="store_true")
    args = parser.parse_args()
    try:
        if args.command == "train":
            from evidencebench.training import train

            config = yaml.safe_load(args.config.read_text("utf-8"))
            if args.query_count:
                config["query_count"] = args.query_count
            if args.negative_method:
                config["negative_method"] = args.negative_method
            print(json.dumps({"run": str(train(config, smoke=args.smoke))}))
        elif args.command == "index":
            from evidencebench.indexing import build_index

            result = build_index(yaml.safe_load(args.config.read_text("utf-8")))
            print(
                json.dumps(
                    {
                        key: result[key]
                        for key in (
                            "fingerprint",
                            "dimension",
                            "embedding_count",
                            "elapsed_seconds",
                        )
                    }
                )
            )
        elif args.command == "search":
            from evidencebench.pipelines import load_retrievers

            config = yaml.safe_load(args.config.read_text("utf-8"))
            if args.corpus:
                config["corpus"] = str(args.corpus)
            units, retrievers, _ = load_retrievers(config, include_dense=args.system != "bm25")
            lookup = {u.element_id: u for u in units}
            hits = retrievers[args.system].retrieve(args.query, {}, args.k)
            print(
                json.dumps(
                    [
                        {
                            **hit.model_dump(),
                            "text": lookup[hit.element_id].text,
                            "source_url": str(lookup[hit.element_id].source_url),
                        }
                        for hit in hits
                    ],
                    indent=2,
                )
            )
        elif args.command == "validate-labels":
            from evidencebench.labels import read_labels, validate_labels

            print(
                json.dumps(
                    validate_labels(
                        read_labels(args.labels), load_units(args.corpus), args.allow_drafts
                    )
                )
            )
        elif args.command == "evaluate":
            from evidencebench.evaluation.runner import evaluate
            from evidencebench.labels import read_labels
            from evidencebench.pipelines import load_retrievers

            if args.suite == "release":
                if args.split != "test":
                    raise ValueError("release suite requires test split")
                from evidencebench.final_evaluation import run_final

                print(json.dumps(run_final()))
                return
            if args.suite == "answers" and args.split == "dev":
                from evidencebench.evaluation.generation_runner import main as answer_main

                answer_main(["--release", "configs/release.yaml"])
                return
            if args.split == "test":
                raise ValueError(
                    "final test disabled until reviewed labels and release protocol are frozen"
                )
            config = yaml.safe_load(args.config.read_text("utf-8"))
            retrieval = yaml.safe_load(Path(config["retrieval_config"]).read_text("utf-8"))
            if config.get("protocol"):
                from evidencebench.protocol import verify_protocol

                verify_protocol(Path(config["protocol"]))
            units, retrievers, metadata = load_retrievers(retrieval)
            reranker = None
            if args.suite == "rerankers":
                from evidencebench.reranking import RerankingRetriever, load_cross_encoder

                reranker = yaml.safe_load(Path(config["reranker_config"]).read_text("utf-8"))
                model = load_cross_encoder(reranker)
                retrievers["cross-encoder"] = RerankingRetriever(
                    retrievers["hybrid"], units, model, retrieval["candidate_k"]
                )
            labels = read_labels(Path(config["dev_labels"]))
            run = evaluate(
                labels,
                units,
                retrievers,
                Path(config["runs_dir"]),
                metadata["fingerprint"],
                provenance={
                    "retrieval": retrieval,
                    "index": metadata["index_fingerprint"],
                    "reranker": reranker,
                },
            )
            print(json.dumps({"run": str(run)}))
        elif args.command == "recalculate":
            from evidencebench.evaluation.runner import recalculate

            print(json.dumps(recalculate(args.run), indent=2))
        elif args.command == "build":
            config = yaml.safe_load(args.config.read_text("utf-8"))
            result = build_corpus(config, args.output or Path(config["output"]), not args.no_fetch)
            print(json.dumps(result, indent=2))
        elif args.command == "inspect":
            if args.run:
                if args.query_id:
                    rows = [
                        json.loads(line)
                        for line in (args.run / "predictions.jsonl").read_text("utf-8").splitlines()
                    ]
                    result = [row for row in rows if row["query_id"] == args.query_id]
                else:
                    result = {
                        "manifest": json.loads((args.run / "manifest.json").read_text("utf-8")),
                        "metrics": json.loads((args.run / "metrics.json").read_text("utf-8")),
                    }
                print(json.dumps(result, ensure_ascii=True, indent=2))
                return
            if args.corpus is None:
                raise ValueError("inspect requires --corpus or --run")
            units = load_units(args.corpus)
            rows = [
                u.model_dump(mode="json")
                for u in units
                if (args.document is None or u.document_id == args.document)
                and (args.page is None or u.page <= args.page <= (u.page_end or u.page))
            ]
            if not rows:
                raise ValueError("no evidence matches this document/page")
            print(json.dumps(rows, indent=2, ensure_ascii=True))
    except (ValueError, OSError, KeyError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc


if __name__ == "__main__":
    main()
