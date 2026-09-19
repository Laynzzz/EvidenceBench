# Five-minute recorded-data demo

Use development examples only. The saved API responses are in
`reports/serving-evaluation.json`; they record an actual local run, not mock output.
The [local replay](../reports/demo.html) and [terminal recording](../reports/demo.cast)
contain a real 5.1-second API session. The five-minute narrative below is a separate
presentation guide. This is not a camera/screen video. HTML/JavaScript structure was
checked; browser policy blocked local-file preview, so visual playback is unverified.
Start the service using the [runbook](runbook.md).

## 0:00–1:00 — define the ML task

Show the QASPER dataset card: 350 human-labeled questions, 191 papers, 5,908 paragraphs.
Explain the 200/50/100 split and why paper families must remain disjoint. Open a
source-page citation. Distinguish original human evidence from automated PDF alignment.

## 1:00–2:00 — compare retrieval and training

Open `reports/development-comparison.png`. Compare BM25, dense, hybrid, untuned and
trained reranking in the development report. Explain 266 positive/800 negative pairs,
why random negatives are easier, and why the learning curve is nearly flat.
Show the wide development confidence interval and the separately frozen test result.

## 2:00–3:00 — ask an answerable question

POST to `/api/v1/query`:

```json
{"query":"In the paper 'Mining Supervisor Evaluation and Peer Feedback in Performance Appraisals', What is the average length of the sentences?"}
```

The recorded answer is `15.5`. Open the response's source URL and cited page.
Explain that an exact quote and valid ID establish membership/provenance, not complete
semantic correctness. `/api/v1/retrieve` shows rankings without involving generation.

## 3:00–4:00 — show a failure and refusal

```json
{"query":"In the paper 'Prose for a Painting', How big is English poem description of the painting dataset?"}
```

The recorded response is `refused`. Then open the NUS/ABUS development failure:
it asks for a difference, but the system quotes `94.0%` instead of calculating a gap.
Explain why arithmetic, long lists and missing table content challenge this pipeline.
Do not hide the generator's low coverage and failures behind the reranker's gain.

## 4:00–5:00 — trace the deployed release

Show `/health/ready` and `/api/v1/models/current`. Follow the checkpoint fingerprint
from `configs/release.yaml` into its training run and the final lock. Show the actual
outage/rollback results and 49-test verification. Explain 429 backpressure and why
five repeated warm requests do not establish production p95.

Conclude with the next scientifically valid step: new human claim-support judgments
and improved answer/context handling evaluated on fresh held-out data. No agent,
public hosting or production users are implied by this demo.
