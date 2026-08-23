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

## Datasets and recorded runs

Training data lives in the repository. The first dataset covers **Svelte
graphics animations**: the raw documentation was obtained from the Svelte
MCP server (12 sections: `transition:`, `in:`/`out:`, `animate:`,
`svelte/transition`, `svelte/animate`, `svelte/motion`, `svelte/easing`,
`{#key}`, scoped/global styles with keyframes, `{@attach}`, `$effect`) and
recorded under `data/svelte-animations/raw/`. `make dataset` rebuilds the
training JSONL deterministically from that raw record.

Every training run configured with a `record` section writes its config,
per-step metrics, stack versions, and any small saved adapter into
`runs/<name>/`, which is committed and pushed after every run:

```bash
make dataset            # rebuild data/svelte-animations/train.jsonl
make train-svelte-tiny  # sanity run: full FT of a tiny GPT-2
make train-svelte-lora  # main run: LoRA on SmolLM2-135M, no truncation
```

Qualitative samples can be recorded with:

```bash
uv run python -m spectre_training.sample \
  --model HuggingFaceTB/SmolLM2-135M \
  --adapter runs/svelte-anim-smollm2-lora \
  --prompt "The transition: directive" \
  --out runs/svelte-anim-smollm2-lora/samples.txt
```

## Layout

```
configs/               Training run configs
data/                  Recorded training datasets (raw sources + JSONL)
runs/                  Recorded training runs (config, metrics, adapters)
src/spectre_training/  Training package (spectre-train, build_dataset, sample)
tests/                 Environment, stack, and dataset tests
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
