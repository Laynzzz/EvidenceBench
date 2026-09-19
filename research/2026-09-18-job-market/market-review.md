# EvidenceBench: job-market check and recommended changes

Research date: September 18, 2026. Reviewed against `plan.md` and Layne Xia’s supplied résumé.

**Keep EvidenceBench, but narrow its required scope. The evidence supports an evaluated, deployable ML system. I would revise my earlier advice on agents: a small, evaluated agent workflow is valuable for AI software roles and some MLE internships. LoRA, multimodal processing, and a large infrastructure stack should remain conditional.**

## What was collected

The final sample contains **200 distinct U.S. opportunities: 100 internships/co-ops and 100 permanent full-time roles**. There are **88 Handshake records and 112 LinkedIn records**, representing 124 normalized employer groups. All retained records display a posting or reposting age within the August 19–September 18 window. **50 are explicitly labeled reposts**, as authorized. Their original publication dates are not established.

I collected 230 descriptions, then removed or reserved 30 records. Screening removed duplicate locations/platforms, contracts and AI-rating gigs, unrelated roles, non-U.S. or unverified geography, ambiguous “1 month ago” dates, and a repost with a passed internship cohort. Two experienced vacancies were reserved to prioritize earlier-career roles. Internships remain internships even when their working-hours label says full-time.

Among the 100 full-time records:

| Level | Count |
|---|---:|
| Explicit graduate/entry-level | 62 |
| Early career with a stated 1–2+ year minimum/range | 9 |
| Level not explicit in the description | 21 |
| Experienced comparison group | 7 |
| Three years of academic or industry experience | 1 |

Eight internships and six full-time jobs explicitly require a PhD. One additional full-time job states PhD or equivalent experience. These are flagged individually. **The sample is market evidence, not a claim that all 200 are suitable applications for you.** Graduation windows, degree enrollment, citizenship/clearance conditions, and unpaid internships still matter. For example, the BNP Paribas graduate posting targets December 2026–June 2027 graduates, which does not match your December 2027 graduation date.

The role mix is 96 MLE/modeling, 78 AI application/software, and 26 ML infrastructure roles. These are broad researcher classifications based on titles and duties; the work overlaps substantially.

## What the descriptions actually mention

Each number below is a count out of 100, so it is also the percentage within that employment group. These are **keyword/phrase mention counts in employer descriptions**, including responsibilities and required or preferred qualifications. They are not counts of mandatory requirements. Absence of a term does not mean the skill is unnecessary. Categories overlap.

| Skill or activity | Internships /100 | Full-time /100 |
|---|---:|---:|
| Python | 81 | 78 |
| Evaluation / experimentation | 74 | 67 |
| Serving / deployment | 55 | 70 |
| Statistics / ML foundations / optimization | 52 | 52 |
| LLMs / generative AI | 49 | 70 |
| PyTorch | 46 | 32 |
| Data preparation / pipelines | 42 | 37 |
| Model training / adaptation | 35 | 41 |
| Retrieval / RAG / ranking | 34 | 45 |
| APIs / backend engineering | 33 | 40 |
| Agents / tool use | 32 | 50 |
| Cloud | 27 | 27 |
| Monitoring / observability | 18 | 34 |
| Docker / Kubernetes | 17 | 20 |
| SQL | 16 | 14 |
| Classical ML / scikit-learn | 16 | 14 |
| Software testing / CI | 10 | 17 |
| Experiment-tracking tools | 3 | 6 |
| LoRA / PEFT | 3 | 1 |

Specific-name counts were small: Hugging Face appeared in 9/200, experiment-tracking tools in 9/200, OpenCV in 5/200, and LoRA/PEFT in 4/200. This does **not** make these tools bad choices. It does mean that the plan’s opening list should not present all of them as equally established recruiter demands.

The role split supports a useful distinction: **agents/tool use appeared in 53/78 AI application/SWE descriptions (67.9%), versus 25/96 MLE/modeling descriptions (26.0%)**. PyTorch appeared in 51/96 MLE/modeling descriptions (53.1%), versus 17/78 AI application/SWE descriptions (21.8%). Treat these as descriptive patterns within this search sample, not estimates of the entire profession.

## Evidence that changes or confirms the advice

| Posting in sample | What the employer describes | Implication for your project |
|---|---|---|
| [Gecko Robotics MLE internship](https://app.joinhandshake.com/jobs/11442460) — I014 | Ownership from problem framing through evaluation and integration, with Python data preparation and model work | Keep a complete ML development story, including data and error analysis |
| [Milwaukee Tool MLE internship](https://app.joinhandshake.com/jobs/11367347) — I025 | ML algorithm development and deployment, quantifiable metrics, data collection/testing, Python, ML foundations, and a deep-learning framework | A strong experimental pipeline is directly relevant beyond RAG jobs |
| [Mosaic AI co-op](https://www.linkedin.com/jobs/view/4456040552/) — I050 | Reproducible datasets and training/evaluation workflows, scoped prototypes, and a documented final package | Reproducibility and technical communication belong in the core deliverable |
| [Workiva MLE internship](https://app.joinhandshake.com/jobs/11365188) — I016 | AI-agent development alongside ML workflows, code review, and testing | Agents are relevant even under some MLE internship titles |
| [Shure AI engineering internship](https://www.linkedin.com/jobs/view/4461390753/) — I039 | AI applications, agents, RAG quality evaluation, APIs, and enterprise integration | A bounded agent/API extension strengthens the AI SWE version of the project |
| [Massport AI internship](https://www.linkedin.com/jobs/view/4461102987/) — I096 | Python prototypes, RAG, model/tool integration, cloud/API work, and evaluating reliability and cost; professional experience is not required | A finished, understandable prototype can be useful evidence for an actual entry-level role |
| [C3 AI graduate FDE](https://app.joinhandshake.com/jobs/11427173) — F046 | Software fundamentals plus familiarity with agent architectures and tool execution; deployment experience is preferred | Add one demonstrable agent workflow if pursuing AI application roles |
| [Brain Co. early-career MLE](https://www.linkedin.com/jobs/view/4362406858/) — F038 | Applied ML with 0–2 years of industry experience, production systems, and generative-AI exposure | Combine ML ownership with the software-delivery experience already on your résumé |
| [BNP Paribas graduate MLE](https://www.linkedin.com/jobs/view/4452228077/) — F095 | Retrieval pipelines, reranking, grounding, RAG evaluation, agent frameworks, and ML engineering | EvidenceBench’s central retrieval/evaluation concept is well aligned with at least one explicit graduate specification; its graduation window limits your eligibility |

## Changes I recommend to plan.md

1. **Make the primary claim narrower.** In sections 1–3, describe a reproducible retrieval/reranking system with measured quality, failure modes, and serving trade-offs. RAG/NLP is a coherent specialization. It does not cover every MLE niche, such as robotics, perception, or time-series forecasting. Your existing OCT work already supplies a complementary computer-vision story.

2. **Keep training and evaluation as the MLE core, while making LoRA conditional.** Preserve BM25, untuned dense retrieval, and an untuned reranker baseline. Train or adapt one component when the data and compute justify it. Compare against those baselines and investigate failures. In sections 6, 10, 18, and 20, replace mandatory LoRA completion with reproducible model adaptation and a justified adaptation method. A small full-fine-tuning experiment may be more appropriate than PEFT for the chosen model. Do not force a positive improvement to satisfy a résumé narrative.

3. **Strengthen the data plan before adding features.** Section 8’s 150–250 queries can be a practical starting point for human-reviewed evaluation, but should not automatically serve as the entire training, development, and test corpus. Specify separate training data, query/document-family splits, hard-negative construction, deduplication, and provenance. Use a learning curve to decide whether more training labels help. Review errors on development data; keep the final test set out of model, prompt, and threshold selection. The plan already states that principle—make the implementation phases equally explicit. Report uncertainty when the test set is small.

4. **Revise the agent recommendation rather than removing agents outright.** For an MLE-first application, finish the retrieval/model/evaluation core before adding agents. For AI SWE applications, promote one bounded tool-using workflow into the planned deliverable. Compare it against the deterministic pipeline on task success, incorrect tool calls, refusals, latency, and cost. The hiring signal is reliable behavior and integration, not the number of agents or adoption of a particular orchestration library.

5. **Keep a compact production path.** Retain FastAPI or an equivalent service, Docker, one deployment target, versioned model/data artifacts, CI smoke checks, structured logs, and measured latency. Demonstrate failures, timeouts, and recovery relevant to the actual application. Defer an extensive monitoring stack, object-store setup, multiple serving systems, or elaborate promotion machinery until a concrete need appears. Your existing AWS/Kafka/Terraform and backend projects already demonstrate substantial software infrastructure experience.

6. **Make multimodal modeling a separate extension.** Parsing figure captions or extracting image regions does not establish that you developed a visual model. Retain image/page provenance where it supports citations, but defer OCR and visual-model comparisons unless you deliberately target document-vision roles and can evaluate the incremental value. For CV internships, package the existing OCT research with clear splits, metrics, and limitations instead of adding a weak vision component to EvidenceBench.

7. **Change the definition of done to emphasize evidence.** A reviewer should be able to recreate a baseline, inspect the labeled data and split policy, compare the selected model to the baseline, examine representative failures, and call the deployed service. The demo should make your contribution and trade-offs obvious within five minutes. Tools belong underneath that story.

## Suggested eight-week allocation

This is my project-planning recommendation, not a duration inferred from job descriptions.

| Time | Main output |
|---|---|
| Weeks 1–2 | Corpus, labeling rules, leakage controls, evaluation runner, BM25/dense baselines |
| Weeks 3–4 | One trained/adapted retrieval component, learning curve, hard-negative experiment, error analysis |
| Week 5 | Grounded answers, citation/refusal evaluation, simple service |
| Week 6 | Deployment, latency/cost measurements, reliability checks; AI SWE path adds one bounded agent comparison |
| Weeks 7–8 | Reproduce results, improve the weakest measured component, document limitations, record the demo, prepare résumé evidence |

For an MLE-focused résumé, the eventual bullet should communicate the task, your model/data contribution, a measured held-out result, and the deployment trade-off. Fill in actual measurements only after the experiments. Your backend experience is already substantial; the most valuable new contribution is showing that you can make and defend ML decisions.

## Limits and sensitivity check

This was an authenticated, relevance-ranked convenience sample from LinkedIn and Handshake. Searches included machine learning, AI engineering, internships, and graduate roles. Search terms, personalized ranking, promoted results, seasonality, and platform coverage influence the sample. The deliberate 100/100 employment split is not an estimate of the market’s internship share. Employer identities and application outcomes were not independently audited.

**TikTok/ByteDance accounts for 49/200 records (24.5%)**, including separately identified requisitions with shared wording. I therefore recalculated the main patterns without that employer group. Among the remaining 151 records, Python appears in 79.5%, evaluation/experimentation in 77.5%, serving/deployment in 68.2%, and agents/tool use in 45.7%. The recommendations above do not depend on TikTok dominating the sample.

The closer-to-your-goal subset is also available in the analysis: 92 internships without an identified PhD-only requirement, and 56 explicitly graduate/entry-level full-time roles without a PhD restriction. Neither label guarantees personal eligibility. Job descriptions show what employers advertise; this review cannot establish that a particular project causes a higher hiring probability.

The complete row-level sample is in [job-sample-200.md](./job-sample-200.md), with a machine-readable version in [job-sample-200.json](./job-sample-200.json). Posting ages, repost labels, location, seniority, degree restrictions, skill mentions, and direct sources are retained for every record. `plan.md` has not been changed.
