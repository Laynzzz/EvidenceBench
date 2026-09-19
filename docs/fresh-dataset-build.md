# Fresh dataset construction record

The user authorized construction of the reserved fresh evaluation dataset on
2026-09-19. This permits public PDF acquisition, local extraction/alignment and
label checks; it does not replenish model-experiment or training allowances.
The [predeclared protocol](fresh-evaluation-protocol.md) controls selection and quotas.

## Execution checklist

- [x] Implement a separate builder and tests using synthetic content.
- [x] Review the builder before public PDF acquisition.
- [x] Acquire and align enough papers for 50 validation / 100 test questions.
- [x] Rebuild from cache without network or writes; compare retained artifacts.
- [x] Check cross-family duplicates and original-release integrity.
- [x] Record counts/hashes and update learning and handoff documents.

Use the existing feature branch. The frozen v1 builder, models and benchmark stay
unchanged. New downloads and extraction caches are under `data/raw/qasper-fresh-v1/`;
new paragraphs under `data/processed/qasper-fresh-v1/`; labels under
`data/labels/qasper-fresh-v1/`. The report is `reports/fresh-dataset.json`.
The builder prints aggregate progress and error types, never question/reference text.

Each download attempt is recorded before the request; interruptions consume that
attempt. At most two requests per paper are allowed across restarts. HTTP 429 stops
the whole acquisition. Redirect hops are explicitly counted and delayed within the
same two-request limit; only HTTPS redirects within arxiv.org are followed.
Bounded streamed responses prevent downloading beyond 30 MB. Invalid PDF parser
errors are retained as skips so the next reserved family can be considered.
Cached PDFs and extracted pages have checksums. Re-running the build recomputes
selection from the same order and cached data, rather than appending another sample.
The build contract pins source code, extraction package versions and protocol hashes.

```powershell
.venv/Scripts/python.exe -X utf8 scripts/build_fresh_qasper.py
.venv/Scripts/python.exe -X utf8 scripts/build_fresh_qasper.py --check
```

The second command requires complete caches, recomputes alignment and selection,
checks the output corpus and labels, checks near-duplicate document families against
v1 as well as the fresh corpus, and writes nothing. Quota or integrity failures stop
the build without weakening the protocol. Final-test content remains procedurally
reserved; upstream labels are human annotations, but page locations are automatic
and generated-answer semantic review has not occurred.

## Implementation verification

Before acquisition, all 78 tests passed with real PostgreSQL; Ruff/format and schema
mypy passed. Seven synthetic builder/download tests cover quota selection and the
two-query family cap, deterministic ordering, duplicate/missing-evidence rejection,
durable retry exhaustion, bounded downloads, cache tampering, rate limits, redirects,
malformed-PDF recovery and a complete build/read-only rebuild. These tests do not
constitute model evaluation.

Code review found unpaced automatic redirects and unhandled parser errors. Both
were reproduced by failing tests and corrected before any real acquisition.
The implementation is committed as `1f5e773`; the original release-lock and
reservation verifiers passed before construction began.

The next compute request is specified separately in
[the fresh-validation proposal](fresh-validation-proposal.md): one CPU-only,
50-query comparison with fixed models, a 150-generation-call cap and a 45-minute
deadline. This proposal has not been executed or treated as approval.

## Executed construction and rebuild

The [dataset report](../reports/fresh-dataset.json) records 150 questions, 105 paper
families and 3,161 aligned paragraphs. Validation uses 33 families for 38 answerable
and 12 unanswerable questions; final test uses 72 families for 75/25. Five validation
and eight test families came from the reserved fallback pools. No selection rules
were changed after looking at outcomes.

Acquisition retained 155 PDFs totaling 119,437,820 bytes. There were 157 requests:
155 successful downloads and two failed attempts for one skipped paper. Of the
downloaded papers, 50 supplied no accepted questions under the fixed filters.
Retain these artifacts and attempts; they count as exposed for any later reservation.
Nothing was uploaded, published or deployed. No embeddings, generation or training ran.

`build_fresh_qasper.py --check` recomputed all paragraph alignment and query selection
from cached data and matched the corpus and exact label bytes. The before/after
snapshot confirmed unchanged sizes and modification times for 631 build files.
Known prior family overlap and document-pair Jaccard flags at the existing .85
threshold were both zero. This is not a guarantee against semantic similarity.
The [verification record](../reports/fresh-dataset-verification.json) contains counts
and the dataset report hash. The original release lock remained valid.
