# Ilham — Phase 2 "Gold Standard" Task List

**Date:** 2026-07-24
**Source:** `docs/GOLD_STANDARD_VALIDATION_SUMMARY.md` (07-23 audit) + Gate 2 open item in `docs/CRA_RELEASE_GATE_MATRIX.md`
**Why this exists:** the 07-23 package was reclassified as a "valid list of findings / initial legal evidence package," not a completed Phase 2 "Gold Standard" deliverable. This is the punch list to actually close that gap. Not a release blocker for RC1 — the gate matrix only requires this be tracked, not finished.

---

## 1. Bring 42 "Partial" profiles to "Complete"

Per the family-coverage table, 42/56 registry profiles have a detection spec but are missing:
- an **active engineering JSON** file, and
- a **legal evidence Markdown** doc

Only 11 profiles currently have both (+ verified rules). Breakdown by family:

| Family | Partial profiles remaining |
|---|---|
| Commercial & Service Agreements | 18 |
| Corporate & Finance Agreements | 14 |
| Property & Real Estate Agreements | 4 |
| Labor & HR Agreements | 4 |
| Baseline & General Contracts | 2 |

For each: write the active JSON profile + legal evidence MD, same shape as the 11 already-complete profiles.

## 2. Formal legal sign-off — 52/56 profiles pending

Only 4/56 profiles currently have a completed physical legal sign-off. Get lawyer review + sign-off on the remaining 52, prioritized by family coverage above (commercial/corporate first — largest volume).

## 3. Fix the stale `saas_agreement` engineering-artifact mapping

`GOLD_STANDARD_VALIDATION_SUMMARY.md` §5 still says:

> `saas_agreement.json` → `software_license` — "Implementation Variant, map as specialized SaaS variant under `software_license`"

This contradicts your own `ALIAS_REVIEW.md` and the registry fix already shipped 2026-07-24: `saas_agreement` is now a **standalone** registry profile, not a `software_license` variant. Update this row (and the "56 registry profiles" count, which is now 57) so the Gold Standard doc doesn't drift from `registry_v1.json` again.

## 4. Re-issue the terminology/scope classification once the above lands

Once profiles are materially complete and lawyer-signed, the package can legitimately be re-labeled from "initial legal evidence package" to "Gold Standard" / "completed Phase 2 deliverable" — don't re-apply that label before then.

---

**Not in scope here** (already closed 2026-07-24, tracked separately in the gate matrix): risk-score ground truth review, all 13 collision pairs, citation coverage reconciliation, legal-conclusion wording pass, legacy `profiles.json` saas_agreement divergence.
