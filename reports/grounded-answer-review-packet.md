# Complete-answer experiment: emitted-answer review packet

Run: `artifacts/grounded-answer-v1/runs/20260924T041708Z-d0f23e62ae`. Status: unreviewed. All emitted answers are included; benchmark references and answerability labels are omitted. No independent human review has occurred.

Evaluate responsiveness, completeness, support and paper-level correctness separately. An exact quote can be real without entailing the answer. Page numbers are physical PDF pages.

## Case 1: dea9e7fe8e47da5e7f31d9b1a46ebe34e731a596

Question: In the paper 'Humor Detection in English-Hindi Code-Mixed Social Media Content : Corpus and Baseline System', What type of system does the baseline classification use?

Answer: support vector machines with radial basis function kernel

Automatic check: exact_quote_presence_only (not entailment).

Citation E1: [paper 1806.05513](../data/raw/qasper-fresh-v1/1806.05513.pdf), PDF page 4.

Selected quote:

N-grams when trained with support vector machines with radial basis function kernel performed better than other features and yielded an accuracy of 68.5%. The best accuracy (69.3%) was given by support vector machines with radial basis function kernel.

Full supplied passage:

```text
Humor Detection in English-Hindi Code-Mixed Social Media Content : Corpus and Baseline System
In this paper, we describe a freely available corpus of 3453 English-Hindi code-mixed tweets. The tweets are annotated with humorous(H) and non-humorous(N) tags along with the language tags at the word level. The task of humor identification in social media texts is analyzed as a classification problem and several machine learning classification models are used. The features used in our classification system are n-grams, bag-of-words, common words and hashtags. N-grams when trained with support vector machines with radial basis function kernel performed better than other features and yielded an accuracy of 68.5%. The best accuracy (69.3%) was given by support vector machines with radial basis function kernel.
```

Review: responsiveness ___; completeness ___; cited support ___; paper correctness ___; rationale ___

## Case 2: 114934e1a1e818630ff33ac5c4cd4be6c6f75bb2

Question: In the paper 'Neural Collective Entity Linking', How effective is their NCEL approach overall?

Answer: NCEL outperforms the state-of-the-art collective methods across five different datasets.

Automatic check: exact_quote_presence_only (not entailment).

Citation E2: [paper 1811.08603](../data/raw/qasper-fresh-v1/1811.08603.pdf), PDF page 10.

Selected quote:

Trained on collected Wikipedia hyperlinks, NCEL outperforms the state-of-the-art collective methods across five different datasets.

Full supplied passage:

```text
Neural Collective Entity Linking
In this paper, we propose a neural model for collective entity linking that is end-to-end trainable. It applies GCN on subgraphs instead of the entire entity graph to efficiently learn features from both local and global information. We design an attention mechanism that endows NCEL robust to noisy data. Trained on collected Wikipedia hyperlinks, NCEL outperforms the state-of-the-art collective methods across five different datasets. Besides, further analysis of the impacts of main modules as well as qualitative results demonstrates its effectiveness.
```

Review: responsiveness ___; completeness ___; cited support ___; paper correctness ___; rationale ___

## Case 3: 1beb4a590fa6127a138f4ed1dd13d5d51cc96809

Question: In the paper 'A Deeper Look into Sarcastic Tweets Using Deep Convolutional Neural Networks', What are the network's baseline features?

Answer: The baseline features include features extracted from pre-trained models.

Automatic check: exact_quote_presence_only (not entailment).

Citation E1: [paper 1610.08815](../data/raw/qasper-fresh-v1/1610.08815.pdf), PDF page 8.

Selected quote:

In another setting, we use the features extracted from the pre-trained models as the static channels of features in the CNN of the baseline method. These features are appended to the hidden layer of the baseline CNN, preceding the final output softmax layer.

Full supplied passage:

```text
A Deeper Look into Sarcastic Tweets Using Deep Convolutional Neural Networks
In another setting, we use the features extracted from the pre-trained models as the static channels of features in the CNN of the baseline method. These features are appended to the hidden layer of the baseline CNN, preceding the final output softmax layer.
```

Review: responsiveness ___; completeness ___; cited support ___; paper correctness ___; rationale ___

## Case 4: 9b7655d39c7a19a23eb8944568eb5618042b9026

Question: In the paper 'Performance Comparison of Crowdworkers and NLP Tools onNamed-Entity Recognition and Sentiment Analysis of Political Tweets', Which toolkits do they use?

Answer: BIBREF17, BIBREF18, TensiStrength BIBREF13, TwitterNLP BIBREF6, CogComp-NLP BIBREF20, Stanford NLP NER BIBREF21

Automatic check: exact_quote_presence_only (not entailment).

Citation E2: [paper 2002.04181](../data/raw/qasper-fresh-v1/2002.04181.pdf), PDF page 2.

Selected quote:

Among commercial NLP toolkits (e.g., BIBREF14, BIBREF15, BIBREF16), we selected BIBREF17 and BIBREF18 for our experiments, which, to the best of our knowledge, are the only publicly accessible commercial APIs for the task of entity-level sentiment analysis that is agnostic to the text domain. We also report results of TensiStrength BIBREF13, TwitterNLP BIBREF6, BIBREF19, CogComp-NLP BIBREF20, and Stanford NLP NER BIBREF21.

Full supplied passage:

```text
Performance Comparison of Crowdworkers and NLP Tools onNamed-Entity Recognition and Sentiment Analysis of Political Tweets
Among commercial NLP toolkits (e.g., BIBREF14, BIBREF15, BIBREF16), we selected BIBREF17 and BIBREF18 for our experiments, which, to the best of our knowledge, are the only publicly accessible commercial APIs for the task of entity-level sentiment analysis that is agnostic to the text domain. We also report results of TensiStrength BIBREF13, TwitterNLP BIBREF6, BIBREF19, CogComp-NLP BIBREF20, and Stanford NLP NER BIBREF21.
```

Review: responsiveness ___; completeness ___; cited support ___; paper correctness ___; rationale ___

## Case 5: b1ce129678e37070e69f01332f1a8587e18e06b0

Question: In the paper 'Sentiment Analysis of Twitter Data for Predicting Stock Market Movements', What dataset is used to train the model?

Answer: Microsoft stock price data

Automatic check: exact_quote_presence_only (not entailment).

Citation E1: [paper 1610.09225](../data/raw/qasper-fresh-v1/1610.09225.pdf), PDF page 3.

Selected quote:

The stock price data of Microsoft are labeled suitably for training using a simple program. If the previous day stock price is more than the current day stock price, the current day is marked with a numeric value of 0, else marked with a numeric value of 1.

Full supplied passage:

```text
Sentiment Analysis of Twitter Data for Predicting Stock Market Movements
The stock price data of Microsoft are labeled suitably for training using a simple program. If the previous day stock price is more than the current day stock price, the current day is marked with a numeric value of 0, else marked with a numeric value of 1. Now, this correlation analysis turns out to be a classification problem. The total positive, negative and neutral emotions in tweets in a 3 day period are calculated successively which are used as features for the classifier model and the output is the labeled next day value of stock 0 or 1.The window size is experimented and best results are achieved when the sentiment values precede 3 days to the stock price. A total of 355 instances, each with 3 attributes are fed to the classifier with a split proportions of 80% train dataset and the remaining dataset for testing. The accuracy of the classifier is discussed in the results section.
```

Review: responsiveness ___; completeness ___; cited support ___; paper correctness ___; rationale ___

## Case 6: 984fc3e726848f8f13dfe72b89e3770d00c3a1af

Question: In the paper 'Automated News Suggestions for Populating Wikipedia Entity Pages', What features are used to represent the novelty of news articles to entity pages?

Answer: novelty of news articles w.r.t the already existing entity profile

Automatic check: exact_quote_presence_only (not entailment).

Citation E2: [paper 1703.10344](../data/raw/qasper-fresh-v1/1703.10344.pdf), PDF page 5.

Selected quote:

Given an entity INLINEFORM0 and the already added news references INLINEFORM1 up to year INLINEFORM2 , the novelty of INLINEFORM3 at year INLINEFORM4 is measured by the KL divergence between the language model of INLINEFORM5 and articles in INLINEFORM6 . We combine this measure with the entity overlap of INLINEFORM7 and INLINEFORM8 . The novelty value of INLINEFORM9 is given by the minimal divergence value.

Full supplied passage:

```text
Automated News Suggestions for Populating Wikipedia Entity Pages
Given an entity INLINEFORM0 and the already added news references INLINEFORM1 up to year INLINEFORM2 , the novelty of INLINEFORM3 at year INLINEFORM4 is measured by the KL divergence between the language model of INLINEFORM5 and articles in INLINEFORM6 . We combine this measure with the entity overlap of INLINEFORM7 and INLINEFORM8 . The novelty value of INLINEFORM9 is given by the minimal divergence value. Low scores indicate low novelty for the entity profile INLINEFORM10 .
```

Review: responsiveness ___; completeness ___; cited support ___; paper correctness ___; rationale ___

## Case 7: b7c3f3942a07c118e57130bc4c3ec4adc431d725

Question: In the paper 'Applying a Pre-trained Language Model to Spanish Twitter Humor Prediction', What did the best systems use for their model?

Answer: ASGD Weight-Dropped Long Short Term Memory (AWD_LSTM) model

Automatic check: exact_quote_presence_only (not entailment).

Citation E1: [paper 1907.03187](../data/raw/qasper-fresh-v1/1907.03187.pdf), PDF page 7.

Selected quote:

We have open-sourced all code used in this contest to further enable research on this task in the future.

Full supplied passage:

```text
Applying a Pre-trained Language Model to Spanish Twitter Humor Prediction
This paper describes our implementation of a neural net model for classification and regression in the HAHA 2019 challenge. Our solution placed 3rd in Task 1 and 2nd in Task 2 in the final competition standings. We describe the data collection, pre-training, and final model building steps for this contest. Twitter has slang and abbreviations that are unique to the short-format as well as generous use of emoticons. To capture these features, we collected our own dataset based on Spanish Tweets that is 16 times larger than the competition data set and allowed us to pre-train a language model. Humor is subtle and using a label smoothed loss prevented us from becoming overconfident in our predictions and train more quickly without the gradual unfreezing required by ULMFiT. We have open-sourced all code used in this contest to further enable research on this task in the future.
```

Citation E3: [paper 1907.03187](../data/raw/qasper-fresh-v1/1907.03187.pdf), PDF page 4.

Selected quote:

For the LM, we selected an ASGD Weight-Dropped Long Short Term Memory (AWD_LSTM, described in Merity et al. BIBREF5 ) model included in Fast.ai.

Full supplied passage:

```text
Applying a Pre-trained Language Model to Spanish Twitter Humor Prediction
We train the LM using a 90/10 training/validation split, reporting the validation loss and accuracy of next-word prediction on the validation set. For the LM, we selected an ASGD Weight-Dropped Long Short Term Memory (AWD_LSTM, described in Merity et al. BIBREF5 ) model included in Fast.ai. We replaced the typical Long Short Term Memory (LSTM) units with Quasi Recurrent Neural Network (QRNN, described in Bradbury et al. BIBREF6 ) units. Our network has 2304 hidden-states, 3 layers and a softmax layer to predict the next-word. We tied the embedding weights BIBREF7 on the encoder and decoder for training. We performed some simple tests with LSTM units and a Transformer Language model, finding all models were similar in performance during LM training. We thus chose to use QRNN units due to improved training speed compared to the alternatives. This model has about 60 million trainable parameters.
```

Review: responsiveness ___; completeness ___; cited support ___; paper correctness ___; rationale ___

## Case 8: a5505e25ee9ae84090e1442034ddbb3cedabcf04

Question: In the paper 'Applying a Pre-trained Language Model to Spanish Twitter Humor Prediction', What were their results on the classification and regression tasks

Answer: 3rd in the classification task and 2nd in the regression task

Automatic check: exact_quote_presence_only (not entailment).

Citation E2: [paper 1907.03187](../data/raw/qasper-fresh-v1/1907.03187.pdf), PDF page 1.

Selected quote:

Our entry into the HAHA 2019 Challenge placed $3^{rd}$ in the classification task and $2^{nd}$ in the regression task.

Full supplied passage:

```text
Applying a Pre-trained Language Model to Spanish Twitter Humor Prediction
Our entry into the HAHA 2019 Challenge placed $3^{rd}$ in the classification task and $2^{nd}$ in the regression task. We describe our system and innovations, as well as comparing our results to a Naive Bayes baseline. A large Twitter based corpus allowed us to train a language model from scratch focused on Spanish and transfer that knowledge to our competition model. To overcome the inherent errors in some labels we reduce our class confidence with label smoothing in the loss function. All the code for our project is included in a GitHub repository for easy reference and to enable replication by others.
```

Review: responsiveness ___; completeness ___; cited support ___; paper correctness ___; rationale ___

## Case 9: e35a7f9513ff1cc0f0520f1d4ad9168a47dc18bb

Question: In the paper 'Combining Advanced Methods in Japanese-Vietnamese Neural Machine Translation', what was the baseline?

Answer: For the baseline systems, the training data includes KyTea-segmented Japanese texts and pyvi-segmented Vietnamese texts. For comparison purpose, we build two baseline systems for each direction: one is use the traditional phrase-based statistical machine translation (SMT), the other one is the NMT system.

Automatic check: exact_quote_presence_only (not entailment).

Citation E3: [paper 1805.07133](../data/raw/qasper-fresh-v1/1805.07133.pdf), PDF page 5.

Selected quote:

Baseline. For the baseline systems, the training data includes KyTea-segmented Japanese texts and pyvi-segmented Vietnamese texts. For comparison purpose, we build two baseline systems for each direction: one is use the traditional phrase-based statistical machine translation (SMT), the other one is the NMT system.

Full supplied passage:

```text
Combining Advanced Methods in Japanese-Vietnamese Neural Machine Translation
Baseline. For the baseline systems, the training data includes KyTea-segmented Japanese texts and pyvi-segmented Vietnamese texts. For comparison purpose, we build two baseline systems for each direction: one is use the traditional phrase-based statistical machine translation (SMT), the other one is the NMT system. Although our training set is small but we find that the NMT systems (2) are still more effective than the phrase-based SMT models (1) in both translation directions.
```

Review: responsiveness ___; completeness ___; cited support ___; paper correctness ___; rationale ___

## Case 10: 219af68afeaecabdfd279f439f10ba7c231736e4

Question: In the paper 'Combining Advanced Methods in Japanese-Vietnamese Neural Machine Translation', what japanese-vietnamese dataset do they use?

Answer: Japanese-Vietnamese parallel corpus

Automatic check: exact_quote_presence_only (not entailment).

Citation E1: [paper 1805.07133](../data/raw/qasper-fresh-v1/1805.07133.pdf), PDF page 5.

Selected quote:

For Mix-Source, instead of using a subsampled monolingual corpus, we use the Vietnamese part of the Japanese-Vietnamese parallel corpus in order to learn the multilingual information in the same domain.

Full supplied passage:

```text
Combining Advanced Methods in Japanese-Vietnamese Neural Machine Translation
The data augmentation methods has been applied only for the Japanese INLINEFORM0 Vietnamese direction. For Back Translation, we use Vietnamese monolingual data from VNESEcorpus of DongDu which includes 349578 sentences. We shuffle the lines of VNESEcorpus corpus and take out the first 106758 sentences (the same as the number of sentence pairs in the original parallel corpus). For Mix-Source, instead of using a subsampled monolingual corpus, we use the Vietnamese part of the Japanese-Vietnamese parallel corpus in order to learn the multilingual information in the same domain. Our datasets are listed in Table TABREF14 .
```

Review: responsiveness ___; completeness ___; cited support ___; paper correctness ___; rationale ___

## Case 11: 63a1cbe66fd58ff0ead895a8bac1198c38c008aa

Question: In the paper 'Going Beneath the Surface: Evaluating Image Captioning for Grammaticality, Truthfulness and Diversity', Which existing models are evaluated?

Answer: LRCN1u model

Automatic check: exact_quote_presence_only (not entailment).

Citation E1: [paper 1912.08960](../data/raw/qasper-fresh-v1/1912.08960.pdf), PDF page 1.

Selected quote:

We introduce a new diagnostic evaluation framework for the task of image captioning, with the goal of directly assessing models for grammaticality, truthfulness and diversity (GTD) of generated captions. We demonstrate the potential of our evaluation framework by evaluating existing image captioning models on a wide ranging set of synthetic datasets that we construct for diagnostic evaluation.

Full supplied passage:

```text
Going Beneath the Surface: Evaluating Image Captioning for Grammaticality, Truthfulness and Diversity
Image captioning as a multimodal task has drawn much interest in recent years. However, evaluation for this task remains a challenging problem. Existing evaluation metrics focus on surface similarity between a candidate caption and a set of reference captions, and do not check the actual relation between a caption and the underlying visual content. We introduce a new diagnostic evaluation framework for the task of image captioning, with the goal of directly assessing models for grammaticality, truthfulness and diversity (GTD) of generated captions. We demonstrate the potential of our evaluation framework by evaluating existing image captioning models on a wide ranging set of synthetic datasets that we construct for diagnostic evaluation. We empirically show how the GTD evaluation framework, in combination with diagnostic datasets, can provide insights into model capabilities and limita
```

Citation E3: [paper 1912.08960](../data/raw/qasper-fresh-v1/1912.08960.pdf), PDF page 4.

Selected quote:

In the remainder of the paper we discuss in detail the diagnostic results of the LRCN1u model demonstrated by the GTD evaluation framework.

Full supplied passage:

```text
Going Beneath the Surface: Evaluating Image Captioning for Grammaticality, Truthfulness and Diversity
In the remainder of the paper we discuss in detail the diagnostic results of the LRCN1u model demonstrated by the GTD evaluation framework.
```

Review: responsiveness ___; completeness ___; cited support ___; paper correctness ___; rationale ___

## Case 12: 3116453e35352a3a90ee5b12246dc7f2e60cfc59

Question: In the paper 'A Neural Topic-Attention Model for Medical Term Abbreviation Disambiguation', To what baseline models is proposed model compared?

Answer: traditional features and Doc2vec model

Automatic check: exact_quote_presence_only (not entailment).

Citation E3: [paper 1910.14076](../data/raw/qasper-fresh-v1/1910.14076.pdf), PDF page 3.

Selected quote:

We conducted a comprehensive comparison with the baseline models, and some of them were never investigated for the abbreviation disambiguation task. We applied traditional features by simply taking the TF-IDF features as the inputs into the classic classifiers. Deep features are also considered: a Doc2vec model BIBREF19 was pre-trained using Gensim and these word embeddings were applied to initialize deep models and fine-tuned.

Full supplied passage:

```text
A Neural Topic-Attention Model for Medical Term Abbreviation Disambiguation
We conducted a comprehensive comparison with the baseline models, and some of them were never investigated for the abbreviation disambiguation task. We applied traditional features by simply taking the TF-IDF features as the inputs into the classic classifiers. Deep features are also considered: a Doc2vec model BIBREF19 was pre-trained using Gensim and these word embeddings were applied to initialize deep models and fine-tuned.
```

Review: responsiveness ___; completeness ___; cited support ___; paper correctness ___; rationale ___

## Case 13: a9a532399237b514c1227f2d6be8601474e669be

Question: In the paper 'A Neural Topic-Attention Model for Medical Term Abbreviation Disambiguation', What existing dataset is re-examined and corrected for training?

Answer: an existing dataset

Automatic check: exact_quote_presence_only (not entailment).

Citation E1: [paper 1910.14076](../data/raw/qasper-fresh-v1/1910.14076.pdf), PDF page 1.

Selected quote:

We re-examine and correct an existing dataset for training and collect a test set to evaluate the models fairly especially for rare senses.

Full supplied passage:

```text
A Neural Topic-Attention Model for Medical Term Abbreviation Disambiguation
Automated analysis of clinical notes is attracting increasing attention. However, there has not been much work on medical term abbreviation disambiguation. Such abbreviations are abundant, and highly ambiguous, in clinical documents. One of the main obstacles is the lack of large scale, balance labeled data sets. To address the issue, we propose a few-shot learning approach to take advantage of limited labeled data. Specifically, a neural topic-attention model is applied to learn improved contextualized sentence representations for medical term abbreviation disambiguation. Another vital issue is that the existing scarce annotations are noisy and missing. We re-examine and correct an existing dataset for training and collect a test set to evaluate the models fairly especially for rare senses. We train our model on the training set which contains 30 abbreviation terms as categories (on average, 479 samples and 3.
```

Review: responsiveness ___; completeness ___; cited support ___; paper correctness ___; rationale ___

## Case 14: ce2b921e4442a21555d65d8ce4ef7e3bde931dfc

Question: In the paper 'From English To Foreign Languages: Transferring Pre-trained Language Models', What languages are the model transferred to?

Answer: French (fr), Russian (ru), Arabic (ar), Chinese (zh), Hindi (hi), and Vietnamese (vi)

Automatic check: exact_quote_presence_only (not entailment).

Citation E2: [paper 2002.07306](../data/raw/qasper-fresh-v1/2002.07306.pdf), PDF page 4.

Selected quote:

We evaluate our approach for six target languages: French (fr), Russian (ru), Arabic (ar), Chinese (zh), Hindi (hi), and Vietnamese (vi).

Full supplied passage:

```text
From English To Foreign Languages: Transferring Pre-trained Language Models
We evaluate our approach for six target languages: French (fr), Russian (ru), Arabic (ar), Chinese (zh), Hindi (hi), and Vietnamese (vi). These languages belong to four different language families. French, Russian, and Hindi are Indo-European languages, similar to English. Arabic, Chinese, and Vietnamese belong to Afro-Asiatic, Sino-Tibetan, and Austro-Asiatic family respectively. The choice of the six languages also reflects different training conditions depending on the amount of monolingual data. French and Russian, and Arabic can be regarded as high resource languages whereas Hindi has far less data and can be considered as low resource.
```

Review: responsiveness ___; completeness ___; cited support ___; paper correctness ___; rationale ___

## Case 15: 27de1d499348e17fec324d0ef00361a490659988

Question: In the paper 'An Evaluation Dataset for Intent Classification and Out-of-Scope Prediction', What is the size of this dataset?

Answer: 23,700 queries

Automatic check: exact_quote_presence_only (not entailment).

Citation E1: [paper 1909.02027](../data/raw/qasper-fresh-v1/1909.02027.pdf), PDF page 2.

Selected quote:

To do so, we constructed a new dataset with 23,700 queries that are short and unstructured, in the same style made by real users of task-oriented systems.

Full supplied passage:

```text
An Evaluation Dataset for Intent Classification and Out-of-Scope Prediction
This paper fills this gap by analyzing intent classification performance with a focus on out-of-scope handling. To do so, we constructed a new dataset with 23,700 queries that are short and unstructured, in the same style made by real users of task-oriented systems. The queries cover 150 intents, plus out-of-scope queries that do not fall within any of the 150 in-scope intents.
```

Citation E3: [paper 1909.02027](../data/raw/qasper-fresh-v1/1909.02027.pdf), PDF page 2.

Selected quote:

We introduce a new crowdsourced dataset of 23,700 queries, including 22,500 in-scope queries covering 150 intents, which can be grouped into 10 general domains. The dataset also includes 1,200 out-of-scope queries.

Full supplied passage:

```text
An Evaluation Dataset for Intent Classification and Out-of-Scope Prediction
We introduce a new crowdsourced dataset of 23,700 queries, including 22,500 in-scope queries covering 150 intents, which can be grouped into 10 general domains. The dataset also includes 1,200 out-of-scope queries. Table TABREF2 shows examples of the data.
```

Review: responsiveness ___; completeness ___; cited support ___; paper correctness ___; rationale ___

## Case 16: 975e60535724f4149c7488699a199ba2920a062c

Question: In the paper 'How we do things with words: Analyzing text as social and cultural data', What background do they have?

Answer: They have a background in analyzing text as social and cultural data, focusing on defining concepts like hate speech and rumor, and using computational methods to measure these concepts. They also address challenges in marking up data and the limitations of NLP tools.

Automatic check: exact_quote_presence_only (not entailment).

Citation E1: [paper 1907.01468](../data/raw/qasper-fresh-v1/1907.01468.pdf), PDF page 8.

Selected quote:

A core step in many analyses is translating social and cultural concepts (such as hate speech, rumor, or conversion) into measurable quantities. Before we can develop measurements for these concepts (the operationalization step, or the “implementation” step as denoted by BIBREF12 ), we need to define them.

Full supplied passage:

```text
How we do things with words: Analyzing text as social and cultural data
A core step in many analyses is translating social and cultural concepts (such as hate speech, rumor, or conversion) into measurable quantities. Before we can develop measurements for these concepts (the operationalization step, or the “implementation” step as denoted by BIBREF12 ), we need to define them. In the conceptualization phase we often start with questions such as: who are the domain experts, and how have they approached the topic? We are looking for a definition of the concept that is flexible enough to apply on our dataset, yet formal enough for computational research. For example, our introductory study on hate speech BIBREF0 used a statement on hate speech produced by the European Union Court of Human Rights. The goal was not to implement this definition directly in software but to use it as a reference point to anchor subsequent analyses.
```

Citation E3: [paper 1907.01468](../data/raw/qasper-fresh-v1/1907.01468.pdf), PDF page 2.

Selected quote:

In the Reddit case, for example, hate speech is measured, however imperfectly, by the presence of particular words semi-automatically extracted from a machine learning algorithm. Operationalizations are never perfect translations, and are often refined over the course of an investigation, but they are crucial.

Full supplied passage:

```text
How we do things with words: Analyzing text as social and cultural data
These are just a small sample of the many opportunities and challenges faced in computational analyses of textual data. New possibilities and frustrating obstacles emerge at every stage of research, from identification of the research question to interpretation of the results. In this article, we take the reader through a typical research process that involves measuring social or cultural concepts using computational methods, discussing both the opportunities and complications that often arise. In the Reddit case, for example, hate speech is measured, however imperfectly, by the presence of particular words semi-automatically extracted from a machine learning algorithm. Operationalizations are never perfect translations, and are often refined over the course of an investigation, but they are crucial.
```

Review: responsiveness ___; completeness ___; cited support ___; paper correctness ___; rationale ___

## Case 17: f903396d943541a8cc65edefb04ca37814ed30dd

Question: In the paper 'How we do things with words: Analyzing text as social and cultural data', What dataset do they use for analysis?

Answer: hate speech

Automatic check: exact_quote_presence_only (not entailment).

Citation E1: [paper 1907.01468](../data/raw/qasper-fresh-v1/1907.01468.pdf), PDF page 8.

Selected quote:

For example, our introductory study on hate speech BIBREF0 used a statement on hate speech produced by the European Union Court of Human Rights.

Full supplied passage:

```text
How we do things with words: Analyzing text as social and cultural data
A core step in many analyses is translating social and cultural concepts (such as hate speech, rumor, or conversion) into measurable quantities. Before we can develop measurements for these concepts (the operationalization step, or the “implementation” step as denoted by BIBREF12 ), we need to define them. In the conceptualization phase we often start with questions such as: who are the domain experts, and how have they approached the topic? We are looking for a definition of the concept that is flexible enough to apply on our dataset, yet formal enough for computational research. For example, our introductory study on hate speech BIBREF0 used a statement on hate speech produced by the European Union Court of Human Rights. The goal was not to implement this definition directly in software but to use it as a reference point to anchor subsequent analyses.
```

Review: responsiveness ___; completeness ___; cited support ___; paper correctness ___; rationale ___

## Case 18: c9b8d3858c112859eabee54248b874331c48f71b

Question: In the paper 'Copenhagen at CoNLL--SIGMORPHON 2018: Multilingual Inflection in Context with Explicit Morphosyntactic Decoding', What type of inflections are considered?

Answer: lemmas and morphosyntactic descriptions (MSD), word forms

Automatic check: exact_quote_presence_only (not entailment).

Citation E1: [paper 1809.01541](../data/raw/qasper-fresh-v1/1809.01541.pdf), PDF page 1.

Selected quote:

in Track 1 the context is given in terms of word forms, lemmas and morphosyntactic descriptions (MSD); in Track 2 only word forms are available.

Full supplied passage:

```text
Copenhagen at CoNLL--SIGMORPHON 2018: Multilingual Inflection in Context with Explicit Morphosyntactic Decoding
There are two tracks of Task 2 of CoNLL–SIGMORPHON 2018: in Track 1 the context is given in terms of word forms, lemmas and morphosyntactic descriptions (MSD); in Track 2 only word forms are available. See Table TABREF1 for an example. Task 2 is additionally split in three settings based on data size: high, medium and low, with high-resource datasets consisting of up to 70K instances per language, and low-resource datasets consisting of only about 1K instances.
```

Review: responsiveness ___; completeness ___; cited support ___; paper correctness ___; rationale ___

## Case 19: 1eef2d2c296fdd10b08bf7b4ff7792cccf177d3b

Question: In the paper 'Automatic Classification of Pathology Reports using TF-IDF Features', What features are used?

Answer: TF-IDF features

Automatic check: exact_quote_presence_only (not entailment).

Citation E1: [paper 1903.07406](../data/raw/qasper-fresh-v1/1903.07406.pdf), PDF page 3.

Selected quote:

For the first experiment series, training reports are pre-processed, then their TF-IDF features are extracted.

Full supplied passage:

```text
Automatic Classification of Pathology Reports using TF-IDF Features
In this study, we performed two different series of experiments: i) evaluating the performance of TF-IDF features and various machine learning classifiers on the task of predicting primary diagnosis from the text content of a given report, and ii) using TF-IDF and LDA techniques to highlight the important keywords within a report. For the first experiment series, training reports are pre-processed, then their TF-IDF features are extracted. The TF-IDF features and the training labels are used to train different classification models. These different classification models and their hyper-parameters are reported in tab:classifier. The performance of classifiers is measured quantitatively on the test dataset using the evaluation metrics discussed in the previous section. For the second experiment series, a random report is selected and its top 50 keywords are extracted using TF-IDF weights. These 50 keywords are highlighte
```

Review: responsiveness ___; completeness ___; cited support ___; paper correctness ___; rationale ___
