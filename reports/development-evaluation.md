# Development experiments

All model selection uses development data. 38 answerable questions in 21 paper families contribute ranking scores; 12 unanswerable questions contribute failure/latency and refusal evidence.

| System | nDCG@10 | Recall@10 | p95 ms | Failures |
|---|---:|---:|---:|---:|
| bm25 | 0.3726 | 0.6096 | 91.5 | 0 |
| dense | 0.3970 | 0.6754 | 97.3 | 0 |
| hybrid | 0.3964 | 0.6491 | 121.9 | 0 |
| trained-100-hard | 0.5602 | 0.8421 | 283.2 | 0 |
| trained-200-hard | 0.5693 | 0.8333 | 313.7 | 0 |
| trained-200-random | 0.5168 | 0.8289 | 288.2 | 0 |
| trained-50-hard | 0.5628 | 0.8421 | 305.1 | 0 |
| untuned | 0.5145 | 0.8158 | 284.1 | 0 |

Seed 42 was predeclared. Configuration selection among its runs used nDCG, subject to the predeclared 1,000 ms reranking p95 ceiling and zero failures. All trained candidates use the same architecture and inference cost. Training size was selected on dev; test does not reselect.

The selected 200-query hard-negative model improves nDCG by 0.0548 over untuned. The paired paper-family bootstrap 95% interval is [-0.0301, 0.1474] (2,000 draws, seed 42). It includes zero; this is not established population-level improvement.

| Training run | Queries / pairs | Negatives | Seed | Dev nDCG | Status |
|---|---:|---|---:|---:|---|
| `20260919T020928Z-3815e006a0` | 4 / 21 | hard | 42 | 0.5451 | complete (smoke) |
| `20260919T021150Z-84299e40de` | 50 / 268 | hard | 42 | 0.5628 | complete  |
| `20260919T021323Z-b0864d9160` | 100 / 538 | hard | 42 | 0.5602 | complete  |
| `20260919T021555Z-346e0e4c88` | None / None | hard | 42 | — | failed  |
| `20260919T021808Z-bce3010267` | 200 / 1066 | hard | 42 | 0.5693 | complete  |
| `20260919T022020Z-23e3eb5e19` | 200 / 1066 | random | 42 | 0.5168 | complete  |
| `20260919T022351Z-7975d080bc` | 200 / 1066 | hard | 43 | 0.5626 | complete  |
| `20260919T022739Z-a791c82d12` | 200 / 1066 | hard | 44 | 0.5578 | complete  |

Three-seed mean nDCG 0.5632, sample SD 0.0058. These repeats estimate seed sensitivity on the same development set, not generalization uncertainty.

50→100→200 queries shows a nearly flat learning curve. Random negatives reach only 0.5168, versus 0.5693 with hard negatives under matched query count and pair count. Unjudged negatives can still contain relevant evidence; zero exact-answer phrase collisions in the automated 800-negative audit does not prove they are true negatives.

One setup run failed before optimization because a replacement model-card object lacked model registration. It is retained as failed. The corrected run saves/reloads the checkpoint and checks score parity within 1e-6. Eight of nine training slots were used, including smoke and failure.

Cached BM25 statistics reproduce all four saved pair sets byte-for-byte; 200-query mining takes 23.78 seconds in the recorded parity check. This is an exact caching optimization; no before/after speedup ratio is claimed without a controlled timing pair.

Raw provenance: `artifacts/verification/development-selection.json`, each training manifest/config/source.zip, local MLflow, and `reports/experiment-summary.json`. CPU four-thread results on this host are not cloud/GPU throughput measurements.

## Unchanged reproduction after final scoring

The ninth and final budgeted run (`20260919T030457Z-c2c07a6dd6`) repeated the selected seed-42 configuration without tuning or reselection. Training pairs and every model parameter were identical (maximum parameter difference 0.0), and dev nDCG remained 0.56931246. The checkpoint-tree fingerprint differs because surrounding artifact metadata differs; the released checkpoint remains the original. This replica is excluded from the three-seed uncertainty roster. All 9/9 training slots are now used.

`python scripts/verify_reports.py` recalculates metrics from the captured original run roster. The frozen `report_experiments.py` is the historical pre-test generator; its directory-discovery assumption predates the later reproduction run. Use the roster-based verifier for the final reports.
