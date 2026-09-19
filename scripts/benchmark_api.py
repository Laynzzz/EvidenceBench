"""Small localhost workload; stores every status including busy/error responses."""

import json
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import httpx
import numpy as np

from evidencebench.ingestion import canonical

QUERY = (
    "In the paper 'Mining Supervisor Evaluation and Peer Feedback in Performance Appraisals', "
    "What is the average length of the sentences?"
)
REFUSAL = (
    "In the paper 'Prose for a Painting', "
    "How big is English poem description of the painting dataset?"
)


def main():
    base = "http://127.0.0.1:8000"
    rows = []

    def call(name, path, payload=None):
        tick = time.perf_counter()
        with httpx.Client(timeout=45) as client:
            response = (
                client.get(base + path)
                if payload is None
                else client.post(base + path, json=payload)
            )
        row = {
            "case": name,
            "http_status": response.status_code,
            "elapsed_ms": (time.perf_counter() - tick) * 1000,
            "response": response.json(),
        }
        rows.append(row)
        return row

    call("live", "/health/live")
    call("ready", "/health/ready")
    versions = call("versions", "/api/v1/models/current")
    call("first_query_after_start", "/api/v1/query", {"query": QUERY})
    for index in range(5):
        call(f"warm_query_{index}", "/api/v1/query", {"query": QUERY})
    call("refusal", "/api/v1/query", {"query": REFUSAL})
    call("invalid_input", "/api/v1/query", {"query": "x" * 2001})
    call("empty_retrieval", "/api/v1/retrieve", {"query": "example", "document_id": "absent"})
    tick = time.perf_counter()
    with ThreadPoolExecutor(max_workers=4) as pool:
        list(
            pool.map(lambda i: call(f"concurrent_{i}", "/api/v1/query", {"query": QUERY}), range(4))
        )
    concurrent_seconds = time.perf_counter() - tick
    warm = [r["elapsed_ms"] for r in rows if r["case"].startswith("warm_query")]
    report = {
        "versions": versions["response"],
        "rows": rows,
        "warm_p50_ms": float(np.quantile(warm, 0.5)),
        "warm_p95_ms": float(np.quantile(warm, 0.95)),
        "warm_samples": len(warm),
        "concurrency": 4,
        "concurrent_attempted_requests_per_second": 4 / concurrent_seconds,
        "concurrent_successful_requests_per_second": sum(
            r["http_status"] == 200 for r in rows if r["case"].startswith("concurrent_")
        )
        / concurrent_seconds,
        "limitations": (
            "Five repeated warm queries; first request is process-cold, "
            "not filesystem-cache-cold. No production load claim."
        ),
    }
    Path("artifacts/verification/api-benchmark.json").write_bytes(canonical(report))
    print(json.dumps({k: v for k, v in report.items() if k not in ("rows", "versions")}))


if __name__ == "__main__":
    main()
