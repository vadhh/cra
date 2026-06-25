"""
Sydeco LightML Contract Risk Analyzer — Backend Validation Runner
Usage: python tests/run_validation.py [--url http://127.0.0.1:5000] [--token <api_token>]

Expects the Flask server to already be running.
If --token is omitted, checks LDV_TEST_TOKEN env var, then auto-provisions a
test user directly in the DB (requires running from ldv-backend/).
"""
import argparse
import json
import os
import sys
from pathlib import Path

import requests

FIXTURES = Path(__file__).parent / "fixtures"

# ── Test definitions ──────────────────────────────────────────────────────────
# Each entry:
#   file          relative path under fixtures/
#   label         human description
#   expected_status  HTTP status code
#   assert_json   key/value pairs that must match in the response body (exact)
#   not_null      response keys that must not be null (skipped if LLM unavailable)
#   llm_dependent True if assertions rely on LLM output (treated as WARN not FAIL when null)

TESTS = [
    # ── Valid PDFs ────────────────────────────────────────────────────────────
    {
        "file": "pdf/01_employment_id.pdf",
        "label": "Indonesian employment contract (PDF)",
        "expected_status": 200,
        "assert_json": {"jurisdiction": "Indonesia", "language": "id"},
        "not_null": ["document_type", "clause_by_clause", "legal_compliance"],
        "llm_dependent": True,
    },
    {
        "file": "pdf/02_lease_be.pdf",
        "label": "Belgian lease agreement (PDF)",
        "expected_status": 200,
        "assert_json": {"jurisdiction": "Belgium"},
        "not_null": ["document_type", "clause_by_clause", "legal_compliance"],
        "llm_dependent": True,
    },
    {
        "file": "pdf/03_nda_en.pdf",
        "label": "English NDA (PDF)",
        "expected_status": 200,
        "assert_json": {"language": "en"},
        "not_null": ["document_type", "clause_by_clause"],
        "llm_dependent": True,
    },
    {
        "file": "pdf/04_incomplete_en.pdf",
        "label": "Incomplete draft contract (PDF)",
        "expected_status": 200,
        "assert_json": {"language": "en"},
        "not_null": [],
        "llm_dependent": True,
    },
    {
        "file": "pdf/05_brochure_en.pdf",
        "label": "Marketing brochure / non-contract (PDF)",
        "expected_status": 200,
        "assert_json": {"language": "en", "jurisdiction": "Unknown"},
        "not_null": [],
        "llm_dependent": True,
    },
    # ── Valid DOCX ────────────────────────────────────────────────────────────
    {
        "file": "docx/01_service_agreement_en.docx",
        "label": "English service agreement (DOCX)",
        "expected_status": 200,
        "assert_json": {"language": "en"},
        "not_null": ["document_type"],
        "llm_dependent": True,
    },
    {
        "file": "docx/02_employment_fr.docx",
        "label": "French employment contract (DOCX)",
        "expected_status": 200,
        "assert_json": {"jurisdiction": "France"},
        "not_null": ["document_type"],
        "llm_dependent": True,
    },
    {
        "file": "docx/03_nda_nl.docx",
        "label": "Dutch NDA (DOCX)",
        "expected_status": 200,
        "assert_json": {"jurisdiction": "Netherlands"},
        "not_null": ["document_type"],
        "llm_dependent": True,
    },
    {
        "file": "docx/04_legal_memo_en.docx",
        "label": "Legal memorandum (DOCX)",
        "expected_status": 200,
        "assert_json": {"language": "en"},
        "not_null": [],
        "llm_dependent": True,
    },
    {
        "file": "docx/05_general_terms_en.docx",
        "label": "General terms and conditions (DOCX)",
        "expected_status": 200,
        "assert_json": {"language": "en"},
        "not_null": [],
        "llm_dependent": True,
    },
    # ── Valid TXT ─────────────────────────────────────────────────────────────
    {
        "file": "txt/01_employment_id.txt",
        "label": "Indonesian employment contract (TXT/UTF-8)",
        "expected_status": 200,
        "assert_json": {"jurisdiction": "Indonesia"},
        "not_null": [],
        "llm_dependent": True,
    },
    {
        "file": "txt/02_lease_be.txt",
        "label": "Belgian lease agreement (TXT/Latin-1)",
        "expected_status": 200,
        "assert_json": {"jurisdiction": "Belgium"},
        "not_null": [],
        "llm_dependent": True,
    },
    {
        "file": "txt/03_short_contract_en.txt",
        "label": "Short freelance contract (TXT)",
        "expected_status": 200,
        "assert_json": {"language": "en"},
        "not_null": [],
        "llm_dependent": True,
    },
    {
        "file": "txt/04_long_agreement_en.txt",
        "label": "Long master services agreement (TXT)",
        "expected_status": 200,
        "assert_json": {"language": "en"},
        "not_null": [],
        "llm_dependent": True,
    },
    {
        "file": "txt/05_irrelevant_en.txt",
        "label": "Quarterly earnings report / non-contract (TXT)",
        "expected_status": 200,
        "assert_json": {"language": "en", "jurisdiction": "Unknown"},
        "not_null": [],
        "llm_dependent": True,
    },
    # ── Negative cases ────────────────────────────────────────────────────────
    {
        "file": "negative/empty.pdf",
        "label": "Empty file",
        "expected_status": 400,
        "assert_json": {},
        "not_null": [],
        "llm_dependent": False,
    },
    {
        "file": "negative/fake.pdf",
        "label": "Text file renamed to .pdf",
        "expected_status": 400,
        "assert_json": {},
        "not_null": [],
        "llm_dependent": False,
    },
    {
        "file": "negative/test.csv",
        "label": "CSV file",
        "expected_status": 400,
        "assert_json": {},
        "not_null": [],
        "llm_dependent": False,
    },
    {
        "file": "negative/test.png",
        "label": "PNG image",
        "expected_status": 400,
        "assert_json": {},
        "not_null": [],
        "llm_dependent": False,
    },
]

REQUIRED_KEYS_200 = {"language", "jurisdiction", "layer1", "layer2", "layer3"}


# ── Runner ────────────────────────────────────────────────────────────────────

def _ensure_token() -> str:
    """Return a valid API token for test requests, provisioning one if needed."""
    token = os.getenv("LDV_TEST_TOKEN", "")
    if token:
        return token
    # Auto-provision a test org + user directly in the DB
    sys.path.insert(0, str(Path(__file__).parent.parent))
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
        token = user["api_token"]
    else:
        token = _secrets.token_urlsafe(32)
        _database.create_user(org["id"], email, _auth.hash_password(_secrets.token_urlsafe(16)), "analyst", token)
    print(f"  Test token: {token}  (set LDV_TEST_TOKEN to skip auto-provision)")
    return token


def run(base_url: str, token: str | None = None) -> int:
    if token is None:
        token = _ensure_token()
    headers = {"Authorization": f"Bearer {token}"}
    results = []
    llm_active = None  # detected on first 200 response

    for tc in TESTS:
        path = FIXTURES / tc["file"]
        if not path.exists():
            results.append({**tc, "outcome": "ERROR", "detail": "Fixture file not found"})
            continue

        try:
            with open(path, "rb") as f:
                resp = requests.post(
                    f"{base_url}/analyze",
                    files={"file": (path.name, f)},
                    headers=headers,
                    timeout=120,
                )
        except requests.exceptions.ConnectionError:
            print(f"\n  ERROR: Cannot connect to {base_url}. Is the server running?")
            sys.exit(1)

        status_ok = resp.status_code == tc["expected_status"]
        detail_lines = []

        if not status_ok:
            detail_lines.append(f"status {resp.status_code} ≠ expected {tc['expected_status']}")

        body = {}
        try:
            body = resp.json()
        except Exception:
            detail_lines.append("response is not JSON")

        # Check response is JSON (no HTML)
        if resp.headers.get("Content-Type", "").startswith("text/html"):
            detail_lines.append("response is HTML (traceback?)")

        if resp.status_code == 200:
            # Schema check
            missing_keys = REQUIRED_KEYS_200 - set(body.keys())
            if missing_keys:
                detail_lines.append(f"missing keys: {missing_keys}")

            # Detect if L4 (Qwen) is active
            if llm_active is None:
                llm_active = body.get("layer4", {}).get("available") is True

            # risk_score shape
            rs = body.get("risk_score")
            if rs is not None and not isinstance(rs, dict):
                detail_lines.append(f"risk_score should be dict, got {type(rs).__name__}")
            if isinstance(rs, dict) and llm_active:
                if rs.get("score") is None:
                    detail_lines.append("risk_score.score is null with LLM active")

            # Exact field assertions
            for key, expected in tc["assert_json"].items():
                actual = body.get(key)
                if actual != expected:
                    detail_lines.append(f"{key}: got {actual!r}, expected {expected!r}")

            # Not-null assertions (skip if LLM not active)
            if llm_active:
                for key in tc.get("not_null", []):
                    if body.get(key) is None:
                        detail_lines.append(f"{key} is null")

        outcome = "PASS" if status_ok and not detail_lines else "FAIL"
        if outcome == "FAIL" and tc["llm_dependent"] and not llm_active and resp.status_code == 200:
            # Downgrade to WARN when the only failures are LLM fields with no model loaded
            llm_failures = all(
                any(key in d for key in tc.get("not_null", [])) for d in detail_lines
            )
            if llm_failures:
                outcome = "WARN"

        results.append({
            **tc,
            "outcome": outcome,
            "status": resp.status_code,
            "detail": "; ".join(detail_lines) if detail_lines else "",
            "body_snippet": json.dumps(body)[:120] if body else "",
        })

    # ── Print report ──────────────────────────────────────────────────────────
    col = {"PASS": "\033[92m", "FAIL": "\033[91m", "WARN": "\033[93m", "ERROR": "\033[91m"}
    reset = "\033[0m"

    print(f"\n{'─'*90}")
    print(f"  Sydeco LightML Contract Risk Analyzer — Validation Report  |  server: {base_url}")
    print(f"  LLM active: {'YES' if llm_active else 'NO (model not loaded — LLM assertions skipped)'}")
    print(f"{'─'*90}")
    print(f"  {'RESULT':<6}  {'STATUS':<6}  {'LABEL'}")
    print(f"{'─'*90}")

    counts = {"PASS": 0, "FAIL": 0, "WARN": 0, "ERROR": 0}
    for r in results:
        o = r["outcome"]
        counts[o] += 1
        status_str = str(r.get("status", "—"))
        print(f"  {col.get(o,'')}{o:<6}{reset}  {status_str:<6}  {r['label']}")
        if r["detail"]:
            print(f"           ↳ {r['detail']}")

    print(f"{'─'*90}")
    print(f"  PASS {counts['PASS']}  |  WARN {counts['WARN']}  |  FAIL {counts['FAIL']}  |  ERROR {counts['ERROR']}")
    print(f"{'─'*90}\n")

    # Save JSON report
    report_path = Path(__file__).parent / "validation_report.json"
    with open(report_path, "w") as f:
        json.dump({"llm_active": llm_active, "results": results}, f, indent=2)
    print(f"  Full report saved to: {report_path}\n")

    return counts["FAIL"] + counts["ERROR"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:5000")
    parser.add_argument("--token", default=None, help="Bearer API token (or set LDV_TEST_TOKEN)")
    args = parser.parse_args()
    sys.exit(run(args.url, token=args.token))
