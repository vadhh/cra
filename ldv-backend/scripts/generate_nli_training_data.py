"""
Generate NLI (premise, hypothesis, label) triples for fine-tuning
typeform/distilbert-base-uncased-mnli on legal clause classification.

Sources:
  - scripts/train_mlp._DATA (160 synthetic full-text clause sentences)
  - data/clause_training_data.csv (keyword-level examples)

Output: data/nli_training_data.jsonl

Usage:
    cd ldv-backend && python3 scripts/generate_nli_training_data.py
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from scripts.train_mlp import _DATA as SYNTH_DATA  # noqa: E402

# Hypothesis → expected NLI label for each clause class
_HYPOTHESES: dict[str, list[tuple[str, str]]] = {
    "abusive_clause": [
        ("This clause is abusive and heavily favors one party.", "entailment"),
        ("This is a balanced and fair contractual provision.", "contradiction"),
    ],
    "payment_risk": [
        ("This clause imposes excessive payment penalties or interest rates.", "entailment"),
        ("This clause describes standard and reasonable payment terms.", "contradiction"),
    ],
    "missing_mandatory": [
        ("This clause is incomplete, a placeholder, or missing key terms.", "entailment"),
        ("This clause is clearly defined and complete.", "contradiction"),
    ],
    "normal": [
        ("This clause is abusive and heavily favors one party.", "contradiction"),
        ("This clause imposes excessive payment penalties or interest rates.", "contradiction"),
        ("This clause is incomplete, a placeholder, or missing key terms.", "contradiction"),
        ("This is a standard and complete contractual provision.", "entailment"),
    ],
}


def _from_master_reasons(datasets_dir: Path) -> list[dict]:
    """Pull Reason text from dangerous_clauses_MASTER.csv as abusive_clause premises."""
    rows: list[dict] = []
    path = datasets_dir / "dangerous_clauses_MASTERv2.csv"
    if not path.exists():
        path = datasets_dir / "dangerous_clauses_MASTER.csv"  # ponytail: fallback to v1
    if not path.exists():
        return rows
    with open(path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            reason = (row.get("Reason") or "").strip()
            if not reason or len(reason) < 20:
                continue
            for hyp, nli_label in _HYPOTHESES["abusive_clause"]:
                rows.append({"premise": reason, "hypothesis": hyp, "label": nli_label})
    return rows


def generate(out_path: Path, csv_path: Path, datasets_dir: Path | None = None) -> None:
    rows: list[dict] = []

    for text, label in SYNTH_DATA:
        for hyp, nli_label in _HYPOTHESES.get(label, []):
            rows.append({"premise": text, "hypothesis": hyp, "label": nli_label})

    if csv_path.exists():
        with open(csv_path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                text  = row.get("text", "").strip()
                label = row.get("label", "").strip()
                if not text or label not in _HYPOTHESES:
                    continue
                for hyp, nli_label in _HYPOTHESES[label]:
                    rows.append({"premise": text, "hypothesis": hyp, "label": nli_label})

    if datasets_dir:
        master_rows = _from_master_reasons(datasets_dir)
        rows.extend(master_rows)
        if master_rows:
            print(f"  +{len(master_rows)} rows from dangerous_clauses_MASTER.csv (Reason field)")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    counts: dict[str, int] = {}
    for r in rows:
        counts[r["label"]] = counts.get(r["label"], 0) + 1

    print(f"Wrote {len(rows)} NLI triples → {out_path}")
    for k in sorted(counts):
        print(f"  {k}: {counts[k]}")


if __name__ == "__main__":
    base = Path(__file__).parent.parent
    generate(
        out_path=base / "data" / "nli_training_data.jsonl",
        csv_path=base / "data" / "clause_training_data.csv",
        datasets_dir=base.parent / "datasets",
    )
