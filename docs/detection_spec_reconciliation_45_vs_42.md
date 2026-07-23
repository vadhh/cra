# Reconciliation: "45 partially usable profiles" vs "42 detection specifications"

**Date:** 2026-07-23
**Author:** Engineering (Afridho)
**Status:** ENGINEERING-SIDE INPUT ONLY — not a resolution. The "42" figure originates in Ilham's report, which is not in this repository; engineering cannot reconstruct his counting method or confirm which 3 profiles he excluded. This document supplies the objective data his reconciliation needs.

---

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

## Ask for Ilham

Given the registry data above, please confirm:
1. What definition of "detection specification" produced your 42 figure?
2. Which 3 (of the 45) did you exclude, and why?
3. Does your 42 need updating to reflect the current registry state, or does engineering need to add a stricter field (e.g. `negative_keywords`) before a profile should count as "spec complete"?

Until this is answered, **the CRA Release Gate Matrix (`docs/CRA_RELEASE_GATE_MATRIX.md`) records Gate 2 as not fully closed** — this reconciliation is one of its listed blockers, not a resolved item.
