# Intact-paragraph experiment: emitted-answer review packet

Run: `artifacts/intact-passage-v1/runs/20260924T210922Z-e266a7a622`. Status: unreviewed. All emitted answers are included; benchmark references and answerability labels are omitted. No independent human review has occurred.

Evaluate responsiveness, completeness, support and paper-level correctness separately. An exact quote can be real without entailing the answer. Page numbers are physical PDF pages.

## Case 1: dea9e7fe8e47da5e7f31d9b1a46ebe34e731a596

Question: In the paper 'Humor Detection in English-Hindi Code-Mixed Social Media Content : Corpus and Baseline System', What type of system does the baseline classification use?

Answer: support vector machines with radial basis function kernel

Automatic check: exact_quote_presence_only (not entailment).

Citation E1.S5 (E1): [paper 1806.05513](../data/raw/qasper-fresh-v1/1806.05513.pdf), PDF page 4.

Selected quote:

N-grams when trained with support vector machines with radial basis function kernel performed better than other features and yielded an accuracy of 68.5%.

Full supplied passage:

```text
Humor Detection in English-Hindi Code-Mixed Social Media Content : Corpus and Baseline System
In this paper, we describe a freely available corpus of 3453 English-Hindi code-mixed tweets. The tweets are annotated with humorous(H) and non-humorous(N) tags along with the language tags at the word level. The task of humor identification in social media texts is analyzed as a classification problem and several machine learning classification models are used. The features used in our classification system are n-grams, bag-of-words, common words and hashtags. N-grams when trained with support vector machines with radial basis function kernel performed better than other features and yielded an accuracy of 68.5%. The best accuracy (69.3%) was given by support vector machines with radial basis function kernel.
```

Citation E1.S6 (E1): [paper 1806.05513](../data/raw/qasper-fresh-v1/1806.05513.pdf), PDF page 4.

Selected quote:

The best accuracy (69.3%) was given by support vector machines with radial basis function kernel.

Full supplied passage:

```text
Humor Detection in English-Hindi Code-Mixed Social Media Content : Corpus and Baseline System
In this paper, we describe a freely available corpus of 3453 English-Hindi code-mixed tweets. The tweets are annotated with humorous(H) and non-humorous(N) tags along with the language tags at the word level. The task of humor identification in social media texts is analyzed as a classification problem and several machine learning classification models are used. The features used in our classification system are n-grams, bag-of-words, common words and hashtags. N-grams when trained with support vector machines with radial basis function kernel performed better than other features and yielded an accuracy of 68.5%. The best accuracy (69.3%) was given by support vector machines with radial basis function kernel.
```

Review: responsiveness ___; completeness ___; cited support ___; paper correctness ___; rationale ___

## Case 2: 955cbea7e5ead36fb89cd6229a97ccb3febcf8bc

Question: In the paper 'Humor Detection in English-Hindi Code-Mixed Social Media Content : Corpus and Baseline System', What experiments were carried out on the corpus?

Answer: 10-fold cross validation on 3543 code-mixed tweets was carried out by dividing the corpus into 10 equal parts with nine parts as training corpus and rest one for testing.

Automatic check: exact_quote_presence_only (not entailment).

Citation E3.S1 (E3): [paper 1806.05513](../data/raw/qasper-fresh-v1/1806.05513.pdf), PDF page 4.

Selected quote:

10-fold cross validation on 3543 code-mixed tweets was carried out by dividing the corpus into 10 equal parts with nine parts as training corpus and rest one for testing.

Full supplied passage:

```text
Humor Detection in English-Hindi Code-Mixed Social Media Content : Corpus and Baseline System
10-fold cross validation on 3543 code-mixed tweets was carried out by dividing the corpus into 10 equal parts with nine parts as training corpus and rest one for testing. Mean accuracy is calculated by taking the average of the accuracy obtained in each iteration of the testing process. Table 2 shows the accuracy for each feature when trained using mentioned classifiers along with the accuracy when all the features are used along with the overall accuracy. Support vector machine with radial basis function kernel and extra tree classifier performs better than other classifiers and yields 69.3% and 67.8% accuracy respectively. The reason kernel SVM yields the best result is because the number of observations is greator than the number of features BIBREF20 . N-grams proved to be the most efficient in all classification models followed by common words and hastags. Bag-of-words feature performed the worst in SVM, random forest and extra tree classifier but yielded better result in naive bayes classifiers. Accuracies mentioned in table 2 were calculated using fine tuning of model parameters using grid search.
```

Review: responsiveness ___; completeness ___; cited support ___; paper correctness ___; rationale ___

## Case 3: 114934e1a1e818630ff33ac5c4cd4be6c6f75bb2

Question: In the paper 'Neural Collective Entity Linking', How effective is their NCEL approach overall?

Answer: NCEL outperforms the state-of-the-art collective methods across five different datasets.

Automatic check: exact_quote_presence_only (not entailment).

Citation E2.S4 (E2): [paper 1811.08603](../data/raw/qasper-fresh-v1/1811.08603.pdf), PDF page 10.

Selected quote:

Trained on collected Wikipedia hyperlinks, NCEL outperforms the state-of-the-art collective methods across five different datasets.

Full supplied passage:

```text
Neural Collective Entity Linking
In this paper, we propose a neural model for collective entity linking that is end-to-end trainable. It applies GCN on subgraphs instead of the entire entity graph to efficiently learn features from both local and global information. We design an attention mechanism that endows NCEL robust to noisy data. Trained on collected Wikipedia hyperlinks, NCEL outperforms the state-of-the-art collective methods across five different datasets. Besides, further analysis of the impacts of main modules as well as qualitative results demonstrates its effectiveness.
```

Review: responsiveness ___; completeness ___; cited support ___; paper correctness ___; rationale ___

## Case 4: 1beb4a590fa6127a138f4ed1dd13d5d51cc96809

Question: In the paper 'A Deeper Look into Sarcastic Tweets Using Deep Convolutional Neural Networks', What are the network's baseline features?

Answer: features extracted from the pre-trained models

Automatic check: exact_quote_presence_only (not entailment).

Citation E1.S1 (E1): [paper 1610.08815](../data/raw/qasper-fresh-v1/1610.08815.pdf), PDF page 8.

Selected quote:

In another setting, we use the features extracted from the pre-trained models as the static channels of features in the CNN of the baseline method.

Full supplied passage:

```text
A Deeper Look into Sarcastic Tweets Using Deep Convolutional Neural Networks
In another setting, we use the features extracted from the pre-trained models as the static channels of features in the CNN of the baseline method. These features are appended to the hidden layer of the baseline CNN, preceding the final output softmax layer.
```

Review: responsiveness ___; completeness ___; cited support ___; paper correctness ___; rationale ___

## Case 5: 3a6e843c6c81244c14730295cfb8b865cd7ede46

Question: In the paper 'A Deeper Look into Sarcastic Tweets Using Deep Convolutional Neural Networks', What are the state of the art models?

Answer: CNN-SVM on the baseline + sentiment + emotion + personality feature set

Automatic check: exact_quote_presence_only (not entailment).

Citation E2.S6 (E2): [paper 1610.08815](../data/raw/qasper-fresh-v1/1610.08815.pdf), PDF page 8.

Selected quote:

As shown in Table TABREF30 , CNN-SVM on the baseline + sentiment + emotion + personality feature set outperforms the state of the art (F1-score: 94.80%).

Full supplied passage:

```text
A Deeper Look into Sarcastic Tweets Using Deep Convolutional Neural Networks
5-fold cross-validation has been carried out on Dataset 2. Also for this dataset, we get the best accuracy when we use all features. Baseline features have performed significantly better (F1-score: 92.32%) than all other features. Supporting the observations we have made from the experiments on Dataset 1, we see CNN-SVM outperforming CNN on Dataset 2. However, when we use all the features, CNN alone (F1-score: 89.73%) does not outperform the state of the art BIBREF8 (F1-score: 92.37%). As shown in Table TABREF30 , CNN-SVM on the baseline + sentiment + emotion + personality feature set outperforms the state of the art (F1-score: 94.80%). Among the pre-trained models, the sentiment model performs best (F1-score: 87.00%).
```

Review: responsiveness ___; completeness ___; cited support ___; paper correctness ___; rationale ___

## Case 6: 58c6737070ef559e9220a8d08adc481fdcd53a24

Question: In the paper 'Performance Comparison of Crowdworkers and NLP Tools onNamed-Entity Recognition and Sentiment Analysis of Political Tweets', What measures are used for evaluation?

Answer: correct classification rate (CCR)

Automatic check: exact_quote_presence_only (not entailment).

Citation E3.S1 (E3): [paper 2002.04181](../data/raw/qasper-fresh-v1/2002.04181.pdf), PDF page 2.

Selected quote:

We report the experimental results for our two tasks in terms of the correct classification rate (CCR).

Full supplied passage:

```text
Performance Comparison of Crowdworkers and NLP Tools onNamed-Entity Recognition and Sentiment Analysis of Political Tweets
We report the experimental results for our two tasks in terms of the correct classification rate (CCR). For sentiment analysis, we have a three-class problem (positive, negative, and neutral), where the classes are mutually exclusive. The CCR, averaged for a set of tweets, is defined to be the number of correctly-predicted sentiments over the number of groundtruth sentiments in these tweets. For NER, we consider that each tweet may reference up to four candidates, i.e., targeted entities. The CCR, averaged for a set of tweets, is the number of correctly predicted entities (candidates) over the number of groundtruth entities (candidates) in this set.
```

Review: responsiveness ___; completeness ___; cited support ___; paper correctness ___; rationale ___

## Case 7: 9b7655d39c7a19a23eb8944568eb5618042b9026

Question: In the paper 'Performance Comparison of Crowdworkers and NLP Tools onNamed-Entity Recognition and Sentiment Analysis of Political Tweets', Which toolkits do they use?

Answer: BIBREF17 and BIBREF18

Automatic check: exact_quote_presence_only (not entailment).

Citation E2.S1 (E2): [paper 2002.04181](../data/raw/qasper-fresh-v1/2002.04181.pdf), PDF page 2.

Selected quote:

Among commercial NLP toolkits (e.g., BIBREF14, BIBREF15, BIBREF16), we selected BIBREF17 and BIBREF18 for our experiments, which, to the best of our knowledge, are the only publicly accessible commercial APIs for the task of entity-level sentiment analysis that is agnostic

Full supplied passage:

```text
Performance Comparison of Crowdworkers and NLP Tools onNamed-Entity Recognition and Sentiment Analysis of Political Tweets
Among commercial NLP toolkits (e.g., BIBREF14, BIBREF15, BIBREF16), we selected BIBREF17 and BIBREF18 for our experiments, which, to the best of our knowledge, are the only publicly accessible commercial APIs for the task of entity-level sentiment analysis that is agnostic to the text domain. We also report results of TensiStrength BIBREF13, TwitterNLP BIBREF6, BIBREF19, CogComp-NLP BIBREF20, and Stanford NLP NER BIBREF21.
```

Review: responsiveness ___; completeness ___; cited support ___; paper correctness ___; rationale ___

## Case 8: 55569d0a4586d20c01268a80a7e31a17a18198e2

Question: In the paper 'Zero-shot Reading Comprehension by Cross-lingual Transfer Learning with Multi-lingual Language Representation Model', what does the model learn in zero-shot setting?

Answer: In the zero-shot setting, the model learns to perform reading comprehension tasks in languages it was not explicitly trained on.

Automatic check: exact_quote_presence_only (not entailment).

Citation E2.S1 (E2): [paper 1909.09587](../data/raw/qasper-fresh-v1/1909.09587.pdf), PDF page 1.

Selected quote:

Multi-BERT has showcased its ability to enable cross-lingual zero-shot learning on the natural language understanding tasks including XNLI BIBREF19, NER, POS, Dependency Parsing, and so on.

Full supplied passage:

```text
Zero-shot Reading Comprehension by Cross-lingual Transfer Learning with Multi-lingual Language Representation Model
Multi-BERT has showcased its ability to enable cross-lingual zero-shot learning on the natural language understanding tasks including XNLI BIBREF19, NER, POS, Dependency Parsing, and so on. We now seek to know if a pre-trained multi-BERT has ability to solve RC tasks in the zero-shot setting.
```

Review: responsiveness ___; completeness ___; cited support ___; paper correctness ___; rationale ___

## Case 9: b1ce129678e37070e69f01332f1a8587e18e06b0

Question: In the paper 'Sentiment Analysis of Twitter Data for Predicting Stock Market Movements', What dataset is used to train the model?

Answer: Microsoft stock price data

Automatic check: exact_quote_presence_only (not entailment).

Citation E1.S1 (E1): [paper 1610.09225](../data/raw/qasper-fresh-v1/1610.09225.pdf), PDF page 3.

Selected quote:

The stock price data of Microsoft are labeled suitably for training using a simple program.

Full supplied passage:

```text
Sentiment Analysis of Twitter Data for Predicting Stock Market Movements
The stock price data of Microsoft are labeled suitably for training using a simple program. If the previous day stock price is more than the current day stock price, the current day is marked with a numeric value of 0, else marked with a numeric value of 1. Now, this correlation analysis turns out to be a classification problem. The total positive, negative and neutral emotions in tweets in a 3 day period are calculated successively which are used as features for the classifier model and the output is the labeled next day value of stock 0 or 1.The window size is experimented and best results are achieved when the sentiment values precede 3 days to the stock price. A total of 355 instances, each with 3 attributes are fed to the classifier with a split proportions of 80% train dataset and the remaining dataset for testing. The accuracy of the classifier is discussed in the results section.
```

Review: responsiveness ___; completeness ___; cited support ___; paper correctness ___; rationale ___

## Case 10: 2ee715c7c6289669f11a79743a6b2b696073805d

Question: In the paper 'Automated News Suggestions for Populating Wikipedia Entity Pages', What baseline model is used?

Answer: salience-based features by Dunietz and Gillick

Automatic check: exact_quote_presence_only (not entailment).

Citation E1.S2 (E1): [paper 1703.10344](../data/raw/qasper-fresh-v1/1703.10344.pdf), PDF page 8.

Selected quote:

The first baseline uses only the salience-based features by Dunietz and Gillick BIBREF11 .

Full supplied passage:

```text
Automated News Suggestions for Populating Wikipedia Entity Pages
B1. The first baseline uses only the salience-based features by Dunietz and Gillick BIBREF11 .
```

Review: responsiveness ___; completeness ___; cited support ___; paper correctness ___; rationale ___

## Case 11: 984fc3e726848f8f13dfe72b89e3770d00c3a1af

Question: In the paper 'Automated News Suggestions for Populating Wikipedia Entity Pages', What features are used to represent the novelty of news articles to entity pages?

Answer: the novelty of an article w.r.t the already existing entity profile, measured by the KL divergence between the language model of the article and articles in the entity page, combined with the entity overlap.

Automatic check: exact_quote_presence_only (not entailment).

Citation E2.S1 (E2): [paper 1703.10344](../data/raw/qasper-fresh-v1/1703.10344.pdf), PDF page 5.

Selected quote:

Given an entity INLINEFORM0 and the already added news references INLINEFORM1 up to year INLINEFORM2 , the novelty of INLINEFORM3 at year INLINEFORM4 is measured by the KL divergence between the language model of INLINEFORM5 and articles in INLINEFORM6 .

Full supplied passage:

```text
Automated News Suggestions for Populating Wikipedia Entity Pages
Given an entity INLINEFORM0 and the already added news references INLINEFORM1 up to year INLINEFORM2 , the novelty of INLINEFORM3 at year INLINEFORM4 is measured by the KL divergence between the language model of INLINEFORM5 and articles in INLINEFORM6 . We combine this measure with the entity overlap of INLINEFORM7 and INLINEFORM8 . The novelty value of INLINEFORM9 is given by the minimal divergence value. Low scores indicate low novelty for the entity profile INLINEFORM10 .
```

Citation E2.S2 (E2): [paper 1703.10344](../data/raw/qasper-fresh-v1/1703.10344.pdf), PDF page 5.

Selected quote:

We combine this measure with the entity overlap of INLINEFORM7 and INLINEFORM8 .

Full supplied passage:

```text
Automated News Suggestions for Populating Wikipedia Entity Pages
Given an entity INLINEFORM0 and the already added news references INLINEFORM1 up to year INLINEFORM2 , the novelty of INLINEFORM3 at year INLINEFORM4 is measured by the KL divergence between the language model of INLINEFORM5 and articles in INLINEFORM6 . We combine this measure with the entity overlap of INLINEFORM7 and INLINEFORM8 . The novelty value of INLINEFORM9 is given by the minimal divergence value. Low scores indicate low novelty for the entity profile INLINEFORM10 .
```

Review: responsiveness ___; completeness ___; cited support ___; paper correctness ___; rationale ___

## Case 12: 70a1b0f9f26f1b82c14783f1b76dfb5400444aa4

Question: In the paper 'State-of-the-Art Vietnamese Word Segmentation', How successful are the approaches used to solve word segmentation in Vietnamese?

Answer: According to our observation, there are achievements and limitations in existing Vietnamese word segmentation systems, but the success varies due to the lack of comprehensive review.

Automatic check: exact_quote_presence_only (not entailment).

Citation E1.S5 (E1): [paper 1906.07662](../data/raw/qasper-fresh-v1/1906.07662.pdf), PDF page 1.

Selected quote:

According to our observation, this study also reports a few of achivements and limitations in existing Vietnamese word segmentation systems.

Full supplied passage:

```text
State-of-the-Art Vietnamese Word Segmentation
Word segmentation is the first step of any tasks in Vietnamese language processing. This paper reviews stateof-the-art approaches and systems for word segmentation in Vietnamese. To have an overview of all stages from building corpora to developing toolkits, we discuss building the corpus stage, approaches applied to solve the word segmentation and existing toolkits to segment words in Vietnamese sentences. In addition, this study shows clearly the motivations on building corpus and implementing machine learning techniques to improve the accuracy for Vietnamese word segmentation. According to our observation, this study also reports a few of achivements and limitations in existing Vietnamese word segmentation systems.
```

Review: responsiveness ___; completeness ___; cited support ___; paper correctness ___; rationale ___

## Case 13: 5c6fa86757410aee6f5a0762328637de03a569e9

Question: In the paper 'Deep Learning for Detecting Cyberbullying Across Multiple Social Media Platforms', What were their performance results?

Answer: They achieved F1 scores of 0.94 for the Wikipedia and Twitter datasets using BLSTM with attention and feature level transfer learning. For the Formspring dataset, they achieved an F1 score of 0.95 with an accuracy score of 98%.

Automatic check: exact_quote_presence_only (not entailment).

Citation E3.S3 (E3): [paper 1801.06482](../data/raw/qasper-fresh-v1/1801.06482.pdf), PDF page 10.

Selected quote:

We achieve F1 scores of 0.94 for both these datasets using BLSTM with attention and feature level transfer learning (Table TABREF25 ).

Full supplied passage:

```text
Deep Learning for Detecting Cyberbullying Across Multiple Social Media Platforms
DNN based models coupled with transfer learning beat the best-known results for all three datasets. Previous best F1 scores for Wikipedia BIBREF4 and Twitter BIBREF8 datasets were 0.68 and 0.93 respectively. We achieve F1 scores of 0.94 for both these datasets using BLSTM with attention and feature level transfer learning (Table TABREF25 ). For Formspring dataset, authors have not reported F1 score. Their method has accuracy score of 78.5% BIBREF2 . We achieve F1 score of 0.95 with accuracy score of 98% for the same dataset.
```

Citation E3.S6 (E3): [paper 1801.06482](../data/raw/qasper-fresh-v1/1801.06482.pdf), PDF page 10.

Selected quote:

We achieve F1 score of 0.95 with accuracy score of 98% for the same dataset.

Full supplied passage:

```text
Deep Learning for Detecting Cyberbullying Across Multiple Social Media Platforms
DNN based models coupled with transfer learning beat the best-known results for all three datasets. Previous best F1 scores for Wikipedia BIBREF4 and Twitter BIBREF8 datasets were 0.68 and 0.93 respectively. We achieve F1 scores of 0.94 for both these datasets using BLSTM with attention and feature level transfer learning (Table TABREF25 ). For Formspring dataset, authors have not reported F1 score. Their method has accuracy score of 78.5% BIBREF2 . We achieve F1 score of 0.95 with accuracy score of 98% for the same dataset.
```

Review: responsiveness ___; completeness ___; cited support ___; paper correctness ___; rationale ___

## Case 14: 7e38e0279a620d3df05ab9b5e2795044f18d4471

Question: In the paper 'Deep Learning for Detecting Cyberbullying Across Multiple Social Media Platforms', What cyberbulling topics did they address?

Answer: personal attack, racism, and sexism

Automatic check: exact_quote_presence_only (not entailment).

Citation E1.S9 (E1): [paper 1801.06482](../data/raw/qasper-fresh-v1/1801.06482.pdf), PDF page 2.

Selected quote:

In contrast to existing bottlenecks, this work targets three different types of social networks (Formspring: a Q&A forum, Twitter: microblogging, and Wikipedia: collaborative knowledge repository) for three topics of cyberbullying (personal attack, racism, and sexism) without doing any explicit feature

Full supplied passage:

```text
Deep Learning for Detecting Cyberbullying Across Multiple Social Media Platforms
Past works on cyberbullying detection have at least one of the following three bottlenecks. First (Bottleneck B1), they target only one particular social media platform. How these methods perform across other SMPs is unknown. Second (Bottleneck B2), they address only one topic of cyberbullying such as racism, and sexism. Depending on the topic, vocabulary and nature of cyberbullying changes. These models are not flexible in accommodating changes in the definition of cyberbullying. Third (Bottleneck B3), they rely on carefully handcrafted features such as swear word list and POS tagging. However, these handcrafted features are not robust against variations in writing style. In contrast to existing bottlenecks, this work targets three different types of social networks (Formspring: a Q&A forum, Twitter: microblogging, and Wikipedia: collaborative knowledge repository) for three topics of cyberbullying (personal attack, racism, and sexism) without doing any explicit feature engineering by developing deep learning based models along with transfer learning.
```

Review: responsiveness ___; completeness ___; cited support ___; paper correctness ___; rationale ___

## Case 15: 551457ed34ca7fc0878c85bc664b135c21059b58

Question: In the paper 'Active Learning for Speech Recognition: the Power of Gradients', Which dataset do they use?

Answer: 190 hours (100K instances) of transcribed speech data

Automatic check: exact_quote_presence_only (not entailment).

Citation E3.S1 (E3): [paper 1612.03226](../data/raw/qasper-fresh-v1/1612.03226.pdf), PDF page 3.

Selected quote:

A base model, INLINEFORM0 , is trained on 190 hours ( INLINEFORM1 100K instances) of transcribed speech data.

Full supplied passage:

```text
Active Learning for Speech Recognition: the Power of Gradients
A base model, INLINEFORM0 , is trained on 190 hours ( INLINEFORM1 100K instances) of transcribed speech data. Then, it selects a subset of a 1,700-hour ( INLINEFORM2 1.1M instances) unlabeled dataset. We query labels for the selected subset and incorporate them into training. Learning rates are tuned on a small validation set of 2048 instances. The trained model is then tested on a 156-hour ( INLINEFORM3 100K instances) test set and we report CTC loss, Character Error Rate (CER) and Word Error Rate (WER).
```

Review: responsiveness ___; completeness ___; cited support ___; paper correctness ___; rationale ___

## Case 16: b7c3f3942a07c118e57130bc4c3ec4adc431d725

Question: In the paper 'Applying a Pre-trained Language Model to Spanish Twitter Humor Prediction', What did the best systems use for their model?

Answer: ASGD Weight-Dropped Long Short Term Memory (AWD_LSTM)

Automatic check: exact_quote_presence_only (not entailment).

Citation E3.S3 (E3): [paper 1907.03187](../data/raw/qasper-fresh-v1/1907.03187.pdf), PDF page 4.

Selected quote:

BIBREF5 ) model included in Fast.ai.

Full supplied passage:

```text
Applying a Pre-trained Language Model to Spanish Twitter Humor Prediction
We train the LM using a 90/10 training/validation split, reporting the validation loss and accuracy of next-word prediction on the validation set. For the LM, we selected an ASGD Weight-Dropped Long Short Term Memory (AWD_LSTM, described in Merity et al. BIBREF5 ) model included in Fast.ai. We replaced the typical Long Short Term Memory (LSTM) units with Quasi Recurrent Neural Network (QRNN, described in Bradbury et al. BIBREF6 ) units. Our network has 2304 hidden-states, 3 layers and a softmax layer to predict the next-word. We tied the embedding weights BIBREF7 on the encoder and decoder for training. We performed some simple tests with LSTM units and a Transformer Language model, finding all models were similar in performance during LM training. We thus chose to use QRNN units due to improved training speed compared to the alternatives. This model has about 60 million trainable parameters.
```

Review: responsiveness ___; completeness ___; cited support ___; paper correctness ___; rationale ___

## Case 17: a5505e25ee9ae84090e1442034ddbb3cedabcf04

Question: In the paper 'Applying a Pre-trained Language Model to Spanish Twitter Humor Prediction', What were their results on the classification and regression tasks

Answer: Our solution placed 3rd in Task 1 and 2nd in Task 2 in the final competition standings.

Automatic check: exact_quote_presence_only (not entailment).

Citation E1.S2 (E1): [paper 1907.03187](../data/raw/qasper-fresh-v1/1907.03187.pdf), PDF page 7.

Selected quote:

Our solution placed 3rd in Task 1 and 2nd in Task 2 in the final competition standings.

Full supplied passage:

```text
Applying a Pre-trained Language Model to Spanish Twitter Humor Prediction
This paper describes our implementation of a neural net model for classification and regression in the HAHA 2019 challenge. Our solution placed 3rd in Task 1 and 2nd in Task 2 in the final competition standings. We describe the data collection, pre-training, and final model building steps for this contest. Twitter has slang and abbreviations that are unique to the short-format as well as generous use of emoticons. To capture these features, we collected our own dataset based on Spanish Tweets that is 16 times larger than the competition data set and allowed us to pre-train a language model. Humor is subtle and using a label smoothed loss prevented us from becoming overconfident in our predictions and train more quickly without the gradual unfreezing required by ULMFiT. We have open-sourced all code used in this contest to further enable research on this task in the future.
```

Review: responsiveness ___; completeness ___; cited support ___; paper correctness ___; rationale ___

## Case 18: fe1dcd6ef1f8618bbceee418f07cafe63a8efe08

Question: In the paper 'VAIS ASR: Building a conversational speech recognition system using language model combination', What is the language model combination technique used in the paper?

Answer: language model combination technique

Automatic check: exact_quote_presence_only (not entailment).

Citation E1.S4 (E1): [paper 1910.05603](../data/raw/qasper-fresh-v1/1910.05603.pdf), PDF page 1.

Selected quote:

In this paper, we attempt to mitigate the problems using language models combination techniques that allows us to utilize both large amount of writing style text and small number of conversation text data.

Full supplied passage:

```text
VAIS ASR: Building a conversational speech recognition system using language model combination
Automatic Speech Recognition (ASR) systems have been evolving quickly and reaching human parity in certain cases. The systems usually perform pretty well on reading style and clean speech, however, most of the available systems suffer from situation where the speaking style is conversation and in noisy environments. It is not straight-forward to tackle such problems due to difficulties in data collection for both speech and text. In this paper, we attempt to mitigate the problems using language models combination techniques that allows us to utilize both large amount of writing style text and small number of conversation text data. Evaluation on the VLSP 2019 ASR challenges showed that our system achieved 4.85% WER on the VLSP 2018 and 15.09% WER on the VLSP 2019 data sets.
```

Citation E2.S1 (E2): [paper 1910.05603](../data/raw/qasper-fresh-v1/1910.05603.pdf), PDF page 2.

Selected quote:

In this paper, we presented our ASR system participated in VLSP 2019 challenge that incorporates a language model combination technique to handle conversation speech with small amount of text data required.

Full supplied passage:

```text
VAIS ASR: Building a conversational speech recognition system using language model combination
In this paper, we presented our ASR system participated in VLSP 2019 challenge that incorporates a language model combination technique to handle conversation speech with small amount of text data required. The method demonstrated that it can help to reduce WER by 3% on the VLSP 2019 challenge.
```

Citation E3.S1 (E3): [paper 1910.05603](../data/raw/qasper-fresh-v1/1910.05603.pdf), PDF page 1.

Selected quote:

In this paper, we present our attempt to mitigate the problems using a large scale data set and a language model combination technique that only require a small amount of conversation data but can still handle very well conversation speech.

Full supplied passage:

```text
VAIS ASR: Building a conversational speech recognition system using language model combination
In this paper, we present our attempt to mitigate the problems using a large scale data set and a language model combination technique that only require a small amount of conversation data but can still handle very well conversation speech.
```

Review: responsiveness ___; completeness ___; cited support ___; paper correctness ___; rationale ___

## Case 19: 44497509fdf5e87cff05cdcbe254fbd288d857ad

Question: In the paper 'Improving the Performance of Neural Machine Translation Involving Morphologically Rich Languages', By how much do they improve the efficacy of the attention mechanism?

Answer: 7.05 BLEU points

Automatic check: exact_quote_presence_only (not entailment).

Citation E1.S6 (E1): [paper 1612.02482](../data/raw/qasper-fresh-v1/1612.02482.pdf), PDF page 1.

Selected quote:

Also, this model (RNNMorph) improved the performance of neural machine translation by 7.05 BLEU points over the RNNSearch model used over the same corpus.

Full supplied passage:

```text
Improving the Performance of Neural Machine Translation Involving Morphologically Rich Languages
The advent of the attention mechanism in neural machine translation models has improved the performance of machine translation systems by enabling selective lookup into the source sentence. In this paper, the efficiencies of translation using bidirectional encoder attention decoder models were studied with respect to translation involving morphologically rich languages. The English - Tamil language pair was selected for this analysis. First, the use of Word2Vec embedding for both the English and Tamil words improved the translation results by 0.73 BLEU points over the baseline RNNSearch model with 4.84 BLEU score. The use of morphological segmentation before word vectorization to split the morphologically rich Tamil words into their respective morphemes before the translation, caused a reduction in the target vocabulary size by a factor of 8. Also, this model (RNNMorph) improved the performance of neural machine translation by 7.05 BLEU points over the RNNSearch model used over the same corpus. Since the BLEU evaluation of the RNNMorph model might be unreliable due to an increase in the number of matching tokens per sentence, the performances of the translations were also compared by means of human evaluation metrics of adequacy, fluency and relative ranking. Further, the use of morphological segmentation also improved the efficacy of the attention mechanism.
```

Review: responsiveness ___; completeness ___; cited support ___; paper correctness ___; rationale ___

## Case 20: 0ee73909ac638903da4a0e5565c8571fc794ab96

Question: In the paper 'Improving the Performance of Neural Machine Translation Involving Morphologically Rich Languages', How were the human judgements assembled?

Answer: A group of 50 native people who were well-versed in both English and Tamil languages acted as annotators for the evaluation.

Automatic check: exact_quote_presence_only (not entailment).

Citation E2.S2 (E2): [paper 1612.02482](../data/raw/qasper-fresh-v1/1612.02482.pdf), PDF page 11.

Selected quote:

A group of 50 native people who were well-versed in both English and Tamil languages acted as annotators for the evaluation.

Full supplied passage:

```text
Improving the Performance of Neural Machine Translation Involving Morphologically Rich Languages
To ensure that the increase in BLEU score correlated to actual increase in performance of translation, human evaluation metrics like adequacy, precision and ranking values (between RNNSearch and RNNMorph outputs) were estimated in Table TABREF30 . A group of 50 native people who were well-versed in both English and Tamil languages acted as annotators for the evaluation. A collection of samples of about 100 sentences were taken from the test set results for comparison. This set included a randomized selection of the translation results to ensure the objectivity of evaluation. Fluency and adequacy results for the RNNMorph results are tabulated. Adequacy rating was calculated on a 5-point scale of how much of the meaning is conveyed by the translation (All, Most, Much, Little, None). The fluency rating was calculated based on grammatical correctness on a 5-point scale of (Flawless, Good, Non-native, Disfluent, Incomprehensive). For the comparison process, the RNNMorph and the RNNSearch + Word2Vec models’ sentence level translations were individually ranked between each other, permitting the two translations to have ties in the ranking. The intra-annotator values were computed for these metrics and the scores are shown in Table TABREF32 BIBREF12 , BIBREF13 .
```

Review: responsiveness ___; completeness ___; cited support ___; paper correctness ___; rationale ___

## Case 21: e35a7f9513ff1cc0f0520f1d4ad9168a47dc18bb

Question: In the paper 'Combining Advanced Methods in Japanese-Vietnamese Neural Machine Translation', what was the baseline?

Answer: KyTea-segmented Japanese texts and pyvi-segmented Vietnamese texts

Automatic check: exact_quote_presence_only (not entailment).

Citation E3.S2 (E3): [paper 1805.07133](../data/raw/qasper-fresh-v1/1805.07133.pdf), PDF page 5.

Selected quote:

For the baseline systems, the training data includes KyTea-segmented Japanese texts and pyvi-segmented Vietnamese texts.

Full supplied passage:

```text
Combining Advanced Methods in Japanese-Vietnamese Neural Machine Translation
Baseline. For the baseline systems, the training data includes KyTea-segmented Japanese texts and pyvi-segmented Vietnamese texts. For comparison purpose, we build two baseline systems for each direction: one is use the traditional phrase-based statistical machine translation (SMT), the other one is the NMT system. Although our training set is small but we find that the NMT systems (2) are still more effective than the phrase-based SMT models (1) in both translation directions.
```

Review: responsiveness ___; completeness ___; cited support ___; paper correctness ___; rationale ___

## Case 22: 219af68afeaecabdfd279f439f10ba7c231736e4

Question: In the paper 'Combining Advanced Methods in Japanese-Vietnamese Neural Machine Translation', what japanese-vietnamese dataset do they use?

Answer: Japanese-Vietnamese parallel corpus in the DongDu corpus

Automatic check: exact_quote_presence_only (not entailment).

Citation E1.S4 (E1): [paper 1805.07133](../data/raw/qasper-fresh-v1/1805.07133.pdf), PDF page 5.

Selected quote:

For Mix-Source, instead of using a subsampled monolingual corpus, we use the Vietnamese part of the Japanese-Vietnamese parallel corpus in order to learn the multilingual information in the same domain.

Full supplied passage:

```text
Combining Advanced Methods in Japanese-Vietnamese Neural Machine Translation
The data augmentation methods has been applied only for the Japanese INLINEFORM0 Vietnamese direction. For Back Translation, we use Vietnamese monolingual data from VNESEcorpus of DongDu which includes 349578 sentences. We shuffle the lines of VNESEcorpus corpus and take out the first 106758 sentences (the same as the number of sentence pairs in the original parallel corpus). For Mix-Source, instead of using a subsampled monolingual corpus, we use the Vietnamese part of the Japanese-Vietnamese parallel corpus in order to learn the multilingual information in the same domain. Our datasets are listed in Table TABREF14 .
```

Review: responsiveness ___; completeness ___; cited support ___; paper correctness ___; rationale ___

## Case 23: 63a1cbe66fd58ff0ead895a8bac1198c38c008aa

Question: In the paper 'Going Beneath the Surface: Evaluating Image Captioning for Grammaticality, Truthfulness and Diversity', Which existing models are evaluated?

Answer: LRCN1u model

Automatic check: exact_quote_presence_only (not entailment).

Citation E2.S1 (E2): [paper 1912.08960](../data/raw/qasper-fresh-v1/1912.08960.pdf), PDF page 6.

Selected quote:

While performing the evaluation experiments on the LRCN1u model, we noticed that caption agreement does not always improve as the training loss decreases.

Full supplied passage:

```text
Going Beneath the Surface: Evaluating Image Captioning for Grammaticality, Truthfulness and Diversity
While performing the evaluation experiments on the LRCN1u model, we noticed that caption agreement does not always improve as the training loss decreases. Ideally, the training objective should be in accordance with how a model is eventually evaluated. In future work, we plan to investigate the feasibility of deliberately encoding the GTD signal in the training process, for instance, by implementing a GTD-aware loss. We also plan to extend the existing ShapeWorldICE benchmark to include more linguistic constructions (such as relative clauses, compound sentences and coreference). By doing so, we hope to reveal how well existing image captioning models cope with complex generation tasks.
```

Review: responsiveness ___; completeness ___; cited support ___; paper correctness ___; rationale ___

## Case 24: 3116453e35352a3a90ee5b12246dc7f2e60cfc59

Question: In the paper 'A Neural Topic-Attention Model for Medical Term Abbreviation Disambiguation', To what baseline models is proposed model compared?

Answer: traditional features, a Doc2vec model

Automatic check: exact_quote_presence_only (not entailment).

Citation E3.S1 (E3): [paper 1910.14076](../data/raw/qasper-fresh-v1/1910.14076.pdf), PDF page 3.

Selected quote:

We conducted a comprehensive comparison with the baseline models, and some of them were never investigated for the abbreviation disambiguation task.

Full supplied passage:

```text
A Neural Topic-Attention Model for Medical Term Abbreviation Disambiguation
We conducted a comprehensive comparison with the baseline models, and some of them were never investigated for the abbreviation disambiguation task. We applied traditional features by simply taking the TF-IDF features as the inputs into the classic classifiers. Deep features are also considered: a Doc2vec model BIBREF19 was pre-trained using Gensim and these word embeddings were applied to initialize deep models and fine-tuned.
```

Citation E3.S3 (E3): [paper 1910.14076](../data/raw/qasper-fresh-v1/1910.14076.pdf), PDF page 3.

Selected quote:

Deep features are also considered: a Doc2vec model BIBREF19 was pre-trained using Gensim and these word embeddings were applied to initialize deep models and fine-tuned.

Full supplied passage:

```text
A Neural Topic-Attention Model for Medical Term Abbreviation Disambiguation
We conducted a comprehensive comparison with the baseline models, and some of them were never investigated for the abbreviation disambiguation task. We applied traditional features by simply taking the TF-IDF features as the inputs into the classic classifiers. Deep features are also considered: a Doc2vec model BIBREF19 was pre-trained using Gensim and these word embeddings were applied to initialize deep models and fine-tuned.
```

Review: responsiveness ___; completeness ___; cited support ___; paper correctness ___; rationale ___

## Case 25: a9a532399237b514c1227f2d6be8601474e669be

Question: In the paper 'A Neural Topic-Attention Model for Medical Term Abbreviation Disambiguation', What existing dataset is re-examined and corrected for training?

Answer: an existing dataset

Automatic check: exact_quote_presence_only (not entailment).

Citation E1.S8 (E1): [paper 1910.14076](../data/raw/qasper-fresh-v1/1910.14076.pdf), PDF page 1.

Selected quote:

We re-examine and correct an existing dataset for training and collect a test set to evaluate the models fairly especially for rare senses.

Full supplied passage:

```text
A Neural Topic-Attention Model for Medical Term Abbreviation Disambiguation
Automated analysis of clinical notes is attracting increasing attention. However, there has not been much work on medical term abbreviation disambiguation. Such abbreviations are abundant, and highly ambiguous, in clinical documents. One of the main obstacles is the lack of large scale, balance labeled data sets. To address the issue, we propose a few-shot learning approach to take advantage of limited labeled data. Specifically, a neural topic-attention model is applied to learn improved contextualized sentence representations for medical term abbreviation disambiguation. Another vital issue is that the existing scarce annotations are noisy and missing. We re-examine and correct an existing dataset for training and collect a test set to evaluate the models fairly especially for rare senses. We train our model on the training set which contains 30 abbreviation terms as categories (on average, 479 samples and 3.24 classes in each term) selected from a public abbreviation disambiguation dataset, and then test on a manually-created balanced dataset (each class in each term has 15 samples). We show that enhancing the sentence representation with topic information improves the performance on small-scale unbalanced training datasets by a large margin, compared to a number of baseline models.
```

Review: responsiveness ___; completeness ___; cited support ___; paper correctness ___; rationale ___

## Case 26: ce2b921e4442a21555d65d8ce4ef7e3bde931dfc

Question: In the paper 'From English To Foreign Languages: Transferring Pre-trained Language Models', What languages are the model transferred to?

Answer: French (fr), Russian (ru), Arabic (ar), Chinese (zh), Hindi (hi), and Vietnamese (vi)

Automatic check: exact_quote_presence_only (not entailment).

Citation E2.S1 (E2): [paper 2002.07306](../data/raw/qasper-fresh-v1/2002.07306.pdf), PDF page 4.

Selected quote:

We evaluate our approach for six target languages: French (fr), Russian (ru), Arabic (ar), Chinese (zh), Hindi (hi), and Vietnamese (vi).

Full supplied passage:

```text
From English To Foreign Languages: Transferring Pre-trained Language Models
We evaluate our approach for six target languages: French (fr), Russian (ru), Arabic (ar), Chinese (zh), Hindi (hi), and Vietnamese (vi). These languages belong to four different language families. French, Russian, and Hindi are Indo-European languages, similar to English. Arabic, Chinese, and Vietnamese belong to Afro-Asiatic, Sino-Tibetan, and Austro-Asiatic family respectively. The choice of the six languages also reflects different training conditions depending on the amount of monolingual data. French and Russian, and Arabic can be regarded as high resource languages whereas Hindi has far less data and can be considered as low resource.
```

Review: responsiveness ___; completeness ___; cited support ___; paper correctness ___; rationale ___

## Case 27: 27de1d499348e17fec324d0ef00361a490659988

Question: In the paper 'An Evaluation Dataset for Intent Classification and Out-of-Scope Prediction', What is the size of this dataset?

Answer: 23,700

Automatic check: exact_quote_presence_only (not entailment).

Citation E1.S2 (E1): [paper 1909.02027](../data/raw/qasper-fresh-v1/1909.02027.pdf), PDF page 2.

Selected quote:

To do so, we constructed a new dataset with 23,700 queries that are short and unstructured, in the same style made by real users of task-oriented systems.

Full supplied passage:

```text
An Evaluation Dataset for Intent Classification and Out-of-Scope Prediction
This paper fills this gap by analyzing intent classification performance with a focus on out-of-scope handling. To do so, we constructed a new dataset with 23,700 queries that are short and unstructured, in the same style made by real users of task-oriented systems. The queries cover 150 intents, plus out-of-scope queries that do not fall within any of the 150 in-scope intents.
```

Citation E3.S1 (E3): [paper 1909.02027](../data/raw/qasper-fresh-v1/1909.02027.pdf), PDF page 2.

Selected quote:

We introduce a new crowdsourced dataset of 23,700 queries, including 22,500 in-scope queries covering 150 intents, which can be grouped into 10 general domains.

Full supplied passage:

```text
An Evaluation Dataset for Intent Classification and Out-of-Scope Prediction
We introduce a new crowdsourced dataset of 23,700 queries, including 22,500 in-scope queries covering 150 intents, which can be grouped into 10 general domains. The dataset also includes 1,200 out-of-scope queries. Table TABREF2 shows examples of the data.
```

Review: responsiveness ___; completeness ___; cited support ___; paper correctness ___; rationale ___

## Case 28: 975e60535724f4149c7488699a199ba2920a062c

Question: In the paper 'How we do things with words: Analyzing text as social and cultural data', What background do they have?

Answer: They have a background in analyzing text as social and cultural data, involving defining concepts, using domain experts, and employing computational methods like machine learning algorithms.

Automatic check: exact_quote_presence_only (not entailment).

Citation E1.S3 (E1): [paper 1907.01468](../data/raw/qasper-fresh-v1/1907.01468.pdf), PDF page 8.

Selected quote:

In the conceptualization phase we often start with questions such as: who are the domain experts, and how have they approached the topic?

Full supplied passage:

```text
How we do things with words: Analyzing text as social and cultural data
A core step in many analyses is translating social and cultural concepts (such as hate speech, rumor, or conversion) into measurable quantities. Before we can develop measurements for these concepts (the operationalization step, or the “implementation” step as denoted by BIBREF12 ), we need to define them. In the conceptualization phase we often start with questions such as: who are the domain experts, and how have they approached the topic? We are looking for a definition of the concept that is flexible enough to apply on our dataset, yet formal enough for computational research. For example, our introductory study on hate speech BIBREF0 used a statement on hate speech produced by the European Union Court of Human Rights. The goal was not to implement this definition directly in software but to use it as a reference point to anchor subsequent analyses.
```

Citation E1.S4 (E1): [paper 1907.01468](../data/raw/qasper-fresh-v1/1907.01468.pdf), PDF page 8.

Selected quote:

We are looking for a definition of the concept that is flexible enough to apply on our dataset, yet formal enough for computational research.

Full supplied passage:

```text
How we do things with words: Analyzing text as social and cultural data
A core step in many analyses is translating social and cultural concepts (such as hate speech, rumor, or conversion) into measurable quantities. Before we can develop measurements for these concepts (the operationalization step, or the “implementation” step as denoted by BIBREF12 ), we need to define them. In the conceptualization phase we often start with questions such as: who are the domain experts, and how have they approached the topic? We are looking for a definition of the concept that is flexible enough to apply on our dataset, yet formal enough for computational research. For example, our introductory study on hate speech BIBREF0 used a statement on hate speech produced by the European Union Court of Human Rights. The goal was not to implement this definition directly in software but to use it as a reference point to anchor subsequent analyses.
```

Citation E3.S2 (E3): [paper 1907.01468](../data/raw/qasper-fresh-v1/1907.01468.pdf), PDF page 2.

Selected quote:

New possibilities and frustrating obstacles emerge at every stage of research, from identification of the research question to interpretation of the results.

Full supplied passage:

```text
How we do things with words: Analyzing text as social and cultural data
These are just a small sample of the many opportunities and challenges faced in computational analyses of textual data. New possibilities and frustrating obstacles emerge at every stage of research, from identification of the research question to interpretation of the results. In this article, we take the reader through a typical research process that involves measuring social or cultural concepts using computational methods, discussing both the opportunities and complications that often arise. In the Reddit case, for example, hate speech is measured, however imperfectly, by the presence of particular words semi-automatically extracted from a machine learning algorithm. Operationalizations are never perfect translations, and are often refined over the course of an investigation, but they are crucial.
```

Review: responsiveness ___; completeness ___; cited support ___; paper correctness ___; rationale ___

## Case 29: f903396d943541a8cc65edefb04ca37814ed30dd

Question: In the paper 'How we do things with words: Analyzing text as social and cultural data', What dataset do they use for analysis?

Answer: European Union Court of Human Rights

Automatic check: exact_quote_presence_only (not entailment).

Citation E1.S5 (E1): [paper 1907.01468](../data/raw/qasper-fresh-v1/1907.01468.pdf), PDF page 8.

Selected quote:

For example, our introductory study on hate speech BIBREF0 used a statement on hate speech produced by the European Union Court of Human Rights.

Full supplied passage:

```text
How we do things with words: Analyzing text as social and cultural data
A core step in many analyses is translating social and cultural concepts (such as hate speech, rumor, or conversion) into measurable quantities. Before we can develop measurements for these concepts (the operationalization step, or the “implementation” step as denoted by BIBREF12 ), we need to define them. In the conceptualization phase we often start with questions such as: who are the domain experts, and how have they approached the topic? We are looking for a definition of the concept that is flexible enough to apply on our dataset, yet formal enough for computational research. For example, our introductory study on hate speech BIBREF0 used a statement on hate speech produced by the European Union Court of Human Rights. The goal was not to implement this definition directly in software but to use it as a reference point to anchor subsequent analyses.
```

Review: responsiveness ___; completeness ___; cited support ___; paper correctness ___; rationale ___

## Case 30: c9b8d3858c112859eabee54248b874331c48f71b

Question: In the paper 'Copenhagen at CoNLL--SIGMORPHON 2018: Multilingual Inflection in Context with Explicit Morphosyntactic Decoding', What type of inflections are considered?

Answer: lemmas and morphosyntactic descriptions (MSD), word forms

Automatic check: exact_quote_presence_only (not entailment).

Citation E1.S1 (E1): [paper 1809.01541](../data/raw/qasper-fresh-v1/1809.01541.pdf), PDF page 1.

Selected quote:

There are two tracks of Task 2 of CoNLL–SIGMORPHON 2018: in Track 1 the context is given in terms of word forms, lemmas and morphosyntactic descriptions (MSD); in Track 2 only word forms are available.

Full supplied passage:

```text
Copenhagen at CoNLL--SIGMORPHON 2018: Multilingual Inflection in Context with Explicit Morphosyntactic Decoding
There are two tracks of Task 2 of CoNLL–SIGMORPHON 2018: in Track 1 the context is given in terms of word forms, lemmas and morphosyntactic descriptions (MSD); in Track 2 only word forms are available. See Table TABREF1 for an example. Task 2 is additionally split in three settings based on data size: high, medium and low, with high-resource datasets consisting of up to 70K instances per language, and low-resource datasets consisting of only about 1K instances.
```

Review: responsiveness ___; completeness ___; cited support ___; paper correctness ___; rationale ___

## Case 31: 1eef2d2c296fdd10b08bf7b4ff7792cccf177d3b

Question: In the paper 'Automatic Classification of Pathology Reports using TF-IDF Features', What features are used?

Answer: TF-IDF features

Automatic check: exact_quote_presence_only (not entailment).

Citation E1.S3 (E1): [paper 1903.07406](../data/raw/qasper-fresh-v1/1903.07406.pdf), PDF page 3.

Selected quote:

For the first experiment series, training reports are pre-processed, then their TF-IDF features are extracted.

Full supplied passage:

```text
Automatic Classification of Pathology Reports using TF-IDF Features
In this study, we performed two different series of experiments: i) evaluating the performance of TF-IDF features and various machine learning classifiers on the task of predicting primary diagnosis from the text content of a given report, and ii) using TF-IDF and LDA techniques to highlight the important keywords within a report. For the first experiment series, training reports are pre-processed, then their TF-IDF features are extracted. The TF-IDF features and the training labels are used to train different classification models. These different classification models and their hyper-parameters are reported in tab:classifier. The performance of classifiers is measured quantitatively on the test dataset using the evaluation metrics discussed in the previous section. For the second experiment series, a random report is selected and its top 50 keywords are extracted using TF-IDF weights. These 50 keywords are highlighted using different colors based on their associated topic, which are extracted through LDA. A non-expert based qualitative inspection is performed on the extracted keywords and their corresponding topics.
```

Citation E1.S4 (E1): [paper 1903.07406](../data/raw/qasper-fresh-v1/1903.07406.pdf), PDF page 3.

Selected quote:

The TF-IDF features and the training labels are used to train different classification models.

Full supplied passage:

```text
Automatic Classification of Pathology Reports using TF-IDF Features
In this study, we performed two different series of experiments: i) evaluating the performance of TF-IDF features and various machine learning classifiers on the task of predicting primary diagnosis from the text content of a given report, and ii) using TF-IDF and LDA techniques to highlight the important keywords within a report. For the first experiment series, training reports are pre-processed, then their TF-IDF features are extracted. The TF-IDF features and the training labels are used to train different classification models. These different classification models and their hyper-parameters are reported in tab:classifier. The performance of classifiers is measured quantitatively on the test dataset using the evaluation metrics discussed in the previous section. For the second experiment series, a random report is selected and its top 50 keywords are extracted using TF-IDF weights. These 50 keywords are highlighted using different colors based on their associated topic, which are extracted through LDA. A non-expert based qualitative inspection is performed on the extracted keywords and their corresponding topics.
```

Review: responsiveness ___; completeness ___; cited support ___; paper correctness ___; rationale ___
