"""
risk_clause_db.py — Keyword-based risky-clause detector (Phase 1 of CSV adoption).

Loads the lawyer-authored category datasets — abusive / dangerous / illegal /
leonine_clauses.csv — and flags risky clauses by keyword phrase.  No ML; a plain
CSV pass, sibling to clause_db.py.  This widens L1 red-flag coverage from the
13 hand-written regex rules in detector_rules._RED_FLAGS to several hundred
multilingual (EN/FR/ID) phrases, each carrying a lawyer-set Impact_Level.

CSV schema (10 logical cols; `dangerous` has a header row, the others don't):
    ID, Category, Clause_Name, Language, Keywords, Risk_Score, Impact_Level,
    Reason, Recommendation, Business_Impact
Trailing Business_Impact occasionally has unquoted commas — we read by position
and only need cols 1..8, so the overflow is ignored.

Public API:
    detect_keyword_flags(text, exclude_ids=()) -> list[dict]   # red-flag shaped
    db_available() -> bool
"""
from __future__ import annotations

import csv
import logging
import re
from pathlib import Path
from typing import Iterable, Optional

logger = logging.getLogger(__name__)

# datasets/ at repo root: detector/ -> ldv-backend/ -> LDV/
_DIR = Path(__file__).resolve().parent.parent.parent / "datasets"
_FILES = ["abusive_clauses.csv", "dangerous_clauses.csv",
          "illegal_clauses.csv", "leonine_clauses.csv"]

# Impact_Level -> red-flag severity used by _layer1_score (HIGH/MEDIUM counted).
_SEVERITY = {"critical": "HIGH", "high": "HIGH", "medium": "MEDIUM", "low": "LOW"}

# ponytail: minimal overlap map. A keyword finding is suppressed when the
# regex rule covering the same concept already fired (passed via exclude_ids),
# so we don't double-count. Extend if new regex rules overlap new categories.
_REGEX_OVERLAP = {
    "unilateral change": "unilateral_modification",
    "one-sided penalty": "excessive_penalty",
    "unlimited liability": "total_liability_exclusion",
}

# Lazy singleton: {clause_name: entry} (best risk_score kept, phrases unioned)
_DB: Optional[dict[str, dict]] = None


def _slug(name: str) -> str:
    return "kw_" + re.sub(r"[^a-z0-9]+", "_", name.strip().lower()).strip("_")


def _to_int(v) -> int:
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return 0


def _load() -> dict[str, dict]:
    """Parse the 4 category CSVs into {clause_name: entry}.  Fail soft.

    Keeps the highest-risk_score row per clause_name and unions keyword phrases
    across languages (EN/FR/ID terms are distinct, so a union only adds reach).
    """
    global _DB
    if _DB is not None:
        return _DB

    db: dict[str, dict] = {}
    for fname in _FILES:
        path = _DIR / fname
        if not path.exists():
            logger.warning("Risk-clause DB missing %s — skipped.", fname)
            continue
        try:
            with open(path, newline="", encoding="utf-8") as f:
                for row in csv.reader(f):
                    if len(row) < 9 or not row[0].strip().isdigit():
                        continue  # header row or malformed
                    category, clause_name = row[1].strip(), row[2].strip()
                    phrases = [k.strip().lower() for k in row[4].split(",") if k.strip()]
                    risk, impact, recommend = _to_int(row[5]), row[6].strip(), row[8].strip()
                    if not clause_name or not phrases:
                        continue
                    e = db.get(clause_name)
                    if e is None:
                        db[clause_name] = {
                            "id": _slug(clause_name), "clause_name": clause_name,
                            "category": category, "risk_score": risk,
                            "impact_level": impact, "recommendation": recommend,
                            "phrases": list(dict.fromkeys(phrases)),
                        }
                    else:
                        for p in phrases:
                            if p not in e["phrases"]:
                                e["phrases"].append(p)
                        if risk > e["risk_score"]:
                            e.update(risk_score=risk, impact_level=impact,
                                     recommendation=recommend, category=category)
        except Exception as ex:  # malformed CSV must not break analysis
            logger.warning("Failed to load %s (%s) — skipped.", fname, ex)

    logger.info("Loaded risk-clause DB: %d distinct risky clauses.", len(db))
    _DB = db
    return _DB


def db_available() -> bool:
    return bool(_load())


_SPECIFIC_WORDS = 3   # a single phrase this long (in words) can flag alone
_MIN_CORROBORATION = 2  # otherwise need this many distinct phrase hits


def _find(low: str, phrase: str) -> tuple[int, int] | None:
    """Word-boundary-aware search; returns (start, end) or None."""
    m = re.search(r"(?<!\w)" + re.escape(phrase) + r"(?!\w)", low)
    return (m.start(), m.end()) if m else None


def detect_keyword_flags(text: str, exclude_ids: Iterable[str] = ()) -> list[dict]:
    """Return red-flag-shaped findings for risky clauses matched by keyword.

    Precision over recall: the category CSV keyword lists include ~800 generic
    single words (e.g. "arbitration", "payment") meant as human indicators, not
    standalone triggers.  Matching a clause therefore requires *corroboration* —
    either one highly-specific phrase (>= _SPECIFIC_WORDS words) or at least
    _MIN_CORROBORATION distinct phrase hits.  1-word phrases never flag alone.
    Word-boundary matching avoids partial-word hits.  Findings whose concept a
    regex rule already fired (exclude_ids) are suppressed via _REGEX_OVERLAP.
    """
    low = text.lower()
    excluded = set(exclude_ids)
    out: list[dict] = []
    for entry in _load().values():
        overlap = _REGEX_OVERLAP.get(entry["clause_name"].lower())
        if overlap and overlap in excluded:
            continue
        matched = []  # (start, end, nwords) for each 2+-word phrase that hit
        for phrase in entry["phrases"]:
            nwords = len(phrase.split())
            if nwords < 2:
                continue  # generic single words never trigger alone
            res = _find(low, phrase)
            if res is not None:
                matched.append((res[0], res[1], nwords))
        has_specific = any(m[2] >= _SPECIFIC_WORDS for m in matched)
        if not (has_specific or len(matched) >= _MIN_CORROBORATION):
            continue
        # snippet from the most specific hit (longest phrase), else first
        anchor = max(matched, key=lambda m: m[2])
        match_start, match_end, _ = anchor
        start = max(0, match_start - 50)
        end = min(len(text), match_end + 60)
        out.append({
            "id":           entry["id"],
            "type":         entry["category"].lower(),
            "severity":     _SEVERITY.get(entry["impact_level"].lower(), "MEDIUM"),
            "description":  f"{entry['category']}: {entry['clause_name']}",
            "evidence":     text[start:end].strip().replace("\n", " "),
            "evidence_span": [match_start, match_end],
            "impact_level": entry["impact_level"],
            "recommendation": entry["recommendation"],
            "source":       "keyword_db",
        })
    return out


if __name__ == "__main__":  # python3 detector/risk_clause_db.py — load + match check
    assert db_available(), "no category CSVs loaded"
    db = _load()
    print(f"OK: {len(db)} distinct risky clauses, "
          f"{sum(len(e['phrases']) for e in db.values())} keyword phrases.")
    text = "The provider accepts unlimited liability for all losses without limit."
    sample = detect_keyword_flags(text)
    assert any(f["type"] == "dangerous" for f in sample), "expected an Unlimited Liability hit"
    f = next(x for x in sample if "liability" in x["description"].lower())
    assert "evidence_span" in f, "evidence_span missing in finding"
    span = f["evidence_span"]
    assert text[span[0]:span[1]].lower() == "unlimited liability", f"span mismatch: {text[span[0]:span[1]]}"
    print(f"    sample hit -> {f['description']} [{f['severity']}] span={span} src={f['source']}")
    suppressed = detect_keyword_flags("unlimited liability",
                                      exclude_ids=["total_liability_exclusion"])
    assert all(x["id"] != "kw_unlimited_liability" for x in suppressed), \
        "overlap suppression failed"
    print("    overlap suppression OK")
