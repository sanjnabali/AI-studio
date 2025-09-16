from pydantic import BaseModel, Field, validator
from typing import List, Literal, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class MessageType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    CODE = "code"
    FILE = "file"

class ChatMessage(BaseModel):
    """Enhanced chat message model"""
    role: MessageRole
    content: str
    type: MessageType = MessageType.TEXT
    metadata: Optional[Dict[str, Any]] = {}
    timestamp: Optional[datetime] = None
    
    @validator('content')
    def content_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Content cannot be empty')
        return v.strip()
    
    class Config:
        use_enum_values = True

class ChatRequest(BaseModel):
    """Enhanced chat request model"""
    messages: List[ChatMessage]
    temperature: Optional[float] = Field(0.7, ge=0.0, le=2.0)
    top_p: Optional[float] = Field(0.9, ge=0.0, le=1.0)
    top_k: Optional[int] = Field(50, ge=1, le=100)
    max_tokens: Optional[int] = Field(200, ge=1, le=2048)
    domain: Optional[str] = "general"
    use_rag: Optional[Union[bool, str]] = False  # Can be bool or adapter name
    stream: Optional[bool] = False
    model_name: Optional[str] = None
    fine_tuned_adapter: Optional[str] = None
    context_window: Optional[int] = Field(2048, ge=512, le=8192)
    
    @validator('domain')
    def validate_domain(cls, v):
        allowed_domains = ['general', 'code', 'creative', 'analysis', 'summarizer', 'marketing']
        if v not in allowed_domains:
            raise ValueError(f'Domain must be one of: {allowed_domains}')
        return v
    
    @validator('messages')
    def messages_not_empty(cls, v):
        if not v:
            raise ValueError('Messages list cannot be empty')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "messages": [
                    {"role": "user", "content": "Write a Python function to calculate fibonacci numbers"}
                ],
                "temperature": 0.7,
                "domain": "code",
                "max_tokens": 300
            }
        }

class ChatResponse(BaseModel):
    """Enhanced chat response model"""
    output: str
    tokens_input: Optional[int] = None
    tokens_output: Optional[int] = None
    latency_ms: Optional[float] = None
    citations: Optional[List[str]] = None
    model_used: Optional[str] = None
    domain_used: Optional[str] = None
    adapter_used: Optional[str] = None
    confidence_score: Optional[float] = None
    safety_score: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = {}
    
    class Config:
        schema_extra = {
            "example": {
                "output": "Here's a Python function to calculate Fibonacci numbers:\n\n```python\ndef fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)\n```",
                "tokens_input": 15,
                "tokens_output": 45,
                "latency_ms": 1250.5,
                "model_used": "microsoft/phi-2",
                "domain_used": "code"
            }
        }

class StreamingResponse(BaseModel):
    """Streaming response chunk"""
    chunk: str
    done: bool = False
    tokens_generated: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = {}

class FineTuningRequest(BaseModel):
    """Fine-tuning request model"""
    adapter_name: str = Field(..., min_length=1, max_length=50)
    training_data: List[Dict[str, Any]]
    base_model: Optional[str] = "microsoft/phi-2"
    lora_config: Optional[Dict[str, Any]] = None
    training_config: Optional[Dict[str, Any]] = None
    
    @validator('adapter_name')
    def validate_adapter_name(cls, v):
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Adapter name must contain only letters, numbers, hyphens, and underscores')
        return v
    
    @validator('training_data')
    def validate_training_data(cls, v):
        if len(v) < 1:
            raise ValueError('Training data must contain at least 1 example')
        if len(v) > 1000:
            raise ValueError('Training data cannot exceed 1000 examples')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "adapter_name": "code_specialist",
                "training_data": [
                    {
                        "messages": [
                            {"role": "user", "content": "Write a sorting function"},
                            {"role": "assistant", "content": "def quicksort(arr): ..."}
                        ],
                        "domain": "code"
                    }
                ],
                "lora_config": {
                    "r": 16,
                    "lora_alpha": 32,
                    "lora_dropout": 0.1
                }
            }
        }

class FineTuningResponse(BaseModel):
    """Fine-tuning response model"""
    job_id: str
    adapter_name: str
    status: Literal["queued", "running", "completed", "failed"]
    progress: Optional[float] = None
    message: Optional[str] = None
    metrics: Optional[Dict[str, float]] = {}
    created_at: datetime
    updated_at: datetime
    
    class Config:
        use_enum_values = True

class ModelInfo(BaseModel):
    """Model information model"""
    name: str
    type: str
    status: Literal["loaded", "loading", "error", "not_loaded"]
    parameters: Optional[int] = None
    memory_usage_mb: Optional[float] = None
    supported_features: List[str] = []
    fine_tuned_adapters: List[str] = []
    
    class Config:
        use_enum_values = True

class RAGDocument(BaseModel):
    """RAG document model"""
    content: str = Field(..., min_length=1)
    metadata: Optional[Dict[str, Any]] = {}
    doc_id: Optional[str] = None
    
    @validator('content')
    def content_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Document content cannot be empty')
        return v.strip()
    
    class Config:
        schema_extra = {
            "example": {
                "content": "This is a sample document about machine learning...",
                "metadata": {
                    "source": "research_paper.pdf",
                    "author": "John Doe",
                    "topic": "machine_learning"
                }
            }
        }

class RAGQuery(BaseModel):
    """RAG query model"""
    query: str = Field(..., min_length=1)
    top_k: Optional[int] = Field(5, ge=1, le=20)
    similarity_threshold: Optional[float] = Field(0.7, ge=0.0, le=1.0)
    filter_metadata: Optional[Dict[str, Any]] = {}
    
    class Config:
        schema_extra = {
            "example": {
                "query": "What is machine learning?",
                "top_k": 5,
                "similarity_threshold": 0.7,
                "filter_metadata": {"topic": "machine_learning"}
            }
        }

class RAGResponse(BaseModel):
    """RAG query response model"""
    query: str
    results: List[Dict[str, Any]]
    count: int
    max_similarity: Optional[float] = None
    avg_similarity: Optional[float] = None
    
    class Config:
        schema_extra = {
            "example": {
                "query": "What is machine learning?",
                "results": [
                    {
                        "document_id": "doc_123",
                        "content": "Machine learning is a subset of AI...",
                        "similarity_score": 0.92,
                        "metadata": {"source": "textbook.pdf"}
                    }
                ],
                "count": 1,
                "max_similarity": 0.92
            }
        }

class VoiceRequest(BaseModel):
    """Voice processing request"""
    audio_format: Literal["wav", "mp3", "ogg"] = "wav"

class VoiceResponse(BaseModel):
    """Voice processing response"""
    transcription: str
    confidence: Optional[float] = None
    language_detected: str = "en"
    duration_seconds: float = 0.0
    latency_ms: float = 0.0
