# LIGHTML Feasibility Study
**Product:** Contract Risk Analyzer (SaaS)
**LIGHTML:** HTML intelligence layer — the front-facing core of the product
**Date:** 2026-06-08
**Scope:** Study only. No implementation.

---

## 1. Context

LDV (Legal Document Verifier) is a working 4-layer ML backend that analyzes legal contracts.
Contract Risk Analyzer is a new SaaS product built on top of it.
LIGHTML is its HTML interface layer — the part users actually see and interact with.

The question is: how much of LDV can be carried over, and how much net-new work does the SaaS require?

---

## 2. What Can Be Extracted from LDV

### 2.1 Analysis Engine — Fully Usable

The entire Python backend is production-ready logic that can be extracted as-is:

| Module | What it provides | Status |
|---|---|---|
| `detector_rules.py` (395 lines) | L1: jurisdiction, governing law, 11 clause types, 8 red-flag rules. Multilingual (EN/FR/ID/NL). | Ready |
| `detector_distilbert.py` (326 lines) | L2: zero-shot NLI clause classification via DistilBERT. Document-type detection. | Ready |
| `detector_scorer.py` (200 lines) | L3: deterministic 0–100 risk score with per-deduction breakdown. Feature vector for future MLP. | Ready |
| `detector_explain.py` (199 lines) | L4: Qwen LLM explanations — summary, clause commentary, compliance, recommendations. | Ready (opt-in) |
| `translator.py` (18 lines) | Non-English → English before L2/L4. Handles 5000-char chunks. | Ready |
| `send_prompt.py` (74 lines) | Lazy-loaded Qwen singleton, 300s timeout, `max_new_tokens=512`. | Ready |
| `app.py` (240 lines) | PDF/DOCX/TXT extraction, MIME validation, language detection, pipeline orchestration. | Reusable with modification |

**What the API already returns** (the data model LIGHTML will consume):

```
{
  language, jurisdiction,
  layer1: { governing_law, venue, clause_presence[], red_flags[] },
  layer2: { document_type, flagged_clauses[] },
  layer3: { score, label, breakdown[], features },
  layer4: { summary, clause_commentary, compliance_notes, recommendations },
  clause_tags: []
}
```

This is a rich, structured payload. LIGHTML does not need to re-derive any of this — it only needs to render it well.

### 2.2 Frontend Primitives — Partially Reusable

The current `ldv-frontend/index.html` (503 lines) contains patterns worth keeping:

| Pattern | Reusable? |
|---|---|
| Drag-and-drop upload zone | Yes — logic is clean |
| Language switcher (EN/FR/ID/NL via `localStorage`) | Yes — extend to more languages |
| Risk badge colors (LOW green / MEDIUM orange / HIGH red) | Yes — establish as brand system |
| XSS escape helper `esc()` | Yes |
| Spinner + error banner | Yes |
| Clause tag badge rendering | Yes — extend color scheme |

What is **not** reusable from the current frontend: the overall page structure (single-page prototype branded for "Sydeco LDV"), the navbar, the dark background theme, and the single-column results layout. These need to be redesigned for a SaaS product.

### 2.3 Test Suite

`tests/create_fixtures.py` + `run_full_validation.py` — 19 test fixtures, full regression coverage. These validate the engine, not the UI. They transfer directly to the SaaS backend.

---

## 3. What Can Be Reused Directly (Zero Rewrite)

These modules can be copied verbatim into the SaaS backend with no changes:

- `detector/detector_rules.py`
- `detector/detector_distilbert.py`
- `detector/detector_scorer.py`
- `detector/detector_explain.py`
- `detector/detector_jurisdiction.py`
- `translator.py`
- `send_prompt.py`
- `sydeco_engine.py` (gracefully returns empty list when model missing)
- All test fixtures and validation scripts

`app.py` needs minor changes: remove the frontend static-file routes (SaaS will serve frontend separately), add auth middleware hooks, add rate-limit hooks. The `/analyze` endpoint logic is otherwise untouched.

**Estimated reuse: ~2,100 of 3,130 backend lines (67%) carry over without modification.**

---

## 4. What Remains to Build

### 4.1 SaaS Infrastructure (Backend)

The LDV backend has no concept of users, sessions, billing, or persistence.

| Component | Description |
|---|---|
| **User auth** | Registration, login, JWT or session tokens, password reset, email verification |
| **Database** | PostgreSQL — users, analyses (results stored as JSONB), subscriptions |
| **File storage** | S3-compatible blob store for uploaded documents (or discard after analysis) |
| **Analysis history** | Per-user list of past analyses: filename, date, score, jurisdiction |
| **Subscription tiers** | Free (N analyses/month), Pro, Enterprise. Stripe integration |
| **Rate limiting** | Per-user API limits enforced server-side |
| **API keys** | Programmatic access for Pro/Enterprise users |
| **Production server** | Replace `flask run` with gunicorn workers. Existing `requirements.txt` already includes gunicorn |
| **Multi-tenancy** | All analysis results scoped by user ID; no cross-tenant data leakage |

### 4.2 LIGHTML — New Frontend (Core of the Product)

This is the primary build. The current `ldv-frontend` is a prototype — LIGHTML is a full product interface.

**Pages required:**

| Page | Content |
|---|---|
| **Landing page** | Hero, feature pitch, pricing, CTA — no analysis yet |
| **Auth pages** | Login, signup, forgot password |
| **Dashboard** | Analysis history list, risk score distribution summary, quick-upload |
| **Analysis view** | Rich results display (see 4.2.1 below) — the centrepiece of LIGHTML |
| **Pricing page** | Tier comparison, upgrade CTA |
| **Account / settings** | Profile, API key management, subscription management |

**4.2.1 Analysis View — what makes LIGHTML distinctive:**

The current LDV frontend renders results as plain text in dark cards. LIGHTML should render the same JSON payload with proper visual intelligence:

- **Risk gauge** — circular or horizontal gauge, color-coded, 0–100 score prominent
- **Clause map** — table of all detected clauses with present/missing status and evidence snippets; click-to-expand
- **Red flag list** — severity-badged cards, one per flag, with the exact evidence quoted
- **L2 AI findings** — confidence-scored list with label and paragraph excerpt
- **L3 score breakdown** — itemized deduction table (why the score is what it is)
- **L4 explanations** — collapsible sections: Summary, Clause Commentary, Compliance, Recommendations
- **Export button** — download as self-contained HTML report or PDF
- **Language** — full EN/FR/ID/NL interface (LDV already supports all four)

### 4.3 HTML Report Export

A downloadable, self-contained `.html` file that freezes the analysis result — a key SaaS deliverable lawyers can share. This is a LIGHTML generator module: takes the `/analyze` JSON response, injects it into an HTML template with inline CSS, and produces a stand-alone file. Requires no backend storage.

### 4.4 What LDV Does Not Yet Cover (Gaps)

| Gap | Impact |
|---|---|
| `legal_mlp.pkl` missing | `clause_tags` always empty. No SaaS blocker — it degrades gracefully |
| L4 text window truncates at 600–1000 chars | Long contracts lose context in Qwen prompts. Medium priority for SaaS |
| `query_tinyllama()` function name is misleading | Rename to `query_llm()` before publishing API to customers |
| No article citations | Lawyers want "Article 1794, Belgian Civil Code". Zero citation support today |
| Google Translate API dependency | `deep-translator` calls Google; not sovereign. Low priority unless enterprise clients require it |

---

## 5. Time Estimate

Assumptions: one full-stack developer, no prior SaaS boilerplate, LDV backend extracted and stable.

### Phase 1 — MVP (working SaaS, no billing)

| Work | Weeks |
|---|---|
| SaaS backend: auth, PostgreSQL schema, /analyze with user scoping, history endpoint | 2–3 |
| LIGHTML: auth pages + dashboard + analysis view (full visual) | 3–4 |
| HTML report export | 1 |
| Deployment: Docker, gunicorn, domain, HTTPS | 1 |
| **Phase 1 total** | **7–9 weeks** |

### Phase 2 — Billing & Hardening

| Work | Weeks |
|---|---|
| Stripe subscription integration + pricing page | 2–3 |
| Rate limiting, API key system | 1 |
| Teams / sharing (share analysis link) | 1–2 |
| L4 text-window fix (chunked Qwen prompts) | 1 |
| **Phase 2 total** | **5–7 weeks** |

### Phase 3 — Quality (deferred)

| Work | Weeks |
|---|---|
| Article citation engine (L1 rule annotations) | 3–4 |
| DistilBERT fine-tuning on labeled data | 4–6 |
| Local translation (replace Google API) | 2–3 |
| MLP clause tagger model (`legal_mlp.pkl`) | 2–3 |
| **Phase 3 total** | **11–16 weeks** |

### Summary

| Phase | Scope | Est. Duration |
|---|---|---|
| MVP | Core SaaS: auth, history, full LIGHTML, export | 7–9 weeks |
| Phase 2 | Billing, rate limits, sharing | 5–7 weeks |
| Phase 3 | ML quality upgrades | 11–16 weeks |
| **Total to market-ready** | **MVP + Phase 2** | **12–16 weeks** |

The analysis engine (67% of backend code) is already built. The primary investment is LIGHTML itself and SaaS infrastructure — not the AI.

---

## 6. Summary

| Question | Answer |
|---|---|
| What can be extracted? | The full 4-layer analysis engine (L1–L4), pipeline orchestration, file extraction, multilingual translation, and test suite |
| What can be reused as-is? | ~2,100 lines of backend Python — all detector modules, translator, LLM wrapper |
| What remains to build? | SaaS infrastructure (auth, DB, billing), and LIGHTML itself (6 pages, rich analysis view, HTML export) |
| Estimated time to MVP? | 7–9 weeks |
| Estimated time to revenue-ready? | 12–16 weeks |
