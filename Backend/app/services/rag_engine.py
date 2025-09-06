import faiss
from sentence_transformers import SentenceTransformer
import numpy as np

class RAGEngine:
    def __init__(self, embedding_model="all-MiniLM-L6-v2"):
        self.embed_model = SentenceTransformer(embedding_model)
        self.texts = []
        self.index = None

    def add_documents(self, docs: list[str]):
        embeddings = self.embed_model.encode(docs)
        self.texts.extend(docs)
        if self.index is None:
            self.index = faiss.IndexFlatL2(embeddings.shape[1])
        self.index.add(np.array(embeddings))

    def query(self, query: str, top_k: int = 3) -> list[str]:
        q_emb = self.embed_model.encode([query])
        D, I = self.index.search(np.array(q_emb), k=top_k)
        return [self.texts[i] for i in I[0]]
