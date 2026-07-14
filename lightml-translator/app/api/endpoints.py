from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.models.schemas import (
    TranslationRequest,
    TranslationResponse,
    LanguageDetectionRequest,
    LanguageDetectionResponse,
    SystemStatusResponse,
    ModelStatus
)
from app.translator.marian import MarianTranslator
from app.translator.ctranslate2_engine import CTranslate2Translator
from app.services.translation_service import TranslationService
from config.settings import settings

router = APIRouter(prefix="/api/v1")

# Singleton for optimal translator resolution
if settings.use_ctranslate2 and CTranslate2Translator.is_available():
    _optimal_translator = CTranslate2Translator()
else:
    _optimal_translator = MarianTranslator()


def get_translation_service() -> TranslationService:
    """Dependency injection provider for the TranslationService."""
    return TranslationService(translator=_optimal_translator)



@router.post(
    "/translate", 
    response_model=TranslationResponse,
    status_code=status.HTTP_200_OK,
    summary="Translate text offline",
    description="Runs the full pipeline to clean, protect structure, mask PII, translate via MarianMT, and format output text."
)
async def translate(
    request: TranslationRequest,
    service: TranslationService = Depends(get_translation_service)
):
    try:
        response = service.translate_document(
            text=request.text,
            source_lang=request.source_lang,
            target_lang=request.target_lang,
            preserve_formatting=request.preserve_formatting,
            sector=request.sector
        )
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Translation process failed: {str(e)}"
        )


@router.post(
    "/detect", 
    response_model=LanguageDetectionResponse,
    status_code=status.HTTP_200_OK,
    summary="Detect source language",
    description="Identifies the language of the provided text and flags if it is supported locally."
)
async def detect_language(
    request: LanguageDetectionRequest,
    service: TranslationService = Depends(get_translation_service)
):
    return service.detect_language(request.text)


@router.get(
    "/status",
    response_model=SystemStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Get service status",
    description="Exposes local model caches and which translation models are active in memory."
)
async def get_system_status():
    cached_models = []
    for lang, model_id in settings.marian_model_mappings.items():
        is_cached = _optimal_translator.check_is_cached(lang)
        is_loaded = _optimal_translator.is_model_loaded(lang, "en")
        
        cached_models.append(
            ModelStatus(
                model_name=model_id,
                is_cached=is_cached,
                is_loaded=is_loaded
            )
        )
        
    return SystemStatusResponse(
        status="healthy",
        environment=settings.env,
        supported_languages=settings.supported_languages,
        cached_models=cached_models
    )

