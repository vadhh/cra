# Multilingual Alias Quality Classification

This document classifies every multilingual alias used by the 11 Technically Mature Profiles in the Contract Risk Analyzer (CRA) system.

## Alias Quality Standards
- **Repository-derived**: Active in the system's JSON configuration files and tested in the regression/benchmark suite.
- **Machine-translated**: Draft translation terms without documented human review in the repository.
- **Human language checked**: Verified by local language speakers for general correctness, but not yet legally reviewed.
- **Legally reviewed**: Reviewed and verified as legally equivalent by a qualified legal reviewer.
- **Formally approved**: Formally signed off as part of the legal approval process.

> [!WARNING]
> Machine translations are not verified as legally equivalent. No alias is marked **Legally reviewed** or **Formally approved** since the formal legal review is **Pending**.

## Profile: Commercial Agreement

| Language | Alias | Status | Basis in Repository | Notes |
| --- | --- | --- | --- | --- |
| English | `commercial contract` | **Human language checked** | Draft list reviewed by technical team | Needs formal legal validation |
| English | `commercial agreement` | **Repository-derived** | Active in profile JSON and covered by integration tests | Safe for system routing, human language checked |
| English | `business agreement` | **Repository-derived** | Active in profile JSON and covered by integration tests | Safe for system routing, human language checked |
| English | `trade agreement` | **Repository-derived** | Active in profile JSON and covered by integration tests | Safe for system routing, human language checked |
| Indonesian | `perjanjian komersial` | **Human language checked** | Draft list reviewed by technical team | Needs formal legal validation |
| French | *None (Evidence Not Found)* | **N/A** | No alias registered in this language | - |
| Dutch | *None (Evidence Not Found)* | **N/A** | No alias registered in this language | - |

---
## Profile: Consulting Agreement

| Language | Alias | Status | Basis in Repository | Notes |
| --- | --- | --- | --- | --- |
| English | `advisory agreement` | **Repository-derived** | Active in profile JSON and covered by integration tests | Safe for system routing, human language checked |
| English | `consultancy agreement` | **Repository-derived** | Active in profile JSON and covered by integration tests | Safe for system routing, human language checked |
| English | `consulting agreement` | **Repository-derived** | Active in profile JSON and covered by integration tests | Safe for system routing, human language checked |
| Indonesian | `perjanjian konsultan` | **Human language checked** | Draft list reviewed by technical team | Needs formal legal validation |
| French | `contrat de conseil` | **Machine-translated** | Placeholder machine translation in registry | High risk of legal mismatch. Do not use in production. |
| Dutch | *None (Evidence Not Found)* | **N/A** | No alias registered in this language | - |

---
## Profile: Employment Contract

| Language | Alias | Status | Basis in Repository | Notes |
| --- | --- | --- | --- | --- |
| English | `employment contract` | **Repository-derived** | Active in profile JSON and covered by integration tests | Safe for system routing, human language checked |
| English | `employment agreement` | **Human language checked** | Draft list reviewed by technical team | Needs formal legal validation |
| English | `work agreement` | **Human language checked** | Draft list reviewed by technical team | Needs formal legal validation |
| English | `labor contract` | **Repository-derived** | Active in profile JSON and covered by integration tests | Safe for system routing, human language checked |
| Indonesian | `kontrak kerja` | **Human language checked** | Draft list reviewed by technical team | Needs formal legal validation |
| Indonesian | `perjanjian kerja` | **Repository-derived** | Active in profile JSON and covered by integration tests | Safe for system routing, human language checked |
| French | *None (Evidence Not Found)* | **N/A** | No alias registered in this language | - |
| Dutch | *None (Evidence Not Found)* | **N/A** | No alias registered in this language | - |

---
## Profile: General Contract

| Language | Alias | Status | Basis in Repository | Notes |
| --- | --- | --- | --- | --- |
| English | `general agreement` | **Human language checked** | Draft list reviewed by technical team | Needs formal legal validation |
| English | `general contract` | **Repository-derived** | Active in profile JSON and covered by integration tests | Safe for system routing, human language checked |
| English | `contract` | **Repository-derived** | Active in profile JSON and covered by integration tests | Safe for system routing, human language checked |
| English | `agreement` | **Repository-derived** | Active in profile JSON and covered by integration tests | Safe for system routing, human language checked |
| Indonesian | `kontrak` | **Human language checked** | Draft list reviewed by technical team | Needs formal legal validation |
| Indonesian | `kontrak umum` | **Repository-derived** | Active in profile JSON and covered by integration tests | Safe for system routing, human language checked |
| Indonesian | `perjanjian` | **Repository-derived** | Active in profile JSON and covered by integration tests | Safe for system routing, human language checked |
| Indonesian | `perjanjian umum` | **Repository-derived** | Active in profile JSON and covered by integration tests | Safe for system routing, human language checked |
| French | *None (Evidence Not Found)* | **N/A** | No alias registered in this language | - |
| Dutch | *None (Evidence Not Found)* | **N/A** | No alias registered in this language | - |

---
## Profile: Lease Agreement

| Language | Alias | Status | Basis in Repository | Notes |
| --- | --- | --- | --- | --- |
| English | `tenancy agreement` | **Repository-derived** | Active in profile JSON and covered by integration tests | Safe for system routing, human language checked |
| English | `lease agreement` | **Repository-derived** | Active in profile JSON and covered by integration tests | Safe for system routing, human language checked |
| English | `property lease` | **Human language checked** | Draft list reviewed by technical team | Needs formal legal validation |
| English | `rental agreement` | **Repository-derived** | Active in profile JSON and covered by integration tests | Safe for system routing, human language checked |
| Indonesian | `perjanjian sewa` | **Human language checked** | Draft list reviewed by technical team | Needs formal legal validation |
| Indonesian | `perjanjian sewa menyewa` | **Repository-derived** | Active in profile JSON and covered by integration tests | Safe for system routing, human language checked |
| French | `bail immobilier` | **Machine-translated** | Placeholder machine translation in registry | High risk of legal mismatch. Do not use in production. |
| Dutch | `huurovereenkomst` | **Machine-translated** | Placeholder machine translation in registry | High risk of legal mismatch. Do not use in production. |

---
## Profile: Loan Agreement

| Language | Alias | Status | Basis in Repository | Notes |
| --- | --- | --- | --- | --- |
| English | `loan contract` | **Repository-derived** | Active in profile JSON and covered by integration tests | Safe for system routing, human language checked |
| English | `loan agreement` | **Repository-derived** | Active in profile JSON and covered by integration tests | Safe for system routing, human language checked |
| English | `creditor agreement` | **Human language checked** | Draft list reviewed by technical team | Needs formal legal validation |
| English | `credit agreement` | **Repository-derived** | Active in profile JSON and covered by integration tests | Safe for system routing, human language checked |
| Indonesian | `perjanjian pinjaman` | **Human language checked** | Draft list reviewed by technical team | Needs formal legal validation |
| Indonesian | `perjanjian kredit` | **Repository-derived** | Active in profile JSON and covered by integration tests | Safe for system routing, human language checked |
| French | `contrat de prêt` | **Machine-translated** | Placeholder machine translation in registry | High risk of legal mismatch. Do not use in production. |
| Dutch | `leningsovereenkomst` | **Machine-translated** | Placeholder machine translation in registry | High risk of legal mismatch. Do not use in production. |

---
## Profile: Non-Disclosure Agreement

| Language | Alias | Status | Basis in Repository | Notes |
| --- | --- | --- | --- | --- |
| English | `non-disclosure agreement` | **Repository-derived** | Active in profile JSON and covered by integration tests | Safe for system routing, human language checked |
| English | `confidentiality agreement` | **Repository-derived** | Active in profile JSON and covered by integration tests | Safe for system routing, human language checked |
| English | `geheimhouding` | **Repository-derived** | Active in profile JSON and covered by integration tests | Safe for system routing, human language checked |
| English | `nda` | **Repository-derived** | Active in profile JSON and covered by integration tests | Safe for system routing, human language checked |
| English | `NDA` | **Human language checked** | Draft list reviewed by technical team | Needs formal legal validation |
| Indonesian | `perjanjian kerahasiaan` | **Human language checked** | Draft list reviewed by technical team | Needs formal legal validation |
| French | `accord de confidentialité` | **Machine-translated** | Placeholder machine translation in registry | High risk of legal mismatch. Do not use in production. |
| Dutch | `geheimhoudingsovereenkomst` | **Machine-translated** | Placeholder machine translation in registry | High risk of legal mismatch. Do not use in production. |

---
## Profile: Partnership Agreement

| Language | Alias | Status | Basis in Repository | Notes |
| --- | --- | --- | --- | --- |
| English | `joint venture agreement` | **Repository-derived** | Active in profile JSON and covered by integration tests | Safe for system routing, human language checked |
| English | `partnership contract` | **Repository-derived** | Active in profile JSON and covered by integration tests | Safe for system routing, human language checked |
| English | `joint venture` | **Human language checked** | Draft list reviewed by technical team | Needs formal legal validation |
| English | `partnership agreement` | **Repository-derived** | Active in profile JSON and covered by integration tests | Safe for system routing, human language checked |
| Indonesian | `perjanjian kemitraan` | **Human language checked** | Draft list reviewed by technical team | Needs formal legal validation |
| Indonesian | `perjanjian kerjasama` | **Repository-derived** | Active in profile JSON and covered by integration tests | Safe for system routing, human language checked |
| French | `contrat de partenariat` | **Machine-translated** | Placeholder machine translation in registry | High risk of legal mismatch. Do not use in production. |
| Dutch | `samenwerkingsovereenkomst` | **Machine-translated** | Placeholder machine translation in registry | High risk of legal mismatch. Do not use in production. |

---
## Profile: Purchase Agreement

| Language | Alias | Status | Basis in Repository | Notes |
| --- | --- | --- | --- | --- |
| English | `purchase agreement` | **Repository-derived** | Active in profile JSON and covered by integration tests | Safe for system routing, human language checked |
| English | `sales contract` | **Repository-derived** | Active in profile JSON and covered by integration tests | Safe for system routing, human language checked |
| English | `sale agreement` | **Human language checked** | Draft list reviewed by technical team | Needs formal legal validation |
| Indonesian | `perjanjian jual beli` | **Human language checked** | Draft list reviewed by technical team | Needs formal legal validation |
| Indonesian | `perjanjian pembelian` | **Repository-derived** | Active in profile JSON and covered by integration tests | Safe for system routing, human language checked |
| French | `contrat de vente` | **Machine-translated** | Placeholder machine translation in registry | High risk of legal mismatch. Do not use in production. |
| Dutch | `koopovereenkomst` | **Machine-translated** | Placeholder machine translation in registry | High risk of legal mismatch. Do not use in production. |

---
## Profile: Service Agreement

| Language | Alias | Status | Basis in Repository | Notes |
| --- | --- | --- | --- | --- |
| English | `services agreement` | **Repository-derived** | Active in profile JSON and covered by integration tests | Safe for system routing, human language checked |
| English | `maintenance agreement` | **Repository-derived** | Active in profile JSON and covered by integration tests | Safe for system routing, human language checked |
| English | `service agreement` | **Repository-derived** | Active in profile JSON and covered by integration tests | Safe for system routing, human language checked |
| English | `MSA` | **Human language checked** | Draft list reviewed by technical team | Needs formal legal validation |
| English | `master services agreement` | **Repository-derived** | Active in profile JSON and covered by integration tests | Safe for system routing, human language checked |
| English | `service contract` | **Repository-derived** | Active in profile JSON and covered by integration tests | Safe for system routing, human language checked |
| Indonesian | `perjanjian jasa` | **Human language checked** | Draft list reviewed by technical team | Needs formal legal validation |
| French | `contrat de services` | **Machine-translated** | Placeholder machine translation in registry | High risk of legal mismatch. Do not use in production. |
| Dutch | `dienstverleningsovereenkomst` | **Machine-translated** | Placeholder machine translation in registry | High risk of legal mismatch. Do not use in production. |

---
## Profile: Software License

| Language | Alias | Status | Basis in Repository | Notes |
| --- | --- | --- | --- | --- |
| English | `software license agreement` | **Repository-derived** | Active in profile JSON and covered by integration tests | Safe for system routing, human language checked |
| English | `software license` | **Repository-derived** | Active in profile JSON and covered by integration tests | Safe for system routing, human language checked |
| English | `saas agreement` | **Human language checked** | Draft list reviewed by technical team | Needs formal legal validation |
| English | `EULA` | **Repository-derived** | Active in profile JSON and covered by integration tests | Safe for system routing, human language checked |
| English | `end user license agreement` | **Repository-derived** | Active in profile JSON and covered by integration tests | Safe for system routing, human language checked |
| English | `software licence` | **Human language checked** | Draft list reviewed by technical team | Needs formal legal validation |
| English | `eula` | **Human language checked** | Draft list reviewed by technical team | Needs formal legal validation |
| English | `license agreement` | **Human language checked** | Draft list reviewed by technical team | Needs formal legal validation |
| Indonesian | *None (Evidence Not Found)* | **N/A** | No alias registered in this language | - |
| French | *None (Evidence Not Found)* | **N/A** | No alias registered in this language | - |
| Dutch | `softwarelicentie` | **Machine-translated** | Placeholder machine translation in registry | High risk of legal mismatch. Do not use in production. |

---
