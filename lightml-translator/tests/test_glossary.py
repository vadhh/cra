import pytest
from app.services.translation_service import TranslationService

@pytest.fixture
def translation_service():
    return TranslationService()

def test_glossary_consistency_legal(translation_service):
    """Verify that legal terms (overeenkomst, overmacht) are translated consistently."""
    text = (
        "Deze overeenkomst is bindend.\n"
        "Ingeval van overmacht zijn de verplichtingen opgeschort.\n"
        "Er is sprake van overmacht als..."
    )
    
    # Translate under the Legal sector
    res = translation_service.translate_document(text, "nl", "en", sector="Legal")
    
    # Check consistent translation of legal terms
    # overeenkomst -> agreement
    # overmacht -> force majeure
    translated_lower = res.translated_text.lower()
    assert "agreement" in translated_lower
    assert "force majeure" in translated_lower
    # Check that "overmacht" was translated consistently both times
    assert translated_lower.count("force majeure") >= 2

def test_glossary_consistency_employment(translation_service):
    """Verify that employment sector terms (arbeidsovereenkomst, werkgever) are consistent."""
    text = (
        "De arbeidsovereenkomst is getekend.\n"
        "De werkgever verklaart dat...\n"
        "De werknemer gaat ermee akkoord."
    )
    
    res = translation_service.translate_document(text, "nl", "en", sector="Legal") # Default sector
    translated_lower = res.translated_text.lower()
    
    # Check consistent translation of terms
    assert "contract" in translated_lower or "agreement" in translated_lower
    assert "employer" in translated_lower
    assert "employee" in translated_lower
