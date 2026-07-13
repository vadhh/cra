import pytest
import os
import re
from app.services.translation_service import TranslationService

@pytest.fixture
def translation_service():
    return TranslationService()

def test_newlines_and_paragraph_boundaries(translation_service):
    """Verify that single newlines and double newline paragraph boundaries are preserved."""
    text = "First paragraph line 1.\nFirst paragraph line 2.\n\nSecond paragraph line 1.\nSecond paragraph line 2."
    response = translation_service.translate_document(
        text=text,
        source_lang="nl",
        target_lang="en",
        preserve_formatting=True
    )
    
    # Assert paragraph boundaries are preserved
    assert "\n\n" in response.translated_text
    lines = response.translated_text.split("\n")
    assert len(lines) >= 4

def test_page_breaks(translation_service):
    """Verify that page breaks (\\f) are preserved exactly where they occurred."""
    text = "Page 1 content.\nMore page 1 content.\fPage 2 content.\nMore page 2 content."
    response = translation_service.translate_document(
        text=text,
        source_lang="nl",
        target_lang="en",
        preserve_formatting=True
    )
    
    # Assert page break symbol is preserved
    assert "\f" in response.translated_text
    pages = response.translated_text.split("\f")
    assert len(pages) == 2
    assert "Page 1" in pages[0] or "Page" in pages[0]
    assert "Page 2" in pages[1] or "Page" in pages[1]

def test_article_numbering(translation_service):
    """Verify that article and clause numbering systems are preserved."""
    text = "Artikel 1: De Definities.\nClause 2.3.1: The scope of work.\nArtikel 10: Slotbepalingen."
    response = translation_service.translate_document(
        text=text,
        source_lang="nl",
        target_lang="en",
        preserve_formatting=True
    )
    
    # Check that identifiers are preserved
    assert "1" in response.translated_text
    assert "2.3.1" in response.translated_text
    assert "10" in response.translated_text
    assert "Article 1" in response.translated_text or "Artikel 1" in response.translated_text
    assert "Clause 2.3.1" in response.translated_text
    assert "Article 10" in response.translated_text or "Artikel 10" in response.translated_text

def test_bullet_lists(translation_service):
    """Verify that bullet and numbered list layouts are preserved."""
    text = (
        "De diensten omvatten:\n"
        "  * Eerste onderdeel van diensten;\n"
        "  * Tweede onderdeel van diensten;\n"
        "  - Derde alternatief."
    )
    response = translation_service.translate_document(
        text=text,
        source_lang="nl",
        target_lang="en",
        preserve_formatting=True
    )
    
    assert "*" in response.translated_text
    assert "-" in response.translated_text
    assert len(response.translated_text.split("\n")) >= 4

def test_tables(translation_service):
    """Verify that markdown tables structure is preserved during translation."""
    text = (
        "| Dienst | Tarief |\n"
        "|---|---|\n"
        "| Ontwikkeling | EUR 5.000 |\n"
        "| Support | EUR 1.200 |"
    )
    response = translation_service.translate_document(
        text=text,
        source_lang="nl",
        target_lang="en",
        preserve_formatting=True
    )
    
    # Table rows should be preserved
    lines = response.translated_text.split("\n")
    assert len(lines) >= 4
    for line in lines:
        if "|" in line:
            assert line.count("|") >= 2

def test_dates(translation_service):
    """Verify that dates are preserved exactly."""
    text = "De datum is 12-07-2026.\nHierna te betalen op 15 August 2026."
    response = translation_service.translate_document(
        text=text,
        source_lang="nl",
        target_lang="en",
        preserve_formatting=True
    )
    
    assert "12-07-2026" in response.translated_text
    assert "15 August 2026" in response.translated_text or "15" in response.translated_text

def test_currency(translation_service):
    """Verify that currency values are preserved exactly."""
    text = "Het bedrag is USD 2,500 per maand.\nDe totale som is EUR 45.000,50."
    response = translation_service.translate_document(
        text=text,
        source_lang="nl",
        target_lang="en",
        preserve_formatting=True
    )
    
    assert "USD 2,500" in response.translated_text
    assert "EUR 45.000,50" in response.translated_text or "45.000,50" in response.translated_text

def test_percentages(translation_service):
    """Verify that percentages are preserved exactly."""
    text = "Het rentepercentage is 12%.\nEen ander tarief is 5.5 percent."
    response = translation_service.translate_document(
        text=text,
        source_lang="nl",
        target_lang="en",
        preserve_formatting=True
    )
    
    assert "12%" in response.translated_text or "12 %" in response.translated_text
    assert "5.5 percent" in response.translated_text or "5.5%" in response.translated_text

def test_defined_legal_terms(translation_service):
    """Verify that defined legal terms in quotes are preserved."""
    text = (
        "Hierin aangeduid als \"Pihak Pertama\" (de Eerste Partij).\n"
        "De voorwaarden van de \"Overeenkomst\" zijn bindend."
    )
    response = translation_service.translate_document(
        text=text,
        source_lang="nl",
        target_lang="en",
        preserve_formatting=True
    )
    
    assert '"Pihak Pertama"' in response.translated_text or "“Pihak Pertama”" in response.translated_text
    assert '"Overeenkomst"' in response.translated_text or "“Overeenkomst”" in response.translated_text

def test_protected_company_names(translation_service):
    """Verify that company names are protected and preserved."""
    text = "PT Sydeco Global is gevestigd te Yogyakarta.\nDe afspraken met PT Acme Corp B.V. zijn definitief."
    response = translation_service.translate_document(
        text=text,
        source_lang="nl",
        target_lang="en",
        preserve_formatting=True
    )
    
    assert "PT Sydeco Global" in response.translated_text
    assert "PT Acme Corp B.V." in response.translated_text or "PT Acme Corp" in response.translated_text

def test_personal_names(translation_service):
    """Verify that personal names are preserved."""
    text = "De contactpersoon is Mr. John Doe.\nDe overeenkomst is getekend door mevrouw Sarah Smith."
    response = translation_service.translate_document(
        text=text,
        source_lang="nl",
        target_lang="en",
        preserve_formatting=True
    )
    
    assert "Mr. John Doe" in response.translated_text
    assert "Sarah Smith" in response.translated_text

def test_addresses(translation_service):
    """Verify that physical addresses are preserved."""
    text = "Het adres is Keizersgracht 123, Amsterdam.\nDe fabriek bevindt zich aan 45 Main Street, Boston."
    response = translation_service.translate_document(
        text=text,
        source_lang="nl",
        target_lang="en",
        preserve_formatting=True
    )
    
    assert "Keizersgracht 123" in response.translated_text
    assert "45 Main Street" in response.translated_text

def test_registration_numbers(translation_service):
    """Verify that commercial/corporate registration numbers are preserved."""
    text = "Het KVK-nummer van het bedrijf is KVK 12345678.\nBTW-nummer is VAT NL123456789B01."
    response = translation_service.translate_document(
        text=text,
        source_lang="nl",
        target_lang="en",
        preserve_formatting=True
    )
    
    assert "KVK 12345678" in response.translated_text
    assert "VAT NL123456789B01" in response.translated_text

def test_article_references(translation_service):
    """Verify that statutory and article references are preserved."""
    text = "Dit is in overeenstemming met Article 12 en conform de Civil Code."
    response = translation_service.translate_document(
        text=text,
        source_lang="nl",
        target_lang="en",
        preserve_formatting=True
    )
    
    assert "Article 12" in response.translated_text
    assert "Civil Code" in response.translated_text

def test_digital_signatures(translation_service):
    """Verify that digital signature marks are preserved."""
    text = "Getekend door: /s/ Robert Smith.\nDit document is [Digitally Signed]."
    response = translation_service.translate_document(
        text=text,
        source_lang="nl",
        target_lang="en",
        preserve_formatting=True
    )
    
    assert "/s/ Robert Smith" in response.translated_text
    assert "[Digitally Signed]" in response.translated_text

def test_expected_outputs_comparison(translation_service):
    """Verify translation of known segments against pre-verified expected translations."""
    expected_pairs = {
        "Huurovereenkomst kantoorruimte": "lease agreement office space",
        "overmacht": "force majeure",
        "broncode (source code)": "source code (source code)",
        "De diensten omvatten het opleveren": "The services include the delivery"
    }
    
    for source, expected in expected_pairs.items():
        res = translation_service.translate_document(source, "nl", "en")
        # Assert semantic equivalence
        assert len(res.translated_text) > 0
        words = expected.lower().split()
        # Verify most words are present
        match_count = sum(1 for w in words if w in res.translated_text.lower())
        assert match_count >= len(words) * 0.5  # At least 50% of expected words match

def test_representative_datasets(translation_service):
    """Verify that translating the representative contract datasets preserves formatting, layout, and critical data tokens."""
    import os
    
    datasets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "datasets")
    
    # 1. NDA (Geheimhoudingsovereenkomst)
    nda_path = os.path.join(datasets_dir, "nda_nl.txt")
    if os.path.exists(nda_path):
        with open(nda_path, "r", encoding="utf-8") as f:
            nda_text = f.read()
        res = translation_service.translate_document(nda_text, "nl", "en", preserve_formatting=True)
        assert "Artikel 1" in res.translated_text or "Article 1" in res.translated_text
        assert "PT Sydeco Global" in res.translated_text
        assert "Ministry of Finance" in res.translated_text
        assert "USD 50,000" in res.translated_text
        assert "5.5%" in res.translated_text
        assert "12-07-2026" in res.translated_text
        assert '"Overeenkomst"' in res.translated_text or "“Overeenkomst”" in res.translated_text

    # 2. Employment Contract (Arbeidsovereenkomst)
    emp_path = os.path.join(datasets_dir, "employment_nl.txt")
    if os.path.exists(emp_path):
        with open(emp_path, "r", encoding="utf-8") as f:
            emp_text = f.read()
        res = translation_service.translate_document(emp_text, "nl", "en", preserve_formatting=True)
        assert "PT Sydeco Global" in res.translated_text or "PTSydeco Global" in res.translated_text
        assert "Mr. John Doe" in res.translated_text
        assert "EUR 4.500" in res.translated_text
        assert "8%" in res.translated_text
        assert "15-08-2026" in res.translated_text
        assert "hr@sydeco.com" in res.translated_text

    # 3. Supplier Agreement (Leveranciersovereenkomst)
    sup_path = os.path.join(datasets_dir, "supplier_nl.txt")
    if os.path.exists(sup_path):
        with open(sup_path, "r", encoding="utf-8") as f:
            sup_text = f.read()
        res = translation_service.translate_document(sup_text, "nl", "en", preserve_formatting=True)
        assert "PT Acme Corp" in res.translated_text
        assert "PT Sydeco Global" in res.translated_text
        assert "8%" in res.translated_text
        assert "12-07-2026" in res.translated_text
        assert "quality@acmecorp.com" in res.translated_text
        assert "+31-20-555-0199" in res.translated_text
        assert "45 Main Street" in res.translated_text

    # 4. Lease Agreement (Huurovereenkomst)
    lease_path = os.path.join(datasets_dir, "lease_nl.txt")
    if os.path.exists(lease_path):
        with open(lease_path, "r", encoding="utf-8") as f:
            lease_text = f.read()
        res = translation_service.translate_document(lease_text, "nl", "en", preserve_formatting=True)
        assert "Keizersgracht 123" in res.translated_text
        assert "EUR 2.500" in res.translated_text
        assert "USD 7,500" in res.translated_text
        assert "2%" in res.translated_text
        assert "12-07-2026" in res.translated_text
        assert "/s/ Robert Smith" in res.translated_text
        assert "\f" in res.translated_text
        assert "10-07-2026" in res.translated_text

    # 5. Partnership Agreement (VOF)
    part_path = os.path.join(datasets_dir, "partnership_nl.txt")
    if os.path.exists(part_path):
        with open(part_path, "r", encoding="utf-8") as f:
            part_text = f.read()
        res = translation_service.translate_document(part_text, "nl", "en", preserve_formatting=True)
        assert "PT Sydeco Global" in res.translated_text
        assert "PT Invest Capital" in res.translated_text
        assert "USD 100.000" in res.translated_text
        assert "60%" in res.translated_text
        assert "40%" in res.translated_text
        assert "12-07-2026" in res.translated_text
        assert "EUR 10.000" in res.translated_text
        assert "Sudirman Avenue" in res.translated_text

    # 6. Software License (Software-licentieovereenkomst)
    sw_path = os.path.join(datasets_dir, "software_license_nl.txt")
    if os.path.exists(sw_path):
        with open(sw_path, "r", encoding="utf-8") as f:
            sw_text = f.read()
        res = translation_service.translate_document(sw_text, "nl", "en", preserve_formatting=True)
        assert "PT Sydeco Global" in res.translated_text
        assert "USD 12.000" in res.translated_text
        assert "12-07-2026" in res.translated_text
        assert "EUR 25.000" in res.translated_text
        assert "support@sydeco.com" in res.translated_text
        assert '"Overeenkomst"' in res.translated_text or "“Overeenkomst”" in res.translated_text
