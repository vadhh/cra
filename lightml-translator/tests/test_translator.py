import pytest
from app.preprocessing.cleaner import TextCleaner
from app.postprocessing.formatter import TextFormatter
from app.protection.tag_protector import TagProtector
from app.protection.pii_masker import PIIMasker
from app.translator.marian import MarianTranslator


def test_cleaner():
    """Verify that cleaner removes control characters and normalizes spaces/lines."""
    cleaner = TextCleaner()
    raw = "Hello   world!\r\nThis is\x00 a test."
    cleaned = cleaner.clean(raw)
    assert cleaned == "Hello world!\nThis is a test."


def test_formatter():
    """Verify that postprocessing formatter aligns punctuation spacing."""
    formatter = TextFormatter()
    raw = "This is a sentence . And ( nested ) text ; done."
    formatted = formatter.format(raw)
    assert formatted == "This is a sentence. And (nested) text; done."


def test_tag_protector():
    """Verify that HTML tags, citations, and placeholders are preserved during pipeline."""
    protector = TagProtector()
    text = "Please refer to UU No. 13/2003 and open <div>tag</div> with {{place}}."
    
    # Run protect
    protected, p_map = protector.protect(text)
    assert "__PROT_HTML_TAG_" in protected
    assert "__PROT_CITATION_" in protected
    assert "__PROT_CURLY_PLACEHOLDER_" in protected
    
    # Run restore
    restored = protector.restore(protected, p_map)
    assert restored == text


def test_pii_masker():
    """Verify that emails and phone numbers are correctly masked and restored."""
    masker = PIIMasker()
    text = "Send mail to john.doe@example.com or call +1-555-555-0199."
    
    # Run mask
    masked, pii_map = masker.mask(text)
    assert "__PII_EMAIL_" in masked
    assert "__PII_PHONE_" in masked
    
    # Run unmask
    unmasked = masker.unmask(masked, pii_map)
    assert unmasked == text


def test_marian_caching_and_metadata():
    """Verify translator caching, load-once behavior, and metadata structure."""
    pytest.importorskip("transformers")
    translator = MarianTranslator()
    
    # Check that model is not loaded initially
    assert translator.is_model_loaded("id", "en") is False
    
    # Load model and verify metadata structure
    metadata = translator.load_model("id", "en")
    assert metadata["model_name"] == "Helsinki-NLP/opus-mt-id-en"
    assert "version" in metadata
    assert metadata["language_pair"] == "id-en"
    assert "loading_time_ms" in metadata
    assert "memory_usage_mb" in metadata
    assert "model_path" in metadata
    
    # Assert model reports as loaded
    assert translator.is_model_loaded("id", "en") is True
    
    # Check that loading a second time hits the cache (loading time should be 0 or instant)
    metadata_cached = translator.load_model("id", "en")
    assert metadata_cached["model_path"] == metadata["model_path"]


def test_marian_graceful_missing_model():
    """Verify that requesting a missing language pair degrades gracefully instead of crashing."""
    pytest.importorskip("transformers")
    translator = MarianTranslator()
    
    # Request language that has no mapped model folder
    metadata = translator.load_model("de", "en")
    # Should resolve to missing status or try fallback and return details gracefully
    assert metadata["status"] in ["missing", "loaded"]
    
    # Translate should return the original text if no local model files exist
    original_text = "Hallo Welt"
    translated = translator.translate(original_text, "de", "en")
    if metadata["status"] == "missing":
        assert translated == original_text
    else:
        assert translated != original_text


def test_marian_thread_safety():
    """Verify that multiple threads can request model loading concurrently without conflicts."""
    pytest.importorskip("transformers")
    import threading
    translator = MarianTranslator()
    
    errors = []
    
    def worker():
        try:
            # Concurrently request loading for Indonesian model
            meta = translator.load_model("id", "en")
            assert meta["language_pair"] == "id-en"
        except Exception as e:
            errors.append(e)

    threads = [threading.Thread(target=worker) for _ in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
        
    assert len(errors) == 0, f"Thread safety errors occurred: {errors}"


def test_ctranslate2_fallback_and_metadata():
    """Verify that CTranslate2 engine loads metadata or falls back cleanly."""
    from app.translator.ctranslate2_engine import CTranslate2Translator
    
    translator = CTranslate2Translator()
    metadata = translator.load_model("id", "en")
    
    assert "model_name" in metadata
    assert "backend" in metadata
    assert metadata["language_pair"] == "id-en"


def test_ctranslate2_benchmark():
    """Benchmarks model loading speed between Transformers and CTranslate2."""
    import time
    from app.translator.marian import MarianTranslator
    from app.translator.ctranslate2_engine import CTranslate2Translator
    
    # 1. Benchmark Transformers Marian MT loader
    marian = MarianTranslator()
    start_marian = time.perf_counter()
    marian.load_model("id", "en")
    marian_dur = (time.perf_counter() - start_marian) * 1000
    
    # 2. Benchmark CTranslate2 loader
    ct = CTranslate2Translator()
    start_ct = time.perf_counter()
    ct.load_model("id", "en")
    ct_dur = (time.perf_counter() - start_ct) * 1000
    
    print(f"\n--- Model Loading Benchmark ---")
    print(f"Transformers Marian Load Time: {marian_dur:.2f}ms")
    print(f"CTranslate2 INT8 Load Time:    {ct_dur:.2f}ms")


def test_document_translation_statistics():
    """Verify that document translation returns structured statistics and page/paragraph metrics."""
    from app.services.translation_service import TranslationService
    
    service = TranslationService()
    document_text = "Perjanjian Sewa Menyewa.\n\nPasal 1: Ketentuan Umum.\fHalaman kedua dari kontrak."
    
    response = service.translate_document(
        text=document_text,
        source_lang="id",
        target_lang="en",
        preserve_formatting=True
    )
    
    # Assert return structures and fields
    assert response.original_text == document_text
    assert response.translated_text
    assert response.backend in ["transformers", "ctranslate2"]
    assert response.confidence >= 0.0
    
    # Assert structural stats are gathered correctly
    assert response.page_statistics["page_count"] == 2
    assert response.paragraph_statistics["paragraph_count"] == 3
    assert response.chunk_statistics["chunk_count"] > 0


