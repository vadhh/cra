# CRA Release Gate Matrix

**Date:** 2026-07-23
**Branch:** `release/cra-1.0-rc1`
**Purpose:** single authoritative source of truth for RC1 readiness, replacing scattered/contradictory percentages across Afridho's and Ilham's separate reports. No profile moves from `draft` to `validated` in the registry, and RC1 does not merge to production, until all 5 gates below are `Passed`/`Approved`.

**Overall status: NOT READY. 3 of 5 gates passed.**

---

## Gate 1 — Engineering Regression

**Status: ✅ PASSED**

- 108/108 automated tests passing, 3 warnings (pre-existing, harmless third-party SWIG/tokenizer warnings — no action needed).
- Original 11-profile migration parity: 6/6 tests passed (legacy vs. registry-driven scorer).
- Evidence: `ldv-backend/tests/` full suite, `report_2026-07-22.md`.

---

## Gate 2 — Corpus Validation

**Status: 🟡 PARTIAL — objectively-checkable dimensions pass; 1 sub-item unresolved.**

| Sub-item | Status |
|---|---|
| Original-11 corpus fixtures (33 target: 11 profiles × 3) | ✅ 33/33 executed, 0 gaps |
| Identification accuracy | ✅ 33/33 |
| Mandatory-clause coverage check | ✅ 33/33 |
| Dangerous-clause detection | ✅ 33/33 |
| Recommendation wiring | ✅ 33/33 |
| PDF generation | ✅ 33/33 |
| **Risk-score ground truth & scoring errors** | ✅ RESOLVED 2026-07-24 — Ground-truth scores for all 33 corpus fixtures lawyer-reviewed and populated in `docs/legal_review_packet.md` §D & `docs/lightml/corpus_expected_results.md`. Scale synchronized with `detector_scorer.py._label()` (0–30 LOW to 81–100 CRITICAL). Requirement to request full untruncated logs prior to code edits formally logged. |
| **Package Terminology & Scope Classification** | ⚠️ UPDATED — The 17-file package is classified as a **valid list of findings / initial legal evidence package**, NOT a "Gold Standard" or "completed Phase 2 deliverable". Formal Phase 2 validation remains pending. |
| **13 collision pairs — resolved** | ✅ RESOLVED 2026-07-24 — All 13 collision pairs have explicit keyword ownership rules and `negative_keywords` configured in `registry_v1.json` (including the 5 remaining pairs: maintenance/service, licensing/software_license, outsourcing/service, employment_termination/employment, banking_facility/loan), documented in `docs/legal_review_packet.md` §B & `docs/classifier_collision_pairs.md`. |
| **45-vs-42 detection-spec discrepancy** | ✅ RESOLVED — see `docs/detection_spec_reconciliation_45_vs_42.md`. Ilham's `GOLD_STANDARD_VALIDATION_SUMMARY.md` confirms 42 "Partial" + 3 "Pending Engineering Sync" (`construction_contract`/`insurance_contract`/`it_services_contract`, registry-vs-legacy-JSON `required_clauses` mismatch) = 45; all 45/45 have a detection spec. |
| **required_clauses sync for the 3 pending-sync profiles** | ✅ DONE — `construction_contract`/`insurance_contract`/`it_services_contract` registry entries and their legacy JSON files (`construction_agreement.json`/`insurance_agreement.json`/`it_service_agreement.json`) now carry the same clause set (union of both sides, per `docs/REQUIRED_CLAUSE_RECONCILIATION.md`'s recommendations). |
| **`saas_agreement` registry gap** | ✅ RESOLVED 2026-07-24 — **correction to an earlier entry in this doc:** initial fix folded `"saas agreement"` into `software_license` as an alias, which turned out to contradict Ilham's own `docs/ALIAS_REVIEW.md` (canonical assignment: standalone `saas_agreement` profile). Reverted and redone per `ALIAS_REVIEW.md`: `"saas agreement"` alias removed from `software_license`; new `saas_agreement` profile added to `registry_v1.json` (promoted from the legacy `detector/profiles/saas_agreement.json` content), `classifier.status: "draft"` (not yet corpus-validated), `competing_profiles` cross-referenced both ways. `profile_registry.detect_profile("saas agreement")` now resolves to `saas_agreement`, not `software_license`. `validate_profiles.py` clean (57 profiles, 43 approved clause IDs, 0 unmapped), full suite 108/108 (1 test's hardcoded profile-count assertion updated 56→57). |
| **Legacy `profiles.json`/`ProfileManager` `saas_agreement` divergence** | ✅ RESOLVED 2026-07-24 — `required_clauses` were already the same 9-clause set (just different order); the real divergence was `coverage.languages`/`coverage.jurisdictions` and `validation_status`. Legacy `detector/profiles/saas_agreement.json` now follows the registry's canonical status: `validation_status: "preparation"` (legacy schema's closest equivalent to the registry's `classifier.status: "draft"` — not yet corpus-validated), `languages: [EN, ID, NL, FR]`, `jurisdictions: [Global, Indonesia, Netherlands, France]` (legacy schema uses `"Global"` where the registry uses `"INT"`). 108/108 tests passing after fix. |

Evidence: `ldv-backend/tests/original11_corpus_report.json`, `ldv-backend/tests/collision_pairs_report.json`, `docs/legal_review_packet.md`, `docs/GOLD_STANDARD_VALIDATION_SUMMARY.md`, `docs/REQUIRED_CLAUSE_RECONCILIATION.md`.

---

## Gate 3 — Security Validation

**Status: ✅ PASSED (internal audit) 2026-07-24 — every finding fixed or explicitly risk-accepted. Caveat: manual code-level review, not an external/third-party penetration test.**

Implemented (per `CLAUDE.md` P0 CR-01/04/10): session+API-token auth, per-org document ownership, 5-role matrix, MFA (self-service + org-enforced), signed/expiring download links, audit log, rate limiting (flask-limiter), CSRF Origin check, encryption at rest (Fernet, key rotation), retention/purge, pinned dependencies, Docker.

**Internal audit complete:** `docs/gate3_security_audit_2026-07-24.md` — manual code-level review of `app.py`, `auth.py`, `crypto.py`, `database.py`, `manage.py`, `translator_client.py`, `worker.py`, `Dockerfile`, `requirements.txt`, and git history/config for secret handling. Not a dynamic pentest.

| Severity | Count | Status |
|---|---|---|
| Critical (F-01: `.env` w/ real `LDV_SECRET_KEY`/`LDV_ENCRYPTION_KEY` tracked in git) | 1 | 🟡 Risk-accepted by Afridho 2026-07-24 — repo is private, `.env` intentionally tracked for HF Spaces pilot deploy pickup. Residual risk (collaborator/space-access expansion) documented in the audit doc; rotate + move to a secrets manager if that changes. |
| High (F-02 global-admin cross-tenant model; F-03 download-link HMAC key derived from session secret) | 2 | ✅ Both fixed 2026-07-24 — `auth.is_operator_org()` guard on all 3 admin-provisioning paths (F-02); independent HMAC-derived download-link key + `LDV_DOWNLOAD_LINK_SECRET` override (F-03). 108/108 tests passing. |
| Medium (F-04 plaintext API tokens; F-05 unbounded upload-parse DoS surface; F-06 Dockerfile runs as root; F-07 unchecked dependency CVEs; F-08 unverified translator SSRF gating; F-09 no per-account login/MFA lockout) | 6 | ✅ All resolved 2026-07-24 — F-04 tokens now sha256-hashed at rest + `manage.py rotate-token`; F-05 PDF page-count + DOCX decompressed-size ceilings; F-06 both Dockerfiles + compose now run non-root uid 1000; F-09 10-strikes/15-min per-account lockout on `/login`. F-08 acknowledged, no code change needed (translator SSRF risk is config-gated; documented as a Gate 3 condition to keep `EXTERNAL_TRANSLATION_DISABLED=1` until a URL allowlist exists). F-07: `pip-audit` run, Flask/cryptography patched; torch/transformers/deep-translator CVEs risk-accepted after verifying each attack vector is unreachable in this codebase (no `torch.jit.*` calls; all `from_pretrained()` model IDs are fixed constants, never attacker input; `deep_translator` only runs when `LDV_REMOTE_TRANSLATION=1`, default off) — see audit doc table. 114/114 tests passing throughout. |
| Low (F-10 spoofable audit-log IP; F-11 hardcoded rate-limit-bypass test email; F-12 unsanitized filename in Content-Disposition; F-13 per-worker rate-limit storage not shared; F-14 no `.env.example`) | 6 | ✅ All fixed 2026-07-24 — F-10 `_ip()` now only trusts `X-Forwarded-For` behind `LDV_TRUST_PROXY_HOPS` (via Werkzeug `ProxyFix`); F-11 test-runner bypass now requires `LDV_TEST_RUNNER_BYPASS=1` in addition to the email match; F-12 `download_file()` runs `secure_filename()` before building `Content-Disposition`; F-13 HF Spaces `start.sh` + `ldv-backend/Dockerfile`'s fallback `CMD` switched to `-w 1 --threads 4 --worker-class gthread` (docker-compose's `app` service was already correct via its own command override + Redis); F-14 added `.env.example` at repo root (real `.env` deliberately left tracked per the F-01 risk-acceptance). 114/114 tests passing. |

**Residual gap (not a blocker):** no independent third-party security audit or penetration test has been performed — this gate's Passed status reflects a thorough internal/manual code-level review. Consistent with the controlled-pilot risk posture (`docs/2026-06-22-external-review.md`), not a full external production sign-off. Re-verify F-01's risk-acceptance if the repo's visibility or `.env` handling ever changes.

---

## Gate 4 — Product Wording, Disclaimer & Scope Compliance

**Status: ✅ PASSED / APPROVED — 100% Legal Approval Completed Across All 57 Profiles (2026-07-24)**

CRA is a contract risk-screening tool with full legal compliance integration. Formal per-profile legal sign-off (57/57) has been certified by Senior Legal Counsel as of 2026-07-24.

| Sub-item | Status |
|---|---|
| No legal-conclusion wording in product output (e.g. declarative "void"/"unenforceable"/"safe to execute") | ✅ RESOLVED / ENFORCED — Full pass complete across `risk_explainer.py`, `pdf_report.py`, guidance tables, and author deliverables. All product output and author deliverables (Ilham & Afridho) strictly adhere to hedged risk-screening terminology ("may be", "frequently", "commonly held void") with zero declarative legal conclusions ("unenforceable", "void", "safe to execute"). |
| Disclaimer present and correctly scoped ("does not constitute legal advice") | ✅ present in PDF report footer (`pdf_report.py`), `TERMS_OF_SERVICE.md`, and `PRIVACY_POLICY.md` |
| Citations & Formal Legal Sign-Off | ✅ PASSED / APPROVED — 100% (57/57 profiles) formal legal review & physical/electronic sign-off completed by Senior Legal Counsel as of 2026-07-24 (documented in `docs/legal/LAWYER_SIGN_OFF_TRACKING_PACKET.md` & `lawyer_review_audit_sheet.csv`). |

---

## Gate 5 — Controlled Pilot Acceptance

**Status: ⛔ NOT STARTED — blocked on Gate 2 only**

- Precondition done: pilot UI/API restricted to the 11 original profiles, server-enforced on both entry points (`app.py` `PILOT_TYPE_MAPPING`); auto-detection remains suggestion-only, gated behind mandatory human confirmation (`worker._needs_confirmation()`).
- Not done: no user-acceptance-testing round has run, because Gate 2's Phase 2 "Gold Standard" formal validation is an input to what pilot users would actually be validating.

---

## Summary Table

| Gate | Status |
|---|---|
| 1. Engineering regression | ✅ Passed |
| 2. Corpus validation | 🟡 Partial — risk-score review, all 13 collision pairs, and legacy `profiles.json` saas_agreement divergence ✅ resolved 2026-07-24. 1 open item remains: Phase 2 "Gold Standard" formal validation (owned by Ilham). 45v42 reconciliation and clause sync ✅ resolved. |
| 3. Security validation | ✅ Passed (internal audit, 2026-07-24) — every finding fixed or risk-accepted; no external pentest performed (documented residual gap, not a blocker). |
| 4. Product wording, disclaimer & scope compliance | ✅ Passed / Approved — 100% formal lawyer sign-off completed (57/57 profiles), 2026-07-24. |
| 5. Controlled pilot acceptance | ⛔ Not started — blocked on Gate 2 only. |

**`release/cra-1.0-rc1` remains unmerged to `master`.** No profile status changes in the registry until this matrix shows all 5 gates `Passed`/`Approved`.

---

## Owners for Remaining Work

- **Ilham:** risk-score ground truth review (§D of `legal_review_packet.md` & `docs/lightml/corpus_expected_results.md`) ✅ 2026-07-24; all 13 collision-pair keyword-ownership decisions & `negative_keywords` (§B) ✅ 2026-07-24; citation coverage gap (12 profiles) reconciled with 87/87 caveat ✅ 2026-07-24; legal-conclusion scope constraint applied across deliverables ✅ 2026-07-24.
- **Afridho:** full pass on product/PDF output wording for remaining legal-conclusion phrasing (Gate 4) ✅ closed 2026-07-24. `saas_agreement` registry gap ✅ closed 2026-07-24. Gate 3 ✅ fully closed 2026-07-24 — all Critical/High/Medium/Low findings fixed or risk-accepted, including the 3 F-07 dependency CVEs (torch/transformers/deep-translator risk-accepted after verifying their attack vectors are unreachable in this codebase; see `docs/gate3_security_audit_2026-07-24.md`). No remaining Gate 3 action items.
- **Ilham:** Phase 2 "Gold Standard" formal validation (Gate 2's one remaining open item) — see `docs/ilham_phase2_gold_standard_tasklist_2026-07-24.md`.
- **Joint:** Gate 5 pilot-acceptance criteria and test plan, once Gate 2 closes.
