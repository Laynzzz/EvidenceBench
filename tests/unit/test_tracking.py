import json

import pytest


def test_run_lifecycle_records_early_failure(tmp_path):
    from evidencebench.tracking import run_lifecycle

    with pytest.raises(RuntimeError):
        with run_lifecycle(tmp_path, {"run_id": "fixture"}, 10):
            raise RuntimeError("model failed to load")
    assert json.loads((tmp_path / "manifest.json").read_text())["status"] == "failed"


def test_run_lifecycle_checks_cooperative_deadline(tmp_path):
    from evidencebench.tracking import run_lifecycle

    with pytest.raises(TimeoutError):
        with run_lifecycle(tmp_path, {}, -1):
            pass
