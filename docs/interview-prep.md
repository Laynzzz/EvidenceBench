# Interview preparation

## Thirty-second explanation

EvidenceBench is an agent-assisted retrieval/reranking project over research papers.
It converts upstream human QASPER annotations into a reproducible 200/50/100-question
benchmark with source-page evidence, compares lexical/dense/hybrid baselines, trains
a small cross-encoder, and serves the selected checkpoint through a local containerized
API. Its frozen held-out reranker improves nDCG@10 from 0.378 to 0.501 on 75 answerable
questions; generation remains weak and is reported separately. I still need to
practice explaining the implementation before claiming independent mastery.

## Architecture walkthrough

Original PDFs and human annotations → paragraph/page alignment → immutable content
units → BM25 and MiniLM embeddings → rank fusion → TinyBERT cross-encoder → calibrated
refusal gate → bounded local Qwen output → quote/citation checks → API response.
Training, development selection and held-out testing are separate CLI flows.
The service uses PostgreSQL vectors and never loads labels. Offline ranking uses
NumPy reference vectors; exact top-20 parity was checked on all 50 dev queries.

## Questions and follow-ups

1. **What exactly did you train?** A 4.39M-parameter cross-encoder relevance scorer,
   using weighted binary cross entropy over 266 positive and 800 sampled negative
   pairs. The embedding model and generator were not fine-tuned. Follow-up: why
   reranking instead of LoRA? It directly targets a measurable ranking bottleneck
   and allows a small controlled experiment. See `training.py` and the model card.
2. **Where do the labels come from?** QASPER's original human questions, answers and
   evidence paragraphs, filtered through deterministic PDF alignment. Human review
   is upstream, not invented agent review. Follow-up: what bias does filtering add?
   It excludes many table/figure/ambiguous cases and emphasizes answerable text.
   See the dataset card and frozen selection/protocol files.
3. **How do you prevent leakage?** Preserve paper-family splits, mine negatives only
   from training papers, use nested training subsets and dev-only checkpoint/threshold
   selection, freeze final code/data/config hashes, and allow one final attempt.
   Follow-up: can you rule out pretrained-model exposure? No; public-data overlap is unknown.
4. **Why hard negatives?** They force the reranker to distinguish plausible lexical
   distractors. Matched 200-query random-negative training reached 0.5168 dev nDCG,
   hard negatives 0.5693. Follow-up: are negatives truly irrelevant? Not necessarily;
   unjudged passages can be false negatives. An exact-answer phrase audit is only a proxy.
5. **What did the learning curve show?** 50/100/200 questions scored 0.5628/0.5602/0.5693.
   More labels did not give a monotonic large gain. Follow-up: what would you try next?
   Diagnose label/context quality and gather independently reviewed data before
   changing model size. Any post-test tuning needs new held-out evidence.
6. **How strong is the gain?** Dev's paired interval included zero. The frozen final
   test gain is 0.1238 nDCG, interval [0.0620, 0.1819], using 2,000 paper-family
   bootstrap draws over 41 answerable families. Follow-up: does that establish
   real-world success? No; it describes this small filtered title-conditioned sample.
7. **Why can citations still be wrong?** An ID proves provenance; a quote proves
   text membership. Neither proves that the claim answers the question. Yes/No
   has a weaker reference-only check. Follow-up: what is unsupported-claim rate?
   It has not been measured with new human claim judgments. Do not relabel automated
   citation overlap as semantic support. See development failure inspection.
8. **What failures did testing catch?** Infinite coordinates, train-candidate cache
   scope, a model-card registration failure, invalid citation formats, Boolean answers
   to open questions, readiness trusting stale row counts, and omitted busy-request
   logs. Follow-up: explain a regression test and how the fix addresses the cause.
9. **How does the service behave under load?** One inference lock admits one request;
   three of four simultaneous demo requests received logged 429 responses. This
   bounds work but limits throughput. Follow-up: why not add a queue or more workers?
   Both require measured capacity/memory needs; they are outside this small host demo.
10. **What does deployment prove?** A local Linux image returned a real answer and
    refusal, survived a DB outage with explicit status codes, and rolled back to a
    previous image/release. Five warm demo requests measured 3.06 s p50/3.18 s p95.
    Follow-up: is this production p95? No, just a small repeated local workload.
11. **How can someone reproduce it?** Use the locked environment, frozen data/models,
    exported selected artifacts and immutable run records. Recalculate predictions
    to avoid test retuning. Follow-up: why record dirty Git state/source archives?
    Experiments between commits still need exact code provenance.
12. **What is not built?** Public hosting, production users, agent orchestration, GPU
    training, live quality monitoring and a human generated-claim audit. Their absence
    is explicit; adding infrastructure is not a substitute for better evidence.

## Prospective resume wording — only after you can explain it

“Built an agent-assisted, reproducible retrieval/reranking benchmark from 350 human-
labeled QASPER questions; trained a TinyBERT reranker with controlled negative-sampling
ablations and improved held-out nDCG@10 from 0.378 to 0.501 on 75 answerable questions.”

“Containerized a shared inference pipeline with FastAPI and PostgreSQL/pgvector;
verified 50-query ranking parity across Windows and Linux and tested dependency
failure, bounded concurrency and rollback.”

Before using these, inspect [evidence mapping](evidence-index.md), explain the filtered
dataset and uncertainty, and practice the demo. Do not claim professional deployment,
users, hiring impact, independent implementation, GPU acceleration or reliable answer
accuracy. Do not describe the offline comparison as a production A/B test.

## What did the paper review reveal?

“A post-test AI audit checked all nine emitted answers against their papers and
16 citations. Two answers were clearly correct and supported, four were incorrect,
and three ambiguous. Some outputs quoted real numbers but answered the wrong
question. The audit also exposed conflicting references and ambiguous question scope.
I kept the frozen benchmark labels and scores unchanged.” See the
[complete audit](claim-review.md) for evidence.

Likely follow-up: why not fix the labels and rerun? Changing labels after observing
test outputs would change the evaluation protocol. Record concerns separately and
use independent adjudication and fresh held-out evaluation for future iterations.
Do not present this AI audit as personally performed or independently human-reviewed.

## Why did you reject the sentence-selector candidate?

“A bounded decoder removed all 22 development generation failures, increasing
coverage from 18% to 60%. But F1 fell from .1184 to .1012 and citation-ID precision
fell, so it failed the predeclared gate. Valid source text did not mean the selected
sentence answered the question. I retained the failed experiment and left the
original service unchanged.” This is a development result, not held-out improvement.
See the [comparison](../reports/answer-selection-development.md).

Follow-up: what would you try next? Separate short-span selection, Boolean inference
and output serialization in a new bounded experiment. Preserve the old result and
use fresh held-out families before claiming release-quality improvement. Do not
present these suggested next steps as implemented or validated.

## What happened when you preserved short answers?

“I compared three development variants using the same cached model and retrieved
contexts. Plain prompting failed. A token-trie constraint over source spans improved
development token F1 from .1184 to .1533 and removed generation failures. A focused
question variant had lower F1 but refused all 12 unanswerable development questions.
Both reduced citation-ID precision, so neither became a production-quality claim.”
See the [three-way comparison](../reports/answer-spans-development.md).

Follow-up: how did you avoid cherry-picking? The candidate definitions and F1-first
selection rule were recorded before inference, every attempt was retained, and all
50 questions were scored for every variant. These are repeatedly used development
data, so independent generalization still requires fresh held-out families. Do not
claim that the .1533 result is test accuracy or that the human-review gate is met.

## How did you diagnose the citation regression?

“I used an offline audit of retained predictions. Of the preferred candidate's 18
citation mismatches, 12 had no gold-labeled passage in the packed context. One quote
also appeared in a gold passage, suggesting an attribution ambiguity. Those are
mechanical observations, not proof of semantic correctness. The next evaluation
must distinguish retrieval coverage from evidence lost during packing.” See the
[audit](../reports/citation-diagnostics-development.md).

Follow-up: how do you avoid reusing an exposed test? “I reserved new paper families
in a fixed hash order, excluding all known selected, attempted and cached families.
The manifest records sources, exclusions and fallback order. This is only dataset
preparation; no new held-out result exists, and public pretraining contamination
cannot be ruled out.” Do not claim this audit or reservation as model improvement.

## How did you make the new dataset reproducible?

“I built a separate 150-question QASPER evaluation set over 105 new paper families.
The family and question order, answerability quotas and two-question family cap were
fixed before construction. The builder preserves download attempts and checksums,
reuses the original page aligner, and records excluded candidates. A cache-only
rebuild reproduced the paragraph records and exact label bytes.”

Follow-up: what failed during development? “Code review found automatic redirects
bypassing request pacing and malformed PDFs stopping resume. Synthetic regression
tests reproduced both, and the fixes preceded real acquisition.” Follow-up: what
does the new dataset prove? “It supplies a reproducible evaluation boundary. No
new model quality result exists yet, and upstream human labels are not human review
of generated answers.” See the [build record](fresh-dataset-build.md).

## How would you make the fresh model comparison controlled and bounded?

“The prepared runner retrieves each question once and shares the resulting context
between the control and candidate. It pins data, source, weights and configuration,
keeps references outside model inputs, and retains failures in the evaluation.
Usage reservations are durable, and an external watchdog bounds the entire worker.
Saved results verify only if the supervisor also reports a successful exit.”

Follow-up: is this already a successful experiment? “No. Eleven synthetic tests and
read-only checks of the real artifacts establish implementation readiness. Actual
model execution and fresh quality measurements await the new compute allowance.”
See [the runner](fresh-validation-runner.md). This distinction matters more than
presenting test-fixture scores as model results.

## What happened when you tested the candidate on fresh validation families?

“On 50 fresh validation questions, constrained spans raised token F1 from .0120 to
.0754 and eliminated 21 failures. I did not promote the candidate: it answered six
of 12 unanswerable questions versus three for the control, and citation-ID precision
fell from .364 to .321. Those violated criteria frozen before the run.”

Follow-up: where would you investigate next? “Recall was .9737 among 50 candidates,
.4934 among reranked top three, and .3487 after threshold-based packing. I would
design a separate development experiment for evidence selection and abstention.
These diagnostics do not prove a fix, and I kept the final test unused.”

Follow-up: how much compute and how trustworthy is the result? “One approved
attempt used 86 generation calls and about six minutes on local CPU, with no paid
services. Saved outputs verify against source/model/data hashes and the supervisor
exit. Token F1 and citation IDs remain proxies; generated claims still need
independent human review.” See [the verified report](../reports/fresh-validation.md).
This agent-assisted work is implemented; personal interview practice remains later.

## Why didn't you simply remove the reranker or raise its threshold?

“An offline audit found that reranking improved top-three evidence recall from .1645
to .4934. Its maximum score was much weaker for answerability, with AUC .5702. A
highly relevant passage may still omit the requested fact. I kept those two tasks
separate rather than assuming a relevance score was calibrated answer confidence.”

Follow-up: did another threshold work? “I replayed all 29 distinct stricter-cutoff
states using saved answers. One met the original numerical gate, retaining only
eight answers. That is a post-hoc operating point, not a validated improvement;
I didn't deploy it or change the recorded failure. The next experiment should
measure evidence sufficiency separately.” See [the audit](../reports/fresh-selection-audit.md).

## How would you test support checking without confounding retrieval?

“I prepared an experiment that reuses the exact 28 candidate answers and their
cited packed passages. One fixed checker prompt either keeps each answer or refuses
it; errors remain failures. It scores the full 50-question development set and adds
F1, coverage and reliability safeguards. Gold answers and labels never enter the
checker payload, and retrieval stays identical.”

Follow-up: has it improved quality? “Not yet measured. Sixteen synthetic tests and
real cache/preflight checks establish preparation. A new 28-call local allowance
is needed to measure the fixed design. The same small model may share the original
generator's mistakes; even a passing result would still need independent evaluation
and human support review.” See [the fixed proposal](support-filter-proposal.md).

## Did the explicit support checker help?

“The completed run accepted all 28 answers, including six answers to unanswerable
questions. It changed no quality metric and added about .796 seconds median check
latency. I rejected it rather than presenting its SUPPORTED labels as verified
facts. The fixed experiment consumed 28 calls and its outputs remain reproducible.”

Follow-up: what did that establish? “It rejected this particular intervention on
development data. It doesn't tell us which design component caused the failure or
that all support checking is ineffective.” Follow-up: could you use a GPU? “An RTX
4090 is available, but the existing environment and measurements are CPU-only. A
new GPU experiment needs a compatible isolated runtime and its own approval.”
See [the recorded result](../reports/support-filter-development.md).

## GPU experiment preparation (not a measured GPU result)

**Why isolate the runtime?** Existing CPU experiments pin their dependencies and
source. A separate CUDA environment enables a new comparison without breaking
that evidence. Model revision, every checkpoint file and package inventory are
recorded. Follow-up: what remains nondeterministic across hardware?

**How do you stop a checker from seeing evaluation labels?** The parent constructs
objects containing only the question, proposed answer and cited text. The worker
validates their exact schema and hash; scoring runs afterward in the parent.
This is explicit input separation, not a security sandbox. Follow-up: why recheck
scoring-data hashes after the worker exits?

**What does the GPU preparation establish?** Synthetic orchestration and approval
boundaries pass, and artifacts/imports verify. It does not establish GPU model
fit, latency or better answers. The proposed comparison changes model, precision
and runtime, so it cannot isolate model size. See the
[proposal](gpu-support-proposal.md) and [tests](../tests/unit/test_gpu_support.py).
This was built with agent assistance; personal understanding remains to practice.

## Discussing the completed GPU experiment

**Did the larger checker improve the system?** It reduced answers on unanswerable
questions from six to one but rejected 24 of 28 answers. F1 fell to .013068 and
coverage to 8%; the fixed gate failed. I would report the trade-off and reject
promotion, rather than cite only the improved abstention metric.

**What did you learn about the GPU implementation?** The pinned 7B model loaded
and ran in BF16 on RTX 4090 with no runtime failures, using 28 calls and 38.765
seconds of worker time. Checker-only timings do not measure serving latency or
training capacity. No additional benchmark was needed to complete the experiment.

**What would you investigate next?** Inspect rejected answers against their cited
text and source papers, separating poor evidence packing, answer generation and
checker mistakes. Scaling the checker changed refusal behavior but did not meet
acceptance. [Evidence](../reports/gpu-support-development.md) is development-only;
independent human review and personal interview practice remain outstanding.

## Correcting an interpretation after error analysis

**Does a large F1 drop prove the checker rejected useful answers?** No. An offline
review found many copied but nonresponsive spans. Token overlap credits shared
words without checking the requested relation or quantity. The frozen gate still
fails; this diagnosis changes the explanation, not the benchmark result.

**How would you isolate the next bottleneck?** Keep retrieval, packing, question
wording and output contract fixed, then compare a stronger answer selector. A
gold-aware span ceiling suggests opportunity, but is never a deployable policy.
One possible label conflict is flagged for adjudication without retroactive
rescores. See the [audit](../reports/gpu-answer-audit.md).

## Designing the next comparison before spending compute

**What stays fixed in the larger-generator experiment?** Questions, selected
passages, their clipping, prompt, candidate-span rules and acceptance metrics.
Only 32 rows have evidence; the 18 threshold refusals remain in all-50 scoring.
Model/precision/runtime differ, so parameter-count causality cannot be claimed.

**How do you avoid declaring a weak candidate a success?** Preserve the previous
seven gate conditions and additionally require F1 above the saved constrained
baseline. Report failed gates and consumption even on crashes. The
[proposal](gpu-generation-proposal.md) is prepared, not executed, and the new
allowance must be approved before any model loading or inference.
