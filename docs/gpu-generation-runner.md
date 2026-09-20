# Fixed-input GPU answer-generator runner

The [proposal](gpu-generation-proposal.md) is implemented and prepared; no new
model execution is authorized. Existing 7B model files and the isolated environment
are reused without installation or dependency changes. The previous support-checker
run remains frozen and its allowance is consumed.

## Read-only preflight

From the repository root:

```powershell
.venv/Scripts/python.exe -X utf8 scripts/run_gpu_generation.py
```

This verifies the prior CPU/GPU results, source and model hashes, runtime inventory
and 32 generated prompt/choice payloads. It loads no model and runs no inference;
it requires retained local weights and the isolated runtime for hashing/imports.
Compare its exact snapshot SHA256 with
[readiness](../reports/gpu-generation-readiness.json). The source-span candidates
are constructed by frozen CPU code without labels. References are available only
to the CPU scorer, not worker prompts or generation choices.

## One new explicit approval is required

After the user approves this specific scope, create
`reports/gpu-generation-authorization.json` with `status: approved`,
`scope: gpu-generation-v1`, the exact readiness `snapshot_sha256`, approval text
and recorded time. Never infer this approval from a request to continue or from
an earlier consumed allowance. Then run once:

```powershell
.venv/Scripts/python.exe -X utf8 scripts/run_gpu_generation.py --run-approved
```

One attempt permits at most 32 generation calls, 64 output tokens per call (2,048
reserved total), 20 seconds cooperative per query and 1,200 seconds hard worker
wall time. No warmup, extra benchmark or retry is included. Failure consumes the
attempt; preserve `artifacts/gpu-generation-v1` rather than deleting it for a retry.
No training, final-test access, label revision, paid service or deployment is included.

After completion, verify without inference:

```powershell
.venv/Scripts/python.exe -X utf8 scripts/run_gpu_generation.py --verify
```

The parent recomputes outputs with the frozen span validator and all eight gate
conditions. It retains all 50 rows, including the 18 unchanged empty-evidence
refusals. Unknown becomes a refusal; generation/validation errors become failures.
The worker records raw output, tokens, calls and time for every attempted query.
The source archive, configuration, inputs, manifests, usage and supervisor records
remain local. Report timing on the 32 generated rows separately: old refusal rows
retain their historical traces, so a mixed-row percentile is not GPU latency.

## Verification and limits

All 144 software tests pass including real PostgreSQL, with two existing dependency
deprecation warnings. Eleven new synthetic tests cover the exact prompt/payload
contract, source/citation validation, budget, approval rejection, full fake-worker
50-row roundtrip, Unicode, unchanged refusals, scoring changes, failed supervisor,
single attempt and all-refusal scoring. The GPU trie matches the frozen CPU trie
on a branching-prefix fixture. Static checks pass. Review found one validation
error-handling difference; a failing regression reproduced it and the fix passed.
Follow-up review found no remaining actionable issue.

Read-only review found all 125,041 textual choices in the fixed inputs pass the
frozen validator. Runtime tokenizer/path filtering still follows the existing
fewer-than-64-token rule. No new model load or generation was performed during
preparation. Synthetic success is not a measured answer-quality or GPU result.
