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
    inspect.add_argument("--corpus", type=Path, required=True)
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
        "--suite", choices=["retrieval-baselines"], default="retrieval-baselines"
    )
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
        if args.command == "index":
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

            if args.split == "test":
                raise ValueError(
                    "final test disabled until reviewed labels and release protocol are frozen"
                )
            config = yaml.safe_load(args.config.read_text("utf-8"))
            retrieval = yaml.safe_load(Path(config["retrieval_config"]).read_text("utf-8"))
            units, retrievers, metadata = load_retrievers(retrieval)
            labels = read_labels(Path(config["dev_labels"]))
            run = evaluate(
                labels,
                units,
                retrievers,
                Path(config["runs_dir"]),
                metadata["fingerprint"],
                provenance={"retrieval": retrieval, "index": metadata["index_fingerprint"]},
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
            units = load_units(args.corpus)
            rows = [
                u.model_dump(mode="json")
                for u in units
                if (args.document is None or u.document_id == args.document)
                and (args.page is None or u.page == args.page)
            ]
            if not rows:
                raise ValueError("no evidence matches this document/page")
            print(json.dumps(rows, indent=2, ensure_ascii=True))
    except (ValueError, OSError, KeyError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc


if __name__ == "__main__":
    main()
