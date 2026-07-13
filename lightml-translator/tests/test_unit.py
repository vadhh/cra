import pytest
from app.services.translation_service import TranslationService
from config.settings import Settings

@pytest.fixture
def translation_service():
    return TranslationService()

def test_supported_languages(translation_service):
    """Verify that supported languages lists in settings are valid."""
    settings = Settings()
    assert "nl" in settings.supported_languages
    assert "fr" in settings.supported_languages
    assert "id" in settings.supported_languages
    assert "de" in settings.supported_languages
    assert "es" in settings.supported_languages
    assert "it" in settings.supported_languages
    assert "pt" in settings.supported_languages
    assert "en" in settings.supported_languages

def test_direct_translations(translation_service):
    """Verify direct translations to English for supported languages."""
    # Test Dutch to English
    res_nl = translation_service.translate_document("overeenkomst", "nl", "en")
    assert "agreement" in res_nl.translated_text.lower()

    # Test French to English
    res_fr = translation_service.translate_document("accord", "fr", "en")
    assert "accord" in res_fr.translated_text.lower() or "agreement" in res_fr.translated_text.lower()

    # Test German to English
    res_de = translation_service.translate_document("Vertrag", "de", "en")
    assert "contract" in res_de.translated_text.lower() or "agreement" in res_de.translated_text.lower()

def test_pivot_translations(translation_service):
    """Verify pivot translation through English (e.g. Dutch -> French)."""
    # Dutch -> English -> French
    res_nl_fr = translation_service.translate_document("huurovereenkomst", "nl", "fr")
    assert res_nl_fr.translated_text is not None
    assert len(res_nl_fr.translated_text) > 0
    # The output should be French (e.g. bail or contrat de location)
    text_lower = res_nl_fr.translated_text.lower()
    assert "bail" in text_lower or "contrat" in text_lower or "location" in text_lower
