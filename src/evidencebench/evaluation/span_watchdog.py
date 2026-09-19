"""External wall-clock bound for each of the three local model experiments."""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

from evidencebench.evaluation.span_runner import reserve_variant
from evidencebench.generation_spans import VARIANTS


def run_experiment(variant: str, root=Path("artifacts/answer-improvement-cycle3")) -> int:
    if variant not in VARIANTS:
        raise ValueError("unknown experiment variant")
    started = time.monotonic()
    process = subprocess.Popen(
        [
            sys.executable,
            "-X",
            "utf8",
            "-m",
            "evidencebench.evaluation.span_runner",
            "--variant",
            variant,
        ]
    )
    reason = "process_exit"
    try:
        code = process.wait(timeout=900)
    except (subprocess.TimeoutExpired, KeyboardInterrupt) as exc:
        reason = "watchdog_timeout" if isinstance(exc, subprocess.TimeoutExpired) else "interrupted"
        process.kill()
        process.wait()
        code = 124 if reason == "watchdog_timeout" else 130
    if code:
        # A failure before model initialization must still consume its authorized slot.
        if not (root / "attempts" / f"{variant}.json").exists():
            reserve_variant(root, variant)
        folder = root / "terminations"
        folder.mkdir(parents=True, exist_ok=True)
        record = {
            "variant": variant,
            "reason": reason,
            "exit_code": code,
            "elapsed_seconds": time.monotonic() - started,
        }
        with (folder / f"{variant}-{time.time_ns()}.json").open("x", encoding="utf-8") as stream:
            json.dump(record, stream, indent=2)
    return code


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--variant", choices=VARIANTS, required=True)
    raise SystemExit(run_experiment(parser.parse_args().variant))


if __name__ == "__main__":
    main()
