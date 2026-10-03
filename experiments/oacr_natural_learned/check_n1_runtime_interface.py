"""Exercise the official GRACE/T5 interface without checkpoint or benchmark reads."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from types import SimpleNamespace

import torch
from transformers import T5Config, T5ForConditionalGeneration
from run_n1_dev_only import add_aux, capture_key, cfg, get_adapter, restore, snapshot


class FixedTokenizer:
    def __call__(self, prompts, **kwargs):
        tokens = torch.tensor([[2, 3, 1] for _ in prompts])
        return {"input_ids": tokens, "attention_mask": torch.ones_like(tokens)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--grace_repo", required=True)
    args = parser.parse_args()
    sys.path.insert(0, str(Path(args.grace_repo).resolve()))
    from grace.editors import GRACE

    torch.manual_seed(1729)
    model = T5ForConditionalGeneration(T5Config(
        vocab_size=32, d_model=16, d_ff=32, d_kv=8, num_layers=5,
        num_decoder_layers=1, num_heads=2, dropout_rate=0.0,
        decoder_start_token_id=0, pad_token_id=0, eos_token_id=1,
    )).eval()
    config = cfg("cpu", 2)
    editor = GRACE(config, SimpleNamespace(model=model, tokenizer=FixedTokenizer()))
    tokens = FixedTokenizer()(["synthetic"])
    tokens["labels"] = torch.tensor([[4, 1]])
    editor.edit(config, tokens, batch_history=[])
    adapter = get_adapter(editor)
    initial = snapshot(adapter)
    assert len(initial["keys"]) == 1

    # Calling full T5 without labels/decoder inputs fails; encoder extraction
    # must complete and remove its hook even though neither is supplied.
    original_hooks = len(adapter._forward_pre_hooks)
    key = capture_key(editor, "synthetic")
    assert key.shape == initial["keys"].shape
    assert len(adapter._forward_pre_hooks) == original_hooks
    assert torch.equal(adapter.keys, initial["keys"])
    assert torch.equal(adapter.values, initial["values"])
    assert add_aux(editor, ["aux1", "aux2"], 2) == 2
    assert len(adapter.keys) == len(adapter.values) == len(adapter.epsilons) == 3
    assert torch.equal(adapter.values[1:], initial["values"].expand(2, -1))
    restore(adapter, initial)
    assert len(adapter.keys) == 1 and torch.equal(adapter.values, initial["values"])
    assert torch.isfinite(editor.model(**tokens).loss)
    print("N1 official GRACE + synthetic T5 interface PASS; no benchmark/model download")


if __name__ == "__main__":
    main()
