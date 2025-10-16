"""
Configuration management for AI Studio Backend
"""

from pydantic_settings import BaseSettings
from pydantic import validator
from typing import Optional, List, Dict, Any
import os
from pathlib import Path


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application Info
    PROJECT_NAME: str = "AI Studio API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Fast multimodal AI studio with optimized performance"
    API_V1_STR: str = "/api"
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 1
    RELOAD: bool = False
    LOG_LEVEL: str = "INFO"
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    @validator("DEBUG", pre=True)
    def set_debug(cls, v, values):
        return values.get("ENVIRONMENT") == "development"
    
    # Security
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"
    
    # CORS Settings
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001", 
        "http://127.0.0.1:3000",
        "https://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ]
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Model Configuration
    MODEL_NAME: str = "microsoft/phi-2"
    MODEL_CACHE_DIR: str = "/app/models"
    DEVICE: str = "auto"  # auto, cpu, cuda
    MODEL_MAX_LENGTH: int = 2048
    MODEL_TEMPERATURE: float = 0.7
    MODEL_TOP_K: int = 50
    MODEL_TOP_P: float = 0.9
    
    # Performance Settings
    MAX_CONCURRENT_REQUESTS: int = 10
    REQUEST_TIMEOUT_SECONDS: int = 300
    MODEL_LOADING_TIMEOUT: int = 600
    RESPONSE_CACHE_TTL: int = 300  # 5 minutes
    PRELOAD_ON_STARTUP: bool = False
    
    # File Upload Limits
    MAX_FILE_SIZE_MB: int = 50
    MAX_FILE_SIZE: int = 50 * 1024 * 1024
    UPLOAD_FOLDER: str = "uploads"
    MAX_AUDIO_DURATION_SECONDS: int = 600  # 10 minutes
    ALLOWED_AUDIO_EXTENSIONS: List[str] = [".wav", ".mp3", ".m4a", ".ogg", ".webm"]
    ALLOWED_DOCUMENT_EXTENSIONS: List[str] = [".txt", ".pdf", ".docx", ".md", ".json"]
    
    # Code Execution Settings
    CODE_EXECUTION_TIMEOUT: int = 30
    MAX_CODE_SIZE_BYTES: int = 51200  # 50KB
    ALLOWED_LANGUAGES: List[str] = ["python", "javascript", "bash", "shell"]
    CODE_TEMP_DIR: str = "/tmp"
    
    # RAG Configuration
    RAG_STORAGE_DIR: str = "/app/rag_storage"
    CHROMA_DB_PATH: str = "rag_storage"
    RAG_CHUNK_SIZE: int = 500
    RAG_CHUNK_OVERLAP: int = 50
    RAG_TOP_K: int = 5
    RAG_MAX_CONTEXT_LENGTH: int = 1500
    
    # Voice Processing
    WHISPER_MODEL_SIZE: str = "tiny"  # tiny, base, small, medium, large
    VOICE_PROCESSING_ENABLED: bool = True
    TTS_ENABLED: bool = False
    
    # Image Generation
    IMAGE_GENERATION_ENABLED: bool = False
    STABLE_DIFFUSION_MODEL: str = "runwayml/stable-diffusion-v1-5"
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    MAX_IMAGE_WIDTH: int = 1024
    MAX_IMAGE_HEIGHT: int = 1024
    
    # Database Settings (optional)
    DATABASE_URL: Optional[str] = "sqlite:///./ai_studio.db"
    REDIS_URL: Optional[str] = None
    
    # Logging Configuration
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE: Optional[str] = "/app/logs/app.log"
    LOG_ROTATION: str = "100 MB"
    LOG_RETENTION: str = "30 days"
    
    # Monitoring & Health Checks
    HEALTH_CHECK_INTERVAL: int = 30
    METRICS_ENABLED: bool = True
    SENTRY_DSN: Optional[str] = None
    
    # Feature Flags
    FEATURES: Dict[str, bool] = {
        "chat_text": True,
        "chat_rag": True,
        "code_execution": True,
        "voice_transcription": True,
        "image_generation": False,
        "streaming": True,
        "authentication": True,
        "rate_limiting": False
    }
    
    # Paths
    @property
    def BASE_DIR(self) -> Path:
        return Path(__file__).parent.parent.parent
    
    @property
    def LOGS_DIR(self) -> Path:
        logs_dir = self.BASE_DIR / "logs"
        logs_dir.mkdir(exist_ok=True)
        return logs_dir
    
    @property
    def TEMP_DIR(self) -> Path:
        temp_dir = self.BASE_DIR / "temp"
        temp_dir.mkdir(exist_ok=True)
        return temp_dir
    
    # Validation
    @validator("MODEL_CACHE_DIR")
    def validate_model_cache_dir(cls, v):
        Path(v).mkdir(parents=True, exist_ok=True)
        return v
    
    @validator("RAG_STORAGE_DIR")
    def validate_rag_storage_dir(cls, v):
        Path(v).mkdir(parents=True, exist_ok=True)
        return v
    
    # Environment-specific overrides
    def get_cors_origins(self) -> List[str]:
        """Get CORS origins based on environment"""
        if self.ENVIRONMENT == "production":
            return [origin for origin in self.BACKEND_CORS_ORIGINS if not origin.startswith("http://localhost")]
        return self.BACKEND_CORS_ORIGINS
    
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"
    
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"
    
    def get_log_level(self) -> str:
        if self.is_development():
            return "DEBUG"
        return "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "allow"


# Domain-specific configurations
class DomainConfig:
    """Domain-specific prompts and settings"""
    
    DOMAIN_PROMPTS = {
        "general": "You are a helpful AI assistant. Provide clear, accurate, and helpful responses.",
        "code": "You are an expert programmer. Provide clean, well-documented code with explanations.",
        "creative": "You are a creative writing assistant. Help with storytelling, poetry, and creative content.",
        "analysis": "You are a data analyst. Help with analysis, insights, and structured thinking.",
        "academic": "You are an academic assistant. Provide scholarly, well-researched responses.",
        "business": "You are a business consultant. Provide practical, actionable business advice."
    }
    
    DOMAIN_SETTINGS = {
        "general": {"temperature": 0.7, "max_tokens": 1000},
        "code": {"temperature": 0.3, "max_tokens": 1000},
        "creative": {"temperature": 0.9, "max_tokens": 1000},
        "analysis": {"temperature": 0.5, "max_tokens": 1000},
        "academic": {"temperature": 0.6, "max_tokens": 1000},
        "business": {"temperature": 0.7, "max_tokens": 1000}
    }


# Security configuration
class SecurityConfig:
    """Security-related configuration"""
    
    # Rate limiting (requests per minute)
    RATE_LIMITS = {
        "chat": 60,
        "code_execution": 30,
        "voice_transcription": 20,
        "image_generation": 10,
        "document_upload": 15
    }
    
    # Dangerous code patterns
    DANGEROUS_PATTERNS = [
        # System operations
        'rm -rf', 'del ', 'format ', 'fdisk', 'mkfs', 'sudo',
        # File operations
        'open(', 'file(', 'with open',
        # Network operations
        'urllib', 'requests', 'socket', 'http',
        # System imports
        'import os', 'import sys', 'import subprocess',
        # Execution functions
        'exec(', 'eval(', '__import__', 'compile(',
        # Input functions
        'input(', 'raw_input('
    ]
    
    # Allowed imports for code execution
    ALLOWED_IMPORTS = {
        "python": [
            "math", "random", "datetime", "json", "re",
            "collections", "itertools", "functools", "string",
            "numpy", "pandas", "matplotlib.pyplot"
        ],
        "javascript": [
            "console", "Math", "Date", "JSON", "String",
            "Array", "Object", "Number", "Boolean"
        ]
    }


# Create global settings instance
settings = Settings()
domain_config = DomainConfig()
security_config = SecurityConfig()


def get_settings() -> Settings:
    """Dependency to get settings"""
    return settings


def get_domain_config() -> DomainConfig:
    """Dependency to get domain config"""
    return domain_config


def get_security_config() -> SecurityConfig:
    """Dependency to get security config"""
    return security_config


# Environment detection utilities
def is_testing() -> bool:
    """Check if running in test environment"""
    return os.getenv("TESTING", "false").lower() == "true"


def is_docker() -> bool:
    """Check if running in Docker container"""
    return os.path.exists("/.dockerenv") or os.getenv("DOCKER_CONTAINER", "false").lower() == "true"


# Configuration validation
def validate_configuration():
    """Validate configuration at startup"""
    errors = []
    
    # Check required directories
    required_dirs = [
        settings.MODEL_CACHE_DIR,
        settings.RAG_STORAGE_DIR,
    ]
    
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            try:
                os.makedirs(dir_path, exist_ok=True)
            except Exception as e:
                errors.append(f"Cannot create directory {dir_path}: {e}")
    
    # Check feature dependencies
    if settings.FEATURES["voice_transcription"] and not settings.VOICE_PROCESSING_ENABLED:
        errors.append("Voice transcription feature enabled but voice processing disabled")
    
    if settings.FEATURES["image_generation"] and not settings.IMAGE_GENERATION_ENABLED:
        errors.append("Image generation feature enabled but image generation disabled")
    
    # Check security settings
    if settings.is_production() and settings.SECRET_KEY == "your-super-secret-key-change-in-production":
        errors.append("Default secret key being used in production environment")
    
    if errors:
        raise ValueError(f"Configuration validation failed: {'; '.join(errors)}")


# Export commonly used settings
__all__ = [
    "Settings",
    "DomainConfig", 
    "SecurityConfig",
    "settings",
    "domain_config",
    "security_config",
    "get_settings",
    "get_domain_config",
    "get_security_config",
    "validate_configuration",
    "is_testing",
    "is_docker"
]