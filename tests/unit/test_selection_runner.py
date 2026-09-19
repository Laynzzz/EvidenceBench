from types import SimpleNamespace

import pytest

from evidencebench.evaluation.selection_runner import validate_dev_roster


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
