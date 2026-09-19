# Fresh validation: candidate fails promotion gate

The single approved comparison completed on all 50 fresh validation questions
(38 answerable, 12 unanswerable; 33 paper families). The constrained-span candidate
improved reference F1 and eliminated generation failures, but answered more
unanswerable questions and reduced citation-ID precision. It **fails the frozen
selection gate and is not promoted**. Phase 4 acceptance remains incomplete.

## Paired results

| Metric | Frozen control | Constrained spans |
|---|---:|---:|
| Answerable token F1 (all 38) | 0.012025 | 0.075424 |
| Answers / 50 | 11 | 28 |
| Failures / 50 | 21 | 0 |
| Refusals / 50 | 18 | 22 |
| False refusals / 38 answerable | 12 | 16 |
| Answers / 12 unanswerable | 3 | 6 |
| Refusals / 12 unanswerable | 6 | 6 |
| Citation-ID precision | 0.363636 | 0.321429 |
| Citation-ID recall | 0.068966 | 0.155172 |
| Local per-query p50 / p95 | 3.099 / 10.284 s | 2.097 / 3.533 s |

F1 improvement and failure-count criteria pass; unanswerable-answer and citation-
precision criteria fail. The control's three remaining unanswerable cases are
failures, not correct refusals. Eliminating format failures alone therefore does
not establish better abstention. All 21 control failures were `invalid_generation`.
Latency includes shared retrieval plus each generator's time; it is not a service
load measurement. Reference agreement does not establish semantic support.

## Evidence bottlenecks: supplementary offline diagnosis

Macro gold-evidence recall over the 38 answerable questions was **97.37%** in the
50 retrieval candidates, **49.34%** in the reranked top three before the threshold,
and **34.87%** after threshold-based packing. Reranking all 50 preserves candidate
recall by construction. The threshold withheld context for 12 answerable questions;
only 17 of 38 had any gold paragraph in the final context. These ID checks do not
measure support surviving the 1,000-character clipping or model-token truncation.

Of the candidate's 28 answers: nine cite a gold paragraph, six have no gold paragraph
packed, seven have gold available but cite other evidence, and six answer an
unanswerable question. These are mechanical categories, not paper-based semantic
judgments. This result points to evidence selection and abstention as priorities
for a separately designed improvement cycle; it does not establish that changing
either will improve held-out performance. No settings were changed after scoring.

Across answerable questions, F1 improved on 12, tied on 25 and worsened on one.
A supplementary, post-hoc paired paper-family bootstrap gives mean delta
**0.06340**, percentile 95% interval **[0.02820, 0.10064]** (38 questions in 26
answerable families, 2,000 resamples, seed 42). Families are sampled with replacement,
then their query deltas are averaged. This interval does not override the gate,
correct for earlier development selection, or prove generalization outside this
filtered sample. See [per-query diagnostics](fresh-validation-diagnostics.json).

## Execution and verification

- Run: `artifacts/fresh-validation-v1/runs/20260919T233427Z-ddfba1b48e`.
- Frozen implementation: `529a74da0b9bc2f4f4e3ecf39472d6c13c010e2a`.
- One attempt; supervisor exited successfully after **358.109 seconds** (5.97 min),
  below the approved 45-minute deadline.
- 3,161 document embeddings, 50 query embeddings, 2,500 reranker pairs;
  32 invocations per generator, **54 control + 32 candidate = 86 generation calls**
  against the 150-call cap. Both received identical retrieved passages.
- Maximum-output-token reservations: 7,448 / 13,200; actual emitted tokens were
  not separately counted. Cached models, CPU only, offline loading, **$0 external spend**.
- The source/config/cache/data hashes, exact query roster, paired contexts, citations,
  metrics, usage and successful supervisor completion passed read-only verification.
- Original v1, cycle-2, cycle-3 and reservation/diagnostic verification also passed.
  No source implementation changed after freezing. The previous 89-test result is
  preparation evidence; this turn verified real execution and reports.

From the repository root, verify without inference:

```powershell
.venv/Scripts/python.exe -X utf8 scripts/verify_fresh_validation.py --run artifacts/fresh-validation-v1/runs/20260919T233427Z-ddfba1b48e
```

[Structured results and artifact hashes](fresh-validation.json),
[authorization](fresh-validation-authorization.json),
[frozen proposal](../docs/fresh-validation-proposal.md), and
[protocol](../docs/fresh-evaluation-protocol.md) preserve the decision trail.
The proposal's pre-approval wording is historical and remains unchanged because
the attempt pins its bytes. All run artifacts and the new index are retained locally;
earlier reproduction ZIPs do not include this comparison. No background job remains.

The 100-question fresh final test remains unused for inference and its examples
uninspected. The original service/release, old results and exhausted earlier budgets
remain unchanged. This allowance is consumed. No extra attempts, training, model
downloads, paid services, final-test run or deployment were performed. Independent
human generated-claim review is still outstanding.
