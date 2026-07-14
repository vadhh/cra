import os
import logging
import requests

logger = logging.getLogger(__name__)

# ponytail: single REST call; no class, no detect/status, no in-process path
def translate_via_microservice(text: str, src_lang: str) -> str:
    if not text.strip():
        return text
    url = os.getenv("LIGHTML_TRANSLATOR_URL", "http://lightml-translator:8000/api/v1/translate")
    try:
        r = requests.post(
            url,
            json={"text": text, "source_lang": src_lang, "target_lang": "en", "sector": "Legal"},
            timeout=120,
        )
        r.raise_for_status()
        return r.json().get("translated_text", text)
    except Exception as e:
        logger.warning("Microservice translation failed: %s", e)
        return text
