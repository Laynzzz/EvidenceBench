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
| 4. Grounded answers | Latest complete-answer gate failed; acceptance incomplete | Complete-answer F1 .1438, 10 failures, 5/12 unanswerable answers; saved 7B span candidate retains its earlier gate pass; human support review and fresh final evaluation remain pending |
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

At the original handoff, app and database were running on loopback only. After the September 24 Docker recovery, the database is healthy and the app remains stopped. Reproduction bundle is 32,055,932 bytes; extraction, every included file hash, corpus/index and selected checkpoint were verified in a separate directory.

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

## Support-filter experiment — prepared; awaiting new allowance

The [fixed proposal](support-filter-proposal.md) and
[runner](support-filter-runner.md) are implemented. Each of the 28 saved answers
would receive one cited-evidence support decision; the other 22 rows stay unchanged,
and all 50 are scored. References and gold labels do not enter checker inputs.
The original gate is supplemented by no new failures, 80% candidate F1 retention
and at least 14 retained answers. This is a proposed same-model self-check, not
independent human semantic review or an accepted replacement.

Sixteen synthetic tests cover the checker adapter, filtering, full worker output,
strict verification, approval binding and timeout behavior. Review suggested stricter
saved-trace validation; failing tests reproduced those gaps and the fixes pass.
All 115 tests pass with real PostgreSQL; Ruff/format and schema typing pass. Existing
reports and the fresh-selection audit still verify. Real read-only preflight confirms
matching cached artifacts and no new attempt. [Readiness](../reports/support-filter-readiness.json)
pins the exact proposed execution. No real checker inference has occurred.

Required next user decision: approve one new local attempt, at most 28 generation
calls and 20 minutes, $0 external spend. The previous allowance explicitly covered
one completed comparison and is exhausted. No final-test access, training, extra
attempts or deployment is included. Preparation is complete; execution waits for
that new approval. Phase 4 acceptance remains incomplete.

## Support filter — completed; no improvement

The user approved the exact prepared snapshot. [Verified results](../reports/support-filter-development.md):
the model accepted all 28 answers, including all six answers on unanswerable questions.
No output changed. F1 remains .075424, citation-ID precision .321429, failures zero;
the same two original gate conditions fail. The filter is rejected for promotion.

One attempt consumed 28 calls, 224 reserved and 84 actual output tokens; the
supervisor exited successfully in 31.375 seconds. All 50 output rows, transformations,
model inputs, source/config/data hashes, metrics, usage and completion verified.
The checker added .796 s p50 / .975 s p95 per checked answer on this CPU. No training,
new models, spending or deployment occurred. The preparation's 115-test result is
historical test evidence; this step verified real model execution and retained results.

The user also identified an RTX 4090 and requires approval for every new model
training/evaluation attempt. Read-only inspection confirmed the GPU and 24,564 MiB
reported memory; the current PyTorch package is CPU-only. [Compute policy](compute-policy.md)
records the preference and need for a separate compatible GPU runtime. No GPU model
work was run. The original service and unused final test remain unchanged; Phase 4
still lacks accepted answer quality and independent human semantic review.

## GPU support-checker comparison — prepared; awaiting approval

- [x] Pin Qwen2.5-7B revision and verify all 14 model files (15.24 GB).
- [x] Prepare an isolated CUDA runtime; check dependencies and imports.
- [x] Implement offline worker, exact-snapshot approval and single-attempt limits.
- [x] Verify synthetic behavior, review fixes and existing frozen evidence.
- [ ] Obtain approval for one real GPU evaluation; execute and report its outcome.

The [proposal](gpu-support-proposal.md), [runner guide](gpu-support-runner.md) and
[readiness snapshot](../reports/gpu-support-readiness.json) describe 28 support
checks of saved answers on the same 50 reused development questions. The prompt,
cited-only payloads and seven gate conditions stay fixed. The model, precision,
hardware and runtime change, so this is not a pure model-size ablation.

125 tests pass including real PostgreSQL, with two existing dependency warnings.
Ruff, formatting, schema typing, CUDA-environment dependency/import checks and
existing report verifiers pass. Ten synthetic tests cover the new orchestration;
review fixes handle Windows Unicode, changed scoring data and extra checkpoints.
No GPU model loading, inference or training occurred. No authorization or real
attempt exists. Next execution requires the user's explicit per-run approval:
one attempt, at most 28 calls/224 reserved output tokens/20 minutes, $0 external
spend. The 100-question final test remains unused; Phase 4 acceptance and
independent human generated-claim review remain incomplete.

## GPU support checker — completed; not promoted

The user approved the exact prepared snapshot and the single RTX 4090 evaluation
completed. [Verified results](../reports/gpu-support-development.md): 24 UNSUPPORTED,
four SUPPORTED, zero failures. Answers to unanswerable questions fall from six to
one, but answer coverage falls from 56% to 8%, F1 from .075424 to .013068 and
citation-ID precision from .321429 to .25. Four of seven gate conditions pass;
F1 retention, answer retention and citation precision fail. No promotion occurs.

One attempt used 28 calls, 224 reserved and 84 actual output tokens, 38.765 seconds
of worker time and $0 external spend. Checker-only p50/p95 are .135/.207 seconds,
not serving latency. Model loading and inference on the pinned CUDA/BF16 setup
are now verified. Launch verification and separate read-only verification both
pass. The preparation's 125-test result remains historical software-test evidence.
The allowance is consumed; no retry or new model work is authorized. Final test
remains unused and Phase 4 independent human review/quality acceptance remain open.

## Saved-answer audit — completed

[Audit](../reports/gpu-answer-audit.md): all 28 source matches are not proof of
answer quality; 19 of 22 answerable outputs have better-overlap eligible spans
available. Eight new tests pass (133 total including PostgreSQL). The assistant
draft identifies 20 nonresponsive, six partial, one unclear and one label-conflict
case; these are not human labels. A masked review packet and blank response
template are ready. No model run, label edit or final-test access occurred.
The next comparison will isolate larger-model answer selection on fixed inputs.

## Fixed-input GPU generation — prepared; new allowance pending

- [x] Reuse frozen prompts/evidence/choices for 32 nonempty inputs.
- [x] Preserve 18 original refusals and all-50 scoring denominators.
- [x] Prepare 32-call/2,048-token/20-minute single-attempt supervision.
- [x] Verify 11 new synthetic tests, full 144-test suite and review fix.
- [ ] Obtain new explicit approval and execute the comparison once.

[Proposal](gpu-generation-proposal.md), [runner](gpu-generation-runner.md) and
[readiness](../reports/gpu-generation-readiness.json) are complete. The new gate
retains all seven prior conditions and adds F1 strictly above the constrained
baseline. No source weights, references, scores or deployed behavior changed.
Model files/runtime/predecessor evidence verify; no new GPU model load, inference,
training or final-test access occurred. This preparation is not Phase 4 acceptance.

## GPU generation — completed; development gate passed

[Results](../reports/gpu-generation-development.md) verify one approved attempt:
32 calls, 380 actual output tokens, 2,048 reserved tokens and 50.750 seconds of
worker time. The candidate answers 24/50 with zero failures; F1 .123578 versus
.075424 and citation-ID precision .458333 versus .321429. Unanswerable answers
fall from six to three. All eight gate conditions pass. A descriptive family
bootstrap interval for the F1 gain is [-.022313, .125398], including zero.

Launch verification and separate read-only recomputation pass. The 18 threshold
refusals are unchanged; reference labels and scoring denominators stay frozen.
The preparation's 144 software tests are historical verification, not rerun here.
[Human review packet](../reports/gpu-generation-human-review.md) contains all 24
answers with citations and paper links; the response template is blank. Human
claim-support review remains required by the plan. No service change, training,
final-test access or additional attempt is authorized. The allowance is consumed.

## GPU answer paper review — completed with AI assistance

- [x] Review all 24 emitted answers against their actual citations and local papers.
- [x] Separate responsiveness, completeness, citation support and paper correctness.
- [x] Record source pages, corrected answers and scope/annotation conflicts.
- [x] Preserve frozen outputs, metrics, labels and blank human response template.

[Review](../reports/gpu-generation-ai-review.md): 3 adequate, 11 partial,
8 inadequate and 2 ambiguous under the stated rubric. The main failure is choosing
the wrong information despite copying source text. Case 3 also shows why a paper's
conclusion must be checked against its result table. Case 24 remains a documented
benchmark-label conflict, with no rescore. This is a single, non-blinded assistant
review, not independent human evaluation; Phase 4 is still incomplete.

The user's requested review is finished, with no new model calls, training or
final-test access. Future preparation can address answer selection and completeness;
any new model experiment still requires a concrete proposal and fresh approval.

## Complete-answer comparison — completed; not promoted

- [x] Implement complete-answer JSON and exact source-body quotation validation.
- [x] Keep worker inputs free of old answers, references and annotation labels.
- [x] Preserve 18 threshold refusals and all 50 scoring rows.
- [x] Verify 26 new synthetic checks and all 170 software tests, including PostgreSQL.
- [x] Fix the code-review finding binding baseline selection to the verified prior run.
- [x] Verify cached source/model/runtime artifacts and 32 payloads without inference.
- [x] Obtain new explicit approval and execute the single bounded GPU attempt.
- [x] Independently recompute saved results and diagnose all ten validation failures.
- [x] Preserve all 19 emitted answers in a separate review packet.

[Proposal](grounded-answer-proposal.md), [runner](grounded-answer-runner.md) and
[readiness](../reports/grounded-answer-readiness.json) preserve the frozen preparation.
[Verified results](../reports/grounded-answer-development.md): 19 answers, 21 refusals,
10 failures; F1 .143765 versus .123578, citation-ID precision .347826 versus .458333,
and five versus three answers to unanswerable questions. Six of eleven conditions
pass; the candidate is not promoted. The F1-gain interval [-.048272, .086372]
includes zero and is descriptive on repeatedly used development data.

One attempt used 32 calls, 3,443 actual output tokens, 12,288 reserved tokens and
176.969 seconds of worker time at $0 external spend. Seven failures violate quote
requirements and three have malformed JSON; no runtime failure or timeout occurred.
The allowance is consumed. No retry, training, service change or final-test access
occurred. The 170-test preparation result is historical and was not rerun here.
The next engineering work is to design a simpler auditable citation output while
addressing answer completeness; it needs a new proposal before any model run.
Independent human review and Phase 4 acceptance remain incomplete.

## Source span-ID comparison — prepared; new approval needed

- [x] Replace model-copied quotes with IDs of deterministic source spans.
- [x] Preserve original inputs, 18 threshold refusals, all-50 scoring and eleven gates.
- [x] Verify 24 new synthetic checks and all 194 software tests with real PostgreSQL.
- [x] Complete independent contract/runner reviews; no actionable findings.
- [x] Verify frozen assets and all 32 prompt lengths without model loading.
- [ ] Obtain new explicit approval before the single model attempt.

[Proposal](span-id-answer-proposal.md), [runner](span-id-answer-runner.md) and
[readiness](../reports/span-id-answer-readiness.json) specify one RTX 4090 attempt:
at most 32 calls, 12,288 reserved output tokens, 20 minutes and $0 external spend.
All 543 source spans preserve body text and offsets; prompts use 484–1,142 of 2,048
input tokens. Quote copying/length errors are eliminated structurally, but malformed
JSON, unsupported answers and incomplete evidence remain possible. Model quality
is unmeasured; Phase 4 remains incomplete and final test unused.

The first full software check failed because Docker's engine was unavailable.
[Socket recovery](../reports/docker-startup-recovery.md) restored Docker and the
existing database without resetting volumes; the subsequent suite passed 194 tests
with two existing deprecation warnings. Runtime socket backups are retained. No new
training, inference, authorization or attempt exists for this candidate.
