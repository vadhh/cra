# P7 — Catalogue Reconciliation
_CRA · Afridho × Ilham · 2026-07-14 · Branch: `staging`_

> **Purpose:** Three-list reconciliation of the ~56 contract types in `registry_v1.json`
> against what is actually wired in the CRA stack today.
>
> **Scope of "fully usable":** classifier can detect it → profile resolves → correct required clauses → scored → in PDF → in frontend dropdown.
> **Action required from Ilham:** mark any legal-content gaps; add missing clause patterns or override classifier hypotheses for partially-usable types.

---

## Legend

| Symbol | Meaning |
|--------|---------|
| 🟢 | Layer present and tested |
| 🟡 | Layer partially present (aliases may match but no dedicated hypothesis or keyword set) |
| 🔴 | Layer missing |

**Columns:**

| Col | Meaning |
|-----|---------|
| **Classifier** | NLI hypothesis or keyword pattern exists for this type |
| **Profile** | Entry in `registry_v1.json` with required clauses |
| **Scorer** | Profile-aware clause-gap scoring works |
| **PDF** | PDF report renders the type label correctly |

---

## List 1 — Fully Usable (classifier + profile + scorer + PDF all wired)

These types can be reliably detected, profiled, scored, and reported from a clean upload with no manual override needed.

| # | Profile ID | Display Name | Classifier Source | Notes |
|---|------------|-------------|-------------------|-------|
| 1 | `employment_contract` | Employment Contract | NLI hypothesis + 8 keyword patterns | Best-tested type |
| 2 | `lease_agreement` | Lease Agreement | NLI hypothesis + 17 keyword patterns | Strong multilingual patterns |
| 3 | `service_agreement` | Service Agreement | NLI hypothesis + keyword patterns | |
| 4 | `consulting_agreement` | Consulting Agreement | NLI hypothesis | Keyword-backed by service_agreement overlap |
| 5 | `commercial_agreement` | Commercial Agreement | NLI hypothesis | |
| 6 | `non_disclosure_agreement` | NDA | NLI hypothesis + keyword (`non-disclosure`) | |
| 7 | `software_license` | Software License Agreement | NLI hypothesis + keyword (`software license`) | |
| 8 | `loan_agreement` | Loan Agreement | NLI hypothesis + keyword (`pret`, `loan`) | |
| 9 | `partnership_agreement` | Partnership Agreement | NLI hypothesis + keyword (`partnership`, `vennoot`) | |
| 10 | `purchase_agreement` | Purchase Agreement | NLI hypothesis + keyword (`purchase`) | |
| 11 | `general_contract` | General Contract | NLI hypothesis (fallback) | Used when no specific type matches |

**Count: 11**

---

## List 2 — Partially Usable (profile + scorer present; classifier detection unreliable or via alias only)

These types have correct required-clause profiles and will score correctly **if** the user selects the type manually or the keyword/alias accidentally fires. The NLI classifier has no dedicated hypothesis and no keyword patterns — detection is probabilistic at best.

| # | Profile ID | Display Name | Gap | Upgrade Path |
|---|------------|-------------|-----|--------------|
| 1 | `distribution_agreement` | Distribution Agreement | No NLI hypothesis. Falls back to `service_agreement` classifier. | Add NLI hypothesis; keyword `distributor`, `perjanjian distribusi` |
| 2 | `franchise_agreement` | Franchise Agreement | No NLI hypothesis or keyword. | Add hypothesis + keyword `waralaba`, `franchise` |
| 3 | `supply_agreement` | Supply Agreement | No NLI hypothesis. Overlaps with `purchase_agreement`. | Add hypothesis; keyword `supplier`, `pasokan` |
| 4 | `agency_agreement` | Agency Agreement | No NLI hypothesis. Overlaps with `service_agreement`. | Add hypothesis; keyword `agent`, `agentuur` |
| 5 | `shareholder_agreement` | Shareholder Agreement | No NLI hypothesis or keyword. | Add hypothesis + keyword `saham`, `aandeelhouder` |
| 6 | `investment_agreement` | Investment Agreement | No NLI hypothesis. | Add hypothesis + keyword `investasi`, `investissement` |
| 7 | `construction_contract` | Construction Contract | No NLI hypothesis or keyword. | Add hypothesis + keyword `konstruksi`, `bangunan` |
| 8 | `maintenance_contract` | Maintenance Contract | Alias `maintenance agreement` may fire `service_agreement`. | Add dedicated hypothesis |
| 9 | `it_services_contract` | IT Services Contract | No NLI hypothesis. May fire `service_agreement`. | Add hypothesis + keyword `managed services`, `layanan IT` |
| 10 | `data_processing_agreement` | Data Processing Agreement | No NLI hypothesis. | Add hypothesis + keyword `DPA`, `GDPR`, `pemrosesan data` |
| 11 | `intellectual_property_assignment` | IP Assignment | No NLI hypothesis or keyword. | Add hypothesis + keyword `hak cipta`, `IP assignment` |
| 12 | `licensing_agreement` | Licensing Agreement | Overlaps with `software_license`. | Add separate hypothesis; keyword `lisensi`, `licence` |
| 13 | `joint_venture_agreement` | Joint Venture Agreement | No NLI hypothesis. Overlaps with `partnership_agreement`. | Add hypothesis + keyword `usaha patungan`, `joint venture` |
| 14 | `memorandum_of_understanding` | MOU / Letter of Intent | No NLI hypothesis or keyword. | Add hypothesis + keyword `MOU`, `nota kesepahaman` |
| 15 | `subcontract_agreement` | Subcontract Agreement | No NLI hypothesis or keyword. | Add hypothesis + keyword `subkontraktor`, `sous-traitance` |
| 16 | `grant_agreement` | Grant Agreement | No NLI hypothesis or keyword. | Add hypothesis + keyword `hibah`, `subvention` |
| 17 | `settlement_agreement` | Settlement Agreement | No NLI hypothesis or keyword. | Add hypothesis + keyword `penyelesaian`, `settlement` |
| 18 | `sponsorship_agreement` | Sponsorship Agreement | No NLI hypothesis or keyword. | Add hypothesis + keyword `sponsor` |
| 19 | `event_contract` | Event Contract | No NLI hypothesis or keyword. | Add hypothesis + keyword `acara`, `event` |
| 20 | `property_management_agreement` | Property Management Agreement | No NLI hypothesis or keyword. | Add hypothesis + keyword `manajemen properti` |
| 21 | `insurance_contract` | Insurance Contract / Policy | No NLI hypothesis or keyword. | Add hypothesis + keyword `asuransi`, `polis`, `assurance` |
| 22 | `escrow_agreement` | Escrow Agreement | No NLI hypothesis or keyword. | Add hypothesis + keyword `escrow` |
| 23 | `outsourcing_agreement` | Outsourcing Agreement | No NLI hypothesis. Overlaps with `service_agreement`. | Add hypothesis + keyword `alih daya`, `outsourcing` |
| 24 | `employment_termination_agreement` | Employment Termination Agreement | No NLI hypothesis. May fire `employment_contract`. | Add hypothesis + keyword `PHK`, `pemutusan hubungan kerja` |
| 25 | `sales_representative_agreement` | Sales Representative Agreement | No NLI hypothesis. Overlaps with `agency_agreement`. | Add hypothesis + keyword `perwakilan penjualan` |
| 26 | `freelance_contract` | Freelance / Independent Contractor | No NLI hypothesis. May fire `consulting_agreement`. | Add hypothesis + keyword `freelance`, `kontraktor independen` |
| 27 | `internship_agreement` | Internship Agreement | No NLI hypothesis or keyword. | Add hypothesis + keyword `magang`, `stage` |
| 28 | `facilities_management_agreement` | Facilities Management Agreement | No NLI hypothesis or keyword. | Add hypothesis + keyword `manajemen fasilitas` |
| 29 | `logistics_agreement` | Logistics / Freight Agreement | No NLI hypothesis or keyword. | Add hypothesis + keyword `logistik`, `pengangkutan` |
| 30 | `media_production_agreement` | Media Production Agreement | No NLI hypothesis or keyword. | Add hypothesis + keyword `produksi media`, `film` |
| 31 | `advertising_agreement` | Advertising Agreement | No NLI hypothesis or keyword. | Add hypothesis + keyword `iklan`, `publicité` |
| 32 | `cooperation_agreement` | Cooperation Agreement | No NLI hypothesis. Alias `kerjasama` may fire `partnership_agreement`. | Add hypothesis; keyword `kerjasama`, `coopération` |
| 33 | `export_import_agreement` | Export / Import Agreement | No NLI hypothesis or keyword. | Add hypothesis + keyword `ekspor impor`, `Incoterms` |
| 34 | `land_acquisition_agreement` | Land Acquisition Agreement | No NLI hypothesis or keyword. | Add hypothesis + keyword `tanah`, `PPAT` |
| 35 | `hotel_management_agreement` | Hotel Management Agreement | No NLI hypothesis or keyword. | Add hypothesis + keyword `manajemen hotel` |
| 36 | `healthcare_services_agreement` | Healthcare Services Agreement | No NLI hypothesis or keyword. | Add hypothesis + keyword `kesehatan`, `layanan medis` |
| 37 | `education_services_agreement` | Education Services Agreement | No NLI hypothesis or keyword. | Add hypothesis + keyword `pendidikan`, `pelatihan` |
| 38 | `energy_supply_agreement` | Energy Supply Agreement | No NLI hypothesis or keyword. | Add hypothesis + keyword `listrik`, `PPA`, `energi` |
| 39 | `mining_agreement` | Mining / Natural Resources Agreement | No NLI hypothesis or keyword. | Add hypothesis + keyword `pertambangan`, `IUP`, `Minerba` |
| 40 | `telecommunications_agreement` | Telecommunications Agreement | No NLI hypothesis or keyword. | Add hypothesis + keyword `telekomunikasi`, `Kominfo` |
| 41 | `banking_facility_agreement` | Banking Facility Agreement | No NLI hypothesis. Overlaps with `loan_agreement`. | Add hypothesis + keyword `fasilitas kredit`, `OJK` |
| 42 | `factoring_agreement` | Factoring Agreement | No NLI hypothesis or keyword. | Add hypothesis + keyword `anjak piutang`, `factoring` |
| 43 | `storage_agreement` | Storage / Warehousing Agreement | No NLI hypothesis or keyword. | Add hypothesis + keyword `pergudangan`, `penyimpanan` |
| 44 | `research_collaboration_agreement` | Research Collaboration Agreement | No NLI hypothesis or keyword. | Add hypothesis + keyword `penelitian`, `recherche` |
| 45 | `government_procurement_contract` | Government Procurement Contract | No NLI hypothesis or keyword. | Add hypothesis + keyword `pengadaan pemerintah`, `Perpres` |

**Count: 45**

---

## List 3 — Name-Only (no implementation beyond registry entry)

These profiles exist in the registry with correct metadata but require **additional implementation** before they can be used in production (dedicated clause rules, jurisdiction-specific legal notes, test fixtures).

> ℹ️ Currently: **none** — all 56 profiles have valid required-clause lists that map to approved `_CLAUSE_RULES` IDs (confirmed by `validate_profiles.py`). The 45 "partial" entries above are functional but unreliable at detection time.

**Count: 0**

---

## Summary Table

| Category | Count | Action |
|----------|-------|--------|
| ✅ Fully usable | 11 | Ready for production |
| 🟡 Partially usable | 45 | Add NLI hypotheses + keyword patterns to `detector_distilbert.py`; Ilham to confirm legal accuracy of required-clause lists |
| 🔴 Name-only | 0 | — |
| **Total in registry** | **56** | |

---

## Recommended Next Steps for Ilham

1. **Confirm clause lists** for all 45 partial types — check that the `required_clauses` in `registry_v1.json` match the legal standard for each ID/FR/NL jurisdiction. Flag any that need additions.
2. **Prioritise NLI hypotheses** — identify which of the 45 are most commonly seen in LDV's client uploads; Afridho will add the NLI hypothesis + keyword patterns for the top N.
3. **Jurisdiction legal notes** — any profile with `"notes": ""` that has known statutory requirements (e.g. Indonesian regulations) should have those filled in by Ilham.
4. **Parity confirmation** — after clause lists are confirmed, run `validate_profiles.py` again and run the existing test suite to confirm `_CONTRACT_TYPE_PROFILES` and registry produce identical results for the 11 fully-usable types. Then `_CONTRACT_TYPE_PROFILES` can be deleted.

---

> **Restriction:** Legal correctness of clause requirements, citations, and risk calibration is not approved by Afridho alone.
> All clause-list changes require Ilham sign-off before the compat layer is removed.
