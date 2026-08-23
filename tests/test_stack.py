"""Environment smoke checks: the training stack imports and can train."""

import accelerate
import datasets
import peft
import torch
import transformers
import trl

from spectre_training.train import load_config, load_jsonl_dataset


def test_stack_versions_present():
    for module in (torch, transformers, datasets, trl, peft, accelerate):
        assert module.__version__


def test_torch_backward_pass():
    model = torch.nn.Linear(4, 2)
    x = torch.randn(8, 4)
    loss = model(x).pow(2).mean()
    loss.backward()
    assert model.weight.grad is not None
    assert torch.isfinite(loss)


def test_smoke_config_and_dataset_load():
    config = load_config("configs/smoke-cpu.yaml")
    assert config["model"]
    dataset = load_jsonl_dataset(config["dataset"]["path"])
    assert len(dataset) >= 16
    assert "text" in dataset.column_names
