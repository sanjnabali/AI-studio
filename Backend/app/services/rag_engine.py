import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional, Any, Tuple
import logging
import json
import pickle
from pathlib import Path
import asyncio
from dataclasses import dataclass
import hashlib
from datetime import datetime
import sqlite3

logger = logging.getLogger(__name__)

@dataclass
class Document:
    """Document representation for RAG"""
    id: str
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[np.ndarray] = None
    timestamp: Optional[datetime] = None

@dataclass
class RAGConfig:
    """RAG configuration"""
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    chunk_size: int = 512
    chunk_overlap: int = 50
    similarity_threshold: float = 0.7
    max_results: int = 5
    index_type: str = "flat"  # "flat" or "ivf"

class RAGEngine:
    """Enhanced RAG engine with document management and persistence"""
    
    def __init__(self, config: Optional[RAGConfig] = None, storage_path: str = "./rag_storage"):
        self.config = config or RAGConfig()
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        
        # Initialize components
        self.embedding_model = None
        self.index = None
        self.documents: Dict[str, Document] = {}
        self.document_embeddings = []
        
        # Database for metadata
        self.db_path = self.storage_path / "metadata.db"
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database for metadata"""
        conn = sqlite3.connect(str(self.db_path))
        conn.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                content TEXT,
                metadata TEXT,
                timestamp TEXT,
                content_hash TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS collections (
                id TEXT PRIMARY KEY,
                name TEXT,
                description TEXT,
                document_count INTEGER,
                created_at TEXT
            )
        """)
        conn.commit()
        conn.close()
    
    async def initialize(self):
        """Initialize the RAG engine"""
        logger.info("Initializing RAG Engine...")
        
        try:
            # Load embedding model
            logger.info(f"Loading embedding model: {self.config.embedding_model}")
            self.embedding_model = SentenceTransformer(self.config.embedding_model)
            
            # Load existing index and documents
            await self.load_from_disk()
            
            logger.info(f"RAG Engine initialized with {len(self.documents)} documents")
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG engine: {e}")
            raise
    
    def chunk_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks"""
        if len(text) <= self.config.chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.config.chunk_size
            
            # Try to break at sentence boundaries
            if end < len(text):
                # Find the last sentence ending before the limit
                last_period = text.rfind('.', start, end)
                last_exclamation = text.rfind('!', start, end)
                last_question = text.rfind('?', start, end)
                
                best_end = max(last_period, last_exclamation, last_question)
                if best_end > start:
                    end = best_end + 1
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = max(start + self.config.chunk_size - self.config.chunk_overlap, end)
        
        return chunks
    
    async def add_document(self, 
                          content: str, 
                          metadata: Optional[Dict[str, Any]] = None,
                          doc_id: Optional[str] = None) -> str:
        """Add a document to the RAG system"""
        
        if not self.embedding_model:
            raise ValueError("RAG engine not initialized")
        
        # Generate document ID if not provided
        if doc_id is None:
            content_hash = hashlib.md5(content.encode()).hexdigest()
            doc_id = f"doc_{content_hash[:12]}"
        
        metadata = metadata or {}
        metadata['added_at'] = datetime.now().isoformat()
        
        try:
            # Chunk the document
            chunks = self.chunk_text(content)
            logger.info(f"Document {doc_id} split into {len(chunks)} chunks")
            
            # Generate embeddings for all chunks
            embeddings = await asyncio.get_event_loop().run_in_executor(
                None, self.embedding_model.encode, chunks
            )
            
            # Store chunks as separate documents
            chunk_ids = []
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                chunk_id = f"{doc_id}_chunk_{i}"
                chunk_metadata = {**metadata, "chunk_id": i, "parent_doc": doc_id}
                
                document = Document(
                    id=chunk_id,
                    content=chunk,
                    metadata=chunk_metadata,
                    embedding=embedding,
                    timestamp=datetime.now()
                )
                
                self.documents[chunk_id] = document
                self.document_embeddings.append(embedding)
                chunk_ids.append(chunk_id)
            
            # Update FAISS index
            await self.rebuild_index()
            
            # Save to database
            await self.save_document_to_db(doc_id, content, metadata)
            
            logger.info(f"Added document {doc_id} with {len(chunks)} chunks")
            return doc_id
            
        except Exception as e:
            logger.error(f"Error adding document {doc_id}: {e}")
            raise
    
    async def rebuild_index(self):
        """Rebuild the FAISS index"""
        if not self.document_embeddings:
            return
        
        embeddings_array = np.array(self.document_embeddings).astype('float32')
        dimension = embeddings_array.shape[1]
        
        if self.config.index_type == "ivf" and len(self.document_embeddings) > 100:
            # Use IVF index for larger collections
            nlist = min(100, len(self.document_embeddings) // 10)
            quantizer = faiss.IndexFlatL2(dimension)
            self.index = faiss.IndexIVFFlat(quantizer, dimension, nlist)
            self.index.train(embeddings_array)
        else:
            # Use flat index for smaller collections
            self.index = faiss.IndexFlatL2(dimension)
        
        self.index.add(embeddings_array)
        logger.info(f"Rebuilt index with {len(self.document_embeddings)} embeddings")
    
    async def query(self, 
                   query: str, 
                   top_k: int = None,
                   similarity_threshold: float = None,
                   filter_metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Query the RAG system"""
        
        if not self.embedding_model or not self.index:
            raise ValueError("RAG engine not initialized or no documents indexed")
        
        top_k = top_k or self.config.max_results
        similarity_threshold = similarity_threshold or self.config.similarity_threshold
        
        try:
            # Generate query embedding
            query_embedding = await asyncio.get_event_loop().run_in_executor(
                None, self.embedding_model.encode, [query]
            )
            query_embedding = query_embedding.astype('float32')
            
            # Search index
            distances, indices = self.index.search(query_embedding, top_k * 2)  # Get extra results for filtering
            
            results = []
            document_ids = list(self.documents.keys())
            
            for distance, idx in zip(distances[0], indices[0]):
                if idx >= len(document_ids):
                    continue
                    
                doc_id = document_ids[idx]
                document = self.documents[doc_id]
                
                # Calculate similarity score (convert L2 distance to similarity)
                similarity = 1.0 / (1.0 + distance)
                
                # Apply similarity threshold
                if similarity < similarity_threshold:
                    continue
                
                # Apply metadata filtering
                if filter_metadata:
                    if not all(
                        document.metadata.get(key) == value
                        for key, value in filter_metadata.items()
                    ):
                        continue
                
                results.append({
                    "document_id": doc_id,
                    "content": document.content,
                    "metadata": document.metadata,
                    "similarity_score": similarity,
                    "distance": float(distance)
                })
                
                if len(results) >= top_k:
                    break
            
            return results
            
        except Exception as e:
            logger.error(f"Query error: {e}")
            raise
    
    async def get_context_for_query(self, 
                                   query: str, 
                                   max_context_length: int = 2000) -> str:
        """Get formatted context for a query"""
        
        results = await self.query(query)
        
        if not results:
            return "No relevant context found."
        
        context_parts = []
        current_length = 0
        
        for result in results:
            content = result["content"]
            metadata = result.get("metadata", {})
            
            # Format context with metadata
            source_info = ""
            if "source" in metadata:
                source_info = f" (Source: {metadata['source']})"
            elif "parent_doc" in metadata:
                source_info = f" (Document: {metadata['parent_doc']})"
            
            formatted_content = f"{content}{source_info}"
            
            if current_length + len(formatted_content) > max_context_length:
                break
            
            context_parts.append(formatted_content)
            current_length += len(formatted_content)
        
        return "\n\n".join(context_parts)
    
    async def save_document_to_db(self, doc_id: str, content: str, metadata: Dict[str, Any]):
        """Save document metadata to database"""
        conn = sqlite3.connect(str(self.db_path))
        try:
            content_hash = hashlib.md5(content.encode()).hexdigest()
            conn.execute("""
                INSERT OR REPLACE INTO documents 
                (id, content, metadata, timestamp, content_hash)
                VALUES (?, ?, ?, ?, ?)
            """, (doc_id, content[:1000], json.dumps(metadata), 
                 datetime.now().isoformat(), content_hash))
            conn.commit()
        finally:
            conn.close()
    
    async def load_from_disk(self):
        """Load existing documents and index from disk"""
        try:
            # Load documents from database
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.execute("SELECT id, content, metadata FROM documents")
            
            for row in cursor.fetchall():
                doc_id, content, metadata_json = row
                metadata = json.loads(metadata_json) if metadata_json else {}
                
                # For now, just store basic info - full content would need separate storage
                document = Document(
                    id=doc_id,
                    content=content,
                    metadata=metadata,
                    timestamp=datetime.now()
                )
                self.documents[doc_id] = document
            
            conn.close()
            
            # Load FAISS index if it exists
            index_path = self.storage_path / "faiss_index.bin"
            if index_path.exists():
                self.index = faiss.read_index(str(index_path))
                logger.info(f"Loaded existing FAISS index with {self.index.ntotal} vectors")
            
        except Exception as e:
            logger.warning(f"Could not load existing data: {e}")
    
    async def save_to_disk(self):
        """Save index and documents to disk"""
        try:
            if self.index:
                index_path = self.storage_path / "faiss_index.bin"
                faiss.write_index(self.index, str(index_path))
                logger.info("Saved FAISS index to disk")
                
        except Exception as e:
            logger.error(f"Error saving to disk: {e}")
    
    async def delete_document(self, doc_id: str) -> bool:
        """Delete a document and its chunks"""
        try:
            # Find all chunks for this document
            chunk_ids = [
                cid for cid, doc in self.documents.items()
                if doc.metadata.get("parent_doc") == doc_id or cid == doc_id
            ]
            
            # Remove from memory
            for chunk_id in chunk_ids:
                if chunk_id in self.documents:
                    del self.documents[chunk_id]
            
            # Remove from database
            conn = sqlite3.connect(str(self.db_path))
            conn.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
            conn.commit()
            conn.close()
            
            # Rebuild index
            self.document_embeddings = [
                doc.embedding for doc in self.documents.values() 
                if doc.embedding is not None
            ]
            await self.rebuild_index()
            
            logger.info(f"Deleted document {doc_id} and {len(chunk_ids)} chunks")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting document {doc_id}: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get RAG system statistics"""
        return {
            "total_documents": len(set(
                doc.metadata.get("parent_doc", doc.id) 
                for doc in self.documents.values()
            )),
            "total_chunks": len(self.documents),
            "index_size": self.index.ntotal if self.index else 0,
            "embedding_dimension": self.embedding_model.get_sentence_embedding_dimension() if self.embedding_model else 0,
            "storage_path": str(self.storage_path),
            "config": {
                "chunk_size": self.config.chunk_size,
                "chunk_overlap": self.config.chunk_overlap,
                "similarity_threshold": self.config.similarity_threshold,
                "max_results": self.config.max_results
            }
        }
    
    async def cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up RAG engine...")
        await self.save_to_disk()
        self.embedding_model = None
        self.index = None
        self.documents.clear()
        self.document_embeddings.clear()