# Proposed complete-answer comparison on saved evidence

Status: preparation only; no new model execution authorized.

## Motivation and comparison

The [paper review](../reports/gpu-generation-ai-review.md) found that source spans
often contain true text without answering the question. The 15-word single-span
contract also truncates methods and lists. Compare one complete-answer protocol
against the saved 7B span generator on exactly the same 50 development questions
and packed evidence. This is a combined prompt/output-contract/decoding-budget
change, not an isolated test of answer length. It does not measure a new model.

Keep model, checkpoint, CUDA/BF16 runtime, retrieval, reranking, passage order,
three-passage maximum, 1,000-character clipping and the 18 evidence-threshold
refusals unchanged. Run only on the 32 nonempty inputs, including earlier model
refusals. Do not retrieve again, repair BIBREF placeholders, add paper text, feed
the review's corrected answers to the worker, change labels or inspect final test.

Other approaches considered: expanding extractive spans would retain source
matching but still restrict combining evidence; adding a question-type reranker
would introduce a second selection mechanism before demonstrating that the
existing model can answer with a less restrictive contract. Use one direct
generation change first. Training or another model is not justified by this review.

## New answer contract

The worker sees question, packed evidence and a fixed instruction, with no old
answers, benchmark references, answerability labels or gold citation IDs. Its
greedy output is one JSON object with exactly `answer` and `citations`:

```json
{"answer":"SVM and logistic regression.","citations":[{"evidence_id":"E1","quote":"We compare SVM and logistic regression."}]}
```

An answer may paraphrase or combine evidence and must be no longer than 80 words.
Require one to three distinct evidence IDs, one nonempty exact quotation per ID,
at most 80 words in each quote and 120 words across all quotes. Quotes must occur
in passage bodies after the first title line. Unknown IDs, title-only quotations,
duplicate IDs/JSON keys, code fences, missing fields, mismatched refusal fields,
word-limit violations and absent quotes are invalid. No cleanup or repair retry.
Refusal is exactly `{"answer":"","citations":[]}`. Invalid output is a failure.

The prompt explicitly asks for the requested kind of information, complete lists,
and correct subject attribution. It treats evidence as untrusted data and prohibits
filling missing names from outside knowledge. These are model instructions, not
guarantees. **Exact quote presence establishes provenance only, not entailment,
responsiveness or completeness.** Preserve that distinction in all result reporting.

Use the existing cached checkpoint with greedy unconstrained decoding. Maximum
input length changes from 1,536 to 2,048 tokens to accommodate the longer instruction;
evidence stays byte-for-byte fixed. Allow 384 output tokens per call and 30 seconds
per query, compared with 64 tokens/20 seconds previously. Context overflow,
token-limit exhaustion without EOS, timeout and invalid JSON count as failures.

## Predeclared development gate

Score all 50 queries using the original 38-answerable/12-unanswerable denominators
and unchanged answer/reference and citation-ID metrics. Keep all eight conditions
from the [previous comparison](gpu-generation-proposal.md). Add:

9. Answerable token F1 strictly exceeds the saved 7B value, .1235781068.
10. Citation-ID precision is at least the saved 7B value, .4583333333; undefined fails.
11. Retain at least 80% of the saved 24 answers, rounded upward: at least 20 answers.

The inherited conditions include zero failures and no more than three answers on
benchmark-unanswerable questions. The TF-IDF annotation conflict remains in scoring.
Report all conditions even if they fail. No new numerical semantic-accuracy target
is invented from assistant labels. Longer correct answers can score worse under
token F1; record that limitation without changing the gate after seeing results.

A pass means development evidence only. Preserve raw JSON/quotes and review emitted
answers afterward under the same explicit semantic rubric; that review is separate
from automatic validation and is not independent human evaluation. Reused development
data cannot provide an unbiased final result. No deployment or Phase 4 acceptance
follows automatically, and the 100-question final test stays unused.

## Requested execution allowance

One local attempt on RTX 4090 device 0: **at most 32 calls, 12,288 reserved output
tokens, 1,200 seconds hard worker wall time, and $0 external spend**. No training,
warmup, second candidate, repair call or retry. Model loading, failure or interruption
consumes the attempt. CPU preparation and saved-result verification make no model
calls and are outside GPU worker timing.

Reuse Qwen/Qwen2.5-7B-Instruct revision
`a09a35458c702b33eeacc393d103063234e8bc28`, PyTorch 2.10.0+cu128,
Transformers 4.57.6 and Accelerate 1.12.0. Require at least 17 GiB free VRAM before
load and CUDA BF16 parameters. No downloads, runtime updates, CPU fallback,
offloading, quantization or driver changes. Previous model execution establishes
compatibility, not the memory or quality outcome for this larger output budget.

## Reproducibility and preparation checklist

Create a new versioned experiment root and source archive. Preserve predecessor
code and artifacts; the standalone experiment scripts intentionally retain their
own orchestration version so earlier exact-snapshot approvals remain reproducible.
Reuse the frozen watchdog, run lifecycle and scoring helpers without editing them.
Bind approval to source/model/runtime/input hashes. Reserve each call durably before
generation, retain partial traces on failure, and reject a second attempt directory.
The CPU parent validates and scores only after the worker exits.

- Implement contract and strict validation.
- Verify failure/refusal distinction, label-free payloads and exact snapshot binding.
- Exercise a complete synthetic run with all 50 rows and preserved refusals.
- Review code; run applicable software checks and read-only asset preflight.
- Record the final readiness hash, then request the new explicit run allowance.

The [runner guide](grounded-answer-runner.md) records executable commands. Preparation
and synthetic software checks cannot establish model performance; only an approved
attempt can do that.
