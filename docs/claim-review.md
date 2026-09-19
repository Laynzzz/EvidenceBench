# Human claim-support review — nine generated answers

This is the remaining human evaluation gate in plan.md sections 11–12. QASPER supplies human questions, reference answers and relevant paragraphs; it does not directly judge these newly generated claims and their selected citations. This form is prepared, not completed.

For each answer, record **supported / unsupported / unclear** based on whether the cited model-visible excerpts support the complete answer to the question. Separately record **correct / incorrect / ambiguous** against the human reference, and mark each citation **supports / does not support / unclear**. If references conflict or the excerpt is insufficient, use ambiguous/unclear rather than guessing. All nine emitted answers are included; refusals and failures have separate recorded denominators.

Reply with the nine numbered verdicts and any citation exceptions, or fill this document. Record reviewer and date when completed. The audit is descriptive after the final test; it must not silently trigger model or threshold tuning.

Reviewer: **pending**

Date: **pending**

Status: **not human-reviewed**

## 1. e9a0a69eacd554141f56b60ab2d1912cc33f526a

In the paper 'Sentiment Analysis of Code-Mixed Indian Languages: An Overview of SAIL_Code-Mixed Shared Task @ICON-2017', what was the baseline?

Generated answer: **0.331**

Upstream human reference: Random labeling | Alternative human answer:  randomly assigning any of the sentiment values to each of the test instances

Claim support: **pending**

Answer correctness: **pending**

Citation verdicts: **pending**

### E1: source page 8–8

[Original source](https://arxiv.org/pdf/1803.06745) — evidence `750ee7dbec733ad32260d15cd6e0f9773e800348b49f74ca8642c2e0769b0a28`

> Sentiment Analysis of Code-Mixed Indian Languages: An Overview of SAIL_Code-Mixed Shared Task @ICON-2017
> This paper presents the details of shared task held during the ICON 2017. The competition presents the sentiment identification task from HI-EN and BN-EN code-mixed datasets. A random baseline system obtained macro average f-score of 0.331 and 0.339 for HI-EN and BN-EN datasets, respectively. The best performing team obtained maximum macro average f-score of 0.569 and 0.526 for HI-EN and BN-EN datasets, respectively. The team used word and character level n-grams as features and SVM for sentiment classification. We plan to enhance the current dataset and include more data pairs in the next version of the shared task. In future, more advanced task like aspect based sentiment analysis and stance detection can be performed on code-mixed dataset.

## 2. 36cb7ebdd39e0b8a89ff946d3a3aef8a76a6bb43

In the paper 'Gender Prediction from Tweets: Improving Neural Representations with Hand-Crafted Features', Are LSA-reduced n-gram features considered hand-crafted features?

Generated answer: **Yes**

Upstream human reference: Yes | Alternative human answer: No

Claim support: **pending**

Answer correctness: **pending**

Citation verdicts: **pending**

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

Claim support: **pending**

Answer correctness: **pending**

Citation verdicts: **pending**

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

Claim support: **pending**

Answer correctness: **pending**

Citation verdicts: **pending**

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

Claim support: **pending**

Answer correctness: **pending**

Citation verdicts: **pending**

### E3: source page 2–2

[Original source](https://arxiv.org/pdf/2003.12139) — evidence `1eba376f485287e53c10c665709aba6da24e947cf38799ac14bceea5458a9414`

> Integrating Crowdsourcing and Active Learning for Classification of Work-Life Events from Tweets
> Query optimization techniques (e.g., active learning) can reduce the number of tweets that need to be labeled, while yielding comparable performance for the downstream machine learning tasks BIBREF17, BIBREF18, BIBREF19. Active learning algorithms have been widely applied in various areas including NLP BIBREF20 and image processing BIBREF21. In a pool-based active learning scenario, data samples for training a machine learning algorithm (e.g., a classifier for identifying job loss events) are drawn from a pool of unlabeled data according to some forms of informativeness measure (a.k.a. active learning strategies BIBREF22), and then the most informative instances are selected to be annotated. For a classification task, in essence, an active learning strategy should be able to pick the “best” samples to be labelled that will improve the classification performance the most.

## 6. b70e4c49300dc3eab18e907ab903afd2a0c6075a

In the paper 'Evaluating the Cross-Lingual Effectiveness of Massively Multilingual Neural Machine Translation', What are the five downstream tasks?

Generated answer: **5**

Upstream human reference: These include 3 classification tasks: NLI (XNLI dataset), document classification (MLDoc dataset) and intent classification, and 2 sequence tagging tasks: POS tagging and NER. | Alternative human answer: NLI (XNLI dataset); document classification (MLDoc dataset); intent classification; POS tagging; NER | Alternative human answer: NLI (XNLI dataset); document classification (MLDoc dataset);  intent classification; sequence tagging tasks: POS tagging; NER | Alternative human answer: NLI; document classification; intent classification; POS tagging; NER

Claim support: **pending**

Answer correctness: **pending**

Citation verdicts: **pending**

### E1: source page 3–4

[Original source](https://arxiv.org/pdf/1909.00437) — evidence `46fd8d3b5f3df9efd201eac4cff6cbadf8cdcd3465d5ffd1858eff56d50a361e`

> Evaluating the Cross-Lingual Effectiveness of Massively Multilingual Neural Machine Translation
> As stated earlier, we use MMTE to perform downstream cross-lingual transfer on 5 NLP tasks. These include 3 classification tasks: NLI (XNLI dataset), document classification (MLDoc dataset) and intent classification, and 2 sequence tagging tasks: POS tagging and NER. We detail all of the experiments in this section.

## 7. 3dad6b792044018bb968ac0d0fd4628653f9e4b7

In the paper 'Character n-gram Embeddings to Improve RNN Language Models', Which word embeddings do they compare against?

Generated answer: **char INLINEFORM3 -MS-vec**

Upstream human reference: Unanswerable in the named paper

Claim support: **pending**

Answer correctness: **pending**

Citation verdicts: **pending**

### E2: source page 7–8

[Original source](https://arxiv.org/pdf/1906.05506) — evidence `f815c8db259cd39a9487f6444cadb2f615ead7c76703faab854793c2511c576a`

> Character n-gram Embeddings to Improve RNN Language Models
> In this paper, we incorporated character information with RNN language models. Based on the research in the field of word embedding construction BIBREF0 , we focused on character INLINEFORM0 -gram embeddings to construct word embeddings. We used multi-dimensional self-attention BIBREF11 to encode character INLINEFORM1 -gram embeddings. Our proposed char INLINEFORM2 -MS-vec improved the performance of state-of-the-art RNN language models and achieved the best perplexities on Penn Treebank, WikiText-2, and WikiText-103. Moreover, we investigated the effect of char INLINEFORM3 -MS-vec on application tasks, specifically, machine translation and headline generation. Our experiments show that char INLINEFORM4 -MS-vec also improved the performance of a neural encoder-decoder on both tasks.

## 8. b424ad7f9214076b963a0077d7345d7bb5a7a205

In the paper 'UIT-ViIC: A Dataset for the First Evaluation on Vietnamese Image Captioning', Do they use crowdsourcing for the captions?

Generated answer: **Yes**

Upstream human reference: Yes

Claim support: **pending**

Answer correctness: **pending**

Citation verdicts: **pending**

### E1: source page 1–1

[Original source](https://arxiv.org/pdf/2002.00175) — evidence `e55a17bc9015aa5d4902c528a1f43aa53a0742fb48355527609fe26ac73896dc`

> UIT-ViIC: A Dataset for the First Evaluation on Vietnamese Image Captioning
> Image Captioning, the task of automatic generation of image captions, has attracted attentions from researchers in many fields of computer science, being computer vision, natural language processing and machine learning in recent years. This paper contributes to research on Image Captioning task in terms of extending dataset to a different language - Vietnamese. So far, there is no existed Image Captioning dataset for Vietnamese language, so this is the foremost fundamental step for developing Vietnamese Image Captioning. In this scope, we first build a dataset which contains manually written captions for images from Microsoft COCO dataset relating to sports played with balls, we called this dataset UIT-ViIC. UIT-ViIC consists of 19,250 Vietnamese captions for 3,850 images. Following that, we evaluate our dataset on deep neural network models and do comparisons with English dataset and two Vietnamese datasets b

## 9. de346decb1fbca8746b72c78ea9d1208902f5e0a

In the paper 'A Lost Croatian Cybernetic Machine Translation Program', What language was this research published in?

Generated answer: **Croatian**

Upstream human reference: Unanswerable in the named paper

Claim support: **pending**

Answer correctness: **pending**

Citation verdicts: **pending**

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
