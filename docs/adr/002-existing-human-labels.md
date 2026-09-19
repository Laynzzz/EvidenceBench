# 002: Use an existing human-labeled benchmark

The user explicitly chose an existing human-labeled benchmark on 2026-09-18 instead
of personally reviewing the NIST drafts. Preserve the functioning NIST extraction
pilot and never relabel its agent drafts as human annotations.

Selected: QASPER v0.3 from AllenAI, a scientific-document QA dataset containing
human questions, answers and paragraph-level supporting evidence. Its dataset card
lists CC BY 4.0 and original paper-level train/validation/test splits:
[dataset](https://huggingface.co/datasets/allenai/qasper),
[paper](https://arxiv.org/abs/2105.03011).
This changes the domain from NIST manuals to NLP research papers, within the user's
authorized corpus change. It does not justify changing the MLE-first objective.

Protocol fixed before model selection: checksum-pinned original archives; original
paper-level splits; SHA-256 ordering with seed 42; 200 supported training questions,
50 development questions (38 answerable / 12 unanswerable), and 100 final-test
questions (75 / 25). Accept unanimous answerability only. Answerable questions need
text evidence from every annotation; exclude figure/table evidence. Union the
annotators' evidence paragraphs and preserve alternative human answers.

The retrieval unit is an original QASPER paragraph prefixed by its paper title.
Questions also include the title, making the intended paper explicit to every
system. Evaluation searches the entire frozen corpus without a gold-paper filter.
Only automatically mapped paragraphs are included; missing/ambiguous mappings
exclude questions needing them. This favors extraction-friendly text evidence and
is a derived benchmark, not a reproduction of the original QASPER leaderboard.

Map paragraphs to the shortest unique one/two-page span using all normalized
words, numeric consistency, and >=90% character 5-gram coverage. This handles joined
PDF words and preserves page ranges. It remains an automatic location estimate,
not proof of factual/numerical support. The cache includes extraction recipe and
package versions. Acquisition timestamps/checksums are persisted, not regenerated.
Regression tests cover missing final sentences, duplicate locations, and decimal
number confusion. Bounding boxes are unavailable for these original paragraphs.

Grade 2 means upstream supporting evidence; unjudged paragraphs are treated as
nonrelevant for ranking metrics, not asserted to be human-judged negatives. No
grade-1 judgments are invented. The denominator includes every accepted answerable
question, even when retrieval misses all positives. Refusal rates include the
separately counted unanswerable questions. Final test remains disabled until release
selection/scoring are frozen; importer progress exposes counts only.

The upstream labels are human annotations, not a claim of new human review by this
project. Derived paragraph/chunk alignment is automated and must be audited and
described separately. Public benchmark contamination cannot be ruled out.
