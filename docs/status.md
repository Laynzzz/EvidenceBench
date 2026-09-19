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
| 4. Grounded answers | Implemented and measured; acceptance incomplete | V3 dev F1 .1184, coverage 18%, 22/50 failures; human generated-claim support audit missing |
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
