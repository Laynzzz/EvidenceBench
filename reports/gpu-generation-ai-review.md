# Paper-grounded AI review of the 24 GPU answers

Status: **completed AI-assisted review**, 2026-09-20. Reviewer: Codex assistant. This is neither independent human review nor a blinded assessment: benchmark references, answerability labels and earlier results were already visible.

Run: `artifacts/gpu-generation-v1/runs/20260920T145452Z-b1abbfbaf5`. Source repository revision: `94685b8`; candidate preparation: `89781c1`.

## Findings

**3 adequate, 11 partial, 8 inadequate and 2 ambiguous answers**, under the rubric below. These counts describe all 24 emitted development answers, not all 50 questions, a held-out sample, or production accuracy. The 26 refusals were not reviewed.

| Judgment | Cases | Count |
|---|---|---:|
| Adequate | 21, 22, 24 | 3 |
| Partial | 1, 2, 3, 6, 7, 8, 10, 12, 14, 16, 18 | 11 |
| Inadequate | 4, 5, 9, 11, 15, 17, 19, 20 | 8 |
| Ambiguous question scope | 13, 23 | 2 |

The dominant problem is selecting the information the question requests. Examples include an F1 score instead of model names (case 5), preprocessing instead of baseline systems (17), and an unnamed existing dataset instead of UMInventory (20). Cases 13 and 23 remain unresolved in scope, and their emitted answers are not adequate under either discussed interpretation.

Citation support is a separate axis: 22 excerpts/claims are supported as literal content, one misattributes the source subject (11), and one has an unclear best-system referent (13). **22/24 is not semantic answer precision.** A copied fragment, a tautology or the wrong kind of fact can be source-grounded and still fail the question. The frozen citation-ID metric (.458333) measures something else and is unchanged.

Three source issues matter: the humor paper alternates 3,543 and 3,453 tweets (2); NCEL's conclusion is broader than its result table warrants (3); and the TF-IDF answer is paper-supported despite the benchmark unanswerable label (24). The Spanish humor paper supplies ranks and classification scores but no numeric regression result in its results section (14); none has been invented.

## Method and limits

Read the actual emitted citation for support, then relevant sections of the corresponding local PDF for question-level correctness and corrections. Page numbers below are **one-based physical PDF pages**. Cached page extractions were used for text search; six rendered pages were visually checked to resolve tables, numbers and morphology examples: 1806.05513 pp. 2/4, 1610.08815 p. 9, 1811.08603 p. 8, 1907.03187 p. 7 and 1809.01541 p. 2.

All 16 PDFs match the hashes recorded by the completed experiment. The structured review preserves exact questions, outputs, citations, source hashes, page references, judgments and frozen reference metadata. No benchmark label, prediction, model setting or metric was changed. Suggested answers are editorial corrections from full papers, not new model outputs; they may exceed the old source-span/15-word contract and need replacement citations.

The verdicts are conservative editorial judgments rather than an objective new benchmark. In particular, cases 1 and 8 depend on singular-versus-study-wide scope, case 6 on whether a metric stem is sufficient, and case 14 on whether ranks alone satisfy results. Those sensitivities are recorded individually. No inter-rater agreement or independent human validation is claimed.

### Rubric

- **answer adequacy:** adequate: answers the requested information correctly; partial: useful requested information but missing detail or needing qualification; inadequate: wrong referent, wrong answer type or no requested information; ambiguous: question scope prevents a unique judgment, with emitted deficiencies explained.
- **responsiveness:** responsive / partial / nonresponsive / unclear; whether the response addresses what was asked.
- **completeness:** complete / partial / missing / unclear; requested information coverage, independent of truth.
- **cited support:** supported / unsupported / unclear for the emitted literal content with source referents preserved. A supported fragment or score can still be a useless answer. This is NOT complete-answer support or benchmark citation-ID precision. Pronoun misattribution is unsupported; an unspecified best-system referent is unclear.
- **paper correctness:** correct / partially_correct / incorrect / ambiguous as an answer to this question. Incorrect includes wrong answer types and tautological nonanswers, even if the isolated words are true.

## Project implication

The previously passed development gate is still a real recorded result, but it does not establish useful complete answers. Keep the candidate development-only. Future preparation should prioritize question-type-aware answer selection, complete lists/method names, and sufficient answer length, while recording those as separate changes to the frozen protocol. Source inconsistencies and annotation conflicts should remain explicit review notes. A new model run needs its own proposal and approval; none was launched here.

The requested assistant review is complete. The plan's independent-human criterion remains unfulfilled, not silently waived or relabeled. There is no request for the user to repeat this review now.

## Per-case review

### Case 1: partial

Query ID: `dea9e7fe8e47da5e7f31d9b1a46ebe34e731a596`

**Question:** In the paper 'Humor Detection in English-Hindi Code-Mixed Social Media Content : Corpus and Baseline System', What type of system does the baseline classification use?

**Emitted answer:** support vector machines with radial basis function kernel

**Judgments:** responsiveness partial; completeness partial; cited support supported; paper correctness as an answer partially_correct.

**Paper evidence:** [1806.05513.pdf](../data/raw/qasper-fresh-v1/1806.05513.pdf) — PDF pages 1, 2, 3, 4. The emitted citation corresponds to page(s) 4.

RBF-SVM is a real classifier and the best reported configuration, so the citation supports the selected system. Section 3.3 describes four classifiers, however. The answer identifies one member rather than the overall supervised humor-classification setup.

**Suggested answer:** A supervised humor classifier using n-grams, bag-of-words, common words and hashtags; the experiments compare RBF-SVM, random forest, extra trees and naive Bayes. RBF-SVM gives the best reported accuracy, 69.3%.

**Qualification:** If the singular question is interpreted as asking only for the best classifier, this short answer is adequate. The broader baseline-system reading used here yields partial.

### Case 2: partial

Query ID: `955cbea7e5ead36fb89cd6229a97ccb3febcf8bc`

**Question:** In the paper 'Humor Detection in English-Hindi Code-Mixed Social Media Content : Corpus and Baseline System', What experiments were carried out on the corpus?

**Emitted answer:** 10-fold cross validation on 3543 code-mixed tweets was carried out

**Judgments:** responsiveness partial; completeness partial; cited support supported; paper correctness as an answer partially_correct.

**Paper evidence:** [1806.05513.pdf](../data/raw/qasper-fresh-v1/1806.05513.pdf) — PDF pages 1, 2, 3, 4. The emitted citation corresponds to page(s) 4.

It gives the cross-validation protocol but omits the actual task: humorous versus non-humorous tweet classification with feature/classifier comparisons. The cited results section says 3,543, while the conclusion says 3,453 and Table 1 totals 1,755 + 1,698 = 3,453. Both conflicting numbers are visible in the PDF.

**Suggested answer:** They evaluated humor/non-humor classification with four classifiers and several feature sets using ten-fold cross-validation and mean accuracy. The paper inconsistently reports the corpus size as 3,543 and 3,453.

**Qualification:** Do not silently replace the generated number or call it a hallucination: its cited passage really says 3,543. The inconsistency is in the paper.

### Case 3: partial

Query ID: `114934e1a1e818630ff33ac5c4cd4be6c6f75bb2`

**Question:** In the paper 'Neural Collective Entity Linking', How effective is their NCEL approach overall?

**Emitted answer:** Trained on collected Wikipedia hyperlinks, NCEL outperforms the state-of-the-art collective methods across five different datasets

**Judgments:** responsiveness responsive; completeness complete; cited support supported; paper correctness as an answer partially_correct.

**Paper evidence:** [1811.08603.pdf](../data/raw/qasper-fresh-v1/1811.08603.pdf) — PDF pages 7, 8, 9, 10. The emitted citation corresponds to page(s) 10.

The emitted sentence matches the conclusion, but its unqualified superiority claim is stronger than Table 1. NCEL has ACE2004 macro-F1 .89 versus WNED .90; CoNLL-TestA micro-F1 .79 versus PBoH .80; other entries tie. The paper reports best performance in most cases and better averages, not a strict win for every metric/dataset.

**Suggested answer:** NCEL performs strongly across five datasets, with the best GERBIL average micro- and macro-F1 (.84 each), and wins on WW and TAC2010; individual GERBIL results include ties and losses.

**Qualification:** Supported by the cited conclusion does not mean fully justified by all experimental evidence. This is a qualification issue, not missing numerical detail alone.

### Case 4: inadequate

Query ID: `1beb4a590fa6127a138f4ed1dd13d5d51cc96809`

**Question:** In the paper 'A Deeper Look into Sarcastic Tweets Using Deep Convolutional Neural Networks', What are the network's baseline features?

**Emitted answer:** Baseline features have performed significantly better (F1-score: 92.32%) than all other features. Supporting the observations

**Judgments:** responsiveness nonresponsive; completeness missing; cited support supported; paper correctness as an answer incorrect.

**Paper evidence:** [1610.08815.pdf](../data/raw/qasper-fresh-v1/1610.08815.pdf) — PDF pages 6, 7, 8, 9. The emitted citation corresponds to page(s) 8.

The answer reports an F1 result rather than identifying the baseline features. Section 4.5 defines them as the learned features from a CNN trained on the sarcasm corpus; the fully connected layer supplies 100 features.

**Suggested answer:** The baseline features are the 100-dimensional fully connected representation learned by a CNN trained to distinguish sarcastic from non-sarcastic tweets.

**Qualification:** The 92.32% figure is grounded in the cited results, but a true score is not an answer to a feature-identification question.

### Case 5: inadequate

Query ID: `3a6e843c6c81244c14730295cfb8b865cd7ede46`

**Question:** In the paper 'A Deeper Look into Sarcastic Tweets Using Deep Convolutional Neural Networks', What are the state of the art models?

**Emitted answer:** F1-score: 92.37%

**Judgments:** responsiveness nonresponsive; completeness missing; cited support supported; paper correctness as an answer incorrect.

**Paper evidence:** [1610.08815.pdf](../data/raw/qasper-fresh-v1/1610.08815.pdf) — PDF pages 2, 3, 8, 9. The emitted citation corresponds to page(s) 8.

A score is returned where model identities are requested. Table 3 compares the methods of Ptacek et al. (2014) and Joshi et al. (2015); 92.37% belongs to Ptacek on Dataset 2.

**Suggested answer:** The comparison methods are Ptacek et al. (2014), using n-gram/word-shape/punctuation features, and Joshi et al. (2015), using contextual incongruity with lexical and pragmatic features.

**Qualification:** The full PDF resolves the BIBREF placeholder in the retrieved passage. The isolated score is real but does not name either approach.

### Case 6: partial

Query ID: `58c6737070ef559e9220a8d08adc481fdcd53a24`

**Question:** In the paper 'Performance Comparison of Crowdworkers and NLP Tools onNamed-Entity Recognition and Sentiment Analysis of Political Tweets', What measures are used for evaluation?

**Emitted answer:** We report the experimental results for our two tasks in terms of the correct classification

**Judgments:** responsiveness partial; completeness partial; cited support supported; paper correctness as an answer partially_correct.

**Paper evidence:** [2002.04181.pdf](../data/raw/qasper-fresh-v1/2002.04181.pdf) — PDF pages 2, 3. The emitted citation corresponds to page(s) 2.

The response reaches the words correct classification but stops before rate (CCR), so it never finishes naming the metric. The complete metric and its task-specific definitions are immediately present in the cited paragraph.

**Suggested answer:** Correct classification rate (CCR): correctly predicted sentiments or entities divided by the corresponding ground-truth counts, as defined for each task.

**Qualification:** Partial credit recognizes the identifiable metric stem. A stricter answerability rubric could mark the unfinished phrase inadequate; it is not a complete metric name.

### Case 7: partial

Query ID: `9b7655d39c7a19a23eb8944568eb5618042b9026`

**Question:** In the paper 'Performance Comparison of Crowdworkers and NLP Tools onNamed-Entity Recognition and Sentiment Analysis of Political Tweets', Which toolkits do they use?

**Emitted answer:** TensiStrength

**Judgments:** responsiveness partial; completeness partial; cited support supported; paper correctness as an answer partially_correct.

**Paper evidence:** [2002.04181.pdf](../data/raw/qasper-fresh-v1/2002.04181.pdf) — PDF pages 2, 3. The emitted citation corresponds to page(s) 2.

TensiStrength is one of seven evaluated toolkits. It omits the other six. The PDF resolves the commercial/API names hidden behind BIBREF placeholders in the packed text.

**Suggested answer:** TensiStrength, Google Cloud Natural Language, Rosette Text Analytics, TwitterNLP, spaCy, CogComp-NLP and Stanford NER; their use differs between sentiment analysis and NER.

**Qualification:** The paper mentions other commercial products as background; AYLIEN, MS Text Analytics and IBM Watson are not part of the seven evaluated tools.

### Case 8: partial

Query ID: `2ee715c7c6289669f11a79743a6b2b696073805d`

**Question:** In the paper 'Automated News Suggestions for Populating Wikipedia Entity Pages', What baseline model is used?

**Emitted answer:** B1. The first baseline uses only the salience-based features by Dunietz and Gillick

**Judgments:** responsiveness partial; completeness partial; cited support supported; paper correctness as an answer partially_correct.

**Paper evidence:** [1703.10344.pdf](../data/raw/qasper-fresh-v1/1703.10344.pdf) — PDF pages 8, 9. The emitted citation corresponds to page(s) 8.

It correctly identifies B1, one article-entity placement baseline. The study also has B2 and two article-section baselines, so this is incomplete under a study-wide reading.

**Suggested answer:** For article-entity placement: B1 uses Dunietz and Gillick salience features; B2 accepts entities appearing in the article title. For article-section placement: S1 chooses highest lexical similarity and S2 the most frequent section.

**Qualification:** The singular wording is underspecified. If only B1 was intended, the emitted answer is adequate; the paper-wide review marks partial and retains that uncertainty.

### Case 9: inadequate

Query ID: `984fc3e726848f8f13dfe72b89e3770d00c3a1af`

**Question:** In the paper 'Automated News Suggestions for Populating Wikipedia Entity Pages', What features are used to represent the novelty of news articles to entity pages?

**Emitted answer:** novelty of news articles for an entity page

**Judgments:** responsiveness nonresponsive; completeness missing; cited support supported; paper correctness as an answer incorrect.

**Paper evidence:** [1703.10344.pdf](../data/raw/qasper-fresh-v1/1703.10344.pdf) — PDF pages 5, 10. The emitted citation corresponds to page(s) 10.

The phrase repeats the property named in the question without explaining how it is represented. Section 4.1.3 describes KL divergence between article language models combined with entity overlap, compared against previously referenced articles.

**Suggested answer:** Novelty combines language-model KL divergence with entity overlap against existing news references, using the minimum comparison value over previous articles.

**Qualification:** The conclusion supports the generic term novelty but not the requested feature definition. The suggested answer requires a different source passage on page 5.

### Case 10: partial

Query ID: `5c6fa86757410aee6f5a0762328637de03a569e9`

**Question:** In the paper 'Deep Learning for Detecting Cyberbullying Across Multiple Social Media Platforms', What were their performance results?

**Emitted answer:** DNN based models coupled with transfer learning beat the best-known results for all three datasets

**Judgments:** responsiveness partial; completeness partial; cited support supported; paper correctness as an answer partially_correct.

**Paper evidence:** [1801.06482.pdf](../data/raw/qasper-fresh-v1/1801.06482.pdf) — PDF pages 2, 3, 7, 8, 9, 10. The emitted citation corresponds to page(s) 10.

This is a supported qualitative summary, but it omits the reported performance numbers available in the same citation. The paper distinguishes F1 from accuracy and notes that prior Formspring work did not report F1.

**Suggested answer:** The paper reports F1 .94 on Wikipedia and Twitter, and F1 .95 with accuracy .98 on Formspring using deep models and transfer learning.

**Qualification:** These are the authors' historical reported results, not a current state-of-the-art claim or a revalidation of their experimental protocol.

### Case 11: inadequate

Query ID: `7e38e0279a620d3df05ab9b5e2795044f18d4471`

**Question:** In the paper 'Deep Learning for Detecting Cyberbullying Across Multiple Social Media Platforms', What cyberbulling topics did they address?

**Emitted answer:** Second, they address just one topic of cyberbullying. Third, they rely on carefully handcrafted features

**Judgments:** responsiveness nonresponsive; completeness missing; cited support unsupported; paper correctness as an answer incorrect.

**Paper evidence:** [1801.06482.pdf](../data/raw/qasper-fresh-v1/1801.06482.pdf) — PDF pages 1, 2, 3. The emitted citation corresponds to page(s) 1.

The selected they refers to existing works in the abstract, not the authors' proposed system. Used as an answer about this paper, the excerpt misattributes a limitation of prior work and never supplies any topic.

**Suggested answer:** They address personal attacks, racism and sexism. Wikipedia covers personal attacks, Twitter covers racism/sexism, and Formspring is not restricted to one topic.

**Qualification:** Verbatim copying does not preserve support when a pronoun is attached to the wrong subject.

### Case 12: partial

Query ID: `551457ed34ca7fc0878c85bc664b135c21059b58`

**Question:** In the paper 'Active Learning for Speech Recognition: the Power of Gradients', Which dataset do they use?

**Emitted answer:** 190 hours

**Judgments:** responsiveness partial; completeness partial; cited support supported; paper correctness as an answer partially_correct.

**Paper evidence:** [1612.03226.pdf](../data/raw/qasper-fresh-v1/1612.03226.pdf) — PDF pages 3. The emitted citation corresponds to page(s) 3.

190 hours is the labeled base-training subset size, not a dataset identity or a description of the complete setup. The passage describes transcribed speech, an unlabeled pool, validation instances and a separate test set.

**Suggested answer:** The setup uses 190 hours of transcribed speech, a 1,700-hour unlabeled pool, 2,048 validation instances and a 156-hour test set; the cited setup does not name a public benchmark.

**Qualification:** Do not infer a corpus name or language from the model's Deep Speech citation. The saved reference emphasizes sizes, but that does not make the two-word response self-contained.

### Case 13: ambiguous

Query ID: `b7c3f3942a07c118e57130bc4c3ec4adc431d725`

**Question:** In the paper 'Applying a Pre-trained Language Model to Spanish Twitter Humor Prediction', What did the best systems use for their model?

**Emitted answer:** We tied the embedding weights

**Judgments:** responsiveness unclear; completeness unclear; cited support unclear; paper correctness as an answer ambiguous.

**Paper evidence:** [1907.03187.pdf](../data/raw/qasper-fresh-v1/1907.03187.pdf) — PDF pages 1, 2, 3, 4, 5, 6, 7, 8. The emitted citation corresponds to page(s) 4.

Tied embeddings are a detail of the authors' own model. The question does not identify whether best systems means their selected runs or the winning competitors. The paper describes its own QRNN-based ULMFiT variant and reports its ranks, but does not establish the architectures of the first-place competitors.

**Suggested answer:** If referring to this submission: a ULMFiT-style model with QRNN units, tied encoder/decoder embeddings and task-specific heads. If referring to the competition winners: their architectures are not established in this paper.

**Qualification:** The benchmark marks this unanswerable. Retain that label; the source supports tied embeddings for the authors, not the unspecified best systems. This is not an adequate answer under either reading.

### Case 14: partial

Query ID: `a5505e25ee9ae84090e1442034ddbb3cedabcf04`

**Question:** In the paper 'Applying a Pre-trained Language Model to Spanish Twitter Humor Prediction', What were their results on the classification and regression tasks

**Emitted answer:** Our entry into the HAHA 2019 Challenge placed $3^{rd}$ in the classification task and $2^{nd}$

**Judgments:** responsiveness partial; completeness partial; cited support supported; paper correctness as an answer partially_correct.

**Paper evidence:** [1907.03187.pdf](../data/raw/qasper-fresh-v1/1907.03187.pdf) — PDF pages 1, 4, 5, 6, 7. The emitted citation corresponds to page(s) 1.

It gives the correct classification rank and begins the regression rank, but omits in the regression task and the available classification metrics. Table 3 reports test F1 .8099; the results text and conclusion give second place for regression without a numeric regression result.

**Suggested answer:** Third in classification with test F1 .8099 (accuracy .8458, precision .7806, recall .8416), and second in regression. A numeric regression score is not supplied in the reported results.

**Qualification:** Do not invent an RMSE value. Under a ranks-only reading the intended information is largely recoverable, but the emitted sentence remains unfinished.

### Case 15: inadequate

Query ID: `fe1dcd6ef1f8618bbceee418f07cafe63a8efe08`

**Question:** In the paper 'VAIS ASR: Building a conversational speech recognition system using language model combination', What is the language model combination technique used in the paper?

**Emitted answer:** language models combination techniques

**Judgments:** responsiveness nonresponsive; completeness missing; cited support supported; paper correctness as an answer incorrect.

**Paper evidence:** [1910.05603.pdf](../data/raw/qasper-fresh-v1/1910.05603.pdf) — PDF pages 1, 2. The emitted citation corresponds to page(s) 1.

The response merely restates language model combination. Section II.B describes combining domain n-gram models based on perplexity on a small target-domain text; Section IV.C additionally combines general and conversational systems at the decoding-lattice level.

**Suggested answer:** Domain n-gram models are combined using target-domain perplexity; general and conversational systems are then combined at decoding-lattice level, with general:conversation weights .6:.4 for VLSP2018 and .7:.3 for VLSP2019.

**Qualification:** This is lattice/system combination, not an unsupported assertion about interpolating model parameters. The method details need page 2, beyond the emitted abstract citation.

### Case 16: partial

Query ID: `0ee73909ac638903da4a0e5565c8571fc794ab96`

**Question:** In the paper 'Improving the Performance of Neural Machine Translation Involving Morphologically Rich Languages', How were the human judgements assembled?

**Emitted answer:** A group of 50 native people who were well-versed in both English and Tamil languages

**Judgments:** responsiveness partial; completeness partial; cited support supported; paper correctness as an answer partially_correct.

**Paper evidence:** [1612.02482.pdf](../data/raw/qasper-fresh-v1/1612.02482.pdf) — PDF pages 11. The emitted citation corresponds to page(s) 11.

The answer identifies the annotators but leaves out how judgments were collected. Section 5.2 describes about 100 randomly selected translation outputs, five-point adequacy and fluency scales, and relative rankings allowing ties.

**Suggested answer:** Fifty English/Tamil-proficient native annotators judged about 100 randomly selected translations, using five-point adequacy and fluency ratings and pairwise relative rankings with ties allowed.

**Qualification:** The full PDF supplies the end of the procedure that is truncated in the packed passage; it does not retroactively make the generated response complete.

### Case 17: inadequate

Query ID: `e35a7f9513ff1cc0f0520f1d4ad9168a47dc18bb`

**Question:** In the paper 'Combining Advanced Methods in Japanese-Vietnamese Neural Machine Translation', what was the baseline?

**Emitted answer:** For the baseline systems, the training data includes KyTea-segmented Japanese texts and pyvi-segmented Vietnamese texts

**Judgments:** responsiveness nonresponsive; completeness missing; cited support supported; paper correctness as an answer incorrect.

**Paper evidence:** [1805.07133.pdf](../data/raw/qasper-fresh-v1/1805.07133.pdf) — PDF pages 5, 6. The emitted citation corresponds to page(s) 5.

The response describes preprocessing of the baseline training data without identifying the baseline systems. The next sentence in its own cited paragraph gives the needed answer: phrase-based SMT and NMT in each translation direction.

**Suggested answer:** A phrase-based statistical machine translation system and an NMT system for each direction, trained on KyTea-segmented Japanese and pyvi-segmented Vietnamese.

**Qualification:** The preprocessing statement is true, but it is the wrong answer type for which baseline.

### Case 18: partial

Query ID: `219af68afeaecabdfd279f439f10ba7c231736e4`

**Question:** In the paper 'Combining Advanced Methods in Japanese-Vietnamese Neural Machine Translation', what japanese-vietnamese dataset do they use?

**Emitted answer:** Japanese-Vietnamese parallel corpus

**Judgments:** responsiveness partial; completeness partial; cited support supported; paper correctness as an answer partially_correct.

**Paper evidence:** [1805.07133.pdf](../data/raw/qasper-fresh-v1/1805.07133.pdf) — PDF pages 5, 6. The emitted citation corresponds to page(s) 5.

Japanese-Vietnamese parallel corpus gives only the language pair and data type already requested. Section V.A identifies TED talks extracted from WIT3, with 106,758 cleaned sentence pairs.

**Suggested answer:** Japanese-Vietnamese TED-talk parallel data extracted from WIT3: 106,758 training sentence pairs, with dev2010 for validation and tst2010 for testing.

**Qualification:** The citation discusses augmentation and does not name WIT3. The full-paper correction requires citing the data-collection paragraph, not reusing the generic excerpt as if it named the dataset.

### Case 19: inadequate

Query ID: `3116453e35352a3a90ee5b12246dc7f2e60cfc59`

**Question:** In the paper 'A Neural Topic-Attention Model for Medical Term Abbreviation Disambiguation', To what baseline models is proposed model compared?

**Emitted answer:** We applied traditional features by simply taking the TF-IDF features as the inputs into the

**Judgments:** responsiveness nonresponsive; completeness missing; cited support supported; paper correctness as an answer incorrect.

**Paper evidence:** [1910.14076.pdf](../data/raw/qasper-fresh-v1/1910.14076.pdf) — PDF pages 3, 4. The emitted citation corresponds to page(s) 3.

The unfinished sentence names a feature representation but none of the baseline models. Section 3 explicitly lists four classical classifiers and four neural baselines.

**Suggested answer:** TF-IDF with SVM, logistic regression, naive Bayes and random forest; plus CNN, LSTM, LSTM with soft attention and LSTM with self-attention.

**Qualification:** TF-IDF is an input representation, not a replacement for the requested classifier identities.

### Case 20: inadequate

Query ID: `a9a532399237b514c1227f2d6be8601474e669be`

**Question:** In the paper 'A Neural Topic-Attention Model for Medical Term Abbreviation Disambiguation', What existing dataset is re-examined and corrected for training?

**Emitted answer:** We re-examine and correct an existing dataset for training and collect a test set to

**Judgments:** responsiveness nonresponsive; completeness missing; cited support supported; paper correctness as an answer incorrect.

**Paper evidence:** [1910.14076.pdf](../data/raw/qasper-fresh-v1/1910.14076.pdf) — PDF pages 1, 2. The emitted citation corresponds to page(s) 1.

The response repeats that an existing dataset was corrected without identifying it. Section 2 names UMInventory, created by University of Minnesota researchers; the authors remove erroneous samples and select 30 abbreviation terms.

**Suggested answer:** UMInventory, the University of Minnesota clinical abbreviation dataset, cleaned to remove erroneous samples and retain 30 abbreviation terms.

**Qualification:** The abstract citation cannot support the missing dataset name; the correction needs the dataset section on page 2.

### Case 21: adequate

Query ID: `ce2b921e4442a21555d65d8ce4ef7e3bde931dfc`

**Question:** In the paper 'From English To Foreign Languages: Transferring Pre-trained Language Models', What languages are the model transferred to?

**Emitted answer:** French (fr), Russian (ru), Arabic (ar), Chinese (zh), Hindi (hi), and Vietnamese (vi). These languages

**Judgments:** responsiveness responsive; completeness complete; cited support supported; paper correctness as an answer correct.

**Paper evidence:** [2002.07306.pdf](../data/raw/qasper-fresh-v1/2002.07306.pdf) — PDF pages 4. The emitted citation corresponds to page(s) 4.

All six target languages are correctly listed in the cited paragraph and in the paper's data section. The trailing words These languages are a formatting defect but do not omit or alter any requested language.

**Suggested answer:** French, Russian, Arabic, Chinese, Hindi and Vietnamese.

**Qualification:** A cosmetic trailing fragment is recorded without treating it as a substantive factual failure.

### Case 22: adequate

Query ID: `27de1d499348e17fec324d0ef00361a490659988`

**Question:** In the paper 'An Evaluation Dataset for Intent Classification and Out-of-Scope Prediction', What is the size of this dataset?

**Emitted answer:** 23,700 queries

**Judgments:** responsiveness responsive; completeness complete; cited support supported; paper correctness as an answer correct.

**Paper evidence:** [1909.02027.pdf](../data/raw/qasper-fresh-v1/1909.02027.pdf) — PDF pages 2, 5. The emitted citation corresponds to page(s) 2.

23,700 queries directly answers the size question. Section 2 gives 22,500 in-scope plus 1,200 out-of-scope queries, and Table 4 repeats the total.

**Suggested answer:** 23,700 queries: 22,500 in-scope and 1,200 out-of-scope.

**Qualification:** This is the full dataset size, not just the training split or number of intents.

### Case 23: ambiguous

Query ID: `c9b8d3858c112859eabee54248b874331c48f71b`

**Question:** In the paper 'Copenhagen at CoNLL--SIGMORPHON 2018: Multilingual Inflection in Context with Explicit Morphosyntactic Decoding', What type of inflections are considered?

**Emitted answer:** inflected word form

**Judgments:** responsiveness unclear; completeness unclear; cited support supported; paper correctness as an answer ambiguous.

**Paper evidence:** [1809.01541.pdf](../data/raw/qasper-fresh-v1/1809.01541.pdf) — PDF pages 1, 2, 3, 4, 5. The emitted citation corresponds to page(s) 1.

Inflected word form names the output without specifying a type. The question could mean contextual versus context-agnostic inflection, or specific morphological categories. Page 1 establishes contextual morphological (re)inflection; Table 1 illustrates made with V;PST;V.PTCP;PASS, but an example is not an exhaustive category inventory.

**Suggested answer:** The task is morphological inflection in context: generate a word form from a lemma and its sentence context. If a complete list of inflection categories is intended, the paper does not establish such an inventory in the inspected task description.

**Qualification:** Retain the frozen unanswerable label and document the scope ambiguity. The emitted generic phrase is inadequate under both readings; do not infer a complete category list from one example.

### Case 24: adequate

Query ID: `1eef2d2c296fdd10b08bf7b4ff7792cccf177d3b`

**Question:** In the paper 'Automatic Classification of Pathology Reports using TF-IDF Features', What features are used?

**Emitted answer:** TF-IDF features

**Judgments:** responsiveness responsive; completeness complete; cited support supported; paper correctness as an answer correct.

**Paper evidence:** [1903.07406.pdf](../data/raw/qasper-fresh-v1/1903.07406.pdf) — PDF pages 3. The emitted citation corresponds to page(s) 3.

TF-IDF features correctly identifies the classification representation. Section III.B defines the term-weight vector and III.E says it is used for classifier training. LDA is used separately for topic grouping of keywords.

**Suggested answer:** TF-IDF-weighted term vectors extracted from the preprocessed pathology reports.

**Qualification:** The frozen benchmark row says unanswerable, creating a paper/annotation conflict. Preserve its reference label and all official scores; record this separately rather than silently granting benchmark credit.

## Evidence and verification

[Structured AI review](gpu-generation-ai-review.json) includes source/output hashes and all judgments. [Verification record](gpu-generation-ai-review-verification.json) records exact roster/answer/citation checks and unchanged frozen artifacts. The original [human packet](gpu-generation-human-review.md) and [blank human template](gpu-generation-human-review-template.json) remain untouched. [Original results](gpu-generation-development.md) remain the authoritative experiment metrics.

Verification here is document/provenance checking, not model evaluation or rerunning the software test suite. No training, new model inference, final-test access or external model-service spend occurred.
