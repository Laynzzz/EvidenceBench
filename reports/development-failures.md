# Development failure inspection

Generated inspection with agent review of the question, human reference, raw output and ranking. This is not a new human label set or a human semantic-support audit. Every development query with imperfect baseline/candidate nDCG or an answer/refusal error is retained.

Reviewed/retained 36 unique failure queries. All 50 development outputs were inspected.

## 1. 0a75a52450ed866df3a304077769e1725a995bb7

In the paper 'Attention-based Wav2Text with Feature Transfer Learning', How does their decoder generate text?

Human reference: decoder task, which predicts the target sequence probability at time INLINEFORM3 based on previous output and context information | Alternative human answer: Decoder predicts the sequence of phoneme or grapheme at each time based on the previous output and context information with a beam search strategy

Status: failure; answer: ''; reason: invalid_generation

Diagnosis: generation contract failure; see raw output; no judged support in top-3 context candidates; reranking regression.

Raw generation: `{"answer":"Feature transfer learning is used to assist in training the encoder-decoder model.", "evidence_ids":["[E1]","[E2]","[E3]"]}`

Source citations: []

## 2. b06512c17d99f9339ffdab12cedbc63501ff527e

In the paper 'DOLORES: Deep Contextualized Knowledge Graph Embeddings', Is fine-tuning required to incorporate these embeddings into existing models?

Human reference: No

Status: refused; answer: ''; reason: insufficient_evidence

Diagnosis: false refusal.

Raw generation: ``

Source citations: []

## 3. 99e78c390932594bd833be0f5c890af5c605d808

In the paper 'Medication Regimen Extraction From Clinical Conversations', What is the baseline?

Human reference: QA PGNet; Multi-decoder QA PGNet with lookup table embedding | Alternative human answer: QA PGNet and Multi-decoder QA PGNet

Status: answered; answer: 'baseline'; reason: None

Diagnosis: no judged support in top-3 context candidates; reranking regression; compare answer and reference; valid IDs/quotes do not establish correctness.

Raw generation: `{"answer":"baseline","evidence_ids":["E1"]}`

Source citations: [{'bbox': None, 'document_id': 'qasper-1912.04961', 'element_id': '2aac445dc30d901fbd9ed242e05d9cd6f71112d1504d97ce3936de741732218a', 'page': 1, 'page_end': 2, 'reranker_score': 4.368937015533447, 'section': 'Abstract', 'source_url': 'https://arxiv.org/pdf/1912.04961'}]

## 4. f161e6d5aecf8fae3a26374dcb3e4e1b40530c95

In the paper 'Medication Regimen Extraction From Clinical Conversations', What embeddings are used?

Human reference: simple lookup table embeddings learned from scratch; using high-performance contextual embeddings, which are ELMo BIBREF11, BERT BIBREF16 and ClinicalBERT BIBREF13 | Alternative human answer: ELMO BIBREF11, BERT BIBREF12 and ClinicalBERT BIBREF13

Status: failure; answer: ''; reason: invalid_generation

Diagnosis: generation contract failure; see raw output; no judged support in top-3 context candidates; reranking regression.

Raw generation: `{"answer":"ELMo,EBERT,BERT"}`

Source citations: []

## 5. 3d7d865e905295d11f1e85af5fa89b210e3e9fdf

In the paper 'Learning Autocomplete Systems as a Communication Game', How many participants were trying this communication game?

Human reference: 100  | Alternative human answer: 100 crowdworkers

Status: refused; answer: ''; reason: insufficient_evidence

Diagnosis: false refusal.

Raw generation: ``

Source citations: []

## 6. 4c18081ae3b676cc7831403d11bc070c10120f8e

In the paper 'Mining Supervisor Evaluation and Peer Feedback in Performance Appraisals', What clustering algorithms were used?

Human reference: CLUTO; Carrot2 Lingo | Alternative human answer: simple clustering algorithm which uses the cosine similarity between word embeddings

Status: failure; answer: ''; reason: invalid_generation

Diagnosis: generation contract failure; see raw output.

Raw generation: `{"answer":"SVM with ADWS kernel","evidence_ids":["E1"]}`

Source citations: []

## 7. 61652a3da85196564401d616d251084a25ab4596

In the paper 'Mining Supervisor Evaluation and Peer Feedback in Performance Appraisals', What is the size of the real-life dataset?

Human reference: 26972 | Alternative human answer: 26972 sentences

Status: failure; answer: ''; reason: invalid_generation

Diagnosis: generation contract failure; see raw output; no judged support in top-3 context candidates; reranking regression.

Raw generation: `{"answer":"2000", "evidence_ids":["E1","E2","E3"]}`

Source citations: []

## 8. fa30a938b58fc05131c3854f12efe376cbad887f

In the paper 'Distant supervision for emotion detection using Facebook reactions', What was their performance on emotion detection?

Human reference: Answer with content missing: (Table 3) Best author's model B-M average micro f-score is 0.409, 0.459, 0.411 on Affective, Fairy Tales and ISEAR datasets respectively.

Status: failure; answer: ''; reason: invalid_generation

Diagnosis: generation contract failure; see raw output; no judged support in top-3 context candidates; reranking regression; upstream missing-table annotation ambiguity.

Raw generation: `{"answer":"No", "evidence_ids":["E1"]}`

Source citations: []

## 9. de53af4eddbc30c808d90b8a11a29217d377569e

In the paper 'Distant supervision for emotion detection using Facebook reactions', Which Facebook pages did they look at?

Human reference: FoxNews, CNN, ESPN, New York Times, Time magazine, Huffington Post Weird News, The Guardian, Cartoon Network, Cooking Light, Home Cooking Adventure, Justin Bieber, Nickelodeon, Spongebob, Disney | Alternative human answer: FoxNews, CNN, ESPN, New York Times, Time magazine, Huffington Post Weird News, The Guardian, Cartoon Network, Cooking Light, Home Cooking Adventure, Justin Bieber, Nickelodeon, Spongebob, Disney.

Status: failure; answer: ''; reason: generation_timeout

Diagnosis: generation contract failure; see raw output.

Raw generation: `{"answer":"FoxNews, CNN, ESPN, New York Times, Time magazine, Huffington Post Weird News, The Guardian, Cartoon Network, Cooking Light, H", "evidence_ids":["E1","E2","E3"]}`

Source citations: []

## 10. f875337f2ecd686cd7789e111174d0f14972638d

In the paper 'Distant supervision for emotion detection using Facebook reactions', Which existing benchmarks did they compare to?

Human reference: Affective Text; Fairy Tales; ISEAR | Alternative human answer:  Affective Text dataset; Fairy Tales dataset; ISEAR dataset

Status: failure; answer: ''; reason: invalid_generation

Diagnosis: generation contract failure; see raw output.

Raw generation: `{"answer":"[E1]", "evidence_ids":["E1"]}`

Source citations: []

## 11. d41e20ec716b5904a272938e5a8f5f3f15a7779e

In the paper 'A Framework for the Computational Linguistic Analysis of Dehumanization', How do they identify discussions of LGBTQ people in the New York Times?

Human reference: act paragraphs containing any word from a predetermined list of LGTBQ terms

Status: failure; answer: ''; reason: invalid_generation

Diagnosis: generation contract failure; see raw output; no judged support in top-3 context candidates.

Raw generation: `{"answer":"No", "evidence_ids":["E1"]}`

Source citations: []

## 12. cb384dc5366b693f28680374d31ff45356af0461

In the paper 'A Framework for the Computational Linguistic Analysis of Dehumanization', Do they model semantics

Human reference: Yes

Status: answered; answer: 'Yes'; reason: None

Diagnosis: compare answer and reference; valid IDs/quotes do not establish correctness.

Raw generation: `{"answer":"Yes", "evidence_ids":["E1", "E3"]}`

Source citations: [{'bbox': None, 'document_id': 'qasper-2003.03014', 'element_id': '86e29f05e01d8bb1c4e4daa6ca0f0e6dc769c09afe1a4f6b1cdaff284c1be2c8', 'page': 2, 'page_end': 2, 'reranker_score': 3.645655632019043, 'section': 'Introduction', 'source_url': 'https://arxiv.org/pdf/2003.03014'}, {'bbox': None, 'document_id': 'qasper-2003.03014', 'element_id': '0275b035ad24351a790405ec87dfad24004ab4a078b385abb763795914f5a0fb', 'page': 5, 'page_end': 5, 'reranker_score': 2.9957802295684814, 'section': 'Operationalizing Dehumanization ::: Negative Evaluation of a Target Group ::: Word Embedding Neighbor Valence', 'source_url': 'https://arxiv.org/pdf/2003.03014'}]

## 13. 7b4fb6da74e6bd1baea556788a02969134cf0800

In the paper 'Symmetric Regularization based BERT for Pair-wise Semantic Reasoning', Do they train their model starting from a checkpoint?

Human reference: No

Status: answered; answer: 'No'; reason: None

Diagnosis: compare answer and reference; valid IDs/quotes do not establish correctness.

Raw generation: `{"answer":"No", "evidence_ids":["E1"]}`

Source citations: [{'bbox': None, 'document_id': 'qasper-1909.03405', 'element_id': 'fec2be12a1a845955829300e62f2ca23080c8fc6b2f59bdffe3c8c7ac2339afe', 'page': 3, 'page_end': 4, 'reranker_score': 3.5203351974487305, 'section': 'Experiment Settings', 'source_url': 'https://arxiv.org/pdf/1909.03405'}]

## 14. bc31a3d2f7c608df8c019a64d64cb0ccc5669210

In the paper 'Symmetric Regularization based BERT for Pair-wise Semantic Reasoning', What BERT model do they test?

Human reference: BERTbase

Status: failure; answer: ''; reason: invalid_generation

Diagnosis: generation contract failure; see raw output; no judged support in top-3 context candidates; reranking regression.

Raw generation: `{"answer":"BERT-PN", "evidence_ids":"[E2,E3]"}`

Source citations: []

## 15. d98847340e46ffe381992f1a594e75d3fb8d385e

In the paper 'A Question-Entailment Approach to Question Answering', What machine learning and deep learning methods are used for RQE?

Human reference: Logistic Regression; neural networks

Status: failure; answer: ''; reason: invalid_generation

Diagnosis: generation contract failure; see raw output; no judged support in top-3 context candidates.

Raw generation: `{"answer":"No", "evidence_ids":["E1"]}`

Source citations: []

## 16. 932b39fd6c47c6a880621a62e6a978491d881d60

In the paper 'Knowledge Graph Representation with Jointly Structural and Textual Encoding', What baselines are used for comparison?

Human reference: TransE

Status: refused; answer: ''; reason: insufficient_evidence

Diagnosis: false refusal.

Raw generation: ``

Source citations: []

## 17. b36f867fcda5ad62c46d23513369337352aa01d2

In the paper 'Knowledge Graph Representation with Jointly Structural and Textual Encoding', What datasets are used to evaluate this paper?

Human reference: WordNet BIBREF0; Freebase BIBREF1; WN18 (a subset of WordNet) BIBREF24 ; FB15K (a subset of Freebase) BIBREF2

Status: refused; answer: ''; reason: insufficient_evidence

Diagnosis: false refusal.

Raw generation: ``

Source citations: []

## 18. ed67359889cf61fa11ee291d6c378cccf83d599d

In the paper 'Shallow reading with Deep Learning: Predicting popularity of online content using only its title', Which pretrained word vectors did they use?

Human reference: pre-trained GloVe word vectors  | Alternative human answer: GloVe word vectors BIBREF16 pre-trained on two datasets: Wikipedia 2014 with Gigaword5 (W+G5) and Common Crawl (CC)

Status: failure; answer: ''; reason: invalid_generation

Diagnosis: generation contract failure; see raw output.

Raw generation: `{"answer":"BIBREF16", "evidence_ids":["E1"]}`

Source citations: []

## 19. 955de9f7412ba98a0c91998919fa048d339b1d48

In the paper 'Shallow reading with Deep Learning: Predicting popularity of online content using only its title', Which shallow approaches did they experiment with?

Human reference: SVM | Alternative human answer: SVM with linear kernel using bag-of-words features

Status: failure; answer: ''; reason: invalid_generation

Diagnosis: generation contract failure; see raw output; no judged support in top-3 context candidates.

Raw generation: `{"answer":"[E1]", "evidence_ids":["E1"]}`

Source citations: []

## 20. 252a645af9876241fb166e5822992ce17fec6eb6

In the paper 'Shallow reading with Deep Learning: Predicting popularity of online content using only its title', What is the average length of the title text?

Human reference: Unanswerable in the named paper

Status: answered; answer: '4090'; reason: None

Diagnosis: missing refusal; compare answer and reference; valid IDs/quotes do not establish correctness.

Raw generation: `{"answer":"4090", "evidence_ids":["E1"]}`

Source citations: [{'bbox': None, 'document_id': 'qasper-1707.06806', 'element_id': 'ca6acd617d0ebd9a0b27e3a4f8b9d344919400b71a46655107f4f9f60e773f08', 'page': 6, 'page_end': 6, 'reranker_score': 4.8052568435668945, 'section': 'Datasets', 'source_url': 'https://arxiv.org/pdf/1707.06806'}]

## 21. 3b371ea554fa6639c76a364060258454e4b931d4

In the paper 'Shallow reading with Deep Learning: Predicting popularity of online content using only its title', Where do they obtain the news videos from?

Human reference: NowThisNews Facebook page

Status: failure; answer: ''; reason: invalid_generation

Diagnosis: generation contract failure; see raw output; reranking regression.

Raw generation: `{"answer":"news videos from NowThisNews Facebook page collected between 07/2015 and 07/2016", "evidence_ids":[4]}`

Source citations: []

## 22. ddb23a71113cbc092cbc158066d891cae261e2c6

In the paper 'Shallow reading with Deep Learning: Predicting popularity of online content using only its title', What is the source of the news articles?

Human reference: main news channels, such as Yahoo News, The Guardian or The Washington Post | Alternative human answer: The BreakingNews dataset

Status: failure; answer: ''; reason: invalid_generation

Diagnosis: generation contract failure; see raw output; reranking regression.

Raw generation: `{"answer":"The sources are Yahoo News, The Guardian, and The Washington Post.", "evidence_ids":[4]}`

Source citations: []

## 23. 425bd2ccfd95ead91d8f2b1b1c8ab9fc3446cb82

In the paper 'Shallow reading with Deep Learning: Predicting popularity of online content using only its title', What evaluation metrics are used?

Human reference: standard accuracy metric | Alternative human answer: accuracy

Status: failure; answer: ''; reason: invalid_generation

Diagnosis: generation contract failure; see raw output; reranking regression.

Raw generation: `{"answer":"None", "evidence_ids":[],""}`

Source citations: []

## 24. 4bc2784be43d599000cb71d31928908250d4cef3

In the paper 'Identification of Indian Languages using Ghost-VLAD pooling', What is the GhostVLAD approach?

Human reference: extension of the NetVLAD; adds Ghost clusters along with the NetVLAD clusters | Alternative human answer: An extension of NetVLAD which replaces hard assignment-based clustering with soft assignment-based clustering with the additon o fusing Ghost clusters to deal with noisy content.

Status: failure; answer: ''; reason: invalid_generation

Diagnosis: generation contract failure; see raw output.

Raw generation: `{"answer":"GhostVLAD is an extension of the NetVLAD approach used for face recognition.", "evidence_ids":["E1","E2","E3"]}`

Source citations: []

## 25. b65a83a24fc66728451bb063cf6ec50134c8bfb0

In the paper 'Text Summarization using Abstract Meaning Representation', How are sentences selected from the summary graph?

Human reference: finding the important sentences from the story; extracting the key information from those sentences using their AMR graphs | Alternative human answer:  Two methods: first is to simply pick initial few sentences,  second is to capture the relation between the two most important entities  (select the first sentence which contains both these entities).

Status: failure; answer: ''; reason: invalid_generation

Diagnosis: generation contract failure; see raw output; no judged support in top-3 context candidates; reranking regression.

Raw generation: `{"answer":"No", "evidence_ids":["E1"]}`

Source citations: []

## 26. 9b4dc790e4ff49562992aae4fad3a38621fadd8b

In the paper 'Embedding Geographic Locations for Modelling the Natural Environment using Flickr Tags and Structured Data', what are the existing approaches?

Human reference: BOW-Tags; BOW-KL(Tags); BOW-All; GloVe

Status: failure; answer: ''; reason: invalid_generation

Diagnosis: generation contract failure; see raw output; no judged support in top-3 context candidates.

Raw generation: `{"answer":"Existing approaches include the use of Flickr for modeling urban environments, meta-data from photo-sharing websites like Flickr, and the integration of structured information from traditional scientific resources.", "evidence_ids":["E1","E3"]}`

Source citations: []

## 27. 71bd5db79635d48a0730163a9f2e8ef19a86cd66

In the paper 'A Framework for Evaluation of Machine Reading Comprehension Gold Standards', What features are absent from MRC gold standards that can result in potential lexical ambiguity?

Human reference: Restrictivity ; Factivity ; Coreference  | Alternative human answer: semantics-altering grammatical modifiers

Status: failure; answer: ''; reason: invalid_generation

Diagnosis: generation contract failure; see raw output.

Raw generation: `{"answer":"Lexical cues","evidence_ids":["E1"]}`

Source citations: []

## 28. 0ec56e15005a627d0b478a67fd627a9d85c3920e

In the paper 'Text Classification based on Word Subspace with Term-Frequency', What can word subspace represent?

Human reference: Word vectors, usually in the context of others within the same class

Status: failure; answer: ''; reason: generation_timeout

Diagnosis: generation contract failure; see raw output; no judged support in top-3 context candidates.

Raw generation: `{"answer":"word subspace represents the`

Source citations: []

## 29. d28d86524292506d4b24ae2d486725a6d57a3db3

In the paper 'Pretraining-Based Natural Language Generation for Text Summarization', What is the ROUGE score of the highest performing model?

Human reference: 33.33 average of ROUGE-1, ROUGE-2 and ROUGE-L  | Alternative human answer: 33.33

Status: refused; answer: ''; reason: insufficient_evidence

Diagnosis: false refusal.

Raw generation: ``

Source citations: []

## 30. c1c44fd96c3fa6e16949ae8fa453e511c6435c68

In the paper 'Pretraining-Based Natural Language Generation for Text Summarization', Why masking words in the decoder is helpful?

Human reference: ecause this process is similar to the cloze task in BERT's pre-train process, therefore by using the ability of the contextual language model the decoder can generate more fluent and natural sequences.

Status: refused; answer: ''; reason: insufficient_evidence

Diagnosis: false refusal; no judged support in top-3 context candidates; reranking regression.

Raw generation: ``

Source citations: []

## 31. 0a5ffe4697913a57fda1fd5a188cd5ed59bdc5c7

In the paper 'External Lexical Information for Multilingual Part-of-Speech Tagging', which languages are explored?

Human reference: Bulgarian, Croatian, Czech, Danish, English, French, German, Indonesian, Italian, Norwegian, Persian, Polish, Portuguese, Slovenian, Spanish and Swedish | Alternative human answer: Bulgarian; Croatian; Czech; Danish; English; French; German; Indonesian; Italian; Norwegian; Persian; Polish; Portuguese; Slovenian; Spanish ; Swedish

Status: failure; answer: ''; reason: invalid_generation

Diagnosis: generation contract failure; see raw output; no judged support in top-3 context candidates.

Raw generation: `{"answer":"French","evidence_ids":["BIBREF12", "BIBREF40", "BIBREF41"]}`

Source citations: []

## 32. 3ddff6b707767c3dd54d7104fe88b628765cae58

In the paper 'External Lexical Information for Multilingual Part-of-Speech Tagging', which datasets did they experiment with?

Human reference: Universal Dependencies v1.2 treebanks for the following 16 languages: Bulgarian, Croatian, Czech, Danish, English, French, German,
Indonesian, Italian, Norwegian, Persian, Polish, Portuguese, Slovenian, Spanish, and Swedish | Alternative human answer: Universal Dependencies v1.2 treebanks BIBREF21 , hereafter UD1.2

Status: refused; answer: ''; reason: insufficient_evidence

Diagnosis: false refusal; no judged support in top-3 context candidates.

Raw generation: ``

Source citations: []

## 33. 45a5961a4e1d1c22874c4918e5c98bd3c0a670b3

In the paper 'Analysis of Wikipedia-based Corpora for Question Answering', How many question types do they find in the datasets analyzed?

Human reference: seven  | Alternative human answer: 7

Status: refused; answer: ''; reason: insufficient_evidence

Diagnosis: false refusal; no judged support in top-3 context candidates; reranking regression.

Raw generation: ``

Source citations: []

## 34. 375b281e7441547ba284068326dd834216e55c07

In the paper 'Macaw: An Extensible Conversational Information Seeking Platform', What is a wizard of oz setup?

Human reference: seeker interacts with a real conversational interface; intermediary (or the wizard) receives the seeker's message and performs different information seeking actions | Alternative human answer: a setup where the seeker interacts with a real conversational interface and the wizard, an intermediary, performs actions related to the seeker's message

Status: failure; answer: ''; reason: invalid_generation

Diagnosis: generation contract failure; see raw output.

Raw generation: `{"answer":"Yes", "evidence_ids":["E1","E2"]}`

Source citations: []

## 35. 6ecb69360449bb9915ac73c0a816c8ac479cbbfc

In the paper 'Macaw: An Extensible Conversational Information Seeking Platform', What modalities are supported by Macaw?

Human reference: text, speech, image, click, etc

Status: refused; answer: ''; reason: insufficient_evidence

Diagnosis: false refusal; no judged support in top-3 context candidates.

Raw generation: ``

Source citations: []

## 36. e86130c5b9ab28f0ec539c2bed1b1ae9efb99b7d

In the paper 'Resolving the Scope of Speculation and Negation using Transformer-Based Architectures', What is the size of SFU Review corpus?

Human reference: Unanswerable in the named paper

Status: answered; answer: '4'; reason: None

Diagnosis: missing refusal; compare answer and reference; valid IDs/quotes do not establish correctness.

Raw generation: `{"answer":"4", "evidence_ids":["E1"]}`

Source citations: [{'bbox': None, 'document_id': 'qasper-2001.02885', 'element_id': '4e37dde554c143d067b6e92a921b2389ba2da4f00d2c37774cc4072c8af19c52', 'page': 1, 'page_end': 1, 'reranker_score': 3.9846088886260986, 'section': 'Abstract', 'source_url': 'https://arxiv.org/pdf/2001.02885'}]

## Cross-case conclusions

Observed patterns include invented/bracketed citation IDs, JSON with incorrect field types, irrelevant exact quotes, long lists cut by the output limit, and Boolean responses to open questions (the latter is now rejected in v3). The NUS/ABUS example asks for a difference but receives a single success rate; this extractive pipeline cannot perform that calculation. A human reference mentions missing Table 3: it remains unchanged in the frozen labels. Abstract math/reference placeholders and first-1,000-character context truncation limit answer availability. No claim of semantic support is derived from this automated report.
