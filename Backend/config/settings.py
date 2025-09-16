import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from Backend/.env
backend_dir = Path(__file__).parent.parent  # Backend directory
env_path = backend_dir / ".env"
load_dotenv(dotenv_path=env_path)

class Settings:
    # Directory paths
    BACKEND_DIR = Path(__file__).parent.parent
    MLOPS_DIR = BACKEND_DIR.parent / "Mlops"
    MLFLOW_DIR = BACKEND_DIR.parent / "Mlflow"
    FRONTEND_DIR = BACKEND_DIR.parent / "Frontend"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "fallback-secret-key")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BACKEND_DIR}/backend.db")
    
    # LLM Settings
    LLM_MODEL_PATH: str = os.getenv("LLM_MODEL_PATH", str(MLOPS_DIR / "models"))
    LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "2048"))
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    
    # RAG Storage
    RAG_STORAGE_PATH: str = os.getenv("RAG_STORAGE_PATH", str(BACKEND_DIR / "rag_storage"))
    VECTOR_DB_PATH: str = os.getenv("VECTOR_DB_PATH", str(BACKEND_DIR / "rag_storage" / "vectordb"))
    
    # File Upload & Ingestion
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "10485760"))
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", str(BACKEND_DIR / "ingestion" / "uploads"))
    SUPPORTED_FILE_TYPES: list = os.getenv("SUPPORTED_FILE_TYPES", "pdf,txt,docx,md").split(",")
    
    # MLflow
    MLFLOW_TRACKING_URI: str = os.getenv("MLFLOW_TRACKING_URI", str(MLFLOW_DIR))
    MLFLOW_EXPERIMENT_NAME: str = os.getenv("MLFLOW_EXPERIMENT_NAME", "chat-experiments")
    
    # App Settings
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))

settings = Settings()