import logging
import os
# pyrefly: ignore [missing-import]
from deep_translator import GoogleTranslator

logger = logging.getLogger(__name__)


def _local_translate(text: str, src_lang: str) -> str:
    """Translate using the local lightml-translator microservice."""
    from translator_client import translate_via_microservice
    return translate_via_microservice(text, src_lang)


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
