# Fresh evaluation preparation

Status at reservation: **paper families reserved; construction and evaluation not run**.
Subsequent construction evidence is tracked in [the build record](fresh-dataset-build.md).
The original test has been exposed, and the old development set has been reused
for multiple experiments. Neither can support a new untouched-test claim.

## Executed preparation

- [x] Audit saved development citation mismatches without inference.
- [x] Freeze family exclusions and deterministic candidate/fallback order.
- [ ] Acquire PDFs, align paragraphs, validate labels and freeze new dataset hashes.
- [ ] Declare a new compute allowance and freeze evaluation runner/configuration.
- [ ] Run fresh validation; freeze the final decision before final-test access.
- [ ] Run final test once and complete independent human claim-support review.

The [reservation manifest](../data/manifests/fresh-evaluation-reservation.json)
excludes 333 unique families appearing in the v1 selection, alignment-attempt audit,
downloaded PDFs or processed caches. It preserves both the pre-acquisition inventory
and exclusion reasons. Source JSON and selection/audit files have SHA-256 hashes.
Only raw QASPER dictionary keys are used for reservation; questions, answers, titles
and paper contents are not used to choose families or printed for inspection.

Official QASPER dev supplies 60 primary validation families and 181 ordered fallback
families. Official QASPER test supplies 120 primary final-test families and 211
fallback families. All pools are disjoint and exclude known prior local use. This
does not prove that pretrained models never encountered these public papers, or
that no earlier unrecorded inspection occurred. It is a local evaluation safeguard.

Within each source partition, sort paper IDs by
`sha256("fresh-eval-v1:42:" + paper_id)`. The first 60/120 form the primary groups;
the remaining order is fixed for fallback. No rerolling seeds or replacing difficult
papers based on predictions. Re-running preparation cannot overwrite a differing
manifest. Verification retains the original cache snapshot so future planned PDF
acquisition cannot silently change the reservation.

## Construction rules fixed before new answers are inspected

Use a separate `qasper-fresh-v1` corpus/label directory and new manifests. Never call
the original builder directly: it writes v1 manifest paths. Reuse its reviewed
annotation-selection and automatic page-alignment helpers without changing them.
Keep all human answer alternatives, exclude mixed answerability, and require every
annotated evidence passage to map to retained paragraph IDs for answerable queries.
Page alignment remains automatic, not human-reviewed page attribution.

Target 50 validation queries (38 answerable/12 unanswerable) and 100 final-test
queries (75/25). These are practical evaluation sizes, not a statistical power claim.
Visit families in their frozen order and questions by SHA-256 of
`fresh-eval-query-v1:42:<query_id>`. Take at most two accepted queries per family,
filling each answerability quota without model scores or correctness-based selection.
Skip unsupported annotations, failed alignment, duplicate question IDs, PDFs over
30 MB or over 250 pages, and unavailable PDFs with a recorded reason. Limit acquisition
to two attempts per paper, at least three seconds between requests. Use fallback
families only after primary candidates are exhausted, and preserve every skip.
If quotas cannot be met, report the shortfall; do not relax rules silently.

Final-test construction should emit aggregate counts/hashes and validation errors
only. Do not inspect its examples while developing. Once corpus/labels are frozen,
reserve a single final evaluation; any subsequent changes consume that test's
unseen status. A local file is a procedural holdout, not an access-control barrier.

## Candidate and evaluation boundary

The preferred candidate is the already selected cycle-3 **constrained** span
generator. Its comparison is the frozen v1 generator with the same cached models,
retriever/reranker weights, threshold and passage/token limits. Fresh document
embeddings/index construction will be new compute; it has not been run. No weights
are retrained. The focused variant is a recorded development trade-off, not a
per-query fallback or a newly selected winner.

Before any model run, pin an evaluation manifest with source/config/model/corpus/
label hashes and a bounded allowance covering embedding and inference calls,
timeouts and retained failures. The prior nine training slots and three cycle-3
experiments are exhausted. This preparation does not grant new runs or spending.

Fresh validation is a check of the fixed candidate, not an unrestricted tuning
loop. A promising candidate must improve answerable token F1, have no more explicit
failures or unanswerable answers, and have citation-ID precision no lower than the
control. Record coverage, false refusals, citation recall and all denominators as
well. This adds citation precision to the exploratory gate because the old gate
allowed a substantial regression; it does not revise past experiment decisions.
If the fixed candidate fails, retain the result and leave the new final test unused.
Any revised candidate needs a new explicit experiment protocol.

If validation passes, freeze the candidate and score both systems on final test
once. Report every result, including an adverse result. Use paired family bootstrap
intervals for answerable F1 differences, alongside counts and conditional citation
precision. Do not describe an interval spanning zero as demonstrated improvement.
Report evidence recall before packing and after packing to separate evidence
availability from generation errors. Semantic correctness and claim support still
need the plan's independent human review; ID membership, exact quotes, upstream
human labels and AI audits do not satisfy that criterion. Deployment is not
automatically authorized by a passing exploratory or fresh-validation comparison.

## Reproduction

```powershell
.venv/Scripts/python.exe -X utf8 scripts/prepare_fresh_evaluation.py --check
```

This verifies the saved audit, reservation and original release lock without
inference, downloads or writes. Running without `--check` creates missing outputs
exclusively, and refuses to replace differing retained outputs.
