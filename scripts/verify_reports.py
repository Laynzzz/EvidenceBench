"""Post-evaluation report verification from saved outputs; never runs or selects models."""

import json
import statistics
from pathlib import Path

from evidencebench.evaluation.answers import answer_metrics
from evidencebench.evaluation.metrics import paired_family_bootstrap, score_ranking
from evidencebench.evaluation.runner import recalculate
from evidencebench.ingestion import digest
from evidencebench.protocol import verify_protocol


def read(path):
    return json.loads(Path(path).read_text("utf-8"))


def main():
    verify_protocol(Path("data/manifests/release-lock.json"))
    report = read("reports/final-evaluation.json")
    assert recalculate(Path(report["ranking_run"])) == report["ranking_metrics"]
    run = Path(report["answer_run"])
    predictions = (run / "predictions.jsonl").read_bytes()
    assert digest(predictions) == read(run / "manifest.json")["predictions_hash"]
    assert (
        answer_metrics([json.loads(x) for x in predictions.splitlines()])
        == report["answer_metrics"]
    )
    rows = [
        json.loads(x)
        for x in (Path(report["ranking_run"]) / "predictions.jsonl").read_text("utf-8").splitlines()
    ]
    lookup = {(r["system"], r["query_id"]): r for r in rows}
    pairs = [
        {
            "family_id": r["family_id"],
            "baseline": score_ranking(
                lookup["untuned", r["query_id"]]["predicted"], r["relevance"], 10
            )["ndcg"],
            "candidate": score_ranking(r["predicted"], r["relevance"], 10)["ndcg"],
        }
        for r in rows
        if r["system"] == "selected" and r["answerable"]
    ]
    assert paired_family_bootstrap(pairs) == report["selected_vs_untuned_family_bootstrap"]
    # Use the recorded pre-test experiment roster, not a changing directory glob.
    snapshot = read("reports/experiment-summary.json")
    assert recalculate(Path(snapshot["development"]["run"])) == snapshot["development"]["metrics"]
    repeats = {}
    for experiment in snapshot["training"]:
        manifest = read(Path(experiment["run"]) / "manifest.json")
        assert experiment["ndcg"] == manifest.get("dev_ndcg_at_10")
        if (
            experiment["status"] == "complete"
            and not experiment["smoke"]
            and experiment["queries"] == 200
            and experiment["negative_method"] == "hard"
        ):
            if experiment["seed"] in repeats:
                raise ValueError("duplicate seed in original uncertainty roster")
            repeats[experiment["seed"]] = experiment["ndcg"]
    assert set(repeats) == {42, 43, 44}
    print(
        json.dumps(
            {
                "ranking_answer_bootstrap_and_development_reports": "verified",
                "original_three_seed_mean": statistics.mean(repeats.values()),
                "original_three_seed_sample_sd": statistics.stdev(repeats.values()),
            }
        )
    )


if __name__ == "__main__":
    main()
