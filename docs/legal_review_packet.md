# CRA Legal Review Packet

**Purpose:** single, self-contained ground-truth source for everything currently blocked on a licensed lawyer's judgment before CRA can move beyond the controlled-pilot phase. This maps to Gate 4 ("legal review") of the CRA Release Gate Matrix (`CLAUDE.md` TODO, external review 2026-06-22/2026-07-17).

**This document contains no legal opinions.** Every table below is the *actual content* pulled directly from the live source files (`registry_v1.json`, `required_clauses_MASTER.csv`, `classifier_collision_pairs.md`, `original11_corpus_report.json`, `risk_explainer.py`, `legal_citations.csv`) as of 2026-07-22 — nothing summarized-then-discarded, nothing invented. Reviewer / Date / Decision fields are left blank for a named reviewer to complete; a checkbox or table row with no name in it means no review has happened yet. Per the 2026-07-17 external review: legal approval is currently **0/56** profiles; nothing in this packet changes that until a reviewer actually signs a section below.

**How to use this packet:** each section is one class of open legal decision, with the full underlying data inlined so no other file needs to be opened to review it. Sections are independent; a lawyer can complete them in any order or split across reviewers. Sections B and F are known to drift as engineering work lands (collision-pair count shrinks as classifier bugs get fixed; citation count grows as new citations are verified) — re-run the referenced scripts before treating stale counts as current if this packet is reused much later.

---

## A. Contract-profile validation (56 profiles, full clause + jurisdiction + hypothesis data)

Every profile's required-clause set, jurisdiction coverage, and NLI hypothesis needs a named reviewer's sign-off before it can move from `draft` to `validated` status in `detector/profiles/registry_v1.json`. **11 profiles are already `validated`** and in the controlled pilot (manual-selection only, per 2026-07-21) — even those have not had a *formal* legal sign-off recorded; "validated" here is an engineering/pilot-readiness status, not a legal-approval status.

| # | Profile ID | Display Name | Status | Jurisdictions | Required Clauses | NLI Hypothesis | Reviewer | Date | Decision |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `commercial_agreement` | Commercial Agreement | ✅ validated (pilot) | ID, FR, NL, INT | `governing_law`, `jurisdiction_venue`, `payment_terms`, `termination`, `limitation_liability`, `dispute_resolution` | This document is a commercial agreement between businesses. | | | ☐ Approve ☐ Revise ☐ Reject |
| 2 | `consulting_agreement` | Consulting Agreement | ✅ validated (pilot) | ID, FR, NL, INT | `governing_law`, `jurisdiction_venue`, `scope_of_services`, `payment_terms`, `confidentiality`, `termination`, `dispute_resolution` | This document covers consulting or advisory services. | | | ☐ Approve ☐ Revise ☐ Reject |
| 3 | `employment_contract` | Employment Contract | ✅ validated (pilot) | ID, FR, NL, INT | `governing_law`, `jurisdiction_venue`, `termination`, `notice_period`, `compensation`, `working_hours`, `dispute_resolution` | This document involves employment terms between employer and employee. | | | ☐ Approve ☐ Revise ☐ Reject |
| 4 | `general_contract` | General Contract | ✅ validated (pilot) | ID, FR, NL, INT | `governing_law`, `jurisdiction_venue`, `payment_terms`, `termination`, `dispute_resolution`, `limitation_liability` | This is a general legal agreement between two or more parties. | | | ☐ Approve ☐ Revise ☐ Reject |
| 5 | `lease_agreement` | Lease Agreement | ✅ validated (pilot) | ID, FR, NL, INT | `governing_law`, `jurisdiction_venue`, `lease_term`, `rent_amount`, `security_deposit`, `maintenance_responsibility`, `termination`, `dispute_resolution` | This document is a lease or rental agreement for property. | | | ☐ Approve ☐ Revise ☐ Reject |
| 6 | `loan_agreement` | Loan Agreement | ✅ validated (pilot) | ID, FR, NL, INT | `governing_law`, `jurisdiction_venue`, `principal_amount`, `interest_rate`, `repayment_schedule`, `default_provisions`, `termination`, `dispute_resolution` | This document covers a loan of money between lender and borrower. | | | ☐ Approve ☐ Revise ☐ Reject |
| 7 | `non_disclosure_agreement` | Non-Disclosure Agreement | ✅ validated (pilot) | ID, FR, NL, INT | `governing_law`, `jurisdiction_venue`, `confidentiality`, `termination`, `return_of_materials`, `dispute_resolution` | This document involves confidentiality and non-disclosure obligations. | | | ☐ Approve ☐ Revise ☐ Reject |
| 8 | `partnership_agreement` | Partnership Agreement | ✅ validated (pilot) | ID, FR, NL, INT | `governing_law`, `jurisdiction_venue`, `capital_contribution`, `profit_sharing`, `management_rights`, `termination`, `dispute_resolution` | This document establishes a business partnership between parties. | | | ☐ Approve ☐ Revise ☐ Reject |
| 9 | `purchase_agreement` | Purchase Agreement | ✅ validated (pilot) | ID, FR, NL, INT | `governing_law`, `jurisdiction_venue`, `goods_description`, `payment_terms`, `delivery_terms`, `warranty`, `title_transfer`, `dispute_resolution` | This document covers the purchase or sale of goods or assets. | | | ☐ Approve ☐ Revise ☐ Reject |
| 10 | `service_agreement` | Service Agreement | ✅ validated (pilot) | ID, FR, NL, INT | `governing_law`, `jurisdiction_venue`, `scope_of_services`, `payment_terms`, `termination`, `limitation_liability`, `dispute_resolution` | This document covers the provision of services. | | | ☐ Approve ☐ Revise ☐ Reject |
| 11 | `software_license` | Software License Agreement | ✅ validated (pilot) | INT, ID, NL, FR | `governing_law`, `jurisdiction_venue`, `license_grant`, `ip_ownership`, `limitation_liability`, `warranty_disclaimer`, `termination`, `dispute_resolution` | This document grants a license to use software between licensor and licensee. | | | ☐ Approve ☐ Revise ☐ Reject |
| 12 | `advertising_agreement` | Advertising Agreement | ⚪ draft | ID, INT | `governing_law`, `jurisdiction_venue`, `scope_of_services`, `payment_terms`, `ip_ownership`, `termination`, `dispute_resolution` | This document is an advertising or marketing agreement for the promotion of a product, service, or brand. | | | ☐ Approve ☐ Revise ☐ Reject |
| 13 | `agency_agreement` | Agency Agreement | ⚪ draft | ID, FR, NL, INT | `governing_law`, `jurisdiction_venue`, `scope_of_services`, `compensation`, `termination`, `dispute_resolution` | This document is a commercial agency agreement in which an agent acts on behalf of a principal to negotiate or conclude transactions. | | | ☐ Approve ☐ Revise ☐ Reject |
| 14 | `banking_facility_agreement` | Banking Facility Agreement | ⚪ draft | ID, FR, NL, INT | `governing_law`, `jurisdiction_venue`, `principal_amount`, `interest_rate`, `repayment_schedule`, `default_provisions`, `termination`, `dispute_resolution` | This document is a banking facility agreement under which a bank provides a credit facility to a borrower. | | | ☐ Approve ☐ Revise ☐ Reject |
| 15 | `construction_contract` | Construction Contract | ⚪ draft | ID, INT | `governing_law`, `jurisdiction_venue`, `scope_of_services`, `payment_terms`, `delivery_terms`, `warranty`, `termination`, `indemnification`, `dispute_resolution` | This document is a construction contract for the design, building, or engineering of a physical structure. | | | ☐ Approve ☐ Revise ☐ Reject |
| 16 | `cooperation_agreement` | Cooperation Agreement | ⚪ draft | ID, FR, NL, INT | `governing_law`, `jurisdiction_venue`, `scope_of_services`, `termination`, `dispute_resolution` | This document is a cooperation agreement establishing a framework for collaboration between parties without forming a joint venture. | | | ☐ Approve ☐ Revise ☐ Reject |
| 17 | `data_processing_agreement` | Data Processing Agreement | ⚪ draft | FR, NL, INT | `governing_law`, `jurisdiction_venue`, `confidentiality`, `termination`, `dispute_resolution` | This document is a data processing agreement governing how a processor handles personal data on behalf of a controller. | | | ☐ Approve ☐ Revise ☐ Reject |
| 18 | `distribution_agreement` | Distribution Agreement | ⚪ draft | ID, FR, NL, INT | `governing_law`, `jurisdiction_venue`, `scope_of_services`, `payment_terms`, `termination`, `limitation_liability`, `dispute_resolution` | This document is a distribution agreement in which a distributor resells the supplier's products within an assigned territory. | | | ☐ Approve ☐ Revise ☐ Reject |
| 19 | `education_services_agreement` | Education Services Agreement | ⚪ draft | ID, INT | `governing_law`, `jurisdiction_venue`, `scope_of_services`, `payment_terms`, `termination`, `dispute_resolution` | This document is an education or training services agreement for the provision of instruction or educational programs. | | | ☐ Approve ☐ Revise ☐ Reject |
| 20 | `employment_termination_agreement` | Employment Termination Agreement | ⚪ draft | ID | `governing_law`, `jurisdiction_venue`, `compensation`, `termination`, `dispute_resolution`, `entire_agreement` | This document is an employment termination or separation agreement setting the terms on which an employment relationship ends. | | | ☐ Approve ☐ Revise ☐ Reject |
| 21 | `energy_supply_agreement` | Energy Supply Agreement | ⚪ draft | ID, INT | `governing_law`, `jurisdiction_venue`, `scope_of_services`, `payment_terms`, `delivery_terms`, `force_majeure`, `termination`, `dispute_resolution` | This document is an energy supply agreement for the delivery of electricity, power, or other energy resources. | | | ☐ Approve ☐ Revise ☐ Reject |
| 22 | `escrow_agreement` | Escrow Agreement | ⚪ draft | ID, INT | `governing_law`, `jurisdiction_venue`, `principal_amount`, `termination`, `dispute_resolution` | This document is an escrow agreement in which a neutral third party holds funds or assets until agreed conditions are met. | | | ☐ Approve ☐ Revise ☐ Reject |
| 23 | `event_contract` | Event Contract | ⚪ draft | ID, INT | `governing_law`, `jurisdiction_venue`, `scope_of_services`, `payment_terms`, `force_majeure`, `termination`, `dispute_resolution` | This document is an event contract for the planning, staging, or provision of services at an event. | | | ☐ Approve ☐ Revise ☐ Reject |
| 24 | `export_import_agreement` | Export / Import Agreement | ⚪ draft | ID, INT | `governing_law`, `jurisdiction_venue`, `goods_description`, `payment_terms`, `delivery_terms`, `title_transfer`, `termination`, `dispute_resolution` | This document is an export or import agreement for the cross-border sale and shipment of goods. | | | ☐ Approve ☐ Revise ☐ Reject |
| 25 | `facilities_management_agreement` | Facilities Management Agreement | ⚪ draft | ID, INT | `governing_law`, `jurisdiction_venue`, `scope_of_services`, `payment_terms`, `termination`, `indemnification`, `dispute_resolution` | This document is a facilities management agreement for the operation and maintenance of a building or site's facilities. | | | ☐ Approve ☐ Revise ☐ Reject |
| 26 | `factoring_agreement` | Factoring Agreement | ⚪ draft | ID, INT | `governing_law`, `jurisdiction_venue`, `principal_amount`, `payment_terms`, `default_provisions`, `termination`, `dispute_resolution` | This document is a factoring agreement in which a business sells its invoices or receivables to a factor for immediate cash. | | | ☐ Approve ☐ Revise ☐ Reject |
| 27 | `franchise_agreement` | Franchise Agreement | ⚪ draft | ID, FR, NL, INT | `governing_law`, `jurisdiction_venue`, `license_grant`, `ip_ownership`, `payment_terms`, `termination`, `dispute_resolution` | This document is a franchise agreement granting a franchisee the right to operate under the franchisor's brand and business system. | | | ☐ Approve ☐ Revise ☐ Reject |
| 28 | `freelance_contract` | Freelance / Independent Contractor Agreement | ⚪ draft | ID, FR, NL, INT | `governing_law`, `jurisdiction_venue`, `scope_of_services`, `payment_terms`, `ip_ownership`, `termination`, `dispute_resolution` | This document is a freelance or independent contractor agreement engaging a self-employed individual to perform services. | | | ☐ Approve ☐ Revise ☐ Reject |
| 29 | `government_procurement_contract` | Government Procurement Contract | ⚪ draft | ID | `governing_law`, `jurisdiction_venue`, `scope_of_services`, `payment_terms`, `delivery_terms`, `warranty`, `termination`, `indemnification`, `dispute_resolution` | This document is a government procurement contract for the supply of goods, services, or works to a government entity. | | | ☐ Approve ☐ Revise ☐ Reject |
| 30 | `grant_agreement` | Grant Agreement | ⚪ draft | ID, FR, INT | `governing_law`, `jurisdiction_venue`, `principal_amount`, `termination`, `dispute_resolution` | This document is a grant agreement under which funds are given to a recipient for a specified purpose without repayment. | | | ☐ Approve ☐ Revise ☐ Reject |
| 31 | `healthcare_services_agreement` | Healthcare Services Agreement | ⚪ draft | ID, INT | `governing_law`, `jurisdiction_venue`, `scope_of_services`, `payment_terms`, `confidentiality`, `indemnification`, `termination`, `dispute_resolution` | This document is a healthcare services agreement for the provision of medical or clinical services. | | | ☐ Approve ☐ Revise ☐ Reject |
| 32 | `hotel_management_agreement` | Hotel Management Agreement | ⚪ draft | ID, INT | `governing_law`, `jurisdiction_venue`, `scope_of_services`, `compensation`, `termination`, `indemnification`, `dispute_resolution` | This document is a hotel management agreement appointing an operator to manage a hotel property on the owner's behalf. | | | ☐ Approve ☐ Revise ☐ Reject |
| 33 | `it_services_contract` | IT Services Contract | ⚪ draft | ID, FR, NL, INT | `governing_law`, `jurisdiction_venue`, `scope_of_services`, `payment_terms`, `ip_ownership`, `limitation_liability`, `warranty_disclaimer`, `termination`, `dispute_resolution` | This document is an IT services contract for the provision of information technology support or managed services. | | | ☐ Approve ☐ Revise ☐ Reject |
| 34 | `insurance_contract` | Insurance Contract / Policy | ⚪ draft | ID, FR, NL, INT | `governing_law`, `jurisdiction_venue`, `insurance`, `termination`, `dispute_resolution` | This document is an insurance contract or policy under which an insurer agrees to cover specified risks in exchange for premiums. | | | ☐ Approve ☐ Revise ☐ Reject |
| 35 | `intellectual_property_assignment` | Intellectual Property Assignment | ⚪ draft | ID, FR, NL, INT | `governing_law`, `jurisdiction_venue`, `ip_ownership`, `compensation`, `warranty`, `dispute_resolution` | This document is an intellectual property assignment transferring ownership of IP rights from one party to another. | | | ☐ Approve ☐ Revise ☐ Reject |
| 36 | `internship_agreement` | Internship Agreement | ⚪ draft | ID, FR, NL, INT | `governing_law`, `jurisdiction_venue`, `working_hours`, `termination`, `dispute_resolution` | This document is an internship agreement setting the terms of a temporary work-learning placement for a student or trainee. | | | ☐ Approve ☐ Revise ☐ Reject |
| 37 | `investment_agreement` | Investment Agreement | ⚪ draft | ID, FR, NL, INT | `governing_law`, `jurisdiction_venue`, `principal_amount`, `profit_sharing`, `termination`, `dispute_resolution` | This document is an investment agreement setting the terms under which an investor provides capital in exchange for equity or returns. | | | ☐ Approve ☐ Revise ☐ Reject |
| 38 | `joint_venture_agreement` | Joint Venture Agreement | ⚪ draft | ID, INT | `governing_law`, `jurisdiction_venue`, `capital_contribution`, `profit_sharing`, `management_rights`, `termination`, `dispute_resolution` | This document is a joint venture agreement establishing a jointly owned business between two or more parties. | | | ☐ Approve ☐ Revise ☐ Reject |
| 39 | `land_acquisition_agreement` | Land Acquisition Agreement | ⚪ draft | ID | `governing_law`, `jurisdiction_venue`, `goods_description`, `payment_terms`, `title_transfer`, `termination`, `dispute_resolution` | This document is a land acquisition agreement for the purchase or transfer of land or real property. | | | ☐ Approve ☐ Revise ☐ Reject |
| 40 | `licensing_agreement` | Licensing Agreement | ⚪ draft | ID, FR, NL, INT | `governing_law`, `jurisdiction_venue`, `license_grant`, `ip_ownership`, `payment_terms`, `termination`, `dispute_resolution` | This document is a licensing agreement granting rights to use intellectual property in exchange for royalties or fees. | | | ☐ Approve ☐ Revise ☐ Reject |
| 41 | `logistics_agreement` | Logistics / Freight Agreement | ⚪ draft | ID, INT | `governing_law`, `jurisdiction_venue`, `scope_of_services`, `payment_terms`, `delivery_terms`, `limitation_liability`, `termination`, `dispute_resolution` | This document is a logistics or freight agreement for the transportation and handling of goods. | | | ☐ Approve ☐ Revise ☐ Reject |
| 42 | `maintenance_contract` | Maintenance Contract | ⚪ draft | ID, FR, NL, INT | `governing_law`, `jurisdiction_venue`, `scope_of_services`, `payment_terms`, `termination`, `limitation_liability`, `dispute_resolution` | This document is a maintenance contract for the ongoing upkeep or repair of equipment or property. | | | ☐ Approve ☐ Revise ☐ Reject |
| 43 | `media_production_agreement` | Media Production Agreement | ⚪ draft | ID, INT | `governing_law`, `jurisdiction_venue`, `scope_of_services`, `payment_terms`, `ip_ownership`, `termination`, `dispute_resolution` | This document is a media production agreement for the creation of film, video, or other media content. | | | ☐ Approve ☐ Revise ☐ Reject |
| 44 | `memorandum_of_understanding` | Memorandum of Understanding | ⚪ draft | ID, FR, NL, INT | `governing_law`, `jurisdiction_venue`, `termination`, `dispute_resolution` | This document is a memorandum of understanding recording a preliminary, often non-binding, agreement between parties. | | | ☐ Approve ☐ Revise ☐ Reject |
| 45 | `mining_agreement` | Mining / Natural Resources Agreement | ⚪ draft | ID | `governing_law`, `jurisdiction_venue`, `scope_of_services`, `payment_terms`, `termination`, `indemnification`, `dispute_resolution` | This document is a mining or natural resources agreement granting rights to extract minerals or resources from land. | | | ☐ Approve ☐ Revise ☐ Reject |
| 46 | `outsourcing_agreement` | Outsourcing Agreement | ⚪ draft | ID | `governing_law`, `jurisdiction_venue`, `scope_of_services`, `payment_terms`, `confidentiality`, `termination`, `dispute_resolution` | This document is an outsourcing agreement transferring a business function or process to an external service provider. | | | ☐ Approve ☐ Revise ☐ Reject |
| 47 | `property_management_agreement` | Property Management Agreement | ⚪ draft | ID, INT | `governing_law`, `jurisdiction_venue`, `scope_of_services`, `compensation`, `termination`, `indemnification`, `dispute_resolution` | This document is a property management agreement appointing a manager to operate and maintain real property on the owner's behalf. | | | ☐ Approve ☐ Revise ☐ Reject |
| 48 | `research_collaboration_agreement` | Research Collaboration Agreement | ⚪ draft | ID, FR, NL, INT | `governing_law`, `jurisdiction_venue`, `ip_ownership`, `confidentiality`, `termination`, `dispute_resolution` | This document is a research collaboration agreement between parties jointly conducting research. | | | ☐ Approve ☐ Revise ☐ Reject |
| 49 | `sales_representative_agreement` | Sales Representative Agreement | ⚪ draft | ID, FR, NL, INT | `governing_law`, `jurisdiction_venue`, `scope_of_services`, `compensation`, `termination`, `dispute_resolution` | This document is a sales representative agreement in which a representative sells the principal's products, typically for commission. | | | ☐ Approve ☐ Revise ☐ Reject |
| 50 | `settlement_agreement` | Settlement Agreement | ⚪ draft | ID, FR, NL, INT | `governing_law`, `jurisdiction_venue`, `dispute_resolution`, `termination`, `entire_agreement` | This document is a settlement agreement resolving a dispute between parties, often in exchange for a payment or release of claims. | | | ☐ Approve ☐ Revise ☐ Reject |
| 51 | `shareholder_agreement` | Shareholder Agreement | ⚪ draft | ID, FR, NL, INT | `governing_law`, `jurisdiction_venue`, `capital_contribution`, `profit_sharing`, `management_rights`, `termination`, `dispute_resolution` | This document is a shareholder agreement governing the rights and obligations of shareholders in a company. | | | ☐ Approve ☐ Revise ☐ Reject |
| 52 | `sponsorship_agreement` | Sponsorship Agreement | ⚪ draft | ID, FR, NL, INT | `governing_law`, `jurisdiction_venue`, `payment_terms`, `ip_ownership`, `termination`, `dispute_resolution` | This document is a sponsorship agreement in which a sponsor provides funding or support in exchange for promotional benefits. | | | ☐ Approve ☐ Revise ☐ Reject |
| 53 | `storage_agreement` | Storage / Warehousing Agreement | ⚪ draft | ID, INT | `governing_law`, `jurisdiction_venue`, `scope_of_services`, `payment_terms`, `limitation_liability`, `termination`, `dispute_resolution` | This document is a storage or warehousing agreement for the safekeeping of goods on behalf of a depositor. | | | ☐ Approve ☐ Revise ☐ Reject |
| 54 | `subcontract_agreement` | Subcontract Agreement | ⚪ draft | ID, INT | `governing_law`, `jurisdiction_venue`, `scope_of_services`, `payment_terms`, `termination`, `indemnification`, `dispute_resolution` | This document is a subcontract agreement in which a subcontractor performs part of a main contractor's obligations. | | | ☐ Approve ☐ Revise ☐ Reject |
| 55 | `supply_agreement` | Supply Agreement | ⚪ draft | ID, FR, NL, INT | `governing_law`, `jurisdiction_venue`, `goods_description`, `payment_terms`, `delivery_terms`, `warranty`, `termination`, `dispute_resolution` | This document is a supply agreement for the ongoing delivery of goods from a supplier to a buyer. | | | ☐ Approve ☐ Revise ☐ Reject |
| 56 | `telecommunications_agreement` | Telecommunications Agreement | ⚪ draft | ID, INT | `governing_law`, `jurisdiction_venue`, `scope_of_services`, `payment_terms`, `limitation_liability`, `termination`, `dispute_resolution` | This document is a telecommunications agreement for the provision of network, telephony, or communications services. | | | ☐ Approve ☐ Revise ☐ Reject |

---

## B. Classifier collision-pair keyword ownership

13 profile pairs were identified as sharing enough vocabulary to collide (`docs/classifier_collision_pairs.md`, 2026-07-17), generated from `registry_v1.json`'s `classifier.competing_profiles` field. **Coverage gap:** only 13 of 56 profiles (23%) have `competing_profiles` populated at all — the other 43 have no documented collision risk, so this list is a starting point, not a complete pairwise analysis. **Every one of the 13 pairs has an empty `negative_keywords` list on both sides** — the registry schema has a field designed exactly to resolve this kind of confusion, and none of the 13 known-colliding profiles use it. `service_agreement` is the dominant collision hub (5 of 13 pairs collide against it).

As of the latest test run (`ldv-backend/tests/collision_pairs_report.json`, 2026-07-22), **7 of 13 resolve cleanly**; the 6 below still need a human call on which profile should "own" the shared term. None of these are silent-wrong-result risks in the running pilot — every non-`validated` resolved profile already forces mandatory human confirmation (`worker._needs_confirmation()`'s `draft_profile` gate).

### Pair 2 — `purchase_agreement` (validated) vs `supply_agreement` (draft)
- **Differentiating rule:** purchase_agreement is a *one-off transactional* purchase/sale of goods or assets; supply_agreement is *ongoing/recurring delivery* from a supplier to a buyer.
- **A-only signal:** "sale agreement", "sales contract", "koopovereenkomst"
- **B-only signal:** "supplier agreement", "procurement agreement", "perjanjian pengadaan", "pasokan"
- **Registry gap:** no negative_keywords; the ongoing-vs-one-off distinction is structural/temporal, not purely lexical.
- **Current test result:** `supply_agreement`'s own B-signal text still resolves to `purchase_agreement`.
- Reviewer: _______________ Date: _______________ Decision: ☐ purchase_agreement owns it ☐ supply_agreement owns it ☐ Keep ambiguous, always confirm

### Pair 6 — `licensing_agreement` (draft) vs `software_license` (validated)
- **Differentiating rule:** software_license is *software-specific* (EULA, SaaS, source code); licensing_agreement is broader IP licensing (patents, trademarks, content) with no software requirement.
- **A-only signal:** "perjanjian lisensi", "contrat de licence" (generic)
- **B-only signal:** "eula", "saas agreement", "end user license agreement", "software licence"
- **Registry gap:** no negative_keywords; licensing_agreement's positive_keywords heavily overlap software_license's own aliases.
- **Current test result:** `licensing_agreement`'s own A-signal text resolves to `software_license`.
- Reviewer: _______________ Date: _______________ Decision: ☐ software_license owns it ☐ licensing_agreement owns it ☐ Keep ambiguous, always confirm

### Pair 7 — `joint_venture_agreement` (draft) vs `partnership_agreement` (validated)
- **Differentiating rule:** weakest boundary alongside pair 4/12 below — "joint venture agreement" is *literally a partnership_agreement positive keyword*. joint_venture_agreement's hypothesis specifies a *jointly-owned business entity*; partnership_agreement is broader.
- **Registry gap:** literal keyword duplication between competing profiles — the same string appears in both profiles' `positive_keywords`, which cannot disambiguate them.
- **Current test result:** `joint_venture_agreement`'s own A-signal text resolves to `partnership_agreement`.
- Reviewer: _______________ Date: _______________ Decision: ☐ partnership_agreement owns it ☐ joint_venture_agreement owns it ☐ Keep ambiguous, always confirm

### Pair 8 — `outsourcing_agreement` (draft) vs `service_agreement` (validated)
- **Differentiating rule:** outsourcing_agreement requires *transfer of an existing business function/process* to an external provider; service_agreement doesn't require an existing internal function being handed off.
- **A-only signal:** "alih daya", "perjanjian outsourcing"
- **B-only signal:** "maintenance agreement", "dienstverleningsovereenkomst"
- **Registry gap:** no negative_keywords.
- **Current test result:** `outsourcing_agreement`'s own A-signal text resolves to `service_agreement` (this is the documented/expected ambiguity, not a new bug — see 2026-07-22 engineering fix that removed a *different*, unrelated false-positive on this same pair).
- Reviewer: _______________ Date: _______________ Decision: ☐ service_agreement owns it ☐ outsourcing_agreement owns it ☐ Keep ambiguous, always confirm

### Pair 9 — `employment_contract` (validated) vs `employment_termination_agreement` (draft)
- **Differentiating rule:** clearest boundary in the set — employment_contract governs an *ongoing* employment relationship; employment_termination_agreement governs its *end* (severance/separation terms). Low collision risk if temporal framing is used as signal.
- **A-only signal:** "kontrak kerja", "work agreement"
- **B-only signal:** "phk", "separation agreement", "pemutusan hubungan kerja"
- **Registry gap:** no negative_keywords (e.g. employment_contract could list "termination"/"severance"/"separation" as negative keywords).
- **Current test result:** `employment_termination_agreement`'s own B-signal text (termination/PHK language) still resolves to `employment_contract`.
- Reviewer: _______________ Date: _______________ Decision: ☐ employment_contract owns it ☐ employment_termination_agreement owns it ☐ Keep ambiguous, always confirm

### Pair 13 — `banking_facility_agreement` (draft) vs `loan_agreement` (validated)
- **Differentiating rule:** banking_facility_agreement is a *regulated bank* extending a *credit facility* (revolving/drawdown structure, OJK-regulated in Indonesia); loan_agreement is broader (any lender/borrower relationship).
- **A-only signal:** "ojk", "fasilitas kredit", "credit facility agreement"
- **B-only signal:** none distinctly — loan_agreement's keywords are a superset that banking_facility_agreement's terms could also trigger.
- **Registry gap:** no negative_keywords; loan_agreement has no signal that excludes bank-facility structures, so it risks absorbing bank-facility contracts by default.
- **Current test result:** `banking_facility_agreement`'s own A-signal text resolves to `loan_agreement`.
- Reviewer: _______________ Date: _______________ Decision: ☐ loan_agreement owns it ☐ banking_facility_agreement owns it ☐ Keep ambiguous, always confirm

### For reference — the 7 pairs that already resolve cleanly (no decision needed)
Pair 1 (distribution_agreement vs service_agreement), Pair 3 (agency_agreement vs service_agreement), Pair 4 (maintenance_contract vs service_agreement — fixed 2026-07-22, see engineering log), Pair 5 (it_services_contract vs service_agreement), Pair 10 (agency_agreement vs sales_representative_agreement), Pair 11 (consulting_agreement vs freelance_contract), Pair 12 (cooperation_agreement vs partnership_agreement — note: this pair has the *same* literal-keyword-duplication registry gap as pairs 7/4 above, "perjanjian kerjasama"/"samenwerkingsovereenkomst" appear in both profiles' positive_keywords, but current test text happens not to trigger the collision; worth a proactive decision here too even though today's test passed).

---

## C. Required/dangerous-clause severity sign-off (full 34-clause guidance table)

`datasets/required_clauses_MASTER.csv` (942 rows total) carries lawyer-authored `Impact_Level` ratings driving L3 risk-score deductions. Full distribution: **120 Critical, 462 High, 246 Medium, 114 Low.** This table shows the EN guidance (via `clause_db.py`'s `clause_guidance()`/`clause_impact()`, the same functions the running system calls) for every one of the 34 distinct clause IDs actually referenced across the 56 profiles' `required_clauses` lists in Section A. This data already exists and is *not* fabricated or engineering-invented — Ilham authored it. What's missing is a **formal, dated sign-off** recording who reviewed and approved these ratings as current.

| Clause ID | Impact Level | Reason | Recommendation | Business Impact |
|---|---|---|---|---|
| `governing_law` | CRITICAL | Specifying which country's laws interpret the contract provides legal certainty and predictability. | State the governing law explicitly (e.g., 'Swiss law' or 'French law'). Avoid vague references. | Without governing law, disputes may be decided under unexpected or unfavorable legal systems. |
| `jurisdiction_venue` | *(unmapped — no Ilham DB entry for this clause ID; by design, per `clause_db.py` — "Jurisdiction/Venue" was never reconciled to an Ilham `Clause_Name`)* | | | |
| `payment_terms` | CRITICAL | Payment terms define when and how money changes hands, preventing cash flow disputes. | Specify the payment schedule, due dates, acceptable methods (cash, bank transfer), and consequences of late payment. | Unclear payment terms lead to delayed payments and financial uncertainty. |
| `termination` | HIGH | A termination clause allows parties to exit the contract legally under agreed conditions, preventing perpetual obligations. | Include a right to terminate with written notice (e.g., 30 days) and provisions for termination for breach. | Without termination rights, a party may be trapped in an unfavorable or non-performing agreement. |
| `dispute_resolution` | HIGH | A clear dispute resolution mechanism avoids costly and lengthy court battles by providing an agreed process. | Specify the method (mediation, arbitration, or courts), the venue, and any pre-litigation steps (e.g., mediation). | Without this, parties may face expensive and unpredictable litigation in an inconvenient forum. |
| `limitation_liability` | CRITICAL | A liability clause allocates financial risk between parties and typically includes a cap to limit exposure. | Include a mutual limitation of liability (e.g., capped at the contract value) and exclude indirect damages. | Unlimited liability can bankrupt a party due to a single error or breach. |
| `confidentiality` | HIGH | Confidentiality clauses protect sensitive business information shared during the contract from misuse. | Define what is confidential, the duration of the obligation, and exceptions (e.g., required by law). | Loss of trade secrets and competitive advantage if sensitive information is leaked. |
| `force_majeure` | MEDIUM | A force majeure clause excuses performance when events beyond control occur, protecting parties from liability. | Define events that qualify (e.g., natural disasters, war, pandemics) and the consequences (suspension, termination). | Without it, a party may be liable for non-performance caused by truly uncontrollable events. |
| `compensation` | CRITICAL | The salary clause defines compensation and payment frequency to avoid wage disputes. | Specify gross monthly salary, any extra months (e.g., 13th), and the payment date. | Without a salary clause, the employee may not be paid or may be underpaid. |
| `working_hours` | CRITICAL | Working hours determine overtime pay and compliance with labor laws. | State the weekly or monthly working hours, and if applicable, the distribution across days. | Missing hours can lead to wage disputes and labor law violations. |
| `scope_of_services` | CRITICAL | The contract must clearly define what is being provided, sold, lent, or done to avoid misunderstandings. | Describe the subject matter in detail including quantity, quality, specifications, and any relevant characteristics. | Vague object leads to disputes about performance and may render the contract void. |
| `principal_amount` | CRITICAL | The exact amount borrowed must be stated to define the debt. | Write the amount in both numbers and words, specifying the currency. | Without a clear amount, the loan is unenforceable. |
| `interest_rate` | HIGH | If interest applies, the rate and calculation method must be specified to avoid disputes. | State the annual percentage rate, when interest accrues, and any late payment penalty rate. | Unclear interest terms lead to disagreements on total repayment amount. |
| `repayment_schedule` | CRITICAL | How and when the loan is repaid must be clear to avoid default disputes. | Specify the repayment method (one-time, instalments), dates, and duration. Include consequences of late payment. | Without a schedule, the lender may never get repaid or the borrower may face unexpected demands. |
| `delivery_terms` | HIGH | Delivery terms determine when ownership and risk pass from seller to buyer. | Specify who delivers, the address, the deadline, and when risk transfers (e.g., at collection or delivery). | Disputes over damaged goods during transport if risk transfer is unclear. |
| `warranty` | CRITICAL | A warranty clause defines the seller's responsibility for defects after sale. | State whether legal warranty applies, or any additional guarantees, and exclusions (e.g., sold as is). | Without warranty, the buyer may have no recourse for defective goods. |
| `indemnification` | HIGH | An indemnification clause ensures that one party covers legal costs if the other is sued by a third party. | Define the scope of indemnity, whether it is mutual, and any caps or exclusions. | Without indemnification, a party may bear significant legal expenses for the counterparty's mistakes. |
| `insurance` | MEDIUM | An insurance clause ensures that risks are backed by financial guarantees from third parties. | Require the counterparty to maintain relevant insurance (e.g., liability, workers' comp) and provide certificates. | Without insurance, a party may have to pay directly for damages if the other party is insolvent. |
| `notice_period` | *(unmapped — intentionally, per CLAUDE.md: Ilham's "Notice" clause covers formal communications, not a termination notice period, so it was never reconciled to this clause ID)* | | | |
| `lease_term` | MEDIUM | Defines the duration of the lease. | Ensure the lease term has clear start and end dates. | Prevents tenancy disputes regarding duration. |
| `rent_amount` | HIGH | Specifies the rental payment obligation. | State the exact rent amount, currency, and due date. | Establishes clear cash flow obligations. |
| `security_deposit` | MEDIUM | Secures the landlord against property damage or default. | Define deposit amount, terms of return, and holding details. | Protects owner's capital asset. |
| `maintenance_responsibility` | MEDIUM | Allocates repair and upkeep duties. | Clearly allocate structural vs non-structural repairs. | Controls property upkeep costs. |
| `license_grant` | HIGH | Grants the legal right to use software/IP. | Specify if scope is non-exclusive, worldwide, or revocable. | Defines product monetization boundaries. |
| `ip_ownership` | CRITICAL | Retains or transfers ownership of IP. | Ensure IP ownership remains with developer unless transferred. | Protects core business intellectual property asset. |
| `warranty_disclaimer` | HIGH | Limits liability for product defects. | Include standard UCC disclaimers (merchantability, fitness for purpose). | Prevents litigation on performance expectations. |
| `default_provisions` | MEDIUM | Defines what constitutes default. | State default triggers and cure periods (typically 15-30 days). | Provides clean remedy paths on breach. |
| `capital_contribution` | MEDIUM | Specifies the capital funding requirements. | Specify each partner's cash or property contribution. | Ensures clear capitalization framework. |
| `profit_sharing` | HIGH | Sets rules for distributing profit/loss. | Ensure profit allocation matches ownership share. | Governs distribution of company earnings. |
| `goods_description` | MEDIUM | Defines what products are sold. | Specify goods descriptions by reference to an exhibit. | Aligns buyer/seller expectations. |
| `return_of_materials` | MEDIUM | Obligates return of assets on contract end. | Allow option to return or destroy confidential info. | Ensures post-termination IP cleanup. |
| `title_transfer` | MEDIUM | Specifies when ownership transfers. | Align title transfer with delivery and risk of loss. | Determines asset liability cutoff points. |
| `management_rights` | MEDIUM | Defines voting and operational control. | Allocate decision-making structures clearly. | Prevents governance gridlocks. |
| `entire_agreement` | LOW | An entire agreement clause confirms that the written contract contains all agreed terms, superseding prior discussions. | Include this clause to prevent claims based on earlier oral or written promises not in the contract. | Without it, a party may assert that side agreements or prior statements are binding. |

- [ ] Reviewer: _______________ Date: _______________
- [ ] ☐ Approve as-is ☐ Approve with noted revisions (list below) ☐ Needs rework
- Notes:

---

## D. Risk-score ground truth (full 33-fixture table)

The deterministic L3 scorer (`ldv-backend/detector/detector_scorer.py`) produces a 0-100 score per document. **No fixture currently has a lawyer-reviewed expected score** — every score below is reported as `PENDING` (actual computed value shown, no pass/fail claim), by design, to avoid inventing ground truth. This is the complete, current output of `ldv-backend/tests/original11_corpus_report.json` (2026-07-22 run, 33/33 target fixtures, 0 known classifier bugs).

| Profile | Fixture | Identification | Mandatory Clauses | Dangerous Clauses | Risk Score (actual — PENDING ground truth) | Recommendations | PDF |
|---|---|---|---|---|---|---|---|
| `employment_contract` | `pdf/01_employment_id.pdf` | PASS | 3/7 present (missing: governing_law, jurisdiction_venue, notice_period, dispute_resolution) | informational: 0 fired | 45 (MEDIUM) | PASS | PASS |
| `employment_contract` | `txt/01_employment_id.txt` | PASS | 2/7 present (missing: governing_law, jurisdiction_venue, termination, notice_period, dispute_resolution) | informational: 0 fired | 60 (MEDIUM) | PASS | PASS |
| `employment_contract` | `txt/11_low_risk_employment_en.txt` | PASS | 4/7 present (missing: jurisdiction_venue, termination, dispute_resolution) | informational: 0 fired | 46 (MEDIUM) | PASS | PASS |
| `lease_agreement` | `pdf/02_lease_be.pdf` | PASS | 5/8 present (missing: jurisdiction_venue, maintenance_responsibility, dispute_resolution) | informational: 0 fired | 41 (MEDIUM) | PASS | PASS |
| `lease_agreement` | `txt/02_lease_be.txt` | PASS | 4/8 present (missing: jurisdiction_venue, lease_term, maintenance_responsibility, dispute_resolution) | informational: 0 fired | 51 (MEDIUM) | PASS | PASS |
| `lease_agreement` | `txt/13_medium_risk_lease_nl.txt` | PASS | 2/8 present (missing: jurisdiction_venue, lease_term, security_deposit, maintenance_responsibility, termination, dispute_resolution) | informational: 0 fired | 76 (HIGH) | PASS | PASS |
| `software_license` | `txt/bench_software_license_pos.txt` | PASS | 6/8 present (missing: termination, dispute_resolution) | informational: 0 fired | 30 (LOW) | PASS | PASS |
| `software_license` | `txt/bench_software_license_neg.txt` | PASS | 6/8 present (missing: termination, dispute_resolution) | PASS | 63 (HIGH) | PASS | PASS |
| `software_license` | `txt/08_medium_risk_partial_en.txt` | PASS | 4/8 present (missing: jurisdiction_venue, warranty_disclaimer, termination, dispute_resolution) | informational: 0 fired | 53 (MEDIUM) | PASS | PASS |
| `service_agreement` | `docx/01_service_agreement_en.docx` | PASS | 5/7 present (missing: jurisdiction_venue, termination) | informational: 0 fired | 31 (MEDIUM) | PASS | PASS |
| `service_agreement` | `txt/06_high_risk_leonine_en.txt` | PASS | 5/7 present (missing: jurisdiction_venue, dispute_resolution) | PASS | 99 (CRITICAL) | PASS | PASS |
| `service_agreement` | `txt/15_critical_risk_no_law_en.txt` | PASS | 6/7 present (missing: scope_of_services) | informational: 3 fired | 100 (CRITICAL) | PASS | PASS |
| `consulting_agreement` | `txt/bench_consulting_agreement_pos.txt` | PASS | 6/7 present (missing: dispute_resolution) | informational: 0 fired | 31 (MEDIUM) | PASS | PASS |
| `consulting_agreement` | `txt/bench_consulting_agreement_neg.txt` | PASS | 6/7 present (missing: dispute_resolution) | PASS | 64 (HIGH) | PASS | PASS |
| `consulting_agreement` | `txt/07_high_risk_missing_clauses_en.txt` | PASS | 5/7 present (missing: jurisdiction_venue, confidentiality) | informational: 0 fired | 23 (LOW) | PASS | PASS |
| `commercial_agreement` | `txt/bench_commercial_agreement_pos.txt` | PASS | 4/6 present (missing: limitation_liability, dispute_resolution) | informational: 0 fired | 51 (MEDIUM) | PASS | PASS |
| `commercial_agreement` | `txt/bench_commercial_agreement_neg.txt` | PASS | 5/6 present (missing: dispute_resolution) | PASS | 56 (MEDIUM) | PASS | PASS |
| `commercial_agreement` | `docx/bench_commercial_agreement_pos.docx` | PASS | 4/6 present (missing: limitation_liability, dispute_resolution) | informational: 0 fired | 51 (MEDIUM) | PASS | PASS |
| `non_disclosure_agreement` | `pdf/03_nda_en.pdf` | PASS | 3/6 present (missing: jurisdiction_venue, return_of_materials, dispute_resolution) | informational: 0 fired | 41 (MEDIUM) | PASS | PASS |
| `non_disclosure_agreement` | `txt/14_low_risk_nda_en.txt` | PASS | 3/6 present (missing: termination, return_of_materials, dispute_resolution) | informational: 0 fired | 48 (MEDIUM) | PASS | PASS |
| `non_disclosure_agreement` | `docx/03_nda_nl.docx` | PASS | 2/6 present (missing: jurisdiction_venue, termination, return_of_materials, dispute_resolution) | informational: 0 fired | 48 (MEDIUM) | PASS | PASS |
| `loan_agreement` | `txt/bench_loan_agreement_pos.txt` | PASS | 6/8 present (missing: termination, dispute_resolution) | informational: 0 fired | 30 (LOW) | PASS | PASS |
| `loan_agreement` | `txt/bench_loan_agreement_neg.txt` | PASS | 6/8 present (missing: termination, dispute_resolution) | PASS | 63 (HIGH) | PASS | PASS |
| `loan_agreement` | `txt/09_medium_risk_no_venue_en.txt` | PASS | 5/8 present (missing: jurisdiction_venue, termination, dispute_resolution) | informational: 0 fired | 38 (MEDIUM) | PASS | PASS |
| `partnership_agreement` | `txt/bench_partnership_agreement_pos.txt` | PASS | 6/7 present (missing: dispute_resolution) | informational: 0 fired | 15 (LOW) | PASS | PASS |
| `partnership_agreement` | `txt/bench_partnership_agreement_neg.txt` | PASS | 6/7 present (missing: dispute_resolution) | PASS | 48 (MEDIUM) | PASS | PASS |
| `partnership_agreement` | `docx/bench_partnership_agreement_pos.docx` | PASS | 6/7 present (missing: dispute_resolution) | informational: 0 fired | 15 (LOW) | PASS | PASS |
| `purchase_agreement` | `txt/bench_purchase_agreement_pos.txt` | PASS | 6/8 present (missing: warranty, dispute_resolution) | informational: 1 fired | 60 (MEDIUM) | PASS | PASS |
| `purchase_agreement` | `txt/bench_purchase_agreement_neg.txt` | PASS | 6/8 present (missing: warranty, dispute_resolution) | PASS | 93 (CRITICAL) | PASS | PASS |
| `purchase_agreement` | `pdf/bench_purchase_agreement_pos.pdf` | PASS | 5/8 present (missing: jurisdiction_venue, warranty, dispute_resolution) | informational: 1 fired | 68 (HIGH) | PASS | PASS |
| `general_contract` | `docx/04_legal_memo_en.docx` | PASS | 1/6 present (missing: governing_law, jurisdiction_venue, payment_terms, termination, dispute_resolution) | informational: 0 fired | 70 (HIGH) | PASS | PASS |
| `general_contract` | `docx/06_memo_fr.docx` | PASS | 2/6 present (missing: jurisdiction_venue, payment_terms, termination, dispute_resolution) | informational: 0 fired | 58 (MEDIUM) | PASS | PASS |
| `general_contract` | `txt/04_long_agreement_en.txt` | PASS | 5/6 present (missing: jurisdiction_venue) | informational: 0 fired | 40 (MEDIUM) | PASS | PASS |

**Ask:** for each row (or a representative sample), does the actual score/label look legally reasonable given the clauses present/missing? Where it doesn't, what should the correct score/label be, and why (which clause weight is off)?

- [ ] Reviewer: _______________ Date: _______________
- Fixtures reviewed: _____ / 33
- Notes / corrected scores:

---

## E. Recommendation-wording spot-check (full 13-entry red-flag guidance table)

Every red flag finding carries a `suggested_correction` drawn from `_RED_FLAG_GUIDANCE` in `detector/risk_explainer.py` (missing-clause findings instead pull from Section C above via `clause_db.py`). Engineering has only verified these are *present* (non-empty) on every finding — not that the legal wording is correct or appropriately hedged for a non-lawyer end user. This is the complete, current content of `_RED_FLAG_GUIDANCE`.

| Flag ID | Reason | Suggested Correction (verbatim) |
|---|---|---|
| `leonine_profit` | Allocating all profits to a single party breaches the principle of mutual benefit and can render the agreement void as a leonine clause under most civil-law systems. | Profits shall be distributed proportionally to each party's contribution as set out in Schedule A. No party may be excluded from losses while retaining the right to profits. |
| `leonine_no_loss` | A leonine clause that shields one party from any loss undermines the shared-risk nature of the agreement and is frequently unenforceable. | Each party shall bear losses in proportion to their respective investment or contribution share as defined herein. |
| `excessive_penalty` | A penalty rate this high functions as a punitive damages clause rather than a genuine pre-estimate of loss, and courts in many jurisdictions will reduce or strike it. | Late payment interest shall not exceed 0.5% per month (6% per annum), calculated on the overdue outstanding amount. |
| `rights_waiver` | A blanket waiver of all legal rights is overly broad, may be unenforceable against mandatory consumer or employment protections, and leaves the waiving party without recourse. | Each party retains all statutory rights and remedies afforded under applicable law. No general waiver of rights is granted by this agreement. |
| `unilateral_modification` | Letting one party amend the agreement at will, without the other's consent, removes the mutuality required for a binding contract and exposes the other party to unpredictable terms. | This agreement may only be amended by a written instrument signed by authorised representatives of all parties, with a minimum notice period of 30 days. |
| `total_liability_exclusion` | Excluding all liability regardless of cause typically fails against gross negligence, willful misconduct, or statutory protections, and signals a serious imbalance of risk. | The total aggregate liability of either party shall not exceed the total fees paid under this agreement in the 12 months preceding the event giving rise to liability. |
| `auto_renewal_no_notice` | Automatic renewal with little or no notice traps the counterparty into a new term before they can reasonably evaluate the relationship, and violates consumer-protection notice requirements in several jurisdictions. | This agreement renews automatically for successive 12-month terms unless either party provides written notice of non-renewal at least 60 days before the current term expires. |
| `short_payment_window_high` | A payment window this short (days or hours) gives the paying party little room to process invoices and creates disproportionate default/penalty risk for routine delays. | Payment shall be due within thirty (30) days of the invoice date ("Net 30"), unless a different term is expressly agreed in writing by both parties. |
| `short_payment_window_medium` | An 8-14 day payment window is tighter than standard commercial terms and can create cash-flow strain and inadvertent default risk. | Payment shall be due within thirty (30) days of the invoice date ("Net 30"), unless a shorter cycle is expressly justified by the nature of the transaction. |
| `customer_pays_vendor_errors` | Shifting the cost of the vendor's own mistakes onto the customer removes the vendor's incentive for quality control and is an unusual departure from standard risk allocation. | The Vendor shall bear, at no cost to the Customer, all expenses arising from the correction of errors or defects caused by the Vendor's own acts or omissions. |
| `fee_for_dispute` | Charging a fee merely to raise a complaint or dispute discourages legitimate claims and may be viewed as an unfair barrier to access to justice. | Either party may raise a dispute under this agreement without payment of any fee. Dispute-resolution costs shall be allocated as set out in the Dispute Resolution clause. |
| `no_liability_intentional` | Excluding liability for intentional or grossly negligent conduct is void as against public policy in most legal systems — a party cannot contract out of liability for its own bad faith. | Nothing in this agreement excludes or limits either party's liability for intentional misconduct, fraud, or gross negligence; the liability limits in this agreement apply only to ordinary negligence. |
| `illegal_object` | The contract references activity that is criminal or otherwise illegal; an agreement with an illegal object is void and unenforceable in its entirety. | Remove the illegal subject matter immediately and have counsel review whether the remainder of the contract is severable. |

**Ask:** for each row, is the wording legally accurate and appropriately hedged for a non-lawyer end user reading it inside a report (not "you must," but advisory language)?

- [ ] Reviewer: _______________ Date: _______________
- Rows reviewed: _____ / 13
- Notes:

---

## F. Legal citations — full table, already complete, no action needed

`datasets/legal_citations.csv`: **87/87 rows `status=verified`.**
> **Reconciliation Caveat on Citation Coverage:** While 100% of the 87 existing rows in `datasets/legal_citations.csv` are marked `verified`, this figure reflects row integrity within the active citation database, **not 100% overall profile coverage**. As documented in `docs/lightml/CONSISTENCY_REPORT.md` and `docs/LEGAL_CITATION_VERIFICATION.md`, 12 profiles in the registry still have required clauses (such as `jurisdiction_venue` and `notice_period`) lacking statutory citations, logged as "Evidence Not Found" in the gap tracker. The "87/87 verified" claim applies strictly to existing DB rows.


| Finding ID | Jurisdiction | Article/Reference | Source | Note |
|---|---|---|---|---|
| `leonine_profit` | FR | Art. 1844-1 | French Code civil | Clause léonine attribuant tout le profit à un associé réputée non écrite |
| `leonine_profit` | ID | Pasal 1635 | KUHPerdata (Indonesian Civil Code) | Perjanjian leonine yang memberi seluruh keuntungan ke satu pihak dilarang |
| `leonine_profit` | generic | — | — | One-sided profit allocation; leonine clauses are void in most civil-law systems |
| `leonine_no_loss` | FR | Art. 1844-1 | French Code civil | Exonération totale d'un associé des pertes réputée non écrite |
| `leonine_no_loss` | ID | Pasal 1635 | KUHPerdata (Indonesian Civil Code) | Klausul yang membebaskan sekutu dari seluruh kerugian = leonine terlarang |
| `leonine_no_loss` | generic | — | — | Investor bearing no loss is a leonine term, generally unenforceable |
| `excessive_penalty` | FR | Art. 1231-5 | French Code civil | Le juge peut réduire une clause pénale manifestement excessive |
| `excessive_penalty` | BE | Art. 5.88 | Belgian Civil Code, Book 5 | Reduction of a manifestly excessive penalty clause |
| `excessive_penalty` | ID | Pasal 1309 | KUHPerdata (Indonesian Civil Code) | Hakim dapat mengurangi ganti rugi yang berlebihan |
| `excessive_penalty` | generic | — | — | Penalty rates this high are typically reducible by a court |
| `rights_waiver` | FR | Art. 1171 | French Code civil | Clause d'un contrat d'adhésion créant un déséquilibre significatif réputée non écrite |
| `rights_waiver` | generic | — | — | Blanket waiver of legal rights is often unenforceable as an unfair term |
| `unilateral_modification` | FR | Art. 1171 | French Code civil | Déséquilibre significatif — clause réputée non écrite |
| `unilateral_modification` | generic | — | — | Unilateral modification without notice is commonly treated as abusive |
| `total_liability_exclusion` | FR | Art. 1170 | French Code civil | Clause privant de sa substance l'obligation essentielle réputée non écrite |
| `total_liability_exclusion` | generic | — | — | Total exclusion of liability is frequently struck down, especially for the essential obligation |
| `no_liability_intentional` | FR | Art. 1231-3 | French Code civil | Pas d'exonération de responsabilité en cas de dol (faute intentionnelle) |
| `no_liability_intentional` | generic | — | — | Liability for intentional fault cannot be excluded by contract |
| `illegal_object` | FR | Art. 1162 | French Code civil | Le contrat ne peut déroger à l'ordre public par son contenu |
| `illegal_object` | ID | Pasal 1320 & 1337 | KUHPerdata (Indonesian Civil Code) | Sebab yang halal diperlukan; perjanjian dengan sebab terlarang batal |
| `illegal_object` | BE | Art. 5.51 | Belgian Civil Code, Book 5 | A contract requires a lawful object/content |
| `illegal_object` | generic | — | — | An unlawful object voids the contract |
| `governing_law` | generic | — | — | Absence of a governing-law clause creates conflict-of-laws uncertainty over the applicable law |
| `dispute_resolution` | generic | — | — | Without a dispute-resolution clause, parties default to ordinary court litigation |
| `scope_of_services` | ID | Pasal 1320, Pasal 1338 | KUH Perdata (Indonesian Civil Code) | Syarat sah perjanjian dan kebebasan berkontrak; prinsip umum hukum kontrak |
| `payment_terms` | ID | Pasal 1234 | KUH Perdata (Indonesian Civil Code) | KUH Perdata tentang perikatan dan pembayaran; regulasi sektor terkait jika berlaku |
| `termination` | ID | Pasal 1320, Pasal 1338 | KUH Perdata (Indonesian Civil Code) | Syarat sah perjanjian dan kebebasan berkontrak; prinsip umum hukum kontrak |
| `governing_law` | ID | Pasal 1338 | KUH Perdata (Indonesian Civil Code) | Kebebasan berkontrak; hukum yang dipilih para pihak sepanjang tidak bertentangan dengan hukum yang berlaku |
| `dispute_resolution` | ID | Pasal 1338; UU No. 30/1999 (Arbitrase) | KUH Perdata (Indonesian Civil Code) | UU Arbitrase dan Alternatif Penyelesaian Sengketa; HIR/RBg untuk litigasi |
| `force_majeure` | ID | Pasal 1244, 1245 | KUH Perdata (Indonesian Civil Code) | Keadaan memaksa (force majeure) |
| `confidentiality` | ID | Pasal 1338; UU No. 30/2000 (Rahasia Dagang) | KUH Perdata (Indonesian Civil Code) | Rahasia dagang; ketentuan wanprestasi KUH Perdata |
| `limitation_liability` | ID | Pasal 1243, Pasal 1365 | KUH Perdata (Indonesian Civil Code) | Ganti rugi dan wanprestasi; perbuatan melawan hukum |
| `indemnification` | ID | Pasal 1243, Pasal 1365 | KUH Perdata (Indonesian Civil Code) | Ganti rugi dan wanprestasi; perbuatan melawan hukum |
| `insurance` | ID | UU No. 40/2014 (Perasuransian) | Indonesian statute (UU) | Ketentuan polis dan perjanjian yang berlaku |
| `assignment` | ID | Pasal 1320, Pasal 1338 | KUH Perdata (Indonesian Civil Code) | Syarat sah perjanjian dan kebebasan berkontrak |
| `amendment` | ID | Pasal 1320, Pasal 1338 | KUH Perdata (Indonesian Civil Code) | Syarat sah perjanjian dan kebebasan berkontrak |
| `entire_agreement` | ID | Pasal 1320, Pasal 1338 | KUH Perdata (Indonesian Civil Code) | Syarat sah perjanjian dan kebebasan berkontrak |
| `severability` | ID | Pasal 1320, Pasal 1338 | KUH Perdata (Indonesian Civil Code) | Syarat sah perjanjian dan kebebasan berkontrak |
| `principal_amount` | ID | Pasal 1234 | KUH Perdata (Indonesian Civil Code) | Perikatan dan pembayaran |
| `interest_rate` | ID | Pasal 1234 | KUH Perdata (Indonesian Civil Code) | Perikatan dan pembayaran |
| `repayment_schedule` | ID | Pasal 1234 | KUH Perdata (Indonesian Civil Code) | Perikatan dan pembayaran |
| `working_hours` | ID | UU No. 13/2003 (Ketenagakerjaan), as amended by UU No. 6/2023 | Indonesian statute (UU) | Peraturan ketenagakerjaan terkait |
| `compensation` | ID | UU No. 13/2003 (Ketenagakerjaan), as amended by UU No. 6/2023 | Indonesian statute (UU) | Peraturan ketenagakerjaan terkait |
| `delivery_terms` | ID | Pasal 1320, Pasal 1338 | KUH Perdata (Indonesian Civil Code) | Syarat sah perjanjian dan kebebasan berkontrak |
| `warranty` | ID | Pasal 1320, Pasal 1338 | KUH Perdata (Indonesian Civil Code) | Syarat sah perjanjian dan kebebasan berkontrak |
| `lease_term` | generic | Art. 1709 | French civil-style code | Lease term must be defined or determinable |
| `lease_term` | FR | Art. 1709 | French Code civil | Le contrat de louage doit être conclu pour un temps certain |
| `lease_term` | ID | Pasal 1548 | KUHPerdata | Perjanjian sewa-menyewa dibuat untuk waktu tertentu |
| `rent_amount` | generic | Art. 1709 | French civil-style code | Rent amount must be agreed by both parties |
| `rent_amount` | FR | Art. 1709 | French Code civil | Le bail exige l'obligation de payer un prix certain |
| `rent_amount` | ID | Pasal 1548 | KUHPerdata | Penyewa wajib membayar suatu harga sewa tertentu |
| `security_deposit` | generic | Art. 2288 | French civil-style code | Security deposit is a caution/pledge contract |
| `security_deposit` | FR | Art. 2288 | French Code civil | Dépôt de garantie ou cautionnement d'obligations |
| `security_deposit` | ID | Pasal 1820 | KUHPerdata | Penanggungan utang atau jaminan uang deposit sewa |
| `maintenance_responsibility` | generic | Art. 1719 | French civil-style code | Landlord must maintain the leased premises |
| `maintenance_responsibility` | FR | Art. 1719 | French Code civil | Le bailleur est obligé d'entretenir la chose louée |
| `maintenance_responsibility` | ID | Pasal 1550 | KUHPerdata | Pemberi sewa wajib memelihara barang sewaan |
| `license_grant` | generic | IP usage license | general law | License grant defines permissions and boundaries |
| `license_grant` | FR | Art. L122-4 | French Code de la propriété intellectuelle | Toute représentation ou reproduction intégrale ou partielle requiert autorisation |
| `license_grant` | ID | UU No. 28/2014 | UU Hak Cipta | Lisensi hak cipta harus dibuat secara tertulis |
| `ip_ownership` | generic | IP ownership rules | general law | Ownership of IP remains with creator unless assigned |
| `ip_ownership` | FR | Art. L111-1 | French Code de la propriété intellectuelle | L'auteur jouit d'un droit de propriété incorporelle exclusif |
| `ip_ownership` | ID | UU No. 28/2014 | UU Hak Cipta | Hak milik kekayaan intelektual dilindungi oleh undang-undang |
| `warranty_disclaimer` | generic | UCC 2-316 | Uniform Commercial Code | Disclaimers of implied warranties must be conspicuous |
| `warranty_disclaimer` | FR | Art. 1643 | French Code civil | Exclusion de garantie des vices cachés possible si convenue |
| `warranty_disclaimer` | ID | Pasal 1491 | KUHPerdata | Penyangkalan jaminan cacat tersembunyi dapat disepakati |
| `default_provisions` | generic | Default provisions | general law | Default clauses set the grounds for breach |
| `default_provisions` | FR | Art. 1224 | French Code civil | La résolution résulte soit d'une clause résolutoire |
| `default_provisions` | ID | Pasal 1238 | KUHPerdata | Wanprestasi memerlukan adanya pernyataan lalai |
| `capital_contribution` | generic | Art. 1832 | French civil-style code | Partners must contribute capital or industry |
| `capital_contribution` | FR | Art. 1832 | French Code civil | Les associés conviennent d'apporter des biens ou leur industrie |
| `capital_contribution` | ID | Pasal 1618 | KUHPerdata | Setiap sekutu wajib memasukkan modal ke persekutuan |
| `profit_sharing` | generic | Art. 1832 | French civil-style code | Partners must share profits and losses |
| `profit_sharing` | FR | Art. 1832 | French Code civil | Les associés partagent le bénéfice ou profit et les pertes |
| `profit_sharing` | ID | Pasal 1618 | KUHPerdata | Pembagian untung dan rugi diatur berdasarkan kontribusi modal |
| `management_rights` | generic | Management rights | general law | Management and voting rights govern the partnership |
| `management_rights` | FR | Art. 1852 | French Code civil | Les associés prennent les décisions collectives de gestion |
| `management_rights` | ID | Pasal 1636 | KUHPerdata | Pengurus persekutuan ditunjuk untuk mengelola hubungan usaha |
| `goods_description` | generic | UCC 2-201 | Uniform Commercial Code | Description of goods is required for sale validity |
| `goods_description` | FR | Art. 1583 | French Code civil | La vente est parfaite dès qu'on est convenu de la chose |
| `goods_description` | ID | Pasal 1457 | KUHPerdata | Jual beli memerlukan penentuan barang yang dijual |
| `return_of_materials` | generic | Return of materials | general law | NDA property return/destruction obligations are standard |
| `return_of_materials` | FR | Art. 1134 | French Code civil | Les conventions légalement formées tiennent lieu de loi |
| `return_of_materials` | ID | Pasal 1338 | KUHPerdata | Persetujuan yang dibuat secara sah berlaku sebagai undang-undang |
| `title_transfer` | generic | UCC 2-401 | Uniform Commercial Code | Title transfers upon physical delivery unless agreed |
| `title_transfer` | FR | Art. 1583 | French Code civil | Le transfert de propriété s'opère par l'accord sur la chose |
| `title_transfer` | ID | Pasal 1459 | KUHPerdata | Hak milik atas barang tidak pindah sebelum penyerahan |

All 87 existing database rows: `status=verified` (caveat: 12 registry profiles still have coverage gaps for required clauses, logged as Evidence Not Found). No further DB row action needed unless new citations are added.

---

## Sign-off

Once all sections above are complete, record the overall Gate 4 outcome here:

- **Gate 4 (Legal Review) status:** ☐ Not started ☐ In progress ☐ Complete
- **Overall reviewer(s):** _______________
- **Date:** _______________
- **Blocking items remaining:** _______________
