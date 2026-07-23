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
| **Risk-score ground truth** | ⛔ PENDING — 0/33 lawyer-reviewed; `docs/legal_review_packet.md` §D has actual scores staged for review, unreviewed |
| **13 collision pairs — resolved** | 🟡 1/6 remaining pairs closed by Ilham's `docs/ALIAS_REVIEW.md` (`joint_venture_agreement` vs `partnership_agreement` — matches our proposed fix); **5 pairs still need Ilham's keyword-ownership call** (maintenance/service, licensing/software_license, outsourcing/service, employment_termination/employment, banking_facility/loan), `docs/legal_review_packet.md` §B |
| **45-vs-42 detection-spec discrepancy** | ✅ RESOLVED — see `docs/detection_spec_reconciliation_45_vs_42.md`. Ilham's `GOLD_STANDARD_VALIDATION_SUMMARY.md` confirms 42 "Partial" + 3 "Pending Engineering Sync" (`construction_contract`/`insurance_contract`/`it_services_contract`, registry-vs-legacy-JSON `required_clauses` mismatch) = 45; all 45/45 have a detection spec. Follow-up clause-sync work is still open, tracked below. |

**New follow-up from the 45-vs-42 resolution:** sync `required_clauses` between the 3 legacy per-file JSON profiles (`construction_agreement.json`, `insurance_agreement.json`, `it_service_agreement.json`) and their registry entries, per `docs/REQUIRED_CLAUSE_RECONCILIATION.md`'s per-clause recommendations, and resolve the `saas_agreement` registry gap (currently unmapped; Ilham recommends treating it as a `software_license` variant). Not yet done.

Evidence: `ldv-backend/tests/original11_corpus_report.json`, `ldv-backend/tests/collision_pairs_report.json`, `docs/legal_review_packet.md`, `docs/GOLD_STANDARD_VALIDATION_SUMMARY.md`, `docs/REQUIRED_CLAUSE_RECONCILIATION.md`.

---

## Gate 3 — Security Validation

**Status: 🟡 PARTIAL — hardening implemented in code; no formal audit performed.**

Implemented (per `CLAUDE.md` P0 CR-01/04/10): session+API-token auth, per-org document ownership, 5-role matrix, MFA (self-service + org-enforced), signed/expiring download links, audit log, rate limiting (flask-limiter), CSRF Origin check, encryption at rest (Fernet, key rotation), retention/purge, pinned dependencies, Docker.

**Not done:** no independent security audit, penetration test, or formal sign-off exists. `ldv-backend/tests/security_validator.py` is a one-function test helper (fetches an auth token), not a validation suite. This gate cannot be marked `Passed` on code-hardening alone — it requires an actual security review pass, internal or third-party.

---

## Gate 4 — Legal Review

**Status: ⛔ NOT STARTED**

- `docs/legal_review_packet.md` created 07-22 as the single lawyer sign-off entry point (6 sections: profile validation, collision-pair ownership, clause-severity sign-off, risk-score ground truth, recommendation-wording spot-check, citations).
- Citations: 87/87 already `verified` — no action needed there.
- Everything else in the packet: sign-off checkbox unchecked, reviewer field blank, 0/56 profiles formally approved.
- **Formal legal approval: 0/56. Repository-supported evidence package prepared: 11/56 (the validated profiles) — evidence prepared is not approval.**

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
| 2. Corpus validation | 🟡 Partial — 2 open items (risk-score review, 5 collision pairs). 45v42 reconciliation ✅ resolved; clause-sync follow-up open. |
| 3. Security validation | 🟡 Partial — hardening done, no formal audit |
| 4. Legal review | ⛔ Not started |
| 5. Controlled pilot acceptance | ⛔ Not started — blocked on 2–4 |

**`release/cra-1.0-rc1` remains unmerged to `master`.** No profile status changes in the registry until this matrix shows all 5 gates `Passed`/`Approved`.

---

## Owners for Remaining Work

- **Ilham:** risk-score ground truth review (§2 of `legal_review_packet.md`), 5 remaining collision-pair keyword-ownership decisions (§B), formal legal reviewer sign-off (Gate 4).
- **Afridho:** sync `required_clauses` for the 3 pending-engineering-sync profiles + resolve `saas_agreement` registry gap; arrange/perform Gate 3 formal security validation; keep this matrix updated as each item closes.
- **Joint:** Gate 5 pilot-acceptance criteria and test plan, once Gates 2–4 close.
