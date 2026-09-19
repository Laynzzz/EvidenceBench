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

The remaining human gate has a concrete [nine-answer review form](claim-review.md). It is explicitly pending, not agent-filled human judgment.
