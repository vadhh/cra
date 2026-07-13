from typing import List, Optional
from pydantic import BaseModel, Field


class TranslationRequest(BaseModel):
    """Schema representing a text translation request."""
    text: str = Field(..., min_length=1, description="The input text to translate.")
    source_lang: str = Field("auto", description="The source language code (e.g., 'id', 'fr', 'nl'). Use 'auto' for automatic detection.")
    target_lang: str = Field("en", description="The target language code (default is 'en').")
    preserve_formatting: bool = Field(True, description="Whether to protect document structure and special symbols.")
    sector: Optional[str] = Field("Legal", description="The business/legal sector of the document (e.g., 'Employment', 'Software', 'Finance', 'Insurance', 'Construction', 'Government', 'Healthcare', 'Legal').")


class TranslationResponse(BaseModel):
    """Schema representing the translation API response."""
    original_text: str
    translated_text: str
    source_lang: str
    target_lang: str
    model_used: str
    processing_time_ms: float
    backend: str = "transformers"
    confidence: float = 1.0
    chunk_statistics: Optional[dict] = Field(default_factory=dict)
    page_statistics: Optional[dict] = Field(default_factory=dict)
    paragraph_statistics: Optional[dict] = Field(default_factory=dict)
    quality_score: float = 100.0
    risk_level: str = "LOW"
    warnings: List[str] = Field(default_factory=list)
    quality_report: Optional[dict] = Field(default_factory=dict)




class LanguageDetectionRequest(BaseModel):
    """Schema representing a request to detect language."""
    text: str = Field(..., min_length=1, description="Text to analyze for language identification.")


class LanguageDetectionResponse(BaseModel):
    """Schema representing the language detection response."""
    detected_lang: str
    confidence: float
    is_supported: bool


class ModelStatus(BaseModel):
    """Status details of an offline translation model."""
    model_name: str
    is_cached: bool
    is_loaded: bool


class SystemStatusResponse(BaseModel):
    """System health status and loaded models metadata."""
    status: str
    environment: str
    supported_languages: List[str]
    cached_models: List[ModelStatus]
