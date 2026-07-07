import logging
import os
from deep_translator import GoogleTranslator

logger = logging.getLogger(__name__)

# Helsinki-NLP/opus-mt model ids per langdetect source code
# ponytail: mul-en covers anything not listed; models download lazily on first use
_OPUS_MT = {
    "id": "Helsinki-NLP/opus-mt-id-en",
    "fr": "Helsinki-NLP/opus-mt-fr-en",
    "nl": "Helsinki-NLP/opus-mt-nl-en",
    "de": "Helsinki-NLP/opus-mt-de-en",
    "es": "Helsinki-NLP/opus-mt-es-en",
    "it": "Helsinki-NLP/opus-mt-it-en",
    "pt": "Helsinki-NLP/opus-mt-pt-en",
}
_OPUS_MT_FALLBACK = "Helsinki-NLP/opus-mt-mul-en"

_local_model_cache: dict = {}  # model_id → (model, tokenizer)


def _local_translate(text: str, src_lang: str) -> str:
    """Translate using the local lightml-translator microservice."""
    import requests

    url = os.getenv("LIGHTML_TRANSLATOR_URL", "http://lightml-translator:8000/api/v1/translate")
    try:
        resp = requests.post(
            url,
            json={
                "text": text,
                "source_lang": src_lang,
                "target_lang": "en",
                "preserve_formatting": True,
                "sector": "Legal"
            },
            timeout=120
        )
        if resp.status_code == 200:
            return resp.json()["translated_text"]
        else:
            logger.warning("Local microservice translation failed (status %s) — returning original text", resp.status_code)
            return text
    except Exception as e:
        logger.warning("Local microservice translation request failed: %s — returning original text", e)
        return text


def translate_text(text, target_lang, src_lang: str = "auto"):
    backend = os.getenv("LDV_REMOTE_TRANSLATION", "0")

    if backend == "local":
        logger.info("Local translation: src=%s → %s", src_lang, target_lang)
        return _local_translate(text, src_lang)

    if backend != "1":
        logger.warning(
            "Translation disabled — document text stays local "
            "(set LDV_REMOTE_TRANSLATION=1 for Google, =local for offline Marian MT). "
            "Non-English ML layers will run on the original text."
        )
        return text

    # Google path (LDV_REMOTE_TRANSLATION=1)
    chunks = [text[i : i + 5000] for i in range(0, len(text), 5000)]
    translated_chunks = []
    for chunk in chunks:
        try:
            translated_chunks.append(
                GoogleTranslator(source="auto", target=target_lang).translate(chunk)
            )
        except Exception as e:
            logger.warning("Translation chunk failed: %s", e)
            translated_chunks.append(chunk)
    return "\n".join(translated_chunks)
