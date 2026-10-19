"""
Canonical Data Schemas for RAG Engine (Member 4).
Strictly adheres to MASTER/04_DATA_SCHEMAS.md.
"""

from dataclasses import dataclass, asdict, field
from typing import List, Dict, Any, Optional

@dataclass
class Chunk:
    """
    Chunk contract: Every chunk MUST retain document identity and metadata.
    No anonymous chunks allowed.
    """
    document_id: str
    filename: str
    page: int
    section: str
    chunk_id: str
    source_type: str  # "native_pdf" | "scanned_pdf" | "text" | "table" | "image_ocr"
    content_hash: str  # SHA-256 hash of chunk text
    text: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class Source:
    """
    Canonical Source Object matching MASTER/04_DATA_SCHEMAS.md
    """
    document_id: str
    filename: str
    page: int
    section: str
    chunk_id: str
    score: float
    text: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class RetrievalResult:
    query: str
    top_k: int
    sources: List[Source]
    has_evidence: bool
    grounding_status: str  # "SUPPORTED FACT" | "INFERENCE" | "INSUFFICIENT EVIDENCE"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "top_k": self.top_k,
            "sources": [s.to_dict() for s in self.sources],
            "has_evidence": self.has_evidence,
            "grounding_status": self.grounding_status,
            "metadata": self.metadata
        }
