# # Backend/app/main.py



from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import uvicorn
import logging
from contextlib import asynccontextmanager

# Import all modules
from config.settings import settings
from app.core.security import security_manager
from app.models.user import Base
from app.services.llm import llm_service
from app.services.rag_engine import rag_engine
from app.api.endpoints import auth, chat_text, chat_rag, voice_to_text, code_execution, image_gen

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Database setup
engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

# Security
security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting AI Studio application...")
    try:
        # Initialize RAG engine
        await rag_engine.initialize()
        logger.info("RAG engine initialized")
        
        # Pre-load default models
        await llm_service.get_model("chat")
        logger.info("Default chat model loaded")
        
        yield
        
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        raise
    finally:
        # Shutdown
        logger.info("Shutting down AI Studio application...")

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="AI Studio - Production-ready AI development platform",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dependency to get current user
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    try:
        token = credentials.credentials
        payload = security_manager.verify_token(token)
        user_id = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        # Get user from database
        from Backend.app.models.user import User
        user = db.query(User).filter(User.id == user_id).first()
        
        if user is None or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        return user
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "service": settings.APP_NAME
    }

# API health check endpoint (for frontend compatibility)
@app.get("/api/health")
async def api_health_check():
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "service": settings.APP_NAME,
        "api": "available"
    }

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(chat_text.router, prefix="/api/chat", tags=["Chat"])
app.include_router(chat_rag.router, prefix="/api/rag", tags=["RAG"])
app.include_router(voice_to_text.router, prefix="/api/voice", tags=["Voice"])
app.include_router(code_execution.router, prefix="/api/code", tags=["Code"])
app.include_router(image_gen.router, prefix="/api/image", tags=["Image"])

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.APP_NAME} API",
        "version": settings.VERSION,
        "docs": "/docs"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )