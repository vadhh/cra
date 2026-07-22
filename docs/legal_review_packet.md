# CRA Legal Review Packet

**Purpose:** single entry point for everything currently blocked on a licensed lawyer's judgment before CRA can move beyond the controlled-pilot phase. This maps to Gate 4 ("legal review") of the CRA Release Gate Matrix (`CLAUDE.md` TODO, external review 2026-06-22/2026-07-17).

**This document contains no legal opinions.** All facts below are engineering-verifiable (registry status, test counts, file locations). Every decision field is left blank for a named reviewer to complete — nothing here is pre-filled or assumed. Per the 2026-07-17 external review: legal approval is currently **0/56** profiles; nothing in this packet should be read as changing that until a reviewer actually signs a section below.

**How to use this packet:** each section below is one class of open legal decision. For each, review the referenced source file(s) — not this document alone, which only indexes and summarizes — and fill in Reviewer / Date / Decision. Sections are independent; a lawyer can complete them in any order or split across reviewers.

---

## A. Contract-profile validation (56 profiles)

Every profile's required-clause set, jurisdiction coverage, and clause guidance needs a named reviewer's sign-off before it can move from `draft` to `validated` status in `detector/profiles/registry_v1.json`. **11 profiles are already `validated`** and in the controlled pilot (manual-selection only, per 2026-07-21) — even those have not had a *formal* legal sign-off recorded; "validated" here is an engineering/pilot-readiness status, not a legal-approval status.

Source to review per profile: `detector/profiles/registry_v1.json` (required clauses, jurisdictions), `datasets/required_clauses_MASTER.csv` (clause guidance/rationale, filter by `Contract_Type`).

| # | Profile ID | Display Name | Engineering Status | Required Clauses | Reviewer | Review Date | Decision |
|---|---|---|---|---|---|---|---|
| 1 | `commercial_agreement` | Commercial Agreement | ✅ validated (pilot) | 6 | | | ☐ Approve ☐ Revise ☐ Reject |
| 2 | `consulting_agreement` | Consulting Agreement | ✅ validated (pilot) | 7 | | | ☐ Approve ☐ Revise ☐ Reject |
| 3 | `employment_contract` | Employment Contract | ✅ validated (pilot) | 7 | | | ☐ Approve ☐ Revise ☐ Reject |
| 4 | `general_contract` | General Contract | ✅ validated (pilot) | 6 | | | ☐ Approve ☐ Revise ☐ Reject |
| 5 | `lease_agreement` | Lease Agreement | ✅ validated (pilot) | 8 | | | ☐ Approve ☐ Revise ☐ Reject |
| 6 | `loan_agreement` | Loan Agreement | ✅ validated (pilot) | 8 | | | ☐ Approve ☐ Revise ☐ Reject |
| 7 | `non_disclosure_agreement` | Non-Disclosure Agreement | ✅ validated (pilot) | 6 | | | ☐ Approve ☐ Revise ☐ Reject |
| 8 | `partnership_agreement` | Partnership Agreement | ✅ validated (pilot) | 7 | | | ☐ Approve ☐ Revise ☐ Reject |
| 9 | `purchase_agreement` | Purchase Agreement | ✅ validated (pilot) | 8 | | | ☐ Approve ☐ Revise ☐ Reject |
| 10 | `service_agreement` | Service Agreement | ✅ validated (pilot) | 7 | | | ☐ Approve ☐ Revise ☐ Reject |
| 11 | `software_license` | Software License Agreement | ✅ validated (pilot) | 8 | | | ☐ Approve ☐ Revise ☐ Reject |
| 12 | `advertising_agreement` | Advertising Agreement | ⚪ draft | 7 | | | ☐ Approve ☐ Revise ☐ Reject |
| 13 | `agency_agreement` | Agency Agreement | ⚪ draft | 6 | | | ☐ Approve ☐ Revise ☐ Reject |
| 14 | `banking_facility_agreement` | Banking Facility Agreement | ⚪ draft | 8 | | | ☐ Approve ☐ Revise ☐ Reject |
| 15 | `construction_contract` | Construction Contract | ⚪ draft | 9 | | | ☐ Approve ☐ Revise ☐ Reject |
| 16 | `cooperation_agreement` | Cooperation Agreement | ⚪ draft | 5 | | | ☐ Approve ☐ Revise ☐ Reject |
| 17 | `data_processing_agreement` | Data Processing Agreement | ⚪ draft | 5 | | | ☐ Approve ☐ Revise ☐ Reject |
| 18 | `distribution_agreement` | Distribution Agreement | ⚪ draft | 7 | | | ☐ Approve ☐ Revise ☐ Reject |
| 19 | `education_services_agreement` | Education Services Agreement | ⚪ draft | 6 | | | ☐ Approve ☐ Revise ☐ Reject |
| 20 | `employment_termination_agreement` | Employment Termination Agreement | ⚪ draft | 6 | | | ☐ Approve ☐ Revise ☐ Reject |
| 21 | `energy_supply_agreement` | Energy Supply Agreement | ⚪ draft | 8 | | | ☐ Approve ☐ Revise ☐ Reject |
| 22 | `escrow_agreement` | Escrow Agreement | ⚪ draft | 5 | | | ☐ Approve ☐ Revise ☐ Reject |
| 23 | `event_contract` | Event Contract | ⚪ draft | 7 | | | ☐ Approve ☐ Revise ☐ Reject |
| 24 | `export_import_agreement` | Export / Import Agreement | ⚪ draft | 8 | | | ☐ Approve ☐ Revise ☐ Reject |
| 25 | `facilities_management_agreement` | Facilities Management Agreement | ⚪ draft | 7 | | | ☐ Approve ☐ Revise ☐ Reject |
| 26 | `factoring_agreement` | Factoring Agreement | ⚪ draft | 7 | | | ☐ Approve ☐ Revise ☐ Reject |
| 27 | `franchise_agreement` | Franchise Agreement | ⚪ draft | 7 | | | ☐ Approve ☐ Revise ☐ Reject |
| 28 | `freelance_contract` | Freelance / Independent Contractor Agreement | ⚪ draft | 7 | | | ☐ Approve ☐ Revise ☐ Reject |
| 29 | `government_procurement_contract` | Government Procurement Contract | ⚪ draft | 9 | | | ☐ Approve ☐ Revise ☐ Reject |
| 30 | `grant_agreement` | Grant Agreement | ⚪ draft | 5 | | | ☐ Approve ☐ Revise ☐ Reject |
| 31 | `healthcare_services_agreement` | Healthcare Services Agreement | ⚪ draft | 8 | | | ☐ Approve ☐ Revise ☐ Reject |
| 32 | `hotel_management_agreement` | Hotel Management Agreement | ⚪ draft | 7 | | | ☐ Approve ☐ Revise ☐ Reject |
| 33 | `it_services_contract` | IT Services Contract | ⚪ draft | 9 | | | ☐ Approve ☐ Revise ☐ Reject |
| 34 | `insurance_contract` | Insurance Contract / Policy | ⚪ draft | 5 | | | ☐ Approve ☐ Revise ☐ Reject |
| 35 | `intellectual_property_assignment` | Intellectual Property Assignment | ⚪ draft | 6 | | | ☐ Approve ☐ Revise ☐ Reject |
| 36 | `internship_agreement` | Internship Agreement | ⚪ draft | 5 | | | ☐ Approve ☐ Revise ☐ Reject |
| 37 | `investment_agreement` | Investment Agreement | ⚪ draft | 6 | | | ☐ Approve ☐ Revise ☐ Reject |
| 38 | `joint_venture_agreement` | Joint Venture Agreement | ⚪ draft | 7 | | | ☐ Approve ☐ Revise ☐ Reject |
| 39 | `land_acquisition_agreement` | Land Acquisition Agreement | ⚪ draft | 7 | | | ☐ Approve ☐ Revise ☐ Reject |
| 40 | `licensing_agreement` | Licensing Agreement | ⚪ draft | 7 | | | ☐ Approve ☐ Revise ☐ Reject |
| 41 | `logistics_agreement` | Logistics / Freight Agreement | ⚪ draft | 8 | | | ☐ Approve ☐ Revise ☐ Reject |
| 42 | `maintenance_contract` | Maintenance Contract | ⚪ draft | 7 | | | ☐ Approve ☐ Revise ☐ Reject |
| 43 | `media_production_agreement` | Media Production Agreement | ⚪ draft | 7 | | | ☐ Approve ☐ Revise ☐ Reject |
| 44 | `memorandum_of_understanding` | Memorandum of Understanding | ⚪ draft | 4 | | | ☐ Approve ☐ Revise ☐ Reject |
| 45 | `mining_agreement` | Mining / Natural Resources Agreement | ⚪ draft | 7 | | | ☐ Approve ☐ Revise ☐ Reject |
| 46 | `outsourcing_agreement` | Outsourcing Agreement | ⚪ draft | 7 | | | ☐ Approve ☐ Revise ☐ Reject |
| 47 | `property_management_agreement` | Property Management Agreement | ⚪ draft | 7 | | | ☐ Approve ☐ Revise ☐ Reject |
| 48 | `research_collaboration_agreement` | Research Collaboration Agreement | ⚪ draft | 6 | | | ☐ Approve ☐ Revise ☐ Reject |
| 49 | `sales_representative_agreement` | Sales Representative Agreement | ⚪ draft | 6 | | | ☐ Approve ☐ Revise ☐ Reject |
| 50 | `settlement_agreement` | Settlement Agreement | ⚪ draft | 5 | | | ☐ Approve ☐ Revise ☐ Reject |
| 51 | `shareholder_agreement` | Shareholder Agreement | ⚪ draft | 7 | | | ☐ Approve ☐ Revise ☐ Reject |
| 52 | `sponsorship_agreement` | Sponsorship Agreement | ⚪ draft | 6 | | | ☐ Approve ☐ Revise ☐ Reject |
| 53 | `storage_agreement` | Storage / Warehousing Agreement | ⚪ draft | 7 | | | ☐ Approve ☐ Revise ☐ Reject |
| 54 | `subcontract_agreement` | Subcontract Agreement | ⚪ draft | 7 | | | ☐ Approve ☐ Revise ☐ Reject |
| 55 | `supply_agreement` | Supply Agreement | ⚪ draft | 8 | | | ☐ Approve ☐ Revise ☐ Reject |
| 56 | `telecommunications_agreement` | Telecommunications Agreement | ⚪ draft | 7 | | | ☐ Approve ☐ Revise ☐ Reject |

---

## B. Classifier collision-pair keyword ownership (6 open pairs)

13 profile pairs were identified as sharing enough vocabulary to collide (`docs/classifier_collision_pairs.md`, 2026-07-17). As of the latest test run (`ldv-backend/tests/collision_pairs_report.json`, 2026-07-22), **7 of 13 resolve cleanly**; the 6 below still need a human call on which profile should "own" the shared term when text is genuinely ambiguous. This is a domain/legal judgment, not something engineering can decide — see `docs/classifier_collision_pairs.md` for full differentiating-rule detail per pair.

Note: none of these are silent-wrong-result risks in the running pilot — every non-`validated` resolved profile already forces mandatory human confirmation (`worker._needs_confirmation()`'s `draft_profile` gate).

| Pair | Contested Between | Root Cause (shared keyword/root) | Current Default | Reviewer | Decision |
|---|---|---|---|---|---|
| 2 | `purchase_agreement` (validated) vs `supply_agreement` (draft) | "agreement", goods/procurement language | `supply_agreement`'s own text still resolves to `purchase_agreement` | | ☐ purchase_agreement owns it ☐ supply_agreement owns it ☐ Keep ambiguous, always confirm |
| 6 | `licensing_agreement` (draft) vs `software_license` (validated) | "license"/"licence" shared root | `licensing_agreement`'s own text resolves to `software_license` | | ☐ software_license owns it ☐ licensing_agreement owns it ☐ Keep ambiguous, always confirm |
| 7 | `joint_venture_agreement` (draft) vs `partnership_agreement` (validated) | "joint venture agreement" is literally a `partnership_agreement` keyword | `joint_venture_agreement`'s own text resolves to `partnership_agreement` | | ☐ partnership_agreement owns it ☐ joint_venture_agreement owns it ☐ Keep ambiguous, always confirm |
| 8 | `outsourcing_agreement` (draft) vs `service_agreement` (validated) | generic service/delegation language | `outsourcing_agreement`'s own text resolves to `service_agreement` | | ☐ service_agreement owns it ☐ outsourcing_agreement owns it ☐ Keep ambiguous, always confirm |
| 9 | `employment_contract` (validated) vs `employment_termination_agreement` (draft) | "employment", "kontrak kerja" shared root | `employment_termination_agreement`'s own text (termination/PHK language) still resolves to `employment_contract` | | ☐ employment_contract owns it ☐ employment_termination_agreement owns it ☐ Keep ambiguous, always confirm |
| 13 | `banking_facility_agreement` (draft) vs `loan_agreement` (validated) | both are lender/borrower credit structures | `banking_facility_agreement`'s own text resolves to `loan_agreement` | | ☐ loan_agreement owns it ☐ banking_facility_agreement owns it ☐ Keep ambiguous, always confirm |

---

## C. Required/dangerous-clause severity sign-off

`datasets/required_clauses_MASTER.csv` (942 rows) already carries lawyer-authored `Impact_Level` ratings driving L3 risk-score deductions: **120 Critical, 462 High, 246 Medium, 114 Low.** This data exists and is *not* fabricated or engineering-invented — Ilham authored it. What's missing is a **formal, dated sign-off** recording who reviewed and approved these ratings as current, since the 2026-07-17 review's "0/56 legal approval" finding applies to this dataset too (existence of lawyer-authored data ≠ recorded lawyer approval of it).

- [ ] Reviewer: _______________ Date: _______________
- [ ] ☐ Approve as-is ☐ Approve with noted revisions (list below) ☐ Needs rework
- Notes:

---

## D. Risk-score ground truth

The deterministic L3 scorer (`ldv-backend/detector/detector_scorer.py`) produces a 0-100 score per document. **No fixture currently has a lawyer-reviewed expected score** — every score in the corpus harness is reported as `PENDING` (actual value shown, no pass/fail claim), by design, to avoid inventing ground truth. 33 fixtures are ready and waiting: `ldv-backend/tests/original11_corpus_report.json` lists each fixture's actual computed score/label (LOW/MEDIUM/HIGH/CRITICAL) next to its identified profile and missing-clause list.

**Ask:** for each of the 33 fixtures (or a representative sample), does the actual score/label look legally reasonable given the clauses present/missing? Where it doesn't, what should the correct score/label be, and why (which clause weight is off)?

- [ ] Reviewer: _______________ Date: _______________
- Fixtures reviewed: _____ / 33
- Notes / corrected scores:

---

## E. Recommendation-wording spot-check

Every red flag / missing-clause finding carries a `suggested_correction` (from `_RED_FLAG_GUIDANCE` in `detector/risk_explainer.py`, or `clause_db.py`'s Ilham-authored `Recommendation` field). Engineering has only verified these are *present* (non-empty) on every finding — not that the legal *wording* is correct or appropriately hedged for a non-lawyer end user.

**Ask:** spot-check a sample of `suggested_correction` text (source: run any fixture through `/analyze`, or read `detector/risk_explainer.py`'s `_RED_FLAG_GUIDANCE` table directly) for legal accuracy and appropriate hedging language ("consider," "may wish to," not "you must").

- [ ] Reviewer: _______________ Date: _______________
- Sample reviewed: _____ findings
- Notes:

---

## F. Legal citations — already complete, no action needed

`datasets/legal_citations.csv`: **87/87 rows `status=verified`.** No open item here as of 2026-07-22. Listed for completeness/transparency only — new citations added in future will need the same verification before `citation_db.py` will surface them to end users (it fails closed to `verified`-only by default).

---

## Sign-off

Once all sections above are complete, record the overall Gate 4 outcome here:

- **Gate 4 (Legal Review) status:** ☐ Not started ☐ In progress ☐ Complete
- **Overall reviewer(s):** _______________
- **Date:** _______________
- **Blocking items remaining:** _______________
