# Fresh QASPER evaluation dataset

Construction follows the frozen [family reservation](../data/manifests/fresh-evaluation-reservation.json)
and [evaluation protocol](../docs/fresh-evaluation-protocol.md). The new corpus is
separate from v1. [The build record](../docs/fresh-dataset-build.md) distinguishes
implemented checks from executed construction and verification.

## Verified dataset

| Split | Questions | Answerable | Unanswerable | Paper families |
|---|---:|---:|---:|---:|
| Validation (`dev`) | 50 | 38 | 12 | 33 |
| Final test | 100 | 75 | 25 | 72 |
| Total | 150 | 113 | 37 | 105 |

The corpus contains 3,161 aligned paragraphs and 202 query/evidence judgments.
Its fingerprint is `e436aff0b5fb63209ab23faedf393321fa41250ff7bd33264048f2691ae3d9a1`.
The [structured report](fresh-dataset.json) records corpus, label and audit hashes;
[verification metadata](fresh-dataset-verification.json) records the cache rebuild.
Known prior family overlap and full-document Jaccard flags at .85 were zero.
**No model performance has been evaluated on these data.**

## Selection and provenance

The source is the same QASPER v0.3 human-annotated benchmark described in the
[original dataset card](qasper-dataset-card.md). Official dev supplies fresh validation
families and official test supplies fresh final-test families. The reservation
excludes 333 known locally selected, alignment-attempted or cached paper families.
It cannot establish absence from pretrained models' training data or unrecorded
prior inspection.

Families and questions are traversed in predeclared hash order. At most two accepted
questions are retained per paper. Answerability quotas are fixed, and every annotated
evidence paragraph for an answerable question must align to the PDF. Unsupported
annotations and unavailable/invalid PDFs are recorded. Fallback families retain the
same fixed order. No model scores influence inclusion.

The builder preserves human answer alternatives and unanimous answerability rules;
it does not invent negatives or resolve disagreements about answer wording. Source
paragraph IDs use the unchanged v1 recipe. PDF page locations are automatic
alignments, not independently human-verified citations. Test questions/references
are processed by code but are not printed or inspected during construction.

## Reproduction and limitations

```powershell
.venv/Scripts/python.exe -X utf8 scripts/build_fresh_qasper.py --check
```

The check recomputes selection and alignment using checksum-verified caches,
compares the paragraph records and exact label bytes, checks document similarity
against v1 and within the new corpus, and verifies the original release lock.
Its output is aggregate metadata. It neither downloads papers nor runs models.
Paper PDFs and extraction caches remain local and ignored by Git; PDFs are not
redistributed. The public dataset's attribution and PDF rights remain as documented
in the original dataset card.

These are quota-selected, PDF-alignable research-paper questions, not a random
sample of all research questions. Family exclusion, automatic alignment and the
two-question cap change the sampled population. A lack of high-Jaccard duplicate
documents does not exclude subtler topic or semantic overlap. Correctness and
claim-support evaluation are still pending; building labels produces no new model
performance result and does not satisfy independent generated-answer human review.
