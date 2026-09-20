# Local compute and approval policy

The user explicitly permits proposing RTX 4090 training and requires approval for
every new model training or evaluation/testing run, as with prior bounded experiments.
This applies to local GPU work with $0 external spend. A previous approval authorizes
only its recorded attempt and limits; it is not a reusable training budget.

Read-only inspection after the support-filter run found:

- NVIDIA GeForce RTX 4090, 24,564 MiB total memory reported by `nvidia-smi`.
- NVIDIA driver 591.86.
- Current project environment: PyTorch `2.14.0+cpu`; `torch.version.cuda` is null.

The current environment cannot execute CUDA model workloads. A GPU experiment needs
a separate compatible runtime, with dependency versions and model/data hashes pinned.
Preserve the existing environment and frozen manifests for CPU reproduction. No GPU
benchmark, model load, training, inference, installation or driver change was performed
as part of this inspection. Driver presence alone does not verify a working GPU model
pipeline, available free VRAM, performance or a chosen model's memory fit.

Before each new experiment, prepare a concrete proposal stating the objective,
dataset split, fixed comparisons, model/runtime, maximum attempts, calls/steps,
wall-clock time and external spend. Ask for explicit approval before starting model
compute. Record the approval against the actual snapshot. Preserve failures, partial
outputs and metered usage; a replacement attempt needs its own allowance.

The fresh final-test set remains unused. No training/evaluation approval implicitly
authorizes final-test access, paid infrastructure, model publication or deployment.

Subsequent authorized preparation created `artifacts/gpu-support-env` with
PyTorch 2.10.0+cu128, Transformers 4.57.6 and Accelerate 1.12.0, and downloaded the
pinned Qwen2.5-7B checkpoint. Hashes, dependency consistency and imports were checked;
no model was loaded and no GPU tensor workload occurred. The original `.venv` is
still CPU-only. See the [pending proposal](gpu-support-proposal.md) and
[execution guide](gpu-support-runner.md). GPU compatibility and memory fit remain
unverified until the next explicitly approved attempt.
