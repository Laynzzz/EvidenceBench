# QASPER-derived evidence benchmark v1

The user selected an existing human-labeled benchmark. [QASPER](https://huggingface.co/datasets/allenai/qasper)
provides questions, answers and evidence from NLP practitioners. This project adapts
the original v0.3 archives; see the [annotation paper](https://arxiv.org/abs/2105.03011).
QASPER text/annotations are CC BY 4.0. Original PDFs retain their authors' rights
and are fetched locally, not redistributed in Git. No private documents are used.

| Split | Papers | Paragraphs | Questions | Answerable / unanswerable |
|---|---:|---:|---:|---:|
| Train | 112 | 3,579 | 200 | 200 / 0 |
| Development | 27 | 790 | 50 | 38 / 12 |
| Final test | 52 | 1,539 | 100 | 75 / 25 |
| Total | 191 | 5,908 | 350 | 313 / 37 |

There are 1,912 source PDF pages and 451 supporting query–paragraph judgments.
Original paper splits are preserved. SHA-256 ordering with seed 42 and fixed class
quotas determine the subset before model selection. The selected IDs, PDF checksums,
label hashes and scoring rules are frozen in `data/manifests/`. Retrieval searches
the full frozen corpus. Training/mining accesses training families only.

All annotators must agree on answerability. Every answer annotation needs usable
text evidence; figure/table evidence and questions missing mapped support are excluded.
The union of human evidence is grade 2; alternative human answers are retained.
No grade-1 judgments are invented. Unjudged passages count as nonrelevant in ranking
metrics but are not asserted to be human-judged negatives. Unanswerable means not
answerable in the named paper. Titles are visible in both queries and paragraphs.

Mapping uses pdfplumber 0.11.10 / pdfminer-six 20260107, NFKC, joined-word-tolerant
matching, numeric consistency and character 5-gram coverage. Unique one/two-page
ranges are retained: 782 paragraphs span pages. Of 9,828 paragraphs in selected
papers, 5,908 passed mapping. The audit records 435 question-level missing-evidence
mapping events and two unavailable PDFs; these are not complete-upstream failure rates.

Mapping is automated, not human verification. Agent visual inspection of one train
and one dev page confirmed those samples, not population-wide accuracy. Math/reference
placeholders remain; equations are not reconstructed; bounding boxes are null.
Filtering favors text and extraction-friendly papers. Fixed answerability quotas
do not represent real traffic prevalence. Public-model pretraining contamination
cannot be ruled out. This derived task is not the original QASPER leaderboard.

Repeat builds produced identical corpus and label bytes. Corpus fingerprint:
`7ee04c7e89a9e5997ece5a26960a820d61a85fc9dc47491b2c1383a201d16412`.
Raw audit: `artifacts/verification/qasper-data-audit.json`. Final-test scoring stays
disabled until release selection is frozen. See [protocol decision](../docs/adr/002-existing-human-labels.md).
