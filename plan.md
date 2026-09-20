# EvidenceBench — implementation plan

**Goal:** Build a reproducible retrieval and reranking system that demonstrates data preparation, model training, evaluation, and software delivery for U.S. MLE internships.

**Architecture:** A versioned public document corpus feeds lexical and dense retrieval, a cross-encoder reranker, and a fixed grounded-answer pipeline. Offline evaluation and FastAPI serving share the same pipeline. A bounded agent is a separate extension for AI software engineering applications.

**Tech stack:** Python, PyTorch, Transformers, sentence-transformers, BM25, PostgreSQL/pgvector, FastAPI, Docker, pytest, and local MLflow. LoRA, LangGraph, visual models, and additional monitoring services are conditional.

**Research basis:** [September 18, 2026 market review](research/2026-09-18-job-market/market-review.md) and [200 source-linked postings](research/2026-09-18-job-market/job-sample-200.md).

**Status:** Experimental local implementation and reranker evaluation verified. QASPER supplies upstream human labels. The requested [paper-based AI review](docs/claim-review.md) is complete for all nine emitted answers: two correct, four incorrect and three ambiguous. Generated-answer quality remains weak; independent human semantic review remains unperformed. See [execution status](docs/status.md) and [measured results](reports/final-evaluation.md).
**Primary target:** MLE internship, particularly applied ML, search/ranking, and NLP/LLM systems.
**Secondary target:** AI software engineering internship or graduate role.
**Schedule:** Eight focused weeks, or roughly 10–12 part-time weeks as a planning estimate. The optional extension uses remaining time within that budget.
**Portfolio claim:** An evaluated retrieval/reranking system whose data, trained model, failure analysis, and serving trade-offs can be inspected and reproduced.

For implementation, work through the phases sequentially using the executing-plans workflow. This document does not require parallel agents or automatically trigger implementation.

## 1. Why this project

The research sample contains 100 internships and 100 full-time U.S. postings observed within the previous month, including 50 explicitly flagged reposts. Python appeared in 81 internship descriptions, evaluation/experimentation in 74, serving/deployment in 55, PyTorch in 46, retrieval/RAG/ranking in 34, and agents/tool use in 32. Agents appeared in 50 full-time descriptions. LoRA/PEFT appeared in only 4 of the 200 descriptions.

These are mentions across responsibilities and required/preferred qualifications, not universal hiring requirements. The sample is a targeted convenience sample; 49 records are from TikTok/ByteDance. The review includes a sensitivity check excluding that group. Do not present these results as representative market shares or proof that this project increases hiring probability.

The résumé already demonstrates backend delivery, testing, cloud/infrastructure work, and PyTorch medical-imaging research. EvidenceBench should add clear ownership of an ML problem: constructing useful data, selecting metrics, training a component, analyzing errors, and deploying the justified configuration.

This is a search/NLP specialization. For computer-vision roles, use the existing OCT research as complementary evidence. PDF extraction alone does not demonstrate visual-model development.

## 2. Required outcomes

- A public corpus with provenance, document-family splits, stable identifiers, and reproducible processing.
- Separate training data and human-reviewed development/test evaluation sets.
- BM25, untuned dense, hybrid, and untuned cross-encoder baselines.
- One reproducible trained reranker, a training-data learning curve, and a hard-negative ablation.
- Paired evaluation of quality, failures, and latency. Positive training gains are not a completion requirement.
- Grounded answers with source-page citations and a measured refusal policy.
- A containerized API running on one documented deployment target, with version metadata, structured logs, and reliability checks.
- Dataset/model cards, an experiment report, and a short demonstration linked to raw results.

The trained model need not be the deployed model. If an untuned model wins under the predeclared development selection criteria, deploy it and explain the unsuccessful adaptation experiment honestly.

## 3. Scope and priority

### Required MLE core

- One coherent domain of public, text-native technical PDFs.
- Text extraction with page/section provenance and coordinates where available.
- Deterministic normalization, chunking, validation, and versioning.
- Training labels, hard negatives, reviewed evaluation labels, and explicit scoring rules.
- Retrieval baselines, hybrid fusion, and untuned/trained cross-encoder comparisons.
- A fixed retrieval → rerank → answer → citation-validation pipeline.
- One deployment, a lightweight comparison report or API demo, and reproducibility artifacts.

### Optional AI SWE extension

After the core is deployable and development evaluation is stable, add one bounded tool-using workflow and compare it against the fixed pipeline. Prioritize this extension for AI SWE applications. It is optional for the MLE core and must not displace model/data work or final validation.

### Deferred unless a measured failure justifies them

- OCR, figure extraction, visual embeddings, visual-language models, and specialized table parsing.
- LoRA/PEFT, generator fine-tuning, embedding-model training, and multiple vector stores.
- LangGraph, multiple agents, workflow UIs, and autonomous research behavior.
- MinIO/S3 artifact services, hosted registries, Kubernetes, distributed serving, and autoscaling.
- OpenTelemetry/Prometheus/Grafana services and a custom React application.

Default to one trainable component, one database, one generator, and one deployment target. Do not add a technology merely to mention it on the résumé.

## 4. User stories

1. Rebuild a dataset/index from a manifest and verify its fingerprint.
2. Compare baselines and candidates on development data without consulting final test results.
3. Reproduce training and inspect data, checkpoints, learning curves, and ablations.
4. Inspect a failed query, relevant evidence, rankings, answer, and failure label.
5. Query the deployed system and receive citations, status, versions, and stage latency.
6. Recalculate the final report from saved per-example results.
7. If the extension is enabled, compare the agent with the fixed pipeline under matched evidence and resource limits.

## 5. Architecture and interfaces

```mermaid
flowchart LR
    MAN[Public manifest] --> ING[Extract, validate, chunk]
    ING --> ART[Local versioned artifacts]
    ING --> IDX[BM25 and dense index builder]
    IDX --> PG[(PostgreSQL and pgvector)]
    Q[Query] --> RET[Retrieve and fuse]
    PG --> RET
    RET --> RER[Selected cross-encoder]
    RER --> GEN[Fixed grounded-answer pipeline]
    GEN --> CHECK[Citation validation and refusal policy]
    CHECK --> API[FastAPI response]
    TRAIN[Training labels] --> FIT[Train and ablate]
    FIT --> RER
    EVAL[Offline evaluator] --> RET
    EVAL --> GEN
    EVAL --> RUN[MLflow and per-example reports]
    FIT --> RUN
    API --> LOG[Structured logs and latency report]
    RET -. optional .-> AG[Bounded agent comparison]
    AG -. same generation and validation .-> GEN
```

Evaluation and serving import the same retrieval, reranking, evidence-packing, and validation functions. Notebooks must not contain a separate production implementation.

| Contract | Required fields |
|---|---|
| ContentUnit | Document/family/version IDs, page, element ID, text, section, optional bounding box, source checksum |
| QueryExample | Query ID/text, split, query family, graded relevant element IDs, answerability, answer criteria, supporting evidence IDs, label provenance |
| RankedEvidence | Element ID, retrieval/reranker scores, rank, source document/page |
| QueryResult | Request ID, answer/status, citations, ranked evidence, version IDs, stage timings, validation status |
| RunManifest | Run ID, code revision, config hash, data/index fingerprints, model/tokenizer revisions, seed, hardware, elapsed time, artifact paths |

Implement typed interfaces: `retrieve(query, filters, k)` and `rerank(query, candidates, k)` return ordered RankedEvidence records; `answer(query, evidence)` returns a QueryResult. Scoring consumes QueryExample records and saved predictions rather than silently rerunning models.

## 6. Toolchain and resource decisions

Pin compatible package versions in `uv.lock` after verifying the actual environment. Pin model/tokenizer revisions separately. A mutable model name alone is insufficient for a published result.

| Area | Core choice | Boundary |
|---|---|---|
| Environment | Python, uv, Ruff, pytest; type checks on shared contracts | Select a supported Python version compatible with measured hardware during setup |
| Data | Pydantic, Pandas/PyArrow, Parquet/JSONL | Another validation library is optional |
| Extraction | One PDF text/geometry extractor, chosen after license/extraction checks | No required OCR or OpenCV |
| Retrieval | BM25, one sentence-transformer, reciprocal-rank fusion | One primary chunking scheme and one targeted alternative |
| Reranking | Small PyTorch/Transformers cross-encoder | Full fine-tuning if it fits; PEFT requires a documented reason |
| Storage | PostgreSQL/pgvector and local artifact directories | No second vector store or object-store service |
| Tracking | Local MLflow, immutable run manifests and result files | No remote tracking or hosted registry required |
| Generation | One small pinned local instruction model | Retrieval experiments remain independent of generator quality |
| Serving | FastAPI, Pydantic, Docker Compose | One app and database; read-only serving artifacts |
| Telemetry | Structured JSON logs and benchmark reports | Add monitoring services only to answer a concrete question |
| Demo | API documentation and generated comparison/error reports | Small Streamlit UI only if inspection otherwise suffers |
| Optional agent | Typed Python workflow | LangGraph only if state management warrants it |

At kickoff, measure CPU/GPU memory and pilot throughput. Record a compute/time budget, maximum run count, latency/memory limits, and any approved monetary budget in `configs/budget.yaml` before full training. Paid services are not assumed. Reduce model/context/batch size before adding cloud infrastructure. If local generation remains infeasible, document a capped hosted-model substitution, its exact model ID, cost, and reproducibility limits before use.

## 7. Planned file structure

Create files when their phase needs them; this map does not imply application code exists.

```text
README.md
pyproject.toml
uv.lock
Dockerfile
compose.yaml
configs/
  budget.yaml
  corpus.yaml
  retrieval.yaml
  training.yaml
  generation.yaml
  evaluation.yaml
  release.yaml
data/
  manifests/
  labels/
  README.md
src/evidencebench/
  schemas.py
  cli.py
  ingestion.py
  chunking.py
  indexing.py
  retrieval.py
  reranking.py
  training.py
  generation.py
  citations.py
  tracking.py
  evaluation/
    metrics.py
    runner.py
    reports.py
  serving/
    app.py
    pipeline.py
tests/
  unit/
  integration/
  fixtures/
  load/
reports/
  dataset-card.md
  model-card.md
  evaluation-report.md
  error-taxonomy.md
  evidence-index.md
  runbook.md
artifacts/                 # ignored generated data; immutable run directories
research/                  # existing market evidence, excluded from corpus
.github/workflows/ci.yml
```

The optional extension adds `src/evidencebench/agent.py`, `configs/agent.yaml`, and agent task fixtures. Split modules when they acquire multiple responsibilities; avoid scaffolding unnecessary subsystems.

## 8. Corpus, labels, and leakage controls

### Corpus and retrieval protocol

Choose one collection of public technical manuals or developer documentation with enough independent document families to support train/dev/test separation. Prefer text-native PDFs and a domain whose answers can be reviewed accurately.

The manifest records URL, usage/license conditions, checksum, retrieval date, document/version/family ID, page count, MIME type, and split assignment. Commit only redistributable sources; otherwise provide fetch instructions. Résumé content, job-market descriptions, private documents, and application records are not training data.

Group versions and near-duplicate documents before assigning roughly 60/20/20 percent of document families to train/dev/test. Adjust counts for a small corpus before labeling and record the assignments. Development/test retrieval searches the full frozen corpus, including distractors, but training and hard-negative mining use training-family content only. This measures retrieval over unseen families without fitting on their content or labels. If the corpus cannot support that claim, change the protocol before experimenting.

### Evaluation labels: separate from training

- Plan for **150–250 human-reviewed development/test queries combined**, approximately one-third development and two-thirds final test. This is a starting budget, not a statistical sufficiency guarantee.
- Include approximately 20–25% unanswerable or insufficient-evidence cases in each evaluation split. Report this deliberately constructed balance.
- Use a written relevance scale: 0 = irrelevant, 1 = useful context, 2 = directly supports an answer. Record answer criteria, acceptable citations, and ambiguity decisions.
- Spread questions across document families and query types; report family counts as well as query counts.
- Review labels without seeing model predictions. Blindly re-review a subset after a delay; do not claim inter-annotator agreement from a single reviewer.
- If only 80 reviewed evaluation queries are feasible, release an explicitly exploratory pilot with uncertainty. Do not describe it as equivalent to the planned full evaluation.

### Training data and learning curve

- Build a separate training-query set. Do not use the 150–250 evaluation queries as the entire train/dev/test dataset.
- Initial target: at least 200 distinct training queries with supported positives and sampled negatives. Report query count and query-document pair count separately.
- Compare nested subsets of 50, 100, and 200 training queries against the same development set. Expand only if the learning curve and budget justify it.
- Synthetic training queries are allowed with generator/prompt provenance and a reviewed sample. Record audit size, observed errors, and corrections. Evaluation labels require human review regardless of origin.
- Mine negatives using training-only BM25/dense retrieval. Remove known positives, review likely false negatives, and save sampler seed and pool version.
- If useful training data is inadequate, reduce corpus scope or invest in labeling before adding agents or visual features. An incomplete adaptation experiment does not satisfy the full MLE definition of done.

### Test isolation

- Freeze labels, query IDs, family assignments, and scoring rules before selection.
- Development data owns model, chunking, fusion, prompt, threshold, and deployment choices.
- CI uses independent fixtures/development examples, not repeated final-test metrics.
- Run final test evaluation after candidate configurations and scoring code are frozen; evaluate predeclared comparisons together.
- Inspect test failures after recording results. Subsequent tuning makes that set development evidence; obtain a fresh holdout before claiming a new unbiased test result.

## 9. Deterministic ingestion

1. Validate the manifest, MIME types, and source checksums.
2. Extract text, sections, pages, and available coordinates.
3. Normalize whitespace, Unicode, headers/footers, and hyphenation using versioned rules.
4. Create stable document/element/chunk IDs and source-page mappings.
5. Produce the primary chunking view and validation report.
6. Write Parquet records and a fingerprint covering sources, extractor/config, and output.

Check repeated-run fingerprints, missing text, empty pages, duplicate IDs, invalid coordinates, and broken citations. Inspect representative pages from each extraction pattern. Flag or exclude scanned/problematic PDFs rather than silently producing empty evidence.

Render pages on demand for inspection. Reliably extracted tables may be retained as text with provenance and stated limits. OCR, figure interpretation, and visual retrieval require a separate extension with a text-only control and task-specific labels.

## 10. Retrieval and model adaptation

### Baseline ladder

Implement BM25 → untuned dense → reciprocal-rank fusion → hybrid plus untuned cross-encoder → hybrid plus trained cross-encoder. Keep the corpus, query set, and scoring code constant. Metadata filters represent explicit user constraints; never supply hidden gold-document filters during evaluation.

Record Recall@5/10/20, nDCG@10, MRR, index size/build time, and stage latency. Use nDCG@10 as the primary answerable-query ranking metric. Report unanswerable queries separately.

### Training experiment

- Preserve the untuned cross-encoder baseline before training.
- Use full fine-tuning when the architecture/hardware permit it. Use LoRA/PEFT only with documented compatibility, memory savings, parameter count, and trade-offs. Generator tuning is outside core scope.
- Save data fingerprints, query/pair counts, negative sampling, model/tokenizer revision, seed, optimizer/schedule, checkpoint hash, and compute record.
- Run the nested training-query learning curve and a matched random-negative versus hard-negative ablation; keep other settings fixed for the ablation.
- Report loss curves, failed runs, overfitting, and development slices. Repeat shortlisted configurations with three seeds if the budget permits; otherwise disclose single-seed uncertainty.
- Select by development nDCG@10 subject to predeclared latency/memory limits and answerability/slice checks. Prefer the simpler or cheaper configuration when differences are inconclusive.

A well-diagnosed negative result is useful evidence. Do not force positive improvement or switch headline metrics after seeing results.

## 11. Grounded answers and optional agent

### Core fixed pipeline

Retrieve, rerank, pack evidence with stable IDs, generate structured output, validate citations, and answer or refuse. Calibrate evidence-sufficiency thresholds on development data only.

A valid citation ID establishes provenance, not factual support. Evaluate support against human-reviewed claim criteria. A model-assisted judge is supplementary; disclose its model, rubric, and disagreement with human review.

Reject invalid citation references. Permit at most one bounded output-format repair, then return a structured failure/refusal. Configure retrieval, context, token, and timeout limits. Treat retrieved text as data, never as instructions that may change system policy or tools.

### Optional bounded workflow

Use the same corpus, generator, citation checks, and evaluation protocol as the fixed control. Permit one query reformulation and an optional calculator. Expose only typed retrieval, evidence-opening, and restricted numeric-expression tools. Do not expose arbitrary code, shell, filesystem browsing, or unrestricted network access.

Default limits: one reformulation, four tool calls, and one format repair, plus configured wall-clock/token ceilings. Trace validated tool calls, outcomes, and concise state summaries; do not expose hidden reasoning.

Create development and held-out task scenarios before agent tuning. Compare completion, invalid calls, refusal, call counts, latency, and cost. Include a matched-budget comparison so extra compute is not mistaken for an architectural gain. Use deterministic tool fixtures for contracts and repeated real-model runs for behavioral variance.

LangGraph is optional. Include the agent in the demo only if development results justify the complexity; a negative comparison can remain a labeled experiment.

## 12. Evaluation and failure analysis

| Area | Required evidence |
|---|---|
| Retrieval | Recall@5/10/20, nDCG@10, MRR, per-query rankings/judgments |
| Answers | Correctness against written criteria; unsupported-claim rate |
| Citations | Fraction of cited claims supported; coverage of claims requiring evidence; invalid references |
| Refusal | Answerability precision/recall; answers and abstentions separated |
| Serving | Warm/cold p50/p95 latency, throughput, errors/timeouts, peak memory, hardware and workload |
| Optional agent | Completion, tool validity/selection, refusal, exhausted budgets, variance, latency/cost versus control |

Define denominators and missing-output treatment before comparisons. Include timeouts/failures in end-to-end reporting. Report response coverage alongside correctness so excessive refusals cannot inflate the apparent quality.

Use paired comparisons on identical queries. Bootstrap at document-family level when questions share sources; disclose small family counts and uncertainty. Preserve bootstrap seeds and per-example outputs. Automated judges are not ground truth.

Review at least 30 unique development queries that fail in a baseline or candidate. If fewer than 30 exist, review all and report the actual count. Categories: extraction, chunking, lexical/dense miss, fusion, reranking regression, false negatives in labels, insufficient context, unsupported claim, incorrect citation, false refusal, missing refusal, and annotation ambiguity. Add tool/calculation categories only for the extension.

## 13. Artifacts and release selection

Use immutable `artifacts/runs/<run_id>/` directories containing the run manifest, configuration, predictions, aggregates, plots, failure review, and checkpoint references. MLflow provides comparison and links; exported files keep reproduction possible without a tracking UI.

PostgreSQL stores corpus/index metadata and embeddings. Parquet/JSONL store processed data and labels. Local files store source documents, checkpoints, and reports. Large files stay outside Git with checksums and reconstruction/download instructions.

`configs/release.yaml` pins checkpoint/model, index/data fingerprints, prompts, thresholds, and image version. Selection uses development evidence. Final evaluation reports quality and checks correctness; it does not select a different winner from test scores. Critical failures block release and require a documented protocol reset before new test claims.

## 14. API and inspection

| Route | Responsibility |
|---|---|
| POST /api/v1/query | Fixed pipeline; answer/refusal, citations, versions, stage timings |
| POST /api/v1/retrieve | Ranked candidates for inspection |
| GET /api/v1/models/current | Release/model/index/data/prompt identifiers |
| GET /health/live | Process health |
| GET /health/ready | Database, index, model readiness |

Batch evaluation and release selection are CLI operations. Do not expose labels, training, reload, or arbitrary configuration changes through a public API. Use a curated corpus and bounded input; document upload is deferred.

Responses include request ID, status/reason, cited document/page/source references, available coordinates, evidence scores, versions, and timings. Generated inspection reports may show development labels. Keep test labels out of serving and pre-release demo selection.

## 15. Deployment and reliability

- Build a reproducible Compose app/database stack with versioned artifact mounts.
- Deploy one immutable image on one documented host. A local/campus host is acceptable if hardware/cost prevents public hosting; provide a recording and reproduction instructions without claiming public access.
- Log request/stage timings, errors, empty retrieval, refusals, citation validation failures, token usage when available, and versions.
- Generate benchmark reports from logs; dashboards are optional.
- Distinguish proxy signals from labeled quality. Do not claim drift detection from a static demo.
- Bound requests and handle database failure, corrupt/missing index, invalid input, model timeouts, and generation failure with explicit status codes.
- Roll back by restarting with the previous image and release manifest; hot reload and registry services are unnecessary.

Record host specifications, concurrency, query/context lengths, warm-up, cache state, duration, success/error counts, and peak memory. Execution time and monetary spending are different; do not describe guessed cloud costs as measured costs.

## 16. Verification strategy

| Layer | Meaningful checks |
|---|---|
| Unit/contracts | IDs, deduplication/splits, fusion, metric denominators, citation references, schemas |
| Data fixtures | Representative redistributable PDF extraction/page mapping; corrupt/scanned input |
| Integration | Index build/load, pgvector, checkpoint loading, shared pipeline, API contract |
| ML | Untuned/trained comparison, learning curve, negative-sampling ablation, loss behavior, affordable seed repeats |
| Reliability | Oversized input, missing dependencies, timeouts, malformed output, invalid citations |
| Reproduction | Clean fixture corpus/index build and reference report within stated tolerance |
| Optional agent | Schemas, limits, document-instruction resistance, invalid tool output, refusal, budget exhaustion |

Fixtures are independent of the final test set. Test behavior and failure modes rather than incidental implementation details. Full GPU experiments are separate from ordinary CI.

## 17. CI and release workflow

Pull requests run formatting/lint, contract/type checks, unit/data tests, a small PostgreSQL integration test, fixture-model API smoke tests, and a container build. Use mocked generation for protocol tests and a recorded real-model smoke run before release. Routine CI needs no GPU training.

Experiments take versioned configs, data/index versions, model revisions, seeds, and budgets; they produce immutable artifacts and MLflow records. A release takes the development-selected manifest, runs frozen final evaluation, builds/deploys the image, and records health/query/refusal smoke results. Exercise and document rollback.

## 18. Implementation phases

Commands below describe the phase contract. Implemented commands and current config paths are documented in the README/runbook; historical `configs/evaluation.yaml` examples use `configs/qasper-evaluation.yaml` for the current benchmark. Each phase has owned files, concrete work, and an acceptance gate. Make incremental changes and record a reviewable checkpoint after each accepted phase.

### Phase 1 — corpus and reproducible data (week 1)

**Files:** Environment/lockfile; `configs/budget.yaml`, `configs/corpus.yaml`; `data/manifests/`; `src/evidencebench/{schemas,cli,ingestion,chunking}.py`; ingestion fixtures/tests; dataset card.

- [x] Select/license-check the corpus, pilot hardware/extraction, and record limits.
- [x] Define shared schemas and source/family identifiers.
- [x] Add checks for repeatability, empty text, duplicate sources, and page mapping; confirm deliberately corrupt inputs are detected.
- [x] Implement extraction, normalization, fingerprints, and source inspection.
- [x] Assign families to splits and check near-duplicate/version grouping.

**Check:** Run `uv run evidencebench build --config configs/corpus.yaml` twice into clean output directories. Fingerprints/IDs match and sampled elements resolve to their source pages. Reject a corpus requiring substantial OCR rescue.

### Phase 2 — labels and baselines (week 2)

**Files:** `data/labels/`, labeling guide; retrieval/evaluation configs; indexing, retrieval, tracking, evaluation modules; metric/retrieval tests; error taxonomy.

- [x] Write scoring rules and separate training/evaluation query pools.
- [x] Review/freeze evaluation labels and audit cross-split duplicates.
- [x] Verify metrics on hand-calculated cases, including ties, empty results, and unanswerable queries.
- [x] Implement BM25, dense retrieval, fusion, and per-example recording.
- [x] Run development baselines and begin failure review without final-test outcomes.

**Check:** `uv run evidencebench evaluate --config configs/evaluation.yaml --split dev --suite retrieval-baselines`. Recalculate aggregates from saved predictions; verify family disjointness and exact query/pair counts.

### Phase 3 — adaptation and analysis (weeks 3–4)

**Files:** Training config; training/reranking modules; training-data/checkpoint tests; model card and evaluation report.

- [x] Establish the untuned cross-encoder baseline.
- [x] Verify positive/negative construction and reject non-training-family candidates.
- [x] Run an overfit/debug pilot to check gradients, tokenizer compatibility, loss, and checkpoint reload.
- [x] Train the nested query subsets and matched negative-sampling ablation within budget.
- [x] Compare development quality, latency, slices, and failures.
- [x] Select using predeclared criteria and repeat seeds where affordable.

**Checks:** `uv run evidencebench train --config configs/training.yaml`; `uv run evidencebench evaluate --config configs/evaluation.yaml --split dev --suite rerankers`. Connect training data, curves, checkpoints, per-query changes, and latency. LoRA use and positive lift are not acceptance gates.

### Phase 4 — grounded answers (week 5)

**Files:** Generation config; generation/citation modules; citation/answer tests; evaluation report.

- [x] Implement evidence packing, structured output, citations, and development-calibrated refusal.
- [x] Test missing evidence, invalid IDs, malformed output, bounded repair, and instructions embedded in documents.
- [ ] Evaluate answer/citation support, unsupported claims, and refusal errors.
- [x] Produce an inspection report linking rankings and answers to pages.

**Check:** `uv run evidencebench evaluate --config configs/evaluation.yaml --split dev --suite answers`. Valid IDs alone cannot count as supported claims. Use development examples for demonstrations.

### Phase 5 — service and deployment (week 6)

**Files:** Serving modules, Dockerfile, Compose, release config, CI, API/load tests, runbook.

- [x] Implement bounded query/retrieval/health/version endpoints using the shared pipeline.
- [x] Add startup checks, timeouts, structured logs, and dependency-failure responses.
- [x] Deploy the development-selected configuration to one host.
- [x] Benchmark warm/cold behavior and concurrency; exercise rollback.
- [x] Verify documented commands in a fresh environment.

**Checks:** `uv run pytest tests/unit tests/integration`; `docker compose up --build`; recorded health, answer, refusal, invalid-input, and dependency-failure requests.

**Core gate:** Data, adaptation experiments, development reports, and service work together. If the gate fails, finish the core in week 7 and drop the agent extension.

### Phase 6 — choose one focus (week 7)

**Default MLE path:** Address the largest measured data/model weakness, complete uncertainty analysis, and reproduce the shortlisted run. Update existing modules/tests/reports; add no new subsystem.

**Implemented focus:** controlled hard-negative training, exact cached mining, three-seed sensitivity, 36-query failure analysis and cross-environment ranking parity. The answer-format defect was fixed before test freeze. The agent remains deferred. Checkboxes below belong only to the unselected optional path.

**Optional AI SWE path:** Add `src/evidencebench/agent.py`, `configs/agent.yaml`, agent tests, `data/labels/agent-dev.jsonl`, `data/labels/agent-test.jsonl`, and `reports/agent-comparison.md`.

- [ ] Freeze task rules, budgets, and held-out scenarios before tuning.
- [ ] Implement the bounded workflow and deterministic tool/failure tests.
- [ ] Compare with the fixed pipeline on development tasks, including matched budgets and repeated real-model runs.
- [ ] Decide demo inclusion from development results.

**Check if selected:** `uv run evidencebench evaluate --config configs/evaluation.yaml --split dev --suite agent`. Neither path may tune from final-test results.

### Phase 7 — final evaluation and portfolio release (week 8)

**Files:** Release config, final cards/reports, evidence index, runbook, README, optional agent comparison.

- [x] Freeze candidates, scoring, and release selection before final evaluation.
- [x] Run predeclared test comparisons, record all outcomes, then review test failures without tuning on them.
- [x] Reproduce the main comparison cleanly and verify the deployed version matches its manifest.
- [x] Complete limitations, baseline/candidate figures, and a short demo.
- [x] Link each prospective résumé claim to its run, data, metric definition, and limitation.

**Checks:** `uv run evidencebench evaluate --config configs/evaluation.yaml --split test --suite release`; inspect the actual emitted run with `uv run evidencebench inspect --run <recorded-run-id>`. Aggregates must be recalculable from predictions. Document how any post-test repair affects holdout validity.

## 19. Portfolio demonstration

Use a five-minute narrative:

1. Define the task; show corpus, query/pair counts, and family-level split policy.
2. Compare baseline/selected rankings on development examples, including a failure.
3. Show the learning curve, controlled ablation, final held-out quality, and serving trade-offs.
4. Ask answerable/unanswerable questions and open source citations.
5. Trace the release to its run manifest and show containerized API health/version information.

For AI SWE applications, add a short fixed-versus-agent comparison only when completed. Keep its metrics and resource costs separate. Do not call an offline benchmark a production A/B test or a caption parser a trained visual model.

The demo passes when the product works, ML reasoning is clear, results are reproducible, and limitations are visible.

## 20. Definition of done

### MLE core

Unchecked criteria are not waived: automated answer/reference agreement does not replace human claim-support judgments. The release is explicitly experimental. Remote CI has not run; checked CI fixtures refer to local equivalents.

- [x] Corpus provenance, usage conditions, and family splits are documented.
- [x] Repeated ingestion/index builds and page citations are verified.
- [x] Training queries/pairs are separate from reviewed development/test labels.
- [x] Baselines precede adaptation and comparisons share one protocol.
- [x] Trained reranker, learning curve, and controlled negative-sampling ablation are reproducible.
- [x] Development selection and untouched final-test reporting are documented.
- [x] Quality, latency, memory, failures, and uncertainty are honestly reported.
- [x] Development failures are reviewed under the documented count rule.
- [ ] Answers have measured support, citation, and refusal behavior.
- [x] One containerized deployment handles tested failures and exposes health/versions.
- [x] CI fixtures, clean-environment reproduction, and rollback checks pass.
- [x] Cards, reports, evidence index, README, and demo are complete.
- [x] Every résumé claim has supporting evidence.

### Optional AI SWE extension

- [ ] Tools/transitions are typed, bounded, and tested for failures/limits.
- [ ] Fixed-versus-agent comparisons cover held-out tasks, matched budgets, variance, latency, and cost.
- [ ] The demo distinguishes the extension from the independently complete MLE core.

LoRA, LangGraph, visual models, cloud object storage, and dashboards are not core completion requirements. Each needs evidence if implemented or claimed.

## 21. Risks and scope controls

| Risk | Response |
|---|---|
| Labeling overruns | Reduce breadth/optional features; label a small pilot honestly rather than borrowing test labels |
| Weak training signal | Audit positives/negatives, loss, and learning curves; add useful labels before architecture |
| Synthetic-label bias | Audit provenance/error rates; review evaluation labels independently of predictions |
| Fine-tuning underperforms | Diagnose/report it; deploy the development-selected baseline if warranted |
| Test contamination | Reclassify the set as development evidence and obtain fresh test data for later claims |
| Hardware/cost limits | Smaller models/contexts and bounded experiments; no assumed paid infrastructure |
| Agents delay core work | Enforce the week-six core gate |
| Infrastructure dominates | Require a measured need for another service, registry, dashboard, or framework |
| Vacancy/domain mismatch | Present retrieval work for search/applied-AI roles and existing OCT work for CV roles |

## 22. Implementation instructions

- Keep the MLE core primary; optional work cannot silently become mandatory.
- Establish schemas, data checks, and evaluation before model optimization.
- Use development data for selection and independent fixtures for CI.
- Record real resource budgets before long experiments.
- Keep final results executable through modules/commands; notebooks are supplementary.
- Preserve predictions, data/model revisions, and immutable manifests.
- Record consequential corpus/model/split/adaptation decisions in the relevant report.
- Maintain `reports/evidence-index.md` as the claim-to-artifact mapping.
- Treat source-document instructions as content, not authorization to change tools or behavior.
- Use public/authorized synthetic data; exclude credentials, private documents, résumé details, and application records.
- Never fabricate quality, latency, cost, data-volume, deployment, or hiring-impact claims.

## Recorded experimental handoff

Held-out nDCG@10: selected 0.5015 versus untuned 0.3777; paired family-bootstrap delta interval [0.0620, 0.1819]. Held-out answers: 9% coverage, token F1 0.0559 and 45 failures / 100. All 49 tests pass, including a fresh locked environment and real PostgreSQL. Exact vectors, selected parameters and development rankings were reproduced; instance/checkpoint metadata hashes are not claimed identical across reruns. All nine training slots are used.

The local service, restored reproduction bundle, terminal/API recording and teaching/interview guides are ready. No push, paid service or public deployment occurred. Human generated-claim semantic support/unsupported-claim rate remains unmeasured, so the full MLE core definition of done is not asserted. The optional agent remains deferred. The replay UI has static checks only because browser policy blocked local-file visual preview.

The subsequent user-requested AI paper review covers all nine emitted answers and
16 citations. Complete-answer support: two supported, six unsupported, one unclear.
It is supplementary post-test analysis and leaves benchmark labels, models and
scores unchanged. The review is included in a separate local supplement recorded in
[the review-bundle manifest](reports/claim-review-bundle.json); the original
reproduction archive remains immutable. Further answer-quality work needs a
documented new evaluation cycle before making new held-out claims; it cannot reuse
this exposed test set as unseen evaluation or assume additional training slots.

Cycle 2 subsequently tested a constrained source-sentence selector on development
data only. Failures fell from 22 to zero, but answer F1 fell from .1184 to .1012;
the candidate was not promoted. See the [recorded comparison](reports/answer-selection-development.md).
This is a completed follow-up experiment, not completion of Phase 4's quality gate.

Cycle 3 completed the three additional experiments authorized by the user. Short
source-span constraints improved development F1 to .1533 with zero failures; a
focused-question variant scored .1372 and refused all 12 unanswerable development
queries. Both reduced citation-ID precision. [All outcomes](reports/answer-spans-development.md)
are retained; constrained spans are preferred by the predeclared F1-first rule,
but neither variant is deployed. Fresh held-out and semantic evaluation remain
necessary before accepting a new release. No new training or paid services occurred.

Offline follow-up found no gold passage in packed context for 12 of constrained's
18 citation mismatches. [The audit](reports/citation-diagnostics-development.md)
does not establish semantic correctness. [Fresh evaluation preparation](docs/fresh-evaluation-protocol.md)
reserves 60 validation and 120 test families after excluding 333 known previously
used/attempted/cached families. Corpus construction and evaluation remain unrun;
the original experiment budgets and release artifacts are unchanged.

The reserved fresh dataset was subsequently constructed and verified: 50 validation
and 100 final-test questions, 105 paper families and 3,161 aligned paragraphs. A
cache-only rebuild reproduced the retained records and label bytes; known prior
family overlap and high-Jaccard duplicate flags are zero. See the
[dataset card](reports/fresh-dataset.md). No model evaluation, embeddings, training
or deployment occurred. A [bounded validation proposal](docs/fresh-validation-proposal.md)
is prepared for a new allowance; final test and human semantic review remain pending.

The fresh-validation comparison runner is subsequently implemented and tested with
synthetic models, with read-only preflight on the actual artifacts/caches. It keeps
one shared retrieval pass, durable compute caps, a single attempt and an external
watchdog, and verifies saved results without inference. [Execution instructions](docs/fresh-validation-runner.md)
are ready. No fresh model run has occurred; the new allowance remains pending.

The user subsequently approved and completed the single fresh-validation comparison.
[Verified results](reports/fresh-validation.md): constrained F1 .0754 versus control
.0120, zero versus 21 failures, but unanswerable answers increase from 3/12 to 6/12
and citation-ID precision declines from .364 to .321. The predeclared gate fails;
the candidate is not promoted. One attempt consumed 86 generation calls and 5.97
minutes of local CPU time at $0 external spend. The fresh final test remains unused.
Evidence recall drops from .9737 among 50 candidates to .4934 in the reranked top
three and .3487 after packing. Future evidence-selection and abstention work needs
its own design and allowance; this diagnosis is not permission to retune or rerun.
Independent human generated-claim review and Phase 4 acceptance remain outstanding.

The subsequent [offline selection audit](reports/fresh-selection-audit.md) isolates
the remaining issues using saved outputs. Reranking improves top-three gold recall
from .1645 to .4934; its maximum score has answerability AUC .5702. Exhaustive stricter
cutoff replay has one post-hoc gate-passing state out of 29, retaining only eight
answers. It is diagnostic evidence, not a revised selection or permission to promote.
The next experimental direction is to measure evidence sufficiency separately from
relevance, with packing changes tested separately. This requires a new bounded
experiment design before inference. The audit added no model calls or spending.

That next [support-filter design](docs/support-filter-proposal.md) is now implemented
and synthetically verified: 28 cited-evidence checks on existing answers, all 50
development questions retained in scoring. Explicit errors count as failures;
additional guards prevent new failures or loss of most F1/coverage. The
[runner](docs/support-filter-runner.md) binds approval to frozen source/data/model
hashes, meters calls, and permits one attempt under an external watchdog.
115 tests pass including PostgreSQL; real artifact preflight is ready without
inference. A new allowance is required before its single 28-call/20-minute local
execution. No support-filter performance or independent human review is claimed.

The user subsequently approved that single support-filter run. It completed and
[verified](reports/support-filter-development.md), but accepted all 28 answers,
including the six unanswerable cases. Metrics are unchanged and the gate still fails.
One attempt used 28 calls and 31.375 seconds on CPU at $0 external spend. It is not
promoted; final test remains unused. The user confirmed an RTX 4090 and requires
approval for every new model training/evaluation run. The current PyTorch runtime
is CPU-only; [future GPU work](docs/compute-policy.md) needs a separate compatible
runtime and a newly approved bounded experiment.

GPU preparation is now complete for a bounded larger-checker comparison using
Qwen2.5-7B on the local RTX 4090. The [proposal](docs/gpu-support-proposal.md)
keeps the saved 28 answers, cited-only inputs and seven gate conditions fixed.
An isolated CUDA environment and 14 pinned model files are prepared; 125 tests
pass including real PostgreSQL. [Readiness](reports/gpu-support-readiness.json)
binds the proposed execution; no real GPU model loading or inference occurred.
Execution awaits explicit approval for one attempt, at most 28 calls and 20
minutes, $0 external spend. This does not complete Phase 4 or independent human
review, and does not authorize training or the unused final test.

The subsequently approved GPU support-checker attempt completed and
[verified](reports/gpu-support-development.md). It rejected 24 of 28 answers,
leaving four answers, F1 .013068, citation-ID precision .25 and zero failures.
Unanswerable answers improve from six to one, but F1/answer retention and citation
precision gates fail. It is not promoted. The run used 28 calls and 38.765 seconds
on RTX 4090 at $0 external spend. The allowance is consumed; further model runs
need new approval. Final test and Phase 4's unmet acceptance criteria are unchanged.

A subsequent [offline answer audit](reports/gpu-answer-audit.md) separates copied
text from responsiveness. All 28 outputs match source spans; 13 reach the 15-word
cap, and 19 of 22 answerable cases have higher-F1 spans available in packed text.
The draft review flags one possible label conflict without altering scores/labels.
133 software tests pass. Next prepare a fixed-input 7B answer-selector comparison;
its execution needs a new allowance. Independent human review remains pending.

That [GPU generator comparison](docs/gpu-generation-proposal.md) is implemented
and synthetically verified. The same prompt, evidence and 15-word output contract
are retained; the candidate must also strictly beat the saved constrained F1.
[Readiness](reports/gpu-generation-readiness.json) pins a single proposed attempt:
32 calls, 2,048 reserved tokens, 20 minutes, $0 external spend. 144 tests pass
including PostgreSQL. Execution awaits new approval; no new model work occurred.

The approved [GPU generation run](reports/gpu-generation-development.md) completed
and passed all eight predeclared development conditions: F1 .123578 versus .075424,
citation-ID precision .458333 versus .321429, 24 answers and zero failures. Answers
on unanswerable questions fall from six to three. The post-hoc paired family
bootstrap F1-gain interval [-.022313, .125398] includes zero; it is not a selection-
adjusted interval or proof of improvement. One attempt used 32 calls/380 actual
output tokens/50.750 seconds, $0 external spend. The allowance is consumed.
The candidate remains development-only; the service and final test are unchanged.
A [24-answer human review packet](reports/gpu-generation-human-review.md) and blank
response template are ready. Phase 4 is incomplete until the semantic-review
criterion is met; fresh final evaluation requires a separately approved scope.

The user requested that the assistant perform the review. That
[paper-grounded AI review](reports/gpu-generation-ai-review.md) is now complete
for all 24 emitted answers: 3 adequate, 11 partial, 8 inadequate and 2 ambiguous,
with rubric-sensitive cases explicitly qualified. The findings prioritize better
selection of the requested information and complete answers over mere source
copying. Suggested corrections do not change frozen predictions or scores.
This completes the requested assistant review; it does not fulfill or waive the
independent-human criterion. No new model run or final-test access occurred.
