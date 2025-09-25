# Backend/app/models/user.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, Dict, Any

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    last_login = Column(DateTime)
    
    # AI Studio specific fields
    api_key = Column(String(255), unique=True)
    model_preferences = Column(JSON, default=lambda: {
        "default_model": "microsoft/DialoGPT-medium",
        "temperature": 0.7,
        "max_tokens": 1000,
        "top_p": 0.9,
        "top_k": 50
    })
    usage_stats = Column(JSON, default=lambda: {
        "total_requests": 0,
        "total_tokens": 0,
        "last_request": None
    })

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    session_name = Column(String(255), default="New Chat")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    model_config = Column(JSON, default=lambda: {})
    is_archived = Column(Boolean, default=False)

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, index=True, nullable=False)
    user_id = Column(Integer, index=True, nullable=False)
    role = Column(String(50), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    message_type = Column(String(50), default="text")  # text, code, image, audio
    message_metadata = Column(JSON, default=lambda: {})
    created_at = Column(DateTime, default=func.now())
    token_count = Column(Integer, default=0)

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_type = Column(String(100), nullable=False)
    processed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    chunk_count = Column(Integer, default=0)
    embedding_model = Column(String(255))

class CodeExecution(Base):
    __tablename__ = "code_executions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    session_id = Column(Integer, index=True)
    language = Column(String(50), nullable=False)
    code = Column(Text, nullable=False)
    output = Column(Text)
    error = Column(Text)
    execution_time = Column(Integer)  # milliseconds
    created_at = Column(DateTime, default=func.now())
    status = Column(String(50), default="pending")  # pending, success, error


