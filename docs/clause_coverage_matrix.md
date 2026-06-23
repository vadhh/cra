# Clause-Coverage Matrix (CR-11)

This matrix maps every internal clause ID within the analyzer pipeline to its corresponding name in Ilham's required-clause database (`Clause_Name`s), the L1 detection method, supported languages, and validation status.

## Clause Mapping and Support Matrix

| Internal Clause ID | Clause Title | Ilham Database Name (`Clause_Name`) | L1 Detection Method | Supported Languages | Status |
|---|---|---|---|---|---|
| `governing_law` | Governing Law | Governing Law | Regex Rule | EN, FR, ID, NL | 🟢 Complete & Verified |
| `jurisdiction_venue` | Jurisdiction / Venue | (none - unmapped by design) | Regex Rule | EN, FR, ID, NL | 🟢 Complete & Verified |
| `payment_terms` | Payment Terms | Payment Terms | Keyword Fallback | EN, FR, ID, NL | 🟢 Complete & Verified |
| `termination` | Termination | Termination | Keyword Fallback | EN, FR, ID, NL | 🟢 Complete & Verified |
| `dispute_resolution` | Dispute Resolution | Dispute Resolution | Keyword Fallback | EN, FR, ID, NL | 🟢 Complete & Verified |
| `limitation_liability` | Limitation of Liability | Liability | Keyword Fallback | EN, FR, ID, NL | 🟢 Complete & Verified |
| `confidentiality` | Confidentiality | Confidentiality | Keyword Fallback | EN, FR, ID, NL | 🟢 Complete & Verified |
| `force_majeure` | Force Majeure | Force Majeure | Keyword Fallback | EN, FR, ID, NL | 🟢 Complete & Verified |
| `compensation` | Compensation / Salary | Salary | Keyword Fallback | EN, FR, ID, NL | 🟢 Complete & Verified |
| `working_hours` | Working Hours | Working Hours | Keyword Fallback | EN, FR, ID, NL | 🟢 Complete & Verified |
| `scope_of_services` | Scope of Services | Scope of Work | Keyword Fallback | EN, FR, ID, NL | 🟢 Complete & Verified |
| `principal_amount` | Principal Amount | Loan Amount | Keyword Fallback | EN, FR, ID, NL | 🟢 Complete & Verified |
| `interest_rate` | Interest Rate | Interest Rate | Keyword Fallback | EN, FR, ID, NL | 🟢 Complete & Verified |
| `repayment_schedule` | Repayment Schedule | Repayment Schedule | Keyword Fallback | EN, FR, ID, NL | 🟢 Complete & Verified |
| `delivery_terms` | Delivery Terms | Delivery Terms | Keyword Fallback | EN, FR, ID, NL | 🟢 Complete & Verified |
| `warranty` | Warranty | Warranty | Keyword Fallback | EN, FR, ID, NL | 🟢 Complete & Verified |
| `indemnification` | Indemnification | Indemnification | Keyword Fallback | EN, FR, ID, NL | 🟢 Complete & Verified |
| `insurance` | Insurance | Insurance | Keyword Fallback | EN, FR, ID, NL | 🟢 Complete & Verified |
| `assignment` | Assignment | Assignment | Keyword Fallback | EN, FR, ID, NL | 🟢 Complete & Verified |
| `severability` | Severability | Severability | Keyword Fallback | EN, FR, ID, NL | 🟢 Complete & Verified |
| `entire_agreement` | Entire Agreement | Entire Agreement | Keyword Fallback | EN, FR, ID, NL | 🟢 Complete & Verified |
| `amendment` | Amendment | Amendment | Keyword Fallback | EN, FR, ID, NL | 🟢 Complete & Verified |
| `notice_period` | Notice Period | (none - unmapped by design) | Keyword Fallback | EN, FR, ID, NL | 🟡 Unmapped (Notice is communication, not termination period) |
| `lease_term` | Lease Term | (none - unmapped by design) | Keyword Fallback | EN, FR, ID, NL | 🟡 Unmapped Fallback (L3 missing weight applies) |
| `rent_amount` | Rent Amount | (none - unmapped by design) | Keyword Fallback | EN, FR, ID, NL | 🟡 Unmapped Fallback (L3 missing weight applies) |
| `security_deposit` | Security Deposit | (none - unmapped by design) | Keyword Fallback | EN, FR, ID, NL | 🟡 Unmapped Fallback (L3 missing weight applies) |
| `maintenance_responsibility` | Maintenance | (none - unmapped by design) | Keyword Fallback | EN, FR, ID, NL | 🟡 Unmapped Fallback (L3 missing weight applies) |
| `license_grant` | License Grant | (none - unmapped by design) | Keyword Fallback | EN, FR, ID, NL | 🟡 Unmapped Fallback (L3 missing weight applies) |
| `ip_ownership` | IP Ownership | (none - unmapped by design) | Keyword Fallback | EN, FR, ID, NL | 🟡 Unmapped Fallback (L3 missing weight applies) |
| `warranty_disclaimer` | Warranty Disclaimer | (none - unmapped by design) | Keyword Fallback | EN, FR, ID, NL | 🟡 Unmapped Fallback (L3 missing weight applies) |
| `default_provisions` | Default Provisions | (none - unmapped by design) | Keyword Fallback | EN, FR, ID, NL | 🟡 Unmapped Fallback (L3 missing weight applies) |
| `capital_contribution` | Capital Contribution | (none - unmapped by design) | Keyword Fallback | EN, FR, ID, NL | 🟡 Unmapped Fallback (L3 missing weight applies) |
| `profit_sharing` | Profit Sharing | (none - unmapped by design) | Keyword Fallback | EN, FR, ID, NL | 🟡 Unmapped Fallback (L3 missing weight applies) |
| `management_rights` | Management Rights | (none - unmapped by design) | Keyword Fallback | EN, FR, ID, NL | 🟡 Unmapped Fallback (L3 missing weight applies) |
| `goods_description` | Goods Description | (none - unmapped by design) | Keyword Fallback | EN, FR, ID, NL | 🟡 Unmapped Fallback (L3 missing weight applies) |
| `return_of_materials` | Return of Materials | (none - unmapped by design) | Keyword Fallback | EN, FR, ID, NL | 🟡 Unmapped Fallback (L3 missing weight applies) |
| `title_transfer` | Title Transfer | (none - unmapped by design) | Keyword Fallback | EN, FR, ID, NL | 🟡 Unmapped Fallback (L3 missing weight applies) |

## Key Insights
*   **Unmapped-by-design IDs**: 14 contract-profile required clause IDs are unmapped to Ilham's required-clauses database. Because they do not exist in her CSV, they correctly fall back to the standard `_W_MISSING_REQUIRED` severity weight in the Layer 3 scorer.
*   **Boilerplate / Cross-cutting clauses**: 6 boilerplate clause IDs (`indemnification`, `insurance`, `assignment`, `severability`, `entire_agreement`, `amendment`) are fully mapped and verified, dynamically attaching guidance rationales.
