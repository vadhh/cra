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
| **13 collision pairs — resolved** | ⛔ 7/13 unresolved (A-signal 9/13 correct as of 07-22 bugfixes; 6 pairs need Ilham's keyword-ownership call, `docs/legal_review_packet.md` §B) |
| **45-vs-42 detection-spec discrepancy** | ⛔ UNRECONCILED — see `docs/detection_spec_reconciliation_45_vs_42.md` (created today; registry shows 45/45 have a hypothesis+keyword spec, contradicting the "42" figure — needs Ilham's confirmation of his counting method) |

Evidence: `ldv-backend/tests/original11_corpus_report.json`, `ldv-backend/tests/collision_pairs_report.json`, `docs/legal_review_packet.md`.

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
| 2. Corpus validation | 🟡 Partial — 3 open items (risk-score review, 6 collision pairs, 45v42 reconciliation) |
| 3. Security validation | 🟡 Partial — hardening done, no formal audit |
| 4. Legal review | ⛔ Not started |
| 5. Controlled pilot acceptance | ⛔ Not started — blocked on 2–4 |

**`release/cra-1.0-rc1` remains unmerged to `master`.** No profile status changes in the registry until this matrix shows all 5 gates `Passed`/`Approved`.

---

## Owners for Remaining Work

- **Ilham:** risk-score ground truth review (§2 of `legal_review_packet.md`), collision-pair keyword-ownership decisions (§B), 45-vs-42 reconciliation confirmation, formal legal reviewer sign-off (Gate 4).
- **Afridho:** arrange/perform Gate 3 formal security validation; keep this matrix updated as each item closes.
- **Joint:** Gate 5 pilot-acceptance criteria and test plan, once Gates 2–4 close.
