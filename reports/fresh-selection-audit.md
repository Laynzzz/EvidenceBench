# Evidence selection and abstention audit

This is a reproducible, post-hoc analysis of the **saved 50-question fresh-validation
comparison**, not another model evaluation. The original candidate still fails its
promotion gate. No new model calls, downloads, training, spending, or final-test
example access occurred.

## Reranking helps; selecting three passages still loses evidence

All ranking metrics below use the same 38 answerable questions. Recall is the
mean fraction of gold paragraph IDs recovered per question, not a pooled count.
Every annotated supporting paragraph has binary relevance for this audit.

| Stage / depth | Macro gold recall | Questions with any gold / 38 |
|---|---:|---:|
| Hybrid top 3 | 0.1645 | 8 |
| Reranked top 3, before threshold | 0.4934 | 23 |
| Reranked top 5, before threshold | 0.6645 | 29 |
| Reranked top 10, before threshold | 0.8224 | 34 |
| All 50 candidates, before or after reranking | 0.9737 | 37 |
| Actual packed context, after threshold | 0.3487 | 17 |

At depth three, reranking gains a gold hit on 17 questions and loses one on two;
six retain a hit and 13 remain misses. Binary nDCG@10 rises from **0.2056 to 0.5080**.
Removing the reranker is not supported by this evidence. Its relevance ordering
helps considerably even though its absolute score is a weak abstention signal.

Expanding the context from three to five passages would expose more gold IDs,
but no answers were generated with that context. It could exceed input limits or
add distracting evidence. ID recall also says nothing about whether supporting
text survives character clipping. These are opportunities for a later controlled
packing experiment, not measured answer improvements.

## The relevance-score cutoff does not reliably identify answerability

The frozen threshold is **3.2478480339050293**. Its observed decisions were:

| Upstream label | Pass context to generator | Withhold context |
|---|---:|---:|
| Answerable (38) | 26 | 12 |
| Unanswerable (12) | 6 | 6 |

Top-score answerability AUC is **0.5702**, computed over all 38 x 12 positive/negative
pairs with half credit for tied scores. Answerable scores have median **3.6086**
and range **[2.1012, 4.8386]**; unanswerable scores have median **3.3869** and range
**[2.1175, 4.9754]**. These overlapping scores are not calibrated probabilities.
The highest-scoring query is unanswerable and the candidate answered it. A stricter
monotone top-score cutoff cannot eliminate every unanswerable answer in this sample
while retaining any answerable answer.

## Exhaustive suppression replay: a narrow apparent pass

The audit enumerates every distinct state from raising the cutoff and suppressing
existing candidate answers, keeping equal-score queries together. Existing refusals
and failures stay as recorded. It never lowers the cutoff, changes context, or
invents answers for ungenerated cases. These are saved-output counterfactuals;
they contain no new latency measurements or generation results.

Of **29 states**, including the unchanged candidate and refusal of all its answers,
only **one** meets the original four numerical gate conditions on this same sample:

| Metric | Original candidate | Post-hoc passing state |
|---|---:|---:|
| Representative threshold | 3.247848 | just above 4.1825971603393555 |
| Answer count / 50 | 28 | 8 |
| Answerable token F1 | 0.075424 | 0.025764 |
| Unanswerable answers / 12 | 6 | 1 |
| Citation-ID precision | 0.321429 | 0.375000 |
| Failures | 0 | 0 |

The same state applies for cutoffs in **(4.1825971603393555, 4.209939956665039]**.
The script records `math.nextafter(score, +inf)` to represent removal of a tied
score group under the existing `score >= threshold` rule. This precision is for
reproducibility, not evidence for a meaningful universal operating point.

Removing the next answer drops F1 to **0.011028**, below the control's **0.012025**.
The apparent pass keeps only 16% coverage and was found after examining all 29
states. It is **not selected, independently validated, or deployed**, and does not
revise the failed original run. Optimizing to this single interval would risk
fitting a small development sample rather than solving answerability.

## Engineering outcome and next direction

Keep the trained reranker. Investigate evidence sufficiency separately from raw
relevance: an unanswerable question can still retrieve highly related paragraphs.
For a later experiment, change one factor at a time: first test a question-and-
evidence support decision on the existing candidate answers, then separately test
packing if warranted. A support filter could improve abstention while sacrificing
coverage; it must be evaluated on all questions, not only accepted answers.
This is a proposed direction, not implemented model behavior or a new compute
allowance. The validation set is now development evidence; it must not be described
as untouched when used to choose a revised system. The final test stays unused.

The new [audit script](../scripts/audit_fresh_selection.py) verifies the original
attempt before processing it and preserves source/input hashes in
[the structured report](fresh-selection-audit.json). It accepts only the known
validation run. Different retained output is rejected instead of overwritten.
Frozen model code, prompts, threshold, labels, original reports and release remain
unchanged.

```powershell
.venv/Scripts/python.exe -X utf8 scripts/audit_fresh_selection.py --check
.venv/Scripts/python.exe -m pytest -q tests/unit/test_fresh_selection_audit.py
```

Ten synthetic tests cover macro denominators, binary nDCG, AUC ties/undefined
classes, paired-trace and ranking corruption, exhaustive cutoff ties, immutable
report checks, and verification failures preventing report writes. Code review
identified missing assertions/guard coverage, which were added. The `--check`
command recomputes the real audit without inference or writes. Human semantic
support remains unmeasured by this audit; Phase 4 acceptance is still incomplete.

Final checks: **99 tests passed**, including real PostgreSQL (two existing dependency
deprecation warnings); Ruff, formatting, schema typing, original-cycle verifiers,
the fresh-run verifier and audit recomputation passed. The original comparison's
artifact hashes remain unchanged. No deployed behavior changed.
