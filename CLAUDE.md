# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Sydeco LightML Contract Risk Analyzer** — a Flask backend that analyzes legal documents using a 4-layer ML pipeline: rule-based detection (L1), DistilBERT NLI clause classification (L2), deterministic risk scorer (L3), and optional Qwen LLM explanations (L4).

## Running the Backend

```bash
cd ldv-backend
pip install -r requirements.txt
FLASK_APP=app.py python3 -m flask run --port 5000
```

**Testing the `/analyze` endpoint:**

```bash
# Default (L1 + L2 + L3, fast)
curl -X POST http://127.0.0.1:5000/analyze -F "file=@/path/to/contract.pdf"

# With Qwen explanations (L4, slow — several minutes on CPU)
curl -X POST "http://127.0.0.1:5000/analyze?explain=1" -F "file=@/path/to/contract.pdf"
```

Accepts `.pdf`, `.docx`, `.txt` (max 10 MB). Response: `{language, jurisdiction, layer1, layer2, layer3, layer4, clause_tags}`.

**Environment variables (security defaults — all fail closed):**

| Var | Default | Effect |
|-----|---------|--------|
| `LDV_SECRET_KEY` | unset | Signs Flask session cookies. If unset, an ephemeral per-process key is generated (sessions drop on restart). **Set before any real deployment.** |
| `LDV_DB_PATH` | `ldv-backend/sydeco.db` | Overrides the SQLite database path (used by tests and deployments). |
| `LDV_ADMIN_EMAIL` | unset | Email for the first admin account. Consumed by `python manage.py seed-admin` (must be paired with `LDV_ADMIN_PASSWORD`). |
| `LDV_ADMIN_PASSWORD` | unset | Password for the first admin account. Consumed by `python manage.py seed-admin` (must be paired with `LDV_ADMIN_EMAIL`). |
| `LDV_REMOTE_TRANSLATION` | `0` | `1` allows sending document text to Google Translate. Off = non-English docs analyzed untranslated (L1 is multilingual; L2 degrades). |
| `LDV_CORS_ORIGINS` | unset | Comma-separated origins. Unset = no CORS headers (same-origin only). |
| `LDV_DEBUG` | `0` | `1` enables Flask debug mode (Werkzeug debugger — never in production). |

**User provisioning:** The first admin account is created with:
```bash
LDV_ADMIN_EMAIL=admin@example.com LDV_ADMIN_PASSWORD=securepassword python manage.py seed-admin
```

Further users are created with:
```bash
python manage.py create-user <email> <org> [--role admin]
```

Analysis results are addressed by unguessable UUID (`analyses.public_id`), not integer IDs — `/upload` returns `{"id": "<uuid hex>"}` and `/api/result/<uuid>` is the only lookup. `database.init_db()` auto-migrates old DBs (adds + backfills `public_id`). **Note:** `/api/result/<uuid>` now requires user authentication and enforces organization ownership (cross-org requests return 403).

**Check model/layer status:**

```bash
curl http://127.0.0.1:5000/health
```

**Running the validation suite:**

```bash
python3 tests/create_fixtures.py          # generate fixtures once
python3 tests/run_validation.py           # quick regression
python3 tests/run_full_validation.py      # full checklist (300s timeout)
```

Results saved to `tests/validation_report.json` and `tests/validation_report.md`.

## Architecture

### 4-Layer Pipeline

| Layer | File | Method | Speed |
|-------|------|--------|-------|
| L1 Rules | `detector/detector_rules.py` | Regex/keyword — jurisdiction, governing law, clause presence, red flags | <10 ms |
| L2 DistilBERT | `detector/detector_distilbert.py` | Zero-shot NLI (`typeform/distilbert-base-uncased-mnli`, ~67 MB) | 5–15 s CPU |
| L3 Scorer | `detector/detector_scorer.py` | Deterministic formula on L1+L2 features, 0-100 score | <1 ms |
| L4 Qwen | `detector/detector_explain.py` | Qwen3-1.7B explanations — opt-in via `?explain=1` | minutes CPU |

### Layer details

**L1 (`detector_rules.py`):** Covers 7 jurisdictions (ID/BE/FR/NL/EN&W/US/generic), venue/governing-law detection, 11 clause types, 8 regex red-flag rules (leonine, excessive penalty, rights waiver, unilateral modification, liability exclusion, auto-renewal, illegal object) **plus a keyword second pass** (`risk_clause_db`, 289 lawyer-authored risky clauses). All multilingual (EN/FR/ID/NL). Returns `{governing_law, venue, clause_presence, red_flags, layer1_score}`.

**L2 (`detector_distilbert.py`):** NLI label order for `typeform/distilbert-base-uncased-mnli` is `{0: ENTAILMENT, 1: NEUTRAL, 2: CONTRADICTION}` (index 0, not 2 — unlike facebook/bart). Doc-type hypotheses are per-label specific phrases, not template-based (`"This document is a {}"` scores near-zero due to grammar). Clause classifier uses threshold 0.70 with OR-logic across multiple hypotheses per label. Paragraph splitter splits on `\n+` (single newlines — contracts use one clause per line). Returns `{document_type, flagged_clauses, layer2_available}`.

**Semantic missing-clause check (`semantic_clause_presence()` in `detector_distilbert.py`):** Before L3 scoring, `app._semantic_backfill()` re-checks the *required* clauses that L1's keyword/regex pass marked absent. For each, it runs NLI entailment of a tuned presence hypothesis (`_CLAUSE_PRESENCE_HYPOTHESES`, plain declarative phrasing — meta "This document states…" phrasings score ~0 under this MNLI model) against the doc's paragraphs; a paragraph above `_SEM_PRESENCE_THRESHOLD` (0.65) flips that `clause_presence` entry to `present` with `source="semantic_nli"`. Pure recovery (only False→True), reuses the already-loaded DistilBERT (no Qwen), bounded to the missing-required set with per-clause early-exit. L3 is unchanged — it reads `present` as before, so semantically-recovered clauses no longer incur a missing-mandatory penalty.

**L3 (`detector_scorer.py`):** Required-ness is **contract-type-aware** — `evaluate_contract_type_requirements()` resolves the mandatory clause set from `detector_rules._CONTRACT_TYPE_PROFILES` keyed on the L2 `document_type` label (falls back to `_BASELINE_REQUIRED` for unknown types). Missing-mandatory penalties are **severity-scaled** by Ilham's `Impact_Level` via `clause_db.clause_impact()`: CRITICAL –20 / HIGH –15 / MEDIUM –10 / LOW –5, falling back to flat –10 (`_W_MISSING_REQUIRED`) for clauses not reconciled to her DB. Other weights: –25/HIGH L1 flag, –10/MEDIUM L1 flag, –8/unique L2 finding, –12/no governing law, –8/no venue. De-duplicates L1/L2 overlapping findings; excludes governing_law/jurisdiction_venue from the generic missing count (they have dedicated penalty lines). `has_governing_law`/`has_venue` use OR logic (detect_governing_law() result OR clause_presence check) to avoid pattern-set mismatches. `layer3_score(layer1, layer2, lang="EN")` returns `{score, label, breakdown, features, contract_type, required_clauses}` — `required_clauses` surfaces per-clause Ilham rationale (Impact_Level/Reason/Recommendation/Business_Impact); `features` is training-ready for future `sklearn.MLPClassifier`.

**L4 (`detector_explain.py`):** 4 focused Qwen prompts (summary, clause commentary, compliance assessment, recommendations) using structured L1/L2/L3 context (not raw text). `available=False` when model not loaded. Opt-in only — default response skips L4 to keep latency fast.

### Other modules

- `send_prompt.py` — `query_llm()` (runs Qwen3-1.7B; renamed from `query_tinyllama`) runs inference via `transformers`. Lazy singleton; loaded once on first call. Has `GENERATION_TIMEOUT` (default 300s) and `max_new_tokens=512`. Override model: `export LDV_MODEL=<hf-model-id>`.
- `translator.py` — wraps `deep-translator` (GoogleTranslator) with 5000-char chunking; translates non-English docs to English before L2/L4. Note: still depends on Google's translation API (not fully local/sovereign).
- `sydeco_engine.py` — MLP clause tagger (`classify_clauses()`); runs after L3. Returns `clause_tags`. Requires `legal_mlp.pkl` model file — currently missing, returns empty list gracefully.
- `detector/detector_jurisdiction.py` — keyword scoring across 4 jurisdictions (ID/BE/FR/NL); degrades to `"Unknown"`.
- `detector/clause_db.py` — runtime adapter for Ilham's lawyer-authored `datasets/required_clauses.csv` (no ML). Lazy singleton, fail-soft. `_CLAUSE_ID_TO_ILHAM` reconciles our clause IDs to her `Clause_Name`s. Feeds L3: `clause_guidance()` (Impact_Level/Reason/Recommendation/Business_Impact, lang EN/ID/FR), `clause_keywords()` (keyword detection fallback in L1 `check_clause_presence`), `clause_impact()` (severity weights). `notice_period` intentionally unmapped — her "Notice" clause is formal communications, not a termination notice period.
- `detector/risk_clause_db.py` — keyword-based risky-clause detector (no ML), loads the lawyer-authored category CSVs (`datasets/{abusive,dangerous,illegal,leonine}_clauses.csv` — 289 risky clauses / 2559 phrases, EN/FR/ID). `detect_keyword_flags(text, exclude_ids)` runs as a **second pass in `detector_rules.detect_red_flags`**, appending findings with `source="keyword_db"` (regex findings now carry `source="regex"`). **Precision-first matching:** 1-word phrases never trigger alone; a clause fires only on *corroboration* — one specific phrase (≥3 words) or ≥2 distinct 2-word phrase hits, word-boundary matched. Suppresses concepts a regex rule already fired via `_REGEX_OVERLAP`. Severity from `Impact_Level`. Validated: 0 false-positives on realistic fixtures, fires on genuinely abusive text, full suite 60 PASS · 0 FAIL. `python3 detector/risk_clause_db.py` self-check.
- `detector/citation_db.py` — runtime adapter for `datasets/legal_citations.csv` (legal source traceability, no ML). Lazy singleton, fail-soft, mirrors `clause_db.py`. `annotate_layer1(layer1, jurisdiction)` attaches an inline `citations: [...]` array to each `red_flags[].id` and `clause_presence[].clause_id` using the doc's detected jurisdiction (falls back to `generic` rows, `[]` if none). Citations are lawyer-authored **data, never LLM-generated**; each carries a `status` (`verified`|`draft`) trust flag — Claude-seeded rows are `draft` until a lawyer verifies. `citations_for(id, juris)` lookup; `verify_against(valid_ids)` drift guard; `python3 detector/citation_db.py` runs the drift + lookup self-check. Wired in `app.py._run_analysis` right after L1.
- `app.py` — Flask entry point; PDF/DOCX/TXT extraction, size limits, MIME validation, language detection, translation, orchestrates all 4 layers.

### `tests/`

- `create_fixtures.py` — generates 19 test files (5 PDF, 5 DOCX, 5 TXT, 4 negatives) under `tests/fixtures/`
- `run_validation.py` — quick regression runner
- `run_full_validation.py` — full checklist with 300s timeout per request

## Environment Quirks

- **Pillow ≥ 9.1.0 required** — `PIL.Image.Resampling` was added in 9.1.0; older versions block all `transformers` imports via `image_utils.py`. Run `pip3 install --upgrade Pillow` if you see `AttributeError: module 'PIL.Image' has no attribute 'Resampling'`.
- **libmagic + DOCX** — on this Ubuntu system, `python-magic` returns `application/octet-stream` for valid DOCX files. Workaround in `app.py`: if `application/octet-stream` + `.docx` + `data[:2] == b"PK"` → treat as `application/zip`.
- **PyTorch inference mode** — security hook blocks `.eval()` calls. Use `model.training = False` to set inference mode instead.
- **No GPU** — 2 CPU cores, CUDA unavailable. L2 (DistilBERT) takes 5–15s; L4 (Qwen) takes several minutes per request.
- **Models cached:** Qwen3-1.7B fully at `~/.cache/huggingface/hub/models--Qwen--Qwen3-1.7B/` (3.8 GB complete). DistilBERT cached at `typeform/distilbert-base-uncased-mnli`.
- **~~googletrans alpha~~** — RESOLVED: `translator.py` now uses `deep-translator` (GoogleTranslator), a maintained library. However, translation still hits Google's API (not local).

## Current Validation Status

Last run: `python3 tests/run_full_validation.py` — **~60 PASS · 2 WARN · 0 FAIL · 9 PENDING**

- The 9 PENDING sections (3, 5, 6, 7.2, 7.3) require L4 (`?explain=1`) — need Qwen loaded and minutes of CPU time per request.
- WARN includes: sydeco_engine.py model file (`legal_mlp.pkl`) missing — clause tagging returns empty.

## TODO

### P0 — Production blockers (from 2026-06-22 external review)

> Sources: `docs/2026-06-22-PRD.md` (authoritative product scope, FR IDs, release gates, roadmap) + `docs/2026-06-22-external-review.md` (verdict 5.5/10, controlled-pilot only). **No paid production use until all P0 are closed and verified.** None are started. These P0 map to PRD Sprint 2 (Security & operations) + Gates 3/4; full requirement IDs (IAM/ING/CLS/CLP/RSK/SCR/CIT/OUT/SUB/SEC) live in the PRD — treat it as the spec of record, this list as the near-term blocker view.

1. ~~**AuthN/AuthZ on results**~~ (CR-01) — **DONE (core features).** Session+API-token login, `organizations`/`users` tables, per-org document ownership, `/api/result/<uuid>` now requires auth + enforces 403 on cross-org access, `/upload`/`/analyze`/`/report` require auth, `/api/stats`/`/api/recent`/`/admin` require an admin account (replacing the legacy `LDV_ADMIN_TOKEN` shared-token mechanism), `manage.py` CLI for provisioning (`seed-admin`, `create-org`, `create-user`). Still TODO: MFA, full 5-role matrix (analyst/legal-reviewer/manager/…), org/user management UI, signed + expiring download links (IAM-04), audit log (SEC-06), rate limiting/CSRF (SEC-07).
2. ~~**Suppress draft citations from client output**~~ (CR-02) — **DONE.** `citations_for()`/`annotate_layer1()` fail closed to `status=="verified"` (`include_drafts=False` default); `/analyze` no longer emits draft citations. Reviewer path passes `include_drafts=True`. Self-check in `citation_db.py` asserts both directions. Still TODO: lawyer approval *workflow* (status transitions UI) — depends on the auth/reviewer endpoint (P0 #1).
3. **Retention / purge / encryption-at-rest** (CR-04) — uploads, extracted text, results, logs cannot persist indefinitely in `uploads/` + SQLite. Add retention+purge controls; encrypt stored documents.
4. **Async job queue** (CR-10) — `flask run` + in-process L2/L4 blocks workers for minutes. Move analysis to a worker queue; return `202`; expose `queued/running/completed/failed`. (Pairs with P1 #3 gunicorn.)
5. **Pinned deps + reproducible deploy** (CR-09, CR-10) — pin `requirements.txt`; Docker/systemd with health checks that expose degraded mode (missing citations/datasets/models must alert + show in report metadata).

**P1 from the review** (track alongside P2 Quality below): clause-coverage matrix (CR-11); lawyer-reviewed benchmark set measuring precision/recall/false-missing by type+jurisdiction+language (CR-05/07/08); version scoring policies + show score-version/confidence/limits in reports (CR-03); language-aware keyword matching + evidence spans (CR-06); package or remove `legal_mlp.pkl` (overlaps P2 #8). Also: fix "100% recall" wording → "all targeted cases passed" (CR-05).

### P1 — Reliability

1. ~~**Replace `googletrans==3.1.0a0`**~~ — **DONE.** `translator.py` now uses `deep-translator` (GoogleTranslator). Remote translation is opt-in via `LDV_REMOTE_TRANSLATION=1` (off by default — confidentiality); still not local when enabled.
2. ~~**Add LLM call timeout**~~ — **DONE.** `send_prompt.py` has `GENERATION_TIMEOUT=300s` via ThreadPoolExecutor + `max_new_tokens=512`.
3. **Run Flask under gunicorn** — `flask run` is single-threaded. Use `gunicorn -w 4 app:app`. (`app.run` debug is now env-gated via `LDV_DEBUG`, off by default.)
4. ~~**Rename `query_tinyllama()`**~~ — **DONE.** Now `query_llm()` in `send_prompt.py` (only caller was `detector_explain.py`).

### P2 — Quality

5. **DistilBERT fine-tuning** — currently zero-shot with no training data in codebase. Need to create labeled dataset (200+ per label) and fine-tune `distilbert-base-multilingual-cased`.
6. **Increase L4 text window** — prompts truncate at 600/800/1000 chars (`detector_explain.py:111,122,179`). Multi-page contracts lose all context beyond the first page. Implement chunking.
7. ~~**Add legal source traceability**~~ — **DONE (mechanism).** `detector/citation_db.py` + `datasets/legal_citations.csv` attach inline per-finding citations (red flags + clauses) with a `verified`/`draft` trust flag. Seeded with confident `draft` rows (FR/ID/BE); **needs lawyer review to verify and expand the CSV** — the code is complete, the data is a starting seed.
8. **Provide `legal_mlp.pkl` model** — `sydeco_engine.py` clause tagger requires this file at `~/Desktop/sydeco_ai_core_bundle/models/legal_mlp.pkl`. Currently missing; clause_tags always returns empty.
9. **Layer 3 MLP training** — replace deterministic formula with trained `sklearn.MLPClassifier` once labeled risk data exists (feature vector interface already in place via `layer3.features`).
10. **Expand jurisdiction coverage** — L1 covers 7 jurisdictions but `detector_jurisdiction.py` only scores 4 (ID/BE/FR/NL).
11. **Local translation** — `deep-translator` still calls Google's API. For full sovereign AI, replace with a local translation model.

### P3 — Nice to have

12. **API versioning** — prefix routes as `/api/v1/analyze`.
13. **Docker setup** — no `Dockerfile` or `docker-compose.yml`.
14. **OpenAPI/Swagger docs** — use `flasgger` or `flask-smorest`.
15. **`raw_text` field** — expose via `?debug=1` only.

---

## Future Deployment Plan (post-dev — NOT for current dev phase)

> Status: **planning only.** We are still in the dev phase; everything runs on one machine. This is the target topology for when we move to server hosting. Do not implement yet.

**Idea:** split the app and the AI model across two machines for better AI performance and isolation.

**Why it makes sense:** today everything shares 2 CPU cores with no GPU — L2 (DistilBERT) takes 5–15s, L4 (Qwen3-1.7B) takes minutes. Flask (HTTP) and PyTorch (inference) compete for the same cores, so a slow Qwen call stalls the web server. Separating inference removes that contention.

**Key caveat:** the real speedup comes from a **GPU**, not merely from a second box. A second *CPU-only* machine gives isolation but Qwen stays slow (minutes is a CPU problem). The AI machine must have a **GPU with enough VRAM** — Qwen3-1.7B fits easily, DistilBERT is tiny. GPU turns minutes into seconds.

**Target topology — 2 machines (not 3):**

| Machine | Responsibilities | Hardware |
|---------|------------------|----------|
| App / web server | Flask under gunicorn, SQLite DB, file extraction (PDF/DOCX/TXT), L1 rules, L3 scorer, citation_db | Modest CPU, no GPU |
| AI / inference server | L2 (DistilBERT) + L4 (Qwen) behind a small inference API | **GPU + adequate VRAM** |

A separate third "DB/server" box adds little at current scale — SQLite on the app machine is fine until real load forces a split. Don't buy hardware for a problem we don't have yet.

**Refactor required:** L2/L4 are currently in-process Python calls (`detector_distilbert.py`, `send_prompt.py`). To move them across machines, wrap them in a small inference API (FastAPI/Flask) on the AI box and have the app server call it over HTTP instead of importing directly. Modest change — the 4 layers are already cleanly separated, so it's mainly adding a network boundary between L1/L3 and L2/L4. Pairs with TODO P1 #3 (gunicorn) and P3 #13 (Docker).

---

## Feature Roadmap (from LEGAL DOC VERIFYER archives)

Prototype modules exist in `LDV AUDIT 12 06 2025 - WHAT TO DO NEXT/ldv-full-upgraded.zip`.

### R1 — Detection upgrades

- **Semantic missing clause detection** — `detector/detector_missingclauses_llm.py`. LLM checks whether required clauses are semantically present. Prototype in archive.
- ~~**Legal source traceability**~~ — **DONE (mechanism).** See `citation_db.py` / TODO P2 #7. CSV seed pending lawyer verification.
- **Legal persona adaptation** — detect B2B/B2C/employment; adjust clause severity thresholds accordingly.
- **Per-client policy enforcement** — admin-configurable list of unacceptable clauses.

### R2 — Rewriting & redrafting

- **Clause recommendation engine** — `detector/detector_recommendation.py`. 3 rewrite variants per risky clause (soft/neutral/strict). Prototype in archive.
- **Auto-redrafting engine** — `redraft_engine.py`. Assembles full safer contract. Prototype in archive.

### R3 — Reporting & export

- **PDF + plaintext report export** — `pdf_export.py`. Clause map, risk score, suggestions. Prototype in archive.
- **Multi-language report** — EN/FR/ID/NL output via `LABELS` dict. Prototype in `PROJECT/PHASE 7/`.

### R4 — Analytics

- **Analytics dashboard** — upload history, risk distribution, clause coverage. Prototype in `PROJECT/PHASE 7/`.

### R5 — AI clause classifier (Phase 8)

- **ML clause classifier** — train on `clause_training_data.csv`; scripts in `PROJECT/PHASE 8/`.
- **Clause negotiation assistant** — suggest fairer terms from `clause_suggestions_extended.json`.

### R6 — Packaging

- **systemd service**, **`.deb`/`.exe` packaging** — post-completion.

### R7 — Phase 9: Contract Drafting Assistant

- Generate full contracts from scratch. Spec in `PROJECT/PHASE 9 CONTRACT DRAFTING ASSISTANT/`. Depends on R2 being mature.
