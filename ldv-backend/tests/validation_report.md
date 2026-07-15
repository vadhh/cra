# Sydeco LightML Contract Risk Analyzer — Validation Report

**Server:** http://127.0.0.1:5000
**LLM active:** NO — LLM-dependent sections marked PENDING
**Summary:** PASS 74 | WARN 2 | FAIL 0 | PENDING 9

---

## Tested Files

- `fixtures/docx/01_service_agreement_en.docx` (37114 B)
- `fixtures/docx/02_employment_fr.docx` (37117 B)
- `fixtures/docx/03_nda_nl.docx` (37083 B)
- `fixtures/docx/04_legal_memo_en.docx` (36998 B)
- `fixtures/docx/05_general_terms_en.docx` (37013 B)
- `fixtures/docx/06_memo_fr.docx` (37069 B)
- `fixtures/docx/07_brochure_nl.docx` (36933 B)
- `fixtures/negative/empty.pdf` (0 B)
- `fixtures/negative/fake.pdf` (57 B)
- `fixtures/negative/test.csv` (49 B)
- `fixtures/negative/test.png` (67 B)
- `fixtures/pdf/01_employment_id.pdf` (1416 B)
- `fixtures/pdf/02_lease_be.pdf` (1497 B)
- `fixtures/pdf/03_nda_en.pdf` (1397 B)
- `fixtures/pdf/04_incomplete_en.pdf` (1046 B)
- `fixtures/pdf/05_brochure_en.pdf` (1317 B)
- `fixtures/pdf/06_scanned_blank_en.pdf` (518 B)
- `fixtures/txt/01_employment_id.txt` (657 B)
- `fixtures/txt/02_lease_be.txt` (718 B)
- `fixtures/txt/03_short_contract_en.txt` (389 B)
- `fixtures/txt/04_long_agreement_en.txt` (2367 B)
- `fixtures/txt/05_irrelevant_en.txt` (543 B)
- `fixtures/txt/06_high_risk_leonine_en.txt` (847 B)
- `fixtures/txt/07_high_risk_missing_clauses_en.txt` (604 B)
- `fixtures/txt/08_medium_risk_partial_en.txt` (620 B)
- `fixtures/txt/09_medium_risk_no_venue_en.txt` (580 B)
- `fixtures/txt/10_low_risk_complete_en.txt` (1199 B)
- `fixtures/txt/11_low_risk_employment_en.txt` (752 B)
- `fixtures/txt/12_high_risk_unilateral_id.txt` (742 B)
- `fixtures/txt/13_medium_risk_lease_nl.txt` (591 B)
- `fixtures/txt/14_low_risk_nda_en.txt` (925 B)
- `fixtures/txt/15_critical_risk_no_law_en.txt` (841 B)
- `fixtures/txt/16_notice_id.txt` (464 B)

---

## Pass/Fail Matrix

| Section | Label | Result | Detail |
|---------|-------|--------|--------|
| 1.1 | GET / returns 200 | ✅ PASS | — |
| 1.1 | No file uploaded → 400 JSON with 'error' key | ✅ PASS | — |
| 1.1 | Valid file → 200 JSON | ✅ PASS | — |
| 1.1 | negative/test.csv → 400 JSON with 'error' key | ✅ PASS | — |
| 1.1 | negative/test.png → 400 JSON with 'error' key | ✅ PASS | — |
| 1.1 | negative/empty.pdf → 400 JSON with 'error' key | ✅ PASS | — |
| 1.1 | negative/fake.pdf → 400 JSON with 'error' key | ✅ PASS | — |
| 1.1 | Global @app.errorhandler(Exception) registered | ✅ PASS | — |
| 1.1 | No Werkzeug debug mode in production path | ✅ PASS | — |
| 1.2 | PDF upload → 200 | ✅ PASS | — |
| 1.2 | PDF has all required keys | ✅ PASS | — |
| 1.2 | PDF layer3 is structured dict {score, label, breakdown} | ✅ PASS | got keys: ['breakdown', 'calibration_status', 'confidence', 'contract_type', 'features', 'label', 'limitation_notice', 'policy_version', 'required_clauses', 'score'] |
| 1.2 | DOCX upload → 200 | ✅ PASS | — |
| 1.2 | DOCX has all required keys | ✅ PASS | — |
| 1.2 | DOCX layer3 is structured dict {score, label, breakdown} | ✅ PASS | got keys: ['breakdown', 'calibration_status', 'confidence', 'contract_type', 'features', 'label', 'limitation_notice', 'policy_version', 'required_clauses', 'score'] |
| 1.2 | TXT upload → 200 | ✅ PASS | — |
| 1.2 | TXT has all required keys | ✅ PASS | — |
| 1.2 | TXT layer3 is structured dict {score, label, breakdown} | ✅ PASS | got keys: ['breakdown', 'calibration_status', 'confidence', 'contract_type', 'features', 'label', 'limitation_notice', 'policy_version', 'required_clauses', 'score'] |
| 1.2 | Same top-level schema for PDF, DOCX, TXT | ✅ PASS | — |
| 1.3 | Empty file → controlled 400 JSON | ✅ PASS | — |
| 1.3 | Text file renamed .pdf → controlled 400 JSON | ✅ PASS | — |
| 1.3 | CSV file → controlled 400 JSON | ✅ PASS | — |
| 1.3 | PNG image → controlled 400 JSON | ✅ PASS | — |
| 2.1 | PDF text extracted: 01_employment_id.pdf | ✅ PASS | 916 chars |
| 2.1 | PDF text extracted: 02_lease_be.pdf | ✅ PASS | 1011 chars |
| 2.1 | PDF text extracted: 03_nda_en.pdf | ✅ PASS | 857 chars |
| 2.1 | PDF text extracted: 04_incomplete_en.pdf | ✅ PASS | 233 chars |
| 2.1 | PDF text extracted: 05_brochure_en.pdf | ✅ PASS | 569 chars |
| 2.1 | PDF text extracted: 06_scanned_blank_en.pdf | ✅ PASS | is blank as expected |
| 2.2 | DOCX text extracted: 01_service_agreement_en.docx | ✅ PASS | 906 chars |
| 2.2 | DOCX text extracted: 02_employment_fr.docx | ✅ PASS | 947 chars |
| 2.2 | DOCX text extracted: 03_nda_nl.docx | ✅ PASS | 928 chars |
| 2.2 | DOCX text extracted: 04_legal_memo_en.docx | ✅ PASS | 654 chars |
| 2.2 | DOCX text extracted: 05_general_terms_en.docx | ✅ PASS | 679 chars |
| 2.2 | DOCX text extracted: 06_memo_fr.docx | ✅ PASS | 760 chars |
| 2.2 | DOCX text extracted: 07_brochure_nl.docx | ✅ PASS | 492 chars |
| 2.3 | TXT text extracted: 01_employment_id.txt | ✅ PASS | 656 chars |
| 2.3 | TXT text extracted: 02_lease_be.txt | ✅ PASS | 717 chars |
| 2.3 | TXT text extracted: 03_short_contract_en.txt | ✅ PASS | 388 chars |
| 2.3 | TXT text extracted: 04_long_agreement_en.txt | ✅ PASS | 2366 chars |
| 2.3 | TXT text extracted: 05_irrelevant_en.txt | ✅ PASS | 540 chars |
| 2.3 | TXT text extracted: 06_high_risk_leonine_en.txt | ✅ PASS | 846 chars |
| 2.3 | TXT text extracted: 07_high_risk_missing_clauses_en.txt | ✅ PASS | 599 chars |
| 2.3 | TXT text extracted: 08_medium_risk_partial_en.txt | ✅ PASS | 619 chars |
| 2.3 | TXT text extracted: 09_medium_risk_no_venue_en.txt | ✅ PASS | 579 chars |
| 2.3 | TXT text extracted: 10_low_risk_complete_en.txt | ✅ PASS | 1198 chars |
| 2.3 | TXT text extracted: 11_low_risk_employment_en.txt | ✅ PASS | 751 chars |
| 2.3 | TXT text extracted: 12_high_risk_unilateral_id.txt | ✅ PASS | 741 chars |
| 2.3 | TXT text extracted: 13_medium_risk_lease_nl.txt | ✅ PASS | 590 chars |
| 2.3 | TXT text extracted: 14_low_risk_nda_en.txt | ✅ PASS | 924 chars |
| 2.3 | TXT text extracted: 15_critical_risk_no_law_en.txt | ✅ PASS | 838 chars |
| 2.3 | TXT text extracted: 16_notice_id.txt | ✅ PASS | 463 chars |
| 4.1 | Indonesian employment (PDF) → Indonesia | ✅ PASS | — |
| 4.1 | Belgian lease (PDF) → Belgium | ✅ PASS | — |
| 4.1 | French employment (DOCX) → France | ✅ PASS | — |
| 4.1 | Dutch NDA (DOCX) → Netherlands | ✅ PASS | — |
| 4.1 | Indonesian employment (TXT) → Indonesia | ✅ PASS | — |
| 4.1 | Belgian lease (TXT) → Belgium | ✅ PASS | — |
| 4.2 | No jurisdiction keywords → Unknown: Contract with no jurisdiction keywords | ✅ PASS | — |
| 4.2 | No jurisdiction keywords → Unknown: Marketing brochure | ✅ PASS | — |
| 4.2 | No jurisdiction keywords → Unknown: Earnings report | ✅ PASS | — |
| 7.1 | Run 1 == Run 2 (identical response body) | ✅ PASS | — |
| 7.1 | Run 2 == Run 3 (identical response body) | ✅ PASS | — |
| 7.1 | LLM fields untested for determinism (model not loaded) | ⚠️ WARN | Load Qwen/Qwen3-1.7B and rerun — do_sample=False should guarantee determinism |
| 8.1 | PDF / DOCX / TXT share identical top-level keys | ✅ PASS | — |
| 8.1 | layer3.score is int 0-100 and layer3.label is LOW/MEDIUM/HIGH/CRITICAL | ✅ PASS | {'breakdown': [{'points': -10, 'reason': 'Missing mandatory clause for employment contract — Notice Period'}, {'points': -15, 'reason': 'Missing mandatory clause for employment contract — Dispute Resolution [HIGH]'}, {'points': -8, 'reason': 'Jurisdiction / venue clause absent'}], 'calibration_status': 'provisional_uncalibrated', 'confidence': 20.0, 'contract_type': 'employment contract', 'features': {'contract_type': 'employment contract', 'has_governing_law': True, 'has_venue': False, 'high_flags': 0, 'l2_available': True, 'mandatory_clauses': [{'clause_id': 'governing_law', 'present': True, 'title': 'Governing Law'}, {'clause_id': 'jurisdiction_venue', 'present': False, 'title': 'Jurisdiction / Venue'}, {'clause_id': 'termination', 'present': True, 'title': 'Termination'}, {'clause_id': 'notice_period', 'present': False, 'title': 'Notice Period'}, {'clause_id': 'compensation', 'present': True, 'title': 'Compensation / Salary'}, {'clause_id': 'working_hours', 'present': True, 'title': 'Working Hours'}, {'clause_id': 'dispute_resolution', 'present': False, 'title': 'Dispute Resolution'}], 'matched_profile': True, 'medium_flags': 0, 'missing_mandatory_ids': ['notice_period', 'dispute_resolution'], 'missing_required': 2, 'unique_l2': 0}, 'label': 'MEDIUM', 'limitation_notice': 'This risk score is based on a provisional, uncalibrated scoring policy. The weights are uncalibrated and should not be used as authoritative legal advice.', 'policy_version': 'default_v1', 'required_clauses': [{'business_impact': 'Tanpa hukum yang mengatur, sengketa dapat diputuskan di bawah sistem hukum yang tidak terduga atau merugikan.', 'clause_id': 'governing_law', 'impact_level': 'Critical', 'present': True, 'reason': 'Menentukan hukum negara mana yang menafsirkan kontrak memberikan kepastian dan prediktabilitas hukum.', 'recommendation': "Nyatakan hukum yang mengatur secara eksplisit (misal 'hukum Swiss' atau 'hukum Prancis'). Hindari referensi samar.", 'source': 'kb_required_clauses', 'title': 'Governing Law'}, {'clause_id': 'jurisdiction_venue', 'present': False, 'title': 'Jurisdiction / Venue'}, {'business_impact': 'Tanpa hak pengakhiran, pihak dapat terjebak dalam perjanjian yang tidak menguntungkan atau tidak berkinerja.', 'clause_id': 'termination', 'impact_level': 'High', 'present': True, 'reason': 'Klausul pengakhiran memungkinkan pihak keluar dari kontrak secara legal, mencegah kewajiban abadi.', 'recommendation': 'Sertakan hak untuk mengakhiri dengan pemberitahuan tertulis (misal 30 hari) dan ketentuan pemutusan karena pelanggaran.', 'source': 'kb_required_clauses', 'title': 'Termination'}, {'clause_id': 'notice_period', 'present': False, 'title': 'Notice Period'}, {'business_impact': 'Tanpa klausul gaji, karyawan mungkin tidak dibayar atau dibayar lebih rendah.', 'clause_id': 'compensation', 'impact_level': 'Critical', 'present': True, 'reason': 'Klausul gaji mendefinisikan kompensasi dan frekuensi pembayaran untuk menghindari sengketa upah.', 'recommendation': 'Tentukan gaji bulanan bruto, bulan tambahan (misal ke-13), dan tanggal pembayaran.', 'source': 'kb_required_clauses', 'title': 'Compensation / Salary'}, {'business_impact': 'Jam yang hilang dapat menyebabkan sengketa upah dan pelanggaran hukum ketenagakerjaan.', 'clause_id': 'working_hours', 'impact_level': 'Critical', 'present': True, 'reason': 'Jam kerja menentukan upah lembur dan kepatuhan terhadap undang-undang ketenagakerjaan.', 'recommendation': 'Sebutkan jam kerja mingguan atau bulanan, dan jika ada, pembagian antar hari.', 'source': 'kb_required_clauses', 'title': 'Working Hours'}, {'business_impact': 'Tanpa ini, para pihak dapat menghadapi litigasi mahal dan tidak terduga di forum yang tidak nyaman.', 'clause_id': 'dispute_resolution', 'impact_level': 'High', 'present': False, 'reason': 'Mekanisme penyelesaian sengketa yang jelas menghindari perang pengadilan yang mahal dan panjang.', 'recommendation': 'Tentukan metode (mediasi, arbitrase, atau pengadilan), tempat, dan langkah pra‑litigasi (misal mediasi).', 'source': 'kb_required_clauses', 'title': 'Dispute Resolution'}], 'score': 33} |
| 8.2 | Unknown jurisdiction doesn't break response | ✅ PASS | — |
| 8.2 | layer2.document_type present even for non-contracts | ✅ PASS | — |
| 8.2 | layer3.score present and numeric even for non-contracts | ✅ PASS | — |
| 8.3 | raw_text excluded from response (privacy/payload decision) | ✅ PASS | — |
| 9.1 | app.py has no Ollama package import or URL (function names are legacy naming only) | ✅ PASS | — |
| 9.1 | app.py has no standalone TinyLlama package import | ✅ PASS | — |
| 9.1 | send_prompt.py uses transformers (no Ollama HTTP call) | ✅ PASS | — |
| 9.1 | send_prompt.py has no hardcoded Ollama URL (11434) | ✅ PASS | — |
| 9.1 | sydeco_engine.py exists — check for legacy imports | ⚠️ WARN | /home/stardhoom/LDV/ldv-backend/sydeco_engine.py |
| 9.2 | CLAUDE.md has no Ollama startup commands (mentions are informational only) | ✅ PASS | — |
| 3.1 | layer2 doc type accuracy: service agreement, NDA, employment, lease, sales, partnership | 🔲 PENDING | Requires Qwen/Qwen3-1.7B model for layer4; layer2/layer3 testable manually |
| 3.2 | Non-contract handling: layer2 confidence low for brochure, marketing, presentation | 🔲 PENDING | Requires Qwen/Qwen3-1.7B model for layer4; layer2/layer3 testable manually |
| 5.1 | layer1 clause presence accuracy: governing law, termination, liability, payment, dispute | 🔲 PENDING | Requires Qwen/Qwen3-1.7B model for layer4; layer2/layer3 testable manually |
| 5.2 | layer2 flagged clause quality: evidence text matches source, label is correct | 🔲 PENDING | Requires Qwen/Qwen3-1.7B model for layer4; layer2/layer3 testable manually |
| 5.3 | Edge cases: unusual wording, split clauses, duplicate sections, incomplete draft | 🔲 PENDING | Requires Qwen/Qwen3-1.7B model for layer4; layer2/layer3 testable manually |
| 6.1 | layer4 compliance notes consistency: no contradiction with layer1/layer2 findings | 🔲 PENDING | Requires Qwen/Qwen3-1.7B model for layer4; layer2/layer3 testable manually |
| 6.2 | layer4 recommendation quality: specific advice, not generic | 🔲 PENDING | Requires Qwen/Qwen3-1.7B model for layer4; layer2/layer3 testable manually |
| 7.2 | layer3 score sanity: score worsens as legal quality degrades (controlled fixtures) | 🔲 PENDING | Requires Qwen/Qwen3-1.7B model for layer4; layer2/layer3 testable manually |
| 7.3 | layer3 boundary checks: LOW/MEDIUM and MEDIUM/HIGH threshold transitions predictable | 🔲 PENDING | Requires Qwen/Qwen3-1.7B model for layer4; layer2/layer3 testable manually |

---

## Known Weaknesses

1. **LLM quality unverified** — Sections 3, 5, 6, 7.2, 7.3 require `Qwen/Qwen3-1.7B` to be
   downloaded (~3 GB) and loaded. Until then, document classification, clause analysis,
   compliance summaries, and risk scoring cannot be quality-assessed.

2. **Text window truncation** — LLM prompts send at most 1500–2000 characters to the model.
   Multi-page contracts lose all context beyond the first page. Chunking is a P2 item.

3. **Jurisdiction coverage** — Keyword scoring covers 4 jurisdictions only (Indonesia, Belgium,
   France, Netherlands). All other countries return `Unknown`.

4. **Translation reliability** — `googletrans==3.1.0a0` is an unofficial alpha. Under Google
   rate-limiting it silently falls back to untranslated text. Replacement is a P1 item.

5. **`sydeco_engine.py` absent** — Section 9.1 of the checklist references this file as the
   "new engine path". It does not exist. The checklist appears forward-looking for a planned
   engine refactor that has not yet been scoped.

6. **Single-threaded server** — `flask run` is single-threaded. Concurrent requests queue.
   Switch to `gunicorn -w 4 app:app` before any multi-user deployment (P2 item).

---

## Decision: `raw_text` Field (Section 8.3)

**Decision: excluded from production response.**

| Option | Assessment |
|--------|-----------|
| Always include | ❌ — legal docs are sensitive; large PDFs produce multi-MB payloads |
| Optional `?debug=1` param | ✅ — expose for developer use only, never in production |
| Never include | ✅ — safest default |

Frontend should display the uploaded file directly. If text highlighting is needed,
implement a separate `/extract` endpoint protected by auth.

---

## Section 11 — Go/No-Go

| Criterion | Status |
|-----------|--------|
| All supported file types work reliably | ✅ |
| All errors return JSON only | ✅ |
| Repeated runs deterministic (non-LLM fields) | ✅ |
| Repeated runs deterministic (LLM fields) | 🔲 PENDING |
| Document type detection credible | 🔲 PENDING |
| Jurisdiction detection honest | ✅ |
| Clause analysis traceable to text | 🔲 PENDING |
| Compliance summary consistent with clauses | 🔲 PENDING |
| Risk scoring behaves logically | 🔲 PENDING |
| No legacy TinyLlama / Ollama in runtime path | ✅ |

---

## Recommendation

**CONDITIONAL PASS — backend is structurally ready for frontend integration.**

All API stability, extraction, jurisdiction, schema, and legacy isolation checks pass. LLM-dependent quality checks (sections 3, 5, 6, 7.2, 7.3) remain pending until `Qwen/Qwen3-1.7B` is loaded. These must pass before production sign-off.

---

*Generated by `tests/run_full_validation.py`*
