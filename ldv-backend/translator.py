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

    # Translate in parallel batches while preserving the one-clause-per-line
    # structure that downstream code depends on. Batching dramatically reduces
    # latency compared to sequential line-by-line model calls.
    device = next(mdl.parameters()).device
    
    # ponytail: batch size is set to 16 to balance CPU/GPU memory footprint and parallel throughput.
    # Ceiling: large batch sizes (>64) on CPU or low-VRAM GPUs can cause OOM.
    # Upgrade: dynamic batch sizing based on resource allocation or environment overrides.
    batch_size = int(os.getenv("LDV_TRANSLATION_BATCH_SIZE", "16"))

    original_lines = text.split("\n")
    tasks = []
    translations_map = {i: [] for i, line in enumerate(original_lines) if line.strip()}

    for idx, line in enumerate(original_lines):
        if not line.strip():
            continue
        words = line.split(" ")
        # Split very long lines (>300 words) to avoid tokenizer truncation limits (max 512 tokens).
        if len(words) > 300:
            sub_chunks = [" ".join(words[i:i + 300]) for i in range(0, len(words), 300)]
            for chunk in sub_chunks:
                tasks.append((idx, chunk))
        else:
            tasks.append((idx, line))

    if not tasks:
        return text

    # Process tasks in parallel batches
    for i in range(0, len(tasks), batch_size):
        batch = tasks[i:i + batch_size]
        batch_texts = [item[1] for item in batch]

        try:
            inputs = tok(batch_texts, return_tensors="pt", padding=True, truncation=True, max_length=512).to(device)
            translated = mdl.generate(**inputs)
            # Use batch_decode if available (HuggingFace standard), fallback to list comprehension
            if hasattr(tok, "batch_decode"):
                translated_texts = tok.batch_decode(translated, skip_special_tokens=True)
            else:
                translated_texts = [tok.decode(t, skip_special_tokens=True) for t in translated]

            for (idx, _), trans_txt in zip(batch, translated_texts):
                translations_map[idx].append(trans_txt)
        except Exception as e:
            logger.warning("Batch translation failed for range %d-%d: %s — falling back to sequential", i, i + len(batch), e)
            # Fail-soft: process this specific batch sequentially to isolate failures
            for idx, text_chunk in batch:
                try:
                    inputs = tok(text_chunk, return_tensors="pt", padding=True, truncation=True, max_length=512).to(device)
                    translated = mdl.generate(**inputs)
                    trans_txt = tok.decode(translated[0], skip_special_tokens=True)
                    translations_map[idx].append(trans_txt)
                except Exception as ex:
                    logger.warning("Single-chunk fallback translation failed for line %d: %s", idx, ex)
                    translations_map[idx].append(text_chunk)

    out = []
    for idx, line in enumerate(original_lines):
        if not line.strip():
            out.append(line)
        else:
            out.append(" ".join(translations_map[idx]))
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
