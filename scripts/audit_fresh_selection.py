"""Post-hoc audit of the fixed fresh-validation run; no model calls or test examples."""

import argparse
import copy
import json
import math
import statistics
from collections import Counter
from pathlib import Path

from evidencebench.evaluation.answers import answer_metrics
from evidencebench.evaluation.metrics import score_ranking
from evidencebench.ingestion import canonical, digest

RUN = Path("artifacts/fresh-validation-v1/runs/20260919T233427Z-ddfba1b48e")
OUTPUT = Path("reports/fresh-selection-audit.json")


def auc(positive, negative):
    """Probability a positive score exceeds a negative, with half credit for ties."""
    if not positive or not negative:
        return None
    return sum((a > b) + 0.5 * (a == b) for a in positive for b in negative) / (
        len(positive) * len(negative)
    )


def quality(rows):
    return {
        k: v
        for k, v in answer_metrics(rows).items()
        if k not in {"p50_ms", "p95_ms", "limitations"}
    }


def passes(control, candidate):
    precision = [r["upstream_citation_precision"] for r in (control, candidate)]
    return (
        candidate["answerable_token_f1"] > control["answerable_token_f1"]
        and candidate["failure_count"] <= control["failure_count"]
        and candidate["missing_refusal_rate"] <= control["missing_refusal_rate"]
        and all(p is not None for p in precision)
        and precision[1] >= precision[0]
    )


def analyze(control, candidate, threshold):
    if not control or len(control) != len(candidate) or not math.isfinite(threshold):
        raise ValueError("finite threshold and nonempty paired rows required")
    ids = [r["query_id"] for r in control]
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate query IDs")
    records = []
    for a, b in zip(control, candidate, strict=True):
        for field in ("query_id", "family_id", "answerable", "supporting_evidence", "trace"):
            if field == "trace":
                same = all(
                    a[field][key] == b[field][key]
                    for key in ("pre_ids", "post_ids", "post_ranking", "packed_ids")
                )
            else:
                same = a[field] == b[field]
            if not same:
                raise ValueError("unpaired rows or evidence")
        trace = a["trace"]
        pre, post, packed = (trace[k] for k in ("pre_ids", "post_ids", "packed_ids"))
        if (
            not post
            or len(pre) != len(set(pre))
            or len(post) != len(set(post))
            or set(pre) != set(post)
            or [h["element_id"] for h in trace["post_ranking"]] != post
        ):
            raise ValueError("complete, unique rankings with identical candidate pools required")
        scores = [h["reranker_score"] for h in trace["post_ranking"]]
        if any(not isinstance(s, (int, float)) or not math.isfinite(s) for s in scores):
            raise ValueError("nonfinite reranker score")
        if scores != sorted(scores, reverse=True):
            raise ValueError("reranker scores are not descending")
        if packed != (post[:3] if scores[0] >= threshold else []):
            raise ValueError("packing differs from frozen policy")
        gold = set(a["supporting_evidence"])
        if bool(gold) != a["answerable"]:
            raise ValueError("answerability and evidence disagree")
        records.append(
            {
                "query_id": a["query_id"],
                "family_id": a["family_id"],
                "answerable": a["answerable"],
                "top_score": scores[0],
                "pre_first_gold_rank": next((i for i, p in enumerate(pre, 1) if p in gold), None),
                "post_first_gold_rank": next((i for i, p in enumerate(post, 1) if p in gold), None),
                "gold_count": len(gold),
                "packed_gold_count": len(gold & set(packed)),
                "threshold_pass": bool(packed),
            }
        )
    positives = [r for r in control if r["answerable"]]
    positive_scores = [r["top_score"] for r in records if r["answerable"]]
    negative_scores = [r["top_score"] for r in records if not r["answerable"]]
    if not positives or not negative_scores:
        raise ValueError("both answerability classes required")

    def rank_summary(key, k):
        values = [
            score_ranking(r["trace"][key], dict.fromkeys(r["supporting_evidence"], 1), k)
            for r in positives
        ]
        return {
            "macro_recall": statistics.mean(v["recall"] for v in values),
            "binary_ndcg": statistics.mean(v["ndcg"] for v in values),
            "questions_with_any_gold": sum(v["recall"] > 0 for v in values),
            "questions_with_all_gold": sum(v["recall"] == 1 for v in values),
        }

    ranking = {
        stage: {str(k): rank_summary(key, k) for k in (1, 3, 5, 10, 20, 50)}
        for stage, key in (("pre", "pre_ids"), ("post", "post_ids"))
    }
    ranking["packed"] = rank_summary("packed_ids", 3)
    transitions = Counter()
    for r in positives:
        gold = set(r["supporting_evidence"])
        before = bool(gold & set(r["trace"]["pre_ids"][:3]))
        after = bool(gold & set(r["trace"]["post_ids"][:3]))
        transitions[f"{'hit' if before else 'miss'}_to_{'hit' if after else 'miss'}"] += 1
    confusion = {
        f"{label}_{action}": sum(
            r["answerable"] == answerable and r["threshold_pass"] == accepted for r in records
        )
        for label, answerable in (("answerable", True), ("unanswerable", False))
        for action, accepted in (("pass", True), ("refuse", False))
    }
    baseline = quality(control)
    cutoffs = sorted(
        {
            threshold,
            *(
                math.nextafter(r["top_score"], math.inf)
                for r, c in zip(records, candidate, strict=True)
                if c["status"] == "answered"
            ),
        }
    )
    replay = []
    for cutoff in cutoffs:
        if cutoff < threshold:
            raise ValueError("cannot replay answers below the frozen threshold")
        filtered = copy.deepcopy(candidate)
        removed = []
        for r, c in zip(records, filtered, strict=True):
            if c["status"] == "answered" and r["top_score"] < cutoff:
                removed.append(c["query_id"])
                c.update(
                    status="refused", answer="", citation_ids=[], reason="posthoc_score_filter"
                )
        metrics = quality(filtered)
        replay.append(
            {
                "threshold": cutoff,
                "removed_answer_ids": removed,
                "metrics": metrics,
                "passes_original_gate": passes(baseline, metrics),
            }
        )
    return {
        "scope": "Post-hoc development diagnosis; no selected replacement or new model evaluation",
        "query_count": len(control),
        "answerable_count": len(positives),
        "frozen_threshold": threshold,
        "ranking": ranking,
        "top3_hit_transitions": dict(sorted(transitions.items())),
        "score_separation": {
            "auc": auc(positive_scores, negative_scores),
            **{
                label: {
                    "count": len(values),
                    "min": min(values),
                    "median": statistics.median(values),
                    "max": max(values),
                }
                for label, values in (
                    ("answerable", positive_scores),
                    ("unanswerable", negative_scores),
                )
            },
        },
        "threshold_confusion": confusion,
        "higher_threshold_replay": replay,
        "replay_gate_pass_count": sum(r["passes_original_gate"] for r in replay),
        "records": records,
        "limitations": [
            "Support IDs have binary relevance, not the original graded ranking labels.",
            "Ranking/packing uses paragraph IDs; it does not measure clipping or semantic support.",
            "Score AUC measures upstream answerability, not generated-answer correctness.",
            "Replay only suppresses saved answers; existing refusals/failures remain.",
            "Lower cutoffs or changed contexts need inference to measure answer quality.",
            "All cutoffs are post-hoc diagnostics; none is independently validated or selected.",
        ],
    }


def persist(path, result, check):
    data = canonical(result) + b"\n"
    if check or path.exists():
        if path.read_bytes() != data:
            raise ValueError("retained audit differs; refusing to overwrite")
    else:
        with path.open("xb") as stream:
            stream.write(data)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Recompute and compare without writes")
    args = parser.parse_args()
    # Only this known validation run is accepted. No arbitrary label or run paths.
    from evidencebench.evaluation.fresh_runner import CORPUS, LABELS, preflight
    from evidencebench.evaluation.fresh_verification import verify_run
    from evidencebench.ingestion import load_units
    from evidencebench.labels import read_labels

    manifest = json.loads((RUN / "manifest.json").read_text("utf-8"))
    if manifest["config"] != preflight():
        raise ValueError("frozen run differs from current verified inputs")
    verify_run(RUN, read_labels(LABELS), load_units(CORPUS))
    rows = {
        v: [json.loads(line) for line in (RUN / f"{v}.jsonl").read_text("utf-8").splitlines()]
        for v in ("control", "constrained")
    }
    result = analyze(
        rows["control"],
        rows["constrained"],
        manifest["config"]["release"]["generation"]["refusal_threshold"],
    )
    result.update(
        run=RUN.as_posix(),
        model_calls=0,
        downloads=0,
        external_spend_usd=0,
        audit_source_sha256=digest(Path(__file__).read_bytes()),
        input_sha256={
            name: digest((RUN / name).read_bytes())
            for name in ("manifest.json", "control.jsonl", "constrained.jsonl")
        },
    )
    persist(OUTPUT, result, args.check)
    print(
        json.dumps(
            {
                "status": "verified" if args.check else "written",
                "report": OUTPUT.as_posix(),
                "ranking": result["ranking"],
                "score_separation": result["score_separation"],
                "threshold_confusion": result["threshold_confusion"],
                "top3_hit_transitions": result["top3_hit_transitions"],
                "replay_gate_pass_count": result["replay_gate_pass_count"],
                "model_calls": 0,
            }
        )
    )


if __name__ == "__main__":
    main()
