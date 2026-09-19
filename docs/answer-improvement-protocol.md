# Answer improvement cycle 2 — development-only selector experiment

Started 2026-09-19 after the user requested continuing answer-quality work.
The original test has been exposed and remains historical evidence. This cycle
does not create a new held-out score or change the deployed v1 release.

## Diagnosis and design

V3 development has 22 failures / 50 queries: 20 invalid generations and two timeouts.
Saved outputs include bracketed/unknown IDs, missing schema fields, non-quote text,
and Yes/No responses to open questions. Repeating the same JSON instruction does
not address the model's difficulty producing both content and the output contract.

Test one candidate using the cached, revision-pinned Qwen2.5-0.5B model. Deterministic
sentence options come only from the original packed passages. The model selects one
option or explicit refusal through a finite token constraint; code copies the
source text and citation. For Boolean questions, options associate Yes/No with a
supporting source sentence. Exact provenance does not establish semantic support.
Sentence extraction can miss lists spanning sentences and may reduce token F1.

## Fixed comparison before candidate inference

- Replay all 50 original development questions from
  `artifacts/answers/20260919T024110Z-6fd1dea23b/predictions.jsonl`.
- Verify the entire roster against `data/labels/qasper-v1/dev.jsonl`, including
  question text, family, answerability and references. Reject other splits/rosters.
- Keep original packed evidence and retrieval-threshold refusals. This isolates
  generation, not improved retrieval. Never provide labels/references to the model.
- Use the same cached model revision, four CPU threads, 1,536 input tokens and
  20-second per-call cooperative timeout. No downloads, paid services or training.
- One completed candidate run, maximum 600 seconds including setup; keep failed/partial
  runs. The documented catalog correction below permits two attempts total. No
  additional candidate tuning in this experiment after seeing its results.
- Rank sentence candidates by their original passage/sentence order, interleaved
  across passages, up to 18 sentences. Drop standalone titles, very short fragments
  and sentences over 450 characters; do not silently truncate long sentences.
  If the catalog exceeds the input limit, remove its last sentence options until
  it fits (both Yes/No alternatives together), recording the dropped count.
  Require terminal punctuation so clipped passage tails cannot become answer options.
- Report the existing answer F1, citation-ID agreement, failure/refusal rates and
  coverage with all denominators. Report candidate generation-only timings
  separately; historical end-to-end timings are not a controlled latency comparison.
- A promising candidate must increase answerable F1, reduce failures and not
  increase unanswerable answers versus the saved baseline. This is an exploration
  gate, not permission to promote a release. Report all outcomes even if it fails.

## Isolation and next gate

New modules/configs/artifacts implement this experiment; frozen source files,
models, labels, scoring and the running service remain unchanged. Synthetic tests
cover provenance, refusal, Boolean restrictions, invalid choices, token-prefix
constraints and time/context limits. A real model run establishes integration.

Any later release decision needs fresh questions from paper families excluded from
all v1 splits, predeclared selection/scoring rules, and a separately sealed test set.
Human-generated-claim review remains a distinct unmet criterion. Cycle 2 development
results must not be described as independent test improvement or full acceptance.

## Execution checklist

- [x] Trace saved development failures and state the hypothesis.
- [ ] Implement the selector and development-only replay with contract tests.
- [ ] Run the single full development comparison and retain provenance.
- [ ] Record results, limitations, reproduction and the next release gate.

Implementation: `src/evidencebench/generation_selection.py`,
`src/evidencebench/evaluation/selection_runner.py`,
`configs/answer-selection.yaml`, and independent tests. Transformers' documented
[generation token constraints](https://huggingface.co/docs/transformers/main_classes/text_generation)
provide the bounded option decoder; this does not require another framework.

## Catalog correction before completed comparison

Independent code review found that the initial splitter admitted incomplete tails
from passages clipped to 1,000 characters. This violated the sentence-only design.
Attempt `20260919T061745Z-0ab2aa2ca9` was interrupted after seven predictions, before
aggregate scoring. Its files remain intact with a separate termination record;
the hard interruption left its original manifest at running.

A synthetic regression reproduces the incomplete-tail bug. The correction requires
terminal punctuation, with optional closing quotes/brackets. One replacement attempt
is allowed to complete the originally intended comparison; this is a documented
protocol correction, not an unreported restart. Neither attempt is held-out evidence.
The runner rejects an unresolved running attempt or any attempt after a completed
comparison. The original training budget remains exhausted and unchanged.
