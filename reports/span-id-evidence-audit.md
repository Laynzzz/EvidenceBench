# Saved span-ID evidence diagnosis

2026-09-24. The format change worked, but the remaining errors require separate
work on evidence delivery and answer selection. This audit uses only saved
development outputs: no inference, training, final-test access or benchmark rescore.
The candidate remains unpromoted and Phase 4 remains incomplete.

## Mechanical evidence path: all 50 development questions

[Recomputed facts](span-id-evidence-audit.json) trace the frozen run
`20260924T055954Z-4ed67439fb`. Among the 38 answerable questions:

| Stage | Questions with at least one annotated supporting passage |
| --- | ---: |
| Retrieved candidate roster | 37 / 38 |
| Reranked top three | 23 / 38 |
| Actually supplied to generator | 17 / 38 |
| Cited in the answer | 14 / 38 |

The first missing-gold stage is retrieval for one question, top-three selection for
14, threshold refusal for six, and citation selection for three. Fourteen reach a
gold citation. These are annotation-ID facts, **not semantic sufficiency scores**:
an unannotated paragraph can still answer a question, and a cited gold paragraph
does not guarantee the generated claim is correct. The stages describe the whole
current pipeline; this audit does not isolate a causal reranker effect.

All 12 answerable refusals occur before generation. Six have an annotated passage
in the reranked top three; six already lack top-three gold. The other six threshold
refusals and both model refusals are benchmark-unanswerable. Of the two model
refusals, assistant review finds one justified by missing requested quantitative
evidence and one unclear because the dataset question's scope is ambiguous.
Threshold changes require a new design; this finding is not permission to tune a
threshold on the repeatedly used development set.

## Clipping: observable boundaries versus useful information loss

The 32 generator inputs contain 96 passage occurrences. Of these, 25 are clipped
at 1,000 characters, 17 end inside an alphanumeric word, and six clipped passages
are cited. Eighteen inputs contain at least one clipped passage. One selected span
ends at the clipped boundary, established by its source offsets rather than text
suffix matching. Counts are occurrences across questions, not unique paragraphs.

Comparing the supplied text with the same original development paragraphs finds
useful omitted details in four cases:

| Question (ID prefix) | Useful information beyond the cut |
| --- | --- |
| Humor baseline classifiers (`dea9e7`) | Random forest and naive Bayes |
| Vietnamese segmentation challenges (`fe2666`) | Incremental corpus learning and interactive feedback |
| Cyberbullying topics (`7e38e0`) | Complete personal-attack, racism and sexism list; output was `perso` |
| Human-judgment procedure (`0ee739`) | Fluency categories and paired sentence ranking with ties |

Restoring those tails may improve the available evidence; improvement in model
answers has **not** been measured. Some of these answers also omit facts already
present before the cut. Clipping is therefore a demonstrated input defect, not
an explanation for every bad answer.

## Assistant semantic review: 32 supplied-evidence cases

[Case-level judgments and exact supporting excerpts](span-id-evidence-review.json)
cover all 30 answers and two model refusals. Two assistant reviewers handled
disjoint batches; each case has one review, with root provenance checks. They saw
references and labels. This is non-blinded assistant diagnosis, not independent
human evaluation, inter-rater agreement, or a new benchmark score.

| Dimension | Assistant judgment counts |
| --- | --- |
| Packed evidence sufficiency, 32 inputs | 16 sufficient, 9 partial, 2 insufficient, 5 ambiguous |
| Answer quality, 30 answers | 7 adequate, 9 partial, 13 inadequate, 1 ambiguous |
| Selected-quote support, 30 answers | 19 supported, 3 partial, 8 unsupported |
| Among 16 inputs judged sufficient | 7 adequate, 5 partial, 4 inadequate answers |

These dimensions deliberately differ. A quote can fully support an unhelpful
restatement without answering the question. Conversely, useful facts elsewhere
in the input do not repair an unrelated selected citation. Frequent errors include
features or training data presented as model identities, omitted list items,
confusing prior work with the target study, and missing antecedents in citations.
The cyberbullying result assigns .95 to Twitter although the cited text says .94;
its partial rating retains that explicit factual error.

Two interpretation limits matter:

- The NCEL answer copies a conclusion claiming outperformance across five datasets.
  Its packed-only adequate rating does not supersede the earlier
  [paper-grounded review](gpu-generation-ai-review.md), which found losses/ties in
  result tables that make blanket outperformance misleading.
- The TF-IDF question has explicit feature evidence despite its unanswerable
  label. Other questions have scope/reference mismatches. Keep these conflicts
  visible without changing frozen labels, metrics or acceptance gates.

## Next engineering decision

Prepare a controlled intact-passage comparison before changing retrieval or
training a model: retain the same paragraph identities, model, prompt contract,
threshold decisions and development roster, and investigate restoring the original
paragraph bodies within a verified context budget. Check token lengths without
loading model weights before fixing any execution allowance. Avoid choosing tails
from reference answers or special-casing the four reviewed questions.

This would test evidence delivery only. It would not address the nine non-adequate
answers with sufficient packed evidence, validate source claims against all paper
tables, or satisfy independent human review. Keep claim attribution and appropriate
refusal as separate unresolved requirements. Do not promote a candidate based on
format validity or one development metric.

## Verification and reproduction

Implementation revision: `05d7d01` (audit and regression fixes). Runtime: Windows,
the locked CPU `.venv`, existing real local PostgreSQL, frozen QASPER fresh-v1
development corpus. The JSON report pins source, corpus, config and prediction
hashes; the frozen runner verifies its upstream snapshot before recomputation.

```powershell
.venv/Scripts/python.exe -X utf8 scripts/audit_span_id_evidence.py --verify
.venv/Scripts/python.exe -X utf8 scripts/verify_span_id_evidence_review.py
.venv/Scripts/python.exe -X utf8 -m pytest tests/unit/test_span_id_audit.py -q --tb=short
```

The 13 synthetic audit checks pass, including three reproduced code-review edge
cases. The full software suite passes **207 tests**, with two existing deprecation
warnings, in 8.24 seconds; PostgreSQL tests load the ignored local database setting
without printing it. These are software checks, not a new model evaluation. The
review verifier confirms the exact 32-case roster, unchanged answers, rating
counts, provenance hashes and **72 exact evidence excerpts**. It cannot certify
the assistant's semantic judgments. Human response templates remain blank.
