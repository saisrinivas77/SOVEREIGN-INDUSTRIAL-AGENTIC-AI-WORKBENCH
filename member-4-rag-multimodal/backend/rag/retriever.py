"""
Local Retriever for SIH26117 Member 4.
Returns canonical Source objects matching MASTER/04_DATA_SCHEMAS.md.
Handles default top_k=5 and empty retrieval / no-evidence states.
"""

from typing import List, Optional

try:
    from backend.rag.schemas import Source, RetrievalResult
    from backend.rag.embeddings import EmbeddingAdapter, LocalDeterministicEmbeddingAdapter
    from backend.rag.vector_store import LocalVectorStore
except ImportError:
    from .schemas import Source, RetrievalResult
    from .embeddings import EmbeddingAdapter, LocalDeterministicEmbeddingAdapter
    from .vector_store import LocalVectorStore

class LocalRetriever:
    """
    Local retriever fetching evidence chunks from local vector store
    and returning canonical Source objects with citations and grounding status.
    """

    def __init__(self, vector_store: Optional[LocalVectorStore] = None, embedding_adapter: Optional[EmbeddingAdapter] = None):
        self.vector_store = vector_store or LocalVectorStore()
        self.embedding_adapter = embedding_adapter or LocalDeterministicEmbeddingAdapter()

    def retrieve(self, query: str, top_k: int = 5, min_score_threshold: float = 0.20) -> RetrievalResult:
        if not query or not query.strip():
            return RetrievalResult(
                query=query,
                top_k=top_k,
                sources=[],
                has_evidence=False,
                grounding_status="INSUFFICIENT EVIDENCE",
                metadata={"reason": "Empty query"}
            )

        query_vector = self.embedding_adapter.embed_query(query)
        raw_matches = self.vector_store.query(query_vector, top_k=top_k)

        sources: List[Source] = []
        for match in raw_matches:
            meta = match.get("metadata", {})
            score = match.get("score", 0.0)

            if score < min_score_threshold:
                continue

            sources.append(Source(
                document_id=meta.get("document_id", "DOC-001"),
                filename=meta.get("filename", "unknown.pdf"),
                page=int(meta.get("page", 1)),
                section=meta.get("section", "General"),
                chunk_id=match.get("chunk_id", "chunk-0"),
                score=score,
                text=match.get("text", "")
            ))

        has_evidence = len(sources) > 0
        grounding_status = "SUPPORTED FACT" if has_evidence else "INSUFFICIENT EVIDENCE"

        return RetrievalResult(
            query=query,
            top_k=top_k,
            sources=sources,
            has_evidence=has_evidence,
            grounding_status=grounding_status,
            metadata={
                "returned_count": len(sources),
                "top_score": sources[0].score if sources else 0.0
            }
        )
