"""Config-driven supervised fine-tuning (SFT) entry point.

Usage:
    spectre-train --config configs/smoke-cpu.yaml

The YAML config has four sections:

- ``model``: Hugging Face model id or local path to fine-tune.
- ``dataset``: where to load training rows from. ``path`` points at a JSONL
  file whose rows contain a ``text`` field (the format TRL's SFTTrainer
  consumes directly).
- ``lora`` (optional): keyword arguments for ``peft.LoraConfig``. Omit the
  section to run full fine-tuning.
- ``sft``: keyword arguments for ``trl.SFTConfig`` (output_dir, max_steps,
  batch size, learning rate, ...).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml
from datasets import Dataset
from peft import LoraConfig
from trl import SFTConfig, SFTTrainer


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


if __name__ == "__main__":
    main()
