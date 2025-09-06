from fastapi import APIRouter
from app.models.chat import ChatRequest, ChatResponse
from app.services.llm import LocalLLMService

router = APIRouter()
llm_service = LocalLLMService()

@router.post("/")
async def chat_text(req: ChatRequest):
    messages_dicts = [m.dict() for m in req.messages]
    output, latency_ms = llm_service.chat(
        messages_dicts,
        temperature=req.temperature,
        top_k=req.top_k,
        top_p=req.top_p,
        domain=req.domain or "general"
    )
    return ChatResponse(output=output, latency_ms=latency_ms)
