# Backend/app/models/chat.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class MessageType(str, Enum):
    TEXT = "text"
    CODE = "code"
    IMAGE = "image"
    AUDIO = "audio"
    FILE = "file"

class ChatMessage(BaseModel):
    role: MessageRole
    content: str
    message_type: MessageType = MessageType.TEXT
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[int] = None
    model_options: Dict[str, Any] = Field(default_factory=dict)
    context_files: List[str] = Field(default_factory=list)

class ChatResponse(BaseModel):
    message: str
    session_id: int
    message_id: int
    model_used: str
    token_count: int
    processing_time: float

class ModelConfig(BaseModel):
    model_name: str = "microsoft/DialoGPT-medium"
    temperature: float = Field(0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(1000, ge=1, le=4000)
    top_p: float = Field(0.9, ge=0.0, le=1.0)
    top_k: int = Field(50, ge=1, le=100)
    frequency_penalty: float = Field(0.0, ge=-2.0, le=2.0)
    presence_penalty: float = Field(0.0, ge=-2.0, le=2.0)
