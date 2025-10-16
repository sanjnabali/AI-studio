# Backend/app/api/endpoints/chat_text.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import logging
import time

from app.models.user import User, ChatSession, ChatMessage as DBChatMessage
from ...models.chat import ChatRequest, ChatResponse, MessageRole, MessageType
from sqlalchemy import func, case
from ...services.llm import llm_service
from ...api.deps import get_current_user
from ...core.database import get_db

logger = logging.getLogger(__name__)
router = APIRouter()

class ChatSessionCreate(BaseModel):
    name: Optional[str] = "New Chat"
    model_options: Optional[Dict[str, Any]] = {}

class ChatSessionResponse(BaseModel):
    id: int
    name: str
    created_at: str
    updated_at: str
    message_count: int
    model_options: Dict[str, Any]

class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    message_type: str
    metadata: Dict[str, Any]
    created_at: str
    token_count: int

@router.post("/sessions", response_model=ChatSessionResponse)
async def create_chat_session(
    session_data: ChatSessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new chat session"""
    try:
        new_session = ChatSession(
            user_id=current_user.id,
            session_name=session_data.name,
            model_options=session_data.model_options or current_user.model_preferences
        )
        
        db.add(new_session)
        db.commit()
        db.refresh(new_session)
        
        return ChatSessionResponse(
            id=new_session.id,
            name=new_session.session_name,
            created_at=new_session.created_at.isoformat(),
            updated_at=new_session.updated_at.isoformat(),
            message_count=0,
            model_options=new_session.model_options
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating chat session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating chat session"
        )

@router.get("/sessions", response_model=List[ChatSessionResponse])
async def get_chat_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all chat sessions for the current user"""
    try:
        # Optimized query to get sessions and message counts in one go
        sessions_with_counts = db.query(
            ChatSession,
            func.count(case((DBChatMessage.session_id == ChatSession.id, DBChatMessage.id))).label("message_count")
        ).outerjoin(DBChatMessage, DBChatMessage.session_id == ChatSession.id).filter(
            ChatSession.user_id == current_user.id,
            ChatSession.is_archived == False
        ).group_by(ChatSession.id).order_by(ChatSession.updated_at.desc()).all()
        
        session_responses = []
        for session, message_count in sessions_with_counts:
            session_responses.append(ChatSessionResponse(
                id=session.id,
                name=session.session_name,
                created_at=session.created_at.isoformat(),
                updated_at=session.updated_at.isoformat(),
                message_count=message_count,
                model_options=session.model_options
            ))

        return session_responses
        
    except Exception as e:
        logger.error(f"Error getting chat sessions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving chat sessions"
        )

@router.get("/sessions/{session_id}/messages", response_model=List[MessageResponse])
async def get_session_messages(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all messages for a chat session"""
    try:
        # Verify session ownership
        session = db.query(ChatSession).filter(
            ChatSession.id == session_id,
            ChatSession.user_id == current_user.id
        ).first()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )
        
        messages = db.query(DBChatMessage).filter(
            DBChatMessage.session_id == session_id
        ).order_by(DBChatMessage.created_at.asc()).all()
        
        return [
            MessageResponse(
                id=msg.id,
                role=msg.role,
                content=msg.content,
                message_type=msg.message_type,
                metadata=msg.metadata,
                created_at=msg.created_at.isoformat(),
                token_count=msg.token_count
            )
            for msg in messages
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session messages: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving messages"
        )

@router.post("/chat", response_model=ChatResponse)
async def chat_completion(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Process a chat completion request"""
    try:
        start_time = time.time()
        
        # Get or create session
        session = None
        if request.session_id:
            session = db.query(ChatSession).filter(
                ChatSession.id == request.session_id,
                ChatSession.user_id == current_user.id
            ).first()
        
        if not session:
            # Create new session
            session = ChatSession(
                user_id=current_user.id,
                session_name="New Chat",
                model_options=request.model_options or current_user.model_preferences
            )
            db.add(session)
            db.commit()
            db.refresh(session)
        
        # Save user message
        user_message = DBChatMessage(
            session_id=session.id,
            user_id=current_user.id,
            role=MessageRole.USER.value,
            content=request.message,
            message_type=MessageType.TEXT.value,
            metadata={},
            token_count=len(request.message.split())
        )
        db.add(user_message)
        
        # Get conversation history
        recent_messages = db.query(DBChatMessage).filter(
            DBChatMessage.session_id == session.id
        ).order_by(DBChatMessage.created_at.desc()).limit(10).all()
        
        # Build conversation context
        conversation_history = []
        for msg in reversed(recent_messages):
            conversation_history.append({
                "role": msg.role,
                "content": msg.content
            })
        conversation_history.append({
            "role": MessageRole.USER.value,
            "content": request.message
        })
        
        # Merge model options with user preferences
        model_options = {**current_user.model_preferences, **(request.model_options or {})}
        
        # Generate response
        llm_response = await llm_service.chat_completion(
            conversation_history,
            model_options
        )
        
        # Save assistant message
        assistant_message = DBChatMessage(
            session_id=session.id,
            user_id=current_user.id,
            role=MessageRole.ASSISTANT.value,
            content=llm_response["response"],
            message_type=MessageType.TEXT.value,
            metadata={
                "model_used": llm_response["model_used"],
                "processing_time": llm_response["processing_time"]
            },
            token_count=llm_response["token_count"]
        )
        db.add(assistant_message)
        
        # Update usage stats
        current_user.usage_stats["total_requests"] += 1
        current_user.usage_stats["total_tokens"] += llm_response["token_count"]
        current_user.usage_stats["last_request"] = time.time()
        
        db.commit()
        db.refresh(assistant_message)
        
        processing_time = time.time() - start_time
        
        return ChatResponse(
            message=llm_response["response"],
            session_id=session.id,
            message_id=assistant_message.id,
            model_used=llm_response["model_used"],
            token_count=llm_response["token_count"],
            processing_time=processing_time
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error in chat completion: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat request: {str(e)}"
        )

@router.delete("/sessions/{session_id}")
async def delete_chat_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a chat session"""
    try:
        session = db.query(ChatSession).filter(
            ChatSession.id == session_id,
            ChatSession.user_id == current_user.id
        ).first()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )
        
        # Delete all messages in the session
        db.query(DBChatMessage).filter(
            DBChatMessage.session_id == session_id
        ).delete()
        
        # Delete the session
        db.delete(session)
        db.commit()
        
        return {"message": "Chat session deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting chat session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting chat session"
        )