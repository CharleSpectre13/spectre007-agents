"""Generate text samples from a base model with an optional LoRA adapter.

Usage:
    uv run python -m spectre_training.sample \
        --model HuggingFaceTB/SmolLM2-135M \
        --adapter runs/svelte-anim-smollm2-lora \
        --prompt "The transition: directive in Svelte" \
        --out runs/svelte-anim-smollm2-lora/samples.txt
"""

from __future__ import annotations

import argparse
from pathlib import Path

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True, help="Base model id or path.")
    parser.add_argument("--adapter", default=None, help="Optional LoRA adapter path.")
    parser.add_argument(
        "--prompt", action="append", required=True, help="Prompt (repeatable)."
    )
    parser.add_argument("--max-new-tokens", type=int, default=80)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--out", default=None, help="Optional file to write samples to.")
    args = parser.parse_args()

    torch.manual_seed(args.seed)
    tokenizer = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForCausalLM.from_pretrained(args.model)
    if args.adapter:
        model = PeftModel.from_pretrained(model, args.adapter)
    model.eval()

    pieces = []
    for prompt in args.prompt:
        inputs = tokenizer(prompt, return_tensors="pt")
        with torch.no_grad():
            output = model.generate(
                **inputs,
                max_new_tokens=args.max_new_tokens,
                do_sample=True,
                top_p=0.9,
                temperature=0.7,
                pad_token_id=tokenizer.eos_token_id,
            )
        text = tokenizer.decode(output[0], skip_special_tokens=True)
        pieces.append(f"=== PROMPT ===\n{prompt}\n=== OUTPUT ===\n{text}\n")

    body = "\n".join(pieces)
    print(body)
    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(body, encoding="utf-8")


if __name__ == "__main__":
    main()
