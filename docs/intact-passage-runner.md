# Intact-paragraph comparison runner

The [proposal](intact-passage-proposal.md) and
[readiness record](../reports/intact-passage-readiness.json) describe a prepared,
unexecuted experiment. No model allowance has been granted. The previously approved
span-ID attempt is consumed and cannot authorize this run.

## Read-only preflight and tokenizer check

```powershell
.venv/Scripts/python.exe -X utf8 scripts/run_intact_passage.py
```

Preflight verifies predecessor artifacts, source/model hashes and runtime inventory.
It restores each selected paragraph from development corpus units only after
checking the old 1,000-character prefix. The generator gets only query ID, question
and full selected text. No reference or assistant-review labels select the text.
All 18 threshold refusals remain unchanged. No model weights are loaded.

To reproduce the separately required tokenizer check, save preflight outputs outside
the attempt root:

```powershell
@'
import importlib.util
from pathlib import Path
s = importlib.util.spec_from_file_location('intact', 'scripts/run_intact_passage.py')
m = importlib.util.module_from_spec(s)
s.loader.exec_module(m)
snapshot, inputs = m.preflight()
p = Path('artifacts/intact-passage-preparation')
p.mkdir(exist_ok=True)
(p / 'snapshot.json').write_bytes(m.canonical(snapshot))
(p / 'inputs.json').write_bytes(m.canonical(inputs))
print(m.digest(m.canonical(snapshot)))
'@ | .venv/Scripts/python.exe -X utf8 -

@'
import hashlib, importlib.util, json, os
from pathlib import Path
os.environ['HF_HUB_OFFLINE'] = '1'
os.environ['TRANSFORMERS_OFFLINE'] = '1'
from transformers import AutoTokenizer
def load(name):
    s = importlib.util.spec_from_file_location(name, f'scripts/{name}.py')
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m
c, h = load('intact_passage_contract'), load('gpu_support_worker')
p = Path('artifacts/intact-passage-preparation')
snapshot = json.loads((p / 'snapshot.json').read_text('utf-8'))
inputs = json.loads((p / 'inputs.json').read_text('utf-8'))
assert h.sha(p / 'inputs.json') == snapshot['inputs_sha256']
assert h.runtime_info() == snapshot['runtime']
c.validate_payloads(inputs, 32)
messages = [c.messages(x) for x in inputs]
assert hashlib.sha256(h.encoded(messages)).hexdigest() == snapshot['messages_sha256']
t = AutoTokenizer.from_pretrained(snapshot['model_dir'], local_files_only=True,
                                  trust_remote_code=False)
counts = [len(t.apply_chat_template(x, add_generation_prompt=True)) for x in messages]
assert len(counts) == 32 and max(counts) <= 2048
print({'prompts': len(counts), 'min_tokens': min(counts), 'max_tokens': max(counts)})
'@ | artifacts/gpu-support-env/Scripts/python.exe -X utf8 -
```

The prepared snapshot uses 484–1,245 input tokens and 582 source spans. Eighteen
inputs receive restored tails; 14 are byte-identical to their prior inputs. The
largest paragraph is 1,626 characters, below the new validator's 4,096-character
guard. This is CPU tokenization, not inference or a GPU memory/performance test.
The readiness record pins these checks to the exact snapshot/messages, cached model
manifest and runtime. The runner itself enforces character limits during preflight;
the worker enforces token limits. **Do not authorize or launch a different snapshot
without repeating the separate tokenizer check.**

## Approval and one attempt

After new explicit approval only, record `reports/intact-passage-authorization.json`
with status `approved`, scope `intact-passage-v1`, the exact readiness snapshot hash,
the user's approval text/time, and these limits:

```json
{"attempts":1,"generation_calls":32,"reserved_output_tokens":12288,"worker_deadline_seconds":1200,"external_spend_usd":0}
```

Then run once:

```powershell
.venv/Scripts/python.exe -X utf8 scripts/run_intact_passage.py --run-approved
```

The runner creates `artifacts/intact-passage-v1` exclusively. Do not delete a failed
attempt to get a retry. The worker checks scope, snapshot, allowance, source files,
runtime, model files, inputs and offline mode before loading. Require 17 GiB free
VRAM and CUDA BF16 on RTX 4090; use no CPU fallback. A watchdog bounds worker time
to 1,200 seconds, with at most 32 calls and 384 reserved output tokens per call.

## Saved evidence after execution

```powershell
.venv/Scripts/python.exe -X utf8 scripts/run_intact_passage.py --verify
```

The verifier reconstructs all 50 predictions from raw responses and restored
paragraphs, checks span quotes, budgets and supervisor completion, and recomputes
the twelve gates. Inherited scoring still compares against the original saved 7B
baseline; the extra F1 condition compares against the verified saved span-ID run.
The full text is persisted in each candidate evidence trace, so quotes from restored
tails are auditable. Existing prior predictions and metrics remain frozen.

Report all failures/refusals, coverage, F1, citation-ID precision/recall and generation
latency. Keep changed/unchanged-input analysis exploratory. Do not include historical
threshold-refusal timings in GPU latency. A verified artifact can still fail its
quality gate. Neither exact quotes nor passing software tests prove semantic support.

## Software verification

```powershell
.venv/Scripts/python.exe -X utf8 -m pytest tests/unit/test_intact_passages.py tests/unit/test_intact_passage_runner.py tests/unit/test_intact_passage_worker.py -q --tb=short
```

The 35 new synthetic checks cover restored text, tail-span citations, label exclusion,
frozen-adapter isolation, full 50-row lifecycle, strict F1 comparison and inherited
gate failure, one-use execution and pre-load tampering. All 242 software tests pass
with the existing local PostgreSQL and two existing deprecation warnings. Use UTF-8
mode on Windows; an initial auxiliary run without it failed an existing Unicode
fixture read under GBK, then passed in UTF-8 mode without modifying frozen files.

No training, real new model run, final-test access, deployment or promotion occurred
during preparation. Existing model caches and database remain local; no paid resource
or new persistent service was created.
