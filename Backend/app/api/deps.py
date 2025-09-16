"""
FastAPI dependencies for AI Studio Backend
"""

from typing import Optional, Dict, Any, Generator
from fastapi import Depends, HTTPException, Request, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import time
import logging

from ..core.config import settings, get_settings, domain_config, security_config
from ..core.security import get_current_user, check_rate_limit, rate_limiter, log_security_event
from ..core.exceptions import RateLimitException, AuthenticationException
from ..utils.helpers import perf_monitor

logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer(auto_error=False)


# Configuration Dependencies
def get_config() -> Dict[str, Any]:
    """Get application configuration"""
    return {
        "features": settings.FEATURES,
        "limits": {
            "max_file_size_mb": settings.MAX_FILE_SIZE_MB,
            "max_audio_duration": settings.MAX_AUDIO_DURATION_SECONDS,
            "code_timeout": settings.CODE_EXECUTION_TIMEOUT,
            "max_code_size": settings.MAX_CODE_SIZE_BYTES
        },
        "supported": {
            "languages": settings.ALLOWED_LANGUAGES,
            "audio_formats": settings.ALLOWED_AUDIO_EXTENSIONS,
            "document_formats": settings.ALLOWED_DOCUMENT_EXTENSIONS
        }
    }


def get_domain_settings(domain: str = "general") -> Dict[str, Any]:
    """Get domain-specific settings"""
    if domain not in domain_config.DOMAIN_SETTINGS:
        domain = "general"
    
    return {
        "prompt": domain_config.DOMAIN_PROMPTS.get(domain, domain_config.DOMAIN_PROMPTS["general"]),
        "settings": domain_config.DOMAIN_SETTINGS.get(domain, domain_config.DOMAIN_SETTINGS["general"]),
        "domain": domain
    }


# Authentication Dependencies
async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[Dict[str, Any]]:
    """Get current user if authenticated, None otherwise"""
    if not settings.FEATURES.get("authentication", False):
        return None
    
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials)
    except Exception as e:
        logger.warning(f"Optional authentication failed: {e}")
        return None


async def get_required_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """Get current user (authentication required)"""
    if not settings.FEATURES.get("authentication", False):
        raise HTTPException(
            status_code=501,
            detail="Authentication not enabled"
        )
    
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return await get_current_user(credentials)


# Rate Limiting Dependencies
async def rate_limit_chat(request: Request) -> None:
    """Rate limiting for chat endpoints"""
    if not settings.FEATURES.get("rate_limiting", False):
        return
    
    await check_rate_limit(request, "chat")


async def rate_limit_code_execution(request: Request) -> None:
    """Rate limiting for code execution endpoints"""
    if not settings.FEATURES.get("rate_limiting", False):
        return
    
    await check_rate_limit(request, "code_execution")


async def rate_limit_voice(request: Request) -> None:
    """Rate limiting for voice endpoints"""
    if not settings.FEATURES.get("rate_limiting", False):
        return
    
    await check_rate_limit(request, "voice_transcription")


async def rate_limit_image(request: Request) -> None:
    """Rate limiting for image generation endpoints"""
    if not settings.FEATURES.get("rate_limiting", False):
        return
    
    await check_rate_limit(request, "image_generation")


async def rate_limit_upload(request: Request) -> None:
    """Rate limiting for upload endpoints"""
    if not settings.FEATURES.get("rate_limiting", False):
        return
    
    await check_rate_limit(request, "document_upload")


# Request Validation Dependencies
async def validate_content_type(
    request: Request,
    allowed_types: list = ["application/json"]
) -> None:
    """Validate request content type"""
    content_type = request.headers.get("content-type", "").split(";")[0]
    
    if content_type not in allowed_types:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported content type: {content_type}. Allowed: {', '.join(allowed_types)}"
        )


async def validate_user_agent(
    user_agent: Optional[str] = Header(None)
) -> Optional[str]:
    """Validate and log user agent"""
    if user_agent:
        # Log suspicious user agents
        suspicious_patterns = ["bot", "crawler", "spider", "scraper"]
        if any(pattern in user_agent.lower() for pattern in suspicious_patterns):
            logger.warning(f"Suspicious user agent detected: {user_agent}")
    
    return user_agent


# Performance Monitoring Dependencies
class RequestTimer:
    """Context manager for request timing"""
    
    def __init__(self, endpoint_name: str):
        self.endpoint_name = endpoint_name
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = time.time() - self.start_time
            perf_monitor.record_metric(
                f"endpoint_latency_{self.endpoint_name}",
                duration * 1000,  # Convert to milliseconds
                {"endpoint": self.endpoint_name}
            )


async def track_request_metrics(request: Request) -> RequestTimer:
    """Dependency to track request metrics"""
    endpoint_name = request.url.path.replace("/", "_").replace("-", "_").strip("_")
    return RequestTimer(endpoint_name)


# Feature Flag Dependencies
async def require_feature(feature_name: str) -> None:
    """Require specific feature to be enabled"""
    if not settings.FEATURES.get(feature_name, False):
        raise HTTPException(
            status_code=501,
            detail=f"Feature '{feature_name}' is not enabled"
        )


def require_chat_text():
    """Dependency to require chat text feature"""
    return Depends(lambda: require_feature("chat_text"))


def require_chat_rag():
    """Dependency to require chat RAG feature"""
    return Depends(lambda: require_feature("chat_rag"))


def require_code_execution():
    """Dependency to require code execution feature"""
    return Depends(lambda: require_feature("code_execution"))


def require_voice_transcription():
    """Dependency to require voice transcription feature"""
    return Depends(lambda: require_feature("voice_transcription"))


def require_image_generation():
    """Dependency to require image generation feature"""
    return Depends(lambda: require_feature("image_generation"))


# Service Health Dependencies
async def check_model_health() -> Dict[str, Any]:
    """Check model service health"""
    # This would integrate with your actual model service
    return {
        "status": "healthy",
        "models_loaded": True,
        "last_check": time.time()
    }


async def check_storage_health() -> Dict[str, Any]:
    """Check storage health"""
    try:
        # Check if required directories exist and are writable
        import os
        from pathlib import Path
        
        directories = [
            settings.MODEL_CACHE_DIR,
            settings.RAG_STORAGE_DIR,
            str(settings.TEMP_DIR)
        ]
        
        health_status = {"status": "healthy", "directories": {}}
        
        for directory in directories:
            path = Path(directory)
            health_status["directories"][directory] = {
                "exists": path.exists(),
                "writable": path.exists() and os.access(path, os.W_OK),
                "readable": path.exists() and os.access(path, os.R_OK)
            }
        
        # Overall health
        all_healthy = all(
            info["exists"] and info["writable"] and info["readable"] 
            for info in health_status["directories"].values()
        )
        
        if not all_healthy:
            health_status["status"] = "degraded"
        
        return health_status
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


# Request Context Dependencies
async def get_request_context(
    request: Request,
    user_agent: Optional[str] = Depends(validate_user_agent),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user)
) -> Dict[str, Any]:
    """Get comprehensive request context"""
    return {
        "client_ip": request.client.host if request.client else "unknown",
        "user_agent": user_agent or "unknown",
        "method": request.method,
        "path": request.url.path,
        "query_params": dict(request.query_params),
        "headers": dict(request.headers),
        "user": current_user,
        "timestamp": time.time()
    }


# Security Headers Dependencies
async def add_security_context(request: Request) -> Dict[str, Any]:
    """Add security context to request"""
    return {
        "request_id": request.headers.get("x-request-id", f"req_{int(time.time())}"),
        "forwarded_for": request.headers.get("x-forwarded-for"),
        "real_ip": request.headers.get("x-real-ip"),
        "origin": request.headers.get("origin"),
        "referer": request.headers.get("referer")
    }


# Pagination Dependencies
async def get_pagination_params(
    page: int = 1,
    page_size: int = 20,
    max_page_size: int = 100
) -> Dict[str, int]:
    """Get pagination parameters with validation"""
    if page < 1:
        raise HTTPException(
            status_code=400,
            detail="Page must be >= 1"
        )
    
    if page_size < 1:
        raise HTTPException(
            status_code=400,
            detail="Page size must be >= 1"
        )
    
    if page_size > max_page_size:
        raise HTTPException(
            status_code=400,
            detail=f"Page size cannot exceed {max_page_size}"
        )
    
    return {
        "page": page,
        "page_size": page_size,
        "offset": (page - 1) * page_size
    }


# File Upload Dependencies
async def validate_file_size(request: Request) -> None:
    """Validate file upload size"""
    content_length = request.headers.get("content-length")
    
    if content_length:
        size_mb = int(content_length) / (1024 * 1024)
        if size_mb > settings.MAX_FILE_SIZE_MB:
            raise HTTPException(
                status_code=413,
                detail=f"File size ({size_mb:.1f}MB) exceeds maximum allowed size ({settings.MAX_FILE_SIZE_MB}MB)"
            )


# Database Dependencies (if using database)
async def get_db_session() -> Generator:
    """Get database session (placeholder)"""
    # This would return actual database session
    # For now, just return None since we're not using a database
    yield None


# Custom Dependencies Factory
def create_endpoint_dependency(
    require_auth: bool = False,
    rate_limit: Optional[str] = None,
    required_features: Optional[list] = None,
    track_metrics: bool = True
):
    """Factory function to create endpoint-specific dependencies"""
    
    async def endpoint_dependency(
        request: Request,
        config: Dict[str, Any] = Depends(get_config),
        context: Dict[str, Any] = Depends(get_request_context),
        security_context: Dict[str, Any] = Depends(add_security_context),
        timer: RequestTimer = Depends(track_request_metrics) if track_metrics else None
    ):
        # Check required features
        if required_features:
            for feature in required_features:
                if not settings.FEATURES.get(feature, False):
                    raise HTTPException(
                        status_code=501,
                        detail=f"Required feature '{feature}' is not enabled"
                    )
        
        # Apply rate limiting
        if rate_limit and settings.FEATURES.get("rate_limiting", False):
            await check_rate_limit(request, rate_limit)
        
        # Require authentication if needed
        if require_auth and settings.FEATURES.get("authentication", False):
            if not context.get("user"):
                raise HTTPException(
                    status_code=401,
                    detail="Authentication required"
                )
        
        return {
            "config": config,
            "context": context,
            "security": security_context,
            "timer": timer
        }
    
    return endpoint_dependency


# Commonly used endpoint dependencies
ChatDependency = create_endpoint_dependency(
    rate_limit="chat",
    required_features=["chat_text"],
    track_metrics=True
)

RAGDependency = create_endpoint_dependency(
    rate_limit="chat",
    required_features=["chat_rag"],
    track_metrics=True
)

CodeExecutionDependency = create_endpoint_dependency(
    rate_limit="code_execution",
    required_features=["code_execution"],
    track_metrics=True
)

VoiceDependency = create_endpoint_dependency(
    rate_limit="voice_transcription",
    required_features=["voice_transcription"],
    track_metrics=True
)

ImageDependency = create_endpoint_dependency(
    rate_limit="image_generation",
    required_features=["image_generation"],
    track_metrics=True
)

UploadDependency = create_endpoint_dependency(
    rate_limit="document_upload",
    track_metrics=True
)


# Export all dependencies
__all__ = [
    # Configuration
    "get_config", "get_domain_settings",
    
    # Authentication
    "get_optional_current_user", "get_required_current_user",
    
    # Rate limiting
    "rate_limit_chat", "rate_limit_code_execution", "rate_limit_voice",
    "rate_limit_image", "rate_limit_upload",
    
    # Validation
    "validate_content_type", "validate_user_agent", "validate_file_size",
    
    # Performance
    "RequestTimer", "track_request_metrics",
    
    # Feature flags
    "require_feature", "require_chat_text", "require_chat_rag",
    "require_code_execution", "require_voice_transcription", "require_image_generation",
    
    # Health checks
    "check_model_health", "check_storage_health",
    
    # Context
    "get_request_context", "add_security_context",
    
    # Pagination
    "get_pagination_params",
    
    # Database
    "get_db_session",
    
    # Factory
    "create_endpoint_dependency",
    
    # Common dependencies
    "ChatDependency", "RAGDependency", "CodeExecutionDependency",
    "VoiceDependency", "ImageDependency", "UploadDependency"
]