"""
File management schemas conforming to MASTER/04_DATA_SCHEMAS.md.
"""

from pydantic import BaseModel, Field


class FileUploadResponse(BaseModel):
    file_id: str = Field(..., description="Canonical file ID e.g. FILE-...")
    filename: str = Field(..., description="Sanitized original filename")
    mime_type: str = Field(..., description="Validated MIME type")
    size: int = Field(..., ge=0, description="File size in bytes")


class FileRecord(BaseModel):
    file_id: str
    filename: str
    mime_type: str
    size: int
    sha256: str
    stored_path: str  # Internal workspace path, never exposed directly in public API
    uploaded_at: str
