# Serving evaluation

The selected release ran locally in Linux Docker on the Windows workstation.
[Raw requests and versions](serving-evaluation.json) include every benchmark response.
Image tested: `sha256:4a7d9ef8cefc0fbb4e079df4c5fa58502b24a76ad5b4121b5fab58fd1a770d9b`.
This image was built from the same inference implementation and release manifest
used by the frozen evaluation; later report/CLI packaging changes do not alter that path.

| Check | Observed result |
|---|---|
| Readiness / liveness / versions | 200; selected QASPER release and model fingerprints |
| First answer after process startup | 15.5 with citations, 4.91 seconds |
| Five repeated warm answers | All 200; p50 3.06 s, p95 3.18 s |
| Unanswerable development question | Explicit refusal, 200, 0.25 s |
| Oversized query | 422 |
| Unknown document filter | 200 with empty evidence |
| Four simultaneous queries | One 200 answer, three logged 429 busy responses |
| Concurrent throughput | 1.22 attempted requests/s; 0.305 successful answers/s |
| DB stopped | Liveness 200, readiness 503, query 503 |
| DB restored | Readiness recovered |
| Previous image/release rollback | Readiness, model metadata and NIST retrieval all 200 |
| Fresh Linux / Windows dev parity | Exact top-20 IDs match on all 50 queries; nDCG 0.5693 |
| Peak app cgroup memory | 3,629,744,128 bytes (3.38 GiB), including accounted cache |

Hardware: i7-13700K, approximately 31.7 GiB host RAM, CPU-only PyTorch. App resource
limit 6 GiB/4 CPUs, DB 1 GiB/2 CPUs. One worker and one inference lock; no request queue.
The answer question is 133 characters and uses three bounded excerpts. The workload
is deliberately small; no production capacity or filesystem-cache-cold latency claim.
“Cold” here means the first request after process startup, with downloaded models
and OS caches already present. Image build/startup is separate from request latency.

For the 50-query Linux retrieval parity workload, p50 was 186.6 ms and p95 274.2 ms.
These stage timings exclude client/network overhead. The warm answer timings include
HTTP/client overhead and generation. Do not compare unlike timing scopes as speedups.

The core behavior is verified by 49 tests, including a real PostgreSQL fixture and
failure contracts. A separate locked base environment also passed all 49 tests, including the final
generation contract fixtures.
The GitHub Actions workflow is configured but has not run remotely. No push/publish
has occurred. See the [runbook](../docs/runbook.md) for exact commands and rollback.

Human semantic-support review remains missing, and generation has many explicit
failures. This deployment demonstrates a working experimental service, not reliable
research-answering quality or production readiness.
