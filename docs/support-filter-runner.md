# Prepared support-filter runner

The [fixed proposal](support-filter-proposal.md) is implemented by
[`scripts/run_support_filter.py`](../scripts/run_support_filter.py). It is ready
for a new, explicitly approved allowance, not a completed model experiment.

It checks the 28 saved constrained answers using their cited packed text, preserves
the 22 existing refusals, and scores all 50 development questions. The checker
cannot see reference answers, supporting-ID labels, answerability, or uncited text.
Its only outputs are SUPPORTED or UNSUPPORTED; errors remain explicit failures.
The prompt and seven decision conditions are fixed before inference. The additional
conditions require no new failures, 80% F1 retention and at least 14 retained answers.

## Commands and authorization

From the repository root, preflight performs integrity and cache checks only:

```powershell
.venv/Scripts/python.exe -X utf8 scripts/run_support_filter.py
```

It verifies the existing complete comparison, current frozen inputs and the cached
model snapshots without loading models. It returns a snapshot hash. The
[readiness record](../reports/support-filter-readiness.json) captures this prepared
state. There is currently no support-filter attempt or authorization file.

Only after the user approves the single new allowance, create
`reports/support-filter-authorization.json` with `status: "approved"`,
`scope: "support-filter-v1"`, the exact `snapshot_sha256`, the user's approval text
and a UTC timestamp. Retain that receipt, then execute once:

```powershell
.venv/Scripts/python.exe -X utf8 scripts/run_support_filter.py --run-approved
```

The receipt must match current preflight; it cannot authorize changed source,
prompt, protocol, saved predictions, labels, models or limits. Reserving the attempt
is exclusive. A failed/interrupted attempt is retained and cannot be replayed.
This is a local process control, not an authentication boundary against an operator
who deliberately edits files. It prevents accidental reuse in the intended workflow.

Verify a completed attempt without inference:

```powershell
.venv/Scripts/python.exe -X utf8 scripts/run_support_filter.py --verify
```

The verifier requires successful supervisor termination and the matching worker
claim; verifies config, source archive and output hashes; reconstructs every output
from the original rows and saved decision; checks input hashes and token/call counts;
and recalculates all metrics. Changed references, altered source answers, invalid
successful decisions and hidden model traces on untouched refusals are rejected.

## Runtime boundaries and evidence

The child starts with offline flags set before library imports. It uses the cached
release Qwen weights/tokenizer on CPU, four threads and float32. Only new checker
calls are metered: at most 28 invocations, 28 generation calls and 224 reserved
output tokens. Actual output tokens are saved separately. No retrieval, embeddings,
reranking, training or download is performed.

Twenty seconds per check is cooperative: generation receives remaining `max_time`,
and any check exceeding it is marked failed. An external supervisor kills and waits
for the child at the hard 20-minute worker deadline, including worker preflight and
model startup. Partial output and the consumed attempt remain available for diagnosis.

Each output retains historical original `elapsed_ms` and a separate
`support_check.elapsed_ms`. Summary metrics deliberately omit historical latency
percentiles. Checker timings must be reported separately; this replay is not a new
end-to-end latency or load benchmark.

All output stays under `artifacts/support-filter-v1/`. No service state or frozen
v1/fresh comparison source changes. No final-test examples are read, and no real
checker answers have been produced during preparation. Its quality is unknown;
same-model self-checking is not independent human semantic review.

## Verification completed before requesting execution

Sixteen new synthetic tests cover cited-only inputs, all-query transformations,
malformed/error outcomes, independent retention guards, approval binding, watchdog
cleanup, actual Torch adapter calls with fake weights, full worker/verification,
reference and trace tampering, supervisor failure, and default CLI behavior.
The fake adapter tests perform no real model inference or downloads.

All **115 tests pass**, including real PostgreSQL, with two existing dependency
deprecation warnings. Ruff, formatting and schema typing pass. Read-only real
preflight, earlier report verifiers and the fresh-selection audit recomputation
pass. Code review found no blocking runtime issue; verifier strictness was improved
with reproduced failing tests before correction. Real-model quality and compatibility
remain unmeasured until the newly approved execution is performed.
