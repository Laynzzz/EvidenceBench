# Intact paragraphs: higher development F1, quality gate failed

The approved RTX 4090 attempt completed and a separate saved-result recomputation
passed. **Nine of twelve predeclared conditions pass; three fail.** Restoring full
paragraphs repairs one clipped answer but also produces two new inappropriate
answers and one invalid response. The candidate is not promoted; Phase 4 remains open.

| Metric, same 50 development questions | Saved 7B span | Previous span-ID | Intact paragraphs |
| --- | ---: | ---: | ---: |
| Answerable token F1, 38 questions | .123578 | .214084 | .240186 |
| Answers | 24 | 30 | 31 |
| Refusals | 26 | 20 | 18 |
| Failures | 0 | 0 | 1 |
| Answer coverage | 48% | 60% | 62% |
| Answers to benchmark-unanswerable questions / 12 | 3 | 4 | 6 |
| Citation-ID precision | .458333 | .428571 | .400000 |
| Citation-ID recall | .189655 | .258621 | .241379 |

The candidate answers 25 answerable and six benchmark-unanswerable questions. One
answerable output fails validation; all 18 threshold refusals remain byte-for-byte
unchanged. Both previous model refusals become answers. Thirty-two calls produced
31 valid answers, no model refusals and one output-contract failure, without runtime
errors or timeouts. No response was repaired, retried or selectively rescored.

## Predeclared gate

| Condition | Outcome |
| --- | --- |
| F1 exceeds original control | Pass: .240186 > .012025 |
| Failures do not exceed original control | Pass: 1 <= 21 |
| Unanswerable answers do not exceed original control | **Fail: 6 > 3** |
| Citation-ID precision is at least original control | Pass: .400000 >= .363636 |
| Retain 80% of constrained-baseline F1 | Pass |
| Retain half of constrained-baseline answers | Pass: 31 >= 14 |
| No new failures versus constrained baseline | **Fail: 1 > 0** |
| F1 exceeds constrained baseline | Pass: .240186 > .075424 |
| F1 exceeds saved 7B baseline | Pass: .240186 > .123578 |
| Citation-ID precision is at least saved 7B | **Fail: .400000 < .458333** |
| Retain 80% of saved 7B answers | Pass: 31 >= 20 |
| F1 strictly exceeds saved span-ID result | Pass: .240186 > .214084 |

The paired F1 gain over the previous span-ID run is **+.026102**. A post-hoc paired
paper-family bootstrap (2,000 resamples, seed 42; 38 answerable questions across 26
families) gives a 95% percentile interval of **[-.016220, .094526]**, including zero.
This is descriptive uncertainty on repeatedly inspected development data, not a
selection-adjusted interval, independent confirmation, or a reason to waive failures.
The cyberbullying-topic correction alone contributes +1/38 = .026316 to overall
F1; other answerable changes have a slightly negative net contribution.

## The controlled input change

The same 96 paragraph occurrences, passage IDs/order, question order, model,
system prompt, output contract and threshold were retained. Twenty-five passage
occurrences regained their original tails. No new passage was retrieved, no
reference selected the restored text, and no final-test row was accessed.

| Generated-input subgroup | Inputs | Answerable questions | Previous F1 | Current F1 |
| --- | ---: | ---: | ---: | ---: |
| At least one restored tail | 18 | 15 | .192934 | .259058 |
| Already intact | 14 | 11 | .476472 | .476472 |

All 14 unchanged inputs produce exactly the same raw output as before. Of the 18
changed inputs, ten retain the same answer and nine the same raw output. These
subgroups were determined by the text intervention, not by outcomes, but the
comparison remains exploratory. Matching outputs in this run do not establish
general CUDA determinism. The 18 untouched threshold refusals are outside this
generated-input table and remain inside the all-50 scoring denominator.

## Improvements and regressions in the saved evidence

Focused assistant inspection distinguishes source presence from claim support;
this is not a new full-paper review or an independent human semantic score.

- **Clipped topic repaired (`7e38e0`):** `perso` becomes "personal attack, racism,
  and sexism." The restored `E1.S9` explicitly names the study's three topics.
- **Numerical attribution corrected (`5c6fa8`):** the answer now assigns .94 to both
  Wikipedia and Twitter and .95 to Formspring. The former Twitter value was .95.
  The necessary facts were already present in the old input; the changed context
  affected selection, so this is not evidence that those numbers had been clipped.
  Selected quotes still use "both these datasets" and "the same dataset": resolving
  their referents requires surrounding passage text, not exact-quote matching alone.
- **Novelty features identified (`984fc3`):** the answer now names KL divergence and
  entity overlap instead of restating novelty. Those facts were also available in
  the earlier E2 passage. Text restoration does not isolate why selection changed.
- **Attention metric misattributed (`444975`):** a former refusal becomes "7.05 BLEU
  points." Its quote measures translation performance, not the requested amount
  of attention-mechanism improvement. The restored paragraph discusses those claims
  separately. More available numbers do not imply an answer to the requested metric.
- **Definition source mistaken for a dataset (`f90339`):** another former refusal
  becomes "European Union Court of Human Rights." Its own passage describes a
  statement used to define hate speech, not the dataset analyzed. The question's
  scope remains ambiguous, but this emitted entity has the wrong role in the source.

Of the four previously identified material-clipping cases, only the cyberbullying
topic answer becomes a valid, substantively improved output. The humor-baseline
answer still gives only RBF SVM, and the human-judgment answer still names annotators
without explaining most of the procedure. The Vietnamese-segmentation answer
attempts a broader response but violates the unchanged contract:

```json
{"span_ids":["E2.S2","E2.S3","E2.S4","E2.S8"]}
```

Four span IDs exceed the maximum of three. Its complete original raw response and
strict validation error are preserved in [the failure report](intact-passage-errors.md).
It remains a failure with zero answer F1. Do not remove a citation, raise the limit
or count its raw prose as a successful answer after seeing the result.

All **41 accepted quotations** match their deterministic source spans; the maximum
is 40 words per quote and 104 words combined per answer. They produce 35 unique
passage citations, 14 matching frozen gold IDs. These checks establish provenance,
not entailment. The known TF-IDF answerability-label conflict and prior NCEL
full-paper overclaim caveat remain; frozen labels and scores are unchanged.

## Execution, verification and reproducibility

- Run: `artifacts/intact-passage-v1/runs/20260924T210922Z-e266a7a622`.
- Prepared revision: `5f7701c397bcbd88a2d4d125c4d0233296e3ad11`.
- Approved snapshot: `784b44c5e71307300b0b77d0a835d38c820d8bef7e9f8c6e5c04d4e94f927228`.
- **32 calls, 1,020 actual output tokens, 12,288 reserved output tokens**.
- Worker elapsed **63.547 seconds**, including model loading and worker checks;
  parent preflight and later verification are excluded. Exit code 0.
- Generation-only p50/p95 **.917 / 2.050 seconds** across 32 invoked inputs;
  the historical refusal timings are excluded. This is not serving latency.
- Qwen2.5-7B-Instruct revision `a09a35458c702b33eeacc393d103063234e8bc28`,
  RTX 4090 CUDA device 0, BF16; PyTorch 2.10.0+cu128, Transformers 4.57.6,
  Accelerate 1.12.0. Free VRAM before loading: 24,104,665,088 bytes; peak not measured.
- **$0 external spend**. No training, downloads, retry, label revision, deployment
  or final-test access. The single allowance is consumed.

Launch verification and a separate read-only reconstruction passed:

```powershell
.venv/Scripts/python.exe -X utf8 scripts/run_intact_passage.py --verify
```

Reporting additionally verified original paragraph prefixes/full bodies, unchanged
scoring labels and retrieval traces, all 18 original refusals, exact span quotations,
input-subgroup membership and cited local PDF hashes. See
[structured evidence](intact-passage-development.json),
[authorization](intact-passage-authorization.json) and the
[runner guide](../docs/intact-passage-runner.md). The preparation's 242 passing
software tests are historical and were not rerun for this unchanged model execution.
The dtype deprecation and inactive sampling-parameter notices were nonfatal.

## Decision

Retain this as a failed controlled development comparison. Restoring missing text
can repair a specific answer, but it also exposes the model to plausible irrelevant
facts, and the fixed three-span limit can conflict with a multi-part answer. More
context alone does not resolve claim attribution, completeness or appropriate refusal.

The [31-answer review packet](intact-passage-review-packet.md) preserves each answer,
selected quote, full supplied passage and paper link. Its
[human response template](intact-passage-human-review-template.json) remains blank.
Phase 4 and independent human acceptance remain incomplete. The next design work
should address the requested fact's role and citation coverage together, using
these saved failures before proposing further compute. No additional model attempt
or training is authorized; the 100-question final test remains unused.
