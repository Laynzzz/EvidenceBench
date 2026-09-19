"""Replay all development retrievals through the separately built Linux service."""

import json
from pathlib import Path

import httpx

from evidencebench.evaluation.runner import aggregate
from evidencebench.ingestion import canonical


def main():
    selection = json.loads(
        Path("artifacts/verification/development-selection.json").read_text("utf-8")
    )
    rows = [
        json.loads(x)
        for x in (Path(selection["run"]) / "predictions.jsonl").read_text("utf-8").splitlines()
    ]
    expected = [r for r in rows if r["system"] == selection["selected"]]
    differences = []
    actual = []
    with httpx.Client(base_url="http://127.0.0.1:8000", timeout=30) as client:
        versions = client.get("/api/v1/models/current").json()
        for row in expected:
            response = client.post("/api/v1/retrieve", json={"query": row["query"], "k": 20})
            response.raise_for_status()
            value = response.json()
            ids = [h["element_id"] for h in value["evidence"]]
            if ids != row["predicted"]:
                differences.append(row["query_id"])
            actual.append(
                {
                    **row,
                    "predicted": ids,
                    "status": "ok",
                    "elapsed_ms": value["timings"]["retrieval_rerank_ms"],
                }
            )
    report = {
        "query_count": len(actual),
        "exact_rank_mismatches": differences,
        "metrics": aggregate(actual),
        "versions": versions,
        "scope": (
            "Windows NumPy baseline versus freshly built Linux PostgreSQL serving, "
            "same selected checkpoint; dev only"
        ),
    }
    Path("artifacts/verification/serving-parity.json").write_bytes(canonical(report))
    Path("artifacts/verification/serving-parity-predictions.jsonl").write_bytes(
        b"\n".join(canonical(r) for r in actual) + b"\n"
    )
    print(
        json.dumps(
            {
                "queries": len(actual),
                "exact_rank_mismatches": len(differences),
                "metrics": report["metrics"],
            }
        )
    )


if __name__ == "__main__":
    main()
