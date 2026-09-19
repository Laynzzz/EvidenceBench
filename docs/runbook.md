# Local runbook

## Scope and prerequisites

Verified deployment target: this Windows 11 workstation running Linux Docker
containers, Intel i7-13700K, about 31.7 GiB RAM. An RTX 4090 exists but all recorded
training/inference uses CPU PyTorch, four threads. The app binds only to
`127.0.0.1:8000`; PostgreSQL binds only to `127.0.0.1:15432`. No public hosting or
paid API was used. The app limit is 6 GiB/4 CPUs, DB 1 GiB/2 CPUs.

Use Python 3.12, uv 0.12.17 and Docker Desktop. Commands run from the repository
root. On this machine uv is also at
`C:\Users\tiany\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\Scripts\uv.exe`.
PowerShell needs `&` before a quoted executable path. Add `-X utf8` when directly
invoking Python if the terminal otherwise uses GBK.

## Start the existing local release

```powershell
uv sync --frozen --extra ml
uv run python scripts/setup_local.py
docker compose up -d --wait db
uv run --extra ml python scripts/import_release_index.py
uv run --extra ml python scripts/export_model_cache.py
docker compose up -d --build --wait app
Invoke-RestMethod http://127.0.0.1:8000/health/ready
Invoke-RestMethod http://127.0.0.1:8000/api/v1/models/current
```

Setup preserves existing `.env` and does not print credentials. The import refuses
to overwrite an existing namespace and checks actual row counts. The cache exporter
fetches only pinned public model files, with no login/token or remote model code.
The service mounts no evaluation labels. Model cache, corpus, index and selected
checkpoint must exist before startup. `configs/release.yaml` is the selected release;
`release-proposal.yaml`, `qwen-release-candidate.yaml` and Smol/NIST configs are
historical experiments, not current entry points.

```powershell
$body = @{query="In the paper 'Mining Supervisor Evaluation and Peer Feedback in Performance Appraisals', What is the average length of the sentences?"} | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/v1/query -ContentType application/json -Body $body
uv run python scripts/benchmark_api.py
uv run python scripts/verify_serving_parity.py
```

The development demo returned **15.5** with source/page references. The API can
also return structured refusals and failures; do not assume every question works.
Use `/api/v1/retrieve` with `k` for evidence inspection. Responses include versions,
request IDs and available stage timings. No authentication is configured because
this deployment is loopback-only; do not expose it publicly as-is.

## Rebuild data or recover another checkout

Large artifacts are ignored by Git. Restore the locally prepared reproduction
bundle (see `reports/artifact-bundle.json`) to reproduce this exact selected
checkpoint/corpus/index. It excludes original paper PDFs and base-model caches.
Get the base models through `export_model_cache.py`. No artifact bundle has been
published or uploaded. A clone alone does not include the trained weights.

To independently rebuild data:

```powershell
uv run --extra ml python scripts/acquire_qasper.py
uv run --extra ml python scripts/build_qasper.py --output artifacts/verification/qasper-rebuild --labels artifacts/verification/qasper-rebuild-labels
```

The frozen selection preserves source paper/question IDs. Existing outputs reject
overwrite. Original PDFs remain downloadable from their own sources and are not
redistributed. To build a new index, copy `configs/qasper-retrieval.yaml`, change its
corpus/index output paths, then run `evidencebench index --config YOUR_CONFIG`.
Do not rewrite an old fingerprint to disguise different bytes.

Training/reselection creates a **new experiment**, not a silent replacement of
this frozen release. The nine-run shared budget is exhausted. Do not bypass it by changing run directories;
record a deliberate budget/protocol revision before further experiments. Reproduction used
the 200-query hard-negative config and seed 42;
50/100-query and random-negative options are CLI flags. Compare dev metrics and
checkpoint scores; metadata/checkpoint bytes may vary across environments. Preserve
the historical final results and use a new holdout for any post-test tuning claim.

## Evaluation, tests and inspection

```powershell
uv run --extra ml evidencebench evaluate --config configs/qasper-evaluation.yaml --split dev --suite rerankers
uv run --extra ml evidencebench evaluate --config configs/qasper-evaluation.yaml --split dev --suite answers
uv run evidencebench recalculate --run artifacts/runs/20260919T025255Z-c1ee0ecf84
uv run evidencebench inspect --run artifacts/runs/20260919T025255Z-c1ee0ecf84
uv run pytest -q
uv run ruff check .
uv run ruff format --check .
uv run mypy src/evidencebench/schemas.py
```

The final `--split test --suite release` command is guarded by
`data/manifests/release-lock.json` and the one-attempt ledger
`artifacts/final-attempt.json`. It is intentionally not a routine rerun command.
Recalculate saved predictions instead. Do not delete the ledger to tune repeatedly
against the same holdout. Frozen files, actual index fingerprint and checkpoint
hash are checked before scoring.

The default DB test skips if `EVIDENCEBENCH_TEST_DATABASE_URL` is absent. To run it
against this project's local DB without printing credentials:

```powershell
uv run python -c "import os,pytest; from dotenv import load_dotenv; load_dotenv('.env'); os.environ['EVIDENCEBENCH_TEST_DATABASE_URL']=os.environ['EVIDENCEBENCH_DATABASE_URL']; raise SystemExit(pytest.main(['-q']))"
```

The isolated environment test used a separate virtual environment and locked base
dependencies. The Docker image independently installed Linux ML dependencies. The
GitHub workflow is configured with pinned actions, tests, PostgreSQL and image build;
remote CI has not run because nothing has been pushed.

## Failures, rollback and logs

- 422: malformed/oversized input. Correct the request.
- 429: inference already in progress. Retry later; requests are not queued.
- 502: generation failed JSON/citation validation after one retry.
- 503: missing/unavailable dependency. Inspect readiness and DB/container health.
- 504: cooperative generator timeout. The result is a failure, not an empty success.

`docker compose logs --no-color app` includes structured query/retrieve records,
including busy requests, versions, stage times, status and token count when available.
Framework logs also include HTTP validation/health requests. Logs contain no raw
question/document text by design. Readiness checks actual row counts but is not a
continuous cryptographic audit of every database vector; arbitrary DB mutations are
outside this prototype's trust model. Startup validates local artifact hashes.

A real outage check stopped only this project's DB: liveness stayed 200, readiness
and query returned 503, and restarting DB restored service. Never stop unrelated
Docker projects. Missing/corrupt local artifacts fail startup rather than serving
with a different index. Cooperative model timeouts are not OS-enforced hard deadlines.

Rollback was exercised to the previous `evidencebench:dev-foundation` image and
its NIST pilot release. It restored readiness, version metadata and retrieval; its
known weak generator was not claimed fixed. Commands for this local historical image:

```powershell
$env:EVIDENCEBENCH_IMAGE='evidencebench:dev-foundation'
$env:EVIDENCEBENCH_RELEASE='configs/pilot-release.yaml'
docker compose up -d --no-build --wait app
Remove-Item Env:EVIDENCEBENCH_IMAGE
Remove-Item Env:EVIDENCEBENCH_RELEASE
docker compose up -d --no-build --wait app
```

Keep the previous image and artifact versions when rolling back. Immutable image IDs
are recorded in the serving report; a locally rebuilt tag can point to a new image.

## Stop and retained state

```powershell
docker compose stop
```

This stops this project's containers and preserves PostgreSQL data, downloaded
models, source PDFs, experiment exports and checkpoints. No cloud resource is
running. Local CPU/RAM/disk/electricity still have real costs; no dollar estimate is
invented. Do not remove volumes or user caches as incidental cleanup.

## Verify the local bundle

Check the ZIP SHA-256 against `reports/artifact-bundle.json` (`Get-FileHash` on Windows), then extract only into the intended checkout. `BUNDLE-MANIFEST.json` records every member hash. The prepared ZIP was extracted into a separate directory and all 201 hashes, 5,908 corpus units, index fingerprint and selected checkpoint tree were verified. The bundle is local only.

`uv run python scripts/verify_reports.py` recalculates the final and original development report roster without rerunning models. This deliberately excludes the later same-seed reproduction from the three-seed uncertainty calculation.
