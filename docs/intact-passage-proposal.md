# Controlled intact-paragraph comparison

Status: preparation only; a new explicit execution allowance is required.

## Question and intervention

The [saved-output audit](../reports/span-id-evidence-audit.md) found useful answer
details beyond the 1,000-character cut in four cases. It also found nine non-adequate
answers despite sufficient supplied evidence. Test whether restoring the original
selected paragraph bodies improves answers; do not assume it fixes claim selection.

For every one of the same 32 nonempty development inputs, resolve its unchanged
paragraph IDs against `qasper-fresh-v1` development units and use the entire original
text, including its original title. Require the old text to equal the original
first 1,000 characters before replacement. Do not use reference answers, gold IDs,
review judgments or query-specific tail choices to select text. The other 18
threshold-refusal rows remain identical, and all 50 rows remain in scoring.

Keep Qwen2.5-7B, its checkpoint, BF16 RTX 4090 execution, greedy decoding, question
order, passage identities/order, threshold, system prompt, span construction,
80-word answer limit and 1–3 span-ID output contract unchanged. Full paragraphs
alter text, source-span catalogs and input lengths together. This tests that
packing intervention, not a separately isolated benefit of any one new span.

The new input validator rejects paragraphs longer than 4,096 characters and missing
bodies rather than clipping or dropping them. Verify all complete rendered prompts
fit the unchanged **2,048-input-token** limit before authorization. Generation keeps
384 output tokens and 30 seconds per query. If any prompt cannot fit, this design
must be revised before approval; do not silently truncate. No retrieval rerun,
training, new documents, placeholder repair or label changes are included.

Alternatives: sentence-boundary trimming would avoid broken words but still discard
some requested facts; increasing top-k would confound paragraph selection with
packing; training a model would not restore information absent from its inputs.
Use the same complete paragraphs first, then diagnose residual semantic errors.

## Gate and interpretation

Keep all eleven conditions from the [span-ID proposal](span-id-answer-proposal.md),
including no more than three benchmark-unanswerable answers, citation-ID precision
at least saved-7B .4583333333, at least 20 answers, zero new failures versus the
constrained baseline, and the inherited control conditions. Add one requirement:
answerable token F1 must be **strictly greater than saved span-ID .2140841029**.
The exact comparator is recomputed from the verified saved span-ID predictions,
not the rounded number in this document. All twelve conditions must pass.

Report all metrics and failure counts even if they worsen. Also compare changes
on restored versus already-intact inputs, with subgroup labels fixed by original
string length rather than outcome. That subgroup diagnosis is exploratory on
repeatedly inspected development data. A positive bootstrap interval would be
descriptive, not selection-adjusted evidence or an untouched final result.

Real source quotations do not establish entailment. Review complete answers,
attribution and refusals separately, retaining known NCEL full-paper and TF-IDF
annotation caveats without rescoring. A development gate pass does not satisfy
independent human review, authorize promotion or waive any Phase 4 requirement.

## Requested compute

One new local attempt on RTX 4090 device 0: **at most 32 generation calls, 12,288
reserved output tokens, a 1,200-second hard worker deadline and $0 external spend**.
No training, warmup, retries, repair calls, extra candidates, downloads or runtime
changes. An attempt is consumed even if loading or execution fails.

Reuse Qwen/Qwen2.5-7B-Instruct revision
`a09a35458c702b33eeacc393d103063234e8bc28`, PyTorch 2.10.0+cu128,
Transformers 4.57.6 and Accelerate 1.12.0 in the isolated GPU runtime. Require
17 GiB free VRAM before loading, all parameters on CUDA in BF16, no offloading or
CPU fallback. Keep the frozen CPU runtime untouched. The prior span-ID run took
60.656 worker seconds; that is historical context, not a promise for longer inputs.

## Preparation and evidence checklist

- [x] Add a private contract adapter accepting bounded original paragraphs.
- [x] Restore only existing paragraph IDs from development units; retain refusals.
- [x] Reuse supervision, metering, output parsing and scoring in isolated adapters.
- [x] Exercise full synthetic lifecycle, tail-span citations and twelve gates.
- [ ] Complete code review and full software checks with PostgreSQL.
- [ ] Verify source/model/runtime hashes and tokenize all prompts without model loading.
- [ ] Record final readiness hash and obtain new explicit execution approval.
- [ ] After approval only: run once, independently reconstruct all outputs and report.

The preparation artifact records completion of the remaining checks without editing
this proposal after it is hashed. `artifacts/intact-passage-v1` is the unique run
root, created only on approved execution. Read-only preparation uses a separate
directory. Every prior experiment remains frozen and reproducible. The worker
receives only query ID, question and evidence; scoring labels stay outside it.
The input file, restored text, messages, span catalogs, source files and prior result
artifacts are hash-bound to approval. Calls are durably reserved before inference.

No fresh final-test access, deployment, publication or paid resource is requested.
The 100-question final test and the blank independent-human template remain unused.
