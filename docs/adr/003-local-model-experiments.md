# 003: Small local models and bounded experiments

Use pinned MiniLM embeddings and a TinyBERT cross-encoder before considering larger
models. The CPU runtime scored 50 fixture pairs in 0.100 seconds; the RTX 4090 is
present but this environment currently has CPU-only PyTorch. No cloud spend is
authorized or used. Compare nested 50/100/200-query hard-negative training and a
matched 200-query random-negative ablation. Keep the subset/mining seed fixed;
repeat the shortlisted configuration with two additional initialization/shuffle
seeds within the recorded shared budget. Time limits are cooperative stage/step
checks, not hard operating-system preemption.

The training script adapts the installed train-sentence-transformers template:
weighted BCE from actual pair balance, pre-training evaluation, early stopping,
best development checkpoint, and save/reload prediction parity. Project policy
overrides the template's cloud tracking/public Hub defaults. MLflow uses local
SQLite plus exported run files. No training or evaluation data is uploaded.

Generation uses pinned SmolLM2-360M-Instruct on CPU, limited to three excerpts,
1,536 input tokens, 100 output tokens, 20 seconds and at most one format repair.
The initial fixture produced a valid cited answer in 1.76 seconds; this establishes
execution only, not benchmark quality. Answers must be exact quotes in their cited
packed passages. Quote validation prevents invented spans but does not prove the
quote answers the question. Human QASPER answer references remain the evaluation
target. Free-form synthesis and multi-passage conclusions are outside this first
extractive configuration; report false refusals and answer coverage explicitly.

Model source: [SmolLM2 model card](https://huggingface.co/HuggingFaceTB/SmolLM2-360M-Instruct).

## Development evidence and revision

SmolLM2's short fixture did not generalize to full evidence. Its real development
pilot was deliberately aborted after 15 of 50 questions: 13 failures, two refusals,
zero answers. Preserve this partial denominator; it is not a complete comparison.
Use Qwen2.5-0.5B-Instruct as the one additional local candidate, pinned in the
release manifest. The local artifact-download ceiling increases from 1,500 to
3,000 MB to accommodate its approximately 1 GB weights. No paid provider is used.

Qwen v2 generated JSON more consistently but still failed 17/50 development cases;
many valid quotes were irrelevant. Boolean answers need a weaker citation-only
check because Yes/No is rarely an exact evidence span. The v3 validator also
requires a boolean-shaped question, after v2 accepted No for open questions.
This fixes a contract defect before final evaluation. It does not establish
semantic support and does not authorize relaxing the human-review acceptance gate.

Release scope is an **experimental local retrieval/reranking API with a limited
answer endpoint**. The optional agent is deferred because core answer quality is
weak. No test outcomes are used to select the model, threshold, prompt or checkpoint.
