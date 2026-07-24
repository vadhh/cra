# CRA Release Gate Matrix

**Date:** 2026-07-23
**Branch:** `release/cra-1.0-rc1`
**Purpose:** single authoritative source of truth for RC1 readiness, replacing scattered/contradictory percentages across Afridho's and Ilham's separate reports. No profile moves from `draft` to `validated` in the registry, and RC1 does not merge to production, until all 5 gates below are `Passed`/`Approved`.

**Overall status: NOT READY. 1 of 5 gates passed.**

---

## Gate 1 — Engineering Regression

**Status: ✅ PASSED**

- 108/108 automated tests passing, 3 warnings (pre-existing, harmless third-party SWIG/tokenizer warnings — no action needed).
- Original 11-profile migration parity: 6/6 tests passed (legacy vs. registry-driven scorer).
- Evidence: `ldv-backend/tests/` full suite, `report_2026-07-22.md`.

---

## Gate 2 — Corpus Validation

**Status: 🟡 PARTIAL — objectively-checkable dimensions pass; 3 sub-items unresolved.**

| Sub-item | Status |
|---|---|
| Original-11 corpus fixtures (33 target: 11 profiles × 3) | ✅ 33/33 executed, 0 gaps |
| Identification accuracy | ✅ 33/33 |
| Mandatory-clause coverage check | ✅ 33/33 |
| Dangerous-clause detection | ✅ 33/33 |
| Recommendation wiring | ✅ 33/33 |
| PDF generation | ✅ 33/33 |
| **Risk-score ground truth & scoring errors** | ⛔ PENDING — 0/33 lawyer-reviewed; review feedback on "critical scoring error" was truncated. **Action required:** request full untruncated details from reviewer before attempting code changes. |
| **Package Terminology & Scope Classification** | ⚠️ UPDATED — The 17-file package is classified as a **valid list of findings / initial legal evidence package**, NOT a "Gold Standard" or "completed Phase 2 deliverable". Formal Phase 2 validation remains pending. |
| **13 collision pairs — resolved** | 🟡 `docs/ALIAS_REVIEW.md`'s 4 alias-collision renames (`saas agreement`, `joint venture agreement`, `perjanjian kerjasama`, `samenwerkingsovereenkomst`) applied to `registry_v1.json` 2026-07-24 — see `saas_agreement` row below; `joint_venture_agreement` vs `partnership_agreement` and `cooperation_agreement` vs `partnership_agreement` (pairs #7, #12) now cleanly disambiguated. **5 pairs still need Ilham's keyword-ownership call** (maintenance/service, licensing/software_license, outsourcing/service, employment_termination/employment, banking_facility/loan), `docs/legal_review_packet.md` §B / `docs/classifier_collision_pairs.md` |
| **45-vs-42 detection-spec discrepancy** | ✅ RESOLVED — see `docs/detection_spec_reconciliation_45_vs_42.md`. Ilham's `GOLD_STANDARD_VALIDATION_SUMMARY.md` confirms 42 "Partial" + 3 "Pending Engineering Sync" (`construction_contract`/`insurance_contract`/`it_services_contract`, registry-vs-legacy-JSON `required_clauses` mismatch) = 45; all 45/45 have a detection spec. |
| **required_clauses sync for the 3 pending-sync profiles** | ✅ DONE — `construction_contract`/`insurance_contract`/`it_services_contract` registry entries and their legacy JSON files (`construction_agreement.json`/`insurance_agreement.json`/`it_service_agreement.json`) now carry the same clause set (union of both sides, per `docs/REQUIRED_CLAUSE_RECONCILIATION.md`'s recommendations). |
| **`saas_agreement` registry gap** | ✅ RESOLVED 2026-07-24 — **correction to an earlier entry in this doc:** initial fix folded `"saas agreement"` into `software_license` as an alias, which turned out to contradict Ilham's own `docs/ALIAS_REVIEW.md` (canonical assignment: standalone `saas_agreement` profile). Reverted and redone per `ALIAS_REVIEW.md`: `"saas agreement"` alias removed from `software_license`; new `saas_agreement` profile added to `registry_v1.json` (promoted from the legacy `detector/profiles/saas_agreement.json` content), `classifier.status: "draft"` (not yet corpus-validated), `competing_profiles` cross-referenced both ways. `profile_registry.detect_profile("saas agreement")` now resolves to `saas_agreement`, not `software_license`. `validate_profiles.py` clean (57 profiles, 43 approved clause IDs, 0 unmapped), full suite 108/108 (1 test's hardcoded profile-count assertion updated 56→57). |
| **Legacy `profiles.json`/`ProfileManager` `saas_agreement` divergence** | 🟡 OPEN, low priority — `profiles.json`'s standalone legacy `saas_agreement` entry (used only by the registry-load fallback path + admin CRUD screens, not live `/analyze`) still has a slightly different clause set than the new registry profile. Owner: Afridho/Ilham joint call on reconciling or retiring it. Not a release blocker. |

Evidence: `ldv-backend/tests/original11_corpus_report.json`, `ldv-backend/tests/collision_pairs_report.json`, `docs/legal_review_packet.md`, `docs/GOLD_STANDARD_VALIDATION_SUMMARY.md`, `docs/REQUIRED_CLAUSE_RECONCILIATION.md`.

---

## Gate 3 — Security Validation

**Status: 🟡 PARTIAL — internal code-level audit performed 2026-07-24; critical/high/most-medium findings closed, low findings + 3 dependency CVEs remain.**

Implemented (per `CLAUDE.md` P0 CR-01/04/10): session+API-token auth, per-org document ownership, 5-role matrix, MFA (self-service + org-enforced), signed/expiring download links, audit log, rate limiting (flask-limiter), CSRF Origin check, encryption at rest (Fernet, key rotation), retention/purge, pinned dependencies, Docker.

**Internal audit complete:** `docs/gate3_security_audit_2026-07-24.md` — manual code-level review of `app.py`, `auth.py`, `crypto.py`, `database.py`, `manage.py`, `translator_client.py`, `worker.py`, `Dockerfile`, `requirements.txt`, and git history/config for secret handling. Not a dynamic pentest.

| Severity | Count | Status |
|---|---|---|
| Critical (F-01: `.env` w/ real `LDV_SECRET_KEY`/`LDV_ENCRYPTION_KEY` tracked in git) | 1 | 🟡 Risk-accepted by Afridho 2026-07-24 — repo is private, `.env` intentionally tracked for HF Spaces pilot deploy pickup. Residual risk (collaborator/space-access expansion) documented in the audit doc; rotate + move to a secrets manager if that changes. |
| High (F-02 global-admin cross-tenant model; F-03 download-link HMAC key derived from session secret) | 2 | ✅ Both fixed 2026-07-24 — `auth.is_operator_org()` guard on all 3 admin-provisioning paths (F-02); independent HMAC-derived download-link key + `LDV_DOWNLOAD_LINK_SECRET` override (F-03). 108/108 tests passing. |
| Medium (F-04 plaintext API tokens; F-05 unbounded upload-parse DoS surface; F-06 Dockerfile runs as root; F-07 unchecked dependency CVEs; F-08 unverified translator SSRF gating; F-09 no per-account login/MFA lockout) | 6 | ✅ 4 fixed 2026-07-24 (F-04 tokens now sha256-hashed at rest + `manage.py rotate-token`; F-05 PDF page-count + DOCX decompressed-size ceilings; F-06 both Dockerfiles + compose now run non-root uid 1000; F-09 10-strikes/15-min per-account lockout on `/login`). F-08 acknowledged, no code change needed (translator SSRF risk is config-gated; documented as a Gate 3 condition to keep `EXTERNAL_TRANSLATION_DISABLED=1` until a URL allowlist exists). F-07 partial: `pip-audit` run, Flask/cryptography patched; torch/transformers/deep-translator CVEs need an owner decision (scheduled major-version bump + regression pass, or risk-accept) — see audit doc table. 108/108 tests passing throughout. |
| Low (spoofable audit-log IP; hardcoded rate-limit-bypass test email; unsanitized filename in Content-Disposition; per-worker rate-limit storage not shared; no `.env.example`) | 6 | ⛔ Open |

**Not done:** no independent third-party security audit or penetration test. This gate cannot move to `Passed` until the 3 open F-07 dependency-CVE decisions and the 6 Low-severity items are fixed or explicitly risk-accepted (same treatment as F-01/F-02/F-03).

---

## Gate 4 — Product Wording, Disclaimer & Scope Compliance

**Status: 🟡 PARTIAL — scope clarified 2026-07-24; wording fixes in progress.**

CRA is a contract risk-screening tool, not a legal-opinion engine. It identifies missing, dangerous, abusive, or unbalanced clauses and calculates risk scores — it does not certify enforceability, and its recommendations do not replace legal counsel. Formal per-profile legal sign-off (0/56) is **not** a release blocker; this gate instead checks that the product doesn't claim to be something it isn't.

| Sub-item | Status |
|---|---|
| No legal-conclusion wording in product output (e.g. declarative "void"/"unenforceable"/"safe to execute") | ✅ RESOLVED / ENFORCED — Full pass complete across `risk_explainer.py`, `pdf_report.py`, guidance tables, and author deliverables. All product output and author deliverables (Ilham & Afridho) strictly adhere to hedged risk-screening terminology ("may be", "frequently", "commonly held void") with zero declarative legal conclusions ("unenforceable", "void", "safe to execute"). |
| Disclaimer present and correctly scoped ("does not constitute legal advice") | ✅ present in PDF report footer (`pdf_report.py`) |
| Citations traceability | ✅ RECONCILED WITH CAVEAT — 87/87 existing database rows in `legal_citations.csv` are marked `verified`. **Caveat:** 87/87 applies strictly to existing DB row integrity, not 100% profile coverage. 12 registry profiles still have required clauses lacking matching statutory citations (logged as "Evidence Not Found" in gap tracker). |

Superseded framing: `docs/legal_review_packet.md` (07-22) was built as a lawyer sign-off entry point under the prior Gate 4 mandate (07-17 review). Its non-legal sections (collision-pair ownership §B, risk-score ground truth §D, recommendation-wording spot-check) remain useful engineering/product inputs; its sign-off checkbox/reviewer-field mechanism is no longer a release requirement.

---

## Gate 5 — Controlled Pilot Acceptance

**Status: ⛔ NOT STARTED — blocked on Gates 2–4**

- Precondition done: pilot UI/API restricted to the 11 original profiles, server-enforced on both entry points (`app.py` `PILOT_TYPE_MAPPING`); auto-detection remains suggestion-only, gated behind mandatory human confirmation (`worker._needs_confirmation()`).
- Not done: no user-acceptance-testing round has run, because Gates 2–4 (risk-score ground truth, collision-pair decisions, legal sign-off) are inputs to what pilot users would actually be validating.

---

## Summary Table

| Gate | Status |
|---|---|
| 1. Engineering regression | ✅ Passed |
| 2. Corpus validation | 🟡 Partial — 2 open items (risk-score review, 5 collision pairs). 45v42 reconciliation and clause sync ✅ resolved. |
| 3. Security validation | 🟡 Partial — internal audit done 2026-07-24; 1 critical risk-accepted, 2 high fixed, 4/6 medium fixed + 1 acknowledged + 1 partial (3 CVEs need owner decision), 6 low open |
| 4. Product wording, disclaimer & scope compliance | 🟡 Partial — wording audit in progress |
| 5. Controlled pilot acceptance | ⛔ Not started — blocked on 2–4 |

**`release/cra-1.0-rc1` remains unmerged to `master`.** No profile status changes in the registry until this matrix shows all 5 gates `Passed`/`Approved`.

---

## Owners for Remaining Work

- **Ilham:** risk-score ground truth review (§2 of `legal_review_packet.md`) and corresponding fix to the reversed scale in `docs/lightml/corpus_expected_results.md`; 5 remaining collision-pair keyword-ownership decisions (§B); citation coverage gap (12 profiles) reconciled with 87/87 caveat ✅ 2026-07-24; legal-conclusion scope constraint applied across deliverables ✅ 2026-07-24.
- **Afridho:** full pass on product/PDF output wording for remaining legal-conclusion phrasing (Gate 4) ✅ closed 2026-07-24; decide on the 3 open F-07 dependency CVEs (torch/transformers scheduled bump + regression pass, or risk-accept; deep-translator risk-accept given it's disabled by default) and triage the 6 Low findings in `docs/gate3_security_audit_2026-07-24.md`; keep this matrix updated as each item closes. `saas_agreement` registry gap ✅ closed 2026-07-24. Gate 3 High findings (F-02, F-03) and 4/6 Medium findings (F-04, F-05, F-06, F-09) ✅ fixed 2026-07-24; F-08 acknowledged, no action needed unless `LDV_REMOTE_TRANSLATION=local` is turned on.
- **Joint:** Gate 5 pilot-acceptance criteria and test plan, once Gates 2–4 close.
