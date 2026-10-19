"""
RAG module exports for Member 4.
"""

from .schemas import Chunk, Source, RetrievalResult
from .parser import DocumentParser, ParsedPage
from .chunker import DocumentChunker
from .embeddings import EmbeddingAdapter, SentenceTransformerAdapter, LocalDeterministicEmbeddingAdapter
from .vector_store import LocalVectorStore
from .retriever import LocalRetriever
from .grounding import GroundingEngine
from .pipeline import RAGMultimodalPipeline

__all__ = [
    "Chunk",
    "Source",
    "RetrievalResult",
    "DocumentParser",
    "ParsedPage",
    "DocumentChunker",
    "EmbeddingAdapter",
    "SentenceTransformerAdapter",
    "LocalDeterministicEmbeddingAdapter",
    "LocalVectorStore",
    "LocalRetriever",
    "GroundingEngine",
    "RAGMultimodalPipeline"
]
