"""
Knowledge and RAG schemas conforming to MASTER/03_API_CONTRACTS.md and MASTER/04_DATA_SCHEMAS.md.
"""

from typing import Literal
from pydantic import BaseModel, Field


class IndexRequest(BaseModel):
    file_id: str = Field(..., description="Canonical file ID to index into RAG")


class IndexResponse(BaseModel):
    document_id: str = Field(..., description="Canonical document ID e.g. DOC-...")
    status: Literal["indexed"] = "indexed"


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000, description="Search query string")
    top_k: int = Field(default=5, ge=1, le=10, description="Top K results to retrieve (1..10)")


class Source(BaseModel):
    document_id: str = Field(..., description="Canonical document ID")
    filename: str = Field(..., description="Source document filename")
    page: int | None = Field(default=None, description="Page number where content is found")
    section: str | None = Field(default=None, description="Section heading or number")
    chunk_id: str = Field(..., description="Unique chunk identifier")
    score: float = Field(..., description="Retrieval similarity score")
    text: str = Field(..., description="Retrieved chunk text content")


class SearchResponse(BaseModel):
    results: list[Source] = Field(default_factory=list)
