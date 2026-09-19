"""Verify all retained cycle-3 experiments without rerunning model inference."""

import json
from pathlib import Path

from evidencebench.evaluation.answers import answer_metrics
from evidencebench.evaluation.selection_runner import validate_dev_roster
from evidencebench.generation_spans import VARIANTS, build_spans, resolve_span
from evidencebench.ingestion import canonical, digest, load_units
from evidencebench.labels import read_labels
from evidencebench.protocol import verify_protocol


def read(path):
    return json.loads(Path(path).read_text("utf-8"))


def main():
    verify_protocol(Path("data/manifests/release-lock.json"))
    report = read("reports/answer-spans-development.json")
    assert set(report["experiments"]) <= set(VARIANTS)
    if report["status"] == "complete":
        assert set(report["experiments"]) == set(VARIANTS)
        assert report["attempts_used"] == 3
    completed = {}
    model_calls = 0
    for variant, record in report["experiments"].items():
        run = Path(record["run"])
        manifest = read(run / "manifest.json")
        config = manifest["config"]
        assert config["generation"]["variant"] == variant
        assert digest(canonical(config)) == manifest["config_hash"]
        assert read(run / "config.json") == config
        assert digest((run / "source.zip").read_bytes()) == manifest["source_archive_hash"]
        assert (Path(config["output_root"]) / "attempts" / f"{variant}.json").exists()
        assert digest(Path(config["source_predictions"]).read_bytes()) == config["source_sha256"]
        assert digest(Path(config["dev_labels"]).read_bytes()) == config["dev_labels_sha256"]
        if manifest["status"] != "complete":
            assert record["status"] != "complete"
            continue
        assert record["status"] == "complete"
        assert record["run_seconds"] == manifest["total_elapsed_seconds"]
        assert digest((run / "predictions.jsonl").read_bytes()) == manifest["predictions_hash"]
        rows = [json.loads(x) for x in (run / "predictions.jsonl").read_text("utf-8").splitlines()]
        labels = read_labels(Path(config["dev_labels"]))
        baseline = [
            json.loads(x)
            for x in Path(config["source_predictions"]).read_text("utf-8").splitlines()
        ]
        originals = {r["query_id"]: r for r in baseline}
        validate_dev_roster(rows, labels)
        validate_dev_roster(baseline, labels)
        metrics = read(run / "metrics.json")
        assert metrics == record["metrics"]
        assert answer_metrics(rows) == metrics["candidate"]
        assert answer_metrics(baseline) == metrics["baseline"]
        units = {u.element_id: u for u in load_units(Path(config["corpus"]))}
        for row in rows:
            model_calls += row["trace"].get("output_tokens", 0) > 0
            original = originals[row["query_id"]]
            if row["status"] == "answered":
                packed = row["trace"]["packed_evidence"]
                assert packed == original["trace"]["packed_evidence"]
                parsed = resolve_span(
                    row["trace"]["raw_generation"], packed, row["question"], build_spans(packed)
                )
                assert parsed["answer"] == row["answer"]
                assert len(parsed["evidence_ids"]) == len(row["citation_ids"]) == 1
                unit = units[row["citation_ids"][0]]
                assert unit.family_id == row["family_id"]
                assert unit.text[:1000] == packed[parsed["evidence_ids"][0]]
            if row["reason"] == "insufficient_evidence":
                assert original["reason"] == "insufficient_evidence"
        b, c = metrics["baseline"], metrics["candidate"]
        gate = (
            c["answerable_token_f1"] > b["answerable_token_f1"]
            and c["failure_count"] < b["failure_count"]
            and c["missing_refusal_rate"] <= b["missing_refusal_rate"]
        )
        assert gate == metrics["passes_exploration_gate"]
        if gate:
            completed[variant] = c
    expected = (
        max(
            completed,
            key=lambda v: (
                completed[v]["answerable_token_f1"],
                completed[v]["upstream_citation_precision"] or 0,
                -completed[v]["failure_count"],
            ),
        )
        if completed
        else None
    )
    assert report["preferred_development_candidate"] == expected
    if report["status"] == "complete":
        assert report["model_calls"] == model_calls == 93
    print(
        json.dumps(
            {
                "cycle3_reports_and_provenance": "verified",
                "experiments": len(report["experiments"]),
                "preferred_development_candidate": expected,
            }
        )
    )


if __name__ == "__main__":
    main()
