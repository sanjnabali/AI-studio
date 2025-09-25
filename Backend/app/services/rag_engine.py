# Backend/app/services/rag_engine.py
import os
import asyncio
import hashlib
from typing import List, Dict, Any, Optional
import logging
from config.settings import settings

# Disable ChromaDB telemetry before importing
os.environ["CHROMADB_DISABLE_TELEMETRY"] = "true"

# Patch posthog to prevent telemetry errors
try:
    import posthog
    # Monkey patch the capture method to prevent errors
    original_capture = posthog.capture
    def safe_capture(*args, **kwargs):
        try:
            return original_capture(*args, **kwargs)
        except Exception:
            pass  # Silently ignore telemetry errors
    posthog.capture = safe_capture
except ImportError:
    pass

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import fitz  # PyMuPDF
import docx
import pandas as pd
from pathlib import Path

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Handles document ingestion and text extraction"""
    
    @staticmethod
    def extract_text_from_pdf(file_path: str) -> List[Dict[str, Any]]:
        """Extract text from PDF file"""
        try:
            doc = fitz.open(file_path)
            chunks = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                
                if text.strip():  # Only process non-empty pages
                    # Split into smaller chunks (roughly 500 words)
                    words = text.split()
                    chunk_size = 500
                    
                    for i in range(0, len(words), chunk_size):
                        chunk_text = ' '.join(words[i:i + chunk_size])
                        if len(chunk_text.strip()) > 50:  # Ignore very small chunks
                            chunks.append({
                                'text': chunk_text,
                                'page': page_num + 1,
                                'chunk_id': f"page_{page_num + 1}_chunk_{i // chunk_size + 1}"
                            })
            
            doc.close()
            return chunks
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF {file_path}: {str(e)}")
            return []
    
    @staticmethod
    def extract_text_from_docx(file_path: str) -> List[Dict[str, Any]]:
        """Extract text from DOCX file"""
        try:
            doc = docx.Document(file_path)
            full_text = []
            
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    full_text.append(paragraph.text)
            
            text = '\n'.join(full_text)
            words = text.split()
            chunks = []
            chunk_size = 500
            
            for i in range(0, len(words), chunk_size):
                chunk_text = ' '.join(words[i:i + chunk_size])
                if len(chunk_text.strip()) > 50:
                    chunks.append({
                        'text': chunk_text,
                        'paragraph_range': f"{i}-{min(i + chunk_size, len(words))}",
                        'chunk_id': f"docx_chunk_{i // chunk_size + 1}"
                    })
            
            return chunks
            
        except Exception as e:
            logger.error(f"Error extracting text from DOCX {file_path}: {str(e)}")
            return []
    
    @staticmethod
    def extract_text_from_txt(file_path: str) -> List[Dict[str, Any]]:
        """Extract text from TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
            
            words = text.split()
            chunks = []
            chunk_size = 500
            
            for i in range(0, len(words), chunk_size):
                chunk_text = ' '.join(words[i:i + chunk_size])
                if len(chunk_text.strip()) > 50:
                    chunks.append({
                        'text': chunk_text,
                        'word_range': f"{i}-{min(i + chunk_size, len(words))}",
                        'chunk_id': f"txt_chunk_{i // chunk_size + 1}"
                    })
            
            return chunks
            
        except Exception as e:
            logger.error(f"Error extracting text from TXT {file_path}: {str(e)}")
            return []

class RAGEngine:
    """Retrieval-Augmented Generation Engine"""
    
    def __init__(self):
        self.embedding_model = None
        self.chroma_client = None
        self.collections: Dict[str, Any] = {}
        
    async def initialize(self):
        """Initialize the RAG engine"""
        try:
            # Disable ChromaDB telemetry completely
            os.environ["CHROMADB_DISABLE_TELEMETRY"] = "true"

            # Initialize embedding model
            logger.info("Loading embedding model...")
            self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)

            # Initialize ChromaDB
            os.makedirs(settings.CHROMA_DB_PATH, exist_ok=True)
            self.chroma_client = chromadb.PersistentClient(
                path=settings.CHROMA_DB_PATH,
                settings=Settings(anonymized_telemetry=False, is_persistent=True)
            )

            logger.info("RAG engine initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing RAG engine: {str(e)}")
            raise
    
    def _generate_collection_name(self, user_id: int, document_name: str) -> str:
        """Generate a unique collection name for user and document"""
        hash_input = f"{user_id}_{document_name}".encode('utf-8')
        hash_hex = hashlib.md5(hash_input).hexdigest()[:8]
        return f"user_{user_id}_doc_{hash_hex}"
    
    async def process_document(self, 
                             file_path: str, 
                             user_id: int, 
                             document_name: str) -> Dict[str, Any]:
        """Process and ingest a document into the vector database"""
        try:
            # Extract text based on file type
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext == '.pdf':
                chunks = DocumentProcessor.extract_text_from_pdf(file_path)
            elif file_ext == '.docx':
                chunks = DocumentProcessor.extract_text_from_docx(file_path)
            elif file_ext == '.txt':
                chunks = DocumentProcessor.extract_text_from_txt(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_ext}")
            
            if not chunks:
                raise ValueError("No text content extracted from document")
            
            # Generate embeddings
            texts = [chunk['text'] for chunk in chunks]
            embeddings = self.embedding_model.encode(texts, convert_to_tensor=False)
            
            # Create or get collection
            collection_name = self._generate_collection_name(user_id, document_name)
            
            try:
                collection = self.chroma_client.create_collection(
                    name=collection_name,
                    metadata={"user_id": user_id, "document_name": document_name}
                )
            except Exception:
                # Collection might already exist
                collection = self.chroma_client.get_collection(name=collection_name)
            
            # Prepare data for insertion
            ids = [f"{document_name}_{i}" for i in range(len(chunks))]
            metadatas = []
            
            for i, chunk in enumerate(chunks):
                metadata = {
                    "user_id": str(user_id),
                    "document_name": document_name,
                    "chunk_id": chunk.get('chunk_id', f'chunk_{i}'),
                    "file_type": file_ext
                }
                metadata.update({k: str(v) for k, v in chunk.items() if k != 'text'})
                metadatas.append(metadata)
            
            # Insert into ChromaDB
            collection.add(
                embeddings=embeddings.tolist(),
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            
            self.collections[collection_name] = collection
            
            return {
                "status": "success",
                "collection_name": collection_name,
                "chunks_processed": len(chunks),
                "document_name": document_name
            }
            
        except Exception as e:
            logger.error(f"Error processing document {document_name}: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "document_name": document_name
            }
    
    async def search_documents(self, 
                             query: str, 
                             user_id: int, 
                             document_names: Optional[List[str]] = None,
                             top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant document chunks"""
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query], convert_to_tensor=False)
            
            results = []
            
            # Get all user collections if no specific documents specified
            if not document_names:
                all_collections = self.chroma_client.list_collections()
                user_collections = [
                    col for col in all_collections 
                    if col.metadata and col.metadata.get("user_id") == user_id
                ]
            else:
                user_collections = []
                for doc_name in document_names:
                    collection_name = self._generate_collection_name(user_id, doc_name)
                    try:
                        collection = self.chroma_client.get_collection(name=collection_name)
                        user_collections.append(collection)
                    except Exception as e:
                        logger.warning(f"Collection {collection_name} not found: {str(e)}")
            
            # Search each collection
            for collection in user_collections:
                try:
                    search_results = collection.query(
                        query_embeddings=query_embedding.tolist(),
                        n_results=min(top_k, 10),
                        include=["documents", "metadatas", "distances"]
                    )
                    
                    for i in range(len(search_results['documents'][0])):
                        results.append({
                            "text": search_results['documents'][0][i],
                            "metadata": search_results['metadatas'][0][i],
                            "distance": search_results['distances'][0][i],
                            "document_name": search_results['metadatas'][0][i].get('document_name', 'Unknown')
                        })
                        
                except Exception as e:
                    logger.error(f"Error searching collection {collection.name}: {str(e)}")
            
            # Sort by distance (similarity)
            results.sort(key=lambda x: x['distance'])
            
            return results[:top_k]
            
        except Exception as e:
            logger.error(f"Error searching documents: {str(e)}")
            return []
    
    async def get_user_documents(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all documents for a user"""
        try:
            all_collections = self.chroma_client.list_collections()
            user_docs = []
            
            for collection in all_collections:
                if collection.metadata and collection.metadata.get("user_id") == user_id:
                    doc_info = {
                        "collection_name": collection.name,
                        "document_name": collection.metadata.get("document_name", "Unknown"),
                        "chunk_count": collection.count()
                    }
                    user_docs.append(doc_info)
            
            return user_docs
            
        except Exception as e:
            logger.error(f"Error getting user documents: {str(e)}")
            return []
    
    async def delete_document(self, user_id: int, document_name: str) -> bool:
        """Delete a document from the vector database"""
        try:
            collection_name = self._generate_collection_name(user_id, document_name)
            self.chroma_client.delete_collection(name=collection_name)
            
            if collection_name in self.collections:
                del self.collections[collection_name]
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting document {document_name}: {str(e)}")
            return False
    
    async def generate_rag_response(self, 
                                  query: str, 
                                  user_id: int,
                                  llm_service,
                                  document_names: Optional[List[str]] = None,
                                  model_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate response using RAG"""
        try:
            # Search for relevant documents
            search_results = await self.search_documents(
                query, user_id, document_names, top_k=3
            )
            
            if not search_results:
                return {
                    "response": "I couldn't find any relevant information in your documents to answer this question.",
                    "sources": [],
                    "model_used": "rag",
                    "processing_time": 0,
                    "token_count": 0
                }
            
            # Build context from search results
            context_parts = []
            sources = []
            
            for result in search_results:
                context_parts.append(f"Document: {result['document_name']}\nContent: {result['text']}")
                sources.append({
                    "document": result['document_name'],
                    "chunk_id": result['metadata'].get('chunk_id', 'unknown'),
                    "similarity": 1 - result['distance']  # Convert distance to similarity
                })
            
            context = "\n\n---\n\n".join(context_parts)
            
            # Build RAG prompt
            rag_prompt = f"""Based on the following context from the user's documents, please answer the question.

Context:
{context}

Question: {query}

Answer based on the provided context. If the context doesn't contain enough information to answer the question, please say so.

Answer:"""
            
            # Generate response using LLM
            if model_config is None:
                model_config = {}
            
            llm_response = await llm_service.generate_response(
                rag_prompt, 
                model_type="chat",
                **model_config
            )
            
            # Combine with RAG metadata
            return {
                "response": llm_response["response"],
                "sources": sources,
                "model_used": llm_response["model_used"],
                "processing_time": llm_response["processing_time"],
                "token_count": llm_response["token_count"],
                "context_used": len(search_results)
            }
            
        except Exception as e:
            logger.error(f"Error generating RAG response: {str(e)}")
            return {
                "response": f"I encountered an error while processing your question: {str(e)}",
                "sources": [],
                "model_used": "error",
                "processing_time": 0,
                "token_count": 0
            }

# Global RAG engine instance
rag_engine = RAGEngine()