"""Experiment B entry point; keep Experiment A's frozen runner unchanged."""

import argparse
import importlib.util
from pathlib import Path

WRAPPER_PATH = Path("scripts/run_claim_grounded_no_cutoff.py")
RUNNER_PATH = Path(__file__).resolve().with_name("run_claim_grounded.py")
spec = importlib.util.spec_from_file_location("claim_grounded_no_cutoff_base", RUNNER_PATH)
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)
runner.SOURCE_PATHS = (*runner.SOURCE_PATHS, WRAPPER_PATH)
_score_candidate = runner.score_candidate


def score_candidate(candidate, previous, decisions, usage, supervisor, baseline_report):
    result = _score_candidate(candidate, previous, decisions, usage, supervisor, baseline_report)
    call_count = sum(decision["generation_calls"] for decision in decisions)
    result["candidate"]["generation_latency_ms"]["scope"] = (
        f"{call_count} supplied-evidence calls; excludes model loading and historical refusals"
    )
    return result


runner.score_candidate = score_candidate


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Prepare, run once, or verify claim-grounded Experiment B."
    )
    parser.add_argument("--baseline-run", type=Path, required=True)
    parser.add_argument("--gpu-python", type=Path, default=runner.GPU_PYTHON)
    parser.add_argument("--experiment", choices=("B",), default="B")
    parser.add_argument("--corpus", type=Path, required=True)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--freeze", action="store_true")
    mode.add_argument("--run-approved", action="store_true")
    mode.add_argument("--verify", action="store_true")
    arguments = parser.parse_args(argv)

    forwarded = [
        "--baseline-run",
        str(arguments.baseline_run),
        "--gpu-python",
        str(arguments.gpu_python),
        "--experiment",
        "B",
        "--corpus",
        str(arguments.corpus),
    ]
    for flag in ("--freeze", "--run-approved", "--verify"):
        if getattr(arguments, flag[2:].replace("-", "_")):
            forwarded.append(flag)
    runner.main(forwarded)


if __name__ == "__main__":
    main()
