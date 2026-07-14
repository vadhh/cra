import os
import json
import csv
import tempfile
import threading
import pytest
from app.protection.legal_protection import LegalProtectionEngine
from app.protection.glossary_engine import GlossaryEngine, GlossaryTerm
from app.services.quality_analyzer import TranslationQualityAnalyzer
from app.services.translation_service import TranslationService
from app.models.schemas import TranslationResponse


# =====================================================================
# 1. LEGAL PROTECTED TERMS ENGINE TESTS
# =====================================================================

def test_legal_protection_detection_and_restore():
    """Verify that all legal protected entities are correctly masked and restored."""
    engine = LegalProtectionEngine()
    
    # Text containing HTML, Markdown, URLs, Emails, Phone, Signatures, Statutory refs,
    # Articles, Clauses, Companies, Government Agencies, Addresses, Person Names,
    # Defined Terms, Percentages, Currencies, Dates, and Numbers.
    raw_text = (
        "<html>This is a <b>document</b></html>\n"
        "Please read **Section 1.1** of the rules.\n"
        "Visit https://google.com or write to support@sydeco.com.\n"
        "Call us at +1-555-555-0199 or sign /s/ John Doe.\n"
        "According to UU No. 13/2003 and Civil Code, we must refer to Article 5.\n"
        "Clause 1.2: PT Sydeco Global and Ministry of Finance are located at 45 Main Street, Boston.\n"
        "Mr. Robert Smith and \"First Party\" agreed on 12% interest on USD 5,000 on 12-07-2026."
    )
    
    protected, p_map = engine.protect(raw_text)
    
    # Assert placeholders were injected for different categories
    assert "__LEG_PROT_" in protected
    assert "HTML" in "".join(p_map.keys())
    assert "URL" in "".join(p_map.keys())
    assert "EMAIL" in "".join(p_map.keys())
    assert "PHONE" in "".join(p_map.keys())
    assert "SIGNATURE" in "".join(p_map.keys())
    assert "STATUTORY_REF" in "".join(p_map.keys())
    assert "ARTICLE_REF" in "".join(p_map.keys())
    assert "COMPANY" in "".join(p_map.keys())
    assert "GOV_AGENCY" in "".join(p_map.keys())
    assert "ADDRESS" in "".join(p_map.keys())
    assert "PERSON" in "".join(p_map.keys())
    assert "PERCENTAGE" in "".join(p_map.keys())
    assert "CURRENCY" in "".join(p_map.keys())
    assert "DATE" in "".join(p_map.keys())
    
    # Restore and verify 100% integrity
    restored = engine.restore(protected, p_map)
    assert restored == raw_text


def test_legal_protection_collision_safety():
    """Verify that the engine handles potential placeholder collisions with unique salting."""
    engine = LegalProtectionEngine()
    
    # Text containing what looks like a placeholder
    raw_text = "This is a dummy __LEG_PROT_HTML_0__ token."
    protected, p_map = engine.protect(raw_text)
    
    # The original fake placeholder should NOT be replaced by restore unless it matched a pattern,
    # but the unique salt ensures they don't collide.
    restored = engine.restore(protected, p_map)
    assert restored == raw_text


def test_legal_protection_thread_safety():
    """Verify that LegalProtectionEngine is thread-safe across concurrent executions."""
    engine = LegalProtectionEngine()
    errors = []
    
    def worker(worker_id):
        try:
            text = f"Worker {worker_id}: Mr. John Doe is from PT Acme Corp on 12-07-2026."
            protected, p_map = engine.protect(text)
            
            # Simulate some processing delay
            import time
            time.sleep(0.01)
            
            restored = engine.restore(protected, p_map)
            assert restored == text, f"Restoration mismatch for worker {worker_id}"
        except Exception as e:
            errors.append(e)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(20)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
        
    assert len(errors) == 0, f"Thread-safety errors: {errors}"


# =====================================================================
# 2. LEGAL GLOSSARY ENGINE TESTS
# =====================================================================

def test_glossary_engine_csv_json_loader():
    """Verify CSV and JSON dictionary loaders and sector-specific glossary versioning."""
    engine = GlossaryEngine()
    
    # 1. Test CSV Loader
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8") as tf:
        csv_path = tf.name
        writer = csv.writer(tf)
        # Columns: source_term, target_term, sector, confidence, context_words
        writer.writerow(["pekerja", "employee", "Employment", "0.9", "karyawan,staf"])
        writer.writerow(["lisensi", "license", "Software", "0.85", "aplikasi"])

    try:
        success = engine.load_csv(csv_path, "id", "en", "Employment", "2.1.0")
        assert success is True
        
        # Verify term loaded with metadata
        terms = engine.get_terms("id", "en", "Employment")
        assert "pekerja" in terms
        assert terms["pekerja"] == "employee"
    finally:
        os.remove(csv_path)

    # 2. Test JSON Loader
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as tf:
        json_path = tf.name
        json.dump([
            {
                "source_term": "keadaan memaksa",
                "target_term": "force majeure",
                "sector": "Legal",
                "version": "2.2.0",
                "confidence": 0.95,
                "context_words": ["bencana", "darurat"]
            }
        ], tf)

    try:
        success = engine.load_json(json_path, "id", "en", "Legal", "2.2.0")
        assert success is True
        
        terms = engine.get_terms("id", "en", "Legal")
        assert "keadaan memaksa" in terms
        assert terms["keadaan memaksa"] == "force majeure"
    finally:
        os.remove(json_path)


def test_glossary_engine_context_awareness():
    """Verify that term selection boosts confidence dynamically based on sector and context words."""
    engine = GlossaryEngine()
    
    # Clear and set custom terms with identical source term but different sector/contexts
    engine._glossaries[("id", "en")] = [
        GlossaryTerm("suku bunga", "interest rate", "Finance", "1.0", 0.8, ["bank", "pinjaman"]),
        GlossaryTerm("suku bunga", "yield rate", "Investment", "1.0", 0.7, ["obligasi", "saham"])
    ]
    
    # Text with finance context
    text_finance = "Harap perhatikan bahwa suku bunga bank sangat rendah."
    injected, r_map, details = engine.inject_glossary(text_finance, "id", "en", sector="Finance")
    
    # The Finance candidate should win due to matching sector and context word 'bank'
    assert len(details) == 1
    assert details[0]["target"] == "interest rate"
    assert details[0]["confidence"] == 1.0  # 0.8 + 0.2 (sector) + 0.1 (context 'bank') clamped to 1.0


def test_glossary_engine_conflict_detection():
    """Verify that GlossaryEngine detects duplicate and overlapping terminology definitions."""
    engine = GlossaryEngine()
    
    # Set duplicate and overlapping terms
    engine._glossaries[("id", "en")] = [
        GlossaryTerm("pihak", "party", "Legal", "1.0", 1.0),
        GlossaryTerm("pihak", "side", "Legal", "1.0", 0.9),  # Duplicate
        GlossaryTerm("perjanjian", "agreement", "Legal", "1.0", 1.0),
        GlossaryTerm("perjanjian kerja", "employment contract", "Legal", "1.0", 1.0)  # Overlapping
    ]
    
    conflicts = engine.detect_conflicts("id", "en")
    types = [c["type"] for c in conflicts]
    
    assert "duplicate_translation" in types
    assert "overlapping_term" in types


# =====================================================================
# 3. TRANSLATION QUALITY ANALYZER TESTS
# =====================================================================

def test_quality_analyzer_checks():
    """Verify that TranslationQualityAnalyzer flags missing, modified, or distorted segments."""
    analyzer = TranslationQualityAnalyzer()
    
    source = "Pihak Pertama wajib membayar USD 1,000 pada tanggal 12-07-2026. Dia tidak boleh terlambat."
    # 1. Perfect translation comparison
    translation_good = "The First Party shall pay USD 1,000 on 12-07-2026. He must not be late."
    result_good = analyzer.analyze(source, translation_good, "id", "en", avg_confidence=0.99)
    assert result_good["quality_score"] >= 90.0
    assert result_good["risk_level"] == "LOW"
    assert len(result_good["warnings"]) == 0

    # 2. Number mismatch test
    translation_bad_num = "The First Party shall pay USD 2,500 on 12-07-2026. He must not be late."
    result_num = analyzer.analyze(source, translation_bad_num, "id", "en")
    assert result_num["quality_score"] < 90.0
    assert any("Number mismatch" in w for w in result_num["warnings"])

    # 3. Date mismatch test
    translation_bad_date = "The First Party shall pay USD 1,000 on 25-12-2026. He must not be late."
    result_date = analyzer.analyze(source, translation_bad_date, "id", "en")
    assert result_date["quality_score"] < 90.0
    assert any("Date mismatch" in w for w in result_date["warnings"])

    # 4. Polarity / Negation mismatch test
    translation_bad_neg = "The First Party shall pay USD 1,000 on 12-07-2026. He is allowed to be late."
    result_neg = analyzer.analyze(source, translation_bad_neg, "id", "en")
    assert result_neg["quality_score"] < 80.0
    assert any("Negation mismatch" in w for w in result_neg["warnings"])

    # 5. Legal meaning shift (Obligation modality mismatch)
    # Source has "wajib" (mandatory) and "tidak boleh" (mandatory).
    # Bad translation changes them to "may" (discretionary) and "may" (discretionary).
    translation_bad_modal = "The First Party may pay USD 1,000 on 12-07-2026. He may be late."
    result_modal = analyzer.analyze(source, translation_bad_modal, "id", "en")
    assert result_modal["quality_score"] < 80.0
    assert any("Legal meaning shift" in w for w in result_modal["warnings"])


# =====================================================================
# 4. INTEGRATION PIPELINE TEST
# =====================================================================

class MockTranslator:
    def translate_batch(self, batch, src, tgt, scores_out=None):
        if scores_out is not None:
            scores_out.extend([0.0] * len(batch))
        return [f"[Mocked translation for: {s}]" for s in batch]


def test_translation_service_pipeline():
    """Verify that TranslationService orchestrates the entire protection and QA pipeline."""
    translator = MockTranslator()
    service = TranslationService(translator=translator)
    
    text = "PT Sydeco Global wajib menyelesaikan kontrak ini pada tanggal 12-07-2026."
    response = service.translate_document(
        text=text,
        source_lang="id",
        target_lang="en",
        preserve_formatting=True,
        sector="Legal"
    )
    
    assert isinstance(response, TranslationResponse)
    assert response.original_text == text
    assert "PT Sydeco Global" in response.translated_text
    assert "12-07-2026" in response.translated_text
    assert response.quality_score is not None
    assert response.risk_level in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    assert isinstance(response.warnings, list)
    assert isinstance(response.quality_report, dict)
