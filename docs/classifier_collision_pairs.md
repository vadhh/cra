# Classifier Collision-Pair List

Generated from `registry_v1.json`'s `classifier.competing_profiles` field (P2). Engineering-produced from registry data; legal correctness of any actual corpus text still requires Ilham's review per the 2026-07-16 mandate.

## Coverage gap

Only **13 of 56 profiles** (23%) have `competing_profiles` populated. The other 43 have no documented collision risk at all — this list is a starting point from what P2's registry migration already captured (P7 catalogue reconciliation notes), not a complete pairwise analysis. Full coverage requires a domain-expert pass identifying which of the remaining 43×55 possible pairs actually risk misclassification — out of scope for what can be derived from existing data alone.

**Every one of the 13 pairs below has an empty `negative_keywords` list on both sides.** `negative_keywords` exists in the registry schema specifically to disambiguate collisions (a keyword that should *suppress* a candidate label when present), but none of the known-colliding profiles have any configured. This is the single most actionable gap: these 13 pairs are the ones the registry itself already flags as confusable, and none of them have the field designed to resolve that confusion.

`service_agreement` is the dominant collision hub — 5 of the 13 pairs (distribution, agency, maintenance, IT services, outsourcing agreements) all collide against it, meaning it's the highest-risk generic-label fallback in the registry.

---

## Pair summary

| # | Profile A | Status | Profile B | Status | Shared vocabulary risk |
|---|---|---|---|---|---|
| 1 | distribution_agreement | draft | service_agreement | validated | "agreement", generic service language |
| 2 | purchase_agreement | validated | supply_agreement | draft | "agreement", goods/procurement language |
| 3 | agency_agreement | draft | service_agreement | validated | "agreement", generic service language |
| 4 | maintenance_contract | draft | service_agreement | validated | "maintenance agreement" is literally a service_agreement keyword too |
| 5 | it_services_contract | draft | service_agreement | validated | "services", generic service language |
| 6 | licensing_agreement | draft | software_license | validated | "license"/"licence" shared root |
| 7 | joint_venture_agreement | draft | partnership_agreement | validated | "joint venture agreement" is literally a partnership_agreement keyword too |
| 8 | outsourcing_agreement | draft | service_agreement | validated | generic service/delegation language |
| 9 | employment_contract | validated | employment_termination_agreement | draft | "employment", "kontrak kerja" root |
| 10 | agency_agreement | draft | sales_representative_agreement | draft | both are commission-based sales-representation structures |
| 11 | consulting_agreement | validated | freelance_contract | draft | both cover an individual providing paid expertise |
| 12 | cooperation_agreement | draft | partnership_agreement | validated | "perjanjian kerjasama"/"samenwerkingsovereenkomst" shared across both |
| 13 | banking_facility_agreement | draft | loan_agreement | validated | both are lender/borrower credit structures |

---

## Per-pair detail

### 1. distribution_agreement vs service_agreement
- **Differentiating rule (from hypothesis wording):** distribution_agreement requires a *reseller relationship over an assigned territory* ("distributor resells the supplier's products within an assigned territory"); service_agreement is generic labor/expertise provision with no resale or territory concept.
- **A-only signal:** "distributor", "distribution agreement", "perjanjian distribusi", "contrat de distribution"
- **B-only signal:** "maintenance agreement", "dienstverleningsovereenkomst"
- **Missing:** no negative_keywords on either side (e.g. service_agreement should list "distributor"/"territory"/"resell" as negative keywords, and vice versa).
- **Required corpus examples:** (a) a distribution contract using territory/resale/distributor language with no generic service framing, (b) a service contract using "service"/"maintenance" language with no resale/territory language, (c) a borderline case — e.g. a "service agreement" that includes an ancillary product-resale clause — to test whether the classifier over-triggers on distribution_agreement from a single incidental mention.

### 2. purchase_agreement vs supply_agreement
- **Differentiating rule:** purchase_agreement is a *one-off transactional* purchase/sale of goods or assets; supply_agreement is *ongoing/recurring delivery* from a supplier to a buyer.
- **A-only signal:** "sale agreement", "sales contract", "koopovereenkomst"
- **B-only signal:** "supplier agreement", "procurement agreement", "perjanjian pengadaan", "pasokan"
- **Missing:** no negative_keywords; the ongoing-vs-one-off distinction is a *structural/temporal* fact, not purely lexical — keyword matching alone may not reliably separate these without an NLI hypothesis contrast or explicit duration-language cues in positive_keywords (e.g. "ongoing", "recurring deliveries", "term of supply").
- **Required corpus examples:** (a) single-transaction purchase contract (fixed goods, fixed price, one delivery), (b) recurring supply contract (delivery schedule, standing order, term/renewal language), (c) borderline — a purchase agreement with installment deliveries — to test the ongoing/one-off boundary.

### 3. agency_agreement vs service_agreement
- **Differentiating rule:** agency_agreement requires an *agent acting on behalf of a principal to negotiate or conclude transactions* (a representation/authority relationship); service_agreement has no principal-agent authority component.
- **A-only signal:** "agent", "agentuur", "commercial agency", "contrat d'agence"
- **B-only signal:** "maintenance agreement", "dienstverleningsovereenkomst"
- **Missing:** no negative_keywords.
- **Required corpus examples:** (a) agency contract with explicit authority-to-negotiate/conclude-transactions language, (b) plain service contract with no representation/authority language, (c) borderline — a service contract where the provider is loosely described as representing the client — to test false-positive risk on "agent"-adjacent wording.

### 4. maintenance_contract vs service_agreement
- **Differentiating rule:** weakest boundary in the set — "maintenance agreement" is *literally listed as a service_agreement positive keyword*, directly contradicting maintenance_contract's own existence as a separate profile.
- **Missing:** this is a registry data conflict, not just a missing negative_keyword — recommend either (a) removing "maintenance agreement" from service_agreement's positive_keywords now that maintenance_contract exists as its own profile, or (b) adding "equipment"/"repair"/"upkeep" as required co-occurring terms to maintenance_contract's positive_keywords so it only fires on the narrower subset, plus adding "equipment maintenance"/"repair" as negative_keywords on service_agreement.
- **Required corpus examples:** (a) equipment/property maintenance contract (repair, upkeep, service intervals), (b) generic service agreement with no equipment/repair language, (c) borderline — an IT support contract that uses "maintenance" loosely — to test whether the fix in the point above overcorrects.

### 5. it_services_contract vs service_agreement
- **Differentiating rule:** it_services_contract requires *IT/technology-specific* service delivery (managed services, IT support); service_agreement is domain-generic.
- **A-only signal:** "managed services", "technology services agreement", "layanan it"
- **B-only signal:** "maintenance agreement", "dienstverleningsovereenkomst"
- **Missing:** no negative_keywords.
- **Required corpus examples:** (a) IT/managed-services contract with clear technology scope (SLAs, uptime, helpdesk, infrastructure), (b) non-IT service contract (e.g. cleaning, consulting-adjacent), (c) borderline — a general service contract that happens to mention "software" or "systems" once — to test over-triggering on incidental tech vocabulary.

### 6. licensing_agreement vs software_license
- **Differentiating rule:** software_license is *software-specific* (EULA, SaaS, source code); licensing_agreement is broader IP licensing (patents, trademarks, content, franosable IP) with no software requirement.
- **A-only signal:** "perjanjian lisensi", "contrat de licence" (generic)
- **B-only signal:** "eula", "saas agreement", "end user license agreement", "software licence"
- **Missing:** no negative_keywords; licensing_agreement's positive_keywords ("license agreement", "licence") heavily overlap software_license's own aliases (confirmed earlier in this session — software_license's own aliases list includes "license agreement").
- **Required corpus examples:** (a) non-software IP license (trademark, patent, media/content licensing) with zero software vocabulary, (b) software license/EULA with source-code/SaaS language, (c) borderline — a technology licensing deal that includes both software and patent rights — to test which profile wins when both signal sets are present.

### 7. joint_venture_agreement vs partnership_agreement
- **Differentiating rule:** weakest boundary alongside pair #4 — "joint venture agreement" is *literally a partnership_agreement positive keyword*. joint_venture_agreement's hypothesis specifies a *jointly-owned business entity*; partnership_agreement is broader (any business partnership, not necessarily a new jointly-owned entity).
- **Missing:** same registry data conflict as pair #4 — "joint venture agreement" should arguably be removed from partnership_agreement's positive_keywords now that joint_venture_agreement is its own profile, with negative_keywords added on both sides (partnership_agreement: "newly formed entity"/"jointly owned"; joint_venture_agreement: none obviously needed if the above is fixed).
- **Required corpus examples:** (a) JV contract explicitly forming a new jointly-owned legal entity, (b) general partnership agreement with no new-entity formation, (c) borderline — a partnership agreement that also references forming a subsidiary — to test the new-entity boundary.

### 8. outsourcing_agreement vs service_agreement
- **Differentiating rule:** outsourcing_agreement requires *transfer of an existing business function/process* to an external provider; service_agreement doesn't require an existing internal function being handed off.
- **A-only signal:** "alih daya", "perjanjian outsourcing"
- **B-only signal:** "maintenance agreement", "dienstverleningsovereenkomst"
- **Missing:** no negative_keywords.
- **Required corpus examples:** (a) BPO/outsourcing contract with explicit function-transfer language (transition, handover, transferred employees/assets), (b) plain service contract with no transfer/transition language, (c) borderline — a large-scope service contract that mentions taking over some client staff — to test the transfer-of-function threshold.

### 9. employment_contract vs employment_termination_agreement
- **Differentiating rule:** clearest boundary in the set — employment_contract governs an *ongoing* employment relationship; employment_termination_agreement governs its *end* (severance/separation terms). Low collision risk if temporal framing (start vs. end of relationship) is used as signal.
- **A-only signal:** "kontrak kerja", "work agreement"
- **B-only signal:** "phk", "separation agreement", "pemutusan hubungan kerja"
- **Missing:** no negative_keywords (e.g. employment_contract could list "termination"/"severance"/"separation" as negative keywords).
- **Required corpus examples:** (a) standard ongoing employment contract (start date, ongoing duties, compensation, no termination terms), (b) termination/severance agreement (final pay, release of claims, end date), (c) borderline — an employment contract that includes a termination-for-cause clause (routine, not itself a termination agreement) — to confirm this doesn't misfire the termination-agreement label.

### 10. agency_agreement vs sales_representative_agreement
- **Differentiating rule:** subtlest pair in the set — both are commission-based sales-representation structures. agency_agreement implies *authority to conclude transactions on the principal's behalf* (binding authority); sales_representative_agreement implies the representative *sells the principal's products* (typically without binding contractual authority — more of a referral/sales role).
- **A-only signal:** "agentuurovereenkomst", "contrat d'agence"
- **B-only signal:** "perwakilan penjualan", "sales agent agreement"
- **Missing:** no negative_keywords; both profiles are currently draft status, so neither has been empirically validated — highest-priority pair for corpus testing given how thin the lexical distinction is (both use "agent" language).
- **Required corpus examples:** (a) agency contract with explicit "authority to bind"/"conclude transactions" language, (b) sales rep contract with commission-only, no-binding-authority language, (c) borderline — a sales rep contract that also grants limited negotiation authority — to probe whether authority-to-bind is a reliable enough signal on its own.

### 11. consulting_agreement vs freelance_contract
- **Differentiating rule:** both cover an individual/firm providing paid expertise; consulting_agreement implies *advisory* engagement (strategy, expert opinion); freelance_contract implies *deliverable-based independent contractor* work (task/project completion, not necessarily advisory).
- **A-only signal:** "advisory agreement", "contrat de conseil"
- **B-only signal:** "independent contractor agreement", "kontraktor independen"
- **Missing:** no negative_keywords.
- **Required corpus examples:** (a) consulting contract framed around advice/strategy/expert recommendations, (b) freelance/contractor contract framed around specific deliverables and milestones, (c) borderline — a freelance contract for "consulting services" deliverables — to test whether framing (advisory vs. deliverable) or the word "consulting" itself dominates classification.

### 12. cooperation_agreement vs partnership_agreement
- **Differentiating rule:** cooperation_agreement's hypothesis explicitly *excludes* joint-venture/partnership formation ("collaboration... without forming a joint venture"), but its positive_keywords overlap partnership_agreement's directly: "perjanjian kerjasama" and "samenwerkingsovereenkomst" appear in **both** profiles' positive_keywords lists.
- **Missing:** direct keyword overlap between two competing profiles, not just similar vocabulary — same class of registry data conflict as pairs #4 and #7. Recommend removing the shared Indonesian/Dutch terms from one side or adding negative_keywords that key off entity-formation language (partnership_agreement: presence of formation/capital-contribution clauses as a positive signal; cooperation_agreement: explicit "no separate entity formed" as a positive signal).
- **Required corpus examples:** (a) cooperation/collaboration agreement with explicit no-new-entity, no-profit-sharing framing, (b) partnership agreement with entity formation, capital contribution, profit-sharing terms, (c) borderline — a cooperation agreement with a limited profit-sharing clause — to test the entity-formation boundary.

### 13. banking_facility_agreement vs loan_agreement
- **Differentiating rule:** banking_facility_agreement is a *regulated bank* extending a *credit facility* (revolving/drawdown structure, OJK-regulated in Indonesia); loan_agreement is broader (any lender/borrower relationship, not necessarily a bank or a facility structure).
- **A-only signal:** "ojk", "fasilitas kredit", "credit facility agreement"
- **B-only signal:** none distinctly — loan_agreement's keywords ("loan agreement", "credit agreement", "perjanjian pinjaman") are a superset that banking_facility_agreement's terms could also trigger.
- **Missing:** no negative_keywords; loan_agreement has no signal that excludes bank-facility structures, so it risks absorbing bank-facility contracts by default (banking_facility_agreement is still draft status, so this is currently expected/acceptable, but should be tracked as a known gap).
- **Required corpus examples:** (a) bank credit facility contract (revolving credit, drawdown, OJK/regulatory references), (b) simple bilateral loan agreement (non-bank lender, single disbursement), (c) borderline — a bank-issued single-disbursement term loan — to test whether "issued by a bank" alone should route to banking_facility_agreement or stay loan_agreement.

---

## Summary of registry data issues found while producing this list

1. **All 13 pairs have empty `negative_keywords`** on both sides — the field exists for exactly this purpose and is unused.
2. **3 pairs have literal keyword duplication** between competing profiles (maintenance_contract/service_agreement, joint_venture_agreement/partnership_agreement, cooperation_agreement/partnership_agreement) — the *same* keyword string appears in both profiles' `positive_keywords`, which cannot possibly disambiguate them and actively encourages misclassification toward whichever profile is checked first.
3. Only 23% of profiles have any `competing_profiles` annotation — this list is not comprehensive.

These are flagged for Ilham/joint review, not corrected unilaterally here, since resolving them requires judgment about which profile should "own" the disputed keyword — a legal/domain call, not a code fix.
