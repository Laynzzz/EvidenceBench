# Proposed complete answers with source span IDs

Status: prepared engineering change; execution requires a new explicit allowance.

## Question and fixed comparison

The [previous complete-answer experiment](../reports/grounded-answer-development.md)
failed: seven responses violated exact-quote/length requirements and three violated
JSON syntax. Test whether replacing generated quotations with selected source span
IDs permits useful complete answers while preserving auditable source quotations.
This changes evidence presentation, prompt and citation selection together; it is
not an isolated answer-length ablation or a demonstrated quality improvement.

Keep the same Qwen2.5-7B checkpoint, isolated CUDA/BF16 runtime, greedy decoding,
50 development questions, saved passage text/order, 1,000-character clipping and
all 18 original evidence-threshold refusals. Generate only the 32 nonempty inputs.
Keep 2,048 input tokens, 384 output tokens and 30 seconds per query. No retrieval,
reference-label changes, new paper text, placeholder repair, corrected answers,
training or final-test access. This is repeatedly inspected development data.

## Deterministic spans and output contract

Split each passage body after its title into ordered spans using punctuation
followed by whitespace, or newline boundaries. Split longer segments at whitespace
word boundaries into at most 40 words. Preserve every non-whitespace character,
original order, internal whitespace and body-relative start/end offsets. Omit only
separator whitespace between spans. This is a text partition, not a linguistic
sentence parser; abbreviations may split and long sentences may need adjacent spans.

IDs have the form `E1.S1`, scoped to one question and fixed evidence. The worker sees
only the question plus passage titles and ordered span IDs/text. Original packed
evidence stays intact in the input artifact; span catalogs and rendered messages
are reproducible from it and are hashed in the approved snapshot. No scoring labels,
old outputs, previous review judgments or gold IDs enter the prompt.

Return exactly:

```json
{"answer":"SVM and logistic regression.","span_ids":["E1.S1","E1.S2"]}
```

An answer may paraphrase/combine sources and must be at most 80 whitespace words.
Require one to three unique existing span IDs. Multiple spans may come from one
passage. Code attaches their exact source quotes, each at most 40 words and at most
120 words in total. Deduplicate parent passage IDs for unchanged citation-ID scoring.
Do not silently truncate quotes or discard selected IDs to force acceptance.

Refusal is exactly `{"answer":"","span_ids":[]}`. Unknown/duplicate IDs,
duplicate JSON keys, extra fields, overlong/whitespace-padded answers, empty-answer
with citations, code fences, token/context overflow and timeouts are failures.
No output repair or retry. JSON errors remain possible; span selection removes
quotation copying and word counting from the model, not all generation failures.
Quotes use the label `exact_quote_presence_only`: they do not prove entailment,
responsiveness, completeness or full-paper correctness.

Alternatives: weakening the old quote validator would change an already measured
protocol and hide its failures; increasing the output budget does not address
inexact copying; structured constrained decoding would add an inference dependency
and still not fix long/inexact quotations. Use deterministic source spans first.
The 40-word partition and three-span limit can omit context needed for support;
semantic review must assess the emitted answer against the actual chosen spans.

## Unchanged predeclared gate

Score all 50 questions, including all failures and the 18 unchanged refusals, using
the same 38-answerable/12-unanswerable denominators and eleven conditions from
the [complete-answer proposal](grounded-answer-proposal.md). In particular:

- Zero new failures versus the constrained 0.5B baseline.
- No more than three answers on benchmark-unanswerable questions.
- F1 strictly above saved 7B span F1 .1235781068.
- Citation-ID precision at least saved 7B .4583333333; undefined fails.
- Retain at least 20 answers, plus all inherited control/baseline requirements.

The failed complete-answer run is retained as a secondary diagnostic comparison,
not the acceptance baseline. Report F1, failures, answer coverage, citation-ID
precision/recall and unanswerable answers together, even if they worsen. Do not
change this gate after seeing results. A pass is development evidence only. Keep
independent semantic review, fresh final evaluation and deployment separate. The
100-question final test remains unused under this allowance.

## Requested compute and environment

One local RTX 4090 device-0 attempt: **at most 32 calls, 12,288 reserved output
tokens, 1,200 seconds hard worker wall time and $0 external spend**. No training,
warmups, repairs, extra candidates, retries, model downloads or runtime changes.
An attempt remains consumed after a model-loading failure or interruption.

Reuse Qwen/Qwen2.5-7B-Instruct revision
`a09a35458c702b33eeacc393d103063234e8bc28`, PyTorch 2.10.0+cu128,
Transformers 4.57.6 and Accelerate 1.12.0. Require at least 17 GiB free VRAM before
loading and all model parameters on CUDA in BF16. No CPU fallback, quantization or
offloading. Preserve the frozen CPU runtime. The last complete-answer worker used
176.969 seconds; that is context, not a runtime guarantee for this new protocol.

## Execution and verification checklist

- Verify body coverage, offsets, word bounds, strict JSON and refusal/failure handling.
- Verify labels cannot enter worker inputs and original packed evidence is intact.
- Reuse frozen metering/generation/supervision/scoring in private module instances;
  pin both the new adapters and all predecessor dependencies in the snapshot.
- Exercise the full synthetic 50-row lifecycle, one-use ledger and tamper rejection.
- Review code; run software checks and read-only cached-asset/prompt-length checks.
- Record a final readiness hash and request explicit approval before model loading.

The new artifact root is `artifacts/span-id-answer-v1`. Existing experiment roots,
scripts, proposals and results remain frozen. Model calls are durably reserved
before inference. The verifier reconstructs predictions from raw span-ID outputs
and fixed source text without inference; existing results are never reinterpreted
under this new contract. See [runner guide](span-id-answer-runner.md).
