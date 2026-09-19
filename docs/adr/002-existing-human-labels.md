# 002: Use an existing human-labeled benchmark

The user explicitly chose an existing human-labeled benchmark on 2026-09-18 instead
of personally reviewing the NIST drafts. Preserve the functioning NIST extraction
pilot and never relabel its agent drafts as human annotations.

Candidate: QASPER v0.3 from AllenAI, a scientific-document QA dataset containing
human questions, answers and paragraph-level supporting evidence. Its dataset card
lists CC BY 4.0 and original paper-level train/validation/test splits:
[dataset](https://huggingface.co/datasets/allenai/qasper),
[paper](https://arxiv.org/abs/2105.03011).
This changes the domain from NIST manuals to NLP research papers, within the user's
authorized corpus change. It does not justify changing the MLE-first objective.

Before adopting: verify source artifacts and human annotation provenance, preserve
paper-family disjointness, and investigate reliable PDF-page mapping. Do not invent
page numbers from paragraph order. Restrict to text-supported evidence when the
chosen protocol excludes tables/figures. Document filtering and disagreement rules
before model selection, and do not inspect final-test predictions during tuning.

The upstream labels are human annotations, not a claim of new human review by this
project. Derived paragraph/chunk alignment is automated and must be audited and
described separately. Public benchmark contamination cannot be ruled out.
