# Skills for EvidenceBench

Reviewed 2026-09-18 against `plan.md` and `AGENTS.md`. This is a selection guide,
not permission to install skills, publish artifacts, or change the architecture.

## Available now

| Skill | Project use | When |
|---|---|---|
| executing-plans | Track phase acceptance gates and implement the approved design | Throughout |
| test-driven-development | Behavioral tests for ingestion, splits, metrics, retrieval, and API failures | Each feature |
| systematic-debugging | Investigate extraction, model, database, and runtime failures before fixes | When a failure occurs |
| verification-before-completion | Require fresh checks and evidence before claiming a milestone passes | Each checkpoint |
| pdf:pdf | Inspect extracted text, coordinates, and rendered source pages | Corpus pilot and extraction changes |
| requesting-code-review | Independent review of consequential code and plan compliance | Major feature checkpoints |
| using-git-worktrees | Assess workspace isolation before concurrent or separate branch work | Workspace setup when needed |
| browser:control-in-app-browser or playwright | Check API documentation and any later demo in a real browser | Serving/demo phase |
| visualize:visualize | Explain architecture and comparisons during the later learning handoff | When interactive explanation helps |
| finishing-a-development-branch | Verify and hand off a completed branch | Actual completion |

Use one browser-control workflow for a task. Do not add UI or spreadsheet work just
because corresponding skills are available. `brainstorming` and `writing-plans`
support material design changes; the user has already approved this plan for implementation.

## External additions

1. **[train-sentence-transformers](https://github.com/huggingface/skills/blob/main/skills/train-sentence-transformers/SKILL.md)**
   is installed (2026-09-18). It covers CrossEncoder training, loss/data formats,
   hard-negative mining, evaluators, and training troubleshooting. Use its
   CrossEncoder references for phase 3. Preserve our train/dev/test protocol,
   predeclared comparisons, and MLflow choice. Its default Hub upload conflicts
   with our local-only publishing authorization: disable all automatic uploads.
2. **[hf-cli](https://github.com/huggingface/skills/blob/main/skills/hf-cli/SKILL.md)**
   is installed (2026-09-18). It helps discover/download models and inspect Hub resources. Use only the
   needed read/download operations and record immutable model revisions.
3. **[hf-mem](https://github.com/huggingface/skills/blob/main/skills/hf-mem/SKILL.md)**
   estimates model loading/inference memory for model selection. Estimates do not
   replace measured training peak memory, throughput, or our hardware pilot.
4. **[jupyter-notebook](https://github.com/openai/skills/blob/main/skills/.curated/jupyter-notebook/SKILL.md)**
   is optional for later experiment explanations and teaching. The package/CLI
   remains the executable source of truth; notebooks import it.

Sources checked: the installed skill files, OpenAI's curated skill listing, and
the current Hugging Face skill definitions. The two recommended skills were
subsequently installed at the user's request; hf-mem and jupyter-notebook were not.

## Gaps and scope controls

- No reviewed skill here replaces project-specific graded relevance labels,
  family leakage checks, paired retrieval metrics, or bootstrap design.
- Use official library documentation for PyTorch, sentence-transformers,
  pgvector, FastAPI, and MLflow compatibility when implementing those components.
- A general LLM evaluation skill is not automatically a fit for this custom
  retrieval benchmark. A Hub dataset-access skill does not provide human label review.
- Defer cloud-training/hosting, Trackio, vision training, and agent-framework
  skills: they would add services or work outside the current core priorities.
- Do not load every skill on every turn. Read the relevant instructions and
  apply them at their phase; repository and user instructions retain precedence.
