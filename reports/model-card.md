# Reranker and generator model card

## Intended use

EvidenceBench ranks evidence from a fixed collection of NLP papers. It is an
agent-assisted learning/portfolio experiment, suitable for inspecting applied-ML
decisions. It is not a validated research assistant, clinical system, or production
service. The user has not yet practiced explaining all implementation decisions.

## Trained component

Base: `cross-encoder/ms-marco-TinyBERT-L2-v2`, pinned commit
`81d1926f67cb8eee2c2be17ca9f793c7c3bd20cc`, Apache-2.0, about 4.39M parameters.
The encoder scores concatenated question/passage pairs after hybrid retrieval
proposes 50 candidates. Maximum sequence length is 384 tokens. The generator and
MiniLM embedding model are not fine-tuned.

Training uses 200 questions from 112 papers, with 266 positive question/passage
pairs and 800 sampled negatives (1,066 pairs total). No dev/test paper
contributes training negatives. Positives are upstream human evidence annotations;
negatives are unjudged sampled passages, not human-verified nonrelevant passages.

Weighted binary cross entropy uses actual negative/positive ratio 3.0075, batch 16,
learning rate 2e-5, three epochs, 10% warmup, CPU fp32, four threads, max length 384.
Development nDCG selects the checkpoint. Subset/mining seed 42 is fixed while
training seeds 42/43/44 assess sensitivity. The release retains seed 42.
Configuration: `configs/training.yaml`; code: `src/evidencebench/training.py`.

Selected checkpoint SHA-256 tree fingerprint:
`7a7ab6f966a2034cd7c1bae44d0e87933e36e0201a5a5362143d7113754d9613`.
Run: `artifacts/training/20260919T021808Z-bce3010267`.
Each run records dependencies, Git state, source archive, pairs, loss/training state,
checkpoint hash, timing, metrics and local MLflow ID. Source archives disambiguate
experiments executed between local commits. See [development report](development-evaluation.md).

## Experimental generation

`Qwen/Qwen2.5-0.5B-Instruct`, commit
`7ae557604adf67be50417f59c2c2f167def9a775`, Apache-2.0, runs locally in fp32.
It sees three 1,000-character excerpts, bounded to 1,536 input and 100 output tokens,
with a cooperative 20-second generation deadline and one format retry.
The development-calibrated top-score threshold is 3.247848.

Nonboolean answers must be exact normalized quotes in every cited excerpt. Boolean
answers are allowed only for questions starting with a supported auxiliary verb;
this English heuristic can reject valid formulations. Their `grounding_check` is
explicitly `citation_references_only`. Neither path proves the answer is relevant
or factually supported. No model is granted tool, shell, file or network actions.

SmolLM2-360M failed frequently on long evidence despite a successful short fixture.
Its aborted 15-query pilot is retained. Qwen v2 completed the 50-question dev run
with 0.1184 token F1, 28% coverage and 17 failures. A subsequent v3 contract fix
rejects Yes/No answers to open questions; final v3 results are recorded separately.
No human semantic-support audit of generated claims has been performed. Thus the
plan's human claim-support and unsupported-claim-rate acceptance criterion remains
unmet; automated F1 and citation overlap must not be substituted for it.

## Limits

Filtered QASPER is small, English, title-conditioned and predominantly NLP papers.
Text/PDF alignment drops figures, tables, ambiguous passages and many questions.
Its scores cannot be compared directly with the official QASPER leaderboard.
Model pretraining overlap is unknown. Long evidence may be truncated twice: at
model token limits and at answer-context packing. A ranking gain need not improve
answers. A narrow sample and wide family-bootstrap interval limit generalization.

Sources: [TinyBERT model card](https://huggingface.co/cross-encoder/ms-marco-TinyBERT-L2-v2),
[Qwen model card](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct),
[QASPER](https://huggingface.co/datasets/allenai/qasper).
