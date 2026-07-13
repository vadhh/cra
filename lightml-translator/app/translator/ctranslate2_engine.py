import os
import time
import logging
import threading
import resource
import json
from typing import List, Dict, Tuple, Any, Optional
from app.translator.base import BaseTranslator
from config.settings import settings

logger = logging.getLogger(__name__)

try:
    import ctranslate2
    import sentencepiece as spm
    HAS_CTRANSLATE2 = True
except ImportError:
    HAS_CTRANSLATE2 = False
    logger.warning("ctranslate2 or sentencepiece is not installed. CTranslate2 translator will run in fallback/mock mode.")


class CTranslate2Translator(BaseTranslator):
    """
    CTranslate2 optimized translation engine.
    Utilizes INT8 quantized models for fast CPU execution.
    Falls back to original Marian/Transformers if CTranslate2 is unavailable.
    """

    def __init__(self):
        self._translator_cache: Dict[str, Any] = {}
        self._tokenizer_cache: Dict[str, Any] = {}
        self._model_metadata: Dict[str, dict] = {}
        self._lock = threading.RLock()

    @classmethod
    def is_available(cls) -> bool:
        """Returns True if ctranslate2 and sentencepiece dependencies are present."""
        return HAS_CTRANSLATE2

    def _get_ctranslate2_paths(self, source_lang: str, target_lang: str = "en") -> Tuple[str, str, str]:
        """
        Resolves local directories.
        Returns:
            (original_marian_path, ctranslate2_output_path, model_id)
        """
        model_id = f"Helsinki-NLP/opus-mt-{source_lang}-{target_lang}"
        folder_name = f"opus-mt-{source_lang}-{target_lang}"
        
        original_marian_path = os.path.abspath(os.path.join(settings.model_dir, folder_name))
        ctranslate2_output_path = os.path.abspath(os.path.join(settings.model_dir, "ctranslate2", folder_name))
        
        return original_marian_path, ctranslate2_output_path, model_id

    def _get_process_rss_mb(self) -> float:
        """Returns the current process RSS memory usage in Megabytes."""
        try:
            return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0
        except Exception:
            return 0.0

    def convert_marian_to_ctranslate2(self, source_lang: str, target_lang: str = "en") -> bool:
        """
        Converts the original Marian model to CTranslate2 INT8 format programmatically.
        Returns True if successful, False otherwise.
        """
        if not HAS_CTRANSLATE2:
            logger.error("Cannot convert model: CTranslate2 is not installed.")
            return False

        orig_path, ct_path, model_id = self._get_ctranslate2_paths(source_lang, target_lang)
        
        if os.path.isdir(ct_path) and os.path.isfile(os.path.join(ct_path, "model.bin")):
            return True

        if not os.path.isdir(orig_path):
            logger.error(f"Original Marian model path '{orig_path}' is missing. Cannot convert.")
            return False

        with self._lock:
            # Check again after acquiring lock
            if os.path.isdir(ct_path) and os.path.isfile(os.path.join(ct_path, "model.bin")):
                return True

            logger.info(f"Converting Marian model '{model_id}' to CTranslate2 INT8 format...")
            start_time = time.perf_counter()
            try:
                import ctranslate2.converters
                converter = ctranslate2.converters.TransformersConverter(orig_path)
                converter.convert(
                    output_dir=ct_path,
                    quantization="int8",
                    force=True
                )
                duration = (time.perf_counter() - start_time) * 1000
                logger.info(f"Model conversion completed in {duration:.2f}ms. Saved to: {ct_path}")
                return True
            except Exception as e:
                logger.exception(f"Failed to convert model '{model_id}' to CTranslate2: {e}")
                return False

    def load_model(self, source_lang: str, target_lang: str) -> dict:
        """
        Loads the CTranslate2 model and SentencePiece tokenizer into memory cache.
        Thread-safe.
        """
        with self._lock:
            orig_path, ct_path, model_id = self._get_ctranslate2_paths(source_lang, target_lang)

            routing_json_path = os.path.join(ct_path, "routing.json")
            if os.path.isfile(routing_json_path):
                with open(routing_json_path, "r") as f:
                    routing_data = json.load(f)
                for step_model_name in routing_data.get("steps", []):
                    parts = step_model_name.split("-")
                    if len(parts) >= 4:
                        step_src, step_tgt = parts[2], parts[3]
                        self.load_model(step_src, step_tgt)
                metadata = {
                    "model_name": model_id,
                    "version": "1.0.0",
                    "language_pair": f"{source_lang}-{target_lang}",
                    "loading_time_ms": 0.0,
                    "memory_usage_mb": 0.0,
                    "model_path": ct_path,
                    "status": "loaded",
                    "backend": "pivot-wrapper"
                }
                self._model_metadata[ct_path] = metadata
                self._translator_cache[ct_path] = "pivot-wrapper"
                return metadata

            if ct_path in self._translator_cache:
                return self._model_metadata[ct_path]

            # Trigger conversion if missing
            converted = self.convert_marian_to_ctranslate2(source_lang, target_lang)
            if not converted or not HAS_CTRANSLATE2:
                logger.warning(f"CTranslate2 model for '{source_lang}' unavailable. Falling back.")
                return {
                    "model_name": model_id,
                    "version": "unknown",
                    "language_pair": f"{source_lang}-{target_lang}",
                    "loading_time_ms": 0.0,
                    "memory_usage_mb": 0.0,
                    "model_path": ct_path,
                    "status": "unavailable",
                    "backend": "transformers"
                }

            start_time = time.perf_counter()
            mem_before = self._get_process_rss_mb()

            try:
                # Load SentencePiece tokenizers for source and target languages
                source_sp_path = os.path.join(orig_path, "source.spm")
                target_sp_path = os.path.join(orig_path, "target.spm")
                
                if not os.path.isfile(source_sp_path):
                    source_sp_path = target_sp_path
                if not os.path.isfile(target_sp_path):
                    target_sp_path = source_sp_path
                    
                if not os.path.isfile(source_sp_path):
                    raise FileNotFoundError(f"SentencePiece vocabulary model (.spm) not found in '{orig_path}'.")

                source_tokenizer = spm.SentencePieceProcessor()
                source_tokenizer.Load(source_sp_path)
                
                target_tokenizer = spm.SentencePieceProcessor()
                target_tokenizer.Load(target_sp_path)

                # Load CTranslate2 Translator
                translator = ctranslate2.Translator(
                    model_path=ct_path,
                    device="cpu",
                    compute_type=settings.ctranslate2_compute_type,
                    inter_threads=1,
                    intra_threads=settings.ctranslate2_threads
                )

                # Profile measurements
                mem_after = self._get_process_rss_mb()
                loading_time = (time.perf_counter() - start_time) * 1000
                mem_diff = max(0.0, mem_after - mem_before)

                # Get version
                version = "1.0.0"
                config_path = os.path.join(orig_path, "config.json")
                if os.path.isfile(config_path):
                    try:
                        with open(config_path, "r", encoding="utf-8") as f:
                            cfg = json.load(f)
                            version = cfg.get("transformers_version", "1.0.0")
                    except Exception:
                        pass

                metadata = {
                    "model_name": model_id,
                    "version": version,
                    "language_pair": f"{source_lang}-{target_lang}",
                    "loading_time_ms": round(loading_time, 2),
                    "memory_usage_mb": round(mem_diff, 2),
                    "model_path": ct_path,
                    "status": "loaded",
                    "backend": "ctranslate2"
                }

                self._translator_cache[ct_path] = translator
                self._tokenizer_cache[ct_path] = (source_tokenizer, target_tokenizer)
                self._model_metadata[ct_path] = metadata

                logger.info(f"Loaded CTranslate2 model {model_id} in {loading_time:.2f}ms (Memory: +{mem_diff:.2f} MB)")
                return metadata

            except Exception as e:
                logger.exception(f"Failed to load CTranslate2 model from '{ct_path}': {e}")
                return {
                    "model_name": model_id,
                    "version": "unknown",
                    "language_pair": f"{source_lang}-{target_lang}",
                    "loading_time_ms": 0.0,
                    "memory_usage_mb": 0.0,
                    "model_path": ct_path,
                    "status": f"error: {str(e)}",
                    "backend": "transformers"
                }

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """Translates a single text string using CTranslate2."""
        results = self.translate_batch([text], source_lang, target_lang)
        return results[0] if results else text

    def translate_batch(
        self, 
        texts: List[str], 
        source_lang: str, 
        target_lang: str, 
        scores_out: Optional[List[float]] = None
    ) -> List[str]:
        """
        Translates a list of strings in a batch.
        Guards execution and detokenizes results.
        
        Parameters:
            texts: List of strings.
            source_lang: Source language.
            target_lang: Target language.
            scores_out: Optional list that will be populated with translation likelihood scores.
        """
        if not texts:
            return []

        # Ensure model is loaded
        metadata = self.load_model(source_lang, target_lang)
        _, ct_path, _ = self._get_ctranslate2_paths(source_lang, target_lang)
        
        # Fallback if loading failed
        if metadata.get("status") != "loaded" or ct_path not in self._translator_cache:
            logger.warning("CTranslate2 unavailable. Returning original texts.")
            return texts

        # Handle pivot wrappers
        if self._translator_cache[ct_path] == "pivot-wrapper":
            routing_json_path = os.path.join(metadata["model_path"], "routing.json")
            if os.path.isfile(routing_json_path):
                with open(routing_json_path, "r") as f:
                    routing_data = json.load(f)
                current_texts = texts
                for step_model_name in routing_data.get("steps", []):
                    parts = step_model_name.split("-")
                    if len(parts) >= 4:
                        step_src, step_tgt = parts[2], parts[3]
                        step_scores = []
                        current_texts = self.translate_batch(current_texts, step_src, step_tgt, step_scores)
                        if scores_out is not None:
                            if not scores_out:
                                scores_out.extend(step_scores)
                            else:
                                for idx in range(min(len(scores_out), len(step_scores))):
                                    scores_out[idx] = (scores_out[idx] + step_scores[idx]) / 2.0
                return current_texts

        translator = self._translator_cache[ct_path]
        source_tokenizer, target_tokenizer = self._tokenizer_cache[ct_path]

        try:
            # 1. Tokenize texts and append EOS token
            tokenized_batch = []
            for text in texts:
                if not text.strip():
                    tokenized_batch.append([])
                else:
                    tokens = source_tokenizer.EncodeAsPieces(text)
                    tokens.append("</s>")
                    tokenized_batch.append(tokens)

            # 2. Run batch translate
            # CTranslate2 translate_batch accepts list of list of tokens
            translations = translator.translate_batch(
                tokenized_batch,
                max_batch_size=settings.ctranslate2_batch_size,
                beam_size=4
            )

            # 3. Detokenize translations and extract scores
            results = []
            for idx, trans in enumerate(translations):
                if not texts[idx].strip():
                    results.append(texts[idx])
                    if scores_out is not None:
                        scores_out.append(0.0)
                else:
                    hyp = trans.hypotheses[0]
                    detokenized = target_tokenizer.DecodePieces(hyp)
                    results.append(detokenized)
                    
                    if scores_out is not None:
                        # Convert log likelihood to probability/score
                        score = float(trans.scores[0]) if trans.scores else 0.0
                        scores_out.append(score)

            return results

        except Exception as e:
            logger.error(f"CTranslate2 batch inference failed: {e}. Returning original texts.")
            return texts

    def is_model_loaded(self, source_lang: str, target_lang: str) -> bool:
        with self._lock:
            _, ct_path, _ = self._get_ctranslate2_paths(source_lang, target_lang)
            return ct_path in self._translator_cache

    def check_is_cached(self, source_lang: str, target_lang: str = "en") -> bool:
        """Checks if both original Marian and converted CTranslate2 files are present, or if a pivot wrapper is defined."""
        orig_path, ct_path, _ = self._get_ctranslate2_paths(source_lang, target_lang)
        routing_json_path = os.path.join(ct_path, "routing.json")
        if os.path.isfile(routing_json_path):
            return True
        return os.path.isdir(orig_path) and os.path.isdir(ct_path)
