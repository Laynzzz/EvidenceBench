# Saved-answer review packet

Purpose: independent human review of the 28 saved proposed answers. This packet hides checker verdicts, benchmark references and agent judgments. It contains no completed human labels. A reviewer who has seen the other reports should disclose that exposure.

Assess separately: (1) whether the answer responds to the question, (2) whether cited text supports it, (3) whether important requested information is missing, and (4) whether the full paper changes the conclusion. Record supported / unsupported / unclear and a short rationale; use unclear rather than guessing. The JSON response template is gpu-answer-human-review-template.json. Do not treat paper truth alone as citation support.

## Case 1: dea9e7fe8e47da5e7f31d9b1a46ebe34e731a596

Question: In the paper 'Humor Detection in English-Hindi Code-Mixed Social Media Content : Corpus and Baseline System', What type of system does the baseline classification use?

Proposed answer: Support vector machine with radial basis function kernel and extra tree classifier

[Local source paper](../data/raw/qasper-fresh-v1/1806.05513.pdf)

Cited passage E3:

```text
Humor Detection in English-Hindi Code-Mixed Social Media Content : Corpus and Baseline System
10-fold cross validation on 3543 code-mixed tweets was carried out by dividing the corpus into 10 equal parts with nine parts as training corpus and rest one for testing. Mean accuracy is calculated by taking the average of the accuracy obtained in each iteration of the testing process. Table 2 shows the accuracy for each feature when trained using mentioned classifiers along with the accuracy when all the features are used along with the overall accuracy. Support vector machine with radial basis function kernel and extra tree classifier performs better than other classifiers and yields 69.3% and 67.8% accuracy respectively. The reason kernel SVM yields the best result is because the number of observations is greator than the number of features BIBREF20 . N-grams proved to be the most efficient in all classification models followed by common words and hastags. Bag-of-words feature performed th
```

Review: responsiveness ___; cited support ___; completeness ___; rationale ___

## Case 2: 955cbea7e5ead36fb89cd6229a97ccb3febcf8bc

Question: In the paper 'Humor Detection in English-Hindi Code-Mixed Social Media Content : Corpus and Baseline System', What experiments were carried out on the corpus?

Proposed answer: The tremendous amount of user generated data through social networking sites led to the gaining

[Local source paper](../data/raw/qasper-fresh-v1/1806.05513.pdf)

Cited passage E1:

```text
Humor Detection in English-Hindi Code-Mixed Social Media Content : Corpus and Baseline System
The tremendous amount of user generated data through social networking sites led to the gaining popularity of automatic text classification in the field of computational linguistics over the past decade. Within this domain, one problem that has drawn the attention of many researchers is automatic humor detection in texts. In depth semantic understanding of the text is required to detect humor which makes the problem difficult to automate. With increase in the number of social media users, many multilingual speakers often interchange between languages while posting on social media which is called code-mixing. It introduces some challenges in the field of linguistic analysis of social media content (Barman et al., 2014), like spelling variations and non-grammatical structures in a sentence. Past researches include detecting puns in texts (Kao et al., 2016) and humor in one-lines (Mihalcea et al.
```

Review: responsiveness ___; cited support ___; completeness ___; rationale ___

## Case 3: 1beb4a590fa6127a138f4ed1dd13d5d51cc96809

Question: In the paper 'A Deeper Look into Sarcastic Tweets Using Deep Convolutional Neural Networks', What are the network's baseline features?

Proposed answer: The F1-score using sentiment features when combined with baseline features is 94.60%. On both of

[Local source paper](../data/raw/qasper-fresh-v1/1610.08815.pdf)

Cited passage E3:

```text
A Deeper Look into Sarcastic Tweets Using Deep Convolutional Neural Networks
Table TABREF29 shows the performance of different feature combinations. The gap between the F1-scores of only baseline features and all features is larger on the imbalanced dataset than the balanced dataset. This supports our claim that sentiment, emotion and personality features are very useful for sarcasm detection, thanks to the pre-trained models. The F1-score using sentiment features when combined with baseline features is 94.60%. On both of the datasets, emotion and sentiment features perform better than the personality features. Interestingly, using only sentiment, emotion and personality features, we achieve 90.90% F1-score.
```

Review: responsiveness ___; cited support ___; completeness ___; rationale ___

## Case 4: 3a6e843c6c81244c14730295cfb8b865cd7ede46

Question: In the paper 'A Deeper Look into Sarcastic Tweets Using Deep Convolutional Neural Networks', What are the state of the art models?

Proposed answer: The F1-score drops down dramatically to 33.05%

[Local source paper](../data/raw/qasper-fresh-v1/1610.08815.pdf)

Cited passage E3:

```text
A Deeper Look into Sarcastic Tweets Using Deep Convolutional Neural Networks
To test the generalization capability of the proposed approach, we perform training on Dataset 1 and test on Dataset 3. The F1-score drops down dramatically to 33.05%. In order to understand this finding, we visualize each dataset using PCA (Figure FIGREF17 ). It depicts that, although Dataset 1 is mostly linearly separable, Dataset 3 is not. A linear kernel that performs well on Dataset 1 fails to provide good performance on Dataset 3. If we use RBF kernel, it overfits the data and produces worse results than what we get using linear kernel. Similar trends are seen in the performance of other two state-of-the-art approaches BIBREF9 , BIBREF8 . Thus, we decide to perform training on Dataset 3 and test on the Dataset 1. As expected better performance is obtained with F1-score 76.78%. However, the other two state-of-the-art approaches fail to perform well in this setting. While the method by BIBREF9 obtains F1-s
```

Review: responsiveness ___; cited support ___; completeness ___; rationale ___

## Case 5: 58c6737070ef559e9220a8d08adc481fdcd53a24

Question: In the paper 'Performance Comparison of Crowdworkers and NLP Tools onNamed-Entity Recognition and Sentiment Analysis of Political Tweets', What measures are used for evaluation?

Proposed answer: The CCR, averaged for a set of tweets, is defined to be the number of

[Local source paper](../data/raw/qasper-fresh-v1/2002.04181.pdf)

Cited passage E3:

```text
Performance Comparison of Crowdworkers and NLP Tools onNamed-Entity Recognition and Sentiment Analysis of Political Tweets
We report the experimental results for our two tasks in terms of the correct classification rate (CCR). For sentiment analysis, we have a three-class problem (positive, negative, and neutral), where the classes are mutually exclusive. The CCR, averaged for a set of tweets, is defined to be the number of correctly-predicted sentiments over the number of groundtruth sentiments in these tweets. For NER, we consider that each tweet may reference up to four candidates, i.e., targeted entities. The CCR, averaged for a set of tweets, is the number of correctly predicted entities (candidates) over the number of groundtruth entities (candidates) in this set.
```

Review: responsiveness ___; cited support ___; completeness ___; rationale ___

## Case 6: 9b7655d39c7a19a23eb8944568eb5618042b9026

Question: In the paper 'Performance Comparison of Crowdworkers and NLP Tools onNamed-Entity Recognition and Sentiment Analysis of Political Tweets', Which toolkits do they use?

Proposed answer: The crowdworkers were located in the US and hired on the

[Local source paper](../data/raw/qasper-fresh-v1/2002.04181.pdf)

Cited passage E1:

```text
Performance Comparison of Crowdworkers and NLP Tools onNamed-Entity Recognition and Sentiment Analysis of Political Tweets
We used the 1,000-tweet dataset by BIBREF2 that contains the named-entities labels and entity-level sentiments for each of the four 2016 presidential primary candidates Bernie Sanders, Donald Trump, Hillary Clinton, and Ted Cruz, provided by crowdworkers, and by experts in political communication, whose labels are considered groundtruth. The crowdworkers were located in the US and hired on the BIBREF22 platform. For the task of entity-level sentiment analysis, a 3-scale rating of "negative," "neutral," and "positive" was used by the annotators.
```

Review: responsiveness ___; cited support ___; completeness ___; rationale ___

## Case 7: 55569d0a4586d20c01268a80a7e31a17a18198e2

Question: In the paper 'Zero-shot Reading Comprehension by Cross-lingual Transfer Learning with Multi-lingual Language Representation Model', what does the model learn in zero-shot setting?

Proposed answer: Multi-BERT has showcased its ability to enable cross-lingual zero-shot learning on the natural language understanding

[Local source paper](../data/raw/qasper-fresh-v1/1909.09587.pdf)

Cited passage E2:

```text
Zero-shot Reading Comprehension by Cross-lingual Transfer Learning with Multi-lingual Language Representation Model
Multi-BERT has showcased its ability to enable cross-lingual zero-shot learning on the natural language understanding tasks including XNLI BIBREF19, NER, POS, Dependency Parsing, and so on. We now seek to know if a pre-trained multi-BERT has ability to solve RC tasks in the zero-shot setting.
```

Review: responsiveness ___; cited support ___; completeness ___; rationale ___

## Case 8: b1ce129678e37070e69f01332f1a8587e18e06b0

Question: In the paper 'Sentiment Analysis of Twitter Data for Predicting Stock Market Movements', What dataset is used to train the model?

Proposed answer: The stock price data of Microsoft are labeled suitably for training using a simple program

[Local source paper](../data/raw/qasper-fresh-v1/1610.09225.pdf)

Cited passage E1:

```text
Sentiment Analysis of Twitter Data for Predicting Stock Market Movements
The stock price data of Microsoft are labeled suitably for training using a simple program. If the previous day stock price is more than the current day stock price, the current day is marked with a numeric value of 0, else marked with a numeric value of 1. Now, this correlation analysis turns out to be a classification problem. The total positive, negative and neutral emotions in tweets in a 3 day period are calculated successively which are used as features for the classifier model and the output is the labeled next day value of stock 0 or 1.The window size is experimented and best results are achieved when the sentiment values precede 3 days to the stock price. A total of 355 instances, each with 3 attributes are fed to the classifier with a split proportions of 80% train dataset and the remaining dataset for testing. The accuracy of the classifier is discussed in the results section.
```

Review: responsiveness ___; cited support ___; completeness ___; rationale ___

## Case 9: 2ee715c7c6289669f11a79743a6b2b696073805d

Question: In the paper 'Automated News Suggestions for Populating Wikipedia Entity Pages', What baseline model is used?

Proposed answer: B1

[Local source paper](../data/raw/qasper-fresh-v1/1703.10344.pdf)

Cited passage E1:

```text
Automated News Suggestions for Populating Wikipedia Entity Pages
B1. The first baseline uses only the salience-based features by Dunietz and Gillick BIBREF11 .
```

Review: responsiveness ___; cited support ___; completeness ___; rationale ___

## Case 10: 984fc3e726848f8f13dfe72b89e3770d00c3a1af

Question: In the paper 'Automated News Suggestions for Populating Wikipedia Entity Pages', What features are used to represent the novelty of news articles to entity pages?

Proposed answer: The novelty value of

[Local source paper](../data/raw/qasper-fresh-v1/1703.10344.pdf)

Cited passage E2:

```text
Automated News Suggestions for Populating Wikipedia Entity Pages
Given an entity INLINEFORM0 and the already added news references INLINEFORM1 up to year INLINEFORM2 , the novelty of INLINEFORM3 at year INLINEFORM4 is measured by the KL divergence between the language model of INLINEFORM5 and articles in INLINEFORM6 . We combine this measure with the entity overlap of INLINEFORM7 and INLINEFORM8 . The novelty value of INLINEFORM9 is given by the minimal divergence value. Low scores indicate low novelty for the entity profile INLINEFORM10 .
```

Review: responsiveness ___; cited support ___; completeness ___; rationale ___

## Case 11: fe2666ace293b4bfac3182db6d0c6f03ea799277

Question: In the paper 'State-of-the-Art Vietnamese Word Segmentation', Why challenges does word segmentation in Vietnamese pose?

Proposed answer: The first challenge is to acquire very large Vietnamese corpus and to use them in

[Local source paper](../data/raw/qasper-fresh-v1/1906.07662.pdf)

Cited passage E2:

```text
State-of-the-Art Vietnamese Word Segmentation
There are several challenges on supervised learning approaches in future work. The first challenge is to acquire very large Vietnamese corpus and to use them in building a classifier, which could further improve accuracy. In addition, applying linguistics knowledge on word context to extract useful features also enhances prediction performance. The second challenge is design and development of big data warehouse and analytic framework for Vietnamese documents, which corresponds to the rapid and continuous growth of gigantic volume of articles and/or documents from Web 2.0 applications, such as, Facebook, Twitter, and so on. It should be addressed that there are many kinds of Vietnamese documents, for example, Han - Nom documents and old and modern Vietnamese documents that are essential and still needs further analysis. According to our study, there is no a powerful Vietnamese language processing used for processing Vietnamese big data as w
```

Review: responsiveness ___; cited support ___; completeness ___; rationale ___

## Case 12: 7e38e0279a620d3df05ab9b5e2795044f18d4471

Question: In the paper 'Deep Learning for Detecting Cyberbullying Across Multiple Social Media Platforms', What cyberbulling topics did they address?

Proposed answer: Formspring: a Q&A forum, Twitter: microblogging, and Wikipedia: collaborative knowledge repository

[Local source paper](../data/raw/qasper-fresh-v1/1801.06482.pdf)

Cited passage E1:

```text
Deep Learning for Detecting Cyberbullying Across Multiple Social Media Platforms
Past works on cyberbullying detection have at least one of the following three bottlenecks. First (Bottleneck B1), they target only one particular social media platform. How these methods perform across other SMPs is unknown. Second (Bottleneck B2), they address only one topic of cyberbullying such as racism, and sexism. Depending on the topic, vocabulary and nature of cyberbullying changes. These models are not flexible in accommodating changes in the definition of cyberbullying. Third (Bottleneck B3), they rely on carefully handcrafted features such as swear word list and POS tagging. However, these handcrafted features are not robust against variations in writing style. In contrast to existing bottlenecks, this work targets three different types of social networks (Formspring: a Q&A forum, Twitter: microblogging, and Wikipedia: collaborative knowledge repository) for three topics of cyberbullying (perso
```

Review: responsiveness ___; cited support ___; completeness ___; rationale ___

## Case 13: 551457ed34ca7fc0878c85bc664b135c21059b58

Question: In the paper 'Active Learning for Speech Recognition: the Power of Gradients', Which dataset do they use?

Proposed answer: EGL by marginalizing over the most likely 100 labels

[Local source paper](../data/raw/qasper-fresh-v1/1612.03226.pdf)

Cited passage E1:

```text
Active Learning for Speech Recognition: the Power of Gradients
We implement EGL by marginalizing over the most likely 100 labels, and compare it with: 1) a random selection baseline, 2) entropy, and 3) pCTC. Using the same base model, each method queries a variable percentage of the unlabeled dataset. The queries are then included into training set, and the model continues training until convergence. Fig. FIGREF9 reports the metrics (Exact values are reported in Table TABREF12 in the Appendix) on the test set as the query percentage varies. All the active learning methods outperform the random baseline. Moreover, EGL shows a steeper, more rapid reduction in error than all other approaches. Specifically, when querying 20% of the unlabeled dataset, EGL has 11.58% lower CER and 11.09% lower WER relative to random. The performance of EGL at querying 20% is on par with random at 40%, suggesting that using EGL can lead to an approximate 50% decrease in data labeling.
```

Review: responsiveness ___; cited support ___; completeness ___; rationale ___

## Case 14: b7c3f3942a07c118e57130bc4c3ec4adc431d725

Question: In the paper 'Applying a Pre-trained Language Model to Spanish Twitter Humor Prediction', What did the best systems use for their model?

Proposed answer: The first is the baseline NBSVM solution, with an F1 of 0.7548. Second is our

[Local source paper](../data/raw/qasper-fresh-v1/1907.03187.pdf)

Cited passage E2:

```text
Applying a Pre-trained Language Model to Spanish Twitter Humor Prediction
Table TABREF29 gives three results from our submissions in the competition. The first is the baseline NBSVM solution, with an F1 of 0.7548. Second is our first random seed selected for the classifier which produces a 0.8083 result. While better than the NBSVM solution, we pick the best validation F1 from the 20 seeds we tried. This produced our final submission of 0.8099. Our best model achieved an five-fold average F1 of 0.8254 on the validation set shown in Figure FIGREF27 but a test set F1 of 0.8099 - a drop of 0.0155 in F1 for the true out-of-sample data. Also note that our third place entry was 1.1% worse in F1 score than first place but 1.2% better in F1 than the 4th place entry.
```

Review: responsiveness ___; cited support ___; completeness ___; rationale ___

## Case 15: fe1dcd6ef1f8618bbceee418f07cafe63a8efe08

Question: In the paper 'VAIS ASR: Building a conversational speech recognition system using language model combination', What is the language model combination technique used in the paper?

Proposed answer: language model combination technique

[Local source paper](../data/raw/qasper-fresh-v1/1910.05603.pdf)

Cited passage E2:

```text
VAIS ASR: Building a conversational speech recognition system using language model combination
In this paper, we presented our ASR system participated in VLSP 2019 challenge that incorporates a language model combination technique to handle conversation speech with small amount of text data required. The method demonstrated that it can help to reduce WER by 3% on the VLSP 2019 challenge.
```

Review: responsiveness ___; cited support ___; completeness ___; rationale ___

## Case 16: 44497509fdf5e87cff05cdcbe254fbd288d857ad

Question: In the paper 'Improving the Performance of Neural Machine Translation Involving Morphologically Rich Languages', By how much do they improve the efficacy of the attention mechanism?

Proposed answer: 0.73 BLEU points

[Local source paper](../data/raw/qasper-fresh-v1/1612.02482.pdf)

Cited passage E1:

```text
Improving the Performance of Neural Machine Translation Involving Morphologically Rich Languages
The advent of the attention mechanism in neural machine translation models has improved the performance of machine translation systems by enabling selective lookup into the source sentence. In this paper, the efficiencies of translation using bidirectional encoder attention decoder models were studied with respect to translation involving morphologically rich languages. The English - Tamil language pair was selected for this analysis. First, the use of Word2Vec embedding for both the English and Tamil words improved the translation results by 0.73 BLEU points over the baseline RNNSearch model with 4.84 BLEU score. The use of morphological segmentation before word vectorization to split the morphologically rich Tamil words into their respective morphemes before the translation, caused a reduction in the target vocabulary size by a factor of 8. Also, this model (RNNMorph) improved the perform
```

Review: responsiveness ___; cited support ___; completeness ___; rationale ___

## Case 17: 0ee73909ac638903da4a0e5565c8571fc794ab96

Question: In the paper 'Improving the Performance of Neural Machine Translation Involving Morphologically Rich Languages', How were the human judgements assembled?

Proposed answer: None

[Local source paper](../data/raw/qasper-fresh-v1/1612.02482.pdf)

Cited passage E2:

```text
Improving the Performance of Neural Machine Translation Involving Morphologically Rich Languages
To ensure that the increase in BLEU score correlated to actual increase in performance of translation, human evaluation metrics like adequacy, precision and ranking values (between RNNSearch and RNNMorph outputs) were estimated in Table TABREF30 . A group of 50 native people who were well-versed in both English and Tamil languages acted as annotators for the evaluation. A collection of samples of about 100 sentences were taken from the test set results for comparison. This set included a randomized selection of the translation results to ensure the objectivity of evaluation. Fluency and adequacy results for the RNNMorph results are tabulated. Adequacy rating was calculated on a 5-point scale of how much of the meaning is conveyed by the translation (All, Most, Much, Little, None). The fluency rating was calculated based on grammatical correctness on a 5-point scale of (Flawless, Good, Non-n
```

Review: responsiveness ___; cited support ___; completeness ___; rationale ___

## Case 18: e35a7f9513ff1cc0f0520f1d4ad9168a47dc18bb

Question: In the paper 'Combining Advanced Methods in Japanese-Vietnamese Neural Machine Translation', what was the baseline?

Proposed answer: BPE

[Local source paper](../data/raw/qasper-fresh-v1/1805.07133.pdf)

Cited passage E1:

```text
Combining Advanced Methods in Japanese-Vietnamese Neural Machine Translation
Subword NMT. We applied VNBPE and JPBPE to the baseline's data and trained NMT systems. On Vietnamese INLINEFORM0 Japanese, we observed an improvement of 0.6 BLEU points when we used our VNBPE (3) instead of the pyvi's word segmentation (2). Furthermore, when we trained our NMT models using both BPE methods (4), we obtained a bigger gain of 1.15 BLEU points. The similar improvements can be found in the Japanese INLINEFORM1 Vietnamese as well: 0.29 BLEU points between (3) and (2) and 0.57 BLEU points between (4) and (3). This draws two conclusions: (i), despite using an unsupervised Vietnamese word segmentation which is fast, robust and does not require linguistic resources, our NMT systems performed better than those systems employing a complicate word segmentation method, (ii) BPE works significantly well for Japanese texts after we tokenized the texts.
```

Review: responsiveness ___; cited support ___; completeness ___; rationale ___

## Case 19: 219af68afeaecabdfd279f439f10ba7c231736e4

Question: In the paper 'Combining Advanced Methods in Japanese-Vietnamese Neural Machine Translation', what japanese-vietnamese dataset do they use?

Proposed answer: Japanese-Vietnamese parallel corpus

[Local source paper](../data/raw/qasper-fresh-v1/1805.07133.pdf)

Cited passage E1:

```text
Combining Advanced Methods in Japanese-Vietnamese Neural Machine Translation
The data augmentation methods has been applied only for the Japanese INLINEFORM0 Vietnamese direction. For Back Translation, we use Vietnamese monolingual data from VNESEcorpus of DongDu which includes 349578 sentences. We shuffle the lines of VNESEcorpus corpus and take out the first 106758 sentences (the same as the number of sentence pairs in the original parallel corpus). For Mix-Source, instead of using a subsampled monolingual corpus, we use the Vietnamese part of the Japanese-Vietnamese parallel corpus in order to learn the multilingual information in the same domain. Our datasets are listed in Table TABREF14 .
```

Review: responsiveness ___; cited support ___; completeness ___; rationale ___

## Case 20: 63a1cbe66fd58ff0ead895a8bac1198c38c008aa

Question: In the paper 'Going Beneath the Surface: Evaluating Image Captioning for Grammaticality, Truthfulness and Diversity', Which existing models are evaluated?

Proposed answer: In the remainder of the paper we discuss in detail the diagnostic results of the

[Local source paper](../data/raw/qasper-fresh-v1/1912.08960.pdf)

Cited passage E3:

```text
Going Beneath the Surface: Evaluating Image Captioning for Grammaticality, Truthfulness and Diversity
In the remainder of the paper we discuss in detail the diagnostic results of the LRCN1u model demonstrated by the GTD evaluation framework.
```

Review: responsiveness ___; cited support ___; completeness ___; rationale ___

## Case 21: 3116453e35352a3a90ee5b12246dc7f2e60cfc59

Question: In the paper 'A Neural Topic-Attention Model for Medical Term Abbreviation Disambiguation', To what baseline models is proposed model compared?

Proposed answer: To address the issue, we propose a few-shot learning approach to take advantage of limited

[Local source paper](../data/raw/qasper-fresh-v1/1910.14076.pdf)

Cited passage E1:

```text
A Neural Topic-Attention Model for Medical Term Abbreviation Disambiguation
Automated analysis of clinical notes is attracting increasing attention. However, there has not been much work on medical term abbreviation disambiguation. Such abbreviations are abundant, and highly ambiguous, in clinical documents. One of the main obstacles is the lack of large scale, balance labeled data sets. To address the issue, we propose a few-shot learning approach to take advantage of limited labeled data. Specifically, a neural topic-attention model is applied to learn improved contextualized sentence representations for medical term abbreviation disambiguation. Another vital issue is that the existing scarce annotations are noisy and missing. We re-examine and correct an existing dataset for training and collect a test set to evaluate the models fairly especially for rare senses. We train our model on the training set which contains 30 abbreviation terms as categories (on average, 479 samples and 3.
```

Review: responsiveness ___; cited support ___; completeness ___; rationale ___

## Case 22: a9a532399237b514c1227f2d6be8601474e669be

Question: In the paper 'A Neural Topic-Attention Model for Medical Term Abbreviation Disambiguation', What existing dataset is re-examined and corrected for training?

Proposed answer: The implementation is available online; 3) as limited research are conducted on this particular task

[Local source paper](../data/raw/qasper-fresh-v1/1910.14076.pdf)

Cited passage E3:

```text
A Neural Topic-Attention Model for Medical Term Abbreviation Disambiguation
Our contributions can be summarized as: 1) we re-examined and corrected an existing dataset for training and we collected a test set for evaluation with focus especially for rare senses; 2) we proposed a few-shot learning approach which combines topic information and contextualized word embeddings to solve clinical abbreviation disambiguation task. The implementation is available online; 3) as limited research are conducted on this particular task, we evaluated and compared a number of baseline methods including classical models and deep models comprehensively.
```

Review: responsiveness ___; cited support ___; completeness ___; rationale ___

## Case 23: ce2b921e4442a21555d65d8ce4ef7e3bde931dfc

Question: In the paper 'From English To Foreign Languages: Transferring Pre-trained Language Models', What languages are the model transferred to?

Proposed answer: Zero-shot cross-lingual transfer has shown promising results for rapidly building applications for low resource languages

[Local source paper](../data/raw/qasper-fresh-v1/2002.07306.pdf)

Cited passage E1:

```text
From English To Foreign Languages: Transferring Pre-trained Language Models
Pre-trained models BIBREF0, BIBREF1 have received much of attention recently thanks to their impressive results in many down stream NLP tasks. Additionally, multilingual pre-trained models enable many NLP applications for other languages via zero-short cross-lingual transfer. Zero-shot cross-lingual transfer has shown promising results for rapidly building applications for low resource languages. BIBREF2 show the potential of multilingual-BERT BIBREF0 in zero-shot transfer for a large number of languages from different language families on five NLP tasks, namely, natural language inference, document classification, named entity recognition, part-of-speech tagging, and dependency parsing.
```

Review: responsiveness ___; cited support ___; completeness ___; rationale ___

## Case 24: 27de1d499348e17fec324d0ef00361a490659988

Question: In the paper 'An Evaluation Dataset for Intent Classification and Out-of-Scope Prediction', What is the size of this dataset?

Proposed answer: The dataset also includes 1,200 out-of-scope queries. Table

[Local source paper](../data/raw/qasper-fresh-v1/1909.02027.pdf)

Cited passage E3:

```text
An Evaluation Dataset for Intent Classification and Out-of-Scope Prediction
We introduce a new crowdsourced dataset of 23,700 queries, including 22,500 in-scope queries covering 150 intents, which can be grouped into 10 general domains. The dataset also includes 1,200 out-of-scope queries. Table TABREF2 shows examples of the data.
```

Review: responsiveness ___; cited support ___; completeness ___; rationale ___

## Case 25: 975e60535724f4149c7488699a199ba2920a062c

Question: In the paper 'How we do things with words: Analyzing text as social and cultural data', What background do they have?

Proposed answer: The goal was not to implement this definition directly in software but to use it

[Local source paper](../data/raw/qasper-fresh-v1/1907.01468.pdf)

Cited passage E1:

```text
How we do things with words: Analyzing text as social and cultural data
A core step in many analyses is translating social and cultural concepts (such as hate speech, rumor, or conversion) into measurable quantities. Before we can develop measurements for these concepts (the operationalization step, or the “implementation” step as denoted by BIBREF12 ), we need to define them. In the conceptualization phase we often start with questions such as: who are the domain experts, and how have they approached the topic? We are looking for a definition of the concept that is flexible enough to apply on our dataset, yet formal enough for computational research. For example, our introductory study on hate speech BIBREF0 used a statement on hate speech produced by the European Union Court of Human Rights. The goal was not to implement this definition directly in software but to use it as a reference point to anchor subsequent analyses.
```

Review: responsiveness ___; cited support ___; completeness ___; rationale ___

## Case 26: f903396d943541a8cc65edefb04ca37814ed30dd

Question: In the paper 'How we do things with words: Analyzing text as social and cultural data', What dataset do they use for analysis?

Proposed answer: Bigger datasets often make statistics more robust. The size needed for a computational text analysis

[Local source paper](../data/raw/qasper-fresh-v1/1907.01468.pdf)

Cited passage E3:

```text
How we do things with words: Analyzing text as social and cultural data
The size of many newly available datasets is one of their most appealing characteristics. Bigger datasets often make statistics more robust. The size needed for a computational text analysis depends on the research goal: When it involves studying rare events, bigger datasets are needed. However, larger is not always better. Some very large archives are “secretly” collections of multiple and distinct processes that no in-field scholar would consider related. For example, Google Books is frequently used to study cultural patterns, but the over-representation of scientific articles in Google books can be problematic BIBREF11 . Even very large born-digital datasets usually cover limited timespans compared to, e.g., the Gutenberg archive of British novels.
```

Review: responsiveness ___; cited support ___; completeness ___; rationale ___

## Case 27: c9b8d3858c112859eabee54248b874331c48f71b

Question: In the paper 'Copenhagen at CoNLL--SIGMORPHON 2018: Multilingual Inflection in Context with Explicit Morphosyntactic Decoding', What type of inflections are considered?

Proposed answer: Table

[Local source paper](../data/raw/qasper-fresh-v1/1809.01541.pdf)

Cited passage E1:

```text
Copenhagen at CoNLL--SIGMORPHON 2018: Multilingual Inflection in Context with Explicit Morphosyntactic Decoding
There are two tracks of Task 2 of CoNLL–SIGMORPHON 2018: in Track 1 the context is given in terms of word forms, lemmas and morphosyntactic descriptions (MSD); in Track 2 only word forms are available. See Table TABREF1 for an example. Task 2 is additionally split in three settings based on data size: high, medium and low, with high-resource datasets consisting of up to 70K instances per language, and low-resource datasets consisting of only about 1K instances.
```

Review: responsiveness ___; cited support ___; completeness ___; rationale ___

## Case 28: 1eef2d2c296fdd10b08bf7b4ff7792cccf177d3b

Question: In the paper 'Automatic Classification of Pathology Reports using TF-IDF Features', What features are used?

Proposed answer: TF-IDF features and various machine learning classifiers

[Local source paper](../data/raw/qasper-fresh-v1/1903.07406.pdf)

Cited passage E1:

```text
Automatic Classification of Pathology Reports using TF-IDF Features
In this study, we performed two different series of experiments: i) evaluating the performance of TF-IDF features and various machine learning classifiers on the task of predicting primary diagnosis from the text content of a given report, and ii) using TF-IDF and LDA techniques to highlight the important keywords within a report. For the first experiment series, training reports are pre-processed, then their TF-IDF features are extracted. The TF-IDF features and the training labels are used to train different classification models. These different classification models and their hyper-parameters are reported in tab:classifier. The performance of classifiers is measured quantitatively on the test dataset using the evaluation metrics discussed in the previous section. For the second experiment series, a random report is selected and its top 50 keywords are extracted using TF-IDF weights. These 50 keywords are highlighte
```

Review: responsiveness ___; cited support ___; completeness ___; rationale ___
