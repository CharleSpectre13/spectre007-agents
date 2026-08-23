.PHONY: install train-smoke test dataset train-svelte-tiny train-svelte-lora

# Bootstrap the toolchain and sync locked dependencies (same path Cloud Agents use).
install:
	bash .cursor/install.sh

# Tiny CPU-only training run that proves the stack end to end.
train-smoke:
	uv run spectre-train --config configs/smoke-cpu.yaml

test:
	uv run pytest -q

# Rebuild the Svelte animations dataset from the recorded raw docs.
dataset:
	uv run python -m spectre_training.build_dataset \
		--raw data/svelte-animations/raw/svelte-animations-docs.md \
		--out data/svelte-animations/train.jsonl

# Training runs on the Svelte animations dataset (results recorded to runs/).
train-svelte-tiny:
	uv run spectre-train --config configs/svelte-anim-tiny.yaml

train-svelte-lora:
	uv run spectre-train --config configs/svelte-anim-smollm2-lora.yaml
