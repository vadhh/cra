import os
from typing import Dict, List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings for the Offline Translation Service.
    Loads variables from environment or a .env file.
    """
    # General API Configuration
    app_name: str = "LightML Offline Translation Service"
    env: str = "production"
    host: str = "0.0.0.0"
    port: int = 8000
    logging_level: str = "INFO"

    # Directory where local translation models are cached
    model_dir: str = os.getenv(
        "LIGHTML_MODELS_DIR", 
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")
    )

    # Core Translation Settings
    default_target_lang: str = "en"
    supported_languages: List[str] = ["id", "fr", "nl", "de", "es", "it", "pt", "en"]

    # Mapping of source language codes to Hugging Face MarianMT models
    marian_model_mappings: Dict[str, str] = {
        "id": "Helsinki-NLP/opus-mt-id-en",
        "fr": "Helsinki-NLP/opus-mt-fr-en",
        "nl": "Helsinki-NLP/opus-mt-nl-en",
        "de": "Helsinki-NLP/opus-mt-de-en",
        "es": "Helsinki-NLP/opus-mt-es-en",
        "it": "Helsinki-NLP/opus-mt-it-en",
        "pt": "Helsinki-NLP/opus-mt-pt-en",
    }
    marian_fallback_model: str = "Helsinki-NLP/opus-mt-mul-en"

    # Pre/Post Processing and Protection Configuration
    pii_masking_enabled: bool = True
    preserve_placeholders: bool = True
    max_chunk_size: int = 1500  # Character-based sliding window size for translation chunking

    # CTranslate2 Engine Configuration
    use_ctranslate2: bool = True
    ctranslate2_compute_type: str = "int8"  # "int8", "float16", "int16", "float32"
    ctranslate2_threads: int = 4            # Number of CPU threads for parallel decoding
    ctranslate2_batch_size: int = 16        # Default batch size for translation

    # Pydantic Settings Configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )



# Global settings instance
settings = Settings()
