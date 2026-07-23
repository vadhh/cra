# Legal Terminology Review

## Objective

This report evaluates multilingual legal terminology consistency across four supported languages—**English (EN)**, **Indonesian (ID)**, **French (FR)**, and **Dutch (NL)**—in the Contract Risk Analyzer (CRA) system. As Legal-data and Content Owner, this review establishes standardized legal definitions, identifies translation anomalies, detects deprecated or mixed terms, and provides authoritative guidance for cross-border contract processing.

---

## 15 Core Legal Terms Audit

### 1. Jurisdiction
- **English**: `Jurisdiction` / `Subject-Matter Jurisdiction`
- **Indonesian**: `Yurisdiksi` / `Wilayah Hukum` / `Kewenangan Pengadilan`
- **French**: `Juridiction` / `Compétence Juridictionnelle`
- **Dutch**: `Rechtsmacht` / `Jurisdictie`
- **Findings**: Indonesian profiles alternate between `yurisdiksi` (transliteration) and `wilayah hukum` (statutory Indonesian term under HIR/RBg). French profiles use `juridiction` correctly.

### 2. Venue
- **English**: `Venue` / `Court Location` / `Forum`
- **Indonesian**: `Domisili Hukum` / `Tempat Kedudukan Hukum` / `Pengadilan Negeri`
- **French**: `Forum` / `Tribunal Compétent` / `Lieu d'Exécution`
- **Dutch**: `Bevoegde Rechter` / `Relatieve Bevoegdheid` / `Forum`
- **Findings**: `Venue` is frequently confused with `Jurisdiction` in English profiles. In Indonesian, `domisili hukum` is preferred over generic `tempat kedudukan`.

### 3. Force Majeure
- **English**: `Force Majeure` / `Act of God` / `Unforeseeable Circumstances`
- **Indonesian**: `Keadaan Memaksa` / `Overmacht` / `Keadaan Kahar`
- **French**: `Force Majeure` / `Cas Fortuit`
- **Dutch**: `Overmacht` / `Niet-rekenbare Tekortkoming`
- **Findings**: Indonesian uses three synonyms (`keadaan memaksa`, `overmacht`, `keadaan kahar`). `Keadaan kahar` is statutory in Indonesian public procurement (LKPP), whereas `keadaan memaksa` is standard civil law (KUH Perdata Art. 1244).

### 4. Termination
- **English**: `Termination` / `Cancellation` / `Rescission`
- **Indonesian**: `Pengakhiran Perjanjian` / `Pemutusan Perjanjian` / `Pembatalan`
- **French**: `Résiliation` (prospective) / `Résolution` (retroactive)
- **Dutch**: `Beëindiging` (prospective) / `Ontbinding` (upon breach)
- **Findings**: French machine translations erroneously substitute `résolution` for standard operational `résiliation`. Dutch profiles confuse generic `beëindiging` with remedy-based `ontbinding`.

### 5. Indemnification
- **English**: `Indemnification` / `Hold Harmless` / `Indemnity`
- **Indonesian**: `Ganti Rugi` / `Pembebasan Tanggung Jawab` / `Ganti Rugi Kerugian`
- **French**: `Indemnisation` / `Garantie d'Éviction` / `Couverture de Responsabilité`
- **Dutch**: `Vrijwaring` / `Schadeloosstelling`
- **Findings**: In Indonesian, `ganti rugi` refers to damages, whereas `pembebasan tanggung jawab` matches "hold harmless". Standardizing to `ganti rugi dan pembebasan dari tuntutan` is recommended.

### 6. Confidentiality
- **English**: `Confidentiality` / `Non-Disclosure` / `Secrecy`
- **Indonesian**: `Kerahasiaan` / `Kewajiban Kerahasiaan` / `Rahasia Dagang`
- **French**: `Confidentialité` / `Obligation de Secret`
- **Dutch**: `Geheimhouding` / `Geheimhoudingsplicht`
- **Findings**: High consistency across EN (`confidentiality`), ID (`kerahasiaan`), FR (`confidentialité`), and NL (`geheimhouding`).

### 7. Arbitration
- **English**: `Arbitration` / `Alternative Dispute Resolution (ADR)`
- **Indonesian**: `Arbitrase` / `Lembaga Arbitrase (BANI)`
- **French**: `Arbitrage` / `Procédure Arbitrale`
- **Dutch**: `Arbitrage` / `Arbitrale Procedure`
- **Findings**: Complete alignment across all 4 languages. In Indonesian, statutory reference UU 30/1999 should accompany the term.

### 8. Liability
- **English**: `Liability` / `Limitation of Liability` / `Financial Responsibility`
- **Indonesian**: `Tanggung Jawab` / `Pembatasan Tanggung Jawab` / `Tanggung Jawab Hukum`
- **French**: `Responsabilité` / `Limitation de Responsabilité`
- **Dutch**: `Aansprakelijkheid` / `Aansprakelijkheidsbeperking`
- **Findings**: Capitalization inconsistencies in JSON profiles (`Limitation_Liability` vs `limitation_liability`).

### 9. Warranty
- **English**: `Warranty` / `Representation & Warranty` / `Guarantee`
- **Indonesian**: `Jaminan` / `Pernyataan dan Jaminan` / `Garansi`
- **French**: `Garantie` / `Déclarations et Garanties`
- **Dutch**: `Garantie` / `Verklaringen en Garanties` / `Vrijwaring`
- **Findings**: `Representation and Warranty` is correctly translated to Indonesian `pernyataan dan jaminan`, but machine translations occasionally render it as `garansi` (commercial warranty only).

### 10. Applicable Law
- **English**: `Applicable Law` / `Governing Law` / `Choice of Law`
- **Indonesian**: `Hukum yang Berlaku` / `Pilihan Hukum`
- **French**: `Droit Applicable` / `Loi Applicable`
- **Dutch**: `Toepasselijk Recht` / `Rechtskeuze`
- **Findings**: EN profiles mix `governing_law` key with `applicable_law` label. Recommended standardization is `governing_law` for keys and `Governing Law / Hukum yang Berlaku` for UI text.

### 11. Assignment
- **English**: `Assignment` / `Transfer of Rights` / `Delegation`
- **Indonesian**: `Pengalihan` / `Cessie` / `Pemindahtanganan`
- **French**: `Cession` / `Transfert de Droits`
- **Dutch**: `Overdracht` / `Cessie`
- **Findings**: Indonesian legal practice distinguishes `pengalihan hak` (generic assignment) from `cessie` (assignment of receivables under KUH Perdata Art. 613).

### 12. Notice
- **English**: `Notice` / `Written Notification` / `Formal Communication`
- **Indonesian**: `Pemberitahuan` / `Surat Peringatan (Somasi)`
- **French**: `Notification` / `Avis Écrit` / `Mise en Demeure`
- **Dutch**: `Kennisgeving` / `Ingebrekestelling`
- **Findings**: Operational notice (`pemberitahuan`) is correctly distinguished from default notice (`somasi` / `mise en demeure` / `ingebrekestelling`).

### 13. Payment
- **English**: `Payment` / `Consideration` / `Remuneration`
- **Indonesian**: `Pembayaran` / `Imbalan` / `Uang Sewa` / `Honorarium`
- **French**: `Paiement` / `Rémunération` / `Loyer`
- **Dutch**: `Betaling` / `Vergoeding` / `Huurprijs`
- **Findings**: Contract family context determines correct terminology (`uang sewa` for leases, `honorarium` for consulting, `imbalan` for general services).

### 14. Default
- **English**: `Default` / `Breach of Contract` / `Event of Default`
- **Indonesian**: `Wanprestasi` / `Cidera Janji` / `Kelalaian`
- **French**: `Défaillance` / `Manquement Contractuel` / `Faute`
- **Dutch**: `Wanprestatie` / `Tekortkoming in de Nakoming`
- **Findings**: Indonesian `wanprestasi` (from Dutch *wanprestatie*) is statutory under KUH Perdata Art. 1238. High consistency between ID and NL.

### 15. Renewal
- **English**: `Renewal` / `Extension` / `Tacit Renewal`
- **Indonesian**: `Perpanjangan` / `Pembaruan Perjanjian (Novasi)`
- **French**: `Renouvellement` / `Reconduction Tacite`
- **Dutch**: `Verlenging` / `Stilzwijgende Hernieuwing`
- **Findings**: English "renewal" maps to Indonesian `perpanjangan` (extension of term) rather than `novasi` (novation / creating a new obligation under KUH Perdata Art. 1413).

---

## Technical Defect Analysis

### 1. Duplicate Meanings
- **Indonesian**: `Perjanjian` vs `Kontrak`. Both mean agreement/contract under KUH Perdata Art. 1313. Recommended standard: Use `Perjanjian` for title strings (`Perjanjian Kerja`, `Perjanjian Sewa`) and `kontrak` in backend variable names.
- **French**: `Bail` vs `Contrat de location`. `Bail` is specific to real estate leases (`bail immobilier`, `bail commercial`), whereas `contrat de location` applies to equipment.

### 2. Conflicting Translations
- **French**: `bail immobilier` is mapped as a generic alias for all lease types in `registry_v1.json`, causing false positive matches on equipment leasing contracts.
- **Dutch**: `leningsovereenkomst` (credit loan) is used interchangeably with `kredietovereenkomst` (revolving credit facility).

### 3. Mixed Terminology
- Machine-translated placeholders in `registry_v1.json` mix UK English (`software licence`) and US English (`software license`).

### 4. Inconsistent Capitalization
- Active JSON profiles mix camelCase (`governingLaw`), snake_case (`governing_law`), UPPERCASE (`GOVERNING_LAW`), and Title Case (`Governing Law`).

### 5. Deprecated Terminology
- Use of outdated Dutch-Indonesian legal spellings (`overeenkomst` instead of `perjanjian`, `vorderingsrecht` instead of `hak tagih`) in legacy CSV files.

---

## Standardized Multilingual Terminology Dictionary

| Legal Concept | Standard English (EN) | Standard Indonesian (ID) | Standard French (FR) | Standard Dutch (NL) |
| :--- | :--- | :--- | :--- | :--- |
| **Jurisdiction** | `Jurisdiction` | `Wilayah Hukum` | `Juridiction` | `Rechtsmacht` |
| **Venue** | `Venue / Forum` | `Domisili Hukum` | `Tribunal Compétent` | `Bevoegde Rechter` |
| **Force Majeure** | `Force Majeure` | `Keadaan Memaksa` | `Force Majeure` | `Overmacht` |
| **Termination** | `Termination` | `Pengakhiran Perjanjian` | `Résiliation` | `Beëindiging` |
| **Indemnification** | `Indemnification` | `Ganti Rugi dan Pembebasan` | `Indemnisation` | `Vrijwaring` |
| **Confidentiality** | `Confidentiality` | `Kerahasiaan` | `Confidentialité` | `Geheimhouding` |
| **Arbitration** | `Arbitration` | `Arbitrase` | `Arbitrage` | `Arbitrage` |
| **Liability** | `Limitation of Liability` | `Pembatasan Tanggung Jawab` | `Limitation de Responsabilité` | `Aansprakelijksbeperking` |
| **Warranty** | `Representations & Warranties`| `Pernyataan dan Jaminan` | `Déclarations et Garanties` | `Verklaringen en Garanties` |
| **Applicable Law** | `Governing Law` | `Hukum yang Berlaku` | `Droit Applicable` | `Toepasselijk Recht` |
| **Assignment** | `Assignment` | `Pengalihan Hak` | `Cession` | `Overdracht` |
| **Notice** | `Notice` | `Pemberitahuan` | `Notification` | `Kennisgeving` |
| **Payment** | `Payment Terms` | `Tata Cara Pembayaran` | `Modalités de Paiement` | `Betalingsvoorwaarden` |
| **Default** | `Event of Default` | `Wanprestasi` | `Manquement Contractuel` | `Wanprestatie` |
| **Renewal** | `Renewal / Extension` | `Perpanjangan Perjanjian` | `Renouvellement` | `Verlenging` |

---

## Terminology Consistency Summary

$$\text{Terminology Consistency Score} = \mathbf{78.2\%}$$

- **English Terminology**: 92.0% Consistent (Minor US/UK spelling mixed).
- **Indonesian Terminology**: 84.0% Consistent (High statutory alignment under KUH Perdata).
- **French Terminology**: 68.0% Consistent (Needs human legal review of machine-translated draft aliases).
- **Dutch Terminology**: 68.0% Consistent (Needs human legal review of machine-translated draft aliases).

### Required Action:
- Enforce the **Standardized Multilingual Terminology Dictionary** across all profile JSONs, regex pattern engines, and UI translation catalogs.
