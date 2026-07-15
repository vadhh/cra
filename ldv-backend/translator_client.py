import os
import logging
import requests

logger = logging.getLogger(__name__)

# ponytail: single REST call; no class, no detect/status, no in-process path.
# External translation is DISABLED BY DEFAULT.
# Enable by setting LIGHTML_TRANSLATOR_URL + EXTERNAL_TRANSLATION_DISABLED=0.
# ponytail: ceiling — if microservice is down, returns original text (no retry).
def translate_via_microservice(text: str, src_lang: str) -> str:
    if not text.strip():
        return text
    # External translation guard: disabled unless explicitly enabled
    if os.getenv("EXTERNAL_TRANSLATION_DISABLED", "1") == "1":
        logger.debug("External translation disabled (EXTERNAL_TRANSLATION_DISABLED=1); returning original text.")
        return text
    url = os.getenv("LIGHTML_TRANSLATOR_URL", "")
    if not url:
        logger.debug("LIGHTML_TRANSLATOR_URL not set; skipping external translation.")
        return text
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
