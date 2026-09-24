# Source span-ID experiment runner

The [proposal](span-id-answer-proposal.md) specifies the experiment and approval
limits. No real run is authorized during preparation.

## Read-only preparation

```powershell
.venv/Scripts/python.exe -X utf8 scripts/run_span_id_answer.py
```

This verifies predecessor experiments, cached model files and runtime inventory,
then pins source/evidence/message/span-catalog hashes. It does not load model
weights or generate answers. The printed snapshot hash must match the final
readiness record before requesting approval. The separate tokenizer-only check
uses the isolated GPU environment on CPU to measure all 32 prompts; it is not an
inference run or a memory/performance test.

## Approval and one execution

After explicit user approval, record `reports/span-id-answer-authorization.json`
with `status: approved`, `scope: span-id-answer-v1`, the exact `snapshot_sha256`,
approval provenance/date and these `limits` fields:

```json
{"attempts":1,"generation_calls":32,"reserved_output_tokens":12288,"worker_deadline_seconds":1200,"external_spend_usd":0}
```

Then run once:

```powershell
.venv/Scripts/python.exe -X utf8 scripts/run_span_id_answer.py --run-approved
```

The new root is created exclusively. Preserve any interrupted attempt; do not
delete its ledger to obtain a retry. The private runner adapter reuses the frozen
complete-answer lifecycle, merge, gate and watchdog. The worker independently
checks the new scope, exact snapshot, limits, model/runtime/source/input hashes
and offline mode before loading weights. Its private inference adapter changes
only message rendering and validation, retaining the 384-token budget and durable
meter. An independently imported predecessor keeps its original behavior.

## Saved-result verification

```powershell
.venv/Scripts/python.exe -X utf8 scripts/run_span_id_answer.py --verify
```

This checks hashes, budgets, supervisor completion and exact all-50 reconstruction
from saved raw responses. Quotes are reconstructed from the selected spans. Two
spans in one passage yield two quoted spans and one unique scored passage citation.
The inherited `grounded_generation` trace field contains the new raw output; its
format is identified by the run's `span-id-answer-v1` scope.

Report generation-only latency over the 32 invoked rows, excluding the 18 preserved
historical refusal timings. `status: verified` establishes artifact consistency;
it does not imply the quality gate passed or semantic support was reviewed.

## Synthetic software checks

```powershell
.venv/Scripts/python.exe -m pytest tests/unit/test_span_id_answer.py tests/unit/test_span_id_runner.py -q
```

These use fabricated sources and an injected generator; they load no model. Tests
cover exact source partitions, constraints, adapter isolation, a full synthetic
50-row run, durable reservations, one-use execution and pre-load tamper rejection.
