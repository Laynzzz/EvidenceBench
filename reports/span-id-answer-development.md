# Source span-ID comparison: improved development metrics, gate failed

The single approved RTX 4090 run completed and its saved results verify.
**Nine of eleven predeclared conditions pass; two fail.** Source-ID selection
produces zero invalid outputs and higher reference-overlap F1, but answers to
unanswerable questions and citation-ID precision miss the required thresholds.
The candidate is not promoted and Phase 4 answer-quality acceptance stays open.

| Metric, same 50 development questions | Saved 7B span baseline | Previous complete-answer protocol | Source span-ID candidate |
|---|---:|---:|---:|
| Answerable token F1, 38 questions | .123578 | .143765 | .214084 |
| Answers | 24 | 19 | 30 |
| Refusals | 26 | 21 | 20 |
| Failures | 0 | 10 | 0 |
| Answer coverage | 48% | 38% | 60% |
| Answers to unanswerable questions / 12 | 3 | 5 | 4 |
| Citation-ID precision | .458333 | .347826 | .428571 |
| Citation-ID recall | .189655 | .137931 | .258621 |

The candidate answers 26 answerable and four benchmark-unanswerable questions.
The 18 threshold refusals are exactly unchanged. On the 32 invoked inputs, the
model returns 30 answers and two refusals. All 24 answers from the saved 7B span
baseline remain answers; six previous refusals become answers. Relative to the
failed complete-answer protocol, all ten invalid outputs become valid answers,
18 answers remain answers, two refusals become answers and one answer becomes a
refusal. These status transitions do not establish semantic correctness.

## Predeclared gate

| Condition | Result |
|---|---|
| F1 exceeds original control | Pass: .214084 > .012025 |
| Failures do not exceed original control | Pass: 0 <= 21 |
| Unanswerable answers do not exceed original control | **Fail: 4 > 3** |
| Citation-ID precision is at least original control | Pass: .428571 >= .363636 |
| Retain 80% of constrained 0.5B baseline F1 | Pass |
| Retain at least half of constrained-baseline answers | Pass: 30 >= 14 |
| No new failures versus constrained baseline | Pass: zero |
| F1 exceeds constrained baseline | Pass: .214084 > .075424 |
| F1 exceeds saved 7B baseline | Pass: .214084 > .123578 |
| Citation-ID precision is at least saved 7B baseline | **Fail: .428571 < .458333** |
| Retain 80% of saved 7B answers | Pass: 30 >= 20 |

The F1 difference from the saved 7B baseline is **+.090506**. A post-hoc paired
paper-family bootstrap (2,000 resamples, seed 42; 38 answerable queries across
26 families) gives a 95% percentile interval of **[.029309, .160313]**. This interval
excludes zero, but is descriptive on repeatedly inspected development data. It is
not selection-adjusted, an independent final result, or grounds to waive the two
failed conditions. The previous complete-answer run remains a secondary diagnostic
comparison, not a weaker replacement acceptance baseline.

## Structural success and remaining answer errors

All 41 selected quotations match their deterministic source spans exactly. The
largest quote is 40 words and the largest combined quote set is 104 words, below
the 120-word limit. Deduplicating passage citations yields 35 citations, 15 matching
the frozen gold IDs. Citation-ID overlap is distinct from semantic support. All
32 worker decisions have no runtime error; there were no validation failures,
timeouts, repairs or retries.

Focused assistant inspection of saved answers and their actual supplied evidence
still finds important limitations:

- **Wrong numerical attribution:** cyberbullying-performance question
  `5c6fa86757410aee6f5a0762328637de03a569e9` assigns Twitter F1 .95. Its selected
  `E3.S3` says .94 for both datasets, and the full supplied passage identifies them
  as Wikipedia and Twitter. The .95 result belongs to Formspring. Exact quotations
  did not prevent the generated answer from contradicting its evidence.
- **Clipping copied into an answer:** cyberbullying-topics question
  `7e38e0279a620d3df05ab9b5e2795044f18d4471` receives only "perso". The saved
  1,000-character passage ends partway through the list. The contract validates
  source presence but does not detect incomplete words or a nonresponsive fragment.
- **Source roles mixed up:** Japanese–Vietnamese dataset question
  `219af68afeaecabdfd279f439f10ba7c231736e4` names a parallel corpus "in the DongDu
  corpus". The supplied passage describes DongDu as monolingual back-translation
  data and describes the parallel corpus separately. The selected `E1.S4` does not
  support the added DongDu attribution.
- **Nonresponsive phrasing persists:** the medical-dataset answer is "an existing
  dataset"; the ASR-combination answer repeats "language model combination
  technique". Valid formatting does not supply the requested identity or method.

These are diagnostic assistant observations, not a full-paper or independent human
review and not a new aggregate semantic score. The known TF-IDF answerability-label
conflict remains counted in the four unanswerable answers. No labels were changed,
and no alternative score removes that case to obtain a passing result.

Changing evidence presentation, prompt and citation selection together reduced
structural failures in this run. It does not isolate the causal effect of each
change, prove that future outputs will be valid JSON, or resolve insufficient
evidence and answer selection. No model training is justified solely by this result.

## Execution and verification

- Run: `artifacts/span-id-answer-v1/runs/20260924T055954Z-4ed67439fb`.
- Prepared revision: `7392884e76b7f4db38853e3c949d4af01a92a101`.
- Approved snapshot: `70f950e327ed4a198e50de38e2476325cdc7154f708a966d4830f8e290c7932b`.
- One attempt: **32 calls, 962 actual output tokens, 12,288 reserved output tokens**.
- Worker elapsed **60.656 seconds**, including worker checks and model loading;
  excludes parent preflight and subsequent verification. Exit code 0.
- Generation-only p50/p95: **.853 / 1.681 seconds** across the 32 invoked rows.
  Historical timings for the 18 unchanged refusals are excluded. These are not
  end-to-end serving latency measurements or a controlled throughput benchmark.
- Qwen2.5-7B-Instruct revision `a09a35458c702b33eeacc393d103063234e8bc28`, offline
  CUDA device 0 on RTX 4090, BF16. PyTorch 2.10.0+cu128, Transformers 4.57.6,
  Accelerate 1.12.0. Free VRAM before load: 24,104,665,088 bytes; peak not measured.
- **$0 external spend**. No training, downloads, runtime changes, new retrieval,
  repair calls, retries, label changes, deployment or final-test access.

Launch verification and a separate read-only recomputation passed:

```powershell
.venv/Scripts/python.exe -X utf8 scripts/run_span_id_answer.py --verify
```

Verification checks frozen source/configuration/model/runtime/input hashes,
authorization, one-use execution, budget, supervision and output checksums, then
reconstructs all predictions and metrics from the saved raw responses. Reporting
also checks unchanged scoring inputs, all 18 original refusals, exact span quotes,
and source-PDF hashes for emitted citations. See [structured results](span-id-answer-development.json)
and [authorization](span-id-answer-authorization.json). The preparation's 194 passing
software tests are historical evidence; they were not rerun for this model execution.
The dtype deprecation and inactive sampling-parameter notices were nonfatal.

## Decision and next work

Preserve this as promising but gate-failing development evidence. Do not deploy it,
overwrite the earlier candidate or relax the thresholds. The
[30-answer review packet](span-id-answer-review-packet.md) includes every emitted
answer, selected span ID, exact quote, full supplied passage and local paper link.
The [human-response template](span-id-answer-human-review-template.json) is blank.
Independent human semantic acceptance has not occurred.

The next useful analysis is evidence sufficiency, clipping and claim attribution,
including the refusals; valid citations alone cannot answer those questions. It can
start from saved artifacts without more inference. Any changed prompt, context,
refusal policy, training or new evaluation run requires a separately prepared and
approved scope. This allowance is consumed. The 100-question final test stays unused.
