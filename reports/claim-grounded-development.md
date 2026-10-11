# Claim-grounded answer comparison — Experiment A

**Outcome: failed the predeclared development gate; not promoted.** The intent was
to reduce attribution and refusal errors by attaching evidence spans to individual
claims and tightening the prompt. The change combined output format, instructions,
and span coverage, so this run cannot establish which component caused an outcome.

## Frozen comparison

Experiment A used the same 32 saved intact-paragraph inputs and preserved all 18
earlier threshold refusals in the 50-question roster. The fixed local model was
Qwen2.5-7B-Instruct at revision `a09a35458c702b33eeacc393d103063234e8bc28`, on an
RTX 4090 using BF16 and greedy decoding. The frozen prompt limit was 2,048 input
tokens, the generation cap was 384 tokens per call, and the per-question timeout was
30 seconds. The exact prompt lengths were checked before approval (525–1,286 tokens).

The approved one-use allowance was 32 calls, 12,288 reserved output tokens, a
1,200-second worker deadline, and $0 external spend. The run used all 32 calls,
1,233 output tokens and 73.906 seconds of worker time. Model-load time is excluded
from the per-answer latency figures. No training, deployment, B run, or final-test
access occurred.

## Results on the repeated 50-question development cohort

| Candidate | Answerable token F1 | Answer coverage | Answers | Output failures | Answers to 12 unanswerable items | Citation-ID precision / recall |
|---|---:|---:|---:|---:|---:|---:|
| Control | .0120 | 22% | 11 | 21 | 3 | .364 / .069 |
| Constrained baseline | .0754 | 56% | 28 | 0 | 6 | .321 / .155 |
| Intact paragraphs | .2402 | 62% | 31 | 1 | 6 | .400 / .241 |
| Saved 7B baseline | .1236 | 48% | 24 | 0 | 3 | .458 / .190 |
| Saved span-ID candidate | .2141 | 60% | 30 | 0 | 4 | .429 / .259 |
| **Claim-grounded A** | **.0276** | **8%** | **4** | **28** | **1** | **.600 / .052** |

The 18 historical threshold refusals stayed unchanged. Across A's 32 new outputs,
the model produced no intentional empty-claims refusal. Four answers passed the
output contract; 28 were scored as failures. The candidate's token F1 is far below
the saved span-ID result (.2141), and the small increase in citation precision comes
with very low citation recall and only four answers. Token F1 is reference overlap;
citation-ID precision/recall measure ID agreement, not entailment or answer quality.

The all-twelve-gate decision is **4 passed, 8 failed**. A did not beat the saved
span-ID F1, did not retain the answer-count safeguards, and had more output failures
than the saved baselines. Its only F1 win was over the low control. The descriptive
paired paper-family bootstrap gives an F1 delta of −.2126 versus intact paragraphs
(95% interval [−.3068, −.1234]) and −.1865 versus span-ID ([−.2558, −.1175]); it
uses reused development questions and is not independent confirmation or a
selection-adjusted interval.

## Failure review and conditional stop

Independent artifact verification reconstructed the same saved predictions and
metrics. The strict JSON parser rejected 26 otherwise-complete objects because the
model appended a Markdown closing fence (reported as extra data). Two more outputs
ended before the JSON object was closed. The raw strings remain unchanged; none was
cleaned, retried, or rescored. See the [32-case assistant review](claim-grounded-answer-review.json)
and the raw decisions in the local run artifact.

The four structurally valid answers were reviewed against the frozen rubric. The
dataset-size answer (23,700 queries) was direct and supported; the experiments answer
was supported but only partly complete; the evaluation answer named CCR but added
sentiment classes instead of a second measure; and the TF-IDF answer was directly
supported in the text even though the frozen benchmark labels that question
unanswerable. The TF-IDF discrepancy is preserved as an annotation conflict. No
label, prediction, or score was changed. This assistant review is non-blinded
diagnostic evidence, not independent human acceptance.

Experiment B is **skipped**. A fails two required safeguards: zero output failures
(observed 28) and at least 20 answers (observed four). Its unanswerable-answer count
(one) and citation precision (.600) meet their thresholds, but that does not override
the failed conditions. No B readiness record, approval, or model calls were created.

## Reproduction and limits

The saved development report is [`claim-grounded-development.json`](claim-grounded-development.json).
The raw model outputs, consumed approval receipt, model/runtime details, and verified
50-row predictions remain in the ignored local artifact directory
`artifacts/claim-grounded-v1/runs/20261011T004347Z-8bd4e5608a/`; the large run bundle
is not committed. Recompute the saved result without model inference from the
repository root with:

```powershell
python -X utf8 scripts/run_claim_grounded.py `
  --baseline-run F:\Me\Project\evidencebench\artifacts\intact-passage-v1\runs\20260924T210922Z-e266a7a622 `
  --gpu-python F:\Me\Project\evidencebench\artifacts\gpu-support-env\Scripts\python.exe `
  --verify
```

The current CPU deployment and public API remain unchanged. Results are from a small,
reused development set; the assistant audit is not human acceptance; source-ID
provenance is not proof of semantic support; and the reserved 100-question final set
was not used. GitHub CI for this unpushed branch is unverified. The hash-bound
`plan.md` remains unchanged; current cycle disposition is recorded in
[`docs/status.md`](../docs/status.md).
