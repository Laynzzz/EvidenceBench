# Proposed bounded fresh-validation comparison

Status: **prepared for approval; no model runs authorized by this document**.
The previous training and cycle-3 experiment allowances are exhausted. Dataset
construction is separately authorized and recorded in [the build record](fresh-dataset-build.md).
This proposal makes the next requested compute allowance concrete.

## Scope and caps

One comparison on the new **50-question validation split only**, using the frozen
v1 control and the already selected constrained-span candidate. No prompt search,
threshold tuning, training, new model downloads, paid APIs or deployment. Keep the
100-question final test unused; a later final-test run is a separate decision.

- Existing CPU host, four Torch threads, float32; $0 external spend.
- One new dense index over the frozen 3,161-paragraph fresh corpus (each embedded once),
  retained under a new artifact path. No change to the live service or its database.
- At most 50 validation query embeddings and 2,500 query/passage reranker pairs.
  Retrieve once per query and replay identical passages for both generators.
- At most 50 calls to each generator interface. The v1 control permits one format
  repair, so the worst case is **150 underlying generation calls total**:
  100 for control and 50 for candidate. Refusals before generation reduce usage.
- Existing 1,536-token input limit, 100 output tokens per control call and 64 per
  candidate call; at most 13,200 generated tokens across all calls.
- Existing 20-second budget per query/generator invocation. Add an external
  **45-minute wall-clock deadline** for the entire index-and-comparison job.
- One attempt only. Interrupted, failed or timed-out work is retained and consumes
  the attempt. Cached data and attempt records may be inspected without rerunning
  inference; any replacement needs a separately stated allowance.

Use the exact MiniLM revision, trained TinyBERT checkpoint, and Qwen0.5B revision
from `configs/release.yaml`. Keep candidate count 50, three passages, 1,000 characters
per passage, and refusal threshold 3.2478480339050293. Generation code comes from
the frozen v1 control and cycle-3 constrained variant. The fresh corpus changes the
retrieval population for both systems equally; it is not a direct rerun of v1 scores.

## Evidence and decision

Before execution, implement and verify a separate runner; freeze its configuration,
code, corpus/labels and checkpoint hashes in an attempt manifest. Authorization of
this proposal would cover that runner and this single bounded execution, not later
experimental retries. No labels or reference evidence may enter retrieval, packing
or generation. Save pre-rerank and post-rerank rankings, packed IDs, predictions,
timings, call counts, failures and checksums. Run all queries, including failures,
and record CPU latency separately from any previous deployment measurements.

Report answerable token F1, coverage, failures, false refusals, answers to unanswerable
questions, citation-ID precision/recall, and gold-evidence recall before/after packing.
Use the gate already specified in [the protocol](fresh-evaluation-protocol.md):
F1 must improve; failures and unanswerable answers must not increase; citation-ID
precision must not decline. Preserve the outcome even if the candidate fails.
Passing does not satisfy independent human semantic review or authorize deployment.

The final-test labels remain uninspected. Indexing public paper text does not expose
its held-out questions or answers, but the corpus and label artifacts must remain
fixed once the comparison starts.

The constructed dataset is recorded in [fresh-dataset.json](../reports/fresh-dataset.json):
corpus fingerprint `e436aff0b5fb63209ab23faedf393321fa41250ff7bd33264048f2691ae3d9a1`;
validation-label SHA-256 `20c1979353b31afe35526b6b55edf725085a652a76e4df61f0a3ee7226ac3dc5`.
Construction and cache-only verification are complete. The
[comparison runner](fresh-validation-runner.md) is now implemented, with synthetic
integration tests and real read-only preflight checks. It has not loaded models or
run inference on the fresh dataset. Approval covers one execution of this prepared
runner within the bounds above; it does not replenish the older experiment budgets.
