import json

import pytest


def test_protocol_detects_changed_labels_without_loading_examples(tmp_path):
    from evidencebench.ingestion import digest
    from evidencebench.protocol import verify_protocol

    labels = tmp_path / "dev.jsonl"
    labels.write_text("original")
    protocol = tmp_path / "protocol.json"
    protocol.write_text(json.dumps({"files": {str(labels): digest(labels.read_bytes())}}))
    verify_protocol(protocol)
    labels.write_text("changed")
    with pytest.raises(ValueError, match="frozen"):
        verify_protocol(protocol)
