# EvidenceBench

A reproducible retrieval and reranking project for learning applied ML engineering.
The current working increment builds a versioned PDF corpus, searches it with BM25,
dense embeddings and reciprocal-rank fusion, and validates evaluation data.

**Status:** Corpus/retrieval foundations implemented and tested. Model adaptation,
grounded generation, API deployment and final evaluation are not complete. No
retrieval-quality improvement is claimed. See [execution status](docs/status.md).

## Run locally

Requires Python 3.12 and [uv](https://docs.astral.sh/uv/). Commands run from this
repository's root. On this Windows machine, uv is also available at
`C:\Users\tiany\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\Scripts\uv.exe`.

```powershell
uv sync --locked --extra ml
uv run --extra ml evidencebench build --config configs/corpus.yaml
uv run --extra ml evidencebench index --config configs/retrieval.yaml
uv run --extra ml evidencebench search --query "What is a policy enforcement point?" --system hybrid
uv run evidencebench inspect --corpus data/processed/nist-v1 --document nist-sp-800-207 --page 19
```

Existing corpus/index directories are immutable: reruns reject an existing output.
For an independent ingestion comparison, use `--output artifacts/verification/new-build`.
The index path is configured in `configs/retrieval.yaml`; use a new path for a new build.
BM25 search does not need the `ml` extra. Search returns evidence, not generated answers.

The optional `ml` dependency group installs the CPU PyTorch build from PyPI on this
Windows host. Its real MiniLM indexing pilot used four CPU threads. An RTX 4090 is
present, but CUDA-enabled training has not been configured or tested. Do not infer
training throughput from the CPU indexing measurement.

## PostgreSQL verification

Docker Desktop must be running. Setup creates a random password in ignored `.env`;
it does not print credentials. The database binds only to loopback port 15432.

```powershell
uv run python scripts/setup_local.py
docker compose up -d --wait
uv run --extra ml python scripts/verify_postgres.py
docker compose stop
```

The last command stops compute while preserving the local database volume. The
parity script imports the immutable index and compares PostgreSQL/local cosine
rankings. Current interactive search uses the local reference index; database-backed
serving is a later phase. No API or public deployment exists yet.

## Tests and labels

```powershell
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy src/evidencebench/schemas.py
uv run evidencebench validate-labels --labels data/labels/dev-pilot-draft.jsonl --allow-drafts
```

The default tests exercise original synthetic fixtures, not held-out benchmark
examples. The real PostgreSQL test requires `EVIDENCEBENCH_TEST_DATABASE_URL`; it
skips explicitly when the variable is absent. One verified local command is:

```powershell
uv run python -c "import os,pytest; from dotenv import load_dotenv; load_dotenv('.env'); os.environ['EVIDENCEBENCH_TEST_DATABASE_URL']=os.environ['EVIDENCEBENCH_DATABASE_URL']; raise SystemExit(pytest.main(['-q']))"
```

Read the [labeling guide](data/labels/README.md) and [first review batch](docs/label-review-pilot.md).
There are **12 draft development questions and zero human-reviewed benchmark labels**.
`--allow-drafts` validates structure only; it does not authorize quality evaluation.
Once a reviewed `data/labels/dev.jsonl` exists:

```powershell
uv run --extra ml evidencebench evaluate --config configs/evaluation.yaml --split dev --suite retrieval-baselines
uv run evidencebench recalculate --run artifacts/runs/ACTUAL_RUN_ID
```

Replace `ACTUAL_RUN_ID` with the emitted run directory. Final-test execution is
deliberately unavailable until a frozen release protocol is implemented.

## Learn and inspect

- [Teaching guide](docs/teaching-guide.md): product flow, concepts, trade-offs and reading path.
- [Interview preparation](docs/interview-prep.md): claims supported by this implementation.
- [Evidence index](docs/evidence-index.md): verification commands and limitations.
- [Dataset card](reports/dataset-card.md): sources, splits and extraction limitations.
- [Skill map](docs/skill-map.md): installed/recommended skills by phase.
- [Plan](plan.md): full target, including work not yet implemented.
