# Verification and claim-to-artifact index

Recorded locally on 2026-09-18/19 (UTC rollover). No push, publication or paid service.
Portable summaries are committed under `reports/`; raw artifacts are retained locally
and included selectively in the reproduction bundle. Original PDFs are not redistributed.

| Claim | Evidence | Scope / limitation |
|---|---|---|
| Human benchmark provenance | `data/manifests/qasper-v1.json`, `qasper-selection.json`, `qasper-protocol.json`; QASPER dataset card | Upstream human questions/answers/evidence, automated page mapping |
| 200/50/100 split, 191 papers, 5,908 paragraphs | Dataset manifest, public label files, `artifacts/verification/qasper-data-audit.json` | Filtered, title-conditioned NLP papers; not official leaderboard |
| Repeated data bytes | `data/processed/qasper-v1`, `artifacts/verification/qasper-repeat`, `qasper-repeat-labels` | Identical fingerprint and labels, original pinned PDF bytes required |
| Initial NIST pilot | `reports/nist-pilot-card.md`, `artifacts/verification/corpus-repeat` | Historical 1,773 chunks; its 12 draft questions never used for selection |
| Baselines and dev selection | `artifacts/runs/20260919T022155Z-6b3e64a8cc`, `reports/experiment-summary.json` | 38 answerable dev questions, 21 families; 12 unanswerable separate |
| Trained model, learning curve and ablation | `artifacts/training/*`, `reports/development-evaluation.md`, `development-comparison.png` | 50/100/200 queries; matched random/hard negatives; source archives |
| Selected checkpoint | `artifacts/training/20260919T021808Z-bce3010267`, `artifacts/deployed/7a7ab6f966a2` | Tree hash in `configs/release.yaml`, reload score parity 1e-6 |
| Seed uncertainty | Seeds 42/43/44: runs ending `bce3010267`, `7975d080bc`, `a791c82d12` | Same dev set, not independent generalization samples |
| Failed training retained | `artifacts/training/20260919T021555Z-346e0e4c88` | Setup failure before optimization; not omitted from budget |
| Negative mining audit | `artifacts/verification/mining-cache-parity.json`, `negative-phrase-audit.json` | Cached pairs byte-identical; phrase matches cannot prove true negatives |
| Development generation | `artifacts/answers/20260919T024110Z-6fd1dea23b`; `development-answers-v3.json` | 50 dev questions; 18% coverage, F1 .1184, 22 failures |
| Earlier generation failures | `smol-aborted-pilot.json`; Qwen v2 run `20260919T022955Z-8a2d02c769` | Smol pilot only 15/50 completed; v2 Boolean contract bug documented |
| Development failure review | `reports/development-failures.md` | 36 retained failures; agent inspection, not new human semantic labels |
| Frozen final ranking | `data/manifests/release-lock.json`; `artifacts/runs/20260919T025255Z-c1ee0ecf84` | 100 questions / 75 answerable / 41 answerable families; no test reselection |
| Final uncertainty/recalculation | `reports/final-evaluation.json` and `.md` | nDCG delta .1238; paired family interval [.0620,.1819]; raw predictions rechecked |
| Real local API and recovery | `reports/serving-evaluation.json` and `.md`; `artifacts/verification/api-benchmark.json` | Actual answer/refusal, DB outage, rollback; local CPU service only |
| Cross-environment ranking parity | `artifacts/verification/serving-parity.json` and predictions | Exact selected top-20 match on all 50 dev queries, Windows/NumPy vs Linux/PG |
| Memory/latency | Serving report, image ID and cgroup peak counter | 3.38 GiB peak container accounting; five repeated warm answers, small workload |
| Tests / fresh environment | `artifacts/verification/clean-final-tests.log`, current pytest output | 49 passed including real PG; mocked generation contracts do not prove quality |
| Formatting and types | Ruff format/check; mypy `src/evidencebench/schemas.py` | Mypy covers shared schemas, not whole-project typing |
| Container build | `artifacts/verification/final-image-v3-build.log` | Local successful build; image source/runtime checked through real serving |
| CI configuration | `.github/workflows/ci.yml` | Defined, not remotely executed; repository has not been pushed |
| Budget | `configs/budget.yaml`, local manifests | All nine training slots; zero paid provider/cloud jobs; local resource cost not priced |
| Learning and demo | `docs/teaching-guide.md`, `interview-prep.md`, `demo.md`, `runbook.md` | Prepared learning path; no claim of user mastery or camera/screen video |

## Recalculate without changing models

`uv run evidencebench recalculate --run artifacts/runs/20260919T025255Z-c1ee0ecf84`
checks the predictions hash and recomputes ranking aggregates. Answer metrics use
`evidencebench.evaluation.answers.answer_metrics` over their saved prediction rows;
check the manifest's predictions hash first. Family-bootstrap calculations use the
frozen `evaluation/metrics.py`, paired on identical query IDs.

## What remains unproven

Human semantic support/unsupported-claim rate for generated outputs is unmeasured.
Reference F1 and citation-ID agreement do not substitute for this criterion.
There is no representative hiring-market claim, official QASPER leaderboard result,
production traffic, public hosting, GPU training, or evidence that the user has
already independently mastered the agent-assisted code. Historical market-research
files referenced in the plan are absent from this checkout.

## Retained local resources

Python environments, downloaded public source/model files, corpus/index artifacts,
checkpoints, local MLflow database/runs, Docker images and the project PostgreSQL
volume remain. `docker compose stop` preserves them. The final handoff reports
whether the app/database are running. No unrelated Docker projects were modified.

Additional reproduction evidence: `artifacts/verification/training-reproduction.json` (identical pairs, parameter values and dev nDCG; checkpoint metadata differs), `artifacts/verification/index-repeat.json` (identical vector bytes/IDs; instance fingerprint differs with execution provenance). Use `python scripts/verify_reports.py` for captured-roster report verification.

Recorded demo: `reports/demo.cast` and `reports/demo.html`; actual local HTTP output, 12 timestamped events. Static HTML/event/JavaScript checks passed; browser policy blocked local-file visual preview. Bundle: `reports/artifact-bundle.json`, 201 files / 32,055,932 bytes; all hashes and restored corpus/index/checkpoint verified.

The completed [paper-based AI review](claim-review.md) covers all nine emitted
answers and 16 citations. [Structured judgments](../reports/claim-review-ai.json)
include original prediction/source hashes, PDF pages, citation IDs, rationales and
suggested answers. Two answers are clearly correct and supported; the audit is
descriptive and does not satisfy independent human review. The existing artifact
bundle predates this audit; these review files are tracked separately in Git and
packaged in the [review supplement](../reports/claim-review-bundle.json).

Audit verification on 2026-09-19 checked all nine PDF hashes, nine prediction/reference
matches, 16 citation IDs, verdict totals and unchanged original excerpts. Results:
`artifacts/verification/paper-review/verification.json`. The existing
`python scripts/verify_reports.py` check also passed after the review, confirming
the captured ranking/answer/bootstrap/development reports still reproduce.

Cycle 2: [development report](../reports/answer-selection-development.md) and
[structured results](../reports/answer-selection-development.json). A complete
50-query run and interrupted seven-query attempt are retained under
`artifacts/answer-selection-cycle2/`. Source/config/environment and prediction hashes
are recorded per run. `python scripts/verify_answer_selection.py` recalculates the
metrics, verifies source citations and confirms the v1 release lock. The candidate
failed the quality gate and was not deployed. Earlier ZIP bundles predate this cycle.

Cycle 3: [comparison](../reports/answer-spans-development.md),
[structured results](../reports/answer-spans-development.json), and
[predeclared protocol](answer-improvement-cycle3.md). All three variants completed
under `artifacts/answer-improvement-cycle3/`, with atomic attempt records and
source/config/prediction snapshots. `python scripts/verify_span_experiments.py`
verifies all three results and citation provenance without model inference.
The preferred development candidate reaches .1533 F1 but citation-ID precision
declines; it is not deployed or a new held-out result. Earlier ZIP bundles are
historical and do not contain this cycle's code or artifacts.

Offline preparation: [citation diagnostics](../reports/citation-diagnostics-development.md),
[per-query categories and hashes](../reports/citation-diagnostics-development.json),
[fresh evaluation protocol](fresh-evaluation-protocol.md), and
[family reservation](../data/manifests/fresh-evaluation-reservation.json).
`python scripts/prepare_fresh_evaluation.py --check` reproduces the mechanical audit
and verifies the deterministic reservation using its retained cache inventory.
No model inference or new-test scoring is involved. The reservation excludes known
local exposure; it cannot guarantee absence from a model's pretraining data.

Fresh construction: [dataset card](../reports/fresh-dataset.md),
[hash/count report](../reports/fresh-dataset.json),
[rebuild verification](../reports/fresh-dataset-verification.json), and
[execution record](fresh-dataset-build.md). The separate builder reproduces 150
questions / 105 papers / 3,161 paragraphs with `--check`, without model calls or
network requests. Labels are under `data/labels/qasper-fresh-v1/`; source PDFs and
paragraph caches remain local. Final-test examples were not displayed or inspected.
Historical ZIP bundles do not include this dataset or its builder.

Fresh runner preparation: [commands and boundaries](fresh-validation-runner.md),
[compute proposal](fresh-validation-proposal.md), and
[readiness record](../reports/fresh-validation-readiness.json). Default execution of
`python -m evidencebench.evaluation.fresh_runner` performs read-only preflight;
`scripts/verify_fresh_validation.py --run RUN_PATH` verifies saved results after
an approved run. The current record is preparation evidence, not model evaluation.

Fresh validation execution: [result and failed gate](../reports/fresh-validation.md),
[structured verification and hashes](../reports/fresh-validation.json),
[supplementary diagnostics](../reports/fresh-validation-diagnostics.json), and
[authorization](../reports/fresh-validation-authorization.json). All 50 paired
questions completed under `artifacts/fresh-validation-v1/runs/20260919T233427Z-ddfba1b48e`.
The candidate's F1 .0754 versus .0120 and zero versus 21 failures do not qualify it
for promotion: unanswerable answers increase and citation-ID precision declines.
The read-only verifier reproduces metrics and checks provenance, usage and supervisor
completion. Source commit is `529a74d`; the new reports preserve its frozen snapshot.
This is validation evidence on new families, not a final-test or semantic-quality
claim. The final test remains unused, and historical ZIPs predate this comparison.

Offline selection audit: [interpretation](../reports/fresh-selection-audit.md),
[rankings, cutoff replay and hashes](../reports/fresh-selection-audit.json), and
[recomputation script](../scripts/audit_fresh_selection.py). The script's `--check`
mode verifies the original 50-query validation run, then reproduces binary evidence
ranking metrics, score AUC and every stricter answer-suppression state without
inference or writes. Ten synthetic tests cover calculations and rejection paths.
Its single post-hoc passing replay state is not a selected or validated model.

Support-filter preparation: [fixed proposal](support-filter-proposal.md),
[commands and bounds](support-filter-runner.md),
[readiness hashes](../reports/support-filter-readiness.json), and
[runner](../scripts/run_support_filter.py). Sixteen synthetic cases exercise the
adapter, transformations, evaluation guards, ledger/watchdog and verification.
Default CLI execution performs real integrity/cache checks without model loading.
No support-filter attempt or result exists yet; the separate new allowance is
pending. Future real outputs belong under `artifacts/support-filter-v1/`.

Support-filter execution: [outcome](../reports/support-filter-development.md),
[metrics, counts and hashes](../reports/support-filter-development.json), and
[approval receipt](../reports/support-filter-authorization.json). All 28 checked
answers were accepted, so no quality metric changed and the fixed gate failed.
`python scripts/run_support_filter.py --verify` checks the retained single attempt,
including supervisor success and all 50 output transformations, without inference.
The new [GPU compute policy](compute-policy.md) records hardware inspection and the
user's per-experiment approval requirement; it is not GPU performance evidence.

## Prepared GPU support comparison

- [Proposal](gpu-support-proposal.md): fixed comparison and pending compute scope.
- [Runner guide](gpu-support-runner.md): preflight, approval, execution and verification.
- [Asset manifest](../reports/gpu-support-assets.json) and [runtime lock](../configs/gpu-support-requirements.lock): pinned model files and isolated dependencies.
- [Readiness](../reports/gpu-support-readiness.json): exact proposed snapshot; zero model calls.
- [Synthetic tests](../tests/unit/test_gpu_support.py): Unicode, input isolation, inventory, budget, approval, scoring integrity and termination.

Preparation supports reproducibility and software-behavior claims only. No GPU
quality, performance or memory-fit result exists; no new model run is authorized.

## Completed GPU support comparison

[Verified report](../reports/gpu-support-development.md),
[structured results](../reports/gpu-support-development.json) and
[approval](../reports/gpu-support-authorization.json) document one completed GPU
attempt: 28 calls, 24 rejections, four retained answers, no failures, failed quality
gate. The pinned model loaded and ran on RTX 4090; this does not establish general
training capacity or an accepted answer system. The preparation/readiness records
above remain historical. No final-test access or independent human review occurred.

## Offline answer diagnosis

[Audit narrative](../reports/gpu-answer-audit.md) and [recomputable data](../reports/gpu-answer-audit.json)
separate source matching, gold-ID overlap and token F1 from assistant judgments.
[Draft review](../reports/gpu-answer-review-draft.json) is not human evaluation.
The [masked packet](../reports/gpu-answer-review-packet.md) and
[blank response template](../reports/gpu-answer-human-review-template.json)
prepare independent review without claiming it occurred.

## Prepared GPU answer generation

[Proposal](gpu-generation-proposal.md), [execution guide](gpu-generation-runner.md),
[readiness](../reports/gpu-generation-readiness.json), and
[synthetic tests](../tests/unit/test_gpu_generation.py) document the pending
32-call comparison. 144 software tests pass; GPU behavior and answer quality for
this new workload remain unmeasured. No authorization or attempt exists.

## Completed GPU generator comparison

[Report](../reports/gpu-generation-development.md),
[structured results](../reports/gpu-generation-development.json) and
[authorization](../reports/gpu-generation-authorization.json) document a verified
32-call GPU run and all-eight-condition development gate pass. The descriptive
F1-gain interval includes zero. [Human review materials](../reports/gpu-generation-human-review.md)
and [blank response template](../reports/gpu-generation-human-review-template.json)
do not claim completed human labels. Candidate results remain development-only.

## Completed AI-assisted paper review of GPU answers

[Per-case review](../reports/gpu-generation-ai-review.md),
[structured judgments](../reports/gpu-generation-ai-review.json) and
[verification record](../reports/gpu-generation-ai-review-verification.json)
cover all 24 emitted answers and 16 source PDFs. Three answers are adequate,
11 partial, eight inadequate and two ambiguous under an explicit rubric. Source
hashes and original answers/citations are preserved. Six PDF pages were visually
checked for table layout and source ambiguities. No new model evaluation occurred;
this non-blinded assistant review does not constitute independent human labels.

## Prepared complete-answer comparison

[Proposal](grounded-answer-proposal.md), [runner](grounded-answer-runner.md),
[readiness](../reports/grounded-answer-readiness.json) and
[synthetic tests](../tests/unit/test_grounded_answer.py) cover a new answer contract
using fixed saved evidence and model weights. Twenty-six new tests cover strict
JSON, quote limits, reference exclusion, budgets, tampering, baseline binding,
failure/refusal separation and full-cohort reconstruction. All 170 tests pass with
PostgreSQL. Preflight is read-only; no real experiment or semantic quality result
exists for this candidate. The requested allowance remains unapproved.

## Completed complete-answer comparison

[Report](../reports/grounded-answer-development.md),
[structured results](../reports/grounded-answer-development.json),
[raw validation failures](../reports/grounded-answer-errors.md) and
[authorization](../reports/grounded-answer-authorization.json) record one completed
32-call RTX 4090 attempt. Launch verification and independent saved-result
recomputation passed. Six of eleven quality conditions pass; the candidate is not
promoted. F1 .143765, ten failures and five unanswerable answers must be reported
together. The descriptive F1-gain interval includes zero.

[Review packet](../reports/grounded-answer-review-packet.md) and
[blank human template](../reports/grounded-answer-human-review-template.json) cover
all 19 emitted answers, with exact quotations and verified PDF hashes/links. Their
roster, answers, quotes and hashes were checked against saved predictions. They
do not claim completed semantic review. Reports preserve all run/root artifact
hashes; the preparation records above remain historical. The allowance is consumed,
with 3,443 actual output tokens, 176.969 seconds and $0 external spend. No training,
retry, final-test access or deployment occurred.

## Prepared source span-ID comparison

[Proposal](span-id-answer-proposal.md), [runner](span-id-answer-runner.md) and
[readiness](../reports/span-id-answer-readiness.json) describe the deterministic
quote-assembly experiment. New contract/lifecycle tests total 24; the complete
software suite passes 194 tests with PostgreSQL and two existing warnings. Both
independent code reviews found no actionable issues. The initial database failure
and [Docker recovery](../reports/docker-startup-recovery.md) are retained separately.

Cached asset verification and tokenizer-only checks load no model weights. The
32 prompts use 484–1,142 input tokens and contain 543 source spans; body coverage,
offsets and word limits were checked on every supplied passage. The readiness
record includes source and preparation-artifact hashes. This proves preparation
and software invariants, not model quality or semantic support. No allowance or
real attempt exists; the 100-question final test remains unused.

## Completed source span-ID comparison

[Results](../reports/span-id-answer-development.md),
[structured evidence](../reports/span-id-answer-development.json) and
[authorization](../reports/span-id-answer-authorization.json) record the completed
32-call RTX 4090 attempt. Launch verification and independent saved-result
recomputation passed. F1 .214084, 30 answers and zero failures improve development
results; four unanswerable answers and citation-ID precision .428571 fail two of
eleven gates. The positive descriptive bootstrap interval is not selection-adjusted
or a fresh final result. The candidate is not promoted.

All 41 quotations were checked against source catalogs, including source offsets
through catalog reconstruction and unchanged input hashes. The
[30-answer packet](../reports/span-id-answer-review-packet.md) preserves the selected
spans, full supplied passages and verified paper links/hashes. Its
[human template](../reports/span-id-answer-human-review-template.json) is blank.
Focused assistant observations identify numerical misattribution, clipped fragments
and nonresponsive answers; no full semantic score or independent human review is
claimed. One attempt consumed 962 actual output tokens and 60.656 seconds at $0
external spend. No retry, training or final-test access occurred.

## Saved span-ID evidence diagnosis

[Narrative audit](../reports/span-id-evidence-audit.md),
[mechanical facts](../reports/span-id-evidence-audit.json) and
[assistant case review](../reports/span-id-evidence-review.json) separate gold-ID
delivery, string clipping, input sufficiency and claim support. All 50 rows are
traced; 32 supplied-evidence cases are reviewed, with 72 exact excerpts verified.
The assistant labels are non-blinded diagnostic judgments, not human acceptance.
Original-paragraph tails diagnose clipping only; prior full-paper caveats remain.

Audit revision `05d7d01`: 13 synthetic audit tests and 207 total software tests pass,
with real PostgreSQL and two existing deprecation warnings. The saved audit
recomputes exactly with `scripts/audit_span_id_evidence.py --verify`; the review
verifier checks source/reviewer hashes, roster, answers, excerpts and counts.
Negative checks reject fabricated excerpts, duplicate cases, altered counts and
changed source hashes. No model run, final-test access, rescore or promotion occurred.

## Prepared intact-paragraph comparison

[Proposal](intact-passage-proposal.md), [execution guide](intact-passage-runner.md)
and [readiness](../reports/intact-passage-readiness.json) pin the complete-paragraph
input intervention. Preparation revision `5f7701c`: 35 new synthetic checks and all
242 software tests pass with PostgreSQL and two existing warnings. Read-only
preflight verifies predecessor/source/model/runtime artifacts. Exact-message
tokenization in the isolated GPU runtime, on CPU and without weights, yields
484–1,245 input tokens across 32 prompts and 582 spans. All fit 2,048 tokens.

Code review found no blocking adapter bug. Its requested F1 boundary cases are
persisted; the separate tokenizer requirement is documented and completed for the
exact snapshot. A prior auxiliary test invocation without UTF-8 mode failed an
existing GBK fixture read; rerunning in UTF-8 mode passed without frozen-source
changes. No real evaluation or training occurred. One 32-call/20-minute/$0 attempt
needs new approval. The final test remains unused.

## Completed intact-paragraph comparison

[Results](../reports/intact-passage-development.md),
[structured evidence](../reports/intact-passage-development.json) and
[authorization](../reports/intact-passage-authorization.json) preserve the single
32-call RTX 4090 attempt. Launch and separate read-only reconstruction passed.
All 18 threshold refusals and scoring labels are unchanged; restored bodies match
original development units. All 14 unchanged inputs reproduce previous raw output.

F1 .240186 exceeds .214084, but six unanswerable answers, one invalid response and
citation-ID precision .400000 fail three of twelve conditions. The descriptive
paired-family gain interval [-.016220, .094526] includes zero. The
[failure report](../reports/intact-passage-errors.md) preserves the four-span output
without repair. The [31-answer packet](../reports/intact-passage-review-packet.md)
and [blank human template](../reports/intact-passage-human-review-template.json)
include exact quotes, full supplied passages and verified local paper links.
All 41 accepted quotes match source catalogs; exact matching is not entailment.

The run used 1,020 actual tokens and 63.547 worker seconds at $0 external spend.
The allowance is consumed. No new software behavior changed, so preparation's
242 tests were not rerun for execution/reporting. No training, retry, deployment
or final-test access occurred. Phase 4 and independent human acceptance remain open.
