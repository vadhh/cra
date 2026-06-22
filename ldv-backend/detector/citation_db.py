"""
citation_db.py — Runtime adapter for legal source citations.

Reads datasets/legal_citations.csv and attaches article citations to L1
findings (red flags and clauses) by their stable id.  No ML, no models — a
plain CSV parsed once into memory, mirroring clause_db.py.

Citations are *data*, never generated.  The `status` column (verified|draft)
is the trust boundary: Claude-seeded rows are `draft` until a lawyer verifies
them.  **Only `verified` citations are customer-facing** (PRD CIT-02): the
public path suppresses every non-verified row so a draft can never appear as
legal authority.  Internal reviewer paths pass `include_drafts=True` to see the
unverified seeds awaiting verification.

CSV schema
----------
    finding_id, jurisdiction, article, source, note, status

`finding_id` is a red-flag id (leonine_no_loss, excessive_penalty, …) or a
clause id (governing_law, termination, …) — one namespace, already distinct.
`jurisdiction` uses detector codes (BE/FR/ID/NL/EN&W/US/generic); `generic` is
the fallback row used when no jurisdiction-specific row exists.

Public API
----------
    from detector.citation_db import citations_for, annotate_layer1, db_available

    cites = citations_for("leonine_no_loss", "FR")   # -> list[dict]
    annotate_layer1(layer1, "Belgium")               # mutates + returns layer1
"""
from __future__ import annotations

import csv
import logging
from collections import defaultdict
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# datasets/ lives at the repo root: detector/ -> ldv-backend/ -> LDV/
_CSV_PATH = Path(__file__).resolve().parent.parent.parent / "datasets" / "legal_citations.csv"

_GENERIC = "generic"

# detect_jurisdiction() returns full names; the CSV uses short codes.
_JURIS_CODE: dict[str, str] = {
    "indonesia": "ID", "belgium": "BE", "france": "FR", "netherlands": "NL",
    "england": "EN&W", "england & wales": "EN&W", "united kingdom": "EN&W",
    "united states": "US", "usa": "US",
}

# Lazy singleton: {finding_id -> {jurisdiction -> [citation dict, ...]}}
_DB: Optional[dict[str, dict[str, list[dict]]]] = None


def _load() -> dict[str, dict[str, list[dict]]]:
    """Parse the CSV once into {finding_id: {jurisdiction: [rows]}}.  Fail soft."""
    global _DB
    if _DB is not None:
        return _DB

    db: dict[str, dict[str, list[dict]]] = defaultdict(lambda: defaultdict(list))
    if not _CSV_PATH.exists():
        logger.warning("Legal-citation DB not found at %s — citations disabled.", _CSV_PATH)
        _DB = {}
        return _DB

    try:
        with open(_CSV_PATH, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                fid = (row.get("finding_id") or "").strip()
                juris = (row.get("jurisdiction") or _GENERIC).strip() or _GENERIC
                if not fid:
                    continue
                db[fid][juris].append({
                    "article": (row.get("article") or "").strip(),
                    "source":  (row.get("source") or "").strip(),
                    "note":    (row.get("note") or "").strip(),
                    "status":  (row.get("status") or "draft").strip().lower(),
                    "jurisdiction": juris,
                })
        logger.info("Loaded legal-citation DB: %d findings from %s", len(db), _CSV_PATH.name)
    except Exception as e:  # malformed CSV must not break analysis
        logger.warning("Failed to load legal-citation DB (%s) — citations disabled.", e)
        db = {}

    # freeze the defaultdicts into plain dicts so lookups can't create entries
    _DB = {fid: dict(by_juris) for fid, by_juris in db.items()}
    return _DB


def _normalize_juris(jurisdiction: Optional[str]) -> str:
    """Map a detect_jurisdiction() name (or a code) to a CSV jurisdiction code."""
    if not jurisdiction:
        return _GENERIC
    j = jurisdiction.strip()
    return _JURIS_CODE.get(j.lower(), j)  # already-a-code passes through


# ── Public API ─────────────────────────────────────────────────────────────────

def db_available() -> bool:
    """True if the CSV was found and parsed with at least one finding."""
    return bool(_load())


def citations_for(
    finding_id: str,
    jurisdiction: Optional[str] = None,
    include_drafts: bool = False,
) -> list[dict]:
    """Citations for a finding, preferring *jurisdiction*, falling back to generic.

    Returns [] when nothing matches — never raises.  Jurisdiction-specific rows
    and generic rows are both returned (specific first), so a finding shows both
    the local article and the cross-jurisdiction rationale when both exist.

    Customer-safe by default (PRD CIT-02): only rows with status=="verified" are
    returned.  Fail closed — anything not exactly "verified" (draft, blank, a
    typo) is suppressed.  Internal reviewer paths pass include_drafts=True to see
    unverified seeds.
    """
    by_juris = _load().get(finding_id)
    if not by_juris:
        return []
    code = _normalize_juris(jurisdiction)
    out: list[dict] = []
    if code != _GENERIC:
        out.extend(by_juris.get(code, []))
    out.extend(by_juris.get(_GENERIC, []))
    if not include_drafts:
        out = [c for c in out if c.get("status") == "verified"]
    return out


def annotate_layer1(
    layer1: dict,
    jurisdiction: Optional[str] = None,
    include_drafts: bool = False,
) -> dict:
    """Attach a `citations` list to each red flag and clause in a layer1 result.

    Keyed by each finding's id: red_flags[].id and clause_presence[].clause_id.
    The `citations` key is always present (empty list when no row exists) for a
    uniform client contract.  Mutates and returns *layer1*.

    Customer-safe by default: draft citations are suppressed (PRD CIT-02).  The
    future reviewer path passes include_drafts=True for the internal view.
    """
    for flag in layer1.get("red_flags") or []:
        flag["citations"] = citations_for(flag.get("id", ""), jurisdiction, include_drafts)
    for clause in layer1.get("clause_presence") or []:
        clause["citations"] = citations_for(clause.get("clause_id", ""), jurisdiction, include_drafts)
    return layer1


def verify_against(valid_ids) -> list[str]:
    """Return CSV finding_ids that are NOT in *valid_ids* (drift guard).

    Empty == healthy.  A non-empty result means a rule/clause was renamed or
    removed and its citations now reference a dead id (they'd silently never
    attach).  Mirrors clause_db.verify_mappings().
    """
    valid = set(valid_ids)
    return sorted(fid for fid in _load() if fid not in valid)


if __name__ == "__main__":  # run from ldv-backend: python3 detector/citation_db.py
    import os
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from detector import detector_rules as _r

    assert db_available(), "CSV not found/parsed — cannot verify citations"

    valid = {f["id"] for f in _r._RED_FLAGS} | set(_r._CLAUSE_TITLES)
    drift = verify_against(valid)
    assert not drift, f"Citation drift: finding_ids with no live rule/clause: {drift}"

    # CIT-02 trust boundary: leonine_no_loss/FR is a draft seed.
    seed = citations_for("leonine_no_loss", "FR", include_drafts=True)
    assert seed and seed[0]["status"] == "draft", "expected a draft FR citation seed"
    assert citations_for("leonine_no_loss", "FR") == [], "draft must be suppressed for customers"
    assert citations_for("nonexistent_finding", "FR") == [], "unknown id must yield []"

    # default (customer) mode must never leak a non-verified citation,
    # across every finding/jurisdiction combination in the DB
    leaked = [c
              for fid, by_juris in _load().items()
              for juris in by_juris
              for c in citations_for(fid, juris)
              if c.get("status") != "verified"]
    assert not leaked, f"customer mode leaked non-verified citations: {leaked}"

    n = sum(len(c) for byj in _load().values() for c in byj.values())
    n_verified = sum(1 for byj in _load().values() for rows in byj.values()
                     for c in rows if c.get("status") == "verified")
    print(f"OK: {len(_load())} findings cited, {n} citation rows ({n_verified} verified), all ids live.")
    print(f"    draft seed leonine_no_loss/FR -> {seed[0]['article']} ({seed[0]['source']}) [suppressed for customers]")
