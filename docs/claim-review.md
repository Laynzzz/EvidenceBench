# Paper-based claim review — all nine generated answers

Reviewer: **Codex (AI-assisted review)**

Date: **2026-09-19**

Status: **completed AI review; not human-reviewed**

Completed at the user's request against the corresponding original papers. All nine local PDFs match their frozen source-manifest SHA-256 hashes. Relevant sections were inspected in extracted full-paper text, with visual checks of the embedding comparison table and the caption annotation procedure. Original model-visible excerpts are retained below. Source fingerprints and structured judgments are in [the review JSON](../reports/claim-review-ai.json).

## Method and limits

- **Claim support** evaluates whether the emitted citations support the complete answer *to the question*: supported / unsupported / unclear. A true number can still be unsupported as a complete answer when the question asks for a method or a list. This label does not necessarily mean a fabricated fact. Unclear means the evidence leaves the requested property unresolved.
- **Answer correctness** is judged against the paper: correct / incorrect / ambiguous. Ambiguous preserves uncertainty about question scope or an unstated property. Original human references are retained and compared separately; agreement with a reference is not proof of paper correctness.
- **Citation verdicts** use supports / does not support / unclear for each emitted citation. Context from other jointly emitted citations may resolve a term; such cases are explicitly noted. This is not a standalone-passage precision metric. Full-paper material outside the emitted citations can establish correctness but cannot retroactively ground a citation.
- This is a single AI review after the frozen test, not independent human adjudication. The original human semantic-review criterion in plan.md sections 11–12 remains unmet. The user's requested AI review is complete and needs no further user action.
- Scope is all **9 answered outputs and 16 citation links**, from 100 test queries with 46 refusals and 45 failures. Rates below are conditional on emitted answers, not all-query accuracy, and are not generalizable quality estimates. No reference labels, predictions, metrics, models, prompts or thresholds were changed, and these observations must not be used to tune on this test set.

## Findings

| Measure | AI judgment count |
|---|---:|
| Complete answer supported by emitted citations | 2 / 9 (22.2%) |
| Complete answer unsupported by emitted citations | 6 / 9 (66.7%) |
| Claim support unclear | 1 / 9 (11.1%) |
| Paper-based correctness | 2 correct; 4 incorrect; 3 ambiguous |
| Citation judgments, allowing stated joint context | 4 support; 11 do not support; 1 unclear (16 total) |

The two clearly correct, supported answers concern LSA features and pretrained GloVe embeddings. Four incorrect answers substitute a score, a broad approach, a count, or the proposed method for the requested information. Three cases require qualifications about representativeness, crowdsourcing, or which publication is meant. The LSA paper resolves conflicting references; the captioning and embedding-comparison cases raise separate annotation/scope concerns. These findings explain limitations of the existing benchmark metrics without replacing them.

## 1. e9a0a69eacd554141f56b60ab2d1912cc33f526a

In the paper 'Sentiment Analysis of Code-Mixed Indian Languages: An Overview of SAIL_Code-Mixed Shared Task @ICON-2017', what was the baseline?

Generated answer: **0.331**

Upstream human reference: Random labeling | Alternative human answer:  randomly assigning any of the sentiment values to each of the test instances

Claim support: **unsupported**

Answer correctness against the paper: **incorrect**

Citation verdicts:

- **E1: does not support** — E1 establishes the baseline score, but a score alone does not answer which baseline method was used.

**Paper-based reasoning:** The question asks for the baseline method. Section 4.1 (PDF p. 5) specifies random sentiment-label assignment. The returned 0.331 is a real Hindi-English macro F-score, also reported in Table 2 and the conclusion, but does not identify that method. This is a nonresponsive extraction, not a fabricated number.

**Suggested answer:** The baseline randomly assigned sentiment labels to test instances; its macro F-scores were 0.331 for Hindi-English and 0.339 for Bengali-English.

**Reference comparison:** The paper supports the random-labeling references; the generated score does not answer their method question.

**Paper locations checked:** [PDF p. 5](https://arxiv.org/pdf/1803.06745#page=5), [PDF p. 6](https://arxiv.org/pdf/1803.06745#page=6), [PDF p. 8](https://arxiv.org/pdf/1803.06745#page=8). Page numbers are one-based PDF pages, not necessarily printed page labels.

### E1: source page 8–8

[Original source](https://arxiv.org/pdf/1803.06745) — evidence `750ee7dbec733ad32260d15cd6e0f9773e800348b49f74ca8642c2e0769b0a28`

> Sentiment Analysis of Code-Mixed Indian Languages: An Overview of SAIL_Code-Mixed Shared Task @ICON-2017
> This paper presents the details of shared task held during the ICON 2017. The competition presents the sentiment identification task from HI-EN and BN-EN code-mixed datasets. A random baseline system obtained macro average f-score of 0.331 and 0.339 for HI-EN and BN-EN datasets, respectively. The best performing team obtained maximum macro average f-score of 0.569 and 0.526 for HI-EN and BN-EN datasets, respectively. The team used word and character level n-grams as features and SVM for sentiment classification. We plan to enhance the current dataset and include more data pairs in the next version of the shared task. In future, more advanced task like aspect based sentiment analysis and stance detection can be performed on code-mixed dataset.

## 2. 36cb7ebdd39e0b8a89ff946d3a3aef8a76a6bb43

In the paper 'Gender Prediction from Tweets: Improving Neural Representations with Hand-Crafted Features', Are LSA-reduced n-gram features considered hand-crafted features?

Generated answer: **Yes**

Upstream human reference: Yes | Alternative human answer: No

Claim support: **supported**

Answer correctness against the paper: **correct**

Citation verdicts:

- **E1: does not support** — E1 describes prior LSA n-gram work but does not establish the hand-crafted designation.
- **E2: supports** — E2 directly identifies the hand-crafted extension as LSA-reduced n-gram features.
- **E3: supports** — E3 identifies the n-gram extension as hand-crafted; the LSA qualifier is supplied by the jointly cited E2. This is contextual support, not standalone proof of that qualifier.

**Paper-based reasoning:** The introduction explicitly connects the added hand-crafted features to LSA-reduced n-grams. Section 4, Conclusion (PDF p. 7), states the same relationship directly. The paper therefore supports Yes despite the conflicting Yes/No annotations.

**Suggested answer:** Yes. The authors call the LSA-reduced n-gram features hand-crafted and concatenate them with the learned RNN representation.

**Reference comparison:** Matches Yes, conflicts with No. The full paper resolves the substantive question in favor of Yes; both original annotations remain unchanged.

**Paper locations checked:** [PDF p. 2](https://arxiv.org/pdf/1908.09919#page=2), [PDF p. 5](https://arxiv.org/pdf/1908.09919#page=5), [PDF p. 7](https://arxiv.org/pdf/1908.09919#page=7). Page numbers are one-based PDF pages, not necessarily printed page labels.

### E1: source page 1–1

[Original source](https://arxiv.org/pdf/1908.09919) — evidence `559945c2c28180439979be43d7f20449135f154a8b17fccb7d1de1009678b7f5`

> Gender Prediction from Tweets: Improving Neural Representations with Hand-Crafted Features
> Most of the work on gender prediction rely on n-gram features BIBREF2. BIBREF3 give Latent Semantic Analysis (LSA)-reduced forms of word and character n-grams into Support Vector Machine (SVM) and achieve state-of-the-art performance. Apart from exploiting n-gram frequencies, there are studies BIBREF4, BIBREF5, BIBREF6 to extract cross-lingual features to determine gender from tweets. Some other work BIBREF4, BIBREF7 exploit user metadata besides using just tweets.

### E2: source page 2–2

[Original source](https://arxiv.org/pdf/1908.09919) — evidence `1b48556e83a1b5450a706095378b076cfd407d1012320a0eb47b050fa66b8660`

> Gender Prediction from Tweets: Improving Neural Representations with Hand-Crafted Features
> In this work, we propose a model that relies on RNN with attention mechanism (RNNwA). A bidirectional RNN with attention mechanism both on word level and tweet level is trained with word embeddings. The final representation of the user is fed to a fully connected layer for prediction. Since combining some hand-crafted features with a learned linear layer has shown to perform well in complex tasks like Semantic Role Labeling (SRL) BIBREF14, an improved version of the model (RNNwA + n-gram) is also tested with hand-crafted features. In the improved version, LSA-reduced n-gram features are concatenated with the neural representation of the user. Then the result is fed into a fully-connected layer to make prediction. Models are tested in three languages; English, Spanish, and Arabic, and the improved version achieves state-of-the-art accuracy on English, and competitive results on Spanish and Arabic

### E3: source page 5–5

[Original source](https://arxiv.org/pdf/1908.09919) — evidence `def06409c4496b86a965ca821c4011ae8ebaad922473345648db14d89e88fde0`

> Gender Prediction from Tweets: Improving Neural Representations with Hand-Crafted Features
> On the other hand, the improved model (RNNwA + n-gram), where neural and hand-crafted features are concatenated, increases the accuracy of the proposed model by approximately $0,5$% on English and approximately 2% in Spanish and Arabic. This also supports our intuition that the performance of neural models can be improved by hand-crafted features, which is based on the study of BIBREF14. As can be seen in Table TABREF11, the improved model outperforms the state-of-the-art method of BIBREF3 in English and produces competitive results in Spanish and Arabic.

## 3. 452e2d7d7d9e1bb4914903479cd7caff9f6fae42

In the paper 'Deep Learning for Hate Speech Detection in Tweets', Are pretrained embeddings used?

Generated answer: **Yes**

Upstream human reference: GloVe | Alternative human answer: Yes

Claim support: **supported**

Answer correctness against the paper: **correct**

Citation verdicts:

- **E1: supports** — E1 explicitly states that pretrained GloVe embeddings were used.
- **E3: supports** — E3 identifies the GloVe-initialized variants; jointly cited E1 establishes their pretrained provenance. Random-initialization variants are a separate comparison.

**Paper-based reasoning:** The experiments section (PDF p. 2) explicitly uses pretrained GloVe embeddings. The methods also compare random initialization, so Yes means pretrained embeddings were used in some evaluated variants, not every variant.

**Suggested answer:** Yes. They evaluated pretrained GloVe embeddings, including 200-dimensional tweet-trained vectors, alongside random-initialization variants.

**Reference comparison:** Consistent with both GloVe and Yes references.

**Paper locations checked:** [PDF p. 1](https://arxiv.org/pdf/1706.00188#page=1), [PDF p. 2](https://arxiv.org/pdf/1706.00188#page=2). Page numbers are one-based PDF pages, not necessarily printed page labels.

### E1: source page 2–2

[Original source](https://arxiv.org/pdf/1706.00188) — evidence `014573e860d8a103ec67513a2cd7085643d262f8b856d8ecd1fef5bbec7fab85`

> Deep Learning for Hate Speech Detection in Tweets
> We experimented with a dataset of 16K annotated tweets made available by the authors of BIBREF0 . Of the 16K tweets, 3383 are labeled as sexist, 1972 as racist, and the remaining are marked as neither sexist nor racist. For the embedding based methods, we used the GloVe BIBREF5 pre-trained word embeddings. GloVe embeddings have been trained on a large tweet corpus (2B tweets, 27B tokens, 1.2M vocab, uncased). We experimented with multiple word embedding sizes for our task. We observed similar results with different sizes, and hence due to lack of space we report results using embedding size=200. We performed 10-Fold Cross Validation and calculated weighted macro precision, recall and F1-scores.

### E3: source page 1–2

[Original source](https://arxiv.org/pdf/1706.00188) — evidence `e7da36e93a8bc41a2d58c2bed6cb7fb1ee15227fbafcdc79f97d8a3636071ee3`

> Deep Learning for Hate Speech Detection in Tweets
> Proposed Methods: We investigate three neural network architectures for the task, described as follows. For each of the three methods, we initialize the word embeddings with either random embeddings or GloVe embeddings. (1) CNN: Inspired by Kim et. al BIBREF3 's work on using CNNs for sentiment classification, we leverage CNNs for hate speech detection. We use the same settings for the CNN as described in BIBREF3 . (2) LSTM: Unlike feed-forward neural networks, recurrent neural networks like LSTMs can use their internal memory to process arbitrary sequences of inputs. Hence, we use LSTMs to capture long range dependencies in tweets, which may play a role in hate speech detection. (3) FastText: FastText BIBREF4 represents a document by average of word vectors similar to the BoWV model, but allows update of word vectors through Back-propagation during training as opposed to the static word representation in the BoWV model, allowing the mo

## 4. 2301424672cb79297cf7ad95f23b58515e4acce8

In the paper 'Relative contributions of Shakespeare and Fletcher in Henry VIII: An Analysis Based on Most Frequent Words and Most Frequent Rhythmic Patterns', Is Henry VIII reflective of Shakespeare in general?

Generated answer: **Yes**

Upstream human reference: No | Alternative human answer: Yes

Claim support: **unsupported**

Answer correctness against the paper: **ambiguous**

Citation verdicts:

- **E1: does not support** — E1 measures style-classifier accuracy, not whether Henry VIII as a whole is representative of Shakespeare.
- **E2: does not support** — E2 reports stylistic dissimilarity and attribution of scenes to Fletcher; it does not support an unqualified Yes.
- **E3: does not support** — E3 discusses divided authorship, not general representativeness.

**Paper-based reasoning:** Reflective of Shakespeare in general is underspecified: presence of his style is different from representativeness of the whole play. The introduction discusses stylistic dissimilarity, and Section 5 (PDF p. 9) concludes Shakespeare-Fletcher collaboration with different scene contributions. An unqualified Yes is not supported. It would be incorrect if interpreted as saying the whole play is representative of Shakespeare alone; the wording does not justify imposing that interpretation as an unambiguous gold answer.

**Suggested answer:** The play contains Shakespeare-attributed sections, but the paper concludes it is a collaboration with Fletcher; it is not a clean whole-play example of Shakespeare alone.

**Reference comparison:** Matches one of conflicting Yes/No references. That token match does not resolve the vague question or establish semantic correctness.

**Paper locations checked:** [PDF p. 1](https://arxiv.org/pdf/1911.05652#page=1), [PDF p. 2](https://arxiv.org/pdf/1911.05652#page=2), [PDF p. 8](https://arxiv.org/pdf/1911.05652#page=8), [PDF p. 9](https://arxiv.org/pdf/1911.05652#page=9). Page numbers are one-based PDF pages, not necessarily printed page labels.

### E1: source page 4–4

[Original source](https://arxiv.org/pdf/1911.05652) — evidence `1bfce30a9f3e00414b06c9fa607b45ed92b303f5b33c5e18894c6489fb99bd46`

> Relative contributions of Shakespeare and Fletcher in Henry VIII: An Analysis Based on Most Frequent Words and Most Frequent Rhythmic Patterns
> As shown in Table TABREF14, the versification-based models yield a very high accuracy with the recognition of Shakespeare and Fletcher (0.97 to 1 with the exception of Valentinian), yet slightly lower accuracy with the recognition of Massinger (0.81 to 0.88). The accuracy of words-based models remains very high across all three authors (0.95 to 1); in three cases it is nevertheless outperformed by the combined model. We thus may conclude that combined models provide a reliable discriminator between Shakespeare’s, Fletcher’s and Massinger’s styles.

### E2: source page 1–2

[Original source](https://arxiv.org/pdf/1911.05652) — evidence `630b17f9ff35cfd2fdb7d9758065bcdb9b0ba0f0a1a215a549bd77c57941944a`

> Relative contributions of Shakespeare and Fletcher in Henry VIII: An Analysis Based on Most Frequent Words and Most Frequent Rhythmic Patterns
> While the stylistic dissimilarity of Henry VIII (henceforth H8) to Shakespeare’s other plays had been pointed out before BIBREF2, it was not until the mid-nineteenth century that Shakespeare’s sole authorship was called into question. In 1850 British scholar James Spedding published an article BIBREF3 attributing several scenes to John Fletcher. Spedding supported this with data from the domain of versification, namely the ratios of iambic lines ending with a stressed syllable (“The view of earthly glory: men might say”) to lines ending with an extra unstressed one (“Till this time pomp was single, but now married”), pointing out that the distribution of values across scenes is strongly bimodal.

### E3: source page 2–2

[Original source](https://arxiv.org/pdf/1911.05652) — evidence `e3d8bb37dfa684f47016a71d07a193531503163b0ec4bda90db865a2afa7cc77`

> Relative contributions of Shakespeare and Fletcher in Henry VIII: An Analysis Based on Most Frequent Words and Most Frequent Rhythmic Patterns
> More recent articles usually fall in the last mentioned category and attribute the play to Shakespeare and Fletcher (although the shares proposed by them differ). Thomas Horton BIBREF24 employed discriminant analysis of three sets of function words and on this basis attributed most of the scenes to Shakespeare or left them undecided. Thomas Merriam proposed a modification to Spedding’s original attribution concerning re-attribution of several parts of supposedly Fletcher’s scenes back to Shakespeare and vice versa. This was based on measuring the confidence intervals and principal component analysis of frequencies of selected function words in Shakespeare’s and Fletcher’s plays BIBREF25, controversial CUSUM technique concerning the occurrences of another set of selected function words and lines ending with an extra unstressed syllable BIBREF26 o

## 5. 0aca0a208a1e28857fab44e397dc7880e010dbca

In the paper 'Integrating Crowdsourcing and Active Learning for Classification of Work-Life Events from Tweets', Which was the most helpful strategy?

Generated answer: **active learning**

Upstream human reference: Vote entropy and KL divergence;  all the active learning strategies we tested do not work well with deep learning model | Alternative human answer: Entropy algorithm is the best way to build machine learning models. Vote entropy and KL divergence are helpful for the training of machine learning ensemble classifiers. | Alternative human answer: entropy

Claim support: **unsupported**

Answer correctness against the paper: **incorrect**

Citation verdicts:

- **E3: does not support** — E3 explains active learning generally and gives no comparative finding identifying the most helpful strategy.

**Paper-based reasoning:** Active learning names the broad approach, not the best strategy within it. Results (PDF p. 8) identify entropy as reaching optimal performance quickest for LR and RF. Discussion (pp. 9-10) distinguishes vote entropy/KL divergence for machine-learning ensembles and the lack of benefit for the tested deep-learning models.

**Suggested answer:** Entropy was most efficient for the tested LR/RF models. Vote entropy and KL divergence helped machine-learning ensembles; the tested strategies did not help the deep-learning models.

**Reference comparison:** The reference alternatives include these strategy-specific qualifications. Broad active learning text can overlap them without answering the question.

**Paper locations checked:** [PDF p. 8](https://arxiv.org/pdf/2003.12139#page=8), [PDF p. 9](https://arxiv.org/pdf/2003.12139#page=9), [PDF p. 10](https://arxiv.org/pdf/2003.12139#page=10). Page numbers are one-based PDF pages, not necessarily printed page labels.

### E3: source page 2–2

[Original source](https://arxiv.org/pdf/2003.12139) — evidence `1eba376f485287e53c10c665709aba6da24e947cf38799ac14bceea5458a9414`

> Integrating Crowdsourcing and Active Learning for Classification of Work-Life Events from Tweets
> Query optimization techniques (e.g., active learning) can reduce the number of tweets that need to be labeled, while yielding comparable performance for the downstream machine learning tasks BIBREF17, BIBREF18, BIBREF19. Active learning algorithms have been widely applied in various areas including NLP BIBREF20 and image processing BIBREF21. In a pool-based active learning scenario, data samples for training a machine learning algorithm (e.g., a classifier for identifying job loss events) are drawn from a pool of unlabeled data according to some forms of informativeness measure (a.k.a. active learning strategies BIBREF22), and then the most informative instances are selected to be annotated. For a classification task, in essence, an active learning strategy should be able to pick the “best” samples to be labelled that will improve the classification performance the most.

## 6. b70e4c49300dc3eab18e907ab903afd2a0c6075a

In the paper 'Evaluating the Cross-Lingual Effectiveness of Massively Multilingual Neural Machine Translation', What are the five downstream tasks?

Generated answer: **5**

Upstream human reference: These include 3 classification tasks: NLI (XNLI dataset), document classification (MLDoc dataset) and intent classification, and 2 sequence tagging tasks: POS tagging and NER. | Alternative human answer: NLI (XNLI dataset); document classification (MLDoc dataset); intent classification; POS tagging; NER | Alternative human answer: NLI (XNLI dataset); document classification (MLDoc dataset);  intent classification; sequence tagging tasks: POS tagging; NER | Alternative human answer: NLI; document classification; intent classification; POS tagging; NER

Claim support: **unsupported**

Answer correctness against the paper: **incorrect**

Citation verdicts:

- **E1: does not support** — E1 contains both the count and the complete list. It supports the number literally, but not 5 as a complete answer to which tasks.

**Paper-based reasoning:** Section 3, Experiments and Results (PDF p. 4), names all five tasks. The returned 5 repeats the count in the question and omits every task name. The number is true, but the answer is nonresponsive even though its cited passage contains the needed list.

**Suggested answer:** Natural language inference, document classification, intent classification, part-of-speech tagging, and named entity recognition.

**Reference comparison:** The human references name the tasks; the generated count does not provide them.

**Paper locations checked:** [PDF p. 3](https://arxiv.org/pdf/1909.00437#page=3), [PDF p. 4](https://arxiv.org/pdf/1909.00437#page=4). Page numbers are one-based PDF pages, not necessarily printed page labels.

### E1: source page 3–4

[Original source](https://arxiv.org/pdf/1909.00437) — evidence `46fd8d3b5f3df9efd201eac4cff6cbadf8cdcd3465d5ffd1858eff56d50a361e`

> Evaluating the Cross-Lingual Effectiveness of Massively Multilingual Neural Machine Translation
> As stated earlier, we use MMTE to perform downstream cross-lingual transfer on 5 NLP tasks. These include 3 classification tasks: NLI (XNLI dataset), document classification (MLDoc dataset) and intent classification, and 2 sequence tagging tasks: POS tagging and NER. We detail all of the experiments in this section.

## 7. 3dad6b792044018bb968ac0d0fd4628653f9e4b7

In the paper 'Character n-gram Embeddings to Improve RNN Language Models', Which word embeddings do they compare against?

Generated answer: **char INLINEFORM3 -MS-vec**

Upstream human reference: Unanswerable in the named paper

Claim support: **unsupported**

Answer correctness against the paper: **incorrect**

Citation verdicts:

- **E2: does not support** — E2 describes the proposed method and its improvements, not the embeddings compared against; the answer also preserves a formula placeholder.

**Paper-based reasoning:** The returned char INLINEFORM3 -MS-vec names the proposed char n-MS-vec method, with an unresolved formula placeholder, rather than a comparison embedding. Sections 4.2-4.3 and Tables 2/5 (PDF pp. 3-4) compare ordinary learned word embeddings, a two-embedding baseline, charCNN, char n-Sum-vec and char n-SS-vec. Thus the broad question has relevant comparisons in the paper, although a narrower question about named pretrained embedding products would need clarification. The stored unanswerable label should not be treated as proof that the paper contains no embedding comparisons.

**Suggested answer:** For the representation comparisons, they use baseline word embeddings, a two-embedding baseline, charCNN, char n-Sum-vec and char n-SS-vec. The returned char n-MS-vec is their proposed method.

**Reference comparison:** The frozen reference marks this unanswerable. This audit flags a scope/annotation concern rather than changing the label. The emitted proposed-method name is still incorrect for the comparison question.

**Paper locations checked:** [PDF p. 3](https://arxiv.org/pdf/1906.05506#page=3), [PDF p. 4](https://arxiv.org/pdf/1906.05506#page=4), [PDF p. 7](https://arxiv.org/pdf/1906.05506#page=7), [PDF p. 8](https://arxiv.org/pdf/1906.05506#page=8). Page numbers are one-based PDF pages, not necessarily printed page labels.

### E2: source page 7–8

[Original source](https://arxiv.org/pdf/1906.05506) — evidence `f815c8db259cd39a9487f6444cadb2f615ead7c76703faab854793c2511c576a`

> Character n-gram Embeddings to Improve RNN Language Models
> In this paper, we incorporated character information with RNN language models. Based on the research in the field of word embedding construction BIBREF0 , we focused on character INLINEFORM0 -gram embeddings to construct word embeddings. We used multi-dimensional self-attention BIBREF11 to encode character INLINEFORM1 -gram embeddings. Our proposed char INLINEFORM2 -MS-vec improved the performance of state-of-the-art RNN language models and achieved the best perplexities on Penn Treebank, WikiText-2, and WikiText-103. Moreover, we investigated the effect of char INLINEFORM3 -MS-vec on application tasks, specifically, machine translation and headline generation. Our experiments show that char INLINEFORM4 -MS-vec also improved the performance of a neural encoder-decoder on both tasks.

## 8. b424ad7f9214076b963a0077d7345d7bb5a7a205

In the paper 'UIT-ViIC: A Dataset for the First Evaluation on Vietnamese Image Captioning', Do they use crowdsourcing for the captions?

Generated answer: **Yes**

Upstream human reference: Yes

Claim support: **unclear**

Answer correctness against the paper: **ambiguous**

Citation verdicts:

- **E1: unclear** — E1 says manually written and gives dataset size, but says nothing about crowd recruitment. Manual annotation alone cannot establish Yes.

**Paper-based reasoning:** The cited abstract establishes manually written captions, which does not establish crowdsourcing. Section 3.2 (PDF pp. 4-5) describes five native Vietnamese writers aged 22-25 who received sports/vocabulary training, using the web annotation tool in Section 3.1. The explicit Mechanical Turk statement on p. 4 concerns source MS-COCO captions, not the newly written Vietnamese captions. The paper does not clearly establish crowd recruitment for UIT-ViIC, so an unqualified Yes is not verified; this is insufficient evidence, not proof that crowdsourcing was impossible.

**Suggested answer:** UIT-ViIC captions were written by five trained Vietnamese writers using a web tool. The paper explicitly attributes Mechanical Turk to MS-COCO; it does not clearly say UIT-ViIC used crowdsourcing.

**Reference comparison:** Matches the upstream Yes, but the paper does not clearly establish that characterization of the Vietnamese annotation process.

**Paper locations checked:** [PDF p. 1](https://arxiv.org/pdf/2002.00175#page=1), [PDF p. 4](https://arxiv.org/pdf/2002.00175#page=4), [PDF p. 5](https://arxiv.org/pdf/2002.00175#page=5). Page numbers are one-based PDF pages, not necessarily printed page labels.

### E1: source page 1–1

[Original source](https://arxiv.org/pdf/2002.00175) — evidence `e55a17bc9015aa5d4902c528a1f43aa53a0742fb48355527609fe26ac73896dc`

> UIT-ViIC: A Dataset for the First Evaluation on Vietnamese Image Captioning
> Image Captioning, the task of automatic generation of image captions, has attracted attentions from researchers in many fields of computer science, being computer vision, natural language processing and machine learning in recent years. This paper contributes to research on Image Captioning task in terms of extending dataset to a different language - Vietnamese. So far, there is no existed Image Captioning dataset for Vietnamese language, so this is the foremost fundamental step for developing Vietnamese Image Captioning. In this scope, we first build a dataset which contains manually written captions for images from Microsoft COCO dataset relating to sports played with balls, we called this dataset UIT-ViIC. UIT-ViIC consists of 19,250 Vietnamese captions for 3,850 images. Following that, we evaluate our dataset on deep neural network models and do comparisons with English dataset and two Vietnamese datasets b

## 9. de346decb1fbca8746b72c78ea9d1208902f5e0a

In the paper 'A Lost Croatian Cybernetic Machine Translation Program', What language was this research published in?

Generated answer: **Croatian**

Upstream human reference: Unanswerable in the named paper

Claim support: **unsupported**

Answer correctness against the paper: **ambiguous**

Citation verdicts:

- **E1: does not support** — E1 discusses translation/interlanguage examples, not the language in which research was published.
- **E2: does not support** — E2 lists institutions and language departments; these do not establish publication language.
- **E3: does not support** — E3 locates a Croatian research group historically; nationality/location is not publication language.

**Paper-based reasoning:** This research could refer to the current paper or the historical studies it describes. The current paper is in English (PDF p. 1 onward). Its bibliography includes Croatian-language titles for historical works (pp. 11-13), but title language alone does not establish the publication language of every referenced study. None of the three emitted citations establishes publication language. Croatian therefore has no demonstrated citation support and is incorrect if the question means the current paper; the historical referent remains underspecified.

**Suggested answer:** The current paper is written in English. If the question concerns a historical publication, specify which one; the cited passages do not establish its publication language.

**Reference comparison:** The frozen reference marks the question unanswerable. That is consistent with ambiguity about historical research, but does not override the observable English language of the current paper.

**Paper locations checked:** [PDF p. 1](https://arxiv.org/pdf/1908.08917#page=1), [PDF p. 2](https://arxiv.org/pdf/1908.08917#page=2), [PDF p. 4](https://arxiv.org/pdf/1908.08917#page=4), [PDF p. 5](https://arxiv.org/pdf/1908.08917#page=5), [PDF p. 11](https://arxiv.org/pdf/1908.08917#page=11), [PDF p. 12](https://arxiv.org/pdf/1908.08917#page=12), [PDF p. 13](https://arxiv.org/pdf/1908.08917#page=13). Page numbers are one-based PDF pages, not necessarily printed page labels.

### E1: source page 2–2

[Original source](https://arxiv.org/pdf/1908.08917) — evidence `7b33ccdb476776add7a093fe255807c6cf67c2676b1a0d5f7f1d639aed3d1436`

> A Lost Croatian Cybernetic Machine Translation Program
> To put the research of the Croatian group in the right context, we have to explore the origin of the idea of machine translation. The idea of machine translation is an old one, and its origin is commonly connected with the work of Rene Descartes, i.e. to his idea of universal language, as described in his letter to Mersenne from 20.xi.1629 BIBREF0. Descartes describes universal language as a simplified version of the language which will serve as an “interlanguage” for translation. That is, if we want to translate from English to Croatian, we will firstly translate from English to an “interlanguage”, and then from the “interlanguage” to Croatian. As described later in this paper, this idea had been implemented in the machine translation process, firstly in the Indonesian-to-Russian machine translation system created by Andreev, Kulagina and Melchuk from the early 1960s.

### E2: source page 4–5

[Original source](https://arxiv.org/pdf/1908.08917) — evidence `49ec96d3aeda5585e6924f8438efa652aa6625f8ec796bc5b200c7b041879b4f`

> A Lost Croatian Cybernetic Machine Translation Program
> In Yugoslavia, organized effort in machine translation started in 1959, but the first individual effort was made by Vladimir Matković from the Institute for Telecommunications in Zagreb in 1957 in his PhD thesis on entropy in the Croatian language BIBREF10. The main research group in machine translation was formed in 1958, at the Circle for Young Linguists in Zagreb, initiated by a young linguist Bulcsu Laszlo, who graduated in Russian language, Southern Slavic languages and English language and literature at the University of Zagreb in 1952. The majority of the group members came from different departments of the Faculty of Humanities and Social Sciences of the University of Zagreb, with several individuals from other institutions. The members from the Faculty of Humanities and Social Sciences were: Svetozar Petrović (Department of Comparative Literature), Stjepan Babić (Department of Serbo-Croatian Language and Literature), Kruno

### E3: source page 2–2

[Original source](https://arxiv.org/pdf/1908.08917) — evidence `ae06e05262aa1a3a0cd07aabdbfcd59f98ef9f90a11476663bca5f8f48258a56`

> A Lost Croatian Cybernetic Machine Translation Program
> In this paper, we are exploring the historical significance of Croatian machine translation research group. The group was active in 1950s, and it was conducted by Bulcsu Laszlo, Croatian linguist, who was a pioneer in machine translation during the 1950s in Yugoslavia.

## Aggregation after actual review

Unsupported-claim rate: human-labeled unsupported answers divided by the nine emitted answers; report unclear cases separately rather than treating them as supported. Supported-claim coverage: supported answers divided by all 100 final questions, alongside refusal/failure counts. Citation support precision: supporting citation links divided by all reviewed links, with unclear links separate. Do not calculate or claim these human metrics before completing the judgments.
