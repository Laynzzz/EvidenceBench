# Fixed-input GPU generation: development gate passed

The single approved Qwen2.5-7B generation comparison completed on RTX 4090 and its
saved results verify. **All eight predeclared development conditions pass.** This
is a candidate for further validation, not a deployed release or a new held-out
test result. Absolute answer quality remains limited.

| Metric, all 50 reused development questions | Original control | Constrained 0.5B baseline | GPU 7B candidate |
|---|---:|---:|---:|
| Answerable token F1, 38 questions | 0.012025 | 0.075424 | 0.123578 |
| Answers | 11 | 28 | 24 |
| Refusals | 18 | 22 | 26 |
| Failures | 21 | 0 | 0 |
| Answer coverage | 22% | 56% | 48% |
| Answers to unanswerable questions / 12 | 3 | 6 | 3 |
| Citation-ID precision | 0.363636 | 0.321429 | 0.458333 |
| Citation-ID recall | 0.068966 | 0.155172 | 0.189655 |

The candidate answers 21 answerable and three unanswerable questions. The 18
threshold refusals are preserved unchanged. On the other 32
queries, it produces 24 answers and eight model refusals. Three previously refused
questions become answers; seven previously answered questions become refusals.
No support checker runs after generation.

## Predeclared conditions

| Condition | Result |
|---|---|
| F1 exceeds original control | Pass |
| Failures do not exceed original control | Pass |
| Unanswerable answers do not exceed original control | Pass, equal at 3/12 |
| Citation-ID precision is at least original control | Pass |
| Retain at least 80% of constrained-baseline F1 | Pass |
| Retain at least 14 answers | Pass, 24 |
| No new failures versus constrained baseline | Pass, zero |
| F1 strictly exceeds constrained baseline | Pass |

The F1 gain over the constrained baseline is **0.048154**. A descriptive paired
paper-family bootstrap (2,000 resamples, seed 42; 38 answerable queries across 26
families) gives a 95% percentile interval of **[-0.022313, 0.125398]**. It includes
zero, so these data do not establish a statistically reliable gain. This analysis
was computed after the run, is not an added acceptance condition, and is not
adjusted for repeated development-set inspection or model selection.

## Execution and verification

- Run: `artifacts/gpu-generation-v1/runs/20260920T145452Z-b1abbfbaf5`.
- Prepared code: `89781c1`; approved snapshot
  `9d18f8259b643720968ae21a5c9b5622a49afe4be1778544325f8abec45d0cdc`.
- One attempt, **32 generation calls**, **380 actual output tokens**,
  **2,048 reserved output tokens**, no retries, warmups or extra benchmarks.
- Successful worker supervision: **50.750 seconds**, including worker validation
  and model loading, excluding CPU preflight and later verification.
- Generation-only p50/p95 over the 32 invoked queries: **0.381 / 1.093 seconds**.
  These are not end-to-end serving timings; unchanged refusal rows retain their
  historical traces and are excluded from these percentiles.
- Qwen2.5-7B revision `a09a35458c702b33eeacc393d103063234e8bc28`, offline,
  CUDA device 0, RTX 4090, BF16, no quantization or offload.
- Free VRAM before load: 24,104,665,088 bytes; peak VRAM was not measured.
- **$0 external spend**. No training, new retrieval, package changes, downloads,
  label changes, final-test access or deployment.

Transformers emitted the same deprecated dtype-argument and inactive sampling-
parameter notices as the support-checker run. Greedy execution completed without
runtime failures or query timeouts. The approved implementation remained unchanged.

Launch verification passed, followed by a separate read-only verification:

```powershell
.venv/Scripts/python.exe -X utf8 scripts/run_gpu_generation.py --verify
```

Verification checks source/config/model/runtime/input hashes, exact approval,
single attempt, supervisor completion, budget and output checksums. It reconstructs
all 50 predictions and metrics using unchanged scoring inputs. The
[structured report](gpu-generation-development.json) includes per-query outputs,
timings, paired F1 values, bootstrap settings and retained artifact hashes. The
[authorization](gpu-generation-authorization.json) records user approval. The
preparation's 144 passing software tests are historical test evidence; this step
verifies actual model execution without repeating the software suite.

## Interpretation and next gate

Keeping evidence and the output contract fixed produced higher measured reference
agreement with fewer answers on unanswerable questions. Weights, precision,
hardware and runtime all changed, so this cannot isolate parameter count. It also
does not establish semantic correctness: some outputs remain incomplete or answer
the wrong question, including a score where model names were requested. The
previously flagged TF-IDF answerability conflict remains unaltered and counted.

The [24-answer human review packet](gpu-generation-human-review.md) includes every
emitted answer and its actual citations while masking benchmark labels and prior
model outputs. The [response template](gpu-generation-human-review-template.json)
is blank. An independent human review is still needed for claim-support judgments
under the plan; these files do not claim that review occurred. The packet covers
emitted claims, not a full semantic audit of refusals.

The candidate is frozen as development evidence. The 100-question final test stays
unused and the original service remains unchanged. Phase 4 is not fully accepted,
and no deployment or public performance claim follows automatically from this gate
pass. The approved allowance is consumed; any new model run or final-test access
requires a separately prepared scope and explicit approval.
