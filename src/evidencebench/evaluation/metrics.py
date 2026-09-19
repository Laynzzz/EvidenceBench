"""Explicit denominators: positive grades count as relevant; no positives => no ranking score."""

import math
from collections import defaultdict
from typing import Any

import numpy as np


def score_ranking(
    predicted: list[str], relevance: dict[str, int], k: int = 10
) -> dict[str, float] | None:
    if k < 1 or any(grade not in (0, 1, 2) for grade in relevance.values()):
        raise ValueError("invalid metric cutoff or relevance grade")
    if len(set(predicted)) != len(predicted):
        raise ValueError("duplicate predictions")
    relevant = {key for key, grade in relevance.items() if grade > 0}
    if not relevant:
        return None
    top = predicted[:k]
    recall = len(set(top) & relevant) / len(relevant)
    mrr = next((1 / rank for rank, key in enumerate(predicted, 1) if key in relevant), 0.0)
    dcg = sum((2 ** relevance.get(key, 0) - 1) / math.log2(i + 2) for i, key in enumerate(top))
    ideal = sum(
        (2**grade - 1) / math.log2(i + 2)
        for i, grade in enumerate(sorted(relevance.values(), reverse=True)[:k])
    )
    return {"recall": recall, "mrr": mrr, "ndcg": dcg / ideal}


def paired_family_bootstrap(
    rows: list[dict[str, Any]], samples: int = 2000, seed: int = 42
) -> dict[str, Any]:
    if not rows or samples < 1:
        raise ValueError("bootstrap needs paired rows and positive sample count")
    groups: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        value = float(row["candidate"]) - float(row["baseline"])
        if not math.isfinite(value):
            raise ValueError("nonfinite paired score")
        groups[row["family_id"]].append(value)
    keys = sorted(groups)
    rng = np.random.default_rng(seed)
    estimates = []
    for _ in range(samples):
        chosen = rng.integers(0, len(keys), size=len(keys))
        values = [v for i in chosen for v in groups[keys[i]]]
        estimates.append(float(np.mean(values)))
    return {
        "delta": float(np.mean([v for values in groups.values() for v in values])),
        "low": float(np.quantile(estimates, 0.025)),
        "high": float(np.quantile(estimates, 0.975)),
        "family_count": len(keys),
        "query_count": len(rows),
        "samples": samples,
        "seed": seed,
        "warning": "Few families; interval may be unstable" if len(keys) < 10 else None,
    }
