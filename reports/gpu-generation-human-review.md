# GPU generator: 24-answer human review packet

Run: `artifacts/gpu-generation-v1/runs/20260920T145452Z-b1abbfbaf5`. Candidate code: `89781c1`.

Status: pending human review. This packet contains every emitted answer, including potential mistakes. It omits benchmark answerability/reference labels, earlier model answers and automated verdicts. No answer has been marked human-reviewed.

Instructions: evaluate responsiveness, completeness and support from the cited text separately. Use supported / unsupported / unclear for citation support, and explain your judgment. Check the linked full paper for correctness; paper-level truth cannot substitute for support in the actual citation. Record reviewer identity, date and prior exposure in the JSON template. Do not consult benchmark labels before completing the review.

This packet covers emitted claims only, not all refusal decisions. It supports the plan's human claim-support requirement; its completion would not independently authorize model execution, held-out testing or deployment.

## Case 1: dea9e7fe8e47da5e7f31d9b1a46ebe34e731a596

Question: In the paper 'Humor Detection in English-Hindi Code-Mixed Social Media Content : Corpus and Baseline System', What type of system does the baseline classification use?

Proposed answer: support vector machines with radial basis function kernel

[Local source paper](../data/raw/qasper-fresh-v1/1806.05513.pdf)

Cited passage E1:

```text
Humor Detection in English-Hindi Code-Mixed Social Media Content : Corpus and Baseline System
In this paper, we describe a freely available corpus of 3453 English-Hindi code-mixed tweets. The tweets are annotated with humorous(H) and non-humorous(N) tags along with the language tags at the word level. The task of humor identification in social media texts is analyzed as a classification problem and several machine learning classification models are used. The features used in our classification system are n-grams, bag-of-words, common words and hashtags. N-grams when trained with support vector machines with radial basis function kernel performed better than other features and yielded an accuracy of 68.5%. The best accuracy (69.3%) was given by support vector machines with radial basis function kernel.
```

Review: responsiveness ___; completeness ___; cited support ___; paper correctness ___; rationale ___

## Case 2: 955cbea7e5ead36fb89cd6229a97ccb3febcf8bc

Question: In the paper 'Humor Detection in English-Hindi Code-Mixed Social Media Content : Corpus and Baseline System', What experiments were carried out on the corpus?

Proposed answer: 10-fold cross validation on 3543 code-mixed tweets was carried out

[Local source paper](../data/raw/qasper-fresh-v1/1806.05513.pdf)

Cited passage E3:

```text
Humor Detection in English-Hindi Code-Mixed Social Media Content : Corpus and Baseline System
10-fold cross validation on 3543 code-mixed tweets was carried out by dividing the corpus into 10 equal parts with nine parts as training corpus and rest one for testing. Mean accuracy is calculated by taking the average of the accuracy obtained in each iteration of the testing process. Table 2 shows the accuracy for each feature when trained using mentioned classifiers along with the accuracy when all the features are used along with the overall accuracy. Support vector machine with radial basis function kernel and extra tree classifier performs better than other classifiers and yields 69.3% and 67.8% accuracy respectively. The reason kernel SVM yields the best result is because the number of observations is greator than the number of features BIBREF20 . N-grams proved to be the most efficient in all classification models followed by common words and hastags. Bag-of-words feature performed th
```

Review: responsiveness ___; completeness ___; cited support ___; paper correctness ___; rationale ___

## Case 3: 114934e1a1e818630ff33ac5c4cd4be6c6f75bb2

Question: In the paper 'Neural Collective Entity Linking', How effective is their NCEL approach overall?

Proposed answer: Trained on collected Wikipedia hyperlinks, NCEL outperforms the state-of-the-art collective methods across five different datasets

[Local source paper](../data/raw/qasper-fresh-v1/1811.08603.pdf)

Cited passage E2:

```text
Neural Collective Entity Linking
In this paper, we propose a neural model for collective entity linking that is end-to-end trainable. It applies GCN on subgraphs instead of the entire entity graph to efficiently learn features from both local and global information. We design an attention mechanism that endows NCEL robust to noisy data. Trained on collected Wikipedia hyperlinks, NCEL outperforms the state-of-the-art collective methods across five different datasets. Besides, further analysis of the impacts of main modules as well as qualitative results demonstrates its effectiveness.
```

Review: responsiveness ___; completeness ___; cited support ___; paper correctness ___; rationale ___

## Case 4: 1beb4a590fa6127a138f4ed1dd13d5d51cc96809

Question: In the paper 'A Deeper Look into Sarcastic Tweets Using Deep Convolutional Neural Networks', What are the network's baseline features?

Proposed answer: Baseline features have performed significantly better (F1-score: 92.32%) than all other features. Supporting the observations

[Local source paper](../data/raw/qasper-fresh-v1/1610.08815.pdf)

Cited passage E2:

```text
A Deeper Look into Sarcastic Tweets Using Deep Convolutional Neural Networks
5-fold cross-validation has been carried out on Dataset 2. Also for this dataset, we get the best accuracy when we use all features. Baseline features have performed significantly better (F1-score: 92.32%) than all other features. Supporting the observations we have made from the experiments on Dataset 1, we see CNN-SVM outperforming CNN on Dataset 2. However, when we use all the features, CNN alone (F1-score: 89.73%) does not outperform the state of the art BIBREF8 (F1-score: 92.37%). As shown in Table TABREF30 , CNN-SVM on the baseline + sentiment + emotion + personality feature set outperforms the state of the art (F1-score: 94.80%). Among the pre-trained models, the sentiment model performs best (F1-score: 87.00%).
```

Review: responsiveness ___; completeness ___; cited support ___; paper correctness ___; rationale ___

## Case 5: 3a6e843c6c81244c14730295cfb8b865cd7ede46

Question: In the paper 'A Deeper Look into Sarcastic Tweets Using Deep Convolutional Neural Networks', What are the state of the art models?

Proposed answer: F1-score: 92.37%

[Local source paper](../data/raw/qasper-fresh-v1/1610.08815.pdf)

Cited passage E2:

```text
A Deeper Look into Sarcastic Tweets Using Deep Convolutional Neural Networks
5-fold cross-validation has been carried out on Dataset 2. Also for this dataset, we get the best accuracy when we use all features. Baseline features have performed significantly better (F1-score: 92.32%) than all other features. Supporting the observations we have made from the experiments on Dataset 1, we see CNN-SVM outperforming CNN on Dataset 2. However, when we use all the features, CNN alone (F1-score: 89.73%) does not outperform the state of the art BIBREF8 (F1-score: 92.37%). As shown in Table TABREF30 , CNN-SVM on the baseline + sentiment + emotion + personality feature set outperforms the state of the art (F1-score: 94.80%). Among the pre-trained models, the sentiment model performs best (F1-score: 87.00%).
```

Review: responsiveness ___; completeness ___; cited support ___; paper correctness ___; rationale ___

## Case 6: 58c6737070ef559e9220a8d08adc481fdcd53a24

Question: In the paper 'Performance Comparison of Crowdworkers and NLP Tools onNamed-Entity Recognition and Sentiment Analysis of Political Tweets', What measures are used for evaluation?

Proposed answer: We report the experimental results for our two tasks in terms of the correct classification

[Local source paper](../data/raw/qasper-fresh-v1/2002.04181.pdf)

Cited passage E3:

```text
Performance Comparison of Crowdworkers and NLP Tools onNamed-Entity Recognition and Sentiment Analysis of Political Tweets
We report the experimental results for our two tasks in terms of the correct classification rate (CCR). For sentiment analysis, we have a three-class problem (positive, negative, and neutral), where the classes are mutually exclusive. The CCR, averaged for a set of tweets, is defined to be the number of correctly-predicted sentiments over the number of groundtruth sentiments in these tweets. For NER, we consider that each tweet may reference up to four candidates, i.e., targeted entities. The CCR, averaged for a set of tweets, is the number of correctly predicted entities (candidates) over the number of groundtruth entities (candidates) in this set.
```

Review: responsiveness ___; completeness ___; cited support ___; paper correctness ___; rationale ___

## Case 7: 9b7655d39c7a19a23eb8944568eb5618042b9026

Question: In the paper 'Performance Comparison of Crowdworkers and NLP Tools onNamed-Entity Recognition and Sentiment Analysis of Political Tweets', Which toolkits do they use?

Proposed answer: TensiStrength

[Local source paper](../data/raw/qasper-fresh-v1/2002.04181.pdf)

Cited passage E2:

```text
Performance Comparison of Crowdworkers and NLP Tools onNamed-Entity Recognition and Sentiment Analysis of Political Tweets
Among commercial NLP toolkits (e.g., BIBREF14, BIBREF15, BIBREF16), we selected BIBREF17 and BIBREF18 for our experiments, which, to the best of our knowledge, are the only publicly accessible commercial APIs for the task of entity-level sentiment analysis that is agnostic to the text domain. We also report results of TensiStrength BIBREF13, TwitterNLP BIBREF6, BIBREF19, CogComp-NLP BIBREF20, and Stanford NLP NER BIBREF21.
```

Review: responsiveness ___; completeness ___; cited support ___; paper correctness ___; rationale ___

## Case 8: 2ee715c7c6289669f11a79743a6b2b696073805d

Question: In the paper 'Automated News Suggestions for Populating Wikipedia Entity Pages', What baseline model is used?

Proposed answer: B1. The first baseline uses only the salience-based features by Dunietz and Gillick

[Local source paper](../data/raw/qasper-fresh-v1/1703.10344.pdf)

Cited passage E1:

```text
Automated News Suggestions for Populating Wikipedia Entity Pages
B1. The first baseline uses only the salience-based features by Dunietz and Gillick BIBREF11 .
```

Review: responsiveness ___; completeness ___; cited support ___; paper correctness ___; rationale ___

## Case 9: 984fc3e726848f8f13dfe72b89e3770d00c3a1af

Question: In the paper 'Automated News Suggestions for Populating Wikipedia Entity Pages', What features are used to represent the novelty of news articles to entity pages?

Proposed answer: novelty of news articles for an entity page

[Local source paper](../data/raw/qasper-fresh-v1/1703.10344.pdf)

Cited passage E1:

```text
Automated News Suggestions for Populating Wikipedia Entity Pages
In this work, we have proposed an automated approach for the novel task of suggesting news articles to Wikipedia entity pages to facilitate Wikipedia updating. The process consists of two stages. In the first stage, article–entity placement, we suggest news articles to entity pages by considering three main factors, such as entity salience in a news article, relative authority and novelty of news articles for an entity page. In the second stage, article–section placement, we determine the best fitting section in an entity page. Here, we remedy the problem of incomplete entity section profiles by constructing section templates for specific entity classes. This allows us to add missing sections to entity pages. We carry out an extensive experimental evaluation on 351,983 news articles and 73,734 entities coming from 27 distinct entity classes. For the first stage, we achieve an overall performance with P=0.93, R=0.514 and F
```

Review: responsiveness ___; completeness ___; cited support ___; paper correctness ___; rationale ___

## Case 10: 5c6fa86757410aee6f5a0762328637de03a569e9

Question: In the paper 'Deep Learning for Detecting Cyberbullying Across Multiple Social Media Platforms', What were their performance results?

Proposed answer: DNN based models coupled with transfer learning beat the best-known results for all three datasets

[Local source paper](../data/raw/qasper-fresh-v1/1801.06482.pdf)

Cited passage E3:

```text
Deep Learning for Detecting Cyberbullying Across Multiple Social Media Platforms
DNN based models coupled with transfer learning beat the best-known results for all three datasets. Previous best F1 scores for Wikipedia BIBREF4 and Twitter BIBREF8 datasets were 0.68 and 0.93 respectively. We achieve F1 scores of 0.94 for both these datasets using BLSTM with attention and feature level transfer learning (Table TABREF25 ). For Formspring dataset, authors have not reported F1 score. Their method has accuracy score of 78.5% BIBREF2 . We achieve F1 score of 0.95 with accuracy score of 98% for the same dataset.
```

Review: responsiveness ___; completeness ___; cited support ___; paper correctness ___; rationale ___

## Case 11: 7e38e0279a620d3df05ab9b5e2795044f18d4471

Question: In the paper 'Deep Learning for Detecting Cyberbullying Across Multiple Social Media Platforms', What cyberbulling topics did they address?

Proposed answer: Second, they address just one topic of cyberbullying. Third, they rely on carefully handcrafted features

[Local source paper](../data/raw/qasper-fresh-v1/1801.06482.pdf)

Cited passage E3:

```text
Deep Learning for Detecting Cyberbullying Across Multiple Social Media Platforms
Harassment by cyberbullies is a significant phenomenon on the social media. Existing works for cyberbullying detection have at least one of the following three bottlenecks. First, they target only one particular social media platform (SMP). Second, they address just one topic of cyberbullying. Third, they rely on carefully handcrafted features of the data. We show that deep learning based models can overcome all three bottlenecks. Knowledge learned by these models on one dataset can be transferred to other datasets. We performed extensive experiments using three real-world datasets: Formspring (12k posts), Twitter (16k posts), and Wikipedia(100k posts). Our experiments provide several useful insights about cyberbullying detection. To the best of our knowledge, this is the first work that systematically analyzes cyberbullying detection on various topics across multiple SMPs using deep learning based models
```

Review: responsiveness ___; completeness ___; cited support ___; paper correctness ___; rationale ___

## Case 12: 551457ed34ca7fc0878c85bc664b135c21059b58

Question: In the paper 'Active Learning for Speech Recognition: the Power of Gradients', Which dataset do they use?

Proposed answer: 190 hours

[Local source paper](../data/raw/qasper-fresh-v1/1612.03226.pdf)

Cited passage E3:

```text
Active Learning for Speech Recognition: the Power of Gradients
A base model, INLINEFORM0 , is trained on 190 hours ( INLINEFORM1 100K instances) of transcribed speech data. Then, it selects a subset of a 1,700-hour ( INLINEFORM2 1.1M instances) unlabeled dataset. We query labels for the selected subset and incorporate them into training. Learning rates are tuned on a small validation set of 2048 instances. The trained model is then tested on a 156-hour ( INLINEFORM3 100K instances) test set and we report CTC loss, Character Error Rate (CER) and Word Error Rate (WER).
```

Review: responsiveness ___; completeness ___; cited support ___; paper correctness ___; rationale ___

## Case 13: b7c3f3942a07c118e57130bc4c3ec4adc431d725

Question: In the paper 'Applying a Pre-trained Language Model to Spanish Twitter Humor Prediction', What did the best systems use for their model?

Proposed answer: We tied the embedding weights

[Local source paper](../data/raw/qasper-fresh-v1/1907.03187.pdf)

Cited passage E3:

```text
Applying a Pre-trained Language Model to Spanish Twitter Humor Prediction
We train the LM using a 90/10 training/validation split, reporting the validation loss and accuracy of next-word prediction on the validation set. For the LM, we selected an ASGD Weight-Dropped Long Short Term Memory (AWD_LSTM, described in Merity et al. BIBREF5 ) model included in Fast.ai. We replaced the typical Long Short Term Memory (LSTM) units with Quasi Recurrent Neural Network (QRNN, described in Bradbury et al. BIBREF6 ) units. Our network has 2304 hidden-states, 3 layers and a softmax layer to predict the next-word. We tied the embedding weights BIBREF7 on the encoder and decoder for training. We performed some simple tests with LSTM units and a Transformer Language model, finding all models were similar in performance during LM training. We thus chose to use QRNN units due to improved training speed compared to the alternatives. This model has about 60 million trainable parameters.
```

Review: responsiveness ___; completeness ___; cited support ___; paper correctness ___; rationale ___

## Case 14: a5505e25ee9ae84090e1442034ddbb3cedabcf04

Question: In the paper 'Applying a Pre-trained Language Model to Spanish Twitter Humor Prediction', What were their results on the classification and regression tasks

Proposed answer: Our entry into the HAHA 2019 Challenge placed $3^{rd}$ in the classification task and $2^{nd}$

[Local source paper](../data/raw/qasper-fresh-v1/1907.03187.pdf)

Cited passage E2:

```text
Applying a Pre-trained Language Model to Spanish Twitter Humor Prediction
Our entry into the HAHA 2019 Challenge placed $3^{rd}$ in the classification task and $2^{nd}$ in the regression task. We describe our system and innovations, as well as comparing our results to a Naive Bayes baseline. A large Twitter based corpus allowed us to train a language model from scratch focused on Spanish and transfer that knowledge to our competition model. To overcome the inherent errors in some labels we reduce our class confidence with label smoothing in the loss function. All the code for our project is included in a GitHub repository for easy reference and to enable replication by others.
```

Review: responsiveness ___; completeness ___; cited support ___; paper correctness ___; rationale ___

## Case 15: fe1dcd6ef1f8618bbceee418f07cafe63a8efe08

Question: In the paper 'VAIS ASR: Building a conversational speech recognition system using language model combination', What is the language model combination technique used in the paper?

Proposed answer: language models combination techniques

[Local source paper](../data/raw/qasper-fresh-v1/1910.05603.pdf)

Cited passage E1:

```text
VAIS ASR: Building a conversational speech recognition system using language model combination
Automatic Speech Recognition (ASR) systems have been evolving quickly and reaching human parity in certain cases. The systems usually perform pretty well on reading style and clean speech, however, most of the available systems suffer from situation where the speaking style is conversation and in noisy environments. It is not straight-forward to tackle such problems due to difficulties in data collection for both speech and text. In this paper, we attempt to mitigate the problems using language models combination techniques that allows us to utilize both large amount of writing style text and small number of conversation text data. Evaluation on the VLSP 2019 ASR challenges showed that our system achieved 4.85% WER on the VLSP 2018 and 15.09% WER on the VLSP 2019 data sets.
```

Review: responsiveness ___; completeness ___; cited support ___; paper correctness ___; rationale ___

## Case 16: 0ee73909ac638903da4a0e5565c8571fc794ab96

Question: In the paper 'Improving the Performance of Neural Machine Translation Involving Morphologically Rich Languages', How were the human judgements assembled?

Proposed answer: A group of 50 native people who were well-versed in both English and Tamil languages

[Local source paper](../data/raw/qasper-fresh-v1/1612.02482.pdf)

Cited passage E2:

```text
Improving the Performance of Neural Machine Translation Involving Morphologically Rich Languages
To ensure that the increase in BLEU score correlated to actual increase in performance of translation, human evaluation metrics like adequacy, precision and ranking values (between RNNSearch and RNNMorph outputs) were estimated in Table TABREF30 . A group of 50 native people who were well-versed in both English and Tamil languages acted as annotators for the evaluation. A collection of samples of about 100 sentences were taken from the test set results for comparison. This set included a randomized selection of the translation results to ensure the objectivity of evaluation. Fluency and adequacy results for the RNNMorph results are tabulated. Adequacy rating was calculated on a 5-point scale of how much of the meaning is conveyed by the translation (All, Most, Much, Little, None). The fluency rating was calculated based on grammatical correctness on a 5-point scale of (Flawless, Good, Non-n
```

Review: responsiveness ___; completeness ___; cited support ___; paper correctness ___; rationale ___

## Case 17: e35a7f9513ff1cc0f0520f1d4ad9168a47dc18bb

Question: In the paper 'Combining Advanced Methods in Japanese-Vietnamese Neural Machine Translation', what was the baseline?

Proposed answer: For the baseline systems, the training data includes KyTea-segmented Japanese texts and pyvi-segmented Vietnamese texts

[Local source paper](../data/raw/qasper-fresh-v1/1805.07133.pdf)

Cited passage E3:

```text
Combining Advanced Methods in Japanese-Vietnamese Neural Machine Translation
Baseline. For the baseline systems, the training data includes KyTea-segmented Japanese texts and pyvi-segmented Vietnamese texts. For comparison purpose, we build two baseline systems for each direction: one is use the traditional phrase-based statistical machine translation (SMT), the other one is the NMT system. Although our training set is small but we find that the NMT systems (2) are still more effective than the phrase-based SMT models (1) in both translation directions.
```

Review: responsiveness ___; completeness ___; cited support ___; paper correctness ___; rationale ___

## Case 18: 219af68afeaecabdfd279f439f10ba7c231736e4

Question: In the paper 'Combining Advanced Methods in Japanese-Vietnamese Neural Machine Translation', what japanese-vietnamese dataset do they use?

Proposed answer: Japanese-Vietnamese parallel corpus

[Local source paper](../data/raw/qasper-fresh-v1/1805.07133.pdf)

Cited passage E1:

```text
Combining Advanced Methods in Japanese-Vietnamese Neural Machine Translation
The data augmentation methods has been applied only for the Japanese INLINEFORM0 Vietnamese direction. For Back Translation, we use Vietnamese monolingual data from VNESEcorpus of DongDu which includes 349578 sentences. We shuffle the lines of VNESEcorpus corpus and take out the first 106758 sentences (the same as the number of sentence pairs in the original parallel corpus). For Mix-Source, instead of using a subsampled monolingual corpus, we use the Vietnamese part of the Japanese-Vietnamese parallel corpus in order to learn the multilingual information in the same domain. Our datasets are listed in Table TABREF14 .
```

Review: responsiveness ___; completeness ___; cited support ___; paper correctness ___; rationale ___

## Case 19: 3116453e35352a3a90ee5b12246dc7f2e60cfc59

Question: In the paper 'A Neural Topic-Attention Model for Medical Term Abbreviation Disambiguation', To what baseline models is proposed model compared?

Proposed answer: We applied traditional features by simply taking the TF-IDF features as the inputs into the

[Local source paper](../data/raw/qasper-fresh-v1/1910.14076.pdf)

Cited passage E3:

```text
A Neural Topic-Attention Model for Medical Term Abbreviation Disambiguation
We conducted a comprehensive comparison with the baseline models, and some of them were never investigated for the abbreviation disambiguation task. We applied traditional features by simply taking the TF-IDF features as the inputs into the classic classifiers. Deep features are also considered: a Doc2vec model BIBREF19 was pre-trained using Gensim and these word embeddings were applied to initialize deep models and fine-tuned.
```

Review: responsiveness ___; completeness ___; cited support ___; paper correctness ___; rationale ___

## Case 20: a9a532399237b514c1227f2d6be8601474e669be

Question: In the paper 'A Neural Topic-Attention Model for Medical Term Abbreviation Disambiguation', What existing dataset is re-examined and corrected for training?

Proposed answer: We re-examine and correct an existing dataset for training and collect a test set to

[Local source paper](../data/raw/qasper-fresh-v1/1910.14076.pdf)

Cited passage E1:

```text
A Neural Topic-Attention Model for Medical Term Abbreviation Disambiguation
Automated analysis of clinical notes is attracting increasing attention. However, there has not been much work on medical term abbreviation disambiguation. Such abbreviations are abundant, and highly ambiguous, in clinical documents. One of the main obstacles is the lack of large scale, balance labeled data sets. To address the issue, we propose a few-shot learning approach to take advantage of limited labeled data. Specifically, a neural topic-attention model is applied to learn improved contextualized sentence representations for medical term abbreviation disambiguation. Another vital issue is that the existing scarce annotations are noisy and missing. We re-examine and correct an existing dataset for training and collect a test set to evaluate the models fairly especially for rare senses. We train our model on the training set which contains 30 abbreviation terms as categories (on average, 479 samples and 3.
```

Review: responsiveness ___; completeness ___; cited support ___; paper correctness ___; rationale ___

## Case 21: ce2b921e4442a21555d65d8ce4ef7e3bde931dfc

Question: In the paper 'From English To Foreign Languages: Transferring Pre-trained Language Models', What languages are the model transferred to?

Proposed answer: French (fr), Russian (ru), Arabic (ar), Chinese (zh), Hindi (hi), and Vietnamese (vi). These languages

[Local source paper](../data/raw/qasper-fresh-v1/2002.07306.pdf)

Cited passage E2:

```text
From English To Foreign Languages: Transferring Pre-trained Language Models
We evaluate our approach for six target languages: French (fr), Russian (ru), Arabic (ar), Chinese (zh), Hindi (hi), and Vietnamese (vi). These languages belong to four different language families. French, Russian, and Hindi are Indo-European languages, similar to English. Arabic, Chinese, and Vietnamese belong to Afro-Asiatic, Sino-Tibetan, and Austro-Asiatic family respectively. The choice of the six languages also reflects different training conditions depending on the amount of monolingual data. French and Russian, and Arabic can be regarded as high resource languages whereas Hindi has far less data and can be considered as low resource.
```

Review: responsiveness ___; completeness ___; cited support ___; paper correctness ___; rationale ___

## Case 22: 27de1d499348e17fec324d0ef00361a490659988

Question: In the paper 'An Evaluation Dataset for Intent Classification and Out-of-Scope Prediction', What is the size of this dataset?

Proposed answer: 23,700 queries

[Local source paper](../data/raw/qasper-fresh-v1/1909.02027.pdf)

Cited passage E1:

```text
An Evaluation Dataset for Intent Classification and Out-of-Scope Prediction
This paper fills this gap by analyzing intent classification performance with a focus on out-of-scope handling. To do so, we constructed a new dataset with 23,700 queries that are short and unstructured, in the same style made by real users of task-oriented systems. The queries cover 150 intents, plus out-of-scope queries that do not fall within any of the 150 in-scope intents.
```

Review: responsiveness ___; completeness ___; cited support ___; paper correctness ___; rationale ___

## Case 23: c9b8d3858c112859eabee54248b874331c48f71b

Question: In the paper 'Copenhagen at CoNLL--SIGMORPHON 2018: Multilingual Inflection in Context with Explicit Morphosyntactic Decoding', What type of inflections are considered?

Proposed answer: inflected word form

[Local source paper](../data/raw/qasper-fresh-v1/1809.01541.pdf)

Cited passage E2:

```text
Copenhagen at CoNLL--SIGMORPHON 2018: Multilingual Inflection in Context with Explicit Morphosyntactic Decoding
This paper describes our approach and results for Task 2 of the CoNLL–SIGMORPHON 2018 shared task on universal morphological reinflection BIBREF0 . The task is to generate an inflected word form given its lemma and the context in which it occurs.
```

Review: responsiveness ___; completeness ___; cited support ___; paper correctness ___; rationale ___

## Case 24: 1eef2d2c296fdd10b08bf7b4ff7792cccf177d3b

Question: In the paper 'Automatic Classification of Pathology Reports using TF-IDF Features', What features are used?

Proposed answer: TF-IDF features

[Local source paper](../data/raw/qasper-fresh-v1/1903.07406.pdf)

Cited passage E1:

```text
Automatic Classification of Pathology Reports using TF-IDF Features
In this study, we performed two different series of experiments: i) evaluating the performance of TF-IDF features and various machine learning classifiers on the task of predicting primary diagnosis from the text content of a given report, and ii) using TF-IDF and LDA techniques to highlight the important keywords within a report. For the first experiment series, training reports are pre-processed, then their TF-IDF features are extracted. The TF-IDF features and the training labels are used to train different classification models. These different classification models and their hyper-parameters are reported in tab:classifier. The performance of classifiers is measured quantitatively on the test dataset using the evaluation metrics discussed in the previous section. For the second experiment series, a random report is selected and its top 50 keywords are extracted using TF-IDF weights. These 50 keywords are highlighte
```

Review: responsiveness ___; completeness ___; cited support ___; paper correctness ___; rationale ___
