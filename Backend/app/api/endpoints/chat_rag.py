from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List, Optional
from ...models.chat import ChatRequest, ChatResponse
from ...services.llm import llm_service
from ...services.rag_engine import RAGEngine, RAGConfig
import logging
import json

logger = logging.getLogger(__name__)
router = APIRouter()

# Global RAG engine
rag_engine = RAGEngine()

@router.on_event("startup")
async def initialize_rag():
    """Initialize RAG engine on startup"""
    try:
        await rag_engine.initialize()
        logger.info("RAG engine initialized")
    except Exception as e:
        logger.error(f"Failed to initialize RAG engine: {e}")

@router.post("/", response_model=ChatResponse)
async def chat_rag(request: ChatRequest):
    """RAG-enhanced chat endpoint"""
    try:
        # Initialize services if needed
        if not llm_service.model:
            await llm_service.initialize()
        
        # Get the user's last message for context retrieval
        user_messages = [msg for msg in request.messages if msg.role == "user"]
        if not user_messages:
            raise HTTPException(status_code=400, detail="No user message found")
        
        last_user_message = user_messages[-1].content
        
        # Retrieve relevant context
        try:
            context = await rag_engine.get_context_for_query(
                last_user_message,
                max_context_length=1500
            )
            citations = await rag_engine.query(last_user_message, top_k=3)
            citation_list = [f"{i+1}. {cite['metadata'].get('source', 'Unknown')}" 
                           for i, cite in enumerate(citations)]
        except Exception as e:
            logger.warning(f"RAG retrieval failed: {e}")
            context = ""
            citation_list = []
        
        # Enhance messages with context
        enhanced_messages = []
        for msg in request.messages[:-1]:  # All messages except the last
            enhanced_messages.append(msg.dict())
        
        # Add context to the last user message
        if context:
            enhanced_content = f"Context:\n{context}\n\nQuestion: {last_user_message}"
        else:
            enhanced_content = last_user_message
            
        enhanced_messages.append({
            "role": "user",
            "content": enhanced_content
        })
        
        # Generate response
        output, latency = await llm_service.chat(
            messages=enhanced_messages,
            temperature=request.temperature or 0.7,
            top_k=request.top_k or 50,
            top_p=request.top_p or 0.9,
            domain=request.domain or "analysis",
            max_tokens=300
        )
        
        return ChatResponse(
            output=output,
            latency_ms=latency,
            citations=citation_list if citation_list else None
        )
        
    except Exception as e:
        logger.error(f"RAG chat error: {e}")
        raise HTTPException(status_code=500, detail=f"RAG chat error: {str(e)}")

@router.post("/upload-documents")
async def upload_documents(files: List[UploadFile] = File(...)):
    """Upload and index documents for RAG"""
    try:
        results = []
        
        for file in files:
            # Read file content
            content = await file.read()
            
            # Handle different file types
            if file.filename.endswith('.txt'):
                text_content = content.decode('utf-8')
            elif file.filename.endswith('.json'):
                json_data = json.loads(content.decode('utf-8'))
                text_content = json.dumps(json_data, indent=2)
            else:
                # For other types, try to decode as text
                try:
                    text_content = content.decode('utf-8')
                except:
                    logger.warning(f"Could not decode file {file.filename}, skipping")
                    continue
            
            # Add to RAG engine
            metadata = {
                "source": file.filename,
                "file_type": file.content_type,
                "file_size": len(content)
            }
            
            doc_id = await rag_engine.add_document(
                content=text_content,
                metadata=metadata
            )
            
            results.append({
                "filename": file.filename,
                "document_id": doc_id,
                "status": "indexed",
                "size": len(content)
            })
        
        return {
            "message": f"Successfully indexed {len(results)} documents",
            "documents": results,
            "rag_stats": rag_engine.get_stats()
        }
        
    except Exception as e:
        logger.error(f"Document upload error: {e}")
        raise HTTPException(status_code=500, detail=f"Upload error: {str(e)}")

@router.get("/documents")
async def list_documents():
    """List all indexed documents"""
    try:
        stats = rag_engine.get_stats()
        return {
            "stats": stats,
            "documents": list(rag_engine.documents.keys())[:50]  # Limit for performance
        }
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/documents/{doc_id}")
async def delete_document(doc_id: str):
    """Delete a document from the index"""
    try:
        success = await rag_engine.delete_document(doc_id)
        if success:
            return {"message": f"Document {doc_id} deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Document not found")
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search")
async def search_documents(query: str, top_k: int = 5):
    """Search documents directly"""
    try:
        results = await rag_engine.query(query, top_k=top_k)
        return {
            "query": query,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))