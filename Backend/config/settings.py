# Backend/config/settings.py
import os
from typing import List, Optional, Any
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
import json

class Settings(BaseSettings):
    # App Configuration
    APP_NAME: str = Field(default="AI Studio")
    VERSION: str = Field(default="1.0.0")
    DEBUG: bool = Field(default=False)

    # Security
    SECRET_KEY: str = Field(default="dev-secret-key-please-change-32-characters-minimum-1234")
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7)

    # Database
    DATABASE_URL: str = Field(default="sqlite:///./ai_studio.db")

    # CORS Configuration
    ALLOWED_HOSTS: str = Field(default="*")
    CORS_ORIGINS: str = Field(default="http://localhost:3000,http://localhost:5173,http://127.0.0.1:5173")

    @property
    def allowed_hosts(self) -> List[str]:
        if self.ALLOWED_HOSTS == "*":
            return ["*"]
        return [h.strip() for h in self.ALLOWED_HOSTS.split(",") if h.strip()]

    @property
    def cors_origins(self) -> List[str]:
        default_origins = [
            "http://localhost:3000",
            "http://localhost:5173",
            "http://127.0.0.1:5173"
        ]
        if not self.CORS_ORIGINS:
            return default_origins
        origins = [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]
        return origins if origins else default_origins

    # Model Configuration
    DEFAULT_MODEL: str = "microsoft/DialoGPT-medium"
    CODE_MODEL: str = "microsoft/CodeBERT-base"
    SUMMARIZER_MODEL: str = "facebook/bart-large-cnn"

    # Hugging Face
    HF_TOKEN: Optional[str] = Field(None, env="HF_TOKEN")

    # Model Parameters
    DEFAULT_TEMPERATURE: float = 0.7
    DEFAULT_MAX_TOKENS: int = 1000
    DEFAULT_TOP_P: float = 0.9
    DEFAULT_TOP_K: int = 50

    # File Upload
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_FOLDER: str = "./uploads"

    # Voice Configuration
    SPEECH_TO_TEXT_MODEL: str = "openai/whisper-tiny"
    TEXT_TO_SPEECH_MODEL: str = "microsoft/speecht5_tts"

    # RAG Configuration
    CHROMA_DB_PATH: str = "./rag_storage/chroma_db"
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()


