# EvidenceBench

An agent-assisted ML engineering project: reproducible research-paper evidence
retrieval, controlled reranker training, and a local containerized API.

**Measured result:** on a frozen 100-question test set (75 answerable), the trained
TinyBERT reranker achieved **0.501 nDCG@10 versus 0.378 untuned**. The paired paper-
family bootstrap 95% interval for the difference is **[0.062, 0.182]**. These are
results on a filtered QASPER sample, not official leaderboard or production results.

The benchmark contains **350 upstream human-labeled questions**, **191 papers** and
**5,908 evidence paragraphs**, split into 200 training / 50 development / 100 test
questions. Training includes nested data sizes, a random-versus-hard-negative
ablation, three seeds, immutable runs, checkpoint reload checks and local MLflow.

**Status:** retrieval/reranking and local service are verified; final held-out scoring is complete. Generated answers are experimental: the
50-question development run has **0.118 token F1, 18% coverage and 22 failures**.
The [paper-based AI review of all nine emitted test answers](docs/claim-review.md)
is complete: two correct, four incorrect and three ambiguous; two have complete
citation support. Independent human semantic review remains an unmet plan criterion.
The optional agent is deferred. See [status](docs/status.md) and
[final evaluation](reports/final-evaluation.md).

![Development experiments](reports/development-comparison.png)

## Start the existing local deployment

Use Python 3.12, uv and Docker Desktop, from the repository root. Large artifacts
must be present; this working directory already contains them. A fresh clone needs
the local reproduction bundle or newly rebuilt/retrained artifacts; see the runbook.

```powershell
uv sync --frozen --extra ml
uv run python scripts/setup_local.py
docker compose up -d --wait db
uv run --extra ml python scripts/import_release_index.py
uv run --extra ml python scripts/export_model_cache.py
docker compose up -d --build --wait app
Invoke-RestMethod http://127.0.0.1:8000/health/ready
```

The API binds to `127.0.0.1:8000`. Readiness and version metadata are at
`/health/ready` and `/api/v1/models/current`. POST `/api/v1/retrieve` inspects evidence;
POST `/api/v1/query` returns an answer, refusal or structured failure.

```powershell
$body = @{query="In the paper 'Mining Supervisor Evaluation and Peer Feedback in Performance Appraisals', What is the average length of the sentences?"} | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/v1/query -ContentType application/json -Body $body
```

This development demo returned **15.5**, with source-page citations. Five repeated
warm answers measured 3.06 s p50 and 3.18 s p95 on this CPU host. Four simultaneous
requests produced one answer and three logged busy responses. These are small local
workloads, not production capacity claims. `docker compose stop` preserves data.

## Reproduce and inspect

```powershell
uv run --extra ml evidencebench evaluate --config configs/qasper-evaluation.yaml --split dev --suite rerankers
uv run --extra ml evidencebench train --config configs/training.yaml --query-count 50 --negative-method hard
uv run evidencebench recalculate --run artifacts/runs/20260919T025255Z-c1ee0ecf84
uv run pytest -q
uv run ruff check .
uv run ruff format --check .
uv run mypy src/evidencebench/schemas.py
```

Training remains bounded by the shared local budget; all nine slots have been
used. Further training requires a deliberately revised, recorded budget. Data/index outputs are
immutable; use a new output path for a rebuild. Test evaluation has a frozen protocol
and one-attempt ledger—recalculate existing predictions rather than tuning repeatedly.
The default PostgreSQL test skips without its environment variable; the
[runbook](docs/runbook.md) shows the real integration-test command.

The lockfile uses CPU PyTorch on Windows and Linux. No GPU training, paid model API,
cloud hosting, public deployment or remote CI execution is claimed. The service
container has no labels, credentials or document-upload endpoint. Original paper
PDFs stay outside Git and the redistribution bundle.

## Evidence and learning

- [Final evaluation](reports/final-evaluation.md): held-out comparisons, answers and limits.
- [Development experiments](reports/development-evaluation.md): learning curve, ablation, seeds and failures.
- [Dataset card](reports/qasper-dataset-card.md) and [model card](reports/model-card.md).
- [36 development failure cases](reports/development-failures.md).
- [Serving measurements](reports/serving-evaluation.md) and [runbook](docs/runbook.md).
- [Recorded API replay](reports/demo.html), [raw recording](reports/demo.cast), and [five-minute guide](docs/demo.md).
- [Teaching guide](docs/teaching-guide.md) and [interview preparation](docs/interview-prep.md).
- [Evidence index](docs/evidence-index.md): each prospective claim linked to artifacts.
- [Plan](plan.md): verified, incomplete and deferred criteria remain distinct.

This project is intended for learning and an honest portfolio. The user has not yet
practiced explaining every component. Existing job-market research links in the plan
refer to files absent from this checkout and were not recreated during implementation.

The selected reproduction bundle is recorded in [artifact-bundle.json](reports/artifact-bundle.json); all 201 included file hashes and a separate restore were verified. No bundle or repository content has been published. Replay HTML/JavaScript passed static checks; visual browser playback remains unverified because the browser policy blocked the local-file preview.

The completed paper review and updated handoff documents are packaged separately in
[claim-review-bundle.json](reports/claim-review-bundle.json). The supplement preserves
the original reproduction archive and includes per-file hashes for verification.
