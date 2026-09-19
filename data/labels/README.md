# Labeling protocol

No development/test label is currently human-reviewed. `dev-pilot-draft.jsonl`
contains 12 agent drafts, including three easy unanswerable cases. It is a review
starter, not the target 150–250-query evaluation set.

1. Read the source PDF at the physical PDF page number, not only extracted text.
2. Judge relevance: 0 irrelevant; 1 useful context; 2 directly supports the answer.
3. Correct the answer criteria and include all known directly supporting chunks.
   Overlapping chunks may both be relevant. Incomplete judgments underestimate recall.
4. Check answerability against the full frozen corpus. The final set needs difficult
   in-domain missing-evidence cases as well as obvious out-of-domain refusals.
5. Check ambiguous wording, query types, and coverage across families. Do not use
   NIST authority boilerplate, document titles, or tables with interleaved columns
   as family-specific evidence. Figure-only answers are outside the text-only task.
6. Review without model predictions. Record reviewer identity/pseudonym, date,
   method and corrections in `label_provenance`, then set `review_status` to
   `human-reviewed` only after an actual human review. Preserve original drafts.
7. Blindly re-review a sample later and record disagreement; do not call this
   inter-annotator agreement when only one person reviewed.

Create separate train/dev/test JSONL files. The plan targets at least 200 distinct
training queries and 150–250 reviewed dev/test queries combined, with 20–25%
unanswerable cases in each evaluation split. The initial batch does not meet those
targets. The full unreviewed test set has not been authored, inspected, or evaluated.

Training queries and all candidate negatives must use training families. Negative
mining excludes known positives but still needs a false-negative audit. Record
random seeds, the candidate corpus version, unique queries and query-document pair
counts separately. Synthetic training data needs prompt/generator provenance and a
reviewed audit sample; changing the label flag does not constitute review.

Before model selection, freeze IDs, labels, splits, scoring rules and candidate
settings. Validate combined files for duplicate IDs/text across splits. Code checks
exact normalized duplicates; semantic near-duplicates still need review. Development
search sees the full corpus, but labels cannot pass hidden gold-family filters.

Metric convention: Recall@5/10/20 treats grades 1 and 2 as relevant. nDCG@10 uses
gain `2**grade - 1`. MRR uses the first positive within the returned top 20. Ranking
aggregates include answerable queries only. Failures produce empty predictions
and zero ranking scores; report unanswerable/failure counts separately. Equal
scores are broken by stable element ID. Family bootstrap is paired and seeded;
only two development families produce very limited uncertainty evidence.
