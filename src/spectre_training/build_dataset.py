"""Build a JSONL training dataset from raw Svelte documentation markdown.

Usage:
    uv run python -m spectre_training.build_dataset \
        --raw data/svelte-animations/raw/svelte-animations-docs.md \
        --out data/svelte-animations/train.jsonl

The raw file is the concatenated output of the Svelte MCP server's
get-documentation tool. It is split into sections at known top-level
headings, then each section is chunked into training rows that respect
fenced code blocks. Each row is ``{"text": ..., "source": ..., "chunk": n}``;
the trainer consumes ``text`` and the rest is provenance metadata.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

# Top-level headings of the recorded raw file, in document order,
# mapped to the Svelte docs section slug they came from.
SECTION_HEADINGS: list[tuple[str, str]] = [
    ("## transition:", "svelte/transition"),
    ("## in: and out:", "svelte/in-and-out"),
    ("## animate:", "svelte/animate"),
    ("## svelte/transition", "svelte/svelte-transition"),
    ("## svelte/animate", "svelte/svelte-animate"),
    ("## svelte/motion", "svelte/svelte-motion"),
    ("## svelte/easing", "svelte/svelte-easing"),
    ("## {#key ...}", "svelte/key"),
    ("## Scoped styles", "svelte/scoped-styles"),
    ("## Global styles", "svelte/global-styles"),
    ("## {@attach ...}", "svelte/@attach"),
    ("## $effect", "svelte/$effect"),
]

# Soft budget per training row, in characters. Documentation with code blocks
# tokenizes at roughly 3 chars/token, so ~1600 chars keeps every row within a
# 512-token training window without truncation losing content.
MAX_CHUNK_CHARS = 1600


def strip_doc_markup(text: str) -> str:
    """Remove docs-site render markers that are not part of Svelte syntax."""
    return text.replace("+++", "")


def split_sections(raw: str) -> list[tuple[str, str, str]]:
    """Split the raw markdown into (title, slug, body) tuples in file order."""
    lines = raw.splitlines()
    boundaries: list[tuple[int, str, str]] = []
    remaining = list(SECTION_HEADINGS)
    for idx, line in enumerate(lines):
        if remaining and line.strip() == remaining[0][0]:
            heading, slug = remaining.pop(0)
            boundaries.append((idx, heading.removeprefix("## ").strip(), slug))
    if remaining:
        missing = ", ".join(h for h, _ in remaining)
        raise ValueError(f"raw file is missing expected section headings: {missing}")

    sections = []
    for i, (start, title, slug) in enumerate(boundaries):
        end = boundaries[i + 1][0] if i + 1 < len(boundaries) else len(lines)
        body = "\n".join(lines[start + 1 : end]).strip()
        sections.append((title, slug, body))
    return sections


def split_blocks(body: str) -> list[str]:
    """Split a section body into blocks at blank lines, keeping code fences intact."""
    blocks: list[str] = []
    current: list[str] = []
    in_fence = False
    for line in body.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
        if not in_fence and not line.strip():
            if current:
                blocks.append("\n".join(current))
                current = []
        else:
            current.append(line)
    if current:
        blocks.append("\n".join(current))
    return blocks


def pack_chunks(blocks: list[str], budget: int = MAX_CHUNK_CHARS) -> list[str]:
    """Pack consecutive blocks into chunks of at most ``budget`` characters."""
    chunks: list[str] = []
    current: list[str] = []
    size = 0
    for block in blocks:
        block_size = len(block) + 2
        if current and size + block_size > budget:
            chunks.append("\n\n".join(current))
            current = []
            size = 0
        current.append(block)
        size += block_size
    if current:
        chunks.append("\n\n".join(current))
    return chunks


def build_rows(raw: str) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for title, slug, body in split_sections(strip_doc_markup(raw)):
        for i, chunk in enumerate(pack_chunks(split_blocks(body))):
            text = f"# Svelte documentation: {title}\n\n{chunk}"
            rows.append({"text": text, "source": slug, "chunk": i})
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", required=True, help="Raw concatenated docs markdown.")
    parser.add_argument("--out", required=True, help="Output JSONL path.")
    args = parser.parse_args()

    raw = Path(args.raw).read_text(encoding="utf-8")
    rows = build_rows(raw)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    total_chars = sum(len(row["text"]) for row in rows)
    sources = len({row["source"] for row in rows})
    print(
        f"wrote {len(rows)} rows from {sources} sections to {out_path} "
        f"({total_chars} chars, ~{total_chars // 4} tokens)"
    )


if __name__ == "__main__":
    main()
