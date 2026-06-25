"""
Bootstrap-train a risk scorer MLP from test fixtures.

The deterministic L3 scorer provides weak labels; once expert-labeled data
(CSV with feature vectors + true risk scores) is available, pass it via
--csv to replace the bootstrap labels.

Usage:
    cd ldv-backend
    python3 tests/create_fixtures.py          # generate fixtures first
    python3 scripts/train_risk_scorer.py
    python3 scripts/train_risk_scorer.py --csv path/to/labeled.csv

Output: data/risk_scorer.pkl

Activate in scoring: set LDV_USE_MLP_SCORER=1
Feature vector schema (7 numeric features):
    missing_required, high_flags, medium_flags, unique_l2,
    has_governing_law, has_venue, l2_available

CSV format (expert labels):
    missing_required,high_flags,medium_flags,unique_l2,has_governing_law,has_venue,l2_available,risk_score
"""
from __future__ import annotations

import csv
import os
import pickle
import sys
from pathlib import Path

import numpy as np
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, str(Path(__file__).parent.parent))

_FEATURE_COLS = [
    "missing_required", "high_flags", "medium_flags", "unique_l2",
    "has_governing_law", "has_venue", "l2_available",
]


def _features_from_layer3(layer3_features: dict) -> list[float]:
    return [
        float(layer3_features.get("missing_required", 0)),
        float(layer3_features.get("high_flags", 0)),
        float(layer3_features.get("medium_flags", 0)),
        float(layer3_features.get("unique_l2", 0)),
        float(layer3_features.get("has_governing_law", False)),
        float(layer3_features.get("has_venue", False)),
        float(layer3_features.get("l2_available", False)),
    ]


def _bootstrap_from_fixtures(fixtures_dir: Path) -> tuple[list, list]:
    """Run L1+L3 on text fixtures to generate (feature_vector, weak_label) pairs."""
    from detector.detector_rules import layer1_analyze
    from detector.detector_scorer import layer3_score

    X: list[list[float]] = []
    y: list[float] = []
    txt_files = list(fixtures_dir.glob("**/*.txt"))
    if not txt_files:
        print(f"No .txt fixtures in {fixtures_dir} — run tests/create_fixtures.py first")
        return X, y

    for path in txt_files:
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
            l1   = layer1_analyze(text)
            l3   = layer3_score(l1, layer2=None)
            X.append(_features_from_layer3(l3["features"]))
            y.append(float(l3["score"]))
        except Exception as e:
            print(f"  skip {path.name}: {e}")

    print(f"Bootstrap: {len(X)} fixture samples")
    return X, y


def _load_csv(csv_path: Path) -> tuple[list, list]:
    X: list[list[float]] = []
    y: list[float] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            try:
                X.append([float(row[c]) for c in _FEATURE_COLS])
                y.append(float(row["risk_score"]))
            except (KeyError, ValueError):
                continue
    print(f"CSV: {len(X)} labeled samples from {csv_path}")
    return X, y


def train(save_path: Path, csv_path: Path | None, fixtures_dir: Path) -> None:
    X, y = _bootstrap_from_fixtures(fixtures_dir)

    if csv_path and csv_path.exists():
        Xc, yc = _load_csv(csv_path)
        X.extend(Xc)
        y.extend(yc)

    if len(X) < 4:
        print("Too few samples — need at least 4. Check fixtures or supply --csv.")
        sys.exit(1)

    Xa = np.array(X, dtype=float)
    ya = np.array(y, dtype=float)
    X_train, X_test, y_train, y_test = train_test_split(Xa, ya, test_size=0.2, random_state=42)

    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        # ponytail: lbfgs converges reliably on small datasets; switch to adam when n>1000
        ("mlp", MLPRegressor(hidden_layer_sizes=(32, 16), solver="lbfgs", max_iter=2000, random_state=42)),
    ])
    pipeline.fit(X_train, y_train)

    mae_train = mean_absolute_error(y_train, pipeline.predict(X_train))
    mae_test  = mean_absolute_error(y_test,  pipeline.predict(X_test))
    print(f"MAE  train={mae_train:.1f}  test={mae_test:.1f}  (risk score 0-100)")
    print("Note: bootstrap labels = deterministic scorer output; MAE improves only with expert labels.")

    save_path.parent.mkdir(parents=True, exist_ok=True)
    with open(save_path, "wb") as f:
        pickle.dump(pipeline, f)
    print(f"Saved → {save_path}")
    print(f"Activate with: LDV_USE_MLP_SCORER=1")


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv",      type=Path, default=None)
    ap.add_argument("--fixtures", type=Path, default=None)
    ap.add_argument("--out",      type=Path, default=None)
    args = ap.parse_args()

    base     = Path(__file__).parent.parent
    fixtures = args.fixtures or base / "tests" / "fixtures"
    out_path = args.out or Path(os.getenv("LDV_RISK_SCORER_PATH", str(base / "data" / "risk_scorer.pkl")))
    train(out_path, args.csv, fixtures)
