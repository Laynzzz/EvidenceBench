"""Read-only preflight or verification of a retained fresh-validation comparison."""

import argparse
import json
from pathlib import Path

from evidencebench.evaluation.fresh_runner import CORPUS, LABELS, ROOT, preflight
from evidencebench.evaluation.fresh_verification import verify_run
from evidencebench.ingestion import load_units
from evidencebench.labels import read_labels


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, help="Verify saved outputs; never rerun inference")
    args = parser.parse_args()
    snapshot = preflight()
    if args.run:
        manifest = json.loads((args.run / "manifest.json").read_text("utf-8"))
        if manifest["config"] != snapshot:
            raise ValueError("saved run differs from current pinned preflight")
        result = verify_run(args.run, read_labels(LABELS), load_units(CORPUS))
    else:
        result = {
            "preflight": snapshot["status"],
            "queries": snapshot["queries"],
            "paragraphs": snapshot["paragraphs"],
            "attempt_exists": ROOT.exists(),
            "model_calls": 0,
        }
    print(json.dumps(result))


if __name__ == "__main__":
    main()
