from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
import asyncio
import logging
from contextlib import asynccontextmanager
import uvicorn
import torch
from transformers import (
    AutoTokenizer, AutoModelForCausalLM, 
    pipeline, BitsAndBytesConfig
)
from sentence_transformers import SentenceTransformer
from PIL import Image
import io
import tempfile
import time
from typing import Optional, Dict, Any
from pydantic import BaseModel
import json

# Import our modules
from app.api.endpoints import chat_text, chat_rag, voice_to_text
from app.services.llm import LocalLLMService
from app.services.rag_engine import RAGEngine
from app.models.chat import ChatRequest, ChatResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global model storage
model_store = {}

class CompletionRequest(BaseModel):
    prompt: str
    max_new_tokens: int = 100
    temperature: float = 0.6
    top_p: float = 0.9
    domain: Optional[str] = "general"

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management with model loading"""
    logger.info("Starting AI Studio Backend...")
    
    # Initialize models on startup
    await load_models()
    
    # Initialize RAG engine
    app.state.rag_engine = RAGEngine()
    
    yield
    
    # Cleanup on shutdown
    logger.info("Shutting down AI Studio Backend...")
    cleanup_models()

async def load_models():
    """Load all models asynchronously"""
    device = "cuda" if torch.cuda.is_available() else "cpu"
    logger.info(f"Loading models on device: {device}")
    
    try:
        # Load main LLM (Phi-2 - small but powerful)
        logger.info("Loading Phi-2 model...")
        
        # Quantization config for memory efficiency
        quantization_config = None
        if device == "cuda":
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.bfloat16
            )
        
        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained("microsoft/phi-2", trust_remote_code=True)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
            
        # Load model
        model = AutoModelForCausalLM.from_pretrained(
            "microsoft/phi-2",
            quantization_config=quantization_config,
            device_map="auto" if device == "cuda" else None,
            torch_dtype=torch.float16 if device == "cuda" else torch.float32,
            trust_remote_code=True
        )
        
        model_store["tokenizer"] = tokenizer
        model_store["model"] = model
        model_store["device"] = device
        
        # Load embedding model for RAG
        logger.info("Loading embedding model...")
        embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        model_store["embedding_model"] = embedding_model
        
        # Load Whisper for speech-to-text
        logger.info("Loading Whisper model...")
        whisper_pipe = pipeline(
            "automatic-speech-recognition", 
            model="openai/whisper-tiny.en",
            device=0 if device == "cuda" else -1
        )
        model_store["whisper_pipe"] = whisper_pipe
        
        # Load CLIP for image understanding
        logger.info("Loading CLIP model...")
        clip_pipe = pipeline(
            "zero-shot-image-classification",
            model="openai/clip-vit-base-patch16",
            device=0 if device == "cuda" else -1
        )
        model_store["clip_pipe"] = clip_pipe
        
        logger.info("All models loaded successfully!")
        
    except Exception as e:
        logger.error(f"Error loading models: {e}")
        raise

def cleanup_models():
    """Cleanup models and free memory"""
    global model_store
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    model_store.clear()

app = FastAPI(
    title="AI Studio API",
    description="Production-ready multimodal AI studio",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(chat_text.router, prefix="/api/chat-text", tags=["chat"])
app.include_router(chat_rag.router, prefix="/api/chat-rag", tags=["rag"])
app.include_router(voice_to_text.router, prefix="/api/voice", tags=["voice"])

@app.get("/")
def root():
    return {
        "message": "Welcome to AI Studio Backend!",
        "version": "1.0.0",
        "status": "running",
        "features": [
            "text_generation",
            "code_generation", 
            "rag_retrieval",
            "voice_to_text",
            "image_analysis",
            "multimodal_chat"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        model_status = {
            "main_model": "model" in model_store,
            "embedding_model": "embedding_model" in model_store,
            "whisper": "whisper_pipe" in model_store,
            "clip": "clip_pipe" in model_store
        }
        
        return {
            "status": "healthy",
            "models": model_status,
            "device": model_store.get("device", "unknown"),
            "cuda_available": torch.cuda.is_available(),
            "memory_usage": torch.cuda.memory_allocated() / 1024**3 if torch.cuda.is_available() else 0
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@app.post("/completion")
async def completion(request: CompletionRequest):
    """Text completion endpoint with domain specialization"""
    try:
        if "model" not in model_store or "tokenizer" not in model_store:
            raise HTTPException(status_code=503, detail="Models not loaded")
        
        model = model_store["model"]
        tokenizer = model_store["tokenizer"]
        device = model_store["device"]
        
        # Domain-specific prompts
        domain_prompts = {
            "code": "You are an expert programmer. Write clean, efficient code with comments.\n\n",
            "creative": "You are a creative writer. Write engaging, imaginative content.\n\n",
            "analysis": "You are a data analyst. Provide clear, actionable insights.\n\n",
            "general": "You are a helpful AI assistant.\n\n"
        }
        
        domain_prompt = domain_prompts.get(request.domain, domain_prompts["general"])
        full_prompt = domain_prompt + request.prompt
        
        # Tokenize input
        inputs = tokenizer(full_prompt, return_tensors="pt", truncate=True, max_length=1024)
        if device == "cuda":
            inputs = {k: v.to(device) for k, v in inputs.items()}
        
        # Generate response
        start_time = time.time()
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=request.max_new_tokens,
                temperature=request.temperature,
                top_p=request.top_p,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id,
                repetition_penalty=1.1
            )
        
        # Decode response
        response_text = tokenizer.decode(
            outputs[0][inputs["input_ids"].shape[-1]:], 
            skip_special_tokens=True
        ).strip()
        
        latency = (time.time() - start_time) * 1000
        
        return {
            "result": response_text,
            "latency_ms": latency,
            "tokens_generated": len(outputs[0]) - inputs["input_ids"].shape[-1],
            "domain": request.domain
        }
        
    except Exception as e:
        logger.error(f"Completion error: {e}")
        raise HTTPException(status_code=500, detail=f"Generation error: {str(e)}")

@app.post("/image2text/")
async def image_to_text(file: UploadFile = File(...)):
    """Image analysis endpoint"""
    try:
        if "clip_pipe" not in model_store:
            raise HTTPException(status_code=503, detail="CLIP model not loaded")
            
        clip_pipe = model_store["clip_pipe"]
        
        # Read and process image
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        
        # Define candidate labels for classification
        candidate_labels = [
            "a photograph of a person",
            "a photograph of an animal", 
            "a diagram or chart",
            "code or programming",
            "text document",
            "nature or landscape",
            "building or architecture",
            "food or cooking",
            "technology or electronics",
            "art or creative work"
        ]
        
        # Classify image
        results = clip_pipe(image, candidate_labels)
        
        # Get top result
        top_result = max(results, key=lambda x: x['score'])
        
        return {
            "label": top_result['label'],
            "confidence": top_result['score'],
            "all_results": results[:3],  # Return top 3 results
            "image_size": f"{image.width}x{image.height}"
        }
        
    except Exception as e:
        logger.error(f"Image analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"Image processing error: {str(e)}")

@app.post("/speech2text/")
async def speech_to_text(file: UploadFile = File(...)):
    """Speech-to-text endpoint"""
    try:
        if "whisper_pipe" not in model_store:
            raise HTTPException(status_code=503, detail="Whisper model not loaded")
            
        whisper_pipe = model_store["whisper_pipe"]
        
        # Save uploaded file temporarily
        audio_bytes = await file.read()
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp.flush()
            
            # Transcribe audio
            start_time = time.time()
            result = whisper_pipe(tmp.name)
            latency = (time.time() - start_time) * 1000
            
        return {
            "transcription": result["text"].strip(),
            "latency_ms": latency,
            "file_size": len(audio_bytes)
        }
        
    except Exception as e:
        logger.error(f"Speech-to-text error: {e}")
        raise HTTPException(status_code=500, detail=f"Speech processing error: {str(e)}")

@app.post("/embed")
async def create_embeddings(texts: list[str]):
    """Create embeddings for RAG"""
    try:
        if "embedding_model" not in model_store:
            raise HTTPException(status_code=503, detail="Embedding model not loaded")
            
        embedding_model = model_store["embedding_model"]
        
        start_time = time.time()
        embeddings = embedding_model.encode(texts)
        latency = (time.time() - start_time) * 1000
        
        return {
            "embeddings": embeddings.tolist(),
            "count": len(texts),
            "dimensions": embeddings.shape[1],
            "latency_ms": latency
        }
        
    except Exception as e:
        logger.error(f"Embedding error: {e}")
        raise HTTPException(status_code=500, detail=f"Embedding error: {str(e)}")

@app.get("/models/status")
async def model_status():
    """Get status of all loaded models"""
    return {
        "loaded_models": {
            "main_llm": "model" in model_store,
            "embedding": "embedding_model" in model_store, 
            "whisper": "whisper_pipe" in model_store,
            "clip": "clip_pipe" in model_store
        },
        "device": model_store.get("device", "unknown"),
        "memory_usage": {
            "allocated_gb": torch.cuda.memory_allocated() / 1024**3 if torch.cuda.is_available() else 0,
            "reserved_gb": torch.cuda.memory_reserved() / 1024**3 if torch.cuda.is_available() else 0
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Disable reload for production
        workers=1  # Single worker to avoid model loading issues
    )