import os
import time
import logging
import threading
import resource
import json
from typing import Dict, Tuple, Any, Optional
from app.translator.base import BaseTranslator
from config.settings import settings

logger = logging.getLogger(__name__)


class MarianTranslator(BaseTranslator):
    """
    Offline translator implementation using Helsinki-NLP MarianMT models.
    Loads models exclusively from local storage (never downloads at runtime).
    Thread-safe and caches loaded models/tokenizers in memory.
    """
    
    def __init__(self):
        # Cache for loaded models: (model_path) -> (model, tokenizer)
        self._model_cache: Dict[str, Tuple[Any, Any]] = {}
        # Metadata registry of loaded models: (model_path) -> dict
        self._model_metadata: Dict[str, dict] = {}
        # Reentrant lock to ensure thread-safe loading and caching
        self._lock = threading.RLock()
        
    def _get_model_path_and_id(self, source_lang: str, target_lang: str = "en") -> Tuple[str, str]:
        """Resolves the local directory path and official model identifier."""
        model_id = f"Helsinki-NLP/opus-mt-{source_lang}-{target_lang}"
        folder_name = f"opus-mt-{source_lang}-{target_lang}"
        local_path = os.path.abspath(os.path.join(settings.model_dir, folder_name))
        return local_path, model_id

    def _get_process_rss_mb(self) -> float:
        """Returns the current process RSS memory usage in Megabytes."""
        try:
            # ru_maxrss is in Kilobytes on Linux
            return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0
        except Exception as e:
            logger.debug(f"Could not retrieve memory stats: {e}")
            return 0.0

    def _read_model_version(self, model_path: str) -> str:
        """Reads transformers version from model config if available."""
        config_path = os.path.join(model_path, "config.json")
        if os.path.isfile(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                    return cfg.get("transformers_version", "1.0.0")
            except Exception as e:
                logger.debug(f"Failed to parse config.json version: {e}")
        return "1.0.0"

    def load_model(self, source_lang: str, target_lang: str) -> dict:
        """
        Loads MarianMT model and tokenizer into memory.
        Guarded by a thread lock. Returns model metadata.
        """
        with self._lock:
            model_path, model_id = self._get_model_path_and_id(source_lang, target_lang)
            
            # 1. Return immediately if already cached
            if model_path in self._model_cache:
                return self._model_metadata[model_path]
                
            # 2. Check if local path exists
            if not os.path.isdir(model_path):
                logger.warning(f"Requested model path '{model_path}' not found for language '{source_lang}'.")
                
                # Try fallback model
                fallback_path, fallback_id = self._get_model_path_and_id("mul")
                if os.path.isdir(fallback_path):
                    logger.info(f"Falling back to multilingual model: {fallback_path}")
                    model_path, model_id = fallback_path, fallback_id
                    if model_path in self._model_cache:
                        return self._model_metadata[model_path]
                else:
                    logger.error("Both requested model and fallback model are missing.")
                    # Return graceful failure metadata rather than crashing
                    return {
                        "model_name": model_id,
                        "version": "unknown",
                        "language_pair": f"{source_lang}-{target_lang}",
                        "loading_time_ms": 0.0,
                        "memory_usage_mb": 0.0,
                        "model_path": model_path,
                        "status": "missing"
                    }

            # 3. Load model and tokenizer from disk
            start_time = time.perf_counter()
            mem_before = self._get_process_rss_mb()
            
            try:
                from transformers import MarianMTModel, MarianTokenizer
                import torch
                
                logger.info(f"Loading local MarianMT model: {model_path}")
                
                # Force local_files_only to ensure no internet downloads at runtime
                tokenizer = MarianTokenizer.from_pretrained(model_path, local_files_only=True)
                model = MarianMTModel.from_pretrained(model_path, local_files_only=True)
                
                # Move to GPU if available
                device = "cuda" if torch.cuda.is_available() else "cpu"
                model = model.to(device)
                model.eval()  # Set evaluation mode
                
                # Measure statistics
                mem_after = self._get_process_rss_mb()
                loading_time = (time.perf_counter() - start_time) * 1000
                mem_diff = max(0.0, mem_after - mem_before)
                version = self._read_model_version(model_path)
                
                metadata = {
                    "model_name": model_id,
                    "version": version,
                    "language_pair": f"{source_lang}-{target_lang}",
                    "loading_time_ms": round(loading_time, 2),
                    "memory_usage_mb": round(mem_diff, 2),
                    "model_path": model_path,
                    "status": "loaded"
                }
                
                # Update caches
                self._model_cache[model_path] = (model, tokenizer)
                self._model_metadata[model_path] = metadata
                
                logger.info(f"Successfully loaded model {model_id} in {loading_time:.2f}ms (Memory: +{mem_diff:.2f} MB)")
                return metadata
                
            except Exception as e:
                logger.exception(f"Exception encountered while loading local model at '{model_path}': {e}")
                return {
                    "model_name": model_id,
                    "version": "unknown",
                    "language_pair": f"{source_lang}-{target_lang}",
                    "loading_time_ms": 0.0,
                    "memory_usage_mb": 0.0,
                    "model_path": model_path,
                    "status": f"error: {str(e)}"
                }

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """
        Translates text from source language to target language.
        Gracefully returns original text if loading fails.
        """
        if not text.strip():
            return text
            
        # Ensure model is loaded or fall back
        metadata = self.load_model(source_lang, target_lang)
        model_path, _ = self._get_model_path_and_id(source_lang, target_lang)
        
        # Check cache if fallback model was loaded instead
        if model_path not in self._model_cache:
            fallback_path, _ = self._get_model_path_and_id("mul", "en")
            if fallback_path in self._model_cache:
                model_path = fallback_path
            else:
                logger.warning("Translation model unavailable. Returning original text.")
                return text
                
        model, tokenizer = self._model_cache[model_path]
        
        # In mock mode, if we stored mock objects, return mock translation
        if model == "MOCK_MODEL":
            dummy_translations = {
                "id": "This is a translated Indonesian contract clause.",
                "fr": "This is a translated French contract clause.",
                "nl": "This is a translated Dutch contract clause.",
            }
            return dummy_translations.get(source_lang, f"[Translated {source_lang}->{target_lang}]: {text}")
            
        try:
            import torch
            device = next(model.parameters()).device
            
            # Helsinki-NLP models have a 512 max length window
            # Splitting text into chunks of roughly 1500 chars (safe window size)
            chunks = [text[i : i + 1500] for i in range(0, len(text), 1500)]
            translated_chunks = []
            
            for chunk in chunks:
                inputs = tokenizer(
                    chunk, 
                    return_tensors="pt", 
                    padding=True, 
                    truncation=True, 
                    max_length=512
                ).to(device)
                
                with torch.no_grad():
                    generated_ids = model.generate(**inputs)
                    
                decoded = tokenizer.decode(generated_ids[0], skip_special_tokens=True)
                translated_chunks.append(decoded)
                
            return "\n".join(translated_chunks)
            
        except Exception as e:
            logger.error(f"Inference translation failed: {e}. Returning original text.")
            return text

    def is_model_loaded(self, source_lang: str, target_lang: str) -> bool:
        """Returns True if the model path is loaded in the cache."""
        with self._lock:
            model_path, _ = self._get_model_path_and_id(source_lang, target_lang)
            return model_path in self._model_cache

    def check_is_cached(self, source_lang: str, target_lang: str = "en") -> bool:
        """Checks if files exist locally in settings.model_dir."""
        model_path, _ = self._get_model_path_and_id(source_lang, target_lang)
        return os.path.isdir(model_path)
