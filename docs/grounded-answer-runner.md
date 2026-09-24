# Complete-answer experiment runner

This is an experimental answer protocol on saved development evidence. The
[proposal](grounded-answer-proposal.md) defines all changes, gate conditions and
limits. The single approved attempt has now completed and its allowance is consumed.
The [results](../reports/grounded-answer-development.md) fail five of eleven quality
conditions. Use saved-result verification below; execution instructions describe
the historical run and do not authorize another attempt or deletion of its ledger.

## Read-only preflight

From the repository root:

```powershell
.venv/Scripts/python.exe -X utf8 scripts/run_grounded_answer.py
```

This verifies the completed predecessor runs, frozen source/data/results, cached
7B model-file inventory and hashes, isolated runtime inventory and new input
payloads. It loads no model and generates no answers. The printed snapshot hash
must match `reports/grounded-answer-readiness.json` before execution.

## Historical approval and execution

After the user explicitly approves that exact snapshot, record a new
`reports/grounded-answer-authorization.json` with `status: approved`,
`scope: grounded-answer-v1`, its `snapshot_sha256`, approval provenance/date and
the proposed limits. A prior approval or a general instruction to continue cannot
authorize this run.

```powershell
.venv/Scripts/python.exe -X utf8 scripts/run_grounded_answer.py --run-approved
```

The parent exclusively creates `artifacts/grounded-answer-v1`, archives source
and starts the standalone worker using `artifacts/gpu-support-env/Scripts/python.exe`.
The inherited watchdog enforces 20 minutes. The worker rechecks the approval,
source/model/runtime/input hashes and offline environment before loading CUDA BF16
weights. It sends no requests to hosted services and accepts no scoring labels.
There is no automatic retry. A failed or interrupted attempt remains consumed.

Outputs include `inputs.json`, raw `decisions.jsonl`, `usage.json`, hardware details,
all-50 `predictions.jsonl`, `metrics.json`, supervisor termination and source archive.
Every generated answer carries its exact quotations and the label
`exact_quote_presence_only`; this is not a semantic-support verdict.

## Saved-result verification

```powershell
.venv/Scripts/python.exe -X utf8 scripts/run_grounded_answer.py --verify
```

This recomputes validation and metrics from saved raw answers without inference.
It checks all hashes, query order, budgets and supervisor completion. It reports
failure/refusal/answer counts separately and keeps historical timings for the 18
unchanged refusals. New GPU generation latency must be reported over the 32 called
rows separately from prior end-to-end serving latency.

## Software checks

```powershell
.venv/Scripts/python.exe -m pytest tests/unit/test_grounded_answer.py -q
```

These use fabricated passages and an injected synthetic generator. They do not
load a model, establish answer quality or consume an experiment allowance. The
preparation record distinguishes this evidence from the completed real run.
