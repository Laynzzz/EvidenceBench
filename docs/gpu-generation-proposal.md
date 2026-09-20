# Proposed fixed-input GPU answer-generation comparison

Status: prepared and synthetically verified; awaiting a new explicit allowance.

## Question and fixed protocol

The [saved-answer audit](../reports/gpu-answer-audit.md) found better reference-overlap
spans within existing evidence in 19 of 22 answerable cases. Test whether the cached
Qwen2.5-7B-Instruct model selects better answers than the saved constrained 0.5B
baseline. This is a model/runtime comparison: weights, precision, hardware and
library versions differ. It does not isolate parameter count or establish causality
from the gold-aware diagnostic.

Reuse the exact 50 development questions and saved evidence. Generate on the **32
nonempty packed inputs**, including four that previously yielded model refusals.
Preserve the **18 empty-evidence refusals** without generation. Use the frozen
`generation_spans.py` constrained prompt and choice construction: full question,
up to three 1,000-character passages, eligible source spans of at most 15 words,
UNKNOWN refusal, existing boolean protocol, greedy decoding, fewer than 64 tokens
per eligible token path, 64 maximum new tokens, 1,536 input tokens and 20-second
cooperative per-query timeout. No support checker runs after generation.

The CPU parent prepares prompts and choices from question/evidence only. The GPU
worker receives no reference answers, answerability labels or gold citation IDs.
The CPU parent uses the frozen span/citation validator and recomputes metrics after
the worker exits, rechecking scoring data. Errors count as failures, never refusals.
An eligible token span that fails downstream validation is a per-query failure,
matching the original generator. The other rows remain available for scoring.

## Gate fixed before execution

Score all 50 questions with the original 38-answerable/12-unanswerable denominators.
Retain the previous seven conditions and add strict F1 improvement over the saved
constrained baseline:

1. F1 exceeds original control (.0120252554).
2. Failures do not exceed original control (21).
3. No new failures versus constrained baseline (zero).
4. Answers on unanswerable questions do not exceed control (three of 12).
5. Citation-ID precision is at least control (.3636363636); undefined fails.
6. Retain at least 80% of constrained baseline F1 (.0754244957).
7. Retain at least 14 answers, half the constrained baseline coverage.
8. F1 strictly exceeds the constrained baseline (.0754244957).

Passing all conditions is development evidence only, not automatic deployment or
final-test permission. Report every condition even if the model fails many of them.
No prompt/threshold/packing change, post-hoc candidate selection or alternate model
is included. The flagged label conflict is not relabeled or excluded.

## Requested execution scope

**One local attempt**, at most **32 generation calls**, **2,048 reserved output
tokens**, **1,200 seconds hard GPU-worker wall time**, **$0 external spend**.
No retries, warmup, extra benchmark, training or final-test access. A load, OOM,
timeout or interruption consumes the attempt. Calls are reserved durably before
generation and partial outputs survive failures. CPU preflight/report verification
is outside worker timing and makes no model calls.

Reuse the pinned 7B revision `a09a35458c702b33eeacc393d103063234e8bc28` and existing
isolated runtime: PyTorch 2.10.0+cu128, Transformers 4.57.6, Accelerate 1.12.0.
All model files and package versions must match the existing asset manifest.
Require RTX 4090 device 0, BF16 and at least 17 GiB free VRAM before load. No CPU
fallback, offload, quantization, automatic process closure, new downloads or driver
changes. The successful support-checker run establishes fit for that workload;
longer span generation and its peak VRAM remain unverified.

## Evidence and limits

The external watchdog, exact-snapshot approval, exclusive attempt directory,
offline model loading, strict input schema and hash-based recomputation preserve
earlier experiment controls. Reused frozen source and prior results stay unchanged.
Store a new source archive, raw generations, input hashes, usage and all 50 merged
predictions. Report GPU generation-only timings separately from prior CPU serving
results; the unchanged refusal rows retain their historical traces.

The 15-word limit can still exclude useful multi-part answers. Better source-span
selection cannot restore missing evidence, settle ambiguous questions, correct
benchmark labels or replace independent human generated-claim review. The fresh
100-question final test stays unused. Another attempt requires another approval.
