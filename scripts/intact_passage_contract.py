"""Frozen span-ID output format with bounded, intact paragraph inputs."""

import importlib.util
from pathlib import Path

SCOPE = "intact-passage-v1"
MAX_PASSAGE_CHARACTERS = 4096


def validate_payloads(payloads, expected):
    if not isinstance(payloads, list) or len(payloads) != expected:
        raise ValueError("exact generation roster required")
    seen = set()
    for payload in payloads:
        if not isinstance(payload, dict) or set(payload) != {"query_id", "question", "evidence"}:
            raise ValueError("only whitelisted input fields allowed")
        if not all(
            isinstance(payload[k], str) and payload[k].strip() for k in ("query_id", "question")
        ):
            raise ValueError("nonempty query text required")
        if payload["query_id"] in seen:
            raise ValueError("unique query IDs required")
        seen.add(payload["query_id"])
        evidence = payload["evidence"]
        if not isinstance(evidence, dict) or not 1 <= len(evidence) <= 3:
            raise ValueError("one to three evidence passages required")
        if set(evidence) != {f"E{i}" for i in range(1, len(evidence) + 1)}:
            raise ValueError("sequential evidence aliases required")
        if not all(
            isinstance(v, str) and v.partition("\n")[2].strip() and len(v) <= MAX_PASSAGE_CHARACTERS
            for v in evidence.values()
        ):
            raise ValueError("bounded nonempty paragraph bodies required; never truncate")


path = Path(__file__).with_name("span_id_answer_contract.py")
spec = importlib.util.spec_from_file_location("intact_span_contract", path)
prior = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prior)
# The imported functions retain this private instance's globals, not a shared module.
prior.validate_payloads = validate_payloads
messages, catalog, parse = prior.messages, prior.catalog, prior.parse
SYSTEM = prior.SYSTEM
MAX_INPUT_TOKENS, MAX_NEW_TOKENS = prior.MAX_INPUT_TOKENS, prior.MAX_NEW_TOKENS
TIMEOUT_SECONDS, CALL_LIMIT = prior.TIMEOUT_SECONDS, prior.CALL_LIMIT
ALLOWANCE, LIMITS = prior.ALLOWANCE, prior.LIMITS
