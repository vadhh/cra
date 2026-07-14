import os
import logging
import requests
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class SydecoTranslatorError(Exception):
    """Base exception for the Sydeco Translator client."""
    pass

class SydecoTranslatorClient:
    """
    Stable Python interface for the SYDECO LightML Translator.
    Enables Contract Risk Analyzer (CRA) integration either via the REST API
    or directly through the TranslationService in-process if available.
    """

    def __init__(self, endpoint_url: Optional[str] = None, prefer_in_process: bool = False):
        """
        Initializes the SydecoTranslatorClient.

        Parameters:
            endpoint_url: The URL of the translator microservice API.
                          If not provided, falls back to LIGHTML_TRANSLATOR_URL env var,
                          or http://lightml-translator:8000/api/v1.
            prefer_in_process: If True and the app packages are available,
                              loads the translation service in-process.
        """
        self.prefer_in_process = prefer_in_process
        self.service_instance = None

        if self.prefer_in_process:
            try:
                from app.services.translation_service import TranslationService
                self.service_instance = TranslationService()
                logger.info("SydecoTranslatorClient: Initialized translation service in-process.")
            except ImportError:
                logger.warning(
                    "SydecoTranslatorClient: TranslationService modules not found in path. "
                    "Falling back to REST API client."
                )

        if not self.service_instance:
            self.endpoint_url = (
                endpoint_url or 
                os.getenv("LIGHTML_TRANSLATOR_URL", "http://lightml-translator:8000/api/v1/translate")
            )
            # Ensure the endpoint points directly to the translate route
            if not self.endpoint_url.endswith("/translate") and not self.endpoint_url.endswith("/translate/"):
                # Clean trailing slash and append route
                base = self.endpoint_url.rstrip("/")
                if base.endswith("/api/v1"):
                    self.endpoint_url = base + "/translate"
                else:
                    self.endpoint_url = base + "/api/v1/translate"
            logger.info(f"SydecoTranslatorClient: Initialized REST API client pointing to {self.endpoint_url}")

    def translate(
        self, 
        text: str, 
        source_lang: str = "auto", 
        target_lang: str = "en", 
        preserve_formatting: bool = True,
        sector: str = "Legal"
    ) -> str:
        """
        Translates a text block and returns the raw translated string.
        """
        res = self.translate_document(
            text=text,
            source_lang=source_lang,
            target_lang=target_lang,
            preserve_formatting=preserve_formatting,
            sector=sector
        )
        return res.get("translated_text", text)

    def translate_document(
        self, 
        text: str, 
        source_lang: str = "auto", 
        target_lang: str = "en", 
        preserve_formatting: bool = True,
        sector: str = "Legal"
    ) -> Dict[str, Any]:
        """
        Translates a document and returns the full structured response (including statistics).
        """
        if not text.strip():
            return {
                "original_text": text,
                "translated_text": text,
                "source_lang": source_lang,
                "target_lang": target_lang,
                "quality_score": 100.0,
                "risk_level": "LOW"
            }

        # 1. In-process route
        if self.service_instance:
            try:
                response = self.service_instance.translate_document(
                    text=text,
                    source_lang=source_lang,
                    target_lang=target_lang,
                    preserve_formatting=preserve_formatting,
                    sector=sector
                )
                # Convert Pydantic model to dictionary
                return response.model_dump()
            except Exception as e:
                logger.error(f"In-process translation execution failed: {e}")
                raise SydecoTranslatorError(f"In-process translation failed: {e}")

        # 2. REST API route
        payload = {
            "text": text,
            "source_lang": source_lang,
            "target_lang": target_lang,
            "preserve_formatting": preserve_formatting,
            "sector": sector
        }
        try:
            resp = requests.post(self.endpoint_url, json=payload, timeout=120)
            if resp.status_code == 200:
                return resp.json()
            else:
                err_msg = f"HTTP {resp.status_code}: {resp.text}"
                logger.error(f"API translation request failed: {err_msg}")
                raise SydecoTranslatorError(f"REST API translation request failed: {err_msg}")
        except Exception as e:
            logger.error(f"API translation request connection error: {e}")
            raise SydecoTranslatorError(f"REST API connection error: {e}")

    def detect_language(self, text: str) -> Dict[str, Any]:
        """
        Detects the language of the given text.
        """
        if self.service_instance:
            try:
                response = self.service_instance.detect_language(text)
                return response.model_dump()
            except Exception as e:
                raise SydecoTranslatorError(f"In-process language detection failed: {e}")

        detect_url = self.endpoint_url.replace("/translate", "/detect")
        try:
            resp = requests.post(detect_url, json={"text": text}, timeout=30)
            if resp.status_code == 200:
                return resp.json()
            else:
                raise SydecoTranslatorError(f"REST API detect failed: HTTP {resp.status_code}")
        except Exception as e:
            raise SydecoTranslatorError(f"REST API detect connection error: {e}")

    def get_status(self) -> Dict[str, Any]:
        """
        Retrieves system health and cache loading status.
        """
        if self.service_instance:
            return {
                "status": "healthy",
                "mode": "in-process",
                "supported_languages": ["id", "fr", "nl", "de", "es", "it", "pt", "en"]
            }

        status_url = self.endpoint_url.replace("/translate", "/status")
        try:
            resp = requests.get(status_url, timeout=10)
            if resp.status_code == 200:
                return resp.json()
            else:
                raise SydecoTranslatorError(f"REST API status failed: HTTP {resp.status_code}")
        except Exception as e:
            raise SydecoTranslatorError(f"REST API status connection error: {e}")
