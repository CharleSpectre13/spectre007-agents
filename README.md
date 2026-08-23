# spectre007-agents

Training environment for spectre007 agent models. The stack is
[uv](https://docs.astral.sh/uv/)-managed Python 3.12 with PyTorch,
Transformers, TRL, PEFT, Datasets, and Accelerate, plus a config-driven
supervised fine-tuning (SFT) entry point with optional LoRA.

## Quickstart

```bash
make install      # bootstrap uv and sync locked dependencies
make test         # import + backward-pass + config smoke tests
make train-smoke  # tiny CPU-only SFT run proving the stack end to end
```

`make train-smoke` fine-tunes `sshleifer/tiny-gpt2` with LoRA on the tiny
dataset in `data/smoke.jsonl` and writes the checkpoint to
`outputs/smoke-cpu/`. It finishes in well under a minute on CPU.

## Running a training job

Training runs are described by YAML configs (see `configs/smoke-cpu.yaml`):

```bash
uv run spectre-train --config configs/<your-config>.yaml
```

Config sections:

| Section   | Purpose                                                              |
| --------- | -------------------------------------------------------------------- |
| `model`   | Hugging Face model id or local path to fine-tune.                    |
| `dataset` | `path` to a JSONL file whose rows contain a `text` field.            |
| `lora`    | Optional `peft.LoraConfig` kwargs; omit for full fine-tuning.        |
| `sft`     | `trl.SFTConfig` kwargs (output dir, steps, batch size, lr, ...).     |

## Layout

```
configs/               Training run configs
data/                  Small bundled datasets (smoke tests)
src/spectre_training/  Training package (spectre-train entry point)
tests/                 Environment and stack smoke tests
.cursor/               Cloud Agent environment bootstrap
```

## Notes on hardware

Cloud Agent VMs are CPU-only, so `pyproject.toml` pins Linux to the PyTorch
CPU wheel index for small, reproducible installs. For GPU training hosts,
repoint the `pytorch-cpu` index entry (for example to
`https://download.pytorch.org/whl/cu128`) and re-lock with `uv lock`.

## Cloud Agent environment

`.cursor/install.sh` bootstraps the environment for Cloud Agents: it installs
uv when missing and runs `uv sync --frozen` against the committed `uv.lock`,
so agents boot with the full training stack ready.
