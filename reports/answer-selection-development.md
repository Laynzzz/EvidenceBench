# Cycle 2: reliable output formatting did not improve answer quality

The constrained sentence selector eliminated generation failures on this development
replay, but answer token F1 fell. It **fails the predeclared exploration gate and is
not promoted**. The original v1 service and final test results remain unchanged.

| Metric | Frozen v3 development baseline | Sentence selector |
|---|---:|---:|
| Answerable token F1 (38 answerable questions) | 0.1184 | 0.1012 |
| Answered (50 total questions) | 9 | 30 |
| Explicit failures | 22 | 0 |
| Refused | 19 | 20 |
| False refusals (38 answerable) | 9 / 38 | 10 / 38 |
| Unanswerable questions receiving answers | 2 / 12 | 2 / 12 |
| Citation-ID precision against upstream labels | 0.600 | 0.400 |
| Citation-ID recall against upstream labels | 0.120 | 0.240 |

All 50 development queries were replayed with their original retrieved context.
Nineteen retrieval-threshold refusals were retained without model calls; the same
cached Qwen2.5-0.5B model handled the other 31. One selected option was refused and
30 returned answers. No catalog exceeded the input limit. The completed run took
92.09 seconds including model setup. Its all-query p50/p95 were 2.14/4.00 seconds,
including fast replayed refusals and excluding retrieval. These are **not comparable
end-to-end latency measurements** against the historical baseline.

## Why the gate failed

Among 38 answerable questions, reference F1 improved for 12, regressed for four,
and tied for 22. Gains on formerly failed outputs did not offset losing several
high-scoring answers. These are reference-based diagnostics, not human adjudication.

- Asked for average sentence length, the baseline returned `15.5`; the selector
  instead returned a sentence about 4,528 employees. Both numbers come from source
  text, but the latter sentence answers a different question.
- Asked whether a model starts from a checkpoint, the selector changed the
  reference-matching `No` into `Yes`. Constraining option syntax does not verify
  the inference made from the attached sentence.
- Asked which dataset was used, the baseline returned `Reuters-8`; the selector
  chose a generic sentence announcing the experiments.
- A formerly failed embedding question now receives the source sentence naming
  pretrained GloVe vectors and its training corpora. This is a useful recovery,
  but the longer source sentence changes the precision/recall trade-off of token F1.

The model still struggles to select the sentence that answers the specific question.
Some newly nonzero token overlaps are merely topical: the Wizard-of-Oz answer names
the study type without explaining the setup. Coverage is therefore not correctness.
Requiring valid source text fixes provenance/formatting; it does not fix relevance
or Boolean reasoning. No new human semantic-quality estimate is claimed.

## Experiment integrity

The [protocol](../docs/answer-improvement-protocol.md) was written before candidate
inference. An independent reviewer caught incomplete passage tails admitted into the
initial catalog. The first attempt was interrupted after seven outputs, before
aggregate scoring, and retained with a termination sidecar. A synthetic regression
verified the bug; the replacement required sentence-ending punctuation. The protocol
explicitly records this correction and permits two attempts, at most one complete.
No additional candidate tuning followed the completed result.

The corrected candidate ran from commit `983b6ff`, with config, source archive,
model revision, environment and predictions recorded in its immutable run folder.
It used four CPU threads, the existing local model cache, no training and no paid
services. Independent code review found no further substantive issue. All 58 tests
passed including local PostgreSQL; lint, format, schema typing and original frozen
report verification passed. This is local execution, not remote CI or deployment.

## Reproduce and inspect

- [Machine-readable results](answer-selection-development.json)
- Completed run: `artifacts/answer-selection-cycle2/20260919T062027Z-47d413129a`
- Interrupted attempt: `artifacts/answer-selection-cycle2/20260919T061745Z-0ab2aa2ca9`
- Original baseline: `artifacts/answers/20260919T024110Z-6fd1dea23b`
- Read-only verification: `uv run python scripts/verify_answer_selection.py`

The execution command is:

```powershell
uv run --extra ml python -m evidencebench.evaluation.selection_runner
```

Its local run guard now rejects another attempt, preserving the completed experiment. Use the read-only
verification command to recalculate results. Source and checkpoint caches plus
the saved v1 development artifacts are required for reproduction elsewhere.

The next design question is how to preserve accurate short-span/Boolean answers
while reducing format failures. A new experiment must declare its candidate and
budget first; a later release requires fresh paper families and sealed evaluation.
Do not select a hybrid from these per-query outcomes or retune against the v1 test.
