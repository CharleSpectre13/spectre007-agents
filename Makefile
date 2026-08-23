.PHONY: install train-smoke test

# Bootstrap the toolchain and sync locked dependencies (same path Cloud Agents use).
install:
	bash .cursor/install.sh

# Tiny CPU-only training run that proves the stack end to end.
train-smoke:
	uv run spectre-train --config configs/smoke-cpu.yaml

test:
	uv run pytest -q
