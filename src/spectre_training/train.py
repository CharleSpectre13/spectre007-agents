"""Config-driven supervised fine-tuning (SFT) entry point.

Usage:
    spectre-train --config configs/smoke-cpu.yaml

The YAML config has these sections:

- ``model``: Hugging Face model id or local path to fine-tune.
- ``dataset``: where to load training rows from. ``path`` points at a JSONL
  file whose rows contain a ``text`` field (the format TRL's SFTTrainer
  consumes directly).
- ``lora`` (optional): keyword arguments for ``peft.LoraConfig``. Omit the
  section to run full fine-tuning.
- ``sft``: keyword arguments for ``trl.SFTConfig`` (output_dir, max_steps,
  batch size, learning rate, ...).
- ``record`` (optional): ``{dir, name}``. When present, the run's config,
  step-by-step metrics, environment versions, and any small saved adapter
  files are recorded under ``<dir>/<name>/`` so training data and results
  can be committed to the repository.
"""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import accelerate
import datasets as datasets_lib
import peft
import torch
import transformers
import trl
import yaml
from datasets import Dataset
from peft import LoraConfig
from trl import SFTConfig, SFTTrainer

# Copy saved model files into the run record only when they are small
# (LoRA adapters are; full model weights are not).
MAX_RECORDED_FILE_BYTES = 50 * 1024 * 1024

RECORDABLE_FILES = (
    "adapter_config.json",
    "adapter_model.safetensors",
)


def load_config(path: str | Path) -> dict[str, Any]:
    with open(path, encoding="utf-8") as handle:
        config = yaml.safe_load(handle)
    for required in ("model", "dataset", "sft"):
        if required not in config:
            raise KeyError(f"config is missing required section {required!r}")
    return config


def load_jsonl_dataset(path: str | Path) -> Dataset:
    rows = [
        json.loads(line)
        for line in Path(path).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if not rows:
        raise ValueError(f"dataset file {path} contains no rows")
    return Dataset.from_list(rows)


def build_trainer(config: dict[str, Any]) -> SFTTrainer:
    dataset = load_jsonl_dataset(config["dataset"]["path"])
    peft_config = LoraConfig(**config["lora"]) if config.get("lora") else None
    return SFTTrainer(
        model=config["model"],
        args=SFTConfig(**config["sft"]),
        train_dataset=dataset,
        peft_config=peft_config,
    )


def stack_versions() -> dict[str, str]:
    return {
        "torch": torch.__version__,
        "transformers": transformers.__version__,
        "trl": trl.__version__,
        "peft": peft.__version__,
        "datasets": datasets_lib.__version__,
        "accelerate": accelerate.__version__,
    }


def record_run(
    config: dict[str, Any],
    config_path: str,
    trainer: SFTTrainer,
    final_metrics: dict[str, Any],
) -> Path | None:
    record = config.get("record")
    if not record:
        return None

    run_dir = Path(record["dir"]) / record["name"]
    run_dir.mkdir(parents=True, exist_ok=True)

    with (run_dir / "metrics.jsonl").open("w", encoding="utf-8") as handle:
        for entry in trainer.state.log_history:
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")

    run_info = {
        "name": record["name"],
        "config_file": config_path,
        "config": config,
        "finished_at": datetime.now(timezone.utc).isoformat(),
        "train_rows": len(trainer.train_dataset),
        "final_metrics": final_metrics,
        "versions": stack_versions(),
    }
    (run_dir / "run.json").write_text(
        json.dumps(run_info, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    output_dir = Path(trainer.args.output_dir)
    for name in RECORDABLE_FILES:
        source = output_dir / name
        if source.exists() and source.stat().st_size <= MAX_RECORDED_FILE_BYTES:
            shutil.copy2(source, run_dir / name)

    return run_dir


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run supervised fine-tuning from a YAML config."
    )
    parser.add_argument(
        "--config", required=True, help="Path to a YAML training config."
    )
    args = parser.parse_args()

    config = load_config(args.config)
    trainer = build_trainer(config)
    result = trainer.train()
    trainer.save_model()

    output_dir = trainer.args.output_dir
    train_loss = result.metrics.get("train_loss")
    print(f"training complete: train_loss={train_loss:.4f} model saved to {output_dir}")

    run_dir = record_run(config, args.config, trainer, result.metrics)
    if run_dir is not None:
        print(f"run recorded to {run_dir}")


if __name__ == "__main__":
    main()
