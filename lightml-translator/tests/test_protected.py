import pytest
from app.services.translation_service import TranslationService

@pytest.fixture
def translation_service():
    return TranslationService()

def test_protected_entities(translation_service):
    """Verify that protected entities (emails, URLs, phones, HTML, markdown) are never translated or modified."""
    text = (
        "De contactpersoon is bereikbaar via info@sydeco.com.\n"
        "Zie onze website op https://www.sydeco.com/privacy.\n"
        "Bel ons op +31-20-555-0199.\n"
        "Dit is <b>vetgedrukte</b> tekst en **belangrijk**.\n"
        "Getekend door: /s/ John Doe."
    )
    
    res = translation_service.translate_document(text, "nl", "en", preserve_formatting=True)
    
    # Assert all protected terms remain verbatim
    assert "info@sydeco.com" in res.translated_text
    assert "https://www.sydeco.com/privacy" in res.translated_text
    assert "+31-20-555-0199" in res.translated_text
    assert "<b>" in res.translated_text and "</b>" in res.translated_text
    assert "**" in res.translated_text
    assert "/s/ John Doe" in res.translated_text

def test_defined_terms_untranslated(translation_service):
    """Verify that defined legal terms in quotes are never translated or modified."""
    text = 'Dit document wordt aangeduid als de "Overeenkomst" of "Perjanjian".'
    res = translation_service.translate_document(text, "nl", "en", preserve_formatting=True)
    
    assert '"Overeenkomst"' in res.translated_text or "“Overeenkomst”" in res.translated_text
    assert '"Perjanjian"' in res.translated_text or "“Perjanjian”" in res.translated_text
