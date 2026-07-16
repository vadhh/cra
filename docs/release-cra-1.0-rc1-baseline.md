# CRA 1.0-rc1 Baseline Freeze

**Date:** 2026-07-16
**Reason:** Management review (see project memory `ldv-56-profile-review-2026-07-16`) rejected the "56 profiles legally approved / production-ready" claim in `docs/p7_catalogue_reconciliation.md` and `docs/report_2026-07-15.md`. `master`/`staging` are now frozen as an integration baseline, not a production release, pending the legal-validation matrix and outstanding release gates (corpus testing, report/PDF parity, translator integration, deployment gates).

## Freeze artifacts

| Artifact | Value |
|---|---|
| Backup tag | `backup/2026-07-16-pre-rc1` |
| RC branch | `release/cra-1.0-rc1` |
| Frozen commit | `50f7270` — "docs: daily engineering report 2026-07-15" (staging == master at freeze time) |
| DB + uploads backup | `~/ldv-backups/20260716T062227Z/` (local dev backup; `LDV_BACKUP_DIR` unset defaults to `/var/backups/ldv` which needs root on this box) |
| `registry_v1.json` SHA-256 | `2a9b3c057cb884bfa8b07a3c76841e44bc58fbe56b27f338a54c777300a48284` |

## Status at freeze (corrected, per management review)

- 56 profiles registered; **11 fully wired** (classifier + profile + scorer + PDF); **45 partially wired** (registry/clause mappings exist, automatic classification incomplete); **0 name-only**.
- Legally approved: **not established** — requires a profile-by-profile validation matrix (`docs/CRA_56_PROFILE_LEGAL_VALIDATION.xlsx`, pending from Ilham).
- Production-ready: **not established** — corpus testing (56×3 fixtures), report/PDF parity tests, translator-integration validation, and deployment verification are still outstanding.

## Next commits should go to

`release/cra-1.0-rc1` (or a feature branch merged into it) until the mandated priorities in the management review are closed. Do not describe further `master` merges as a "production release" until the release gates above are checked off.
