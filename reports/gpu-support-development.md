# GPU support checker: completed, quality gate failed

The approved Qwen2.5-7B evaluation completed on the RTX 4090 and its saved results
verify. It labeled **24 answers UNSUPPORTED and four SUPPORTED**, with no runtime
failures. This reduces answers to unanswerable questions but removes most answer
coverage and token F1. **The checker is not promoted.**

| Metric, all 50 reused development questions | Control | Unfiltered / CPU checker | GPU checker |
|---|---:|---:|---:|
| Answerable token F1, 38 questions | 0.012025 | 0.075424 | 0.013068 |
| Answers | 11 | 28 | 4 |
| Refusals | 18 | 22 | 46 |
| Runtime failures | 21 | 0 | 0 |
| Answers to unanswerable questions / 12 | 3 | 6 | 1 |
| Answer coverage | 22% | 56% | 8% |
| Citation-ID precision | 0.363636 | 0.321429 | 0.250000 |
| Citation-ID recall | 0.068966 | 0.155172 | 0.017241 |

The previous CPU checker accepted every answer, so its metrics equal the unfiltered
candidate. The GPU checker rejected 19 of 22 answers on answerable questions and
five of six on unanswerable questions. These are question-level benchmark labels:
an answerable question does not imply the proposed answer is correct or supported
by the actual packed citations. The automated checker verdicts are not human labels.

## All predeclared gate conditions

| Condition | Result |
|---|---|
| F1 exceeds control | Pass |
| Failures do not increase versus control | Pass |
| No new checker failures | Pass |
| Unanswerable answers do not increase versus control | Pass |
| Citation-ID precision is not lower than control | **Fail** |
| Retain at least 80% of unfiltered F1 | **Fail** |
| Retain at least half of the 28 answers | **Fail** |

Only four of seven conditions pass. The tiny F1 difference from control does not
establish a statistically reliable gain. No gate was weakened and no alternative
threshold or prompt was selected after inspecting these results. A refusal-heavy
system can reduce unsupported-answer opportunities while being substantially less
useful; the retention guards catch that trade-off.

## Execution and verification

- Run: `artifacts/gpu-support-v1/runs/20260920T025107Z-d0f904ba5f`.
- Prepared implementation: `b5747c1`; exact approved snapshot:
  `dea56f72d2ad0dd731bd360dac28e199c1e4c4ecf9a01803e0d5f4d5ccbffb58`.
- Qwen2.5-7B revision `a09a35458c702b33eeacc393d103063234e8bc28`,
  offline CUDA device 0, BF16, RTX 4090, no offload or quantization.
- One attempt, **28 generation calls**, **84 actual output tokens**,
  **224 reserved output tokens**, no retries, warmups or additional benchmarks.
- Successful worker supervision: **38.765 seconds**, including worker validation
  and model loading. Parent preflight and later verification are excluded.
- Checker-only latency: **0.135 seconds p50 / 0.207 seconds p95** over 28 checks.
  These are not end-to-end serving measurements or a controlled CPU/GPU speedup.
- **$0 external spend**. No training, new retrieval or final-test access.

The actual run establishes that this pinned configuration loaded and executed on
this machine. It does not establish fit for longer inputs, larger batches or training.
The free-memory check observed 24,104,665,088 bytes before loading; peak VRAM was not
measured. Transformers emitted a deprecated `torch_dtype` argument warning and a
notice that sampling parameters may be ignored under greedy generation. All 28
decisions were valid and no call timed out; the approved implementation was unchanged.

The launch verified its results, followed by a separate read-only verification:

```powershell
.venv/Scripts/python.exe -X utf8 scripts/run_gpu_support_filter.py --verify
```

Verification checks the exact approval, source/config/model/runtime/input hashes,
single attempt, successful supervisor, usage, output checksums and recomputed
predictions/metrics, including unchanged scoring inputs. The
[structured report](gpu-support-development.json) records decisions, per-check
timings, answerability breakdown and hashes of retained artifacts. The
[authorization](gpu-support-authorization.json) records the user's approval.
The preparation's 125 passing software tests are historical evidence; this step
verified real execution rather than rerunning the software test suite.

## Interpretation and remaining work

The fixed small checker accepted everything; this larger checker rejected most
answers. Neither configuration meets the project's acceptance gate. Size alone
is not an established solution: weights, precision, hardware and runtime all
changed, and this comparison cannot isolate their effects.

The [saved retrieval audit](fresh-selection-audit.md) already shows missing gold
evidence after selection and packing. A support-only checker cannot recover that
evidence or repair an answer. Before choosing another model experiment, inspect
rejected answers against their actual citations and original papers to separate
valid refusals, checker errors, generation errors and packing omissions. Such an
inspection must be labeled accurately; agent analysis does not satisfy the
independent human generated-claim review requirement.

The single allowance is consumed. Its run and partial-accounting safeguards are
retained, and no background GPU worker remains after successful process exit.
The original service is unchanged, the 100-question final test remains unused,
and Phase 4 answer-quality acceptance and independent human review remain incomplete.
Another model run requires a new concrete proposal and explicit approval.
