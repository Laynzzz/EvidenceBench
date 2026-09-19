import json
import subprocess
import sys


def test_build_cli_produces_inspectable_artifacts(pdf_source, tmp_path):
    path, source = pdf_source
    (tmp_path / "backup-v1.pdf").write_bytes(path.read_bytes())
    manifest = tmp_path / "sources.json"
    manifest.write_text(json.dumps({"sources": [source]}))
    config = tmp_path / "corpus.json"
    output = tmp_path / "processed"
    config.write_text(
        json.dumps(
            dict(
                manifest=str(manifest),
                raw_dir=str(tmp_path),
                output=str(output),
                max_words=30,
                overlap=0,
            )
        )
    )
    result = subprocess.run(
        [sys.executable, "-m", "evidencebench.cli", "build", "--config", str(config), "--no-fetch"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["unit_count"] == 2
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "evidencebench.cli",
            "inspect",
            "--corpus",
            str(output),
            "--document",
            "backup-v1",
            "--page",
            "2",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "Restore backups monthly" in result.stdout
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "evidencebench.cli",
            "search",
            "--corpus",
            str(output),
            "--query",
            "encrypt stored files",
            "--system",
            "bm25",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)[0]["page"] == 1
