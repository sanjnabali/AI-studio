# # Backend/app/main.py
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import uvicorn
import logging
import traceback
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse

# Import all modules
from app.core.config import settings
from app.core.security import security_manager
from app.models.user import Base
from app.services.llm import llm_service
from app.services.rag_engine import rag_engine
from app.api.endpoints import auth, chat_text, chat_rag, voice_to_text, code_execution, image_gen

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
logger = logging.getLogger("ai_studio")

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
        # Initialize heavy services optionally
        if settings.FEATURES.get("chat_rag") and settings.PRELOAD_ON_STARTUP:
            await rag_engine.initialize()
            logger.info("RAG engine initialized")
        else:
            logger.info("RAG engine preload skipped (will lazy-load on first use)")
        
        # Pre-load default models (chat, code, summarizer) optionally
        if settings.PRELOAD_ON_STARTUP:
            await llm_service.initialize()
            logger.info("Core models preloaded")
        else:
            logger.info("Model preload skipped (will lazy-load on first request)")
        
        yield
        
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        raise
    finally:
        # Shutdown
        logger.info("Shutting down AI Studio application...")

# Import rate limiter
from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address

# Create rate limiter
limiter = Limiter(key_func=get_remote_address)

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI Studio - Production-ready AI development platform",
    lifespan=lifespan
)

# Global error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled error", extra={
        "path": request.url.path,
        "method": request.method,
        "client": request.client.host if request.client else None,
        "error": str(exc),
        "trace": traceback.format_exc()[:4000]
    })
    return JSONResponse(status_code=500, content={"detail": "An unexpected error occurred. Please try again."})

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    # Pass-through but log
    logger.warning("HTTPException", extra={"path": request.url.path, "status": exc.status_code, "detail": exc.detail})
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

# Add rate limiter to app state
app.state.limiter = limiter

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
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
        from .models.user import User
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
        "service": settings.PROJECT_NAME
    }

# API health check endpoint (for frontend compatibility)
@app.get("/api/health")
async def api_health_check():
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "service": settings.PROJECT_NAME,
        "api": "available"
    }

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(chat_text.router, prefix="/api/chat", tags=["Chat"])
app.include_router(chat_rag.router, prefix="/api/rag", tags=["RAG"])
app.include_router(voice_to_text.router, prefix="/api/voice", tags=["Voice"])
app.include_router(code_execution.router, prefix="/api/code", tags=["Code"])
app.include_router(image_gen.router, prefix="/api/image", tags=["Image"])

# Frontend error reporting endpoint
@app.post("/api/errors")
async def report_frontend_error(payload: dict, request: Request):
    logger.warning("Frontend error report", extra={
        "path": request.url.path,
        "client": request.client.host if request.client else None,
        "payload": payload
    })
    return {"status": "received"}

# Diagnostics endpoint for deep health checks (no auth, read-only info)
@app.get("/api/diagnostics")
async def diagnostics(db: Session = Depends(get_db)):
    try:
        from app.models.user import User, ChatSession, ChatMessage
        users = db.query(User).count()
        sessions = db.query(ChatSession).count()
        messages = db.query(ChatMessage).count()
        return {
            "status": "ok",
            "service": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT,
            "database_url": (settings.DATABASE_URL or "sqlite:///./ai_studio.db").split("@")[-1],
            "counts": {"users": users, "sessions": sessions, "messages": messages},
            "features": settings.FEATURES,
            "preload_on_startup": settings.PRELOAD_ON_STARTUP,
        }
    except Exception as e:
        logger.error(f"Diagnostics error: {str(e)}")
        return JSONResponse(status_code=500, content={"detail": str(e)})

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} API",
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