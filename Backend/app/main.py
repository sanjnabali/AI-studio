from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import uvicorn
import warnings
import logging

from app.api import api_router
from app.core.config import settings

# Suppress warnings early
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    debug=settings.DEBUG,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint - ADD THIS
@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "message": "AI Studio API is running!",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "documentation": "/docs",
        "health": "/health",
        "api_base": settings.API_V1_STR,
        "endpoints": {
            "auth": f"{settings.API_V1_STR}/auth",
            "chat": f"{settings.API_V1_STR}/chat",
            "voice": f"{settings.API_V1_STR}/voice",
            "code": "/api/code",
            "image": "/image"
        }
    }

# Alternative: Redirect to docs
# @app.get("/")
# async def root():
#     """Redirect to API documentation"""
#     return RedirectResponse(url="/docs")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        workers=settings.WORKERS
    )