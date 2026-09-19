from types import SimpleNamespace

import pytest

from evidencebench.evaluation.selection_runner import validate_dev_roster, verify_run_budget


def test_budget_retains_interrupted_attempt_and_allows_only_one_completion(tmp_path):
    import json

    verify_run_budget(tmp_path, 2)
    run = tmp_path / "attempt1"
    run.mkdir()
    manifest = run / "manifest.json"
    manifest.write_text(json.dumps({"status": "running"}))
    with pytest.raises(ValueError, match="unresolved"):
        verify_run_budget(tmp_path, 2)
    (run / "termination.json").write_text(json.dumps({"status": "interrupted"}))
    verify_run_budget(tmp_path, 2)
    manifest.write_text(json.dumps({"status": "complete"}))
    with pytest.raises(ValueError, match="budget"):
        verify_run_budget(tmp_path, 2)
    manifest.write_text(json.dumps({"status": "failed"}))
    with pytest.raises(ValueError, match="budget"):
        verify_run_budget(tmp_path, 1)


def test_only_exact_development_roster_can_be_replayed():
    label = SimpleNamespace(
        query_id="dev1",
        split="dev",
        text="Question",
        family_id="paper1",
        answerable=True,
        answer_criteria="Reference",
        supporting_evidence=["unit1"],
    )
    row = dict(
        query_id="dev1",
        question="Question",
        family_id="paper1",
        answerable=True,
        answer_criteria="Reference",
        supporting_evidence=["unit1"],
    )
    validate_dev_roster([row], [label])
    for bad_rows in [
        [],
        [row, row],
        [{**row, "query_id": "test1"}],
        [{**row, "answer_criteria": "Changed"}],
    ]:
        with pytest.raises(ValueError):
            validate_dev_roster(bad_rows, [label])
    label.split = "test"
    with pytest.raises(ValueError, match="development"):
        validate_dev_roster([row], [label])
