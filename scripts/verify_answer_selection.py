"""Recalculate cycle-2 development results without loading or rerunning a model."""

import json
from pathlib import Path

from evidencebench.evaluation.answers import answer_metrics
from evidencebench.evaluation.selection_runner import validate_dev_roster
from evidencebench.generation_selection import resolve_choice
from evidencebench.ingestion import canonical, digest, load_units
from evidencebench.labels import read_labels
from evidencebench.protocol import verify_protocol


def read(path):
    return json.loads(Path(path).read_text("utf-8"))


def main():
    verify_protocol(Path("data/manifests/release-lock.json"))
    report = read("reports/answer-selection-development.json")
    run = Path(report["candidate_run"])
    manifest = read(run / "manifest.json")
    assert manifest["status"] == "complete"
    config = manifest["config"]
    assert digest(canonical(config)) == manifest["config_hash"]
    assert read(run / "config.json") == config
    assert digest((run / "source.zip").read_bytes()) == manifest["source_archive_hash"]
    assert digest((run / "predictions.jsonl").read_bytes()) == manifest["predictions_hash"]
    baseline_path = Path(config["source_predictions"])
    label_path = Path(config["dev_labels"])
    assert digest(baseline_path.read_bytes()) == config["source_sha256"]
    assert digest(label_path.read_bytes()) == config["dev_labels_sha256"]
    baseline = [json.loads(x) for x in baseline_path.read_text("utf-8").splitlines()]
    candidate = [json.loads(x) for x in (run / "predictions.jsonl").read_text("utf-8").splitlines()]
    labels = read_labels(label_path)
    validate_dev_roster(baseline, labels)
    validate_dev_roster(candidate, labels)
    metrics = read(run / "metrics.json")
    assert answer_metrics(baseline) == metrics["baseline"]
    assert answer_metrics(candidate) == metrics["candidate"]
    assert report["metrics"] == metrics
    corpus = {u.element_id: u for u in load_units(Path(config["corpus"]))}
    originals = {r["query_id"]: r for r in baseline}
    for row in candidate:
        original = originals[row["query_id"]]
        if row["status"] == "answered":
            trace = row["trace"]
            assert trace["packed_evidence"] == original["trace"]["packed_evidence"]
            parsed = resolve_choice(
                trace["raw_generation"], trace["options"], trace["packed_evidence"], row["question"]
            )
            assert parsed["answer"] == row["answer"]
            assert len(row["citation_ids"]) == len(parsed["evidence_ids"]) == 1
            unit = corpus[row["citation_ids"][0]]
            assert unit.family_id == row["family_id"]
            assert unit.text[:1000] == trace["packed_evidence"][parsed["evidence_ids"][0]]
        if row["reason"] == "insufficient_evidence":
            assert original["reason"] == "insufficient_evidence"
    b, c = metrics["baseline"], metrics["candidate"]
    assert metrics["passes_exploration_gate"] == (
        c["answerable_token_f1"] > b["answerable_token_f1"]
        and c["failure_count"] < b["failure_count"]
        and c["missing_refusal_rate"] <= b["missing_refusal_rate"]
    )
    interrupted = Path(report["interrupted_attempt"])
    termination = read(interrupted / "termination.json")
    assert (
        digest((interrupted / "predictions.jsonl").read_bytes())
        == termination["predictions_sha256"]
    )
    print(
        json.dumps(
            {"cycle2_reports_and_citation_provenance": "verified", "queries": len(candidate)}
        )
    )


if __name__ == "__main__":
    main()
