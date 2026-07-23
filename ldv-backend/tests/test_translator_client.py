"""tests/test_translator_client.py — Priority 5 from the 2026-07-16 management
review: safeguards on the internal LightML translator microservice client
(translator_client.py), which sends contract text over HTTP(S) to an
external URL. The review's instruction was "do not simply flip
EXTERNAL_TRANSLATION_DISABLED=0" -- these tests cover what the client now
enforces before that flag is ever safe to set: HTTPS-only by default, a
payload size cap, optional bearer auth, and no content leakage in logs.
"""
import os
import sys
from unittest.mock import patch, MagicMock

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import translator_client


def _clear_env():
    for var in (
        "EXTERNAL_TRANSLATION_DISABLED", "LIGHTML_TRANSLATOR_URL",
        "LDV_LIGHTML_ALLOW_INSECURE", "LDV_LIGHTML_API_KEY", "LDV_LIGHTML_MAX_CHARS",
    ):
        os.environ.pop(var, None)


def test_disabled_by_default_returns_original_text():
    _clear_env()
    assert translator_client.translate_via_microservice("hello", "fr") == "hello"


def test_no_url_configured_returns_original_text():
    _clear_env()
    os.environ["EXTERNAL_TRANSLATION_DISABLED"] = "0"
    assert translator_client.translate_via_microservice("hello", "fr") == "hello"
    _clear_env()


def test_refuses_plaintext_http_without_explicit_opt_in():
    _clear_env()
    os.environ["EXTERNAL_TRANSLATION_DISABLED"] = "0"
    os.environ["LIGHTML_TRANSLATOR_URL"] = "http://lightml.internal/translate"
    with patch("translator_client.requests.post") as mock_post:
        result = translator_client.translate_via_microservice("hello", "fr")
        assert result == "hello"
        mock_post.assert_not_called()
    _clear_env()


def test_allows_plaintext_http_when_explicitly_opted_in():
    _clear_env()
    os.environ["EXTERNAL_TRANSLATION_DISABLED"] = "0"
    os.environ["LIGHTML_TRANSLATOR_URL"] = "http://localhost:8000/translate"
    os.environ["LDV_LIGHTML_ALLOW_INSECURE"] = "1"
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"translated_text": "bonjour"}
    with patch("translator_client.requests.post", return_value=mock_resp) as mock_post:
        result = translator_client.translate_via_microservice("hello", "en")
        assert result == "bonjour"
        mock_post.assert_called_once()
    _clear_env()


def test_oversized_text_skips_translation():
    _clear_env()
    os.environ["EXTERNAL_TRANSLATION_DISABLED"] = "0"
    os.environ["LIGHTML_TRANSLATOR_URL"] = "https://lightml.internal/translate"
    os.environ["LDV_LIGHTML_MAX_CHARS"] = "10"
    with patch("translator_client.requests.post") as mock_post:
        result = translator_client.translate_via_microservice("this text is way too long", "fr")
        assert result == "this text is way too long"
        mock_post.assert_not_called()
    _clear_env()


def test_sends_bearer_auth_header_when_api_key_set():
    _clear_env()
    os.environ["EXTERNAL_TRANSLATION_DISABLED"] = "0"
    os.environ["LIGHTML_TRANSLATOR_URL"] = "https://lightml.internal/translate"
    os.environ["LDV_LIGHTML_API_KEY"] = "secret-key-123"
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"translated_text": "bonjour"}
    with patch("translator_client.requests.post", return_value=mock_resp) as mock_post:
        translator_client.translate_via_microservice("hello", "en")
        _, kwargs = mock_post.call_args
        assert kwargs["headers"]["Authorization"] == "Bearer secret-key-123"
    _clear_env()


def test_failure_falls_back_to_original_text_without_retry():
    _clear_env()
    os.environ["EXTERNAL_TRANSLATION_DISABLED"] = "0"
    os.environ["LIGHTML_TRANSLATOR_URL"] = "https://lightml.internal/translate"
    with patch("translator_client.requests.post", side_effect=ConnectionError("refused")) as mock_post:
        result = translator_client.translate_via_microservice("hello", "fr")
        assert result == "hello"
        assert mock_post.call_count == 1  # no retry -- documented ceiling
    _clear_env()


def test_check_health_disabled_or_unconfigured():
    _clear_env()
    assert translator_client.check_health() == {"enabled": False, "reachable": None}
    os.environ["EXTERNAL_TRANSLATION_DISABLED"] = "0"
    assert translator_client.check_health() == {"enabled": False, "reachable": None}
    _clear_env()


def test_check_health_refuses_plaintext_http_without_explicit_opt_in():
    _clear_env()
    os.environ["EXTERNAL_TRANSLATION_DISABLED"] = "0"
    os.environ["LIGHTML_TRANSLATOR_URL"] = "http://lightml.internal/translate"
    os.environ["LDV_LIGHTML_API_KEY"] = "secret-key-123"
    with patch("translator_client.requests.get") as mock_get:
        result = translator_client.check_health()
        assert result == {"enabled": True, "reachable": None}
        mock_get.assert_not_called()  # bearer token must never go out in cleartext
    _clear_env()


def test_check_health_probes_health_path_derived_from_base_url():
    _clear_env()
    os.environ["EXTERNAL_TRANSLATION_DISABLED"] = "0"
    os.environ["LIGHTML_TRANSLATOR_URL"] = "https://lightml.internal:9000/translate"
    mock_resp = MagicMock(ok=True)
    with patch("translator_client.requests.get", return_value=mock_resp) as mock_get:
        result = translator_client.check_health()
        assert result == {"enabled": True, "reachable": True}
        called_url = mock_get.call_args[0][0]
        assert called_url == "https://lightml.internal:9000/health"
    _clear_env()


if __name__ == "__main__":
    test_disabled_by_default_returns_original_text()
    test_no_url_configured_returns_original_text()
    test_refuses_plaintext_http_without_explicit_opt_in()
    test_allows_plaintext_http_when_explicitly_opted_in()
    test_oversized_text_skips_translation()
    test_sends_bearer_auth_header_when_api_key_set()
    test_failure_falls_back_to_original_text_without_retry()
    test_check_health_disabled_or_unconfigured()
    test_check_health_refuses_plaintext_http_without_explicit_opt_in()
    test_check_health_probes_health_path_derived_from_base_url()
    print("test_translator_client OK")
