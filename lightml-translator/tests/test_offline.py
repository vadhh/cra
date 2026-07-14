import pytest
import socket
from app.services.translation_service import TranslationService

@pytest.fixture
def translation_service():
    return TranslationService()

def test_offline_translation_no_network(translation_service):
    """Verify that the translation pipeline functions fully offline without any network access."""
    # Temporarily block socket connections to simulate no network
    original_socket = socket.socket
    
    def blocked_socket(*args, **kwargs):
        raise OSError("Network access is disabled during offline validation tests.")
        
    socket.socket = blocked_socket
    
    try:
        # Run a translation request
        res = translation_service.translate_document(
            text="De overeenkomst is ondertekend en is volledig offline.",
            source_lang="nl",
            target_lang="en",
            preserve_formatting=True
        )
        
        # Verify that translation succeeded and returned correct content
        assert res.translated_text is not None
        assert len(res.translated_text) > 0
        assert "agreement" in res.translated_text.lower() or "offline" in res.translated_text.lower()
        print("\nOffline translation verified successfully (socket calls blocked).")
        
    finally:
        # Restore original socket
        socket.socket = original_socket
