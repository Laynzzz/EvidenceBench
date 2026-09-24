# Complete-answer validation failures

These are the original raw outputs and strict validation errors. No response has been repaired or rescored. Malformed outputs are failures, not successful refusals.

## 955cbea7e5ead36fb89cd6229a97ccb3febcf8bc

Question: In the paper 'Humor Detection in English-Hindi Code-Mixed Social Media Content : Corpus and Baseline System', What experiments were carried out on the corpus?

Failure: invalid_answer_contract
Validation detail: quote must occur exactly in passage body and fit word limit

```text
{"answer":"The experiments involved analyzing the task of humor identification in social media texts as a classification problem and using several machine learning classification models such as support vector machines with radial basis function kernel and extra tree classifier. N-grams, bag-of-words, common words, and hashtags were used as features.","citations":[{"evidence_id":"E2","quote":"In this paper, we describe a freely available corpus of 3453 English-Hindi code-mixed tweets. The tweets are annotated with humorous(H) and non-humorous(N) tags along with the language tags at the word level. The task of humor identification in social media texts is analyzed as a classification problem and several machine learning classification models are used. The features used in our classification system are n-grams, bag-of-words, common words and hashtags. N-grams when trained with support vector machines with radial basis function kernel performed better than other features and yielded an accuracy of 68.5%. The best accuracy (69.3%) was given by support vector machines with radial basis function kernel."},{"evidence_id":"E3","quote":"10-fold cross validation on 3543 code-mixed tweets was carried out by dividing the corpus into 10 equal parts with nine parts as training corpus and rest one for testing. Mean accuracy is calculated by taking the average of the accuracy obtained in each iteration of the testing process. Table 2 shows the accuracy for each feature when trained using mentioned classifiers along with the accuracy when all the features are used along with the overall accuracy. Support vector machine with radial basis function kernel and extra tree classifier performs better than other classifiers and yields 69.3% and 67.8% accuracy respectively."}]}
```

## 3a6e843c6c81244c14730295cfb8b865cd7ede46

Question: In the paper 'A Deeper Look into Sarcastic Tweets Using Deep Convolutional Neural Networks', What are the state of the art models?

Failure: invalid_answer_contract
Validation detail: quote must occur exactly in passage body and fit word limit

```text
{"answer":"CNN-SVM on the baseline + sentiment + emotion + personality feature set","citations":[{"evidence_id":"E2","quote":"Among the pre-trained models, the sentiment model performs best (F1-score: 87.00%). As shown in Table TABREF30 , CNN-SVM on the baseline + sentiment + emotion + personality feature set outperforms the state of the art (F1-score: 94.80%)."}]}
```

## 58c6737070ef559e9220a8d08adc481fdcd53a24

Question: In the paper 'Performance Comparison of Crowdworkers and NLP Tools onNamed-Entity Recognition and Sentiment Analysis of Political Tweets', What measures are used for evaluation?

Failure: invalid_answer_contract
Validation detail: quote must occur exactly in passage body and fit word limit

```text
{"answer":"correct classification rate (CCR)","citations":[{"evidence_id":"E3","quote":"We report the experimental results for our two tasks in terms of the correct classification rate (CCR). For sentiment analysis, we have a three-class problem (positive, negative, and neutral), where the classes are mutually exclusive. The CCR, averaged for a set of tweets, is defined to be the number of correctly-predicted sentiments over the number of groundtruth sentiments in these tweets. For NER, we consider that each tweet may reference up to four candidates, i.e., targeted entities. The CCR, averaged for a set of tweets, is the number of correctly predicted entities (candidates) over the number of groundtruth entities (candidates) in this set."}]}
```

## 2ee715c7c6289669f11a79743a6b2b696073805d

Question: In the paper 'Automated News Suggestions for Populating Wikipedia Entity Pages', What baseline model is used?

Failure: invalid_answer_contract
Validation detail: quote must occur exactly in passage body and fit word limit

```text
{"answer":"salience-based features","citations":[{"evidence_id":"E1","quote":"The first baseline uses only the salience-based features by Dunietz and Gillick BIBREF11."}]}
```

## fe2666ace293b4bfac3182db6d0c6f03ea799277

Question: In the paper 'State-of-the-Art Vietnamese Word Segmentation', Why challenges does word segmentation in Vietnamese pose?

Failure: invalid_answer_contract
Validation detail: quote must occur exactly in passage body and fit word limit

```text
{"answer":"Acquiring a very large Vietnamese corpus, applying linguistics knowledge on word context to extract useful features, and handling various types of Vietnamese documents.","citations":[{"evidence_id":"E2","quote":"The first challenge is to acquire very large Vietnamese corpus and to use them in building a classifier, which could further improve accuracy. In addition, applying linguistics knowledge on word context to extract useful features also enhances prediction performance. The second challenge is design and development of big data warehouse and analytic framework for Vietnamese documents, which corresponds to the rapid and continuous growth of gigantic volume of articles and/or documents from Web 2.0 applications, such as, Facebook, Twitter, and so on. It should be addressed that there are many kinds of Vietnamese documents, for example, Han - Nom documents and old and modern Vietnamese documents that are essential and still needs further analysis."}]}
```

## 5c6fa86757410aee6f5a0762328637de03a569e9

Question: In the paper 'Deep Learning for Detecting Cyberbullying Across Multiple Social Media Platforms', What were their performance results?

Failure: invalid_answer_contract
Validation detail: quote must occur exactly in passage body and fit word limit

```text
{"answer":"F1 scores of 0.94 for Wikipedia and Twitter datasets, and an F1 score of 0.95 for the Formspring dataset","citations":[{"evidence_id":"E3","quote":"DNN based models coupled with transfer learning beat the best-known results for all three datasets. Previous best F1 scores for Wikipedia BIBREF4 and Twitter BIBREF8 datasets were 0.68 and 0.93 respectively. We achieve F1 scores of 0.94 for both these datasets using BLSTM with attention and feature level transfer learning (Table TABREF25 ). For Formspring dataset, authors have not reported F1 score. Their method has accuracy score of 78.5% BIBREF2 . We achieve F1 score of 0.95 with accuracy score of 98% for the same dataset."}]}
```

## 7e38e0279a620d3df05ab9b5e2795044f18d4471

Question: In the paper 'Deep Learning for Detecting Cyberbullying Across Multiple Social Media Platforms', What cyberbulling topics did they address?

Failure: invalid_answer_contract
Validation detail: invalid JSON

```text
{"answer":"perso","citations":[{"evidence_id":"E1","quote":"In contrast to existing bottlenecks, this work targets three different types of social networks (Formspring: a Q&A forum, Twitter: microblogging, and Wikipedia: collaborative knowledge repository) for three topics of cyberbullying (perso")}]}
```

## 551457ed34ca7fc0878c85bc664b135c21059b58

Question: In the paper 'Active Learning for Speech Recognition: the Power of Gradients', Which dataset do they use?

Failure: invalid_answer_contract
Validation detail: quote must occur exactly in passage body and fit word limit

```text
{"answer":"190 hours of transcribed speech data and a 156-hour test set","citations":[{"evidence_id":"E3","quote":"A base model, INLINEFORM0 , is trained on 190 hours (INLINEFORM1 100K instances) of transcribed speech data. Then, it selects a subset of a 1,700-hour (INLINEFORM2 1.1M instances) unlabeled dataset. We query labels for the selected subset and incorporate them into training. Learning rates are tuned on a small validation set of 2048 instances. The trained model is then tested on a 156-hour (INLINEFORM3 100K instances) test set and we report CTC loss, Character Error Rate (CER) and Word Error Rate (WER)."}]}
```

## fe1dcd6ef1f8618bbceee418f07cafe63a8efe08

Question: In the paper 'VAIS ASR: Building a conversational speech recognition system using language model combination', What is the language model combination technique used in the paper?

Failure: invalid_answer_contract
Validation detail: invalid JSON

```text
{"answer":"language model combination technique","citations":[{"evidence_id":"E1","quote":"In this paper, we attempt to mitigate the problems using language models combination techniques that allows us to utilize both large amount of writing style text and small number of conversation text data."},{"evidence_id":"E2","quote":"In this paper, we presented our ASR system participated in VLSP 2019 challenge that incorporates a language model combination technique to handle conversation speech with small amount of text data required."},{"evidence_id":"E3","quote":"In this paper, we present our attempt to mitigate the problems using a large scale data set and a language model combination technique that only require a small amount of conversation data but can still handle very well conversation speech."}]}```
```

## 0ee73909ac638903da4a0e5565c8571fc794ab96

Question: In the paper 'Improving the Performance of Neural Machine Translation Involving Morphologically Rich Languages', How were the human judgements assembled?

Failure: invalid_answer_contract
Validation detail: invalid JSON

```text
{"answer":"A group of 50 native people who were well-versed in both English and Tamil languages acted as annotators for the evaluation.","citations":[{"evidence_id":"E2","quote":"To ensure that the increase in BLEU score correlated to actual increase in performance of translation, human evaluation metrics like adequacy, precision and ranking values (between RNNSearch and RNNMorph outputs) were estimated in Table TABREF30 . A group of 50 native people who were well-versed in both English and Tamil languages acted as annotators for the evaluation."}]}```
```
