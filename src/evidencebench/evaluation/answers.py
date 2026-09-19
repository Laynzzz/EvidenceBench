"""Answer-reference agreement, evidence overlap and refusal metrics with fixed denominators."""

import math
import re
from collections import Counter

import numpy as np


def words(text: str) -> list[str]:
    return [w for w in re.findall(r"\w+", text.casefold()) if w not in {"a", "an", "the"}]


def token_f1(prediction: str, reference: str) -> float:
    predicted, expected = words(prediction), words(reference)
    if not predicted or not expected:
        return float(predicted == expected)
    overlap = sum((Counter(predicted) & Counter(expected)).values())
    return 2 * overlap / (len(predicted) + len(expected))


def calibrate_threshold(rows: list[tuple[float, bool]]) -> dict:
    if not rows or not all(math.isfinite(score) for score, _ in rows):
        raise ValueError("calibration requires finite development scores")
    positives, negatives = sum(label for _, label in rows), sum(not label for _, label in rows)
    if not positives or not negatives:
        raise ValueError("calibration requires both answerability classes")
    values = sorted({score for score, _ in rows})
    thresholds = [
        values[0] - 1e-6,
        *[(a + b) / 2 for a, b in zip(values, values[1:], strict=False)],
        values[-1] + 1e-6,
    ]
    results = []
    for threshold in thresholds:
        tpr = sum(score >= threshold and label for score, label in rows) / positives
        tnr = sum(score < threshold and not label for score, label in rows) / negatives
        coverage = sum(score >= threshold for score, _ in rows) / len(rows)
        results.append(
            {
                "threshold": threshold,
                "balanced_accuracy": (tpr + tnr) / 2,
                "evidence_coverage": coverage,
                "answerable_recall": tpr,
                "unanswerable_recall": tnr,
            }
        )
    return max(results, key=lambda r: (r["balanced_accuracy"], r["evidence_coverage"]))


def answer_metrics(rows: list[dict]) -> dict:
    answerable = [r for r in rows if r["answerable"]]
    unanswerable = [r for r in rows if not r["answerable"]]
    answered = [r for r in rows if r["status"] == "answered"]
    correct_cites = sum(
        len(set(r["citation_ids"]) & set(r["supporting_evidence"])) for r in answered
    )
    all_cites = sum(len(set(r["citation_ids"])) for r in answered)
    scores = [
        max(
            token_f1(r["answer"], alternative)
            for alternative in r["answer_criteria"].split(" | Alternative human answer: ")
        )
        if r["status"] == "answered"
        else 0.0
        for r in answerable
    ]
    return {
        "query_count": len(rows),
        "answerable_count": len(answerable),
        "unanswerable_count": len(unanswerable),
        "answered_count": len(answered),
        "failure_count": sum(r["status"] == "failure" for r in rows),
        "answer_coverage": len(answered) / len(rows),
        "answerable_token_f1": float(np.mean(scores)) if scores else None,
        "false_refusal_rate": sum(r["status"] == "refused" for r in answerable) / len(answerable)
        if answerable
        else None,
        "answerable_failure_rate": sum(r["status"] == "failure" for r in answerable)
        / len(answerable)
        if answerable
        else None,
        "unanswerable_refusal_recall": sum(r["status"] == "refused" for r in unanswerable)
        / len(unanswerable)
        if unanswerable
        else None,
        "missing_refusal_rate": sum(r["status"] == "answered" for r in unanswerable)
        / len(unanswerable)
        if unanswerable
        else None,
        "upstream_citation_precision": correct_cites / all_cites if all_cites else None,
        "upstream_citation_recall": (
            correct_cites / sum(len(set(r["supporting_evidence"])) for r in answerable)
        )
        if answerable
        else None,
        "p50_ms": float(np.quantile([r["elapsed_ms"] for r in rows], 0.5)),
        "p95_ms": float(np.quantile([r["elapsed_ms"] for r in rows], 0.95)),
        "limitations": (
            "Token overlap and evidence-ID overlap are reference agreement, "
            "not human semantic judgments of generated claims."
        ),
    }
