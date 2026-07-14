import pytest
from fastapi.testclient import TestClient
from app.main import app

# Import local copy of python client
try:
    from tests.translator_client import SydecoTranslatorClient
except ImportError:
    # Fallback to importing from root if run outside pytest package format
    try:
        from translator_client import SydecoTranslatorClient
    except ImportError:
        SydecoTranslatorClient = None

client = TestClient(app)

def test_local_api_integration():
    """Verify that the FastAPI API routes respond correctly to real JSON payloads."""
    # Test health check
    health_resp = client.get("/health")
    assert health_resp.status_code == 200
    assert health_resp.json()["status"] == "healthy"

    # Test translate endpoint
    payload = {
        "text": "Dit is een overeenkomst.",
        "source_lang": "nl",
        "target_lang": "en",
        "preserve_formatting": True
    }
    trans_resp = client.post("/api/v1/translate", json=payload)
    assert trans_resp.status_code == 200
    data = trans_resp.json()
    assert "translated_text" in data
    assert len(data["translated_text"]) > 0
    assert "agreement" in data["translated_text"].lower()

def test_python_client_integration():
    """Verify that the SydecoTranslatorClient correctly communicates with the service or executes in-process."""
    if SydecoTranslatorClient is None:
        pytest.skip("SydecoTranslatorClient code not found in test context path.")

    # Initialize client (point to FastAPI TestClient wrapper or local service)
    # We can mock requests inside the client to route to our TestClient!
    import requests
    original_post = requests.post
    original_get = requests.get

    def mock_post(url, json=None, **kwargs):
        class MockResponse:
            def __init__(self, r):
                self.status_code = r.status_code
                self.text = r.text
                self._json = r.json()
            def json(self):
                return self._json
        
        # Route to TestClient
        if "/translate" in url:
            r = client.post("/api/v1/translate", json=json)
            return MockResponse(r)
        elif "/detect" in url:
            r = client.post("/api/v1/detect", json=json)
            return MockResponse(r)
        return original_post(url, json=json, **kwargs)

    def mock_get(url, **kwargs):
        class MockResponse:
            def __init__(self, r):
                self.status_code = r.status_code
                self.text = r.text
                self._json = r.json()
            def json(self):
                return self._json
        
        if "/status" in url:
            r = client.get("/api/v1/status")
            return MockResponse(r)
        return original_get(url, **kwargs)

    # Monkeypatch requests
    requests.post = mock_post
    requests.get = mock_get

    try:
        translator = SydecoTranslatorClient(endpoint_url="http://mock-service/api/v1")
        # Run translations
        res = translator.translate("overeenkomst", "nl", "en")
        assert "agreement" in res.lower()

        # Run document translation
        doc_res = translator.translate_document("overeenkomst", "nl", "en")
        assert "translated_text" in doc_res
        assert "quality_score" in doc_res

        # Run language detection
        det_res = translator.detect_language("overeenkomst")
        assert det_res["detected_lang"] == "nl"
    finally:
        # Restore requests methods
        requests.post = original_post
        requests.get = original_get
