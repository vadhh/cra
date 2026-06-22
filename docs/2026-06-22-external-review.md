# External Engineering Review — Daily Reports 12–19 June 2026

> Reviewer assessment of the 12–19 June daily reports for the Sydeco LightML
> Contract Risk Analyzer. Filed 2026-06-22. **Verdict: 5.5/10 — strong
> controlled-pilot prototype, NOT production-ready legal SaaS.** Authorize
> continued dev + internal/pilot testing; do not authorize paid production use
> until the P0 actions (Section 6) are closed and verified.

## 1. Executive assessment

The five reports form a credible, logically connected engineering sequence:
deterministic rules create findings, semantic models improve recall, a scorer
aggregates risk, and a local LLM explains results without controlling them.

| Area | Assessment | Current state |
|------|-----------|---------------|
| Product reasoning | Strong | Correctly separated deterministic detection from ML enhancement. |
| Engineering execution | Strong | Incremental changes, self-checks, drift guards, repeated validation. |
| Legal defensibility | Incomplete | ID citations partially verified; many citations/scoring assumptions draft/uncalibrated. |
| Security & privacy | Improved but incomplete | Prototype leaks fixed, but UUID access ≠ authorization; retention/encryption absent. |
| Deployment readiness | Prototype/pilot | Gunicorn documented; async processing, pinned deps, reproducible deploy unfinished. |
| Quality evidence | Promising but narrow | 60 PASS is regression evidence, not a legal-accuracy or multilingual benchmark. |

## 2. What was done well

- **Correct product architecture** — reframed payment-window detection as a rule-engine problem, not a "wait for more training data" problem.
- **Incremental integration** — required-clause work split into a non-breaking data-adapter phase and a behavior-changing detection/scoring phase.
- **Traceable origin of findings** — sources (rules / lawyer keywords / semantic NLI / keyword DB) are tagged → auditable.
- **Regression discipline** — repeated 60 PASS / 2 WARN / 0 FAIL reran against a stable suite.
- **Security awareness** — identified sequential IDs, remote-translation leakage, open CORS, debug mode, query-string secrets, timeout behavior; several fixed immediately.
- **Legal-source separation** — citations must be lawyer-verifiable and never LLM-generated. Correct trust boundary.
- **Honest deferral** — distinguishes completed / deferred / dependent-on-legal-data work.

## 3. Critical corrections and risks

| ID | Severity | Finding |
|----|----------|---------|
| CR-01 | Critical | A UUID result URL prevents enumeration but does **not** authorize access. Anyone with the URL reads the contract. Production needs user auth, tenant ownership checks, expiring signed download links. |
| CR-02 | Critical | Draft citations must **never** appear as verified legal authority. Runtime must suppress them from client reports or show only in an internal legal-review mode. |
| CR-03 | Critical | Risk weights/labels are not legally calibrated. A score of 95 / CRITICAL can look authoritative when driven by provisional deductions. Reports must show score-version, limitations, confidence separately. |
| CR-04 | Critical | No complete retention/deletion/encryption-at-rest policy. Confidential contracts + extracted text cannot remain indefinitely in uploads/SQLite. |
| CR-05 | High | "100% recall" (12 June) is unsupported by nine smoke tests. Correct claim: "all targeted test patterns passed." Recall needs a labeled benchmark counting false negatives. |
| CR-06 | High | All-language keyword union can create cross-language false positives. Matching should be language-aware, with controlled fallback only when language detection is uncertain. |
| CR-07 | High | The 0.65 semantic-presence threshold is from limited examples. Needs per-contract-type and per-language calibration against positive/negative fixtures. |
| CR-08 | High | 2,559-phrase risky-clause DB corroboration heuristic needs a benchmark, not only clean-fixture checks. Measure precision/recall per category and language. |
| CR-09 | High | "Fail soft" is fine for dev; production must expose degraded-mode health. Missing citations/datasets/models must alert an operator and show in report metadata. |
| CR-10 | High | Gunicorn docs ≠ deployment. Long CPU-bound DistilBERT/Qwen tasks need an async worker queue; otherwise workers block and duplicate large-model memory. |
| CR-11 | Medium | Mapping narrative drifts (15 → 24 of 39 unmapped → 21 complete). Need one coverage matrix: every internal clause ID, external clause name, supported languages, status. |
| CR-12 | Medium | Reports are backend-heavy; user roles, portal behavior, PDF schema, package entitlements, audit trail, billing, case review, legal-review workflow not yet defined. |

## 4. Report-by-report review

**4.1 — 12 June.** Strongest product-thinking report. Distinguishes the weak
payment_risk classifier from the product's ability to detect explicit payment
terms. Approve: payment-window rules, non-contract routing, remote-translation
opt-in, debug/CORS tightening, timeout fix, priority ordering. Correct: replace
"100% recall" with "all nine targeted cases passed." Open: auth/authz,
retention, local translation, async jobs, dependency pinning, unit tests, model
packaging.

**4.2 — 15 June.** Contract-type profile + required-clause bridge are the
correct foundation; resolving requiredness in the scoring layer is reasonable;
removing the wrong notice-period mapping shows good data discipline. Improve:
version profile data, make it editable without code, record reviewer + approval
date. Risk: unknown types falling back to a commercial baseline can mislead —
unknown should also emit an uncertainty warning.

**4.3 — 17 June.** Severity-scaled missing-clause penalties beat a flat
deduction; accepting CRITICAL in the stale test was right. But passing only
proves internal consistency, not legal meaning. Condition: store weights in a
versioned policy file, calibrate with lawyer-reviewed contracts before public
use. Do not claim a CRITICAL score is legally authoritative because the suite
accepts the label.

**4.4 — 18 June.** Semantic missing-clause recovery is valuable (only flips
missing→present, can't invent penalties) and reuses the existing NLI model.
Require: store matched paragraph, entailment score, hypothesis version, model
version with every recovery. Test negation/exceptions/references ("the clause
shall not apply") that fool entailment models.

**4.5 — 19 June.** Closes citation plumbing, keyword-DB adoption, admin-token
hardening, private repo publication. Corroboration rule is a good fix for
single-word false positives. Block for client reports: draft citations and any
finding whose legal source isn't approved for the selected jurisdiction.
Clarify exact clause-mapping coverage — disjoint naming doesn't prove coverage
is complete. Deployment: gunicorn documented not deployed; Docker/systemd,
worker queue, missing `legal_mlp.pkl` remain release blockers.

## 5. Engineering readiness scorecard

| Dimension | Rating | Reason |
|-----------|--------|--------|
| Architecture & separation of concerns | 8/10 | Good layer separation, deterministic trust boundary. |
| Rule & dataset traceability | 8/10 | Source tags, drift guards, citation status strong. |
| Legal validation | 4/10 | Partial verified citations; scoring + many rules need legal calibration. |
| Security & confidentiality | 5/10 | Serious leaks fixed, but access control/retention/encryption incomplete. |
| Reliability & deployment | 4/10 | No complete async/reproducible production deployment. |
| Testing evidence | 6/10 | Stable regression suite, but insufficient benchmark breadth + unit coverage. |
| Multilingual quality | 5/10 | Patterns exist; cross-language + local-translation quality unmeasured. |
| Commercial product completeness | 3/10 | Portal, roles, reports, packages, billing, case workflow unspecified. |
| **Overall** | **5.5/10** | Strong controlled-pilot prototype; not yet production legal SaaS. |

## 6. Required next actions

| Priority | Action |
|----------|--------|
| P0-1 | Authenticated users, tenant ownership, authorization on every result/report endpoint. |
| P0-2 | Suppress draft citations from customer output; add legal-review approval workflow. |
| P0-3 | Retention + purge controls for uploads, extracted text, results, logs; encrypt stored documents. |
| P0-4 | Move analysis to an async job queue; return 202; expose queued/running/completed/failed. |
| P0-5 | Pin dependencies; reproducible Docker/systemd deployment with health checks. |
| P1-1 | Full clause-coverage matrix; resolve every mapping status. |
| P1-2 | Lawyer-reviewed benchmark set by contract type/jurisdiction/language; measure precision, recall, false-missing rate. |
| P1-3 | Version scoring policies; display score version, confidence, limitations in every report. |
| P1-4 | Language-aware keyword matching; retain evidence spans for every finding. |
| P1-5 | Package or remove `legal_mlp.pkl`; no release may depend on a missing external desktop path. |
| P2-1 | Add a local translation model only after baseline gates pass. |
| P2-2 | Keep Qwen opt-in; it must never change findings, score, or citations. |

## 7. Recommended reporting format

Future daily reports: shorter, decision-oriented. Fixed sections — Objective
(one measurable goal), Change summary (files/modules + visible behavior),
Evidence (tests, fixtures, pass/fail, before/after, exact limits),
Security/privacy impact, Legal-data impact (dataset version, verification
status, jurisdiction, reviewer needed), Open risks, Decision required (explicit
questions for Patrick/Ilham), Next task (one task with acceptance criteria).

## 8. Final decision

Accept the engineering work as a strong prototype progression. Authorize
continued development and controlled internal/pilot testing. **Do not authorize
general paid production use until the P0 actions are closed and verified.**
Afridho continues as technical owner of the CRA backend, but all legal-source
activation, scoring-policy approval, and jurisdiction claims require a separate
legal/data approval step (Patrick/Ilham).
