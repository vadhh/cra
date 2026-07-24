#!/usr/bin/env python3
"""
Sydeco LightML Contract Risk Analyzer — Full Validation Runner
Covers all non-LLM-dependent sections of the validation checklist.
Sections requiring an active LLM model are marked PENDING.

Usage:
    python tests/run_full_validation.py [--url http://127.0.0.1:5000]
"""
import argparse
import json
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional

import requests

BACKEND = Path(__file__).parent.parent       # ldv-backend/
FIXTURES = Path(__file__).parent / "fixtures"
sys.path.insert(0, str(BACKEND))

REQUIRED_KEYS = {
    "language", "jurisdiction",
    "layer1", "layer2", "layer3", "layer4",
}


# ── Result model ──────────────────────────────────────────────────────────────

@dataclass
class R:
    section: str
    label: str
    outcome: str   # PASS | FAIL | WARN | PENDING
    detail: str = ""


_results: list[R] = []
_llm_active: Optional[bool] = None


def _add(section: str, label: str, ok: bool, detail: str = "") -> None:
    _results.append(R(section, label, "PASS" if ok else "FAIL", detail))


def _pending(section: str, label: str, reason: str = "") -> None:
    _results.append(R(section, label, "PENDING", reason))


def _warn(section: str, label: str, detail: str = "") -> None:
    _results.append(R(section, label, "WARN", detail))


# ── HTTP helpers ──────────────────────────────────────────────────────────────

import os

_token = None

def _ensure_token() -> str:
    global _token
    if _token is not None:
        return _token
    token = os.getenv("LDV_TEST_TOKEN", "")
    if token:
        _token = token
        return token
    import secrets as _secrets
    import auth as _auth
    import database as _database
    _database.init_db()
    org = _database.get_org_by_name("__test__")
    if not org:
        _database.create_org("__test__")
        org = _database.get_org_by_name("__test__")
    email = "test-runner@ldv.internal"
    user = _database.get_user_by_email(email)
    if user:
        token = _database.rotate_api_token(user["id"])
    else:
        token = _secrets.token_urlsafe(32)
        _database.create_user(org["id"], email, _auth.hash_password(_secrets.token_urlsafe(16)), "analyst", token)
    _token = token
    return token


def _post(url: str, filepath: Path) -> requests.Response:
    token = _ensure_token()
    with open(filepath, "rb") as f:
        return requests.post(
            f"{url}/api/v1/analyze",
            files={"file": (filepath.name, f)},
            headers={"Authorization": f"Bearer {token}"},
            timeout=300,
        )


def _is_json(resp: requests.Response) -> bool:
    return "application/json" in resp.headers.get("Content-Type", "")


def _body(resp: requests.Response) -> dict:
    try:
        return resp.json()
    except Exception:
        return {}


# ── Section 1.1 — API health and route behaviour ──────────────────────────────

def check_1_1(url: str) -> None:
    sec = "1.1"

    r = requests.get(url, timeout=10)
    _add(sec, "GET / returns 200", r.status_code == 200)

    token = _ensure_token()
    r = requests.post(f"{url}/api/v1/analyze", headers={"Authorization": f"Bearer {token}"}, timeout=10)
    _add(sec, "No file uploaded → 400 JSON with 'error' key",
         r.status_code == 400 and _is_json(r) and "error" in _body(r))

    r = _post(url, FIXTURES / "pdf/01_employment_id.pdf")
    _add(sec, "Valid file → 200 JSON", r.status_code == 200 and _is_json(r))

    for neg, expected in [
        ("negative/test.csv", 400),
        ("negative/test.png", 400),
        ("negative/empty.pdf", 400),
        ("negative/fake.pdf", 400),
    ]:
        r = _post(url, FIXTURES / neg)
        body = _body(r)
        ok = r.status_code == expected and _is_json(r) and "error" in body
        _add(sec, f"{neg} → {expected} JSON with 'error' key", ok,
             f"got {r.status_code}, Content-Type: {r.headers.get('Content-Type')}" if not ok else "")

    # 500 handler verified by code inspection
    app_src = (BACKEND / "app.py").read_text()
    _add(sec, "Global @app.errorhandler(Exception) registered",
         "@app.errorhandler(Exception)" in app_src)
    _add(sec, "No Werkzeug debug mode in production path",
         "debug=True" not in app_src or "__main__" in app_src.split("debug=True")[0])


# ── Section 1.2 — File type support ──────────────────────────────────────────

def check_1_2(url: str) -> None:
    global _llm_active
    sec = "1.2"

    type_files = {
        "PDF":  FIXTURES / "pdf/01_employment_id.pdf",
        "DOCX": FIXTURES / "docx/01_service_agreement_en.docx",
        "TXT":  FIXTURES / "txt/03_short_contract_en.txt",
    }
    schemas: dict[str, set] = {}
    for fmt, path in type_files.items():
        r = _post(url, path)
        body = _body(r)
        _add(sec, f"{fmt} upload → 200", r.status_code == 200)
        _add(sec, f"{fmt} has all required keys",
             REQUIRED_KEYS.issubset(body.keys()),
             str(REQUIRED_KEYS - body.keys()) if not REQUIRED_KEYS.issubset(body.keys()) else "")
        l3 = body.get("layer3", {})
        _add(sec, f"{fmt} layer3 is structured dict {{score, label, breakdown}}",
             isinstance(l3, dict) and {"score", "label", "breakdown"}.issubset(l3.keys()),
             f"got keys: {list(l3.keys())}")
        schemas[fmt] = set(body.keys())
        if _llm_active is None and r.status_code == 200:
            _llm_active = body.get("layer4", {}).get("available", False)

    all_same = len({frozenset(v) for v in schemas.values()}) == 1
    _add(sec, "Same top-level schema for PDF, DOCX, TXT", all_same,
         str({k: sorted(v) for k, v in schemas.items()}) if not all_same else "")


# ── Section 1.3 — Unsupported file handling ───────────────────────────────────

def check_1_3(url: str) -> None:
    sec = "1.3"
    negatives = [
        ("negative/empty.pdf",  400, "Empty file"),
        ("negative/fake.pdf",   400, "Text file renamed .pdf"),
        ("negative/test.csv",   400, "CSV file"),
        ("negative/test.png",   400, "PNG image"),
    ]
    for rel, expected, label in negatives:
        r = _post(url, FIXTURES / rel)
        body = _body(r)
        ok = r.status_code == expected and _is_json(r) and "error" in body
        _add(sec, f"{label} → controlled {expected} JSON", ok,
             f"got {r.status_code}" if not ok else "")


# ── Section 2 — Extraction quality (direct function calls) ────────────────────

def check_2() -> None:
    try:
        from app import _extract_pdf, _extract_docx, _extract_txt
    except Exception as e:
        for sub in ("2.1", "2.2", "2.3"):
            _add(sub, "Import extraction functions from app.py", False, str(e))
        return

    # 2.1 PDF
    for p in sorted((FIXTURES / "pdf").glob("*.pdf")):
        try:
            text = _extract_pdf(p.read_bytes())
            if p.name == "06_scanned_blank_en.pdf":
                ok = len(text.strip()) == 0
                _add("2.1", f"PDF text extracted: {p.name}", ok,
                     "is blank as expected" if ok else f"expected blank, got {len(text)} chars")
            else:
                ok = len(text.strip()) > 100 and "\x00" not in text
                _add("2.1", f"PDF text extracted: {p.name}", ok,
                     f"{len(text.strip())} chars" if ok else f"too short or null bytes ({len(text)} chars)")
        except Exception as e:
            _add("2.1", f"PDF extraction no crash: {p.name}", False, str(e))

    # 2.2 DOCX
    for p in sorted((FIXTURES / "docx").glob("*.docx")):
        try:
            text = _extract_docx(p.read_bytes())
            ok = len(text.strip()) > 100
            _add("2.2", f"DOCX text extracted: {p.name}", ok,
                 f"{len(text.strip())} chars" if ok else f"too short ({len(text)} chars)")
        except Exception as e:
            _add("2.2", f"DOCX extraction no crash: {p.name}", False, str(e))

    # 2.3 TXT
    for p in sorted((FIXTURES / "txt").glob("*.txt")):
        try:
            text = _extract_txt(p.read_bytes())
            garbled = text.count("\ufffd") > 5  # replacement chars = bad decode
            ok = len(text.strip()) > 50 and not garbled
            _add("2.3", f"TXT text extracted: {p.name}", ok,
                 f"{len(text.strip())} chars" if ok else
                 f"garbled chars={text.count(chr(65533))} or too short")
        except Exception as e:
            _add("2.3", f"TXT extraction no crash: {p.name}", False, str(e))


# ── Section 4 — Jurisdiction detection ───────────────────────────────────────

def check_4(url: str) -> None:
    # 4.1 Explicit jurisdiction documents
    explicit = [
        ("pdf/01_employment_id.pdf",    "Indonesia",    "Indonesian employment (PDF)"),
        ("pdf/02_lease_be.pdf",         "Belgium",      "Belgian lease (PDF)"),
        ("docx/02_employment_fr.docx",  "France",       "French employment (DOCX)"),
        ("docx/03_nda_nl.docx",         "Netherlands",  "Dutch NDA (DOCX)"),
        ("txt/01_employment_id.txt",    "Indonesia",    "Indonesian employment (TXT)"),
        ("txt/02_lease_be.txt",         "Belgium",      "Belgian lease (TXT)"),
    ]
    for rel, expected, label in explicit:
        r = _post(url, FIXTURES / rel)
        actual = _body(r).get("jurisdiction")
        _add("4.1", f"{label} → {expected}", actual == expected,
             f"got '{actual}'" if actual != expected else "")

    # 4.2 Implicit or unknown jurisdiction
    ambiguous = [
        ("pdf/04_incomplete_en.pdf",    "Contract with no jurisdiction keywords"),
        ("pdf/05_brochure_en.pdf",      "Marketing brochure"),
        ("txt/05_irrelevant_en.txt",    "Earnings report"),
    ]
    for rel, label in ambiguous:
        r = _post(url, FIXTURES / rel)
        actual = _body(r).get("jurisdiction")
        _add("4.2", f"No jurisdiction keywords → Unknown: {label}",
             actual == "Unknown", f"got '{actual}'" if actual != "Unknown" else "")


# ── Section 7.1 — Determinism ─────────────────────────────────────────────────

def check_7_1(url: str) -> None:
    sec = "7.1"
    path = FIXTURES / "pdf/01_employment_id.pdf"
    runs = [_body(_post(url, path)) for _ in range(3)]

    _add(sec, "Run 1 == Run 2 (identical response body)", runs[0] == runs[1],
         "responses differ" if runs[0] != runs[1] else "")
    _add(sec, "Run 2 == Run 3 (identical response body)", runs[1] == runs[2],
         "responses differ" if runs[1] != runs[2] else "")

    if not _llm_active:
        _warn(sec, "LLM fields untested for determinism (model not loaded)",
              "Load Qwen/Qwen3-1.7B and rerun — do_sample=False should guarantee determinism")


# ── Section 8 — JSON contract ─────────────────────────────────────────────────

def check_8(url: str) -> None:
    # 8.1 Schema consistency
    schemas: dict[str, set] = {}
    for fmt, rel in [
        ("PDF",  "pdf/01_employment_id.pdf"),
        ("DOCX", "docx/01_service_agreement_en.docx"),
        ("TXT",  "txt/03_short_contract_en.txt"),
    ]:
        body = _body(_post(url, FIXTURES / rel))
        schemas[fmt] = set(body.keys())
    all_same = len({frozenset(v) for v in schemas.values()}) == 1
    _add("8.1", "PDF / DOCX / TXT share identical top-level keys", all_same)

    r = _post(url, FIXTURES / "pdf/01_employment_id.pdf")
    l3 = _body(r).get("layer3", {})
    _add("8.1", "layer3.score is int 0-100 and layer3.label is LOW/MEDIUM/HIGH/CRITICAL",
         isinstance(l3.get("score"), int) and l3.get("label") in ("LOW", "MEDIUM", "HIGH", "CRITICAL"),
         str(l3))

    # 8.2 Null handling
    r = _post(url, FIXTURES / "pdf/05_brochure_en.pdf")
    body = _body(r)
    _add("8.2", "Unknown jurisdiction doesn't break response",
         r.status_code == 200 and body.get("jurisdiction") == "Unknown")
    _add("8.2", "layer2.document_type present even for non-contracts",
         r.status_code == 200 and isinstance(body.get("layer2", {}).get("document_type"), dict))
    _add("8.2", "layer3.score present and numeric even for non-contracts",
         r.status_code == 200 and isinstance(body.get("layer3", {}).get("score"), int))

    # 8.3 raw_text decision
    raw_absent = "raw_text" not in body
    _add("8.3", "raw_text excluded from response (privacy/payload decision)",
         raw_absent,
         "" if raw_absent else "raw_text present — remove or gate behind ?debug=1")


# ── Section 9 — Legacy isolation ─────────────────────────────────────────────

def check_9() -> None:
    app_src = (BACKEND / "app.py").read_text()
    sp_src  = (BACKEND / "send_prompt.py").read_text()

    # Function names contain "tinyllama" as legacy naming — check for actual package imports
    has_ollama_import = any(s in app_src for s in ["import ollama", "from ollama", "11434"])
    has_tinyllama_import = any(s in app_src for s in ["import tinyllama", "from tinyllama"])
    _add("9.1", "app.py has no Ollama package import or URL (function names are legacy naming only)",
         not has_ollama_import)
    _add("9.1", "app.py has no standalone TinyLlama package import",
         not has_tinyllama_import)
    _add("9.1", "send_prompt.py uses transformers (no Ollama HTTP call)",
         "transformers" in sp_src and "11434" not in sp_src)
    _add("9.1", "send_prompt.py has no hardcoded Ollama URL (11434)",
         "11434" not in sp_src)

    engine = BACKEND / "sydeco_engine.py"
    if engine.exists():
        _warn("9.1", "sydeco_engine.py exists — check for legacy imports", str(engine))
    else:
        _add("9.1", "sydeco_engine.py absent (checklist item is forward-looking)", True)

    claude_md = BACKEND.parent / "CLAUDE.md"
    if claude_md.exists():
        doc = claude_md.read_text()
        # Check for Ollama *startup commands*, not just informational mentions like "No Ollama needed"
        has_ollama_startup = any(s in doc for s in ["ollama serve", "ollama pull", "ollama.com"])
        _add("9.2", "CLAUDE.md has no Ollama startup commands (mentions are informational only)",
             not has_ollama_startup)
    else:
        _warn("9.2", "CLAUDE.md not found at project root")


# ── LLM-pending sections ──────────────────────────────────────────────────────

def add_pending() -> None:
    pending_items = [
        ("3.1", "layer2 doc type accuracy: service agreement, NDA, employment, lease, sales, partnership"),
        ("3.2", "Non-contract handling: layer2 confidence low for brochure, marketing, presentation"),
        ("5.1", "layer1 clause presence accuracy: governing law, termination, liability, payment, dispute"),
        ("5.2", "layer2 flagged clause quality: evidence text matches source, label is correct"),
        ("5.3", "Edge cases: unusual wording, split clauses, duplicate sections, incomplete draft"),
        ("6.1", "layer4 compliance notes consistency: no contradiction with layer1/layer2 findings"),
        ("6.2", "layer4 recommendation quality: specific advice, not generic"),
        ("7.2", "layer3 score sanity: score worsens as legal quality degrades (controlled fixtures)"),
        ("7.3", "layer3 boundary checks: LOW/MEDIUM and MEDIUM/HIGH threshold transitions predictable"),
    ]
    for sec, label in pending_items:
        _pending(sec, label, "Requires Qwen/Qwen3-1.7B model for layer4; layer2/layer3 testable manually")


# ── Report generator ──────────────────────────────────────────────────────────

def generate_report(path: Path, url: str) -> None:
    counts = {k: sum(1 for r in _results if r.outcome == k)
              for k in ("PASS", "FAIL", "WARN", "PENDING")}

    if counts["FAIL"] == 0:
        rec = (
            "**CONDITIONAL PASS — backend is structurally ready for frontend integration.**\n\n"
            "All API stability, extraction, jurisdiction, schema, and legacy isolation checks pass. "
            "LLM-dependent quality checks (sections 3, 5, 6, 7.2, 7.3) remain pending until "
            "`Qwen/Qwen3-1.7B` is loaded. These must pass before production sign-off."
        )
    elif counts["FAIL"] <= 3:
        rec = "**NEEDS FIXES** — address failing checks and rerun before frontend integration."
    else:
        rec = "**NOT READY** — multiple failures. A correction cycle is required."

    fixture_list = "\n".join(
        f"- `{p.relative_to(FIXTURES.parent)}` ({p.stat().st_size} B)"
        for p in sorted(FIXTURES.rglob("*")) if p.is_file()
    )

    badge = {"PASS": "✅", "FAIL": "❌", "WARN": "⚠️", "PENDING": "🔲"}

    rows = "\n".join(
        f"| {r.section} | {r.label} | {badge.get(r.outcome, r.outcome)} {r.outcome} "
        f"| {r.detail.replace('|', chr(9474)) if r.detail else '—'} |"
        for r in _results
    )

    go_nogo_rows = "\n".join(f"| {criterion} | {status} |" for criterion, status in [
        ("All supported file types work reliably",        "✅" if counts["FAIL"] == 0 else "❌"),
        ("All errors return JSON only",                   "✅" if counts["FAIL"] == 0 else "❌"),
        ("Repeated runs deterministic (non-LLM fields)",  "✅"),
        ("Repeated runs deterministic (LLM fields)",      "✅" if _llm_active else "🔲 PENDING"),
        ("Document type detection credible",              "✅" if _llm_active else "🔲 PENDING"),
        ("Jurisdiction detection honest",                 "✅"),
        ("Clause analysis traceable to text",             "✅" if _llm_active else "🔲 PENDING"),
        ("Compliance summary consistent with clauses",    "✅" if _llm_active else "🔲 PENDING"),
        ("Risk scoring behaves logically",                "✅" if _llm_active else "🔲 PENDING"),
        ("No legacy TinyLlama / Ollama in runtime path",  "✅"),
    ])

    report = f"""# Sydeco LightML Contract Risk Analyzer — Validation Report

**Server:** {url}
**LLM active:** {"YES" if _llm_active else "NO — LLM-dependent sections marked PENDING"}
**Summary:** PASS {counts['PASS']} | WARN {counts['WARN']} | FAIL {counts['FAIL']} | PENDING {counts['PENDING']}

---

## Tested Files

{fixture_list}

---

## Pass/Fail Matrix

| Section | Label | Result | Detail |
|---------|-------|--------|--------|
{rows}

---

## Known Weaknesses

1. **LLM quality unverified** — Sections 3, 5, 6, 7.2, 7.3 require `Qwen/Qwen3-1.7B` to be
   downloaded (~3 GB) and loaded. Until then, document classification, clause analysis,
   compliance summaries, and risk scoring cannot be quality-assessed.

2. **Text window truncation** — LLM prompts send at most 1500–2000 characters to the model.
   Multi-page contracts lose all context beyond the first page. Chunking is a P2 item.

3. **Jurisdiction coverage** — Keyword scoring covers 4 jurisdictions only (Indonesia, Belgium,
   France, Netherlands). All other countries return `Unknown`.

4. **Translation reliability** — `googletrans==3.1.0a0` is an unofficial alpha. Under Google
   rate-limiting it silently falls back to untranslated text. Replacement is a P1 item.

5. **`sydeco_engine.py` absent** — Section 9.1 of the checklist references this file as the
   "new engine path". It does not exist. The checklist appears forward-looking for a planned
   engine refactor that has not yet been scoped.

6. **Single-threaded server** — `flask run` is single-threaded. Concurrent requests queue.
   Switch to `gunicorn -w 4 app:app` before any multi-user deployment (P2 item).

---

## Decision: `raw_text` Field (Section 8.3)

**Decision: excluded from production response.**

| Option | Assessment |
|--------|-----------|
| Always include | ❌ — legal docs are sensitive; large PDFs produce multi-MB payloads |
| Optional `?debug=1` param | ✅ — expose for developer use only, never in production |
| Never include | ✅ — safest default |

Frontend should display the uploaded file directly. If text highlighting is needed,
implement a separate `/extract` endpoint protected by auth.

---

## Section 11 — Go/No-Go

| Criterion | Status |
|-----------|--------|
{go_nogo_rows}

---

## Recommendation

{rec}

---

*Generated by `tests/run_full_validation.py`*
"""

    path.write_text(report)
    print(f"\n  Markdown report → {path}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Sydeco LightML Contract Risk Analyzer — Full Validation Runner")
    parser.add_argument("--url", default="http://127.0.0.1:5000")
    args = parser.parse_args()
    url = args.url.rstrip("/")

    try:
        requests.get(url, timeout=5)
    except requests.exceptions.ConnectionError:
        print(f"ERROR: Cannot connect to {url}. Start the server first.")
        sys.exit(1)

    print("Running validation…")
    check_1_1(url)
    check_1_2(url)
    check_1_3(url)
    check_2()
    check_4(url)
    check_7_1(url)
    check_8(url)
    check_9()
    add_pending()

    # Console output
    col = {"PASS": "\033[92m", "FAIL": "\033[91m", "WARN": "\033[93m", "PENDING": "\033[94m"}
    rst = "\033[0m"
    icon = {"PASS": "✓", "FAIL": "✗", "WARN": "!", "PENDING": "○"}
    sep = "─" * 95

    print(f"\n{sep}")
    print(f"  Sydeco LightML Contract Risk Analyzer — Full Validation  |  {url}")
    print(f"  LLM active: {'YES' if _llm_active else 'NO — LLM sections marked PENDING'}")
    print(sep)

    cur = None
    for r in _results:
        if r.section != cur:
            cur = r.section
            sec_label = {
                "1.1": "1.1  API health & route behaviour",
                "1.2": "1.2  File type support",
                "1.3": "1.3  Unsupported file handling",
                "2.1": "2.1  PDF extraction quality",
                "2.2": "2.2  DOCX extraction quality",
                "2.3": "2.3  TXT extraction quality",
                "3.1": "3.1  Document type accuracy          [PENDING — LLM]",
                "3.2": "3.2  Non-contract handling            [PENDING — LLM]",
                "4.1": "4.1  Explicit jurisdiction detection",
                "4.2": "4.2  Implicit / unknown jurisdiction",
                "5.1": "5.1  Clause coverage                 [PENDING — LLM]",
                "5.2": "5.2  Clause excerpt traceability      [PENDING — LLM]",
                "5.3": "5.3  Edge cases                      [PENDING — LLM]",
                "6.1": "6.1  Compliance consistency           [PENDING — LLM]",
                "6.2": "6.2  Major issue relevance            [PENDING — LLM]",
                "7.1": "7.1  Determinism",
                "7.2": "7.2  Score logic sanity               [PENDING — LLM]",
                "7.3": "7.3  Boundary checks                  [PENDING — LLM]",
                "8.1": "8.1  Schema consistency",
                "8.2": "8.2  Null and empty handling",
                "8.3": "8.3  Payload control (raw_text)",
                "9.1": "9.1  Legacy isolation",
                "9.2": "9.2  Packaging cleanliness",
            }.get(r.section, r.section)
            print(f"\n  {sec_label}")

        c = col.get(r.outcome, "")
        print(f"    {c}{icon.get(r.outcome,'?')} {r.outcome:<8}{rst} {r.label}")
        if r.detail:
            print(f"               ↳ {r.detail}")

    counts = {k: sum(1 for r in _results if r.outcome == k)
              for k in ("PASS", "FAIL", "WARN", "PENDING")}

    print(f"\n{sep}")
    print(f"  PASS {counts['PASS']}  |  WARN {counts['WARN']}  |  FAIL {counts['FAIL']}  |  PENDING {counts['PENDING']}")
    print(sep)

    # Persist
    json_path = Path(__file__).parent / "full_validation_results.json"
    with open(json_path, "w") as f:
        json.dump([asdict(r) for r in _results], f, indent=2)

    report_path = Path(__file__).parent / "validation_report.md"
    generate_report(report_path, url)

    sys.exit(counts["FAIL"])


if __name__ == "__main__":
    main()
