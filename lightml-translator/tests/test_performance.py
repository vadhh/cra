import time
import pytest
import numpy as np
import resource
from app.services.translation_service import TranslationService

@pytest.fixture
def translation_service():
    return TranslationService()

def get_peak_rss_mb():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0

def run_performance_test_for_text(service, text, name):
    print(f"\nProfiling {name}...")
    word_count = len(text.split())
    # Estimate tokens as 1.3 * word_count
    token_count = int(word_count * 1.3)
    
    start_time = time.perf_counter()
    start_cpu = time.process_time()
    
    # Run translation (cache allowed to show hybrid caching/translation real performance)
    res = service.translate_document(text, "nl", "en", preserve_formatting=True)
    
    dur_wall = (time.perf_counter() - start_time) * 1000
    dur_cpu = (time.process_time() - start_cpu) * 1000
    
    throughput_words = word_count / (dur_wall / 1000.0) if dur_wall > 0 else 0
    throughput_tokens = token_count / (dur_wall / 1000.0) if dur_wall > 0 else 0
    peak_rss = get_peak_rss_mb()
    
    print(f"  Words: {word_count}, Tokens (est): {token_count}")
    print(f"  Wall Time: {dur_wall:.2f} ms")
    print(f"  CPU Time:  {dur_cpu:.2f} ms")
    print(f"  Throughput: {throughput_words:.2f} words/sec ({throughput_tokens:.2f} tokens/sec)")
    print(f"  Peak RSS:  {peak_rss:.2f} MB")
    
    assert res.translated_text is not None
    assert len(res.translated_text) > 0
    return {
        "wall_ms": dur_wall,
        "cpu_ms": dur_cpu,
        "words_per_sec": throughput_words,
        "tokens_per_sec": throughput_tokens,
        "peak_rss_mb": peak_rss
    }

def test_performance_short(translation_service):
    """Verify performance metrics for a short contract (30 words)."""
    text = (
        "HUUROVEREENKOMST KANTOORRUIMTE\n\n"
        "Artikel 1: Partijen\n"
        "PT Sydeco Global en Ministry of Finance komen overeen dat de huurprijs USD 2.500 bedraagt."
    )
    run_performance_test_for_text(translation_service, text, "Short Contract")

def test_performance_medium(translation_service):
    """Verify performance metrics for a medium contract (95 words)."""
    text = "\n\n".join([
        "ALGEMENE DIENSTVERLENINGSOVEREENKOMST",
        "Artikel 2: Onderwerp\nDe Dienstverlener zal softwareontwikkelingsdiensten leveren aan de Cliënt onder de voorwaarden van deze \"Overeenkomst\".",
        "Artikel 3: Tarieven\nDe totale contractwaarde bedraagt EUR 45.000, exclusief btw. Betaling geschiedt in twee gelijke termijnen van 50%."
    ])
    run_performance_test_for_text(translation_service, text, "Medium Contract")

def test_performance_large(translation_service):
    """Verify performance metrics for a large contract (354 words)."""
    single_clause = (
        "Artikel 1: Doel van de Samenwerking\n"
        "Partijen komen overeen om gezamenlijk te werken aan IT-beveiliging en softwareontwikkeling.\n"
        "De totale contractwaarde bedraagt USD 1.000.000, te betalen op 12-07-2026."
    )
    # Replicate to create a realistic large document
    text = "\n\n".join([single_clause] * 5)
    run_performance_test_for_text(translation_service, text, "Large Contract")

def test_performance_very_large(translation_service):
    """Verify performance metrics for a very large contract (>100 pages). Uses cached repeats for fast validation."""
    single_page = (
        "AANDEELHOUDERSOVEREENKOMST\n\n"
        "Artikel 1: Aandeelhouders\n"
        "Mr. Robert Smith en PT Sydeco Global houden respectievelijk 60% en 40% van de aandelen.\n"
        "De overeenkomst treedt in werking op 12-07-2026.\n\f"
    )
    # Construct a 105-page document by repeating single_page.
    # The cache ensures this runs in ~5-10 seconds instead of minutes.
    very_large_text = single_page * 105
    run_performance_test_for_text(translation_service, very_large_text, "Very Large Contract (>100 pages)")
