import logging
import os
from deep_translator import GoogleTranslator

logger = logging.getLogger(__name__)


def translate_text(text, target_lang):
    # Confidentiality gate: translation sends the full document text to
    # Google's API. For legal documents this must be an explicit opt-in.
    if os.getenv("LDV_REMOTE_TRANSLATION", "0") != "1":
        logger.warning(
            "Remote translation disabled — document text stays local "
            "(set LDV_REMOTE_TRANSLATION=1 to allow sending text to Google). "
            "Non-English ML layers will run on the original text."
        )
        return text

    chunks = [text[i:i+5000] for i in range(0, len(text), 5000)]
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
