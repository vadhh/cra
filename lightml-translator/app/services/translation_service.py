import time
import logging
import re
import math
from typing import Optional, List, Dict, Tuple

# Set seed for reproducible langdetect results
from langdetect import detect, DetectorFactory
DetectorFactory.seed = 0

from app.preprocessing.cleaner import TextCleaner
from app.postprocessing.formatter import TextFormatter
from app.protection.tag_protector import TagProtector
from app.protection.pii_masker import PIIMasker
from app.protection.legal_protection import LegalProtectionEngine
from app.protection.glossary_engine import GlossaryEngine
from app.services.quality_analyzer import TranslationQualityAnalyzer
from app.translator.base import BaseTranslator
from app.models.schemas import TranslationResponse, LanguageDetectionResponse
from config.settings import settings

logger = logging.getLogger(__name__)


class SimpleLRUCache:
    """A thread-safe Least Recently Used (LRU) cache for translation segments."""
    def __init__(self, maxsize: int = 10000):
        from collections import OrderedDict
        import threading
        self.maxsize = maxsize
        self.cache = OrderedDict()
        self.lock = threading.Lock()

    def get(self, key):
        with self.lock:
            if key not in self.cache:
                return None
            self.cache.move_to_end(key)
            return self.cache[key]

    def set(self, key, value):
        with self.lock:
            if key in self.cache:
                self.cache.move_to_end(key)
            self.cache[key] = value
            if len(self.cache) > self.maxsize:
                self.cache.popitem(last=False)


class TranslationService:
    """
    Production-grade document translator orchestrating preprocessing,
    protection, model selection (CTranslate2 with Transformers fallback),
    automatic batching, retry mechanism, and profiling metadata collection.
    """
    
    _global_translation_cache = SimpleLRUCache(maxsize=10000)
    
    def __init__(
        self,
        translator: Optional[BaseTranslator] = None,
        cleaner: Optional[TextCleaner] = None,
        formatter: Optional[TextFormatter] = None,
        tag_protector: Optional[TagProtector] = None,
        pii_masker: Optional[PIIMasker] = None,
        legal_protector: Optional[LegalProtectionEngine] = None,
        glossary_engine: Optional[GlossaryEngine] = None,
        quality_analyzer: Optional[TranslationQualityAnalyzer] = None
    ):
        # Resolve best translator if not injected
        if translator is None:
            try:
                from app.translator.ctranslate2_engine import CTranslate2Translator
                from app.translator.marian import MarianTranslator
                
                if settings.use_ctranslate2 and CTranslate2Translator.is_available():
                    self._translator = CTranslate2Translator()
                    self._fallback_translator = MarianTranslator()
                else:
                    self._translator = MarianTranslator()
                    self._fallback_translator = None
            except Exception as e:
                logger.warning(f"Failed to load CTranslate2 translator: {e}. Falling back.")
                from app.translator.marian import MarianTranslator
                self._translator = MarianTranslator()
                self._fallback_translator = None
        else:
            self._translator = translator
            self._fallback_translator = None

        self._cleaner = cleaner or TextCleaner()
        self._formatter = formatter or TextFormatter()
        self._tag_protector = tag_protector or TagProtector()
        self._pii_masker = pii_masker or PIIMasker()
        self._legal_protector = legal_protector or LegalProtectionEngine()
        self._glossary_engine = glossary_engine or GlossaryEngine()
        self._quality_analyzer = quality_analyzer or TranslationQualityAnalyzer()
        self._translation_cache = self._global_translation_cache

    def detect_language(self, text: str) -> LanguageDetectionResponse:
        """Identifies language and checks whether it's supported by the translator."""
        try:
            detected = detect(text)
            is_supported = detected in settings.supported_languages
            # Dummy confidence score stub as langdetect returns categorical lang
            confidence = 0.99 
            return LanguageDetectionResponse(
                detected_lang=detected,
                confidence=confidence,
                is_supported=is_supported
            )
        except Exception as e:
            logger.warning(f"Language detection failed: {e}. Falling back to 'auto'.")
            return LanguageDetectionResponse(
                detected_lang="unknown",
                confidence=0.0,
                is_supported=False
            )

    def _translate_batch_with_retry_inner(
        self,
        batch: List[str],
        source_lang: str,
        target_lang: str,
        scores_out: List[float]
    ) -> List[str]:
        max_retries = 3
        # 1. Try primary CTranslate2 batch translation
        if hasattr(self._translator, "translate_batch"):
            for attempt in range(max_retries):
                try:
                    return self._translator.translate_batch(
                        batch, 
                        source_lang, 
                        target_lang, 
                        scores_out=scores_out
                    )
                except Exception as e:
                    logger.warning(f"Primary batch translation failed (attempt {attempt+1}/{max_retries}): {e}")
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt)  # Exponential backoff
            
            # If CTranslate2 failed, fall back to Transformers
            if self._fallback_translator:
                logger.info("CTranslate2 execution failed. Falling back to Transformers...")
                try:
                    return [self._fallback_translator.translate(s, source_lang, target_lang) for s in batch]
                except Exception as e:
                    logger.error(f"Fallback translator failed: {e}")
        else:
            # 2. Try standard Transformers/Marian translator
            try:
                return [self._translator.translate(s, source_lang, target_lang) for s in batch]
            except Exception as e:
                logger.warning(f"Transformers translation failed: {e}")
                if self._fallback_translator:
                    try:
                        return [self._fallback_translator.translate(s, source_lang, target_lang) for s in batch]
                    except Exception as e2:
                        logger.error(f"Fallback translator also failed: {e2}")

        # 3. Ultimate fallback: return original strings
        return batch

    def _translate_batch_with_retry(
        self, 
        batch: List[str], 
        source_lang: str, 
        target_lang: str,
        scores_out: List[float]
    ) -> List[str]:
        """Translates a batch of sentences with automatic error retries, fallback, and English pivot translation."""
        has_direct_model = False
        if hasattr(self._translator, "check_is_cached"):
            has_direct_model = self._translator.check_is_cached(source_lang, target_lang)

        if not has_direct_model and source_lang != "en" and target_lang != "en" and source_lang != target_lang:
            logger.info(f"Pivot translation active: {source_lang} -> en -> {target_lang}")
            scores_p1 = []
            en_batch = self._translate_batch_with_retry_inner(batch, source_lang, "en", scores_p1)
            scores_p2 = []
            target_batch = self._translate_batch_with_retry_inner(en_batch, "en", target_lang, scores_p2)
            
            # Combine scores (mean log-likelihoods)
            for idx in range(min(len(scores_p1), len(scores_p2))):
                scores_out.append((scores_p1[idx] + scores_p2[idx]) / 2.0)
            return target_batch
            
        return self._translate_batch_with_retry_inner(batch, source_lang, target_lang, scores_out)

    def translate_document(
        self, 
        text: str, 
        source_lang: str = "auto", 
        target_lang: str = "en",
        preserve_formatting: bool = True,
        sector: Optional[str] = "Legal"
    ) -> TranslationResponse:
        """
        Runs the full translation pipeline with sentence segmenting,
        automatic batching, structure preservation, and statistics tracking.
        """
        start_time = time.time()
        
        # 1. Preprocess cleaning
        cleaned_text = self._cleaner.clean(text)
        
        # 2. Detect language if set to auto
        actual_source = source_lang
        if source_lang == "auto" or not source_lang:
            detection = self.detect_language(cleaned_text)
            actual_source = detection.detected_lang
            if not detection.is_supported:
                logger.warning(f"Detected language '{actual_source}' is not supported. Using fallback.")
                
        # 3. Protect legal protected terms (HTML, Markdown, names, addresses, phone, currency, dates, numbers, etc.)
        legal_protected_text = cleaned_text
        legal_protection_map = {}
        if preserve_formatting:
            legal_protected_text, legal_protection_map = self._legal_protector.protect(cleaned_text)

        # 4. Inject glossary terms
        glossary_protected_text = legal_protected_text
        glossary_map = {}
        glossary_details = []
        if preserve_formatting:
            glossary_protected_text, glossary_map, glossary_details = self._glossary_engine.inject_glossary(
                legal_protected_text, actual_source, target_lang, sector
            )
            
        # 5. Protect PII (Emails, phone numbers)
        masked_text = legal_protected_text
        pii_map = {}
        if settings.pii_masking_enabled:
            masked_text, pii_map = self._pii_masker.mask(legal_protected_text)
            
        # 6. Segment document (Pages -> Paragraphs -> Sentences)
        # We split pages on form feed '\f'
        pages = masked_text.split("\f")
        page_count = len(pages)
        
        flat_sentences: List[Dict[str, Any]] = []
        sentence_counter = 0
        total_word_count = 0
        total_paragraph_count = 0
        
        sentence_splitter = re.compile(r'((?<=[.!?])\s+|\n+)')
        
        # Build structure map
        page_structures = []
        for p_idx, page in enumerate(pages):
            paragraphs = page.split("\n\n")
            total_paragraph_count += len(paragraphs)
            page_structure = []
            
            for pr_idx, para in enumerate(paragraphs):
                para_structure = []
                
                if not para.strip():
                    # Empty or newline whitespace paragraph
                    page_structure.append({"type": "empty", "content": para})
                    continue
                    
                sentences = sentence_splitter.split(para)
                for s_idx, sent in enumerate(sentences):
                    if s_idx % 2 == 1:
                        # This is a sentence separator delimiter
                        para_structure.append(sent)
                        continue
                        
                    # Keep track of words
                    word_count = len(sent.split())
                    total_word_count += word_count
                    
                    # Maximum token handling: split sentences that are excessively long
                    # Helsinki-NLP maximum context window is 512 tokens
                    if len(sent) > 800:
                        logger.info("Large chunk encountered. Segmenting further to respect maximum token limits.")
                        sub_splits = re.split(r'((?<=[,;])\s+)', sent)
                        for ss_idx, sub in enumerate(sub_splits):
                            if ss_idx % 2 == 1:
                                para_structure.append(sub)
                                continue
                            flat_sentences.append({
                                "text": sub,
                                "original_index": sentence_counter,
                                "translated": ""
                            })
                            para_structure.append(sentence_counter)
                            sentence_counter += 1
                    else:
                        flat_sentences.append({
                            "text": sent,
                            "original_index": sentence_counter,
                            "translated": ""
                        })
                        para_structure.append(sentence_counter)
                        sentence_counter += 1
                        
                page_structure.append({"type": "paragraph", "sentences": para_structure})
            page_structures.append(page_structure)
 
        # 7. Execute translations in batches, utilizing the thread-safe cache
        batch_size = settings.ctranslate2_batch_size
        scores: List[float] = []
        
        # Check cache for each sentence segment
        translated_texts = [None] * len(flat_sentences)
        sentences_to_translate_indices = []
        sentences_to_translate_texts = []
        
        for idx, s in enumerate(flat_sentences):
            text_to_trans = s["text"]
            if not text_to_trans.strip():
                translated_texts[idx] = text_to_trans
                continue
                
            cache_key = (actual_source, target_lang, text_to_trans)
            cached_val = self._translation_cache.get(cache_key)
            if cached_val is not None:
                translated_texts[idx] = cached_val
            else:
                sentences_to_translate_indices.append(idx)
                sentences_to_translate_texts.append(text_to_trans)

        # Batch translate only the missing segments
        if sentences_to_translate_texts:
            for i in range(0, len(sentences_to_translate_texts), batch_size):
                batch = sentences_to_translate_texts[i : i + batch_size]
                batch_scores: List[float] = []
                
                translated_batch = self._translate_batch_with_retry(
                    batch, 
                    actual_source, 
                    target_lang, 
                    scores_out=batch_scores
                )
                
                # Fill cache and map back
                for sub_idx, trans_text in enumerate(translated_batch):
                    orig_idx = sentences_to_translate_indices[i + sub_idx]
                    translated_texts[orig_idx] = trans_text
                    
                    orig_text = sentences_to_translate_texts[i + sub_idx]
                    cache_key = (actual_source, target_lang, orig_text)
                    self._translation_cache.set(cache_key, trans_text)
                    
                scores.extend(batch_scores)
 
        # Apply results back
        for idx, trans_text in enumerate(translated_texts):
            flat_sentences[idx]["translated"] = trans_text
 
        # 8. Reassemble document
        reassembled_pages = []
        for p_idx, page_struct in enumerate(page_structures):
            reassembled_paras = []
            for item in page_struct:
                if item["type"] == "empty":
                    reassembled_paras.append(item["content"])
                else:
                    para_pieces = []
                    for val in item["sentences"]:
                        if isinstance(val, int):
                            para_pieces.append(flat_sentences[val]["translated"])
                        else:
                            para_pieces.append(val)
                    reassembled_paras.append("".join(para_pieces))
            reassembled_pages.append("\n\n".join(reassembled_paras))
        
        reassembled_doc = "\f".join(reassembled_pages)
 
        # 9. Unmask PII and restore protected terms (reverse order of protection)
        unmasked_text = reassembled_doc
        if settings.pii_masking_enabled:
            unmasked_text = self._pii_masker.unmask(reassembled_doc, pii_map)
            
        restored_text = unmasked_text
        if preserve_formatting:
            restored_text = self._glossary_engine.restore_glossary(unmasked_text, glossary_map)
            restored_text = self._legal_protector.restore(restored_text, legal_protection_map)
            
        # 10. Postprocess format
        final_text = self._formatter.format(restored_text)
        
        duration = (time.time() - start_time) * 1000
        
        # Calculate confidence metric
        probs = []
        for s in scores:
            try:
                # Convert log likelihood to probability score
                p = math.exp(s) if s <= 0 else 1.0
                probs.append(p)
            except Exception:
                probs.append(1.0)
        avg_confidence = sum(probs) / len(probs) if probs else 1.0
 
        # Compile statistics
        chunk_count = len(flat_sentences)
        avg_chunk_len = sum(len(s["text"]) for s in flat_sentences) / chunk_count if chunk_count > 0 else 0
        
        chunk_stats = {
            "chunk_count": chunk_count,
            "avg_chunk_len": round(avg_chunk_len, 2),
            "batch_size": batch_size
        }
        
        page_stats = {
            "page_count": page_count,
            "avg_words_per_page": round(total_word_count / page_count, 2) if page_count > 0 else 0
        }
        
        paragraph_stats = {
            "paragraph_count": total_paragraph_count,
            "avg_sentences_per_paragraph": round(chunk_count / total_paragraph_count, 2) if total_paragraph_count > 0 else 0
        }
 
        # Resolve model name and backend details
        backend_name = "transformers"
        model_name = settings.marian_model_mappings.get(actual_source, settings.marian_fallback_model)
        
        if hasattr(self._translator, "load_model"):
            meta = self._translator.load_model(actual_source, target_lang)
            backend_name = meta.get("backend", "transformers")
            model_name = meta.get("model_name", model_name)

        # 11. Run Translation Quality Assurance Audit
        qa_result = self._quality_analyzer.analyze(
            source_text=cleaned_text,
            translated_text=final_text,
            source_lang=actual_source,
            target_lang=target_lang,
            avg_confidence=avg_confidence,
            glossary_map=glossary_map
        )
 
        return TranslationResponse(
            original_text=text,
            translated_text=final_text,
            source_lang=actual_source,
            target_lang=target_lang,
            model_used=model_name,
            processing_time_ms=round(duration, 2),
            backend=backend_name,
            confidence=round(avg_confidence, 4),
            chunk_statistics=chunk_stats,
            page_statistics=page_stats,
            paragraph_statistics=paragraph_stats,
            quality_score=qa_result["quality_score"],
            risk_level=qa_result["risk_level"],
            warnings=qa_result["warnings"],
            quality_report=qa_result["report"]
        )

