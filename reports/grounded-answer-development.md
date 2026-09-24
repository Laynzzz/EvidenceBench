# Complete-answer comparison: development gate failed

The approved Qwen2.5-7B experiment completed on RTX 4090 and its saved results
verify. **Six of eleven predeclared conditions pass; five fail.** The higher token
F1 does not justify promotion: failures increased, citation-ID precision declined
and more unanswerable questions received answers. This candidate remains a failed
development experiment. Phase 4 answer-quality acceptance is incomplete.

| Metric, same 50 development questions | Saved 7B span baseline | Complete-answer candidate |
|---|---:|---:|
| Answerable token F1, 38 questions | 0.123578 | 0.143765 |
| Answers | 24 | 19 |
| Refusals | 26 | 21 |
| Failures | 0 | 10 |
| Answer coverage | 48% | 38% |
| Answers to unanswerable questions / 12 | 3 | 5 |
| Citation-ID precision | 0.458333 | 0.347826 |
| Citation-ID recall | 0.189655 | 0.137931 |

The candidate answers 14 answerable and five unanswerable questions. Eighteen
original threshold refusals remain exactly unchanged; the 32 generated
outputs comprise 19 answers, three refusals and ten validation failures. Nine
previous answers and one previous refusal become failures; four previous refusals
become answers. Errors are counted as failures, never successful refusals.

## Predeclared gate

| Condition | Result |
|---|---|
| F1 exceeds original control | Pass: .143765 > .012025 |
| Failures do not exceed original control | Pass: 10 <= 21 |
| Unanswerable answers do not exceed original control | **Fail: 5 > 3** |
| Citation-ID precision is at least original control | **Fail: .347826 < .363636** |
| Retain 80% of constrained 0.5B baseline F1 | Pass |
| Retain at least half of constrained-baseline answers | Pass: 19 >= 14 |
| No new failures versus constrained baseline | **Fail: 10 > 0** |
| F1 exceeds constrained baseline | Pass: .143765 > .075424 |
| F1 exceeds saved 7B baseline | Pass: .143765 > .123578 |
| Citation-ID precision is at least saved 7B baseline | **Fail: .347826 < .458333** |
| Retain 80% of saved 7B answers | **Fail: 19 < 20** |

The F1 difference from the saved 7B baseline is +.020187. A post-hoc paired
paper-family bootstrap (2,000 resamples, seed 42, 38 answerable queries across
26 families) gives a 95% percentile interval of **[-.048272, .086372]**. It includes
zero. This descriptive interval does not adjust for repeated development selection,
establish a reliable gain or change the predeclared gate.

## What failed

The saved raw outputs reproduce all ten failures without model inference.
[Original outputs and errors](grounded-answer-errors.md) preserve the evidence.

| Failure pattern | Cases | Evidence |
|---|---:|---|
| Exact quotes exceed the 80-word per-quote limit | 4 | Humor experiments: 107 and 100 words; evaluation measures: 103; Vietnamese challenges: 114; cyberbullying results: 86 |
| Quote is not an exact body substring | 2 | Sarcasm models: reordered sentences; Wikipedia baseline: changed spacing before the period |
| Both overlong and inexact quote | 1 | Speech dataset: 82 words and altered spacing around an INLINEFORM placeholder |
| Invalid JSON | 3 | Cyberbullying topics: stray parenthesis; ASR combination and human judgments: trailing code fences |

The humor case also exceeds the 120-word combined quotation limit (207 words).
The validator reports the first violated constraint; the table above diagnoses
all quote checks directly from saved strings. No output was repaired, no limit was
relaxed and no alternate score was substituted. All 32 worker decisions have no
runtime error; these failures arose at the response-validation boundary, not from
CUDA failures or timeouts.

Passing this structural check still does not prove usefulness. For example, the
medical dataset answer is just "an existing dataset", and the novelty-features
answer restates novelty relative to an existing profile. These are visible
responsiveness problems, not a new full-paper semantic evaluation. Exact quotation
presence proves provenance only; it does not establish entailment or completeness.
The previously documented TF-IDF label conflict remains unchanged in scoring.

The protocol jointly changes prompt, output format, allowed answer length and
decoding budget. It cannot isolate the effect of longer answers. The saved evidence
and model weights stayed fixed. More capable formatting alone would not resolve
the remaining wrong-answer-type and incomplete-answer problems.

## Execution and reproducibility

- Run: `artifacts/grounded-answer-v1/runs/20260924T041708Z-d0f23e62ae`.
- Prepared code: `205302726ced7dbfb12dcbe9b5bede725feca4f8`.
- Approved snapshot: `bca98bde2292bbe57782d7a7f5e8bd532cfea5b3aa9c599f5a78051ac4e330c0`.
- One attempt, 32 calls, **3,443 actual output tokens**, 12,288 reserved tokens.
- Worker elapsed **176.969 seconds**, including worker checks and model loading;
  excludes parent preflight and saved-result verification. Exit code 0.
- Generation-only p50/p95 over 32 calls: **3.756 / 7.805 seconds**. These exclude
  the 18 historical refusal timings and are not end-to-end serving measurements.
- Qwen2.5-7B-Instruct revision `a09a35458c702b33eeacc393d103063234e8bc28`, offline
  CUDA device 0, RTX 4090, BF16. PyTorch 2.10.0+cu128, Transformers 4.57.6,
  Accelerate 1.12.0 in the isolated GPU environment.
- Free VRAM before loading: 24,104,665,088 bytes. Peak VRAM was not measured.
- **$0 external spend**; no training, retries, repair calls, new retrieval,
  runtime changes, label changes, deployment or final-test access.

Launch verification and a separate read-only recomputation both passed:

```powershell
.venv/Scripts/python.exe -X utf8 scripts/run_grounded_answer.py --verify
```

The verifier checks frozen source/configuration/model/runtime/input hashes,
authorization, the single attempt, budgets, supervision and output checksums. It
reconstructs all predictions and metrics from the original raw model responses.
The [structured report](grounded-answer-development.json) records outputs, timings,
paired F1 values, bootstrap settings, hardware and artifact hashes. Approval is
recorded in [the authorization](grounded-answer-authorization.json). The preparation's
170 passing software tests are historical evidence; the suite was not rerun here.
The dtype deprecation and inactive sampling-parameter notices were nonfatal.

## Decision and remaining work

Do not promote this candidate or overwrite the saved span baseline. The
[19-answer review packet](grounded-answer-review-packet.md) includes every emitted
answer with exact citations and local paper links. Its
[human-response template](grounded-answer-human-review-template.json) is blank;
no independent human semantic review is claimed.

Before another experiment, address the cost of asking the model to reproduce
long exact quotes and distinguish answer completeness from mere reference overlap.
A possible next design is selecting predefined short evidence spans by ID while
generating a separate answer; it must preserve citation auditability and receive
its own design review, verification and explicit run approval. It is not implemented
or authorized by this result. The current allowance is consumed. The 100-question
final test remains unused and Phase 4 acceptance remains open.
