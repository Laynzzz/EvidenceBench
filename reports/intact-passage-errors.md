# Intact-paragraph validation failures

These are the original raw outputs and strict validation errors. No response has been repaired or rescored. Malformed outputs are failures, not successful refusals.

## fe2666ace293b4bfac3182db6d0c6f03ea799277

Question: In the paper 'State-of-the-Art Vietnamese Word Segmentation', Why challenges does word segmentation in Vietnamese pose?

Failure: invalid_answer_contract
Validation detail: nonempty answer needs one to three span IDs

```text
{"answer":"Acquiring a very large Vietnamese corpus, applying linguistics knowledge on word context to extract useful features, designing and developing a big data warehouse for Vietnamese documents, and building a system that can incrementally learn new corpora and interactively process feedback.","span_ids":["E2.S2","E2.S3","E2.S4","E2.S8"]}
```
