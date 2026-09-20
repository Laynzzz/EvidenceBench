# Proposed GPU support-checker comparison

Status: prepared and synthetically verified; **awaiting new model-evaluation approval**.

## Fixed question

The Qwen2.5-0.5B support checker accepted all 28 proposed answers. Test the same
fixed prompt, cited-only payloads, two output labels and scoring rules with
`Qwen/Qwen2.5-7B-Instruct`, revision
`a09a35458c702b33eeacc393d103063234e8bc28`, on the local RTX 4090 in BF16.
This is a larger-model/runtime comparison, not a pure model-size ablation: model
weights, numeric precision, hardware and library versions differ. There is no
claim that a larger checker will improve the result.

Keep the same 50 reused validation questions and the same 28 saved constrained
answers. Check only their cited packed text. No reference answers, gold IDs,
answerability labels or uncited paragraphs enter model inputs. No retrieval,
generation of replacement answers, reranking, prompt tuning or training occurs.
Reuse the seven gate conditions from the completed CPU support-filter proposal:
the four original control comparisons plus no new failures, at least 80% of
unfiltered F1, and at least 14 retained answers. Errors are failures, not refusals.

## Preparation and resource scope

Download the pinned public safetensors/tokenizer files and install a separate CUDA
Python environment under ignored `artifacts/` paths. Preserve the original CPU
environment and frozen experiment sources. Preparation includes artifact hashes,
dependency metadata/import checks and synthetic tests; it includes no GPU tensor
workload, model loading, training or inference. Real GPU compatibility/memory fit
remains unverified until the approved attempt.

Sources checked for this design:

- [Qwen model card](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct): 7.61B parameters,
  Apache-2.0 license, Transformers support. BF16 weight storage alone is about
  15.2 GB decimal; this is not peak VRAM.
- [PyTorch installation archive](https://pytorch.org/get-started/previous-versions/):
  Windows CUDA 12.8 wheels for PyTorch 2.10.0.
- [NVIDIA compatibility documentation](https://docs.nvidia.com/deploy/cuda-compatibility/minor-version-compatibility.html):
  newer drivers retain compatibility with older CUDA applications. A compatible
  version range is not a verified inference run on this machine.

The recorded hardware is an RTX 4090 with 24,564 MiB total memory and driver 591.86.
Other GPU applications may reduce free VRAM. Do not close them automatically.

## Requested new allowance

After preparation and review, request approval for **one** new local evaluation
attempt: at most **28 generation calls**, **224 reserved output tokens** (eight
per check), **20 minutes** hard worker wall-clock time, and **$0 external spend**.
Every check has a cooperative 20-second timeout; all calls run sequentially.
No extra warmup/benchmark call or retry is included. The first model execution is
one of the 28 checks. Require CUDA device 0, BF16, and at least 17 GiB free VRAM
before model loading; no CPU offload, quantization or alternate-model fallback.
The free-memory guard is conservative preparation, not a guarantee against OOM.
Runtime, load, OOM, timeout or interruption failures consume the single attempt.

The parent reserves and snapshots exact inputs, worker code, model files, runtime
versions and protocol before launching the GPU child offline. The child receives
only 28 whitelisted input objects. It retains raw decisions, timings, calls and
actual output-token counts. The CPU parent reconstructs all 50 predictions using
the frozen transformation/scoring helpers after successful child completion.
Verification requires child/supervisor success, exact payload roster, hashes,
unchanged labels and recomputed metrics. Keep checker latency separate from the
historical CPU results and from end-to-end serving latency.

This is development analysis on previously inspected validation data. The new
100-question final test stays unused; independent human generated-claim review
remains outstanding. No passing result authorizes another experiment, training,
final-test access, deployment or model publication.
