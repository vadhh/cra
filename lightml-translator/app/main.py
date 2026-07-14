import logging
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import router as api_router
from config.settings import settings

# Configure logging according to settings
logging.basicConfig(
    level=getattr(logging, settings.logging_level.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("app.main")

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Offline translation engine for Indonesian, French, and Dutch using Helsinki-NLP MarianMT models.",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for local cross-service communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup event handler to pre-warm models if needed
@app.on_event("startup")
async def startup_event():
    logger.info(f"Starting up {settings.app_name} in {settings.env} environment.")
    logger.info(f"Model cache directory set to: {settings.model_dir}")
    # Additional pre-loading of default translation models can be handled here.


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Stopping translation service...")


# Middleware to log API execution times
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    logger.debug(f"Request: {request.url.path} completed in {process_time:.4f}s")
    return response


# Basic Health check route
@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "service": settings.app_name
    }

# Include the API version router
app.include_router(api_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app", 
        host=settings.host, 
        port=settings.port, 
        reload=(settings.env == "development")
    )
