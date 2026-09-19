# ruff: noqa: E501 -- report tables and narrative literals retain readable output
"""Export inspectable development evidence; never reads final labels."""

import json
import statistics
from pathlib import Path

from evidencebench.evaluation.metrics import score_ranking
from evidencebench.ingestion import canonical


def read(path):
    return json.loads(Path(path).read_text("utf-8"))


def main():
    summary = read("artifacts/verification/development-selection.json")
    training = []
    for p in sorted(Path("artifacts/training").glob("*/manifest.json")):
        m = read(p)
        training.append(
            {
                "run": p.parent.as_posix(),
                "status": m["status"],
                "queries": m.get("query_count"),
                "pairs": m.get("pair_count"),
                "seed": m["config"]["seed"],
                "negative_method": m["config"]["negative_method"],
                "smoke": m["config"]["smoke"],
                "ndcg": m.get("dev_ndcg_at_10"),
                "seconds": m.get("elapsed_seconds"),
                "checkpoint_hash": m.get("checkpoint_hash"),
            }
        )
    export = {"development": summary, "training": training}
    Path("reports/experiment-summary.json").write_bytes(canonical(export))
    lines = [
        "# Development experiments",
        "",
        "All model selection uses development data. "
        "38 answerable questions in 21 paper families contribute ranking scores; "
        "12 unanswerable questions contribute failure/latency and refusal evidence.",
        "",
        "| System | nDCG@10 | Recall@10 | p95 ms | Failures |",
        "|---|---:|---:|---:|---:|",
    ]
    for name, m in summary["metrics"].items():
        lines.append(
            f"| {name} | {m['ndcg_at_10']:.4f} | {m['recall_at_10']:.4f} | {m['p95_ms']:.1f} | {m['failure_count']} |"
        )
    lines += [
        "",
        "Primary seed 42 was selected by nDCG, subject to the predeclared 1,000 ms "
        "reranking p95 ceiling and zero failures. All trained candidates use the same "
        "architecture and inference cost. Training size was selected on dev; test does not reselect.",
        "",
        "The selected 200-query hard-negative model improves nDCG by 0.0548 over untuned. "
        "The paired paper-family bootstrap 95% interval is [-0.0301, 0.1474] (2,000 draws, seed 42). "
        "It includes zero; this is not established population-level improvement.",
        "",
        "| Training run | Queries / pairs | Negatives | Seed | Dev nDCG | Status |",
        "|---|---:|---|---:|---:|---|",
    ]
    for r in training:
        value = f"{r['ndcg']:.4f}" if r["ndcg"] is not None else "—"
        lines.append(
            f"| `{Path(r['run']).name}` | {r['queries']} / {r['pairs']} | {r['negative_method']} | {r['seed']} | {value} | {r['status']} {'(smoke)' if r['smoke'] else ''} |"
        )
    repeat = [
        r["ndcg"]
        for r in training
        if r["status"] == "complete"
        and not r["smoke"]
        and r["queries"] == 200
        and r["negative_method"] == "hard"
    ]
    lines += [
        "",
        f"Three-seed mean nDCG {statistics.mean(repeat):.4f}, sample SD {statistics.stdev(repeat):.4f}. "
        "These repeats estimate seed sensitivity on the same development set, not generalization uncertainty.",
        "",
        "50→100→200 queries shows a nearly flat learning curve. Random negatives reach only "
        "0.5168, versus 0.5693 with hard negatives under matched query count and pair count. "
        "Unjudged negatives can still contain relevant evidence; zero exact-answer phrase collisions "
        "in the automated 800-negative audit does not prove they are true negatives.",
        "",
        "One setup run failed before optimization because a replacement model-card object lacked "
        "model registration. It is retained as failed. The corrected run saves/reloads the checkpoint "
        "and checks score parity within 1e-6. Eight of nine training slots were used, including smoke and failure.",
        "",
        "Cached BM25 statistics reproduce all four saved pair sets byte-for-byte; "
        "200-query mining takes 23.78 seconds in the recorded parity check. This is an exact caching "
        "optimization; no before/after speedup ratio is claimed without a controlled timing pair.",
        "",
        "Raw provenance: `artifacts/verification/development-selection.json`, each training "
        "manifest/config/source.zip, local MLflow, and `reports/experiment-summary.json`. "
        "CPU four-thread results on this host are not cloud/GPU throughput measurements.",
    ]
    Path("reports/development-evaluation.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    # Retain all failed development cases, with explicit automated diagnosis limits.
    answers_path = Path("artifacts/verification/development-answers-v3.json")
    if answers_path.exists():
        answer_summary = read(answers_path)
        answer_rows = [
            json.loads(x)
            for x in (Path(answer_summary["run"]) / "predictions.jsonl")
            .read_text("utf-8")
            .splitlines()
        ]
        ranking = [
            json.loads(x)
            for x in (Path(summary["run"]) / "predictions.jsonl").read_text("utf-8").splitlines()
        ]
        lookup = {(r["system"], r["query_id"]): r for r in ranking}
        lines = [
            "# Development failure inspection",
            "",
            "Generated inspection with agent review of the question, human reference, raw output and ranking. "
            "This is not a new human label set or a human semantic-support audit. "
            "Every development query with imperfect baseline/candidate nDCG or an answer/refusal error is retained.",
            "",
        ]
        count = 0
        for row in answer_rows:
            base = lookup["untuned", row["query_id"]]
            candidate = lookup["trained-200-hard", row["query_id"]]
            baseline_score = (
                score_ranking(base["predicted"], base["relevance"], 10)
                if row["answerable"]
                else None
            )
            candidate_score = (
                score_ranking(candidate["predicted"], candidate["relevance"], 10)
                if row["answerable"]
                else None
            )
            if (
                row["answerable"]
                and (
                    row["status"] != "answered"
                    or baseline_score["ndcg"] < 1
                    or candidate_score["ndcg"] < 1
                )
            ) or (not row["answerable"] and row["status"] != "refused"):
                count += 1
                tags = []
                if row["status"] == "failure":
                    tags.append("generation contract failure; see raw output")
                if row["answerable"] and row["status"] == "refused":
                    tags.append("false refusal")
                if not row["answerable"] and row["status"] == "answered":
                    tags.append("missing refusal")
                gold = set(row["supporting_evidence"])
                if row["answerable"] and not gold.intersection(candidate["predicted"][:3]):
                    tags.append("no judged support in top-3 context candidates")
                if candidate_score and candidate_score["ndcg"] < baseline_score["ndcg"]:
                    tags.append("reranking regression")
                if "content missing" in row["answer_criteria"]:
                    tags.append("upstream missing-table annotation ambiguity")
                if row["status"] == "answered":
                    tags.append(
                        "compare answer and reference; valid IDs/quotes do not establish correctness"
                    )
                lines += [
                    f"## {count}. {row['query_id']}",
                    "",
                    row["question"],
                    "",
                    f"Human reference: {row['answer_criteria']}",
                    "",
                    f"Status: {row['status']}; answer: {row['answer']!r}; reason: {row.get('reason')}",
                    "",
                    "Diagnosis: "
                    + "; ".join(tags or ["imperfect ranking; partial support recovered"])
                    + ".",
                    "",
                    "Raw generation: `"
                    + str(row.get("trace", {}).get("raw_generation", "")).replace("`", "\u2032")
                    + "`",
                    "",
                    "Source citations: " + str(row.get("citations", [])),
                    "",
                ]
        lines.insert(
            4,
            f"Reviewed/retained {count} unique failure queries. All 50 development outputs were inspected.\n",
        )
        lines += [
            "## Cross-case conclusions",
            "",
            "Observed patterns include invented/bracketed citation IDs, JSON with incorrect field types, "
            "irrelevant exact quotes, long lists cut by the output limit, and Boolean responses to open questions "
            "(the latter is now rejected in v3). The NUS/ABUS example asks for a difference but receives a single "
            "success rate; this extractive pipeline cannot perform that calculation. A human reference mentions "
            "missing Table 3: it remains unchanged in the frozen labels. Abstract math/reference placeholders and "
            "first-1,000-character context truncation limit answer availability. No claim of semantic support is "
            "derived from this automated report.",
        ]
        Path("reports/development-failures.md").write_text(
            "\n".join(lines) + "\n", encoding="utf-8"
        )
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    primary = [
        r
        for r in training
        if r["status"] == "complete"
        and not r["smoke"]
        and r["seed"] == 42
        and r["negative_method"] == "hard"
    ]
    fig, axes = plt.subplots(1, 2, figsize=(10, 4), layout="constrained")
    axes[0].plot([r["queries"] for r in primary], [r["ndcg"] for r in primary], marker="o")
    axes[0].axhline(
        summary["metrics"]["untuned"]["ndcg_at_10"], color="gray", linestyle="--", label="Untuned"
    )
    axes[0].set(
        xlabel="Training questions",
        ylabel="Development nDCG@10",
        title="Learning curve (seed 42)",
        ylim=(0.45, 0.65),
    )
    axes[0].legend()
    axes[1].bar(
        ["Untuned", "Random negatives", "Hard negatives"],
        [
            summary["metrics"][n]["ndcg_at_10"]
            for n in ["untuned", "trained-200-random", "trained-200-hard"]
        ],
    )
    axes[1].set(
        title="200-question ablation (seed 42)", ylabel="Development nDCG@10", ylim=(0, 0.7)
    )
    fig.savefig("reports/development-comparison.png", dpi=160)


if __name__ == "__main__":
    main()
