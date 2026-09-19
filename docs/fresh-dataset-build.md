# Fresh dataset construction record

The user authorized construction of the reserved fresh evaluation dataset on
2026-09-19. This permits public PDF acquisition, local extraction/alignment and
label checks; it does not replenish model-experiment or training allowances.
The [predeclared protocol](fresh-evaluation-protocol.md) controls selection and quotas.

## Execution checklist

- [x] Implement a separate builder and tests using synthetic content.
- [ ] Review the builder before public PDF acquisition.
- [ ] Acquire and align enough papers for 50 validation / 100 test questions.
- [ ] Rebuild from cache without network or writes; compare retained artifacts.
- [ ] Check cross-family duplicates, original-release integrity and all tests.
- [ ] Record counts/hashes and update learning and handoff documents.

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
