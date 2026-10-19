"""
Base Tool Contract & Canonical Data Models.
Conforms to MASTER/04_DATA_SCHEMAS.md and MASTER/07_TOOL_CONTRACT.md.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field
import hashlib
from pathlib import Path

class ToolResult(BaseModel):
    """Canonical tool result format returned by all registered tools."""
    success: bool
    result: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None
    status: Literal["completed", "failed", "denied"] = "completed"

class Source(BaseModel):
    """Canonical Source schema for RAG retrievals."""
    document_id: str
    filename: str
    page: int
    section: Optional[str] = "General"
    chunk_id: str
    score: float = 1.0
    text: str

class Artifact(BaseModel):
    """Canonical Artifact schema for verified outputs."""
    artifact_id: str
    filename: str
    type: Literal["docx", "xlsx", "code", "csv", "json", "pdf"]
    path: str
    sha256: str
    verified: bool = True

def compute_file_sha256(file_path: Path) -> str:
    """Computes SHA-256 hash of a file on disk."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()

class BaseTool(ABC):
    """
    Abstract base class for all Sovereign AI Workbench tools.
    """
    name: str
    description: str
    input_schema: Dict[str, Any]
    permission: str = "standard"
    timeout_seconds: int = 60

    @abstractmethod
    def execute(self, arguments: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> ToolResult:
        """Execute the tool with validated arguments."""
        pass
