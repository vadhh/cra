"""
Fine-tune typeform/distilbert-base-uncased-mnli on LDV NLI clause data.

Requires: transformers, torch (already in requirements.txt)
GPU recommended — CPU works but takes hours.

Usage:
    cd ldv-backend
    python3 scripts/generate_nli_training_data.py   # once
    python3 scripts/finetune_distilbert.py

Output: ~/.cache/ldv/models/distilbert-nli-finetuned/  (or $LDV_DISTILBERT_PATH)

To use the fine-tuned model in Layer 2, set:
    LDV_DISTILBERT_MODEL=~/.cache/ldv/models/distilbert-nli-finetuned
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import torch
from torch.utils.data import DataLoader, Dataset
from transformers import AutoModelForSequenceClassification, AutoTokenizer

_BASE_MODEL = "typeform/distilbert-base-uncased-mnli"
_LABEL2ID = {"entailment": 0, "neutral": 1, "contradiction": 2}
_EPOCHS = 3
_BATCH  = 16
_LR     = 2e-5
_MAX_LEN = 256


class _NLIDataset(Dataset):
    def __init__(self, rows: list[dict], tokenizer, max_len: int):
        self.rows = rows
        self.tok  = tokenizer
        self.max_len = max_len

    def __len__(self) -> int:
        return len(self.rows)

    def __getitem__(self, i: int):
        r = self.rows[i]
        enc = self.tok(
            r["premise"], r["hypothesis"],
            truncation=True, max_length=self.max_len,
            padding="max_length", return_tensors="pt",
        )
        return {k: v.squeeze(0) for k, v in enc.items()}, torch.tensor(_LABEL2ID[r["label"]])


def _load_jsonl(path: Path) -> list[dict]:
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            if r.get("label") in _LABEL2ID:
                rows.append(r)
    return rows


def train(data_path: Path, out_path: Path) -> None:
    rows = _load_jsonl(data_path)
    if not rows:
        print(f"No valid rows in {data_path}. Run generate_nli_training_data.py first.")
        sys.exit(1)

    print(f"Examples: {len(rows)}")
    split = int(len(rows) * 0.8)
    train_rows, val_rows = rows[:split], rows[split:]

    tok   = AutoTokenizer.from_pretrained(_BASE_MODEL)
    model = AutoModelForSequenceClassification.from_pretrained(
        _BASE_MODEL, num_labels=3, ignore_mismatched_sizes=True
    )

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device: {device}")
    model.to(device)

    train_dl = DataLoader(_NLIDataset(train_rows, tok, _MAX_LEN), batch_size=_BATCH, shuffle=True)
    val_dl   = DataLoader(_NLIDataset(val_rows,  tok, _MAX_LEN), batch_size=_BATCH)

    opt = torch.optim.AdamW(model.parameters(), lr=_LR)

    for epoch in range(_EPOCHS):
        model.train()
        total_loss = 0.0
        for feats, labels in train_dl:
            feats  = {k: v.to(device) for k, v in feats.items()}
            labels = labels.to(device)
            out    = model(**feats, labels=labels)
            out.loss.backward()
            opt.step()
            opt.zero_grad()
            total_loss += out.loss.item()

        model.eval()
        correct = total = 0
        with torch.no_grad():
            for feats, labels in val_dl:
                feats = {k: v.to(device) for k, v in feats.items()}
                preds = model(**feats).logits.argmax(-1).cpu()
                correct += (preds == labels).sum().item()
                total   += len(labels)

        print(f"Epoch {epoch+1}/{_EPOCHS}  loss={total_loss/len(train_dl):.3f}  val_acc={correct/total:.3f}")

    out_path.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(out_path)
    tok.save_pretrained(out_path)
    print(f"Saved → {out_path}")
    print(f"Set LDV_DISTILBERT_MODEL={out_path} to use this model in Layer 2.")


if __name__ == "__main__":
    base      = Path(__file__).parent.parent
    data_path = base / "data" / "nli_training_data.jsonl"
    default   = Path.home() / ".cache/ldv/models/distilbert-nli-finetuned"
    out_path  = Path(os.getenv("LDV_DISTILBERT_PATH", str(default)))
    train(data_path, out_path)
