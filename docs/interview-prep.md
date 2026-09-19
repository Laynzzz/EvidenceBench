# Interview preparation: current implementation

**Thirty-second explanation:** EvidenceBench is a document retrieval experiment
project. I am building a pipeline that versions public PDFs, preserves source-page
citations, compares lexical/dense retrieval, and will train and evaluate a reranker.
The current implementation is agent-assisted and has tested corpus/retrieval
foundations. Training gains and deployed answer quality have not been established.

1. **How do you make an experiment reproducible?** Pin source checksums, preprocessing,
   model revision, dependencies and index order; save predictions and configuration.
   See `ingestion.py`, `indexing.py`, `tracking.py`. Follow-up: what do nondeterministic
   GPU kernels and mutable upstream downloads change? Current CPU smoke is narrower.
2. **Why use BM25 and dense retrieval together?** They encode different relevance
   signals; fusion combines ranks without assuming comparable scores. It may improve
   recall, but improvement requires labeled evidence. See `retrieval.py` and its tests.
   Follow-up: why choose fusion depth/constant on dev, and when is a reranker worthwhile?
3. **How do you prevent leakage?** Group document versions by family; reject duplicate
   queries and non-training negative candidates; keep final tests disabled until freeze.
   See `schemas.py` and `labels.py`. Follow-up: exact checks do not catch semantic
   duplicates, common boilerplate or pretraining exposure.
4. **What did verification catch?** Review found nonfinite geometry could pass ordered
   comparisons. A regression test reproduced infinite coordinates and the validator
   now rejects them. A BM25 fixture also exposed a mistaken expectation: the shorter
   passage outranked the relevant one; the test now uses its hand-calculated nDCG.
5. **What does database parity prove?** PostgreSQL and NumPy return the same top-10
   vector results on three real-model smoke queries. It does not prove relevance,
   high-concurrency throughput or deployment reliability. See `scripts/verify_postgres.py`.

Before putting a claim on a resume, link it to `docs/evidence-index.md` and practice
explaining its scope. Do not claim independent implementation, production users,
measured accuracy gains, GPU training or API deployment from this milestone.
