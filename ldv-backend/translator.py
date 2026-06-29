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
    """Translate using a locally-cached Helsinki-NLP Marian model (no network after download)."""
    from transformers import MarianMTModel, MarianTokenizer

    model_name = _OPUS_MT.get(src_lang, _OPUS_MT_FALLBACK)
    folder_name = model_name.split("/")[-1]
    
    # Try custom models directory first, then default local models/ directory, then download from HF
    env_dir = os.getenv("LDV_MODELS_DIR", "")
    local_dir = os.path.join(os.path.dirname(__file__), "models")
    
    model_path = model_name
    if env_dir and os.path.isdir(os.path.join(env_dir, folder_name)):
        model_path = os.path.join(env_dir, folder_name)
    elif os.path.isdir(os.path.join(local_dir, folder_name)):
        model_path = os.path.join(local_dir, folder_name)

    if model_path not in _local_model_cache:
        logger.info("Local translation: loading %s", model_path)
        try:
            tok = MarianTokenizer.from_pretrained(model_path)
            mdl = MarianMTModel.from_pretrained(model_path)
            # Ensure model runs on GPU if available
            import torch
            device = "cuda" if torch.cuda.is_available() else "cpu"
            mdl = mdl.to(device)
            _local_model_cache[model_path] = (mdl, tok)
        except Exception as e:
            logger.warning("Local translation model load failed (%s): %s — returning original text", model_path, e)
            return text

    mdl, tok = _local_model_cache[model_path]

    # Marian has a 512-token limit; chunk on sentences for safety
    chunks = [text[i : i + 1500] for i in range(0, len(text), 1500)]
    out = []
    device = next(mdl.parameters()).device
    for chunk in chunks:
        try:
            inputs = tok(chunk, return_tensors="pt", padding=True, truncation=True, max_length=512).to(device)
            translated = mdl.generate(**inputs)
            out.append(tok.decode(translated[0], skip_special_tokens=True))
        except Exception as e:
            logger.warning("Local translation chunk failed: %s", e)
            out.append(chunk)
    return "\n".join(out)


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
