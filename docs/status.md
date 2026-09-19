# Execution checklist

Implementation branch: `feat/mle-core`. The accepted architecture is in `../plan.md`.
Human annotations are required for development/test labels; agent-written drafts are not reviewed labels.
The user chose an existing human-labeled benchmark on 2026-09-18. NIST is retained as
the extraction pilot; QASPER is being assessed for the benchmark corpus.

| Phase | Status | Acceptance evidence |
|---|---|---|
| 1. Corpus and reproducible data | NIST pilot verified; benchmark transition in progress | Two identical builds, 1,773 chunks; extraction limitations documented |
| 2. Labels and baselines | Retrieval, metrics, validation and PostgreSQL parity implemented | 25 tests pass with DB; public human-label import pending |
| 3. Adaptation | Pending | Training-only data, learning curve, negative ablation, checkpoint reload |
| 4. Grounded answers | Pending | Structured generation, validated citations, reviewed support/refusals |
| 5. Deployment | Pending | Containerized selected model, failure tests, benchmark, rollback |
| 6. MLE improvement | Pending | Chosen from development evidence; agent extension deferred |
| 7. Final evaluation | Pending | Frozen comparison and untouched holdout; reproducible portfolio artifacts |

No money is authorized. Local bounded development only. No paid services or cloud resources.
Existing research links in the plan refer to files absent from this checkout; preserve those references,
but do not claim those research artifacts are included in this repository.
