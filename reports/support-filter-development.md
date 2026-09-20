# Support filter: completed, no quality improvement

The single approved support-filter attempt completed and passed saved-artifact
verification. The checker returned **SUPPORTED for all 28 candidate answers**, including
all six answers to upstream-unanswerable questions. It rejected none. The other
22 refusals remained unchanged. The fixed development gate **fails** and the filter
is not promoted.

| Metric, all 50 development questions | Control | Unfiltered | Filtered |
|---|---:|---:|---:|
| Answerable token F1, 38 questions | 0.012025 | 0.075424 | 0.075424 |
| Answers | 11 | 28 | 28 |
| Refusals | 18 | 22 | 22 |
| Failures | 21 | 0 | 0 |
| Answers to unanswerable questions / 12 | 3 | 6 | 6 |
| Citation-ID precision | 0.363636 | 0.321429 | 0.321429 |
| Citation-ID recall | 0.068966 | 0.155172 | 0.155172 |

Five of seven criteria pass, including all three retention/reliability safeguards.
The two unchanged failures are increased unanswerable answers and lower citation-ID
precision relative to control. The filter adds work without changing any answer,
citation, refusal or failure. SUPPORTED is the model's output label, not a verified
semantic judgment. This outcome rejects this particular fixed small-model self-check;
it does not establish that every support-verification approach is ineffective.

## Execution and evidence

- Run: `artifacts/support-filter-v1/runs/20260920T013654Z-10773dc70d`.
- Prepared implementation: `59114e8`; exact approved snapshot
  `aab7753b653b9aaa566d003830220e6e5f13cead1d2cd012e1611e83cd3fd227`.
- One attempt; **28 checker calls**, **84 actual output tokens**, **224 reserved
  maximum output tokens**. No retries, failures or per-check timeouts.
- Supervisor exited successfully after **31.375 seconds**, within 20 minutes.
- Check-only latency on the 28 checked answers: **0.796 s p50, 0.975 s p95**.
  These exclude the original pipeline and are not end-to-end service latency.
- Cached Qwen2.5-0.5B, CPU, four threads, float32, offline loading;
  **$0 external spend**. No retrieval, reranking, embeddings, training or downloads.

Verification recomputed all output transformations and metrics and checked approval
snapshot, source/config/output hashes, model-input hashes, reference preservation,
usage, token traces and successful supervisor completion. The original comparison
also verifies as part of preflight. The [structured report](support-filter-development.json)
includes metrics, decisions, individual check timings and artifact checksums;
[authorization](support-filter-authorization.json) records the user's approval.

```powershell
.venv/Scripts/python.exe -X utf8 scripts/run_support_filter.py --verify
```

The [proposal](../docs/support-filter-proposal.md) and historical
[readiness record](support-filter-readiness.json) stay byte-for-byte frozen.
The approval is consumed; no new run is implied by this report. All artifacts and
the terminated process's attempt record are retained locally. No service or release
behavior changed. These are reused validation/development results, not a new final
test. Final-test examples remain uninspected, and Phase 4's independent human
claim-support requirement remains unmet.

## Updated compute preference

After this approved CPU run, the user confirmed an available RTX 4090 and explicitly
required approval for **every new model training or evaluation run**, including
local GPU work. Read-only `nvidia-smi` inspection confirmed an NVIDIA GeForce RTX 4090,
24,564 MiB reported total memory and driver 591.86. No GPU model workload was launched.
Hardware availability is not authorization for additional attempts. Future GPU
experiments need a concrete design, compatible runtime and a separately approved
budget; earlier CPU results remain historical CPU measurements.
