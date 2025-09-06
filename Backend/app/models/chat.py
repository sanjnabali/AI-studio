from pydantic import BaseModel
from typing import List, Literal, Optional

Role = Literal['user', 'assistant', 'system']

class ChatMessage(BaseModel):
    role: Role
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = 0.95
    top_k: Optional[int] = 40
    domain: Optional[str] = None
    use_rag: Optional[bool] = False

class ChatResponse(BaseModel):
    output: str
    tokens_input: Optional[int] = None
    tokens_output: Optional[int] = None
    latency_ms: Optional[float] = None
    citations: Optional[List[str]] = None
