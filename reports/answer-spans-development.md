# Cycle 3 — short source spans improve development F1, with citation trade-offs

Two of the three authorized experiments passed the predeclared exploratory gate.
**Constrained spans** are preferred by the declared F1-first rule. The **focused**
variant has better observed refusal behavior, but lower F1. Neither candidate is
deployed or independently validated on a new held-out set.

| Metric | Original v3 | Plain short answer | Constrained spans | Focused question |
|---|---:|---:|---:|---:|
| Answerable token F1 (38 questions) | 0.1184 | 0.0263 | **0.1533** | 0.1372 |
| Answered / 50 | 9 | 2 | 28 | 28 |
| Explicit failures / 50 | 22 | 28 | **0** | **0** |
| Coverage | 18% | 4% | 56% | 56% |
| False refusals / 38 answerable | 9 | 10 | 12 | 10 |
| Answers on 12 unanswerable questions | 2 | 0 | 2 | **0** |
| Unanswerable refusal recall | 10 / 12 | 10 / 12 | 10 / 12 | **12 / 12** |
| Upstream citation-ID precision | 0.600 | 0.500 | 0.357 | 0.321 |
| Upstream citation-ID recall | 0.120 | 0.020 | 0.200 | 0.180 |
| Exploration gate | Baseline | Fail | Pass | Pass |

Plain generation has zero answers on unanswerable questions partly because two
failed, not because all were refused. Failure, refusal and answer counts remain
separate. The focused variant actually refused all 12; that small observed sample
does not establish reliable refusal in general.

## What changed and what we learned

All variants use the same cached Qwen2.5-0.5B weights, development questions and
packed source context. Nineteen original retrieval-threshold refusals are replayed
in each run; each model processes the remaining 31 questions. Reference answers
and relevance labels never enter model inputs.

1. **Plain** removes the JSON task and asks for a short exact quote. Code supplies
   a citation by matching the quote to source text. This failed: 25 outputs did not
   match eligible source spans and three Boolean outputs lacked the required
   citation format. Examples echoed paper titles. A shorter prompt alone was not
   sufficient for this small model.
2. **Constrained** uses the same prompt with a finite token trie that permits only
   contiguous source spans, valid Boolean/citation pairs, or refusal. It preserves
   short answers such as `GloVe word vectors`, `ELMo and BERT embeddings`, and
   `NowThisNews`. Among answerable queries, F1 improved on 13, regressed on two,
   and tied on 23 relative to v3. The resulting +0.0349 mean F1 is development
   evidence, not an independent or statistically established generalization gain.
3. **Focused** removes only the leading paper-title wrapper from the question.
   It keeps the same constraints and source context. F1 improved on 12 answerable
   questions, regressed on two and tied on 24. It refused the two unanswerable
   questions for which v3 had returned misleading numbers (`4090` and `4`).

## Remaining errors and interpretation limits

Constrained decoding ensures a valid output contract and source membership; it
does not establish that a span answers the question. Some selected spans remain
generic or end mid-thought at the 15-word bound. The embedding answer can omit an
additional embedding named in the reference. Boolean answers still need logical
support beyond a valid citation ID: one reference-matching `No` became `Yes`.

For the average-sentence-length question, constrained generation includes the
correct `15.5` within a longer statistics span. Token F1 falls relative to the
baseline's concise `15.5`, illustrating that this metric penalizes unnecessary
words even when they contain relevant information. Elsewhere small nonzero F1
comes from topical overlap rather than a complete answer. No new human semantic
review or accuracy claim is made.

Citation-ID precision falls substantially for both passing candidates. More answers
yield more cited evidence overall, but more of those citations miss upstream gold
evidence IDs. For repeated quotes, code picks the first matching passage; this can
differ from annotated evidence. Boolean source selection can also be wrong. These
mechanisms warrant inspection, not an assumption that every mismatch is harmless.

The F1-first rule was declared before inference, so constrained remains the preferred
development candidate despite focused's better refusal result. Both are retained
as alternatives; no per-question hybrid or post-hoc change of the winning rule was
used. A release objective may need a different balance of citation support and
abstention, chosen before fresh evaluation.

## Resources, verification and reproduction

- Exactly three authorized attempts completed: 150 query evaluations, including
  93 actual model calls and 57 replayed retrieval refusals. No fourth attempt.
- Model-run elapsed times were 136.89, 134.37 and 126.95 seconds, including model
  initialization inside the run. Parent-watchdog overhead is additional. Each
  external watchdog covers setup and inference with a 900-second wall-clock cap.
- Four CPU threads, existing model cache, no training, no new model downloads,
  no paid services and no deployment. No watchdog timeout occurred.
- Per-query timings exclude retrieval and model loading; fast replayed refusals
  are included. They are not comparable with historical end-to-end latency.
- All 66 tests passed, including local PostgreSQL. Ruff, format and schema typing
  passed. Independent review checked provenance and prompted adding the external
  watchdog. Original v1 and cycle-2 reports still verify.

The [protocol](../docs/answer-improvement-cycle3.md) and inference code were committed
at `b5a93c8` before the first run. Each run stores source/config snapshots, environment,
predictions and metrics. [Structured results](answer-spans-development.json) identify
all three run directories under `artifacts/answer-improvement-cycle3/`.

Read-only reproduction:

```powershell
uv run python scripts/verify_span_experiments.py
```

This recalculates every completed comparison, verifies prediction/config/source
hashes and source citations, checks development membership, confirms the preferred
candidate, and verifies the original release lock. The execution command is
`uv run --extra ml python -m evidencebench.evaluation.span_watchdog --variant NAME`.
All three local slots are spent; it rejects another attempt. Retain the run folders
and attempt records instead of deleting them to bypass the budget.

The next release decision requires fresh paper families, a predeclared evaluation
and selection protocol, and independent claim-support assessment. V1's exposed
test is not reused as a new holdout. Phase 4's full quality gate remains open.
