# GPU support-checker execution

The [proposal](gpu-support-proposal.md) defines one pending experiment. The
[asset manifest](../reports/gpu-support-assets.json) pins the 14 downloaded files
(15,242,807,270 bytes), revision and installed runtime. The isolated environment
uses PyTorch 2.10.0+cu128, Transformers 4.57.6 and Accelerate 1.12.0; the existing
CPU environment remains unchanged. Model artifacts and this environment stay in
ignored local `artifacts/` directories, with no ongoing external charges.

## Read-only preparation

Run from the repository root in PowerShell:

```powershell
.venv/Scripts/python.exe -X utf8 scripts/run_gpu_support_filter.py
```

This checks exact checkpoint inventory and hashes, runtime package versions,
frozen CPU results and the 28 cited-only input objects. It returns a snapshot
SHA256 and does not load a model or allocate GPU tensors. Compare it with
[readiness](../reports/gpu-support-readiness.json). Any snapshot change requires
a newly reviewed proposal before execution. Downloads and package imports do not
establish GPU inference compatibility or peak memory fit.

For environment reconstruction, create an isolated venv using Python 3.12 and
install `configs/gpu-support-requirements.lock` with its interpreter's pip.
Download the exact model revision from the proposal into the manifest's local
directory, then verify every hash. The recorded snapshot includes absolute local
paths and exact packages; reproducing on another machine produces a new snapshot.

## Only after explicit approval

Record the user's explicit approval in `reports/gpu-support-authorization.json`,
including `status: approved`, `scope: gpu-support-v1`, the exact readiness
`snapshot_sha256`, the user's approval text and time. Never create that record
from a general instruction to continue. Then the CPU parent can execute:

```powershell
.venv/Scripts/python.exe -X utf8 scripts/run_gpu_support_filter.py --run-approved
```

The parent creates an exclusive `artifacts/gpu-support-v1` attempt before launching
the offline GPU worker. One attempt permits at most 28 sequential generation calls,
eight output tokens each, no warmup or extra benchmark, and a 1,200-second hard
worker deadline. Failures consume the attempt. Preserve the attempt directory,
termination record, partial decisions and usage; do not delete them to enable a retry.
There is no CPU fallback, offload, training, final-test access or deployment.

After successful execution, this command recomputes the saved metrics without
inference and rechecks the original scoring data and all recorded result hashes:

```powershell
.venv/Scripts/python.exe -X utf8 scripts/run_gpu_support_filter.py --verify
```

Report all seven unchanged gate conditions, retained answers, unsupported verdicts,
runtime failures, actual output tokens and checker-only timings. Compare quality
on all 50 reused development rows. Do not describe GPU checker time as serving
latency, the model/runtime comparison as a pure size ablation, or a passing
automated gate as independent human semantic review.

## Preparation evidence and limits

125 tests pass, including real PostgreSQL and ten new synthetic GPU-runner tests.
The latter cover Unicode JSONL, exact model inventory, scoring-data changes,
approval binding, durable call accounting, single attempts and timeout termination.
Ruff, formatting, schema typing, dependency checks and class imports pass. Existing
CPU reports and the offline selection audit still verify. Follow-up code review
found the three identified defects addressed and no remaining blocking defect.
These are software and artifact checks; no real GPU model execution has occurred.
