import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    # FastAPI settings
    APP_NAME: str = "AI Studio Backend"
    DEBUG: bool = True

    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Model settings
    STABLE_DIFFUSION_MODEL: str = "runwayml/stable-diffusion-v1-5"

    # File upload settings
    MAX_UPLOAD_SIZE_MB: int = 20

    # Security
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "your-secret-key")

    # Database (if needed)
    DATABASE_URL: str = os.environ.get("DATABASE_URL", "sqlite:///./ai_studio.db")

    # Other settings can be added as needed

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()