# Development citation diagnostics

This offline audit reads the saved cycle-3 predictions and frozen corpus. It makes
no model calls, changes no answers, and supplies no human or semantic judgments.
[Per-query records](citation-diagnostics-development.json) contain the source hashes
and reproduce the previously reported citation-ID precision.

| Exclusive category | Constrained | Focused |
|---|---:|---:|
| Cited paragraph is in the human gold evidence set | 10 | 9 |
| No gold paragraph in packed context | 12 | 12 |
| Gold present; quote also occurs in a gold paragraph | 1 | 1 |
| Gold present; quote not found in its packed text | 2 | 5 |
| Gold present; Boolean answer cites another paragraph | 1 | 1 |
| Answer emitted for an unanswerable question | 2 | 0 |
| Refused | 22 | 22 |
| Total | 50 | 50 |

Each variant answers 28 questions. Constrained matches 10/28 gold citation IDs;
focused matches 9/28. Of constrained's 18 mismatches, 12 have no gold paragraph in
the supplied context. Changing quote attribution alone cannot recover those gold
IDs from the current context. One mismatch has the same answer text in a packed
gold paragraph, consistent with ambiguous first-match attribution. This observation
does not establish that changing its citation would make the answer correct.

The categories are sequential: a gold citation wins first, then gold absence,
then Boolean mismatch, then normalized whole-word quote matching. Paper-title
wrappers are excluded from quote matching. “Gold absent” combines retrieval,
reranking and context-packing limitations; this audit does not isolate those stages.
It also does not prove every non-gold paragraph is irrelevant: upstream annotations
may omit valid support. A gold paragraph may be truncated, and even a complete gold
paragraph does not guarantee that a selected quote answers the question.

The practical next investigation is evidence coverage before generation, with
retrieval and packing measured separately. Do not silently add more passages,
change citation assignment or tune thresholds using the reserved final test.
Candidate changes require a separately bounded development experiment. The existing
three-experiment allowance is spent, and no additional experiment was launched.

Reproduce without inference:

```powershell
.venv/Scripts/python.exe -X utf8 scripts/prepare_fresh_evaluation.py --check
```

The command also verifies the [fresh-family reservation](../docs/fresh-evaluation-protocol.md)
and the original release lock. Reserved families are preparation, not measured
generalization or a completed new benchmark.
