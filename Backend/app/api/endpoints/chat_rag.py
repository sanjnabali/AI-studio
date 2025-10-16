# Backend/app/api/endpoints/chat_rag.py
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging
import os
import uuid

from ...models.user import User, Document
from ...services.rag_engine import rag_engine, RAGEngine
from ...services.llm import llm_service
from ...api.deps import get_current_user
from ...core.database import get_db
from ...core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

class RAGRequest(BaseModel):
    query: str
    document_names: Optional[List[str]] = None
    model_options: Optional[Dict[str, Any]] = {}
    session_id: Optional[int] = None

class RAGResponse(BaseModel):
    response: str
    sources: List[Dict[str, Any]]
    model_used: str
    processing_time: float
    token_count: int
    context_used: int

class DocumentInfo(BaseModel):
    id: int
    filename: str
    original_filename: str
    file_size: int
    file_type: str
    processed: bool
    created_at: str
    chunk_count: int

@router.post("/upload", response_model=Dict[str, Any])
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload and process a document for RAG"""
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No file provided"
            )
        
        # Check file size
        file_content = await file.read()
        if len(file_content) > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File size exceeds {settings.MAX_FILE_SIZE} bytes"
            )
        
        # Check file type
        allowed_extensions = ['.pdf', '.docx', '.txt']
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type {file_ext} not supported. Allowed: {allowed_extensions}"
            )
        
        # Create upload directory
        upload_dir = os.path.join(settings.UPLOAD_FOLDER, str(current_user.id))
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filename
        unique_filename = f"{uuid.uuid4().hex}_{file.filename}"
        file_path = os.path.join(upload_dir, unique_filename)
        
        # Save file
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        # Create document record
        document = Document(
            user_id=current_user.id,
            filename=unique_filename,
            original_filename=file.filename,
            file_path=file_path,
            file_size=len(file_content),
            file_type=file_ext,
            processed=False
        )
        
        db.add(document)
        db.commit()
        db.refresh(document)
        
        # Process document with RAG engine
        processing_result = await rag_engine.process_document(
            file_path, 
            current_user.id, 
            file.filename
        )
        
        if processing_result["status"] == "success":
            document.processed = True
            document.chunk_count = processing_result["chunks_processed"]
            document.embedding_model = settings.EMBEDDING_MODEL
            db.commit()
            
            logger.info(f"Document processed successfully: {file.filename}")
            
            return {
                "status": "success",
                "document_id": document.id,
                "filename": file.filename,
                "chunks_processed": processing_result["chunks_processed"],
                "message": "Document uploaded and processed successfully"
            }
        else:
            # Mark as failed
            document.processed = False
            db.commit()
            
            # Clean up file
            if os.path.exists(file_path):
                os.remove(file_path)
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error processing document: {processing_result['error']}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error uploading document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading document: {str(e)}"
        )

@router.get("/documents", response_model=List[DocumentInfo])
async def get_user_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all documents for the current user"""
    try:
        documents = db.query(Document).filter(
            Document.user_id == current_user.id
        ).order_by(Document.created_at.desc()).all()
        
        return [
            DocumentInfo(
                id=doc.id,
                filename=doc.original_filename,
                original_filename=doc.original_filename,
                file_size=doc.file_size,
                file_type=doc.file_type,
                processed=doc.processed,
                created_at=doc.created_at.isoformat(),
                chunk_count=doc.chunk_count or 0
            )
            for doc in documents
        ]
        
    except Exception as e:
        logger.error(f"Error getting user documents: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving documents"
        )

@router.post("/query", response_model=RAGResponse)
async def rag_query(
    request: RAGRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Query documents using RAG"""
    try:
        # Merge model options with user preferences
        model_options = {**current_user.model_preferences, **(request.model_options or {})}

        # Generate RAG response
        rag_response = await rag_engine.generate_rag_response(
            request.query,
            current_user.id,
            llm_service,
            request.document_names,
            model_options
        )
        
        # Update usage stats
        if current_user.usage_stats is None:
            current_user.usage_stats = {"total_requests": 0, "total_tokens": 0}
        current_user.usage_stats["total_requests"] += 1
        current_user.usage_stats["total_tokens"] += rag_response["token_count"]
        db.commit()
        
        return RAGResponse(
            response=rag_response["response"],
            sources=rag_response["sources"],
            model_used=rag_response["model_used"],
            processing_time=rag_response["processing_time"],
            token_count=rag_response["token_count"],
            context_used=rag_response.get("context_used", 0)
        )
        
    except Exception as e:
        logger.error(f"Error in RAG query: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing RAG query: {str(e)}"
        )

@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    rag_engine: RAGEngine = Depends(RAGEngine)
):
    """Delete a document"""
    try:
        document = db.query(Document).filter(
            Document.id == document_id,
            Document.user_id == current_user.id
        ).first()
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        # Delete from vector database
        await rag_engine.delete_document(current_user.id, document.original_filename)
        
        # Delete file
        if os.path.exists(document.file_path):
            os.remove(document.file_path)
        
        # Delete database record
        db.delete(document)
        db.commit()
        
        return {"message": "Document deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting document"
        )
    