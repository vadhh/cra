---
title: LDV Pilot
emoji: ⚖️
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
---

# Contract Risk Analyzer (CRA) — LDV Pilot

> **Automated contract risk assessment** for legal professionals. Upload a PDF, DOCX, or TXT contract and receive a structured risk score, clause-gap analysis, red-flag detection, and a downloadable PDF report — all offline-capable and multilingual.

---

## Features

- **3-layer analysis pipeline** — rule-based clause detection (L1) → NLI document classifier (L2) → deterministic risk scorer with versioned policy (L3)
- **56 contract type profiles** — employment, lease, NDA, service, loan, construction, government procurement, and more; covers Indonesian, French, and Dutch contracts
- **Red-flag detection** — leonine clauses, abusive penalties, unilateral modification, rights waivers
- **Explain Mode** — per-finding annotations with legal citations and replacement clause suggestions
- **Multilingual** — detects and processes contracts in Indonesian, French, Dutch, English; offline translation via lightml-translator
- **OCR fallback** — scanned PDFs handled via Tesseract (EN / FR / ID / NL)
- **Job durability** — queued → processing → completed / retryable; crashed jobs auto-recover after 30 min; max 3 retries enforced
- **Professional review workflow** — draft citations suppressed in customer mode; reviewer audit trail
- **Multi-tenant auth** — org isolation, MFA (TOTP), per-user download controls, API token access
- **Encrypted at rest** — document text and results encrypted with `LDV_ENCRYPTION_KEY`
- **Offline deployment** — no outbound network required; all models ship locally

---

## Repository Structure

```
.
├── ldv-backend/            # Flask API + ML pipeline
│   ├── app.py              # Routes, auth, upload, result, admin
│   ├── worker.py           # Background thread-pool job executor
│   ├── database.py         # SQLite schema, migrations, audit log
│   ├── auth.py             # Session + API token auth, MFA
│   ├── crypto.py           # Fernet encryption at rest
│   ├── pdf_report.py       # PDF report generator (ReportLab)
│   ├── translator.py       # In-process offline translation
│   ├── translator_client.py# External microservice translation (disabled by default)
│   ├── detector/
│   │   ├── detector_rules.py       # L1 rule-based clause & red-flag detection
│   │   ├── detector_distilbert.py  # L2 NLI document classifier
│   │   ├── detector_scorer.py      # L3 risk scorer (versioned policy)
│   │   ├── detector_explain.py     # Explain Mode annotations
│   │   ├── clause_db.py            # Clause keyword definitions
│   │   ├── citation_db.py          # Legal citation database
│   │   ├── risk_clause_db.py       # Red-flag keyword database
│   │   ├── profile_registry.py     # File-driven contract profile loader
│   │   ├── profiles/
│   │   │   └── registry_v1.json    # 56 contract type profiles (single source of truth)
│   │   └── policies/
│   │       └── default_v1.json     # Default scoring policy (weights & thresholds)
│   ├── tests/              # Unit, API, and integration tests (51 tests)
│   └── manage.py           # CLI — seed, migrate, backup, purge
│
├── ldv-frontend/           # Single-page app (Alpine.js + Vanilla CSS)
│   ├── index.html          # Upload, result, retry, explain mode
│   ├── admin.html          # User / org management
│   ├── result.html         # Result permalink page
│   └── account.html        # MFA setup, API token
│
├── datasets/               # Rule and citation CSV databases
│   ├── dangerous_clauses_MASTER.csv
│   ├── legal_citations.csv
│   ├── leonine_clauses.csv
│   └── abusive_clauses.csv
│
├── deploy/                 # Production deployment helpers
│   ├── nginx.conf          # Nginx reverse proxy + TLS config
│   ├── setup.sh            # Fresh-machine install script
│   ├── ldv-backup.cron     # Automated backup cron job
│   └── gen-cert.sh         # Self-signed cert generator
│
├── docs/                   # Engineering docs and reports
├── docker-compose.yml      # Full stack: app + lightml-translator + nginx
└── Dockerfile              # Multi-stage production image
```

---

## Quick Start

### Docker (recommended)

```bash
# 1. Clone and configure
git clone https://github.com/vadhh/cra.git && cd cra

# 2. Set required secrets
cp .env.example .env          # then edit LDV_SECRET_KEY and LDV_ENCRYPTION_KEY

# 3. Run
docker compose up -d
```

App is available at `http://localhost:7860`. Default admin: `admin@example.com` / `password` — **change immediately**.

### Local Development

```bash
cd ldv-backend
pip install -r requirements.txt
python app.py
```

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `LDV_SECRET_KEY` | ✅ | (random, non-persistent) | Flask session secret |
| `LDV_ENCRYPTION_KEY` | ✅ | (none — plaintext mode) | Fernet key for at-rest encryption |
| `LDV_DB_PATH` | | `./sydeco.db` | SQLite database path |
| `LDV_ADMIN_EMAIL` | | `admin@example.com` | Auto-seeded admin email |
| `LDV_ADMIN_PASSWORD` | | `password` | Auto-seeded admin password |
| `EXTERNAL_TRANSLATION_DISABLED` | | `1` | Set to `0` to enable external microservice translation |
| `LIGHTML_TRANSLATOR_URL` | | (none) | URL of the lightml-translator service |
| `LDV_FORCE_MFA_TESTING` | | (none) | Set `1` to bypass MFA in test environments |

> ⚠️ **Always set `LDV_SECRET_KEY` and `LDV_ENCRYPTION_KEY` before any real deployment.**

---

## Analysis Pipeline

```
Upload (PDF / DOCX / TXT)
    │
    ├── OCR fallback (Tesseract) if scanned PDF
    ├── Language detection (langdetect)
    └── Translation to EN if needed
            │
            ▼
    Layer 1 — Rule-Based Detection (detector_rules.py)
    ├── Governing law & venue detection
    ├── Clause presence check (43 clause types)
    └── Red-flag detection (leonine, abusive, penalty, waiver)
            │
            ▼
    Layer 2 — NLI Document Classifier (detector_distilbert.py)
    ├── Zero-shot NLI classification (DistilBERT-based)
    ├── Keyword pre-filter (4 languages)
    └── Document type → profile lookup (56 types, registry_v1.json)
            │
            ▼
    Layer 3 — Risk Scorer (detector_scorer.py)
    ├── Versioned scoring policy (policies/default_v1.json)
    ├── Score breakdown persisted per analysis
    └── Risk score 0–100 + label (LOW / MEDIUM / HIGH / CRITICAL)
            │
            ▼
    Result stored in SQLite (encrypted)
    ├── profile_id, profile_version, detection_source, detection_confidence
    ├── score_breakdown (JSON), policy_version
    └── Served via REST API + PDF report
```

---

## Contract Type Support

The profile registry (`detector/profiles/registry_v1.json`) covers **56 contract types**.
See [`docs/p7_catalogue_reconciliation.md`](docs/p7_catalogue_reconciliation.md) for the full breakdown:

| Status | Count | Description |
|--------|-------|-------------|
| ✅ Fully auto-detected | 11 | NLI hypothesis + keyword patterns + profile + scorer |
| 🟡 Manual override works | 45 | Profile and scoring correct; auto-detection unreliable |

---

## Running Tests

```bash
cd ldv-backend
python -m pytest tests/ -q          # 51 tests
python tests/validate_profiles.py   # clause reference validator
python tests/test_retry.py          # job recovery (B2/B3/B4)
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| API | Flask 3.1, Gunicorn, Flask-Limiter |
| Auth | Session + TOTP MFA (pyotp), API tokens |
| ML | PyTorch 2.11, HuggingFace Transformers 5.4 |
| OCR | Tesseract + PyMuPDF |
| DB | SQLite (via `database.py`) |
| Encryption | Fernet (cryptography 48) |
| PDF | ReportLab |
| Frontend | Alpine.js, Vanilla CSS |
| Deployment | Docker, Nginx, Docker Compose |
| Translation | In-process (offline) + lightml-translator (optional) |

---

## License

Private — PT Sydeco / LDV Pilot. Not for public distribution.
