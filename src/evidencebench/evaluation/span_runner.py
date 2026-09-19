"""Run one of three authorized short-span development experiments."""

import argparse
import json
import os
import time
from collections import Counter
from pathlib import Path

import yaml

from evidencebench.evaluation.answers import answer_metrics
from evidencebench.evaluation.selection_runner import validate_dev_roster
from evidencebench.generation_spans import PROMPT_VERSION, VARIANTS, SpanGenerator
from evidencebench.ingestion import canonical, digest, load_units
from evidencebench.labels import read_labels
from evidencebench.tracking import create_run, run_lifecycle


def reserve_variant(root: Path, variant: str):
    if variant not in VARIANTS:
        raise ValueError("unknown experiment variant")
    attempts = root / "attempts"
    attempts.mkdir(parents=True, exist_ok=True)
    try:
        with (attempts / f"{variant}.json").open("x", encoding="utf-8") as stream:
            json.dump({"variant": variant, "consumes_authorized_attempt": True}, stream)
    except FileExistsError as exc:
        raise ValueError("variant attempt already used; all attempts are retained") from exc


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("configs/answer-spans.yaml"))
    parser.add_argument("--variant", required=True, choices=VARIANTS)
    args = parser.parse_args(argv)
    config = yaml.safe_load(args.config.read_text("utf-8"))
    config["generation"]["variant"] = args.variant
    if config["generation"]["prompt_version"] != PROMPT_VERSION:
        raise ValueError("span prompt version mismatch")
    source = Path(config["source_predictions"])
    label_path = Path(config["dev_labels"])
    for path, expected in [
        (source, config["source_sha256"]),
        (label_path, config["dev_labels_sha256"]),
    ]:
        if digest(path.read_bytes()) != expected:
            raise ValueError("development input checksum mismatch")
    rows = [json.loads(line) for line in source.read_text("utf-8").splitlines()]
    labels = read_labels(label_path)
    validate_dev_roster(rows, labels)
    root = Path(config["output_root"])
    units = load_units(Path(config["corpus"]))
    by_text = {}
    for unit in units:
        by_text.setdefault((unit.family_id, unit.text[:1000]), []).append(unit.element_id)
    evidence_maps = {}
    for row in rows:
        packed = row.get("trace", {}).get("packed_evidence", {})
        aliases = {}
        for key, text in packed.items():
            matches = by_text.get((row["family_id"], text), [])
            if len(matches) != 1:
                raise ValueError("packed development passage must map uniquely to corpus")
            aliases[key] = matches[0]
        if not packed and row.get("reason") != "insufficient_evidence":
            raise ValueError("missing original generation context")
        evidence_maps[row["query_id"]] = aliases
    # Reuse only existing caches; no new models or paid requests.
    os.environ["HF_HUB_OFFLINE"] = "1"
    paths = [
        args.config,
        Path(config["protocol"]),
        Path(__file__),
        Path("src/evidencebench/generation_spans.py"),
    ]
    provenance = {str(p): digest(p.read_bytes()) for p in paths}
    reserve_variant(root, args.variant)
    run, manifest = create_run(
        root / args.variant, {**config, "source_hashes": provenance, "split": "dev"}
    )
    candidate_rows = []
    with run_lifecycle(run, manifest, config["max_run_seconds"]) as check_deadline:
        generator = SpanGenerator(config["generation"])
        for index, original in enumerate(rows, 1):
            check_deadline()
            packed = original.get("trace", {}).get("packed_evidence", {})
            started = time.perf_counter()
            row = {
                key: original[key]
                for key in (
                    "query_id",
                    "question",
                    "family_id",
                    "answerable",
                    "answer_criteria",
                    "supporting_evidence",
                )
            }
            if not packed:
                result = dict(
                    status="refused",
                    reason="insufficient_evidence",
                    answer="",
                    evidence_ids=[],
                    refused=True,
                    attempts=0,
                    output_tokens=0,
                )
                trace = {"retrieval_refusal_replayed": True}
            else:
                try:
                    result = generator.generate(original["question"], packed)
                except Exception as exc:
                    result = dict(
                        status="failure", reason=type(exc).__name__, answer="", evidence_ids=[]
                    )
                trace = {**generator.last_trace, "packed_evidence": packed}
            aliases = result.pop("evidence_ids", [])
            row.update(result)
            row.update(
                citation_ids=[evidence_maps[row["query_id"]][key] for key in aliases],
                elapsed_ms=(time.perf_counter() - started) * 1000,
                timing_scope="generation_only_or_replayed_retrieval_refusal",
                trace=trace,
            )
            candidate_rows.append(row)
            with (run / "predictions.jsonl").open("ab") as stream:
                stream.write(canonical(row) + b"\n")
            print(f"{args.variant} dev {index}/{len(rows)}: {row['status']}", flush=True)
        baseline = answer_metrics(rows)
        candidate = answer_metrics(candidate_rows)
        promising = (
            candidate["answerable_token_f1"] > baseline["answerable_token_f1"]
            and candidate["failure_count"] < baseline["failure_count"]
            and candidate["missing_refusal_rate"] <= baseline["missing_refusal_rate"]
        )
        metrics = {
            "baseline": baseline,
            "candidate": candidate,
            "passes_exploration_gate": promising,
            "candidate_statuses": dict(Counter(r["status"] for r in candidate_rows)),
            "candidate_reasons": dict(Counter(r["reason"] for r in candidate_rows if r["reason"])),
            "limitations": (
                "Development replay only. Latency scopes differ; "
                "no deployment or held-out quality claim."
            ),
        }
        (run / "metrics.json").write_bytes(canonical(metrics))
        manifest.update(
            status="complete", predictions_hash=digest((run / "predictions.jsonl").read_bytes())
        )
    print(json.dumps({"run": run.as_posix(), "metrics": metrics}))


if __name__ == "__main__":
    main()
