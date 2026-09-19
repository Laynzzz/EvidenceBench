# Post-test failure inspection

This inspection occurred after the frozen final run. It did not change data, models, prompts, thresholds or scoring. Observations below are agent analysis of existing human references and saved outputs, not a human generated-claim audit.

## All nine emitted answers

### e9a0a69eacd554141f56b60ab2d1912cc33f526a

In the paper 'Sentiment Analysis of Code-Mixed Indian Languages: An Overview of SAIL_Code-Mixed Shared Task @ICON-2017', what was the baseline?

Returned: `0.331`

Human reference: Random labeling | Alternative human answer:  randomly assigning any of the sentiment values to each of the test instances

Quotes a score instead of identifying the random-labeling baseline.

### 36cb7ebdd39e0b8a89ff946d3a3aef8a76a6bb43

In the paper 'Gender Prediction from Tweets: Improving Neural Representations with Hand-Crafted Features', Are LSA-reduced n-gram features considered hand-crafted features?

Returned: `Yes`

Human reference: Yes | Alternative human answer: No

Human references disagree Yes/No. The predeclared maximum-over-references F1 accepts either; this is annotation ambiguity, not evidence of reliable reasoning.

### 452e2d7d7d9e1bb4914903479cd7caff9f6fae42

In the paper 'Deep Learning for Hate Speech Detection in Tweets', Are pretrained embeddings used?

Returned: `Yes`

Human reference: GloVe | Alternative human answer: Yes

Answer text matches a human alternative; only some cited passages match human evidence. No new human support audit was conducted.

### 2301424672cb79297cf7ad95f23b58515e4acce8

In the paper 'Relative contributions of Shakespeare and Fletcher in Henry VIII: An Analysis Based on Most Frequent Words and Most Frequent Rhythmic Patterns', Is Henry VIII reflective of Shakespeare in general?

Returned: `Yes`

Human reference: No | Alternative human answer: Yes

Human references disagree Yes/No. The predeclared maximum-over-references F1 accepts either; this is annotation ambiguity, not evidence of reliable reasoning.

### 0aca0a208a1e28857fab44e397dc7880e010dbca

In the paper 'Integrating Crowdsourcing and Active Learning for Classification of Work-Life Events from Tweets', Which was the most helpful strategy?

Returned: `active learning`

Human reference: Vote entropy and KL divergence;  all the active learning strategies we tested do not work well with deep learning model | Alternative human answer: Entropy algorithm is the best way to build machine learning models. Vote entropy and KL divergence are helpful for the training of machine learning ensemble classifiers. | Alternative human answer: entropy

Returns the broad approach instead of the requested strategy; reference overlap can award partial credit to an incomplete answer.

### b70e4c49300dc3eab18e907ab903afd2a0c6075a

In the paper 'Evaluating the Cross-Lingual Effectiveness of Massively Multilingual Neural Machine Translation', What are the five downstream tasks?

Returned: `5`

Human reference: These include 3 classification tasks: NLI (XNLI dataset), document classification (MLDoc dataset) and intent classification, and 2 sequence tagging tasks: POS tagging and NER. | Alternative human answer: NLI (XNLI dataset); document classification (MLDoc dataset); intent classification; POS tagging; NER | Alternative human answer: NLI (XNLI dataset); document classification (MLDoc dataset);  intent classification; sequence tagging tasks: POS tagging; NER | Alternative human answer: NLI; document classification; intent classification; POS tagging; NER

The answer gives the count instead of naming five tasks, despite citing an annotated evidence paragraph. Provenance does not establish answer correctness.

### 3dad6b792044018bb968ac0d0fd4628653f9e4b7

In the paper 'Character n-gram Embeddings to Improve RNN Language Models', Which word embeddings do they compare against?

Returned: `char INLINEFORM3 -MS-vec`

Human reference: Unanswerable in the named paper

Missing refusal: the paper is marked unanswerable by the retained human annotations.

### b424ad7f9214076b963a0077d7345d7bb5a7a205

In the paper 'UIT-ViIC: A Dataset for the First Evaluation on Vietnamese Image Captioning', Do they use crowdsourcing for the captions?

Returned: `Yes`

Human reference: Yes

Answer text matches a reference but its citation does not match retained human evidence. This is reference disagreement, not a conclusive semantic judgment.

### de346decb1fbca8746b72c78ea9d1208902f5e0a

In the paper 'A Lost Croatian Cybernetic Machine Translation Program', What language was this research published in?

Returned: `Croatian`

Human reference: Unanswerable in the named paper

Missing refusal: the paper is marked unanswerable by the retained human annotations.

## Reranking regressions

The selected model improved 40, regressed 14 and tied 21 answerable questions by nDCG@10. Aggregate gains do not eliminate per-query regressions. The table records all 14; their causal explanation is not inferred from scores alone.

| Query | Untuned nDCG | Selected nDCG |
|---|---:|---:|
| `e9a0a69eacd554141f56b60ab2d1912cc33f526a` | 0.3869 | 0.3010 |
| `a18d74109ed55ed14c33913efa62e12f207279c0` | 0.3333 | 0.3010 |
| `0b10cfa61595b21bf3ff13b4df0fe1c17bbbf4e9` | 0.2044 | 0.0000 |
| `95af7aaea3ce9dab4cf64e2229ce9b98381dd050` | 0.3026 | 0.0875 |
| `71413505d7d6579e2a453a1f09f4efd20197ab4b` | 0.1815 | 0.0000 |
| `f5513f9314b9d7b41518f98c6bc6d42b8555258d` | 0.1815 | 0.0000 |
| `c845110efee2f633d47f5682573bc6091e8f5023` | 0.3010 | 0.0000 |
| `4d5b74499804ea5bc5520beb88d0f9816f67205a` | 0.7366 | 0.1952 |
| `200c37060d037dee33f3b7c8b1a2aaa58376566e` | 0.4307 | 0.3010 |
| `8e26c471ca0ee1b9779da04c0b81918fd310d0f3` | 0.5714 | 0.2641 |
| `2f75b0498cf6a1fc35f1fb1cac44fc2fbd3d7878` | 0.1672 | 0.1564 |
| `f9ae1b31c1a60aacb9ef869e1cc6b0e70c6e5d8e` | 0.2837 | 0.1413 |
| `845bdcd900c0f96b2ae091d086fb1ab8bb1063f0` | 0.8711 | 0.6183 |
| `740cc392c0c8bfadfe6b3a60c0be635c03e17f2a` | 0.6309 | 0.3869 |

Forty-five outputs failed the generation contract and 46 were refused. Failure strings and packed evidence are preserved in the raw answer run; none were silently dropped. A future model/context change would require a new development/holdout protocol rather than tuning against these cases.
