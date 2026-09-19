"""Copy only this project's pinned public model snapshots into its serving mount."""

import shutil
from pathlib import Path

import yaml
from huggingface_hub import snapshot_download

for config_file in ("configs/retrieval.yaml", "configs/reranker.yaml", "configs/generation.yaml"):
    config = yaml.safe_load(Path(config_file).read_text("utf-8"))
    snapshot = Path(
        snapshot_download(
            config["model_id"],
            revision=config["revision"],
            allow_patterns=["*.json", "*.txt", "*.safetensors", "*.model"],
            local_files_only=False,
            max_workers=1,
        )
    )
    destination = (
        Path("artifacts/hf-cache") / snapshot.parent.parent.name / "snapshots" / snapshot.name
    )
    if not destination.exists():
        shutil.copytree(snapshot, destination, symlinks=False)
    print(f"Prepared {config['model_id']} at its pinned revision")
