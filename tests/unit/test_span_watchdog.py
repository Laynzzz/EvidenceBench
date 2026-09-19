import subprocess

from evidencebench.evaluation.span_watchdog import run_experiment


def test_watchdog_kills_and_records_timeout_without_releasing_slot(tmp_path, monkeypatch):
    calls = []

    class Process:
        def wait(self, timeout=None):
            calls.append(("wait", timeout))
            if timeout is not None:
                raise subprocess.TimeoutExpired("fixture", timeout)
            return -1

        def kill(self):
            calls.append(("kill",))

    monkeypatch.setattr(subprocess, "Popen", lambda command: Process())
    assert run_experiment("plain", tmp_path) == 124
    assert ("kill",) in calls and ("wait", 900) in calls
    assert (tmp_path / "attempts/plain.json").exists()
    assert len(list((tmp_path / "terminations").glob("plain-*.json"))) == 1
