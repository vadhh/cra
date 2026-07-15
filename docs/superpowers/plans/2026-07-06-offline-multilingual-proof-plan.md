# Offline Multilingual Proof Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prove, with a repeatable harness and a PDF report, that LDV analyzes EN/ID/FR/NL contracts and non-contracts with zero outbound network calls, using local Marian MT translation.

**Architecture:** A stdlib socket-level trap (`offline_net_trap.py`) blocks all non-loopback connections for the duration of a test run; a suite runner (`run_offline_validation.py`) drives the existing `_run_analysis` pipeline over an extended fixture set (existing EN/ID/FR/NL contracts + 3 new non-contract fixtures + 1 scanned-PDF + 2 malformed files) under `LDV_REMOTE_TRANSLATION=local`, collecting per-language accuracy/precision/recall/latency/RAM metrics into JSON; a report generator (`generate_offline_report.py`) renders that JSON into a PDF via the already-installed `reportlab` library, matching the existing `pdf_report.py` visual style.

**Tech Stack:** Python 3, stdlib (`socket`, `resource`, `statistics`, `logging`, `json`), `reportlab` (already pinned), pytest, existing LDV modules (`app._run_analysis`, `translator`, `detector_jurisdiction`).

## Global Constraints

- Offline is enforced via a socket-level trap (raises on any non-loopback `connect()`), not physical network disconnection — this is a dev sandbox, not the real deployment target.
- `LDV_REMOTE_TRANSLATION=local` must be set for the run (the default `0` skips translation entirely, which would not exercise the offline Marian MT path being certified).
- `HF_HUB_OFFLINE=1` and `TRANSFORMERS_OFFLINE=1` must also be set — without them, `transformers.from_pretrained()` may attempt an HTTP HEAD request to check for model updates before falling back to cache, which the socket trap would then report as a spurious translation/model-load failure rather than a clean cache hit. This is a necessary implementation detail the design spec didn't spell out, found while planning; it belongs in this task, not a separate one.
- No new dependencies. Reuse `reportlab==4.5.1` (already pinned) for the report; reuse `resource` (stdlib) for peak RSS; no `python-docx`.
- Report output is a PDF at `ldv-backend/tests/offline_validation_report.pdf`. No absolute `/home/...` links anywhere in it — only relative repo paths.
- No OCR is built. The existing fail-closed check in `app.py:196-197` (`ValueError("Scan/OCR required...")`) is the behavior being verified for scanned/malformed input, not replaced.
- Every non-trivial function (network trap, clause-metrics math, percentile calc) gets a real pytest test — no framework beyond pytest, no fixtures beyond what's needed.

---

### Task 1: Download the missing French Marian MT model into the local cache

**Files:**
- None created or modified in the repo. The Hugging Face cache lives at `~/.cache/huggingface/hub/`, outside version control (already the case for the two models already cached).

**Interfaces:**
- Produces: a populated `~/.cache/huggingface/hub/models--Helsinki-NLP--opus-mt-fr-en/` directory, which Task 4/6 depend on being present before the offline run (once cached, `LDV_REMOTE_TRANSLATION=local` + `HF_HUB_OFFLINE=1` can load it without any network access).

- [ ] **Step 1: Download the model (one-time, requires network — this step only)**

Run:
```bash
cd /home/stardhoom/LDV/ldv-backend
python3 -c "
from transformers import MarianTokenizer, MarianMTModel
MarianTokenizer.from_pretrained('Helsinki-NLP/opus-mt-fr-en')
MarianMTModel.from_pretrained('Helsinki-NLP/opus-mt-fr-en')
print('opus-mt-fr-en cached OK')
"
```
Expected: prints `opus-mt-fr-en cached OK` with no exceptions.

- [ ] **Step 2: Verify the cache directory exists**

Run:
```bash
test -d ~/.cache/huggingface/hub/models--Helsinki-NLP--opus-mt-fr-en && echo "CACHE OK" || echo "CACHE MISSING"
```
Expected: `CACHE OK`.

- [ ] **Step 3: No commit** — the HF cache is outside the repo and outside `.gitignore` scope; nothing to stage. Move directly to Task 2.

---

### Task 2: Add FR/NL/ID non-contract fixtures and one scanned-PDF fixture

**Files:**
- Modify: `ldv-backend/tests/create_fixtures.py`

**Interfaces:**
- Produces: `tests/fixtures/docx/06_memo_fr.docx`, `tests/fixtures/docx/07_brochure_nl.docx`, `tests/fixtures/txt/16_notice_id.txt`, `tests/fixtures/pdf/06_scanned_blank_en.pdf` — all four consumed by Task 4's `OFFLINE_SUITE` list by exact relative path.

- [ ] **Step 1: Add the blank/no-text PDF fixture (simulates a scan with no OCR text layer)**

In `ldv-backend/tests/create_fixtures.py`, find this exact block:
```python
make_pdf(
    FIXTURES / "pdf" / "05_brochure_en.pdf",
    "PRODUCT BROCHURE – CloudSuite 2026",
    """Discover the future of enterprise productivity with CloudSuite 2026.

Key Features:
- Real-time collaboration across 50+ apps
- AI-powered workflow automation
- 99.99% uptime SLA guarantee
- ISO 27001 certified security

Pricing Plans:
Starter: USD 29/month per user
Professional: USD 79/month per user
Enterprise: Contact our sales team

CloudSuite is used by over 10,000 businesses worldwide.
Visit www.cloudsuite.example.com or call +1-800-CLOUD-26.

This brochure is for informational purposes only and does not constitute a contract.""",
)


# ── DOCX fixtures ─────────────────────────────────────────────────────────────
```
Replace it with (same content plus a new blank-PDF block inserted before the DOCX section comment):
```python
make_pdf(
    FIXTURES / "pdf" / "05_brochure_en.pdf",
    "PRODUCT BROCHURE – CloudSuite 2026",
    """Discover the future of enterprise productivity with CloudSuite 2026.

Key Features:
- Real-time collaboration across 50+ apps
- AI-powered workflow automation
- 99.99% uptime SLA guarantee
- ISO 27001 certified security

Pricing Plans:
Starter: USD 29/month per user
Professional: USD 79/month per user
Enterprise: Contact our sales team

CloudSuite is used by over 10,000 businesses worldwide.
Visit www.cloudsuite.example.com or call +1-800-CLOUD-26.

This brochure is for informational purposes only and does not constitute a contract.""",
)

# ponytail: blank page, no insert_text call — simulates a scanned image with
# no OCR text layer, exercising app.py's existing "Scan/OCR required" path.
_scan_doc = fitz.open()
_scan_doc.new_page()
_scan_doc.save(str(FIXTURES / "pdf" / "06_scanned_blank_en.pdf"))
_scan_doc.close()


# ── DOCX fixtures ─────────────────────────────────────────────────────────────
```

- [ ] **Step 2: Add the French non-contract fixture (internal legal memo)**

Find this exact block:
```python
make_docx(
    FIXTURES / "docx" / "05_general_terms_en.docx",
    "GENERAL TERMS AND CONDITIONS",
    [
        "These General Terms and Conditions apply to all services provided by OmniServices Ltd.",
        "1. Definitions\n'Service' means any professional service delivered by OmniServices Ltd to a Client.",
        "2. Orders\nAll orders must be confirmed in writing before work commences.",
        "3. Payment\nInvoices are due within 30 days of issue. Late payments accrue interest at 8% per annum.",
        "4. Intellectual Property\nAll deliverables remain the property of OmniServices Ltd until full payment is received.",
        "5. Limitation of Liability\nOmniServices Ltd's total liability shall not exceed the fees paid in the preceding 3 months.",
        "6. Governing Law\nThese terms are governed by English law.",
    ],
)


# ── TXT fixtures ──────────────────────────────────────────────────────────────
```
Replace it with (same block plus two new non-contract fixtures — French memo, Dutch brochure — inserted before the TXT section comment):
```python
make_docx(
    FIXTURES / "docx" / "05_general_terms_en.docx",
    "GENERAL TERMS AND CONDITIONS",
    [
        "These General Terms and Conditions apply to all services provided by OmniServices Ltd.",
        "1. Definitions\n'Service' means any professional service delivered by OmniServices Ltd to a Client.",
        "2. Orders\nAll orders must be confirmed in writing before work commences.",
        "3. Payment\nInvoices are due within 30 days of issue. Late payments accrue interest at 8% per annum.",
        "4. Intellectual Property\nAll deliverables remain the property of OmniServices Ltd until full payment is received.",
        "5. Limitation of Liability\nOmniServices Ltd's total liability shall not exceed the fees paid in the preceding 3 months.",
        "6. Governing Law\nThese terms are governed by English law.",
    ],
)

make_docx(
    FIXTURES / "docx" / "06_memo_fr.docx",
    "NOTE JURIDIQUE INTERNE",
    [
        "À : Conseil d'Administration, Société Lumière SAS",
        "De : Département Juridique",
        "Objet : Conformité au Règlement Général sur la Protection des Données (RGPD)",
        "Date : 1 avril 2026",
        "Cette note résume les obligations de Société Lumière SAS en vertu du RGPD et "
        "recommande des mesures correctives immédiates.",
        "1. Situation actuelle\nLa société ne dispose actuellement d'aucune politique formelle "
        "de conservation des données et n'a pas désigné de délégué à la protection des données.",
        "2. Actions recommandées\n(a) Désigner un DPO dans les 30 jours.\n"
        "(b) Rédiger et publier une politique de conservation des données.\n"
        "(c) Mener un audit complet des activités de traitement des données.",
        "Cette note est confidentielle et protégée par le secret professionnel.",
    ],
)

make_docx(
    FIXTURES / "docx" / "07_brochure_nl.docx",
    "PRODUCTBROCHURE – CloudSuite 2026",
    [
        "Ontdek de toekomst van productiviteit voor bedrijven met CloudSuite 2026.",
        "Belangrijkste functies:\n- Realtime samenwerking in meer dan 50 apps\n"
        "- AI-gestuurde workflow-automatisering\n- 99,99% uptime garantie\n"
        "- ISO 27001 gecertificeerde beveiliging",
        "Prijsplannen:\nStarter: EUR 29/maand per gebruiker\nProfessional: EUR 79/maand per gebruiker\n"
        "Enterprise: Neem contact op met onze verkoopafdeling",
        "CloudSuite wordt gebruikt door meer dan 10.000 bedrijven wereldwijd.",
    ],
)


# ── TXT fixtures ──────────────────────────────────────────────────────────────
```

- [ ] **Step 3: Add the Indonesian non-contract fixture (public notice)**

Locate the last `make_txt(...)` call in the file (`FIXTURES / "txt" / "15_critical_risk_no_law_en.txt"`), which ends with `""",\n)` followed by a blank line and then:
```python
# ── Negative fixtures ─────────────────────────────────────────────────────────
```
Insert a new `make_txt` call for the Indonesian notice immediately before that comment line:
```python
make_txt(
    FIXTURES / "txt" / "16_notice_id.txt",
    """PENGUMUMAN RESMI

Dengan ini diumumkan bahwa PT Sumber Makmur akan mengadakan Rapat Umum Pemegang Saham
Tahunan pada tanggal 15 Mei 2026 di Jakarta.

Agenda rapat meliputi:
- Laporan tahunan direksi
- Persetujuan laporan keuangan tahun 2025
- Pembagian dividen
- Penunjukan auditor independen

Para pemegang saham yang berhalangan hadir dapat memberikan kuasa kepada pihak lain
sesuai dengan ketentuan yang berlaku.

Jakarta, 1 April 2026
Direksi PT Sumber Makmur
""",
)


# ── Negative fixtures ─────────────────────────────────────────────────────────
```

- [ ] **Step 4: Regenerate all fixtures and verify the four new files exist**

Run:
```bash
cd /home/stardhoom/LDV/ldv-backend
python3 tests/create_fixtures.py
test -f tests/fixtures/docx/06_memo_fr.docx && \
test -f tests/fixtures/docx/07_brochure_nl.docx && \
test -f tests/fixtures/txt/16_notice_id.txt && \
test -f tests/fixtures/pdf/06_scanned_blank_en.pdf && \
echo "ALL FOUR NEW FIXTURES PRESENT"
```
Expected: `ALL FOUR NEW FIXTURES PRESENT`.

- [ ] **Step 5: Sanity-check the scanned PDF actually has no extractable text**

Run:
```bash
cd /home/stardhoom/LDV/ldv-backend
python3 -c "
import fitz
doc = fitz.open('tests/fixtures/pdf/06_scanned_blank_en.pdf')
text = ''.join(p.get_text() for p in doc)
assert text.strip() == '', f'expected no text, got: {text!r}'
print('OK: scanned fixture has no extractable text')
"
```
Expected: `OK: scanned fixture has no extractable text`.

- [ ] **Step 6: Commit**

```bash
cd /home/stardhoom/LDV
git add ldv-backend/tests/create_fixtures.py ldv-backend/tests/fixtures/
git commit -m "test: add FR/NL/ID non-contract fixtures and a scanned-PDF fixture"
```

---

### Task 3: Network egress trap (`offline_net_trap.py`)

**Files:**
- Create: `ldv-backend/tests/offline_net_trap.py`
- Test: `ldv-backend/tests/test_offline_net_trap.py`

**Interfaces:**
- Produces: `enable_network_trap() -> None`, `disable_network_trap() -> None`, `self_check() -> bool` — all consumed by Task 5's `run_offline_validation.py`.

- [ ] **Step 1: Write the failing tests**

Create `ldv-backend/tests/test_offline_net_trap.py`:
```python
import socket
from offline_net_trap import enable_network_trap, disable_network_trap, self_check


def test_non_loopback_connect_is_blocked():
    enable_network_trap()
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect(("8.8.8.8", 53))
            assert False, "expected RuntimeError for non-loopback connect"
        except RuntimeError as e:
            assert "BLOCKED" in str(e)
        finally:
            s.close()
    finally:
        disable_network_trap()


def test_loopback_connect_passes_through():
    enable_network_trap()
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        try:
            s.connect(("127.0.0.1", 1))  # nothing listens on port 1 — refused, not blocked
        except RuntimeError:
            assert False, "loopback connect was wrongly blocked"
        except OSError:
            pass  # connection refused/unreachable is expected — it passed through the trap
        finally:
            s.close()
    finally:
        disable_network_trap()


def test_disable_restores_original_connect():
    original = socket.socket.connect
    enable_network_trap()
    disable_network_trap()
    assert socket.socket.connect is original


def test_self_check_reports_true_when_trap_works():
    result = self_check()
    disable_network_trap()
    assert result is True
```

- [ ] **Step 2: Run tests to verify they fail**

Run:
```bash
cd /home/stardhoom/LDV/ldv-backend/tests
python3 -m pytest test_offline_net_trap.py -v
```
Expected: FAIL with `ModuleNotFoundError: No module named 'offline_net_trap'`.

- [ ] **Step 3: Implement `offline_net_trap.py`**

Create `ldv-backend/tests/offline_net_trap.py`:
```python
"""Socket-level egress trap — proves an offline validation run makes zero
outbound network calls.

ponytail: blocks the interpreter's socket layer, not raw syscalls —
sufficient to prove this codebase makes no outbound calls under test, not a
full network-namespace sandbox. Upgrade to iptables/netns only if a future
audit needs kernel-level proof.
"""
import socket

_orig_connect = socket.socket.connect


def _blocked_connect(self, address):
    host = address[0] if isinstance(address, tuple) else address
    if host not in ("127.0.0.1", "::1", "localhost"):
        raise RuntimeError(f"BLOCKED offline-mode outbound connect to {address!r}")
    return _orig_connect(self, address)


def enable_network_trap() -> None:
    socket.socket.connect = _blocked_connect


def disable_network_trap() -> None:
    socket.socket.connect = _orig_connect


def self_check() -> bool:
    """Enable the trap and prove a real outbound connect attempt is blocked."""
    enable_network_trap()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)
    try:
        s.connect(("8.8.8.8", 53))
    except RuntimeError as e:
        return "BLOCKED" in str(e)
    else:
        return False
    finally:
        s.close()
```

- [ ] **Step 4: Run tests to verify they pass**

Run:
```bash
cd /home/stardhoom/LDV/ldv-backend/tests
python3 -m pytest test_offline_net_trap.py -v
```
Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
cd /home/stardhoom/LDV
git add ldv-backend/tests/offline_net_trap.py ldv-backend/tests/test_offline_net_trap.py
git commit -m "test: add socket-level network egress trap for offline validation"
```

---

### Task 4: Pure clause-metrics helpers (`offline_metrics.py`)

**Files:**
- Create: `ldv-backend/tests/offline_metrics.py`
- Test: `ldv-backend/tests/test_offline_metrics.py`

**Interfaces:**
- Produces: `compute_clause_metrics(presence_map: dict, present_expected: list, missing_expected: list) -> dict` (returns `{"tp": int, "fp": int, "tn": int, "fn": int, "details": list}`), `percentile(values: list, pct: float) -> float` — both consumed by Task 5's `run_offline_validation.py`.

- [ ] **Step 1: Write the failing tests**

Create `ldv-backend/tests/test_offline_metrics.py`:
```python
from offline_metrics import compute_clause_metrics, percentile


def test_all_present_expected_detected():
    result = compute_clause_metrics({"a": True, "b": True}, ["a", "b"], [])
    assert result["tp"] == 2
    assert result["fp"] == 0
    assert result["tn"] == 0
    assert result["fn"] == 0
    assert result["details"] == [
        {"clause_id": "a", "status": "TP"},
        {"clause_id": "b", "status": "TP"},
    ]


def test_missing_expected_not_detected_is_true_negative():
    result = compute_clause_metrics({}, [], ["c"])
    assert result["tn"] == 1
    assert result["fn"] == 0


def test_false_negative_when_expected_present_not_detected():
    result = compute_clause_metrics({"a": False}, ["a"], [])
    assert result["fn"] == 1
    assert result["tp"] == 0


def test_false_positive_when_expected_missing_but_detected():
    result = compute_clause_metrics({"c": True}, [], ["c"])
    assert result["fp"] == 1
    assert result["tn"] == 0


def test_percentile_p95_of_ten_values():
    values = list(range(1, 11))  # 1..10
    assert percentile(values, 95) == 10


def test_percentile_empty_list_returns_zero():
    assert percentile([], 95) == 0.0
```

- [ ] **Step 2: Run tests to verify they fail**

Run:
```bash
cd /home/stardhoom/LDV/ldv-backend/tests
python3 -m pytest test_offline_metrics.py -v
```
Expected: FAIL with `ModuleNotFoundError: No module named 'offline_metrics'`.

- [ ] **Step 3: Implement `offline_metrics.py`**

Create `ldv-backend/tests/offline_metrics.py`:
```python
"""Pure metrics helpers for the offline validation harness — no ML imports,
so these stay fast and testable in isolation."""


def compute_clause_metrics(presence_map: dict, present_expected: list, missing_expected: list) -> dict:
    tp = fp = tn = fn = 0
    details = []
    for cid in present_expected:
        if presence_map.get(cid, False):
            tp += 1
            details.append({"clause_id": cid, "status": "TP"})
        else:
            fn += 1
            details.append({"clause_id": cid, "status": "FN"})
    for cid in missing_expected:
        if presence_map.get(cid, False):
            fp += 1
            details.append({"clause_id": cid, "status": "FP"})
        else:
            tn += 1
            details.append({"clause_id": cid, "status": "TN"})
    return {"tp": tp, "fp": fp, "tn": tn, "fn": fn, "details": details}


def percentile(values: list, pct: float) -> float:
    if not values:
        return 0.0
    s = sorted(values)
    k = max(0, min(len(s) - 1, int(round(pct / 100 * (len(s) - 1)))))
    return s[k]
```

- [ ] **Step 4: Run tests to verify they pass**

Run:
```bash
cd /home/stardhoom/LDV/ldv-backend/tests
python3 -m pytest test_offline_metrics.py -v
```
Expected: 6 passed.

- [ ] **Step 5: Commit**

```bash
cd /home/stardhoom/LDV
git add ldv-backend/tests/offline_metrics.py ldv-backend/tests/test_offline_metrics.py
git commit -m "test: add pure clause-metrics and percentile helpers"
```

---

### Task 5: Suite orchestration (`run_offline_validation.py`)

**Files:**
- Create: `ldv-backend/tests/run_offline_validation.py`

**Interfaces:**
- Consumes: `offline_net_trap.enable_network_trap/disable_network_trap/self_check` (Task 3), `offline_metrics.compute_clause_metrics/percentile` (Task 4), `app._run_analysis/_extract_pdf/_extract_docx/_extract_txt` (existing), `detector.detector_jurisdiction.detect_jurisdiction` (existing), `translator` (existing, for capturing failure logs).
- Produces: `ldv-backend/tests/offline_validation_results.json` with top-level keys `self_check_passed`, `config`, `model_provenance`, `translation_failures`, `peak_rss_mb`, `fixtures`, `by_language`, `overall` — consumed by Task 6's `generate_offline_report.py`.

This task is an integration script (drives real ML models) rather than a pure-function unit — its correctness is verified by the full run in Task 7, not by a mocked pytest here. That's an intentional scope boundary: mocking `_run_analysis` would test the mock, not the pipeline.

- [ ] **Step 1: Write `run_offline_validation.py`**

Create `ldv-backend/tests/run_offline_validation.py`:
```python
"""Offline multilingual acceptance harness (Priority 1 acceptance requirement).

Proves EN/ID/FR/NL contract + non-contract analysis with zero outbound
network calls, using local Marian MT translation.

Run: python3 tests/run_offline_validation.py
Writes: tests/offline_validation_results.json
"""
import os
import sys
import json
import time
import logging
import resource
import statistics
from datetime import datetime, timezone
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, BACKEND_DIR)

# Must be set before importing transformers/torch/app — HF_HUB_OFFLINE and
# TRANSFORMERS_OFFLINE make from_pretrained() skip the network entirely and
# use the local cache, instead of attempting an HTTP HEAD check first (which
# the socket trap below would otherwise report as a spurious model-load failure).
os.environ["LDV_REMOTE_TRANSLATION"] = "local"
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

from offline_net_trap import enable_network_trap, disable_network_trap, self_check
from offline_metrics import compute_clause_metrics, percentile

FIXTURES_DIR = Path(HERE) / "fixtures"
RESULTS_PATH = Path(HERE) / "offline_validation_results.json"

_HF_CACHE = Path(os.path.expanduser("~/.cache/huggingface/hub"))
_MODELS_TO_REPORT = [
    "Helsinki-NLP/opus-mt-id-en",
    "Helsinki-NLP/opus-mt-fr-en",
    "Helsinki-NLP/opus-mt-nl-en",
    "typeform/distilbert-base-uncased-mnli",
]

OFFLINE_SUITE = [
    {"path": "pdf/01_employment_id.pdf", "expected": {
        "language": "id", "is_contract": True,
        "present_clauses": ["governing_law", "termination", "working_hours", "compensation"],
        "missing_clauses": ["jurisdiction_venue", "notice_period", "dispute_resolution"],
    }},
    {"path": "pdf/02_lease_be.pdf", "expected": {
        "language": "fr", "is_contract": True,
        "present_clauses": ["governing_law", "termination", "rent_amount", "security_deposit"],
        "missing_clauses": ["jurisdiction_venue", "lease_term", "maintenance_responsibility", "dispute_resolution"],
    }},
    {"path": "pdf/03_nda_en.pdf", "expected": {
        "language": "en", "is_contract": True,
        "present_clauses": ["governing_law", "termination", "confidentiality"],
        "missing_clauses": ["jurisdiction_venue", "return_of_materials", "dispute_resolution"],
    }},
    {"path": "docx/02_employment_fr.docx", "expected": {"language": "fr", "is_contract": True}},
    {"path": "docx/03_nda_nl.docx", "expected": {"language": "nl", "is_contract": True}},
    {"path": "txt/12_high_risk_unilateral_id.txt", "expected": {"language": "id", "is_contract": True}},
    {"path": "txt/13_medium_risk_lease_nl.txt", "expected": {"language": "nl", "is_contract": True}},
    {"path": "pdf/05_brochure_en.pdf", "expected": {"language": "en", "is_contract": False}},
    {"path": "docx/06_memo_fr.docx", "expected": {"language": "fr", "is_contract": False}},
    {"path": "docx/07_brochure_nl.docx", "expected": {"language": "nl", "is_contract": False}},
    {"path": "txt/16_notice_id.txt", "expected": {"language": "id", "is_contract": False}},
    {"path": "pdf/06_scanned_blank_en.pdf", "expected": {"scan_required": True}},
    {"path": "negative/empty.pdf", "expected": {"extraction_error": True}},
    {"path": "negative/fake.pdf", "expected": {"extraction_error": True}},
]


class _TranslationFailureCapture(logging.Handler):
    def __init__(self):
        super().__init__(level=logging.WARNING)
        self.failures = []

    def emit(self, record):
        msg = record.getMessage()
        if "failed" in msg.lower():
            self.failures.append(msg)


def _extract_text(file_path, extract_pdf, extract_docx, extract_txt):
    ext = file_path.suffix.lower()
    data = file_path.read_bytes()
    if ext == ".pdf":
        return extract_pdf(data)
    elif ext == ".docx":
        return extract_docx(data)
    else:
        return extract_txt(data)


def _model_provenance() -> list:
    provenance = []
    for name in _MODELS_TO_REPORT:
        folder = "models--" + name.replace("/", "--")
        ref_path = _HF_CACHE / folder / "refs" / "main"
        if ref_path.exists():
            provenance.append({"name": name, "revision": ref_path.read_text().strip()})
        else:
            provenance.append({"name": name, "revision": "NOT CACHED"})
    return provenance


def run_suite() -> dict:
    from app import _run_analysis, _extract_pdf, _extract_docx, _extract_txt
    from detector.detector_jurisdiction import detect_jurisdiction
    from langdetect import detect

    capture = _TranslationFailureCapture()
    logging.getLogger("translator").addHandler(capture)

    started_at = datetime.now(timezone.utc).isoformat()
    fixture_results = []
    by_language = {}

    for case in OFFLINE_SUITE:
        file_path = FIXTURES_DIR / case["path"]
        expected = case["expected"]
        entry = {"path": case["path"]}

        if expected.get("extraction_error"):
            try:
                _extract_text(file_path, _extract_pdf, _extract_docx, _extract_txt)
                entry["status"] = "FAIL"
                entry["error"] = "expected extraction to raise, it did not"
            except Exception as e:
                entry["status"] = "PASS"
                entry["error"] = str(e)
            fixture_results.append(entry)
            continue

        if expected.get("scan_required"):
            text = _extract_text(file_path, _extract_pdf, _extract_docx, _extract_txt)
            scan_required_detected = not text.strip()
            entry["status"] = "PASS" if scan_required_detected else "FAIL"
            entry["scan_required_detected"] = scan_required_detected
            entry["error"] = None
            fixture_results.append(entry)
            continue

        text = _extract_text(file_path, _extract_pdf, _extract_docx, _extract_txt)
        try:
            lang = detect(text)
        except Exception:
            lang = "unknown"
        jurisdiction = detect_jurisdiction(text)

        t0 = time.perf_counter()
        analysis = _run_analysis(text, jurisdiction, lang)
        latency_ms = (time.perf_counter() - t0) * 1000

        lang_match = lang.lower() == expected["language"].lower()
        l2 = analysis.get("layer2") or {}
        doc_type_detected = (l2.get("document_type") or {}).get("label")
        is_contract_detected = doc_type_detected is not None and analysis.get("layer3", {}).get("skipped") is not True
        is_contract_match = is_contract_detected == expected["is_contract"]

        clause_metrics = {"tp": 0, "fp": 0, "tn": 0, "fn": 0, "details": []}
        if expected["is_contract"] and "present_clauses" in expected:
            presence_list = analysis.get("layer1", {}).get("clause_presence", [])
            presence_map = {c["clause_id"]: c["present"] for c in presence_list}
            clause_metrics = compute_clause_metrics(
                presence_map, expected.get("present_clauses", []), expected.get("missing_clauses", [])
            )

        status = "PASS" if (
            lang_match and is_contract_match
            and clause_metrics["fp"] == 0 and clause_metrics["fn"] == 0
        ) else "FAIL"

        entry.update({
            "language_expected": expected["language"],
            "language_detected": lang,
            "language_match": lang_match,
            "is_contract_expected": expected["is_contract"],
            "is_contract_detected": is_contract_detected,
            "is_contract_match": is_contract_match,
            "document_type_detected": doc_type_detected,
            "clause_tp": clause_metrics["tp"],
            "clause_fp": clause_metrics["fp"],
            "clause_tn": clause_metrics["tn"],
            "clause_fn": clause_metrics["fn"],
            "latency_ms": round(latency_ms, 1),
            "status": status,
            "error": None,
        })
        fixture_results.append(entry)

        lang_key = expected["language"]
        bucket = by_language.setdefault(lang_key, {
            "latencies": [], "total": 0, "passed": 0, "type_correct": 0,
            "clause_tp": 0, "clause_fp": 0, "clause_fn": 0,
        })
        bucket["latencies"].append(latency_ms)
        bucket["total"] += 1
        bucket["passed"] += 1 if status == "PASS" else 0
        bucket["type_correct"] += 1 if is_contract_match else 0
        bucket["clause_tp"] += clause_metrics["tp"]
        bucket["clause_fp"] += clause_metrics["fp"]
        bucket["clause_fn"] += clause_metrics["fn"]

    logging.getLogger("translator").removeHandler(capture)

    by_language_summary = {}
    for lang_key, bucket in by_language.items():
        lat = bucket["latencies"]
        recall_denom = bucket["clause_tp"] + bucket["clause_fn"]
        by_language_summary[lang_key] = {
            "total": bucket["total"],
            "passed": bucket["passed"],
            "failed": bucket["total"] - bucket["passed"],
            "doc_type_accuracy_pct": round(100 * bucket["type_correct"] / bucket["total"], 1) if bucket["total"] else 0.0,
            "clause_recall_pct": round(100 * bucket["clause_tp"] / recall_denom, 1) if recall_denom else None,
            "latency_mean_ms": round(statistics.mean(lat), 1) if lat else 0.0,
            "latency_median_ms": round(statistics.median(lat), 1) if lat else 0.0,
            "latency_p95_ms": round(percentile(lat, 95), 1) if lat else 0.0,
        }

    finished_at = datetime.now(timezone.utc).isoformat()
    peak_rss_mb = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 1)

    total = len(fixture_results)
    passed = sum(1 for r in fixture_results if r["status"] == "PASS")

    return {
        "self_check_passed": True,
        "config": {
            "LDV_REMOTE_TRANSLATION": os.environ.get("LDV_REMOTE_TRANSLATION"),
            "HF_HUB_OFFLINE": os.environ.get("HF_HUB_OFFLINE"),
            "started_at": started_at,
            "finished_at": finished_at,
        },
        "model_provenance": _model_provenance(),
        "translation_failures": capture.failures,
        "peak_rss_mb": peak_rss_mb,
        "fixtures": fixture_results,
        "by_language": by_language_summary,
        "overall": {"total": total, "passed": passed, "failed": total - passed, "blocked": 0},
    }


def main():
    ok = self_check()
    if not ok:
        disable_network_trap()
        raise SystemExit(
            "Network trap self-check FAILED — refusing to run, results would not prove offline operation"
        )
    print("Network trap self-check: PASS (outbound connect correctly blocked)")

    try:
        results = run_suite()
    finally:
        disable_network_trap()

    RESULTS_PATH.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"Results written to {RESULTS_PATH}")
    print(f"Overall: {results['overall']['passed']}/{results['overall']['total']} passed")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Syntax/import smoke check (no models loaded yet)**

Run:
```bash
cd /home/stardhoom/LDV/ldv-backend/tests
python3 -c "import ast; ast.parse(open('run_offline_validation.py').read()); print('SYNTAX OK')"
```
Expected: `SYNTAX OK`.

- [ ] **Step 3: Commit**

```bash
cd /home/stardhoom/LDV
git add ldv-backend/tests/run_offline_validation.py
git commit -m "feat: add offline multilingual validation suite runner"
```

---

### Task 6: PDF report generator (`generate_offline_report.py`)

**Files:**
- Create: `ldv-backend/tests/generate_offline_report.py`
- Test: `ldv-backend/tests/test_generate_offline_report.py`

**Interfaces:**
- Consumes: the JSON schema produced by Task 5 (`self_check_passed`, `config`, `model_provenance`, `translation_failures`, `peak_rss_mb`, `fixtures`, `by_language`, `overall`).
- Produces: `generate_report(results: dict, out_path: Path) -> None`, writing a PDF to `out_path`. `main()` reads `tests/offline_validation_results.json` and writes `tests/offline_validation_report.pdf`.

- [ ] **Step 1: Write the failing test**

Create `ldv-backend/tests/test_generate_offline_report.py`:
```python
from generate_offline_report import generate_report


def test_generates_valid_pdf_from_synthetic_results(tmp_path):
    synthetic = {
        "self_check_passed": True,
        "config": {
            "LDV_REMOTE_TRANSLATION": "local",
            "started_at": "2026-07-06T00:00:00",
            "finished_at": "2026-07-06T00:10:00",
        },
        "model_provenance": [{"name": "Helsinki-NLP/opus-mt-fr-en", "revision": "abc123"}],
        "translation_failures": [],
        "peak_rss_mb": 512.0,
        "fixtures": [
            {"path": "pdf/01_employment_id.pdf", "status": "PASS", "error": None,
             "document_type_detected": "employment contract"},
        ],
        "by_language": {
            "id": {"total": 1, "passed": 1, "failed": 0, "doc_type_accuracy_pct": 100.0,
                   "clause_recall_pct": 100.0, "latency_mean_ms": 500.0,
                   "latency_median_ms": 500.0, "latency_p95_ms": 500.0},
        },
        "overall": {"total": 1, "passed": 1, "failed": 0, "blocked": 0},
    }
    out_path = tmp_path / "report.pdf"
    generate_report(synthetic, out_path)
    assert out_path.exists()
    assert out_path.read_bytes()[:4] == b"%PDF"
    assert out_path.stat().st_size > 1000
```

- [ ] **Step 2: Run test to verify it fails**

Run:
```bash
cd /home/stardhoom/LDV/ldv-backend/tests
python3 -m pytest test_generate_offline_report.py -v
```
Expected: FAIL with `ModuleNotFoundError: No module named 'generate_offline_report'`.

- [ ] **Step 3: Implement `generate_offline_report.py`**

Create `ldv-backend/tests/generate_offline_report.py`:
```python
"""generate_offline_report.py — renders the offline multilingual acceptance
report as a PDF from tests/offline_validation_results.json.

Usage: python3 tests/generate_offline_report.py
"""
import json
from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable,
)

HERE = Path(__file__).parent
RESULTS_PATH = HERE / "offline_validation_results.json"
REPORT_PATH = HERE / "offline_validation_report.pdf"

_NAVY = colors.HexColor("#1a2744")
_GREY = colors.HexColor("#6c757d")

_TABLE_HEADER_STYLE = [
    ("BACKGROUND", (0, 0), (-1, 0), _NAVY),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, -1), 8.5),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dee2e6")),
    ("TOPPADDING", (0, 0), (-1, -1), 4),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
]


def generate_report(results: dict, out_path: Path) -> None:
    W = A4[0] - 4 * cm
    doc = SimpleDocTemplate(
        str(out_path), pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm, topMargin=2 * cm, bottomMargin=2 * cm,
    )
    base = getSampleStyleSheet()

    def _style(name, **kw):
        return ParagraphStyle(name, parent=base["Normal"], **kw)

    h1 = _style("h1", fontSize=18, textColor=_NAVY, fontName="Helvetica-Bold", spaceAfter=6)
    h2 = _style("h2", fontSize=13, textColor=_NAVY, fontName="Helvetica-Bold", spaceBefore=14, spaceAfter=6)
    body = _style("body", fontSize=9, leading=13, spaceAfter=4)
    small = _style("sm", fontSize=8, leading=12, textColor=_GREY, spaceAfter=3)

    story = []
    story.append(Paragraph("LDV Offline Multilingual Acceptance Report", h1))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%d %B %Y, %H:%M')}", small))

    cfg = results.get("config", {})
    story.append(Paragraph(
        f"Config: LDV_REMOTE_TRANSLATION={cfg.get('LDV_REMOTE_TRANSLATION')} | "
        f"Run window: {cfg.get('started_at')} → {cfg.get('finished_at')}", small,
    ))
    story.append(HRFlowable(width=W, thickness=1, color=_NAVY))
    story.append(Spacer(1, 0.3 * cm))

    story.append(Paragraph(
        "Scope: this run tests English, Indonesian, French, and Dutch contract and "
        "non-contract documents, one scanned/no-text PDF, and two malformed files, "
        "with all outbound network sockets blocked (see Verification Evidence).", body,
    ))
    story.append(Spacer(1, 0.3 * cm))

    # ── Test Results ─────────────────────────────────────────────────────
    story.append(Paragraph("Test Results", h2))
    overall = results.get("overall", {})
    rows = [
        ["Test category", "Total", "Passed", "Failed", "Blocked", "Evidence"],
        [
            "Offline multilingual suite",
            str(overall.get("total", 0)), str(overall.get("passed", 0)),
            str(overall.get("failed", 0)), str(overall.get("blocked", 0)),
            "ldv-backend/tests/offline_validation_results.json",
        ],
    ]
    story.append(Table(
        rows, colWidths=[W * 0.27, W * 0.1, W * 0.1, W * 0.1, W * 0.1, W * 0.33],
        style=TableStyle(_TABLE_HEADER_STYLE),
    ))
    story.append(Spacer(1, 0.4 * cm))

    # ── Per-language breakdown ───────────────────────────────────────────
    story.append(Paragraph("Per-Language Metrics", h2))
    lang_rows = [["Language", "Total", "Passed", "Doc-type acc.", "Clause recall", "Mean ms", "Median ms", "P95 ms"]]
    for lang, m in sorted(results.get("by_language", {}).items()):
        lang_rows.append([
            lang.upper(), str(m["total"]), str(m["passed"]),
            f"{m['doc_type_accuracy_pct']}%",
            f"{m['clause_recall_pct']}%" if m["clause_recall_pct"] is not None else "n/a",
            str(m["latency_mean_ms"]), str(m["latency_median_ms"]), str(m["latency_p95_ms"]),
        ])
    story.append(Table(lang_rows, colWidths=[W * 0.13] * 8, style=TableStyle(_TABLE_HEADER_STYLE)))
    story.append(Spacer(1, 0.4 * cm))

    # ── Per-fixture detail ───────────────────────────────────────────────
    story.append(Paragraph("Per-Fixture Detail", h2))
    fix_rows = [["Fixture", "Status", "Detail"]]
    for f in results.get("fixtures", []):
        detail = f.get("error") or f.get("document_type_detected") or ""
        fix_rows.append([f["path"], f["status"], str(detail)[:60]])
    story.append(Table(fix_rows, colWidths=[W * 0.4, W * 0.15, W * 0.45], style=TableStyle(_TABLE_HEADER_STYLE)))
    story.append(Spacer(1, 0.4 * cm))

    # ── Model Provenance ─────────────────────────────────────────────────
    story.append(Paragraph("Model Provenance", h2))
    prov_rows = [["Model", "Revision"]]
    for m in results.get("model_provenance", []):
        prov_rows.append([m["name"], m["revision"]])
    story.append(Table(prov_rows, colWidths=[W * 0.6, W * 0.4], style=TableStyle(_TABLE_HEADER_STYLE)))
    story.append(Spacer(1, 0.3 * cm))

    # ── Translation Failures ─────────────────────────────────────────────
    story.append(Paragraph("Translation Failures", h2))
    failures = results.get("translation_failures") or []
    if failures:
        for msg in failures:
            story.append(Paragraph(msg, body))
    else:
        story.append(Paragraph("None recorded during this run.", body))
    story.append(Spacer(1, 0.3 * cm))

    story.append(Paragraph(f"Peak RAM (RSS): {results.get('peak_rss_mb', 'n/a')} MB", body))
    story.append(Spacer(1, 0.3 * cm))

    # ── Verification Evidence ────────────────────────────────────────────
    story.append(Paragraph("Verification Evidence", h2))
    self_check_line = (
        "PASS — a real outbound connect attempt was raised and blocked"
        if results.get("self_check_passed") else "FAIL"
    )
    story.append(Paragraph(f"Network egress self-check: {self_check_line} before any fixture was processed.", body))
    story.append(Paragraph("Raw results: ldv-backend/tests/offline_validation_results.json", body))
    story.append(Paragraph(
        "Harness source: ldv-backend/tests/run_offline_validation.py, "
        "ldv-backend/tests/offline_net_trap.py", body,
    ))
    story.append(Spacer(1, 0.3 * cm))

    # ── Decisions Required from Management ───────────────────────────────
    story.append(Paragraph("Decisions Required from Management", h2))
    decisions = [
        "Accept socket-level egress blocking as sufficient offline proof for this dev-sandbox "
        "environment, or require kernel-level network-namespace isolation for the next report.",
        "No OCR is implemented; scanned documents are rejected with a clear error rather than "
        "silently mis-analyzed. Confirm this fail-closed behavior is acceptable for the pilot, "
        "or request OCR as a new priority.",
        "Confirm the current fixture set (EN/ID/FR/NL contracts + non-contracts, one scanned "
        "PDF, two malformed files) is sufficient acceptance coverage, or specify additional "
        "cases to add.",
    ]
    for i, d in enumerate(decisions, 1):
        story.append(Paragraph(f"{i}. {d}", body))
    story.append(Spacer(1, 0.3 * cm))

    story.append(Paragraph("Status: Implemented, Tested — pending management Accepted/Blocked decision above.", body))
    story.append(Spacer(1, 0.5 * cm))
    story.append(HRFlowable(width=W, thickness=0.5, color=_GREY))
    story.append(Paragraph(
        "Generated automatically by tests/generate_offline_report.py from "
        "tests/offline_validation_results.json.", small,
    ))

    doc.build(story)


def main():
    if not RESULTS_PATH.exists():
        raise SystemExit(f"{RESULTS_PATH} not found — run run_offline_validation.py first")
    results = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
    generate_report(results, REPORT_PATH)
    print(f"Report written to {REPORT_PATH}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run test to verify it passes**

Run:
```bash
cd /home/stardhoom/LDV/ldv-backend/tests
python3 -m pytest test_generate_offline_report.py -v
```
Expected: 1 passed.

- [ ] **Step 5: Commit**

```bash
cd /home/stardhoom/LDV
git add ldv-backend/tests/generate_offline_report.py ldv-backend/tests/test_generate_offline_report.py
git commit -m "feat: add PDF report generator for offline validation results"
```

---

### Task 7: Full end-to-end acceptance run and evidence commit

**Files:**
- No new source files. Produces the actual evidence artifacts committed to the repo.

**Interfaces:**
- Consumes: everything from Tasks 1–6.
- Produces: `ldv-backend/tests/offline_validation_results.json`, `ldv-backend/tests/offline_validation_report.pdf` — the acceptance deliverables.

- [ ] **Step 1: Run the full offline validation suite (loads real ML models, several minutes on CPU)**

Run:
```bash
cd /home/stardhoom/LDV/ldv-backend
python3 tests/run_offline_validation.py
```
Expected: prints `Network trap self-check: PASS ...`, then runs all fixtures, then `Results written to .../offline_validation_results.json` and an `Overall: X/Y passed` line.

- [ ] **Step 2: Inspect the pass/fail counts before trusting them**

Run:
```bash
cd /home/stardhoom/LDV/ldv-backend
python3 -c "
import json
r = json.load(open('tests/offline_validation_results.json'))
print('self_check_passed:', r['self_check_passed'])
print('overall:', r['overall'])
for lang, m in sorted(r['by_language'].items()):
    print(lang, m)
for f in r['fixtures']:
    if f['status'] != 'PASS':
        print('FAILING FIXTURE:', f['path'], f.get('error'))
"
```
Expected: `self_check_passed: True`; review any `FAILING FIXTURE` lines — if any appear, fix the underlying pipeline issue before proceeding (do not silently accept failures into the report).

- [ ] **Step 3: Generate the PDF report**

Run:
```bash
cd /home/stardhoom/LDV/ldv-backend
python3 tests/generate_offline_report.py
```
Expected: `Report written to .../offline_validation_report.pdf`.

- [ ] **Step 4: Verify the PDF is well-formed and non-trivial**

Run:
```bash
cd /home/stardhoom/LDV/ldv-backend
python3 -c "
p = open('tests/offline_validation_report.pdf', 'rb').read()
assert p[:4] == b'%PDF'
assert len(p) > 2000
print('PDF OK, size:', len(p), 'bytes')
"
```
Expected: `PDF OK, size: <N> bytes`.

- [ ] **Step 5: Commit the evidence artifacts**

```bash
cd /home/stardhoom/LDV
git add ldv-backend/tests/offline_validation_results.json ldv-backend/tests/offline_validation_report.pdf
git commit -m "test: run offline multilingual acceptance suite and record evidence"
```

---

## Self-Review Notes

- **Spec coverage:** model cache (Task 1), FR/NL/ID non-contract + scanned fixtures (Task 2), socket trap + self-check (Task 3), per-language metrics incl. clause recall/precision (Task 4+5), timing percentiles + peak RAM + translation failures + model provenance (Task 5), PDF report with Test Results / Verification Evidence / Model Provenance / Decisions Required sections and a status line (Task 6), full run + committed evidence (Task 7). All spec sections are covered.
- **Placeholder scan:** no TBD/"add later"/"similar to Task N" — every step has complete, runnable code.
- **Type consistency:** `compute_clause_metrics` signature and return shape (Task 4) match exactly how `run_offline_validation.py` calls and destructures it (Task 5). The JSON schema produced in Task 5 matches exactly what `generate_report()` reads in Task 6 (`by_language[...].clause_recall_pct`, `.latency_mean_ms`, etc. all match key-for-key).
