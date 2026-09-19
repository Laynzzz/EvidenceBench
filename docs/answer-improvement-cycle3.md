# Cycle 3 — three authorized local development experiments

The user authorized up to three additional local development experiments on
2026-09-19. No training, paid services or new model downloads. V1 final-test results
are historical and exposed; this cycle makes development claims only.

## Fixed design before inference

Use all 50 checksum-pinned v3 development rows, the same three packed evidence
passages, existing retrieval refusals, cached Qwen2.5-0.5B revision, four CPU threads,
1,536 input tokens and 20 seconds per generation call. One call per eligible query;
maximum 900 seconds including setup per experiment. Each variant can run once;
failed/interrupted attempts consume their slot. Maximum three attempts total.
Launch via `python -m evidencebench.evaluation.span_watchdog --variant <name>`;
the external watchdog kills and records attempts exceeding 900 wall-clock seconds,
including setup. The lower-level runner's cooperative checks are supplementary.

1. **plain:** Ask for a short source quote, without JSON. Code assigns the first
   cited passage containing that exact normalized quote. Boolean questions use
   `Yes | E1` / `No | E1` with a valid supplied alias. `UNKNOWN` means refusal.
2. **constrained:** Same prompt, but a finite token trie restricts output to legal
   contiguous source spans, valid Boolean/alias pairs or `UNKNOWN`.
3. **focused:** Same constrained decoder, with only the leading paper-title wrapper
   removed from the question. Evidence remains unchanged. This tests whether a long
   repeated title distracts the small model from the actual question.

Span catalogs exclude the first title line, unresolved reference/formula markers
and an incomplete final word when a passage is clipped at the recorded 1,000-character
packing limit. They contain contiguous spans up to 15 whitespace-delimited words,
trimming surrounding punctuation without changing letters/digits. The decoder uses
up to 64 output tokens; longer catalog tokenizations are excluded. Plain outputs
must satisfy the same source-span contract. Whole sentences are not required.
Finite token constraints guarantee catalog membership, not semantic correctness.

Boolean citations are model-selected references, not verified logical support.
For quotes that occur in multiple passages, choosing the first matching passage is
deterministic but may differ from upstream human evidence IDs. Report this limitation.
No reference answers, relevance judgments or per-query labels enter model inputs.

## Evaluation and selection

Record complete predictions, raw outputs, provenance, source/config snapshots,
failure/refusal reasons and timing scopes for every attempt. Compare each completed
variant against the same frozen v3 development baseline with unchanged metrics.
Primary metric: answerable token F1 (38 questions). Exploratory gate: improve F1,
reduce failures, and do not increase answers on the 12 unanswerable questions.
Report citation precision/recall, coverage and per-query regressions alongside the
gate. If multiple variants pass, prefer higher F1, then citation precision, then
fewer failures; do not construct a per-query hybrid. Stop after three attempts or
earlier if further variants cannot be run within these constraints.

This is adaptive development, not a fresh benchmark or release acceptance. Even a
passing candidate stays experimental until a new evaluation protocol and fresh
paper families support release selection. No v1 prompts, source, models, labels,
scoring, thresholds or deployed service change. The prior cycle-2 failure is retained.

## Implementation and verification

New modules: `generation_spans.py`, `evaluation/span_runner.py`; configuration:
`configs/answer-spans.yaml`. Use synthetic tests for exact-span provenance,
multi-token trie paths, Boolean restrictions, clipped-word exclusion, refusal,
unknown citations and the three-attempt guard. Reuse existing read-only development
roster validation. Run independent code review before inference and preserve all
failures. Reports and verification commands record results after the experiments.
