# Bounded claim-grounded improvement proposal

## Current evidence

The verified intact-paragraph candidate reaches .240186 answerable token F1, above
the saved span-ID result of .214084. It nevertheless fails three of twelve conditions:
six answers on the 12 benchmark-unanswerable questions, one invalid four-span output,
and .400000 citation-ID precision. The complete cohort remains 50 questions, with
32 supplied-evidence calls and 18 existing threshold refusals. These results belong
to an offline candidate; the deployed CPU pipeline is unchanged.

An assistant-only review of the 32 saved generator inputs and outputs is prepared
separately in [the structured review](../reports/claim-grounded-input-review.json).
It is non-blinded diagnostic evidence, not independent human acceptance. The raw
four-span failure and known label/evidence conflicts remain intact.

## Fixed sequence

### A — claim-attached citations and stricter attribution

Use the response contract in [cycle 4 protocol](answer-improvement-cycle4.md): one
to four claims, up to 80 answer words, at most four distinct source spans, and an
empty claims list for refusal. Attach span IDs to each claim, deterministically join
the existing flat answer, and deduplicate parent citations for unchanged scoring.
Keep the exact 32 intact-paragraph generation inputs and 18 threshold refusals.

Pinned compute: Qwen2.5-7B-Instruct revision
`a09a35458c702b33eeacc393d103063234e8bc28`, RTX 4090 CUDA device 0, BF16,
PyTorch 2.10.0+cu128, Transformers 4.57.6, Accelerate 1.12.0, greedy decoding,
2,048 input tokens, 384 maximum output tokens and a 30-second per-query limit.
The exact runtime must match the frozen artifact inventory. Prompt inspection uses
the local tokenizer only and loads no model weights.

Maximum allowance: **one attempt, 32 calls, 12,288 reserved output tokens, 20 minutes,
$0 external spend**. No truncation, retry or repair. A is a joint comparison of
format, attribution/refusal instructions and citation coverage.

### B — remove the relevance-score cutoff, only if A qualifies

Run B only if A has zero output failures, at most three unanswerable answers,
citation-ID precision at least .458333 and at least 20 answers. Otherwise skip B and
finish the portfolio handoff with A's result.

If eligible, retain A's prompt/model/decoder and all ranking settings, and change
only the numerical relevance cutoff. Use the saved top-three complete paragraphs for
all 50 questions and make a fresh all-50 run. Report the previously blocked 18
separately (12 answerable, six unanswerable).

Maximum allowance: **one attempt, 50 calls, 19,200 reserved output tokens, 30 minutes,
$0 external spend**. B requires its own explicit approval. Approval for A cannot
authorize B.

## Fixed evaluation and selection

Reconstruct each candidate from saved raw responses and score the unchanged 50-query
development cohort. Preserve the existing twelve conditions in
`reports/intact-passage-development.json`; one condition requires F1 strictly above
.214084. Among candidates passing all conditions, order by answerable token F1,
citation-ID precision, then fewer calls. Do not adjust labels or thresholds after
observing a candidate.

Report F1, answer coverage, output failures, answers to benchmark-unanswerable
questions, citation-ID precision/recall, generation latency, actual/reserved tokens,
calls and paired paper-family bootstrap uncertainty. The bootstrap remains descriptive
on repeatedly reused development data. Assistant review is not independent human
acceptance, and no passing development result would establish fresh test performance.

## Required checks and hard boundaries

Before asking for each run's approval, verify the exact model/runtime assets and
tokenize every exact prompt without loading model weights. Run all unit/software tests,
formatting, lint, type checks and PostgreSQL integration checks. Synthetic lifecycle
coverage must verify a one-use exact-snapshot approval, tamper rejection, deadlines,
and call/token budgets. Freeze a separate readiness snapshot, source hashes and
artifact root for each attempt.

After approval and execution, independently recompute predictions/metrics; keep
failed raw outputs and assistant-review disagreements. Do not run training, upgrade
models, use paid services, access the reserved final set, modify the API, or deploy a
candidate. Stop after A and conditional B. Publish a candid report, update the
architecture/reproduction/teaching/interview guides, refresh the recorded-data demo,
and check GitHub CI. The original deployed pipeline remains the release.

## Current approval state

No model run is authorized by this proposal. Each exact readiness snapshot needs a
separate explicit user approval. The current work is preparation only: contract,
runner, synthetic verification, source review, frozen documentation and exact prompt
length verification (all 32 prompts are 525–1,286 tokens). The full software suite,
lint, formatting and targeted type check pass. PostgreSQL integration remains
pending because the local Docker Linux engine is unavailable; no local PostgreSQL
service, reachable default port or configured test database URL was found.
