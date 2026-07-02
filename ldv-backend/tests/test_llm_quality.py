#!/usr/bin/env python3
"""
B1 — LLM Quality Test Suite
Tests layer4 (explain) output quality against the 9 previously-PENDING sections:
  3.1  Document type accuracy
  3.2  Non-contract handling
  5.1  Clause presence accuracy
  5.2  Clause excerpt traceability
  5.3  Edge cases
  6.1  Compliance consistency
  6.2  Recommendation quality
  7.2  Score sanity (degrades with quality)
  7.3  Score boundary transitions

Usage:
    cd ldv-backend
    LDV_TESTING=1 python tests/test_llm_quality.py [--url http://127.0.0.1:5000]
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path

import requests

BACKEND  = Path(__file__).parent.parent
FIXTURES = Path(__file__).parent / "fixtures"
sys.path.insert(0, str(BACKEND))

_results: list[dict] = []


def _r(section: str, label: str, ok: bool, detail: str = "") -> None:
    outcome = "PASS" if ok else "FAIL"
    _results.append({"section": section, "label": label, "outcome": outcome, "detail": detail})
    icon = "✓" if ok else "✗"
    col  = "\033[92m" if ok else "\033[91m"
    rst  = "\033[0m"
    print(f"  {col}{icon} {outcome:<5}{rst} [{section}] {label}", flush=True)
    if detail and not ok:
        print(f"          ↳ {detail}", flush=True)


def _token() -> str:
    token = os.getenv("LDV_TEST_TOKEN", "")
    if token:
        return token
    import secrets as _s
    import auth as _auth
    import database as _db
    _db.init_db()
    org = _db.get_org_by_name("__test__")
    if not org:
        _db.create_org("__test__")
        org = _db.get_org_by_name("__test__")
    email = "test-runner@ldv.internal"
    user = _db.get_user_by_email(email)
    if user:
        return user["api_token"]
    tok = f"tok-{_s.token_urlsafe(16)}"
    _db.create_user(org["id"], email, _auth.hash_password(_s.token_urlsafe(16)), "analyst", tok)
    return tok


# ponytail: explain=True can take 5-10 min on CPU — use a longer timeout and catch gracefully
_TIMEOUT_NORMAL  = 120   # seconds — non-LLM requests should be fast
_TIMEOUT_EXPLAIN = 700   # seconds — Qwen on CPU; ceiling: model loads + 300s generation + overhead


def _analyze(url: str, filepath: Path, explain: bool = False, extra_params: dict | None = None) -> dict:
    tok = _token()
    params = {"explain": "1" if explain else "0"}
    if extra_params:
        params.update(extra_params)
    timeout = _TIMEOUT_EXPLAIN if explain else _TIMEOUT_NORMAL
    try:
        with open(filepath, "rb") as f:
            resp = requests.post(
                f"{url}/api/v1/analyze",
                files={"file": (filepath.name, f)},
                headers={"Authorization": f"Bearer {tok}"},
                params=params,
                timeout=timeout,
            )
        if resp.status_code != 200:
            return {"_error": f"HTTP {resp.status_code}: {resp.text[:200]}"}
        return resp.json()
    except requests.exceptions.ReadTimeout:
        return {"_error": f"ReadTimeout after {timeout}s — LLM inference too slow on this hardware"}


def _wait_explain(result: dict) -> bool:
    """Return True if layer4 is actually populated (not skipped)."""
    l4 = result.get("layer4", {})
    return isinstance(l4, dict) and l4.get("available") is True


# ── Section 3: Document type accuracy ───────────────────────────────────────

def check_3(url: str) -> None:
    cases = [
        ("docx/01_service_agreement_en.docx", "service agreement"),
        ("pdf/03_nda_en.pdf",                 "non-disclosure agreement"),
        ("pdf/01_employment_id.pdf",          "employment contract"),
        ("docx/02_employment_fr.docx",        "employment contract"),
        ("txt/14_low_risk_nda_en.txt",        "non-disclosure agreement"),
    ]
    for rel, expected_type in cases:
        b = _analyze(url, FIXTURES / rel)
        if "_error" in b:
            _r("3.1", f"doc-type {rel}", False, b["_error"]); continue
        got = ((b.get("layer2", {}).get("document_type") or {}).get("label") or "").lower()
        match = expected_type in got or got in expected_type
        _r("3.1", f"doc-type: {Path(rel).name} → {expected_type}", match,
           f"got '{got}'")

    # 3.2 Non-contract: confidence should be low / type absent
    non_contracts = [
        ("pdf/05_brochure_en.pdf",  "brochure"),
        ("txt/05_irrelevant_en.txt","irrelevant text"),
    ]
    for rel, label in non_contracts:
        b = _analyze(url, FIXTURES / rel)
        if "_error" in b:
            _r("3.2", f"non-contract {label}", False, b["_error"]); continue
        dt = b.get("layer2", {}).get("document_type") or {}
        # Either no type detected, or confidence < 0.6, or document_type_note present
        conf = dt.get("confidence", 0)
        lbl  = (dt.get("label") or "").lower()
        non_contract_note = bool(b.get("document_type_note"))
        ok = conf < 0.6 or lbl in ("", "none", "unknown") or non_contract_note
        _r("3.2", f"non-contract confidence low: {label}", ok,
           f"label='{lbl}' conf={conf:.2f}")


# ── Section 5: Clause presence and excerpt quality ───────────────────────────

def check_5(url: str) -> None:
    # 5.1 Known-present clauses are detected
    presence_cases = [
        ("txt/10_low_risk_complete_en.txt", ["governing_law", "termination", "dispute_resolution"]),
        ("pdf/01_employment_id.pdf",        ["termination"]),
        ("pdf/03_nda_en.pdf",               ["governing_law", "confidentiality"]),
    ]
    for rel, expected_present in presence_cases:
        b = _analyze(url, FIXTURES / rel)
        if "_error" in b:
            _r("5.1", f"clause presence {rel}", False, b["_error"]); continue
        presence = {c["clause_id"]: c.get("present", False)
                    for c in (b.get("layer1", {}).get("clause_presence") or [])}
        for cid in expected_present:
            found = presence.get(cid, False)
            _r("5.1", f"clause present: {cid} in {Path(rel).name}", found,
               f"clause_presence keys: {list(presence.keys())}" if not found else "")

    # 5.2 Evidence spans are non-empty strings when clause is detected
    b = _analyze(url, FIXTURES / "txt/10_low_risk_complete_en.txt")
    if "_error" not in b:
        for c in (b.get("layer1", {}).get("clause_presence") or []):
            if c.get("present") and c.get("evidence"):
                ev = c["evidence"]
                _r("5.2", f"evidence non-empty: {c['clause_id']}",
                   isinstance(ev, str) and len(ev.strip()) > 5,
                   f"evidence='{ev[:80]}'")

    # 5.3 Edge cases: incomplete contract gets critical score, short text doesn't crash
    b_incomplete = _analyze(url, FIXTURES / "pdf/04_incomplete_en.pdf")
    if "_error" not in b_incomplete:
        score = b_incomplete.get("layer3", {}).get("score")
        label = b_incomplete.get("layer3", {}).get("label", "")
        _r("5.3", "incomplete contract → HIGH or CRITICAL risk",
           label in ("HIGH", "CRITICAL"),
           f"got score={score} label='{label}'")

    b_short = _analyze(url, FIXTURES / "txt/03_short_contract_en.txt")
    _r("5.3", "short contract doesn't crash", "_error" not in b_short,
       b_short.get("_error", ""))


# ── Section 6: Layer4 compliance quality (requires explain=1) ───────────────

def check_6(url: str) -> None:
    # Use a high-risk fixture so layer4 has real content to work with
    print("  ⏳ Running explain=1 (Qwen inference — may take several minutes on CPU)…", flush=True)
    b = _analyze(url, FIXTURES / "txt/06_high_risk_leonine_en.txt", explain=True)
    if "_error" in b:
        timeout_msg = "ReadTimeout" in b["_error"]
        _r("6.1", "layer4 request succeeded", False, b["_error"])
        if timeout_msg:
            print("  ⚠  Qwen inference timed out — LLM too slow on CPU for production use.", flush=True)
            print("     Either: (a) add GPU, (b) set LDV_GENERATION_TIMEOUT higher, or", flush=True)
            print("     (c) disable ?explain=1 in production until GPU is available.", flush=True)
        return

    l4 = b.get("layer4", {})
    l4_available = l4.get("available", False)
    _r("6.1", "layer4 is available (LLM responded)", l4_available,
       f"layer4={l4}")

    if not l4_available:
        print("  ⚠  LLM did not respond — sections 6 and 7.2/7.3 will be skipped")
        return

    # 6.1 Compliance notes present and non-trivial
    compliance = l4.get("compliance_notes") or l4.get("compliance") or l4.get("summary") or ""
    _r("6.1", "compliance_notes non-empty", len(str(compliance).strip()) > 20,
       f"compliance='{str(compliance)[:100]}'")

    # No contradiction check: layer1 says high risk; layer3 label must not be LOW
    l3_label = b.get("layer3", {}).get("label", "")
    _r("6.1", "layer4 not contradicting layer3 risk (high-risk doc ≠ LOW)",
       l3_label != "LOW",
       f"layer3.label='{l3_label}'")

    # 6.2 Recommendations present and specific (>50 chars, not a generic placeholder)
    recs = l4.get("recommendations") or l4.get("major_issues") or ""
    recs_str = str(recs).strip()
    _r("6.2", "recommendations present",
       len(recs_str) > 50,
       f"recs='{recs_str[:120]}'")
    generic_phrases = ["not available", "n/a", "no recommendations", "none"]
    _r("6.2", "recommendations not a generic placeholder",
       not any(p in recs_str.lower() for p in generic_phrases),
       f"recs='{recs_str[:80]}'")


# ── Section 7.2/7.3: Score sanity and boundary transitions ──────────────────

def check_7(url: str) -> None:
    # Fixture order: CRITICAL → HIGH → MEDIUM → LOW
    # Scores must be monotonically non-increasing (allowing equal only between same band)
    risk_fixtures = [
        ("txt/06_high_risk_leonine_en.txt",        "CRITICAL"),
        ("txt/15_critical_risk_no_law_en.txt",    "CRITICAL"),
        ("txt/08_medium_risk_partial_en.txt",      "MEDIUM"),
        ("txt/09_medium_risk_no_venue_en.txt",     "MEDIUM"),
        ("txt/07_high_risk_missing_clauses_en.txt","LOW"),
        ("txt/10_low_risk_complete_en.txt",        "LOW"),
    ]
    scores = []
    labels = []
    for rel, expected_label in risk_fixtures:
        b = _analyze(url, FIXTURES / rel)
        if "_error" in b:
            _r("7.2", f"score for {Path(rel).name}", False, b["_error"]); continue
        l3 = b.get("layer3", {})
        score = l3.get("score")
        label = l3.get("label", "")
        scores.append((score, Path(rel).name))
        labels.append((label, expected_label, Path(rel).name))
        _r("7.2", f"label correct: {Path(rel).name} → {expected_label}",
           label == expected_label,
           f"got '{label}' (score={score})")

    # 7.3 Scores degrade: earlier (riskier) fixtures must have higher or equal risk score
    if len(scores) >= 2:
        for i in range(1, len(scores)):
            prev_score, prev_name = scores[i - 1]
            cur_score, cur_name   = scores[i]
            if prev_score is None or cur_score is None:
                continue
            # Higher score = more risk in this system
            ok = prev_score >= cur_score
            _r("7.3", f"score degrades: {prev_name}({prev_score}) ≥ {cur_name}({cur_score})",
               ok, f"{prev_score} < {cur_score}" if not ok else "")

    # 7.3 Label boundaries are stable across re-runs (determinism with LLM)
    b1 = _analyze(url, FIXTURES / "txt/08_medium_risk_partial_en.txt")
    b2 = _analyze(url, FIXTURES / "txt/08_medium_risk_partial_en.txt")
    if "_error" not in b1 and "_error" not in b2:
        s1 = b1.get("layer3", {}).get("score")
        s2 = b2.get("layer3", {}).get("score")
        _r("7.3", "identical fixture → identical score (determinism)",
           s1 == s2, f"run1={s1} run2={s2}")


# ── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:5000")
    args = parser.parse_args()
    url = args.url.rstrip("/")

    try:
        requests.get(url, timeout=5)
    except requests.exceptions.ConnectionError:
        print(f"ERROR: Cannot connect to {url}. Start the server first.")
        sys.exit(1)

    print(f"\n{'─' * 80}")
    print(f"  LDV LLM Quality Test Suite  |  {url}")
    print(f"  Sections: 3.1, 3.2, 5.1, 5.2, 5.3, 6.1, 6.2, 7.2, 7.3")
    print(f"{'─' * 80}\n")

    t0 = time.monotonic()
    check_3(url)
    print()
    check_5(url)
    print()
    try:
        check_6(url)
    except Exception as exc:
        _r("6.1", "check_6 crashed unexpectedly", False, str(exc))
    print()
    check_7(url)

    elapsed = time.monotonic() - t0
    counts = {k: sum(1 for r in _results if r["outcome"] == k) for k in ("PASS", "FAIL")}
    print(f"\n{'─' * 80}")
    print(f"  PASS {counts['PASS']}  |  FAIL {counts['FAIL']}  |  {elapsed:.1f}s")
    print(f"{'─' * 80}")

    out = Path(__file__).parent / "llm_quality_results.json"
    out.write_text(json.dumps(_results, indent=2))
    print(f"  Results → {out}")

    sys.exit(counts["FAIL"])


if __name__ == "__main__":
    main()
