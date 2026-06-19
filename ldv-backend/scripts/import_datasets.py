"""
scripts/import_datasets.py — Convert datasets/ CSVs into clause_training_data.csv.

Reads all clause datasets and maps their categories to MLP labels, then appends
new rows into ldv-backend/data/clause_training_data.csv, ready for train_mlp.py.

Usage
-----
    cd ldv-backend
    python3 scripts/import_datasets.py

Output
------
    ldv-backend/data/clause_training_data.csv  (appended, not overwritten)

Run train_mlp.py afterwards to retrain:
    python3 scripts/train_mlp.py

Category → MLP label mapping
-----------------------------
    Detection               → normal
    Missing                 → missing_mandatory
    Dangerous / Abusive
    Leonine / Illegal       → abusive_clause
"""
from __future__ import annotations

import csv
from pathlib import Path

DATASETS_DIR = Path(__file__).parent.parent.parent / "datasets"
OUT_CSV      = Path(__file__).parent.parent / "data" / "clause_training_data.csv"

# Files that have a header row
_HAS_HEADER = {
    "dangerous_clauses.csv",
    "contract_logic_master_sorted.csv",
    "contract_logic_master .csv",
    "required_clauses.csv",
}

# Column indices (0-based)
_COL_CATEGORY    = 1
_COL_CLAUSE_NAME = 2
_COL_KEYWORDS    = 4

# Category → MLP label
_CATEGORY_MAP: dict[str, str] = {
    "detection": "normal",
    "missing":   "missing_mandatory",
    "dangerous": "abusive_clause",
    "abusive":   "abusive_clause",
    "leonine":   "abusive_clause",
    "illegal":   "abusive_clause",
}

# Skip non-clause files
_SKIP_FILES = {"risk_levels.csv"}


def _rows_from_file(path: Path) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    has_header = path.name in _HAS_HEADER
    skipped = 0
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if i == 0 and has_header:
                continue
            if len(row) <= _COL_KEYWORDS:
                skipped += 1
                continue
            category    = row[_COL_CATEGORY].strip().lower()
            clause_name = row[_COL_CLAUSE_NAME].strip()
            keywords    = row[_COL_KEYWORDS].strip()
            label       = _CATEGORY_MAP.get(category)
            if not keywords or label is None:
                skipped += 1
                continue
            text = f"{clause_name}: {keywords}" if clause_name else keywords
            rows.append((text, label))
    if skipped:
        print(f"    (skipped {skipped} rows — unknown category or empty keywords)")
    return rows


def main() -> None:
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)

    # Load existing texts to avoid duplicates
    existing: set[str] = set()
    if OUT_CSV.exists() and OUT_CSV.stat().st_size > 0:
        with open(OUT_CSV, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                existing.add(row.get("text", "").strip())

    new_rows: list[tuple[str, str]] = []
    for csv_file in sorted(DATASETS_DIR.glob("*.csv")):
        if csv_file.name in _SKIP_FILES:
            continue
        file_rows = _rows_from_file(csv_file)
        added = [(t, l) for t, l in file_rows if t not in existing]
        label_counts: dict[str, int] = {}
        for _, lbl in added:
            label_counts[lbl] = label_counts.get(lbl, 0) + 1
        print(f"  {csv_file.name}: {len(file_rows)} rows read, {len(added)} new {dict(sorted(label_counts.items()))}")
        new_rows.extend(added)
        existing.update(t for t, _ in added)

    if not new_rows:
        print("Nothing new to add.")
        return

    write_header = not OUT_CSV.exists() or OUT_CSV.stat().st_size == 0
    with open(OUT_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(["text", "label"])
        writer.writerows(new_rows)

    total_by_label: dict[str, int] = {}
    for _, lbl in new_rows:
        total_by_label[lbl] = total_by_label.get(lbl, 0) + 1

    print(f"\nAdded {len(new_rows)} rows → {OUT_CSV}")
    for lbl, count in sorted(total_by_label.items()):
        print(f"  {lbl}: {count}")
    print("\nRun 'python3 scripts/train_mlp.py' to retrain.")


if __name__ == "__main__":
    main()
