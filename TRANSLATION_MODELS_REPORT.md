# Offline Translation Models Setup — Verification Report

This report documents the download, conversion, registry, and routing verification for the expanded translation model library in the offline Translation Service.

---

## 1. Summary of Translation Model Library

### 1.1. Models Downloaded & Converted
The local models directory `/app/models` now contains seven distinct MarianMT models, converted to CTranslate2 INT8 format for optimal CPU-only execution:

1.  **Helsinki-NLP/opus-mt-id-en**: Indonesian to English (Direct)
2.  **Helsinki-NLP/opus-mt-fr-en**: French to English (Direct)
3.  **Helsinki-NLP/opus-mt-nl-en**: Dutch to English (Direct)
4.  **Helsinki-NLP/opus-mt-mul-en**: Multilingual to English (Fallback)
5.  **Helsinki-NLP/opus-mt-en-id**: English to Indonesian (Direct, *NEW*)
6.  **Helsinki-NLP/opus-mt-en-fr**: English to French (Direct, *NEW*)
7.  **Helsinki-NLP/opus-mt-en-nl**: English to Dutch (Direct, *NEW*)

### 1.2. Disk Usage
*   **Total local model library size**: **2.8 GB** (original PyTorch weight binaries plus optimized CTranslate2 INT8 serialized formats).

---

## 2. Bidirectional Translation Routing Matrix

Direct models handle translations where one side of the language pair is English. Any non-English to non-English translation automatically pivots through English:

| Source Lang | Target Lang | Mode | Routing Strategy |
| :--- | :--- | :--- | :--- |
| **EN** | **ID** | Direct | `en-id` |
| **ID** | **EN** | Direct | `id-en` |
| **EN** | **FR** | Direct | `en-fr` |
| **FR** | **EN** | Direct | `fr-en` |
| **EN** | **NL** | Direct | `en-nl` |
| **NL** | **EN** | Direct | `nl-en` |
| **ID** | **FR** | Pivot | `id-en` → `en-fr` |
| **FR** | **ID** | Pivot | `fr-en` → `en-id` |
| **ID** | **NL** | Pivot | `id-en` → `en-nl` |
| **NL** | **ID** | Pivot | `nl-en` → `en-id` |
| **FR** | **NL** | Pivot | `fr-en` → `en-nl` |
| **NL** | **FR** | Pivot | `nl-en` → `en-fr` |

---

## 3. Verification & Execution Results

All 12 translation routes were fully verified within the Docker runtime environment using the test suite. All tests successfully generated non-empty, contextually correct translations:

-   `✅ EN -> ID`: `Ini adalah perjanjian kontrak.`
-   `✅ ID -> EN`: `This is a contract.`
-   `✅ EN -> FR`: `C'est un contrat.`
-   `✅ FR -> EN`: `This is a contract.`
-   `✅ EN -> NL`: `Dit is een contract.`
-   `✅ NL -> EN`: `This is an agreement.`
-   `✅ ID -> FR (Pivot)`: `C'est un contrat.`
-   `✅ FR -> ID (Pivot)`: `Ini adalah kontrak.`
-   `✅ ID -> NL (Pivot)`: `Dit is een contract.`
-   `✅ NL -> ID (Pivot)`: `Ini adalah kesepakatan.`
-   `✅ FR -> NL (Pivot)`: `Dit is een contract.`
-   `✅ NL -> FR (Pivot)`: `C'est un accord.`

---

## 4. Model Registry Configuration
The central models database [metadata.json](file:///mnt/c/Users/ADVAN/cra/lightml-translator/models/metadata.json) has been updated with SHA256 checksums, local folders, and target schemas for all 7 models.
The legal license clearances have been generated in [license_report.md](file:///mnt/c/Users/ADVAN/cra/lightml-translator/license_report.md) under standard `CC-BY-4.0` attribution guidelines.
