"""Synthetic check that telemetry preserves RNG, outputs and codebook tensors."""
from __future__ import annotations
import argparse
from pathlib import Path
import sys
from types import SimpleNamespace

import torch
from transformers import T5Config, T5ForConditionalGeneration
from replay_routing_v1 import RoutingObserver, codebook_digest, runner


class FixedTokenizer:
    def __call__(self, prompts, **kwargs):
        x = torch.tensor([[2, 3, 1] for _ in prompts])
        return {"input_ids": x, "attention_mask": torch.ones_like(x)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--grace_repo", required=True)
    args = parser.parse_args()
    sys.path.insert(0, str(Path(args.grace_repo).resolve()))
    from grace.editors import GRACE
    torch.manual_seed(1729)
    config = runner.cfg("cpu", 2)
    model = T5ForConditionalGeneration(T5Config(
        vocab_size=32, d_model=16, d_ff=32, d_kv=8, num_layers=5,
        num_decoder_layers=1, num_heads=2, dropout_rate=0,
        decoder_start_token_id=0, pad_token_id=0, eos_token_id=1,
    )).eval()
    editor = GRACE(config, SimpleNamespace(model=model, tokenizer=FixedTokenizer()))
    tokens = FixedTokenizer()(["synthetic"])
    tokens["labels"] = torch.tensor([[4, 1]])
    editor.edit(config, tokens, batch_history=[])
    runner.add_aux(editor, ["aux"], 1)
    adapter = runner.get_adapter(editor)
    # Only this synthetic fixture moves the base key so that auxiliary routing
    # is exercised. The real replay never modifies any constructor output.
    adapter.keys[0] += 100
    digest = codebook_digest(adapter)
    initial_rng = torch.get_rng_state().clone()
    with torch.no_grad():
        baseline = editor.model(**tokens).logits.detach().clone()
    baseline_rng = torch.get_rng_state().clone()
    torch.set_rng_state(initial_rng)
    with RoutingObserver(adapter) as observer, torch.no_grad():
        replay = editor.model(**tokens).logits.detach().clone()
    assert torch.equal(baseline, replay)
    assert torch.equal(baseline_rng, torch.get_rng_state())
    assert digest == codebook_digest(adapter)
    assert len(observer.rows) == 1 and observer.rows[0]["auxiliary_active"]
    assert observer.rows[0]["output_change_l2"] > 0
    print("Observer fixture PASS: same logits, RNG, codebook; auxiliary routing detected")


if __name__ == "__main__":
    main()
