"""
Local ChromaDB Vector Store for SIH26117 Member 4.
Runs 100% locally. Prohibits cloud vector DBs (Pinecone, Qdrant Cloud, Weaviate Cloud).
"""

import math
import os
from typing import List, Dict, Any, Optional

try:
    from backend.rag.schemas import Chunk
except ImportError:
    from .schemas import Chunk

class LocalVectorStore:
    """
    Local vector store wrapping ChromaDB with local persistence / SQLite storage
    and a local fallback store for pure offline operation.
    """

    def __init__(self, collection_name: str = "sovereign_rag", persist_directory: Optional[str] = None):
        self.collection_name = collection_name
        self.persist_directory = persist_directory or os.path.join(os.getcwd(), "outputs", "chromadb")
        self._chroma_client = None
        self._collection = None
        self._fallback_store: List[Dict[str, Any]] = []
        self._init_chroma()

    def _init_chroma(self):
        try:
            import chromadb
            os.makedirs(self.persist_directory, exist_ok=True)
            self._chroma_client = chromadb.PersistentClient(path=self.persist_directory)
            self._collection = self._chroma_client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
        except Exception:
            self._chroma_client = None
            self._collection = None

    def add_chunks(self, chunks: List[Chunk], embeddings: List[List[float]]) -> None:
        if not chunks:
            return

        if self._collection is not None:
            ids = [c.chunk_id for c in chunks]
            documents = [c.text for c in chunks]
            metadatas = [
                {
                    "document_id": c.document_id,
                    "filename": c.filename,
                    "page": c.page,
                    "section": c.section,
                    "chunk_id": c.chunk_id,
                    "source_type": c.source_type,
                    "content_hash": c.content_hash
                }
                for c in chunks
            ]
            self._collection.upsert(
                ids=ids,
                documents=documents,
                metadatas=metadatas,
                embeddings=embeddings
            )
            return

        for chunk, emb in zip(chunks, embeddings):
            self._fallback_store = [item for item in self._fallback_store if item["chunk_id"] != chunk.chunk_id]
            self._fallback_store.append({
                "chunk_id": chunk.chunk_id,
                "chunk": chunk,
                "embedding": emb,
                "text": chunk.text,
                "metadata": {
                    "document_id": chunk.document_id,
                    "filename": chunk.filename,
                    "page": chunk.page,
                    "section": chunk.section,
                    "chunk_id": chunk.chunk_id,
                    "source_type": chunk.source_type,
                    "content_hash": chunk.content_hash
                }
            })

    def query(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        if self._collection is not None:
            try:
                results = self._collection.query(
                    query_embeddings=[query_embedding],
                    n_results=top_k
                )
                formatted = []
                if results and "documents" in results and results["documents"]:
                    docs = results["documents"][0]
                    metas = results["metadatas"][0]
                    distances = results.get("distances", [[]])[0] if "distances" in results else [0.1] * len(docs)
                    ids = results["ids"][0]

                    for doc, meta, dist, cid in zip(docs, metas, distances, ids):
                        score = round(max(0.0, 1.0 - (dist if dist is not None else 0.5)), 4)
                        formatted.append({
                            "chunk_id": cid,
                            "text": doc,
                            "metadata": meta,
                            "score": score
                        })
                return formatted
            except Exception:
                pass

        scored_items = []
        for item in self._fallback_store:
            score = self._cosine_similarity(query_embedding, item["embedding"])
            scored_items.append({
                "chunk_id": item["chunk_id"],
                "text": item["text"],
                "metadata": item["metadata"],
                "score": round(score, 4)
            })

        scored_items.sort(key=lambda x: x["score"], reverse=True)
        return scored_items[:top_k]

    def reset(self) -> None:
        self._fallback_store.clear()
        if self._chroma_client is not None:
            try:
                self._chroma_client.delete_collection(name=self.collection_name)
            except Exception:
                pass
            try:
                self._collection = self._chroma_client.get_or_create_collection(
                    name=self.collection_name,
                    metadata={"hnsw:space": "cosine"}
                )
            except Exception:
                self._init_chroma()

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0
        dot = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot / (norm1 * norm2)
