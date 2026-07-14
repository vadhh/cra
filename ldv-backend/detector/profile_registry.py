"""
profile_registry.py — File-driven Contract Profile Registry (Phase 2).

Single source of truth for all CRA contract types. Replaces the hard-coded
_CONTRACT_TYPE_PROFILES dict in detector_rules.py (kept as compat layer until
parity tests pass).

Usage
-----
    from detector.profile_registry import (
        profile_registry,          # dict[str, dict]  keyed by profile.id
        required_clauses_for,      # str -> list[str]
        profile_for,               # str -> dict | None
        all_profile_ids,           # -> list[str]
        all_display_names,         # -> list[str]  (for frontend dropdown)
        detect_profile,            # str -> dict   (alias lookup result)
    )
"""
from __future__ import annotations

import json
import logging
import os
from functools import lru_cache
from typing import Optional

logger = logging.getLogger(__name__)

_REGISTRY_PATH = os.path.join(
    os.path.dirname(__file__), "profiles", "registry_v1.json"
)


@lru_cache(maxsize=1)
def _load() -> dict:
    with open(_REGISTRY_PATH, encoding="utf-8") as f:
        data = json.load(f)
    return data


def _registry() -> dict:
    """Keyed by profile id; value is the profile dict."""
    return {p["id"]: p for p in _load()["profiles"]}


# ── Public surface ─────────────────────────────────────────────────────────────

def all_profile_ids() -> list[str]:
    return list(_registry().keys())


def all_display_names() -> list[str]:
    return [p["display_name"] for p in _load()["profiles"]]


def profile_for(profile_id: str) -> Optional[dict]:
    """Return profile dict by canonical id, or None."""
    return _registry().get(profile_id)


def detect_profile(label: str) -> Optional[dict]:
    """
    Map a classifier label or alias to a profile dict.
    Returns None when no alias matches (caller should fall back to baseline).
    """
    norm = (label or "").strip().lower()
    if not norm:
        return None
    for p in _load()["profiles"]:
        if norm == p["id"] or norm in [a.lower() for a in p["aliases"]]:
            return p
    return None


def required_clauses_for(label: str) -> tuple[list[str], Optional[str]]:
    """
    Return (required_clause_ids, matched_profile_id).
    Falls back to baseline_required when label doesn't match any profile.

    ponytail: O(n×m) scan; n≈55 profiles, m≈5 aliases. Negligible for this volume.
    """
    p = detect_profile(label)
    if p:
        return p["required_clauses"], p["id"]
    baseline = _load()["baseline_required"]
    return baseline, None


def baseline_required() -> list[str]:
    return list(_load()["baseline_required"])


def registry_version() -> str:
    return _load()["registry_version"]


# ── Convenience export ─────────────────────────────────────────────────────────
# profile_registry is a live view (not cached independently; lru_cache on _load).
profile_registry = property(lambda _: _registry())
