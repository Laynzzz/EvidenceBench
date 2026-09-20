# Support-filter development experiment

Status: **implemented, reviewed and verified for preparation; not run on real models**.
Execution needs a new allowance. See [runner instructions](support-filter-runner.md).

## Question and fixed design

Can a second, explicit evidence-support decision reduce unsupported answers without
losing most of the constrained generator's useful answers? The last audit showed
that relevance scores weakly discriminate answerability (AUC .5702). This experiment
tests support directly; packing, retrieval, weights and original answers stay fixed.

Reuse all 50 saved fresh-validation records from
`artifacts/fresh-validation-v1/runs/20260919T233427Z-ddfba1b48e`.
Only the 28 answered records receive a new check. The checker sees the original
question, proposed answer and its cited passage text from the original packed
context. No reference answer, gold IDs, answerability label, or other uncited text
enters its prompt. A fixed instruction asks whether the proposed answer addresses
the question and is fully supported by the cited evidence. Greedy decoding is
constrained to `SUPPORTED` or `UNSUPPORTED`; it is not a calibrated probability.

Keep an answer only for `SUPPORTED`. Convert `UNSUPPORTED` to a refusal. Invalid
output, exceptions, context overflow and per-check timeout become explicit failures,
not successful refusals. Preserve the original 22 refusals and score all 50 records.
This is a correlated self-check by the same small model, not independent review;
it may confidently accept wrong answers or reject correct ones.

## New allowance requested, not granted by this document

- One local CPU attempt, four Torch threads, existing float32 Qwen2.5-0.5B weights
  and tokenizer at the exact release revision; offline loading only.
- At most 28 checker invocations and 28 underlying generation calls, no retries.
- At most eight new tokens per call, 224 maximum-output-token reservations total;
  record actual output-token counts separately. Input limit 1,536 tokens.
- Twenty seconds per checker invocation, plus an external **20-minute deadline**
  including startup, cache checks, model loading, inference and report writing.
  The per-check limit uses cooperative generation timeout plus elapsed-time failure
  classification; the supervisor enforces the hard whole-worker deadline.
- No embeddings, retrieval, reranking, training, model downloads, paid API or hosted
  execution. **$0 external spend**. Reuse saved contexts and outputs.
- One atomic attempt record; interruption, timeout or failure consumes it. Preserve
  all partial outputs. No replacement attempt without a separate allowance.

The earlier experiment budgets are exhausted. `continue` authorizes preparation,
but does not replenish those explicitly bounded attempts. Before execution, record
the user's new approval against the exact readiness snapshot. Default CLI execution
is read-only preflight; `--run-approved` requires that approval record.

## Fixed decision rule

Report the original control, original constrained candidate and filtered candidate
on the identical 50-question roster. Apply all four original numerical conditions:
F1 strictly exceeds control, failures and answers on unanswerable questions do not
increase versus control, and defined citation-ID precision is at least control's.

Also require **no new failures versus the unfiltered candidate**, **at least 80%
of its answerable F1**, and **at least half its answer count** (14 of 28).
These additional development checks
are fixed before new inference to reject the eight-answer collapse found by the
post-hoc cutoff audit; they do not rewrite the previous experiment's criteria.
Report every outcome even when any condition fails. No prompt/threshold variants,
second attempt, or per-query fallback selection are authorized.

Save decisions, raw outputs, errors, model-input hashes, timing, predictions, metrics,
usage and source/config/data/model hashes. Verification must recompute transformations
and metrics from saved decisions, check paired references/provenance, and require
successful supervisor termination. Report check latency separately from original
pipeline latency; replay is not an end-to-end serving benchmark.

These questions have already been inspected and used for development diagnosis.
Even a passing result is **development evidence**, not fresh holdout performance or
human semantic review. The 100-question final test remains unused and uninspected.
No passing result automatically authorizes final-test inference or deployment.

## Preparation checklist

- [x] Implement a separate script without modifying the frozen comparison source.
- [x] Test no-reference model inputs, exact keep/refuse/failure behavior, all-query
  scoring, coverage/F1 safeguards, usage limits, watchdog, approval binding and
  saved-run verification with synthetic models.
- [x] Verify real inputs and cached artifacts without loading models; retain readiness.
- [x] Review code and update learning/status evidence.
- [ ] Record new user approval against the readiness snapshot before execution.
