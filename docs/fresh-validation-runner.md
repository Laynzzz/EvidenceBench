# Fresh validation runner

Status: implemented and tested with synthetic models; real-model execution awaits
the new allowance in [the bounded proposal](fresh-validation-proposal.md).
Preparation does not consume the attempt or create a new index. No new model
quality claim follows from these implementation checks.

## Commands

Read-only preflight, with no model loading, network requests or attempt reservation:

```powershell
.venv/Scripts/python.exe -X utf8 -m evidencebench.evaluation.fresh_runner
.venv/Scripts/python.exe -X utf8 scripts/verify_fresh_validation.py
```

Only after explicit approval of the new allowance:

```powershell
.venv/Scripts/python.exe -X utf8 -m evidencebench.evaluation.fresh_runner --run-approved
```

This reserves the single attempt under `artifacts/fresh-validation-v1/`. A failed
process start, interrupted job or timeout keeps that reservation. Reusing the
directory fails; do not delete it to manufacture another attempt. The worker checks
the parent's preflight snapshot and can claim its token only once. Both Hugging Face
offline settings enter the worker environment before any model-library import.

After a completed run, verify its saved outputs without inference:

```powershell
.venv/Scripts/python.exe -X utf8 scripts/verify_fresh_validation.py --run artifacts/fresh-validation-v1/runs/RUN_ID
```

Replace `RUN_ID` with the emitted run folder. Incomplete attempts retain their
partial predictions, usage and termination record; the verifier does not relabel
them as complete.

Completion verification requires both the worker's complete manifest and its owning
supervisor's successful process exit. A worker that finishes writing just before
a watchdog timeout still belongs to a timed-out attempt and cannot verify as a
completed comparison. Verification also requires the pinned checkout/configuration:
later source, protocol or proposal edits change the snapshot. Preserve those files
for the run; record results in separate reports and status notes. Historical source
snapshots are retained in the run archive, but this verifier does not automatically
execute archived code or ignore current-checkout drift.

## Boundaries and evidence

Preflight validates the frozen release, dataset/report hashes, 50-query dev roster,
trained checkpoint and required cached model files. It hashes every file present
in both pinned model snapshots, including pooling/module/tokenizer and generation
configuration. It reads final-test label bytes only for checksum verification;
it never parses their examples. Fresh paper text is the retrieval corpus.

The worker embeds the 3,161 paragraphs once and retrieves/reranks each validation
question once. Both generators receive the same top-three 1,000-character passages
after the frozen refusal threshold. Only question text and retrieved text enter
model calls; reference answers and evidence IDs are used for scoring afterward.
The frozen generator implementations reuse the same loaded Qwen weights/tokenizer.
No serving database, deployment config or previous experiment output is changed.

Durable counters are charged before work: 3,161 document embeddings, 50 query
embeddings, 2,500 reranker pairs, 50 invocations per generator, 100 control and 50
candidate underlying generation calls. At most 13,200 output tokens are reserved
using each call's maximum. Reservations survive errors and are not a claim about
actual emitted token counts. A 2,700-second external watchdog covers worker startup,
model loading, indexing and comparison. No model-loading warmup inference is added.

Saved evidence includes source/config/environment snapshots, a separate index,
pre/post-rerank lists, packed IDs/text, both prediction streams, usage and metrics.
Retrieval failures are counted for both variants; generation failures stay with
their respective variant. Successfully captured retrieval evidence survives a
subsequent reranker failure. All 50 queries remain in metric denominators unless
the entire attempt is interrupted, in which case it remains incomplete.

Evidence recall is macro recall over answerable questions: pre/post rerank at depth
50 and packed IDs after threshold/top-three selection. Paragraph-ID presence does
not prove that supporting text survives character clipping. Timing combines shared
retrieval and each generator's own elapsed time; it is local offline timing, not
another deployed-service benchmark. The gate fails when either citation precision
is undefined; otherwise it applies the predeclared F1/failure/refusal/citation rules.

## Validation limits

Synthetic tests exercise call limits, persistent attempt accounting, subprocess
timeout/launch failure, offline startup, cache metadata integrity, reference-input
separation, shared contexts, refusal/failure paths, test-split rejection, the gate,
an entire worker with stand-in models, and saved-output corruption detection.
These establish implementation behavior, not real-model compatibility or quality.
Read-only preflight checks the actual local artifacts and caches without inference.
