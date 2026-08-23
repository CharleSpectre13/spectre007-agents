"""Tests for the Svelte docs dataset builder."""

import json
from pathlib import Path

from spectre_training.build_dataset import (
    SECTION_HEADINGS,
    build_rows,
    pack_chunks,
    split_blocks,
)

RAW_PATH = Path("data/svelte-animations/raw/svelte-animations-docs.md")
DATASET_PATH = Path("data/svelte-animations/train.jsonl")


def test_split_blocks_keeps_code_fences_intact():
    body = "intro text\n\n```svelte\n<div />\n\n<span />\n```\n\noutro"
    blocks = split_blocks(body)
    assert len(blocks) == 3
    assert blocks[1].startswith("```svelte")
    assert blocks[1].endswith("```")


def test_pack_chunks_respects_budget_per_block():
    blocks = ["a" * 300, "b" * 300, "c" * 300]
    chunks = pack_chunks(blocks, budget=650)
    assert len(chunks) == 2
    assert "".join(chunks).count("a") == 300


def test_build_rows_from_recorded_raw_docs():
    rows = build_rows(RAW_PATH.read_text(encoding="utf-8"))
    assert len(rows) >= 30
    sources = {row["source"] for row in rows}
    assert sources == {slug for _, slug in SECTION_HEADINGS}
    for row in rows:
        assert row["text"].startswith("# Svelte documentation: ")
        assert row["text"].count("```") % 2 == 0
        assert "+++" not in row["text"]


def test_committed_dataset_matches_builder_output():
    committed = [
        json.loads(line)
        for line in DATASET_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    rebuilt = build_rows(RAW_PATH.read_text(encoding="utf-8"))
    assert committed == rebuilt
