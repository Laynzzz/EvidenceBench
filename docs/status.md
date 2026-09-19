# Execution status

Branch: `feat/mle-core`. The user selected an existing human-labeled benchmark;
QASPER v0.3 supplies labels, while NIST remains historical extraction evidence.
This is an experimental local release. Criteria below are not weakened to call it
production-ready or fully complete.

| Phase | Status | Evidence / remaining criterion |
|---|---|---|
| 1. Corpus and reproducible data | Verified | 191 papers, 5,908 paragraphs, byte-identical rebuild and frozen selection |
| 2. Labels and baselines | Verified | 200/50/100 human-labeled questions; baselines; 36 dev failures inspected |
| 3. Adaptation | Verified | 50/100/200 learning curve, hard/random ablation, three seeds, reload parity and failed-run retention |
| 4. Grounded answers | Implemented and measured; acceptance incomplete | Fresh validation candidate F1 .0754 versus .0120, zero versus 21 failures; promotion gate fails on abstention and citation precision; human support review missing |
| 5. Deployment | Verified locally | Five routes, real answer/refusal, DB outage, rollback, concurrency, fresh environment, 50-query Linux parity |
| 6. MLE focus | Verified within local scope | Controlled hard negatives, exact mining cache, three-seed sensitivity and failure analysis; agent deferred |
| 7. Final evaluation / portfolio | Verified experimental handoff | Five-system ranking, 100-question answers, restored artifact bundle and recorded API demo; human claim audit remains missing |

The frozen test reranker scores .5015 nDCG versus .3777 untuned, with paired
family-bootstrap difference interval [.0620,.1819]. No post-test model/prompt/
threshold tuning. The actual pipeline remains limited by generation failures.

49 tests passed with real PostgreSQL, including in a separate locked environment.
Ruff and schema mypy passed. Docker build/runtime checks passed locally. Remote CI
has not run because no push was requested. A terminal/API recording, HTML replay and five-minute script are provided.
The browser security policy blocked local-file preview; replay structure/JavaScript
were checked, but visual playback is unverified.

No paid services or cloud resources. All nine shared training-run slots were
used; none remain. Retain artifacts, model caches, local MLflow and database volume.
Existing job-market research links refer to files absent from this checkout; they
were not recreated or independently revalidated during implementation.

Final retained service: app and database running on loopback only. Reproduction bundle is 32,055,932 bytes; extraction, every included file hash, corpus/index and selected checkpoint were verified in a separate directory.

The user-requested [paper-based AI review](claim-review.md) is complete for all nine
emitted answers and 16 citation links. Paper correctness: two correct, four incorrect,
three ambiguous. Complete-answer citation support: two supported, six unsupported,
one unclear. PDF hashes match the frozen manifest; references and scoring remain
unchanged. This completes the requested AI audit, not the plan's independent human
review criterion. No further user action is needed for this audit.

The completed audit and updated handoff documents are retained in a separate local
[review supplement](../reports/claim-review-bundle.json). Its member hashes and
restoration are verified without replacing the original reproduction ZIP.

## Cycle 2 — completed development experiment, candidate not promoted

The [sentence selector comparison](../reports/answer-selection-development.md)
completed on the same 50 development queries: 30 answered, 20 refused, zero failures.
F1 regressed from .1184 to .1012 and citation-ID precision from .600 to .400, so
the predeclared quality gate failed. The source-sentence selection mechanism is
implemented and verified, but it is not a better accepted answer pipeline.
The original release and test outcomes remain unchanged.

One interrupted seven-query attempt and one completed attempt are retained. The
catalog bug and corrected two-attempt budget are explicit in the protocol. Current
checks: 58 tests pass, including real PostgreSQL; Ruff, schema typing and frozen
v1 reports pass. No extra training, model downloads, paid services or deployment.
The next release gate still requires a new evaluation design and fresh held-out
paper families, in addition to the independent human claim-review criterion.

## Cycle 3 — bounded improvement cycle completed

All three user-authorized local experiments completed. [Results](../reports/answer-spans-development.md):
plain short-answer generation regressed to .0263 F1; constrained spans reached
.1533; focused questions reached .1372. Both constrained variants had zero failures
and passed the predeclared exploratory gate. Constrained spans win the F1-first
development rule; focused refused all 12 unanswerable questions. Both reduce
citation-ID precision and retain semantic errors, so neither is deployed.

Exactly three attempts and 93 model calls; no new models, training or paid services.
Current checks: 66 tests pass including PostgreSQL, Ruff/format and schema typing
pass, and all three cycles' saved reports verify. The original service and final
test results are unchanged. Fresh held-out evaluation and independent semantic
review are still required for the next release; Phase 4 is not fully accepted.

## Offline diagnosis and fresh evaluation preparation

[Citation diagnostics](../reports/citation-diagnostics-development.md) explain the
28 constrained answers mechanically: 10 match gold citation IDs; among 18 mismatches,
12 have no gold paragraph in packed context, one quote also occurs in a gold passage,
three have gold available but select other evidence, and two answer unanswerable
queries. These are provenance categories, not semantic judgments.

The [fresh-evaluation protocol](fresh-evaluation-protocol.md) reserves 60 validation
and 120 final-test families, with deterministic fallback pools, excluding 333 known
previously selected, attempted or cached families. Only IDs were used for selection.
This is a reservation, not a built/aligned dataset or a new held-out result.
No model calls, downloads, training, deployment or spending occurred. The earlier
experiment allowance remains exhausted. Construction, a new bounded compute
allowance, fresh evaluation and human semantic review remain separate next steps.

Verification: 71 tests passed with real PostgreSQL (two existing dependency
deprecation warnings); Ruff, formatting and schema mypy passed. The new preparation
check and all three cycles' report/provenance verifiers passed. Independent code
review found no consequential issues. All checks were local and used no inference.

## Fresh evaluation dataset — constructed and verified

The [fresh dataset](../reports/fresh-dataset.md) now contains 50 validation and 100
final-test questions across 105 paper families, with 3,161 aligned paragraphs.
Validation is 38/12 answerable/unanswerable; test is 75/25. Family overlap with v1
and high-Jaccard document duplicate flags are both zero. A cache-only rebuild
reproduced the retained records and label bytes; 631 build files were unchanged.

The builder and seven new tests are committed as `1f5e773`. Review caught and fixed
redirect pacing and malformed-PDF recovery before acquisition. There were 155 PDF
downloads, two failed requests and one skipped unavailable paper; 119,437,820 PDF
bytes remain cached. All previously attempted families remain recorded.
No model inference, embeddings, training, paid services or deployment occurred.

The [next comparison proposal](fresh-validation-proposal.md) is prepared, not run:
50 fresh validation queries, the frozen control and constrained candidate, existing
models, CPU only, at most 150 underlying generation calls and 45 minutes, $0 external
spend. The previous experiment allowance remains exhausted. A new bounded allowance
is needed before executing this comparison; final test and independent human review
remain separate gates. Phase 4 acceptance is still incomplete.

Final checks: 78 tests pass with real PostgreSQL (two existing dependency warnings);
Ruff/format, schema typing, reservation verification and all three original cycles'
report/provenance checks pass. Fresh construction, cache rebuild and source-code
review are complete; no fresh model-quality result is claimed.

## Fresh validation runner — prepared, awaiting new allowance

The [runner](fresh-validation-runner.md) now implements the fixed control-versus-
constrained comparison, shared retrieval/context, bounded usage, offline model
loading, one retained attempt and a 45-minute external watchdog. Its read-only
preflight verifies the real corpus/labels, checkpoint and complete cached model
snapshots without inference. No attempt, index or fresh model predictions exist.

Eleven new synthetic tests cover the comparison, watchdog, cache integrity and an
entire worker with stand-in models, including saved-output verification and timeout
completion races. Code review found and corrected late offline initialization,
incomplete model metadata hashing, lost pre-ranking after a reranker failure and
the supervisor/worker completion race. Real-model compatibility and quality remain
unmeasured until the proposed execution is authorized and performed.

The next user decision is approval of the [prepared bounded comparison](fresh-validation-proposal.md):
one 50-question validation comparison, at most 150 underlying generation calls,
45 minutes, existing models on local CPU, $0 external spend. This does not authorize
training, final-test evaluation, extra attempts or deployment.

Current verification: 89 tests pass including real PostgreSQL; Ruff/format, schema
typing and all original-cycle report checks pass. Real read-only preflight is ready
and confirms no fresh attempt exists. [Readiness evidence](../reports/fresh-validation-readiness.json)
pins the current sources, inputs and cached models. No real fresh-model result exists.

## Fresh validation — completed; candidate not promoted

The user approved the prepared single attempt, recorded in
[authorization](../reports/fresh-validation-authorization.json). All 50 fresh
validation questions completed and saved artifacts passed the verifier, including
the supervisor's successful exit. [Results](../reports/fresh-validation.md): F1
.0120 to .0754, failures 21 to zero, unanswerable answers 3/12 to 6/12, citation-ID
precision .364 to .321. Two of four predeclared criteria fail; no promotion occurs.

This used 86 generation calls, 3,161 document embeddings, 50 query embeddings and
2,500 reranker pairs in 358.109 seconds, with $0 external spend. The allowance is
consumed. The job exited and its index, predictions, counters and manifests remain
local. Frozen source/config/data/model hashes and earlier reports verify unchanged.
No new source implementation was needed during execution or reporting.

Offline diagnosis finds evidence recall .9737 at depth 50, .4934 in reranked top
three and .3487 after threshold-based packing. These ID diagnostics suggest a
future evidence-selection/abstention study, not a validated fix. The fresh final
test remains unused and independent human claim review remains outstanding.
Phase 4 is still incomplete; the original experimental local release remains.
Earlier preparation sections above are historical records, superseded by this result.

## Offline selection audit — completed

- [x] Compare saved pre/post rankings and packing with fixed denominators.
- [x] Measure the frozen score's answerability separation.
- [x] Replay all stricter answer-suppression states without new inference.
- [x] Add synthetic regression tests and verify the retained report.

The [audit](../reports/fresh-selection-audit.md) finds that reranking raises top-three
gold recall from .1645 to .4934 and binary nDCG@10 from .2056 to .5080. Top-score
answerability AUC is .5702. One of 29 post-hoc stricter-cutoff states meets the old
numerical gate, but with only eight answers and F1 .0258. It is not selected or
promoted. A direct evidence-sufficiency decision is the recommended next experiment
direction; a relevance-score cutoff alone has weak discrimination in this sample.

The analysis script and ten synthetic tests are separate from frozen model code.
It verifies the original run first, pins its inputs and source, and supports exact
read-only recomputation. No model calls, downloads, training, final-test examples or
new spending were involved. All experimental allowances remain consumed. The failed
original comparison and Phase 4's unmet semantic-review criterion remain unchanged.

Verification: 99 tests pass including real PostgreSQL, with two existing dependency
deprecation warnings. Ruff, formatting and schema typing pass. The new audit's
exact recomputation, original fresh-run verification, earlier-cycle report checks,
artifact checksums and documentation links pass. Review found no calculation defect;
additional tests now exercise corrupted paired rankings and pre-write verification.
