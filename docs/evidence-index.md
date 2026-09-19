# Verification evidence

This file maps implementation claims to commands and retained local artifacts.
Generated artifacts are ignored by Git and must be reproduced after cloning.

| Claim | Evidence | Limits |
|---|---|---|
| Source integrity and reproducible extraction | `uv run evidencebench build --config configs/corpus.yaml` and a second clean `--output` | Original raw PDFs and pinned versions required |
| Identical corpus content | `data/processed/nist-v1/manifest.json`, `artifacts/verification/corpus-repeat/manifest.json` | 1,773 chunks; see dataset card for omitted figures/tables |
| Invalid data and regression handling | `uv run pytest` | Synthetic fixtures; database test needs configured URL |
| Shared contract types | `uv run mypy src/evidencebench/schemas.py` | Not whole-project strict typing |
| Real embedding build | `artifacts/indexes/minilm-v1/manifest.json` | CPU, four threads, 84.23 seconds includes model load; not quality evaluation |
| Real-model search output | `artifacts/verification/hybrid-search.json` | Two passages from one smoke query, not relevance judgments |
| PostgreSQL vector parity | `uv run --extra ml python scripts/verify_postgres.py`; `artifacts/verification/postgres-parity.json` | Three queries, exact top-10 IDs and score tolerance 1e-6 |
| Raw predictions reproduce metrics | `tests/unit/test_runner.py` | Synthetic fixtures, including timeout; no benchmark labels |
| Draft labels remain unapproved | `validate-labels --labels data/labels/dev-pilot-draft.jsonl --allow-drafts` | 12 drafts / 0 reviewed; evaluator refuses them |

Hardware observed: Windows, Intel i7-13700K, approximately 31.7 GiB RAM,
RTX 4090 (24,564 MiB), driver 591.86. The installed PyTorch wheel is CPU-only.
Database: PostgreSQL 17 with pgvector 0.8.1, image digest pinned in Compose.

Independent code review examined schema/chunk/ingestion behavior and both builds.
It found a nonfinite-coordinate contract bug (fixed with regression coverage) and
shared cross-family boilerplate (documented). It did not audit the whole future system.

Monetary spending: no paid provider/cloud jobs launched. Retained local state:
Python environment, Hugging Face model cache, source PDFs, processed artifacts and
the `evidencebench_postgres-data` volume. `docker compose stop` stops the database
without deleting its data. Do not delete the volume as incidental cleanup.
