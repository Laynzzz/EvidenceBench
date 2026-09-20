# Saved-answer audit: source matching is not answer quality

The offline audit corrects an earlier interpretation: the F1 loss does **not**
show that the GPU checker rejected 24 useful answers. Many rejected outputs are
unfinished or answer a different question. The original seven-condition gate still
fails; no score, label, output or selection is revised.

## Measured facts

- All **28/28** answers match eligible spans in their cited text.
- **13/28** answers reach the 15-word limit; **9/28** cite text at the 1,000-character
  packing boundary. These counts do not establish that either limit caused an error.
- Of **22** answers on answerable questions, **16** had at least one annotated gold
  paragraph packed, but only **9** cited an annotated gold paragraph.
- **19/22** had a span with higher reference-token F1 available within the same
  packed text and existing 15-word span rules. This label-informed diagnostic is
  not a deployable selector, new model score or semantic correctness estimate.
- Recomputed original F1 is .0754244957 and retained F1 .0130679961, using all
  **38 answerable questions**, including refusals. Removed contribution is .0623564996.

## Agent draft review, not independent human evaluation

I reviewed all 28 saved question/answer/citation pairs after seeing benchmark
references and checker decisions: **20 nonresponsive, six partial, one unclear,
one responsive with a possible label conflict**. These are provisional assistant
judgments, not new benchmark labels or checker-accuracy measurements. Of the 24
rejections, 19 are in the nonresponsive group, four partial, and one unclear.
The four retained answers include two partial answers, one tautological answer,
and the label-conflict case. The checker is imperfect in both directions.

Examples explain why the metrics need interpretation:

- Case 24 asks for total dataset size. The answer gives the 1,200 out-of-scope
  subset even though 23,700 total is in the same citation. Its reference F1 is
  .3243: word overlap gives credit to an answer that misses the requested quantity.
- Case 17 asks how human judgments were assembled. The answer is `None`, copied
  from a rating-scale endpoint despite annotator/sample details in the citation.
- Case 1 names two genuine classifiers but omits other baseline components. Its
  rejection can reflect the full-answer requirement, not an unsupported claim.
- Case 28 asks which features the TF-IDF paper uses. The cited text and local
  paper page 3, section B explicitly describe TF-IDF features, while the frozen
  upstream label is unanswerable. This is an adjudication flag, not permission
  to relabel, remove the question, or improve reported scores retrospectively.

Only case 28 received additional local full-paper text inspection in this audit;
other judgments use saved cited passages and supplied references. Full-paper
review and independent human claim-support review remain separate unfinished work.

## Next experiment direction

First isolate answer selection: use the already cached 7B model with the same
32 nonempty packed inputs, question wording, constrained source-span protocol and
15-word limit, preserving the 18 threshold refusals and scoring all 50 questions.
This can test whether a stronger selector uses available evidence better. It cannot
resolve missing evidence, multi-span answers, label conflicts or every limitation
of short extraction. Change context packing or answer format in separate comparisons
rather than confounding them with the model change. Model/runtime differences still
prevent a pure parameter-count attribution. No new model execution is authorized.

## Reproduction and review materials

```powershell
.venv/Scripts/python.exe -X utf8 scripts/audit_gpu_answers.py --check
```

This verifies the frozen run before exact audit recomputation and refuses to
silently overwrite a different report. It performs no inference, but retains the
existing verifier dependency on local checkpoint files and isolated runtime imports.
Eight new synthetic tests cover roster integrity, citation mapping, F1 denominators,
source-span ceilings and persistence. All 133 software tests pass including real
PostgreSQL; code review found no blocking issue. No new training/evaluation calls,
final-test access, downloads or external spending occurred.

[Structured audit](gpu-answer-audit.json) separates measured fields from
[agent draft notes](gpu-answer-review-draft.json). The
[review packet](gpu-answer-review-packet.md) hides model verdicts and reference
labels, and the [human response template](gpu-answer-human-review-template.json)
is blank. Neither artifact counts as completed human review.

## Case-by-case draft rationale

| Case | Checker | Draft response assessment | Rationale |
|---|---|---|---|
| 1 | UNSUPPORTED | partial | Names two classifiers explicitly described in E3, but omits other requested baseline components. Rejection can reflect the full-answer requirement; it is not evidence that these two names are unsupported. |
| 2 | UNSUPPORTED | nonresponsive | An unfinished introduction about social-network data does not describe the corpus experiments. |
| 3 | UNSUPPORTED | nonresponsive | Reports an F1 score and starts another sentence instead of identifying baseline features. |
| 4 | UNSUPPORTED | nonresponsive | A generalization F1 score does not identify the state-of-the-art models requested. |
| 5 | UNSUPPORTED | partial | Mentions CCR, the requested measure, but continues into an unfinished definition. The cited text contains the complete name and definition. |
| 6 | UNSUPPORTED | nonresponsive | Describes crowdworker location and ends before naming a platform; it does not identify NLP toolkits. |
| 7 | UNSUPPORTED | unclear | The question is underspecified and the supplied human reference describes training rather than what zero-shot learning learns. The saved answer is also unfinished. Do not resolve this ambiguity into a checker-error label. |
| 8 | SUPPORTED | partial | Identifies Microsoft stock-price data in the cited passage, but omits tweet-derived features and dataset detail present in the human references. |
| 9 | SUPPORTED | partial | B1 is a real baseline identifier in the citation, but gives no method description and omits other baselines. A supported identifier is not a complete explanation. |
| 10 | UNSUPPORTED | nonresponsive | The fragment The novelty value of does not name the KL-divergence feature, although it is stated earlier in the citation. |
| 11 | UNSUPPORTED | partial | Identifies acquiring a large Vietnamese corpus as one challenge, but stops mid-clause and omits the other challenges. |
| 12 | UNSUPPORTED | nonresponsive | Names social-media platforms when asked for cyberbullying topics. The cited text distinguishes platforms from topics, and truncates the concluding topic list. |
| 13 | UNSUPPORTED | nonresponsive | Describes the EGL sampling method and 100 candidate labels rather than the speech dataset. |
| 14 | UNSUPPORTED | nonresponsive | Gives this submission paper's baseline score, not the methods of the best competition systems. It ends in an incomplete next sentence. |
| 15 | SUPPORTED | nonresponsive | Repeats language model combination technique from the question without identifying the technique, such as the decoding-lattice combination named by the human references. |
| 16 | UNSUPPORTED | nonresponsive | The 0.73 BLEU gain is attributed in the citation to Word2Vec embeddings, not a measurement of attention-mechanism efficacy. This is a relation mismatch despite a matching number. |
| 17 | UNSUPPORTED | nonresponsive | None is one endpoint of an adequacy rating scale, not how human judgments were assembled. The citation explicitly mentions annotators, sample size and rating scales. |
| 18 | UNSUPPORTED | nonresponsive | BPE is the experimental segmentation method applied to baseline data, not an identification of the baseline translation systems. |
| 19 | UNSUPPORTED | partial | The parallel-corpus type is consistent with E1, but the answer omits the dataset name requested; the named WIT3 reference is absent from this cited paragraph. |
| 20 | UNSUPPORTED | nonresponsive | An unfinished sentence about diagnostic results omits even the LRCN1u model named later in the same short citation. |
| 21 | UNSUPPORTED | nonresponsive | Describes the proposed few-shot approach rather than the comparison baseline models. |
| 22 | UNSUPPORTED | nonresponsive | The availability of an implementation does not identify the corrected training dataset. |
| 23 | UNSUPPORTED | nonresponsive | A general statement about low-resource applications does not list the transfer languages. |
| 24 | UNSUPPORTED | nonresponsive | Gives the 1,200-query out-of-scope subset and a dangling Table fragment rather than the 23,700 total explicitly available in the same citation. |
| 25 | UNSUPPORTED | nonresponsive | A statement about using a definition as a reference point does not describe the authors' background. |
| 26 | UNSUPPORTED | nonresponsive | A generic claim about dataset size does not identify a dataset used by these authors. |
| 27 | UNSUPPORTED | nonresponsive | Table does not identify any inflection types. |
| 28 | SUPPORTED | responsive_label_conflict | TF-IDF is explicitly named as the feature representation in the citation and in the locally extracted paper, page 3 section B. The saved upstream unanswerable label appears inconsistent with this question/evidence. The answer also includes unnecessary classifiers wording. Flag for independent adjudication; do not relabel or rescore. |
