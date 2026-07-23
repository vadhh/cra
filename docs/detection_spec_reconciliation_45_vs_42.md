# Reconciliation: "45 partially usable profiles" vs "42 detection specifications"

**Date:** 2026-07-23 (opened) → 2026-07-23 (resolved)
**Author:** Engineering (Afridho), resolved using Ilham's `docs/GOLD_STANDARD_VALIDATION_SUMMARY.md` (merged into `staging`/`release/cra-1.0-rc1` same day)
**Status:** ✅ RESOLVED — see §"Resolution" below. Engineering follow-up (registry/JSON clause sync for 3 profiles) remains open, tracked separately.

---

## Resolution

Ilham's `docs/GOLD_STANDARD_VALIDATION_SUMMARY.md` §2 and §5 supply the exact math, independently of the registry-side audit below:

> | Complete Validation Records | 11 | 19.6% |
> | Partial Validation Records | 42 | 75.0% | Detection Spec available, pending active JSON & legal evidence MD. |
> | Profiles Pending Engineering Sync | 3 | 5.4% | Registry profiles (`construction_contract`, `insurance_contract`, `it_services_contract`) with engineering mismatches. |
> ...
> **Detection Specifications Verified**: 45 / 45 present

**11 + 42 + 3 = 56.** The "42" is not a subset lacking a detection spec — §6 confirms all **45/45** draft profiles have one, matching this document's own registry audit below. Instead, Ilham's workbook splits the 45 non-mature profiles into two buckets:

- **42 "Partial"** — have a detection spec, just missing the downstream active-JSON/legal-evidence artifacts (i.e., normal draft-profile status).
- **3 "Pending Engineering Sync"** — `construction_contract`, `insurance_contract`, `it_services_contract` — held out of the "Partial" bucket specifically because their legacy per-file JSON profile (`construction_agreement.json`, `insurance_agreement.json`, `it_service_agreement.json`) has a **different `required_clauses` list than the registry entry**. Full clause-level detail already existed in `docs/REQUIRED_CLAUSE_RECONCILIATION.md` (merged same batch): e.g. `construction_agreement.json` has `insurance`/`limitation_liability` that the registry lacks, while the registry has `delivery_terms` that the JSON lacks — same pattern for the other two.

This is the identical trio our own 07-22 engineering work (`report_2026-07-22.md` §2c) already found and partially fixed — those are the 3 profiles whose title-matching keyword branches (`_keyword_doc_type()`) were orphaned/misaligned with the registry's display names. **That fix resolved the classifier-routing symptom (a document titled "MAINTENANCE CONTRACT" now resolves correctly); it did not touch the underlying `required_clauses` schema mismatch Ilham is flagging**, which is a separate, still-open reconciliation between the legacy JSON profile files and `registry_v1.json`.

A 4th artifact, `saas_agreement.json`, is called out in the same table but doesn't affect the 45/42/3 math — Ilham maps it as an implementation variant under the already-mature `software_license` profile, not a 57th profile or a member of the 45.

**Follow-up (separate from this reconciliation, not yet done):** synchronize `required_clauses` between the 3 legacy JSON files and `registry_v1.json` per `docs/REQUIRED_CLAUSE_RECONCILIATION.md`'s per-clause recommendations, and add a `saas_agreement` registry entry (or confirm the `software_license` variant mapping) as recommended there.

---

## Original engineering-side audit (superseded by the resolution above, kept for reference)

## What the registry actually shows today

`ldv-backend/detector/profiles/registry_v1.json` (unchanged since the P2 commit `9164835`, which predates this week's bugfixes) contains **56 profiles: 11 `validated`, 45 `draft`**. Querying the registry directly for classifier-spec completeness on all 45 draft profiles:

| Field | Present on how many of the 45 |
|---|---|
| `classifier.hypothesis` (non-empty) | **45 / 45** |
| `classifier.positive_keywords` (non-empty) | **45 / 45** |
| `classifier.negative_keywords` (non-empty) | **0 / 45** |
| `classifier.competing_profiles` (non-empty) | **13 / 45** |

By the most literal reading of "detection specification present" (a hypothesis + keyword set exists), the registry says **45/45, not 42/45** — there is no gap to reconcile on that metric, and it hasn't changed recently (no registry edits since P2).

This means one of two things is true, and only Ilham can say which:

1. **His "42" used a stricter definition** — e.g. a spec only "counts" if it also has `negative_keywords` for disambiguation (0/45 currently qualify under that bar, which would make the real number 0, not 42) or is free of collision risk (43/45 have no `competing_profiles` entry, which would make it 43, not 42).
2. **His "42" was a snapshot from before P2 landed**, and the registry has since caught up — in which case the discrepancy is already closed and just needs the wording updated in his report.

## Full 45-profile audit (input for his reconciliation table)

| Profile ID | Display Name | Hypothesis | Keywords | Negative Keywords | Competing Profiles Documented |
|---|---|:---:|:---:|:---:|:---:|
| distribution_agreement | Distribution Agreement | Y | Y | N | Y |
| franchise_agreement | Franchise Agreement | Y | Y | N | N |
| supply_agreement | Supply Agreement | Y | Y | N | Y |
| agency_agreement | Agency Agreement | Y | Y | N | Y |
| shareholder_agreement | Shareholder Agreement | Y | Y | N | N |
| investment_agreement | Investment Agreement | Y | Y | N | N |
| construction_contract | Construction Contract | Y | Y | N | N |
| maintenance_contract | Maintenance Contract | Y | Y | N | Y |
| it_services_contract | IT Services Contract | Y | Y | N | Y |
| data_processing_agreement | Data Processing Agreement | Y | Y | N | N |
| intellectual_property_assignment | Intellectual Property Assignment | Y | Y | N | N |
| licensing_agreement | Licensing Agreement | Y | Y | N | Y |
| joint_venture_agreement | Joint Venture Agreement | Y | Y | N | Y |
| memorandum_of_understanding | Memorandum of Understanding | Y | Y | N | N |
| subcontract_agreement | Subcontract Agreement | Y | Y | N | N |
| grant_agreement | Grant Agreement | Y | Y | N | N |
| settlement_agreement | Settlement Agreement | Y | Y | N | N |
| sponsorship_agreement | Sponsorship Agreement | Y | Y | N | N |
| event_contract | Event Contract | Y | Y | N | N |
| property_management_agreement | Property Management Agreement | Y | Y | N | N |
| insurance_contract | Insurance Contract / Policy | Y | Y | N | N |
| escrow_agreement | Escrow Agreement | Y | Y | N | N |
| outsourcing_agreement | Outsourcing Agreement | Y | Y | N | Y |
| employment_termination_agreement | Employment Termination Agreement | Y | Y | N | Y |
| sales_representative_agreement | Sales Representative Agreement | Y | Y | N | Y |
| freelance_contract | Freelance / Independent Contractor Agreement | Y | Y | N | Y |
| internship_agreement | Internship Agreement | Y | Y | N | N |
| facilities_management_agreement | Facilities Management Agreement | Y | Y | N | N |
| logistics_agreement | Logistics / Freight Agreement | Y | Y | N | N |
| media_production_agreement | Media Production Agreement | Y | Y | N | N |
| advertising_agreement | Advertising Agreement | Y | Y | N | N |
| cooperation_agreement | Cooperation Agreement | Y | Y | N | Y |
| export_import_agreement | Export / Import Agreement | Y | Y | N | N |
| land_acquisition_agreement | Land Acquisition Agreement | Y | Y | N | N |
| hotel_management_agreement | Hotel Management Agreement | Y | Y | N | N |
| healthcare_services_agreement | Healthcare Services Agreement | Y | Y | N | N |
| education_services_agreement | Education Services Agreement | Y | Y | N | N |
| energy_supply_agreement | Energy Supply Agreement | Y | Y | N | N |
| mining_agreement | Mining / Natural Resources Agreement | Y | Y | N | N |
| telecommunications_agreement | Telecommunications Agreement | Y | Y | N | N |
| banking_facility_agreement | Banking Facility Agreement | Y | Y | N | Y |
| factoring_agreement | Factoring Agreement | Y | Y | N | N |
| storage_agreement | Storage / Warehousing Agreement | Y | Y | N | N |
| research_collaboration_agreement | Research Collaboration Agreement | Y | Y | N | N |
| government_procurement_contract | Government Procurement Contract | Y | Y | N | N |

## Status

The 45-vs-42 counting discrepancy itself is closed (see Resolution above). The one item still open is engineering, not a reconciliation question: sync `required_clauses` for `construction_contract`/`insurance_contract`/`it_services_contract` between the legacy JSON files and the registry, plus resolve the `saas_agreement` registry gap. Tracked in `docs/CRA_RELEASE_GATE_MATRIX.md` Gate 2.
