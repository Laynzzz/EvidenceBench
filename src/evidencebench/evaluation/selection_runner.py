"""Replay a checksum-pinned development trace without changing the frozen release."""

import argparse
import json
import os
import time
from collections import Counter
from pathlib import Path

import yaml

from evidencebench.evaluation.answers import answer_metrics
from evidencebench.generation_selection import PROMPT_VERSION, SelectionGenerator
from evidencebench.ingestion import canonical, digest, load_units
from evidencebench.labels import read_labels
from evidencebench.tracking import create_run, run_lifecycle


def validate_dev_roster(rows, labels):
    if not labels or any(label.split != "dev" for label in labels):
        raise ValueError("development labels only")
    lookup = {label.query_id: label for label in labels}
    if len(rows) != len(labels) or {r["query_id"] for r in rows} != set(lookup):
        raise ValueError("exact development roster required")
    for row in rows:
        label = lookup[row["query_id"]]
        expected = dict(
            question=label.text,
            family_id=label.family_id,
            answerable=label.answerable,
            answer_criteria=label.answer_criteria,
            supporting_evidence=label.supporting_evidence,
        )
        if any(row[key] != value for key, value in expected.items()):
            raise ValueError("development metadata mismatch")


def verify_run_budget(root: Path, max_attempts: int):
    manifests = list(root.glob("*/manifest.json"))
    statuses = [json.loads(p.read_text("utf-8"))["status"] for p in manifests]
    if len(manifests) >= max_attempts or "complete" in statuses:
        raise ValueError("cycle 2 run budget already used; retain the original runs")
    for path, status in zip(manifests, statuses, strict=True):
        if status == "running":
            termination = path.parent / "termination.json"
            if (
                not termination.exists()
                or json.loads(termination.read_text("utf-8")).get("status") != "interrupted"
            ):
                raise ValueError("unresolved prior run; confirm termination before retry")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("configs/answer-selection.yaml"))
    args = parser.parse_args(argv)
    config = yaml.safe_load(args.config.read_text("utf-8"))
    if config["generation"]["prompt_version"] != PROMPT_VERSION:
        raise ValueError("selector prompt version mismatch")
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
    verify_run_budget(root, config.get("max_attempts", 1))
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
        Path("src/evidencebench/generation_selection.py"),
    ]
    provenance = {str(p): digest(p.read_bytes()) for p in paths}
    run, manifest = create_run(root, {**config, "source_hashes": provenance, "split": "dev"})
    candidate_rows = []
    with run_lifecycle(run, manifest, config["max_run_seconds"]) as check_deadline:
        generator = SelectionGenerator(config["generation"])
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
            print(f"selector dev {index}/{len(rows)}: {row['status']}", flush=True)
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
