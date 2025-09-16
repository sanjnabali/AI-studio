from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from ...models.chat import ChatRequest, ChatResponse, StreamingResponse
from ...services.llm import llm_service
import logging
import asyncio

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/", response_model=ChatResponse)
async def chat_text(request: ChatRequest):
    """Text-based chat endpoint with domain specialization"""
    try:
        # Initialize service if not already done
        if not llm_service.model:
            await llm_service.initialize()
        
        # Generate response
        output, latency = await llm_service.chat(
            messages=[msg.dict() for msg in request.messages],
            temperature=request.temperature or 0.7,
            top_k=request.top_k or 50,
            top_p=request.top_p or 0.9,
            domain=request.domain or "general",
            max_tokens=200,
            adapter_name=request.use_rag  # Use as adapter name if provided
        )
        
        # Count tokens (approximate)
        input_text = " ".join([msg.content for msg in request.messages])
        tokens_input = len(llm_service.tokenizer.encode(input_text)) if llm_service.tokenizer else 0
        tokens_output = len(llm_service.tokenizer.encode(output)) if llm_service.tokenizer else 0
        
        return ChatResponse(
            output=output,
            tokens_input=tokens_input,
            tokens_output=tokens_output,
            latency_ms=latency,
            citations=None
        )
        
    except Exception as e:
        logger.error(f"Chat text error: {e}")
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

@router.post("/stream")
async def chat_text_stream(request: ChatRequest):
    """Streaming chat endpoint"""
    try:
        if not llm_service.model:
            await llm_service.initialize()
            
        # For now, return regular response
        # In production, implement proper streaming
        output, latency = await llm_service.chat(
            messages=[msg.dict() for msg in request.messages],
            temperature=request.temperature or 0.7,
            top_k=request.top_k or 50,
            top_p=request.top_p or 0.9,
            domain=request.domain or "general",
            max_tokens=200
        )
        
        return {"output": output, "latency_ms": latency}
        
    except Exception as e:
        logger.error(f"Streaming chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Streaming error: {str(e)}")

@router.get("/models")
async def get_available_models():
    """Get available models and adapters"""
    try:
        model_info = llm_service.get_model_info()
        return {
            "base_model": model_info,
            "fine_tuned_adapters": llm_service.get_available_adapters(),
            "supported_domains": list(llm_service.domain_prompts.keys())
        }
    except Exception as e:
        logger.error(f"Error getting models: {e}")
        raise HTTPException(status_code=500, detail=str(e))