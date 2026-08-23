# AGENTS.md

## Learned User Preferences

- Commit and push the repository to GitHub after every training run.
- Treat this repository as a training space: record all training data (raw sources and derived JSONL) and training results in the repo.
- Run the continual-learning loop (`/continual-learning` with the agents-memory-updater) in every session; the user wants it always on.
- Push training experiments to the practical limits of the available hardware.

## Learned Workspace Facts

- uv-managed Python 3.12 stack: torch 2.13 (CPU wheels on Linux via the `pytorch-cpu` uv index), transformers 5.15, trl 1.10, peft 0.20, datasets 5.0, accelerate 1.14; install with `bash .cursor/install.sh` (bootstraps uv, then runs `uv sync --frozen`).
- Training entry point: `uv run spectre-train --config configs/<name>.yaml`; config sections are `model`, `dataset`, optional `lora`, `sft`, and optional `record`.
- Runs whose config has a `record` section write config, final metrics, library versions, and LoRA adapters to `runs/<name>/`, which gets committed.
- Datasets: raw sources are recorded under `data/<dataset>/raw/` with provenance headers; `src/spectre_training/build_dataset.py` deterministically rebuilds `data/<dataset>/train.jsonl` (`make dataset`); tests assert the committed JSONL matches the builder output, so rebuild after changing the builder.
- Dataset sourcing pattern: obtain documentation live via MCP tools; the first dataset packs 12 Svelte animation/transition/motion/easing doc sections fetched through the Svelte MCP server's list-sections + get-documentation flow.
- The Cloud Agent VM is CPU-only (4 cores, ~15GB RAM); the practical training envelope is ~135M-parameter models (e.g. SmolLM2-135M) with LoRA at sequence length ~768, roughly 6-10 s per optimizer step.
- The Cloud Agent environment is the DB-managed Personal environment (not the committed `.cursor/environment.json`) whose install command is `bash .cursor/install.sh`; environment builds are enabled and run on a recurring schedule.
- `uv run pytest -q` must pass; `make train-smoke` is the tiny CPU smoke run that proves the training stack end to end.
