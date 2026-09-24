"""One approved intact-passage attempt using the frozen span-ID worker safeguards."""

import argparse
import importlib.util
from pathlib import Path


def load(name):
    path = Path(__file__).with_name(f"{name}.py")
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


contract = load("intact_passage_contract")
backend = load("span_id_answer_worker")
# Both layers are private instances; original workers keep their frozen contracts.
backend.contract = contract
backend.backend.contract = lambda: contract
support = backend.support
validate = backend.validate
evaluate = backend.evaluate
load_generator = backend.load_generator


def run_worker(run, token):
    backend.support = support
    backend.validate = validate
    backend.evaluate = evaluate
    backend.load_generator = load_generator
    return backend.run_worker(run, token)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--token", required=True)
    args = parser.parse_args()
    run_worker(args.run, args.token)


if __name__ == "__main__":
    main()
