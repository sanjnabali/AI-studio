from fastapi import APIRouter
from .endpoints import auth, voice_to_text, image_gen, code_execution, chat_text, chat_rag

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
api_router.include_router(chat_text.router, prefix="/api/chat-text", tags=["chat_text"])
api_router.include_router(chat_rag.router, prefix="/api/chat-rag", tags=["chat_rag"])
api_router.include_router(voice_to_text.router, prefix="/api/voice-to-text", tags=["voice_to_text"])
api_router.include_router(image_gen.router, prefix="/api/image-gen", tags=["image_generation"])
api_router.include_router(code_execution.router, prefix="/api/code", tags=["code_execution"])
