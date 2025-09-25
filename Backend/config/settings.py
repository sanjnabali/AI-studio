# Backend/config/settings.py
import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # App Configuration
    APP_NAME: str = "AI Studio"
    VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Security
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database
    DATABASE_URL: str = Field("sqlite:///./ai_studio.db", env="DATABASE_URL")

    # CORS - Allow comma-separated strings from env
    ALLOWED_HOSTS: List[str] = Field(default=["*"])
    CORS_ORIGINS: List[str] = Field(default=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ])

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


