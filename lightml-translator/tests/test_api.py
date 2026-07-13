from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    """Tests the standard service health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert "service" in response.json()


def test_system_status():
    """Tests the active model and config status endpoint."""
    response = client.get("/api/v1/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "supported_languages" in data
    assert len(data["cached_models"]) > 0


def test_language_detection():
    """Tests language detection API route."""
    response = client.post(
        "/api/v1/detect",
        json={"text": "Ini adalah kontrak sewa menyewa apartemen."}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["detected_lang"] == "id"
    assert data["is_supported"] is True


def test_translation_pipeline():
    """Tests the overall translation endpoint routing with dummy translation stubs."""
    # Test Indonesian to English
    payload = {
        "text": "Perjanjian ini dibuat pada hari Senin.",
        "source_lang": "id",
        "target_lang": "en",
        "preserve_formatting": True
    }
    response = client.post("/api/v1/translate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "translated_text" in data
    assert data["source_lang"] == "id"
    assert data["target_lang"] == "en"
    assert "model_used" in data
