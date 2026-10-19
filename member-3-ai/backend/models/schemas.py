"""Canonical Data Schemas and Wire Formats for SIH26117 Workbench.

Conforms strictly to MASTER/04_DATA_SCHEMAS.md and MASTER/05_MODEL_CONTRACT.md.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional, Type, TypeVar, Union
from pydantic import BaseModel, ConfigDict, Field

TaskType = Literal["document", "coding", "vision", "general"]
CapabilityType = Literal["reasoning", "coding", "vision"]
TaskStatus = Literal["queued", "running", "completed", "failed"]
StepStatus = Literal["pending", "running", "completed", "failed"]
ToolStatus = Literal["completed", "failed", "denied"]
EventStatus = Literal["success", "failure", "denied"]
EventType = Literal["task", "model_call", "tool_call", "file_access", "network", "security", "artifact"]
ActorType = Literal["user", "agent", "system"]


def get_utc_timestamp() -> str:
    """Return ISO-8601 UTC timestamp."""
    return datetime.now(timezone.utc).isoformat()


# ==========================================
# CANONICAL WIRE FORMATS (MASTER/04)
# ==========================================

class Task(BaseModel):
    """Canonical Task schema."""
    model_config = ConfigDict(extra="ignore")

    task_id: str
    instruction: str
    file_ids: List[str] = Field(default_factory=list)
    task_type: TaskType
    status: TaskStatus = "queued"
    created_at: str = Field(default_factory=get_utc_timestamp)


class PlanStep(BaseModel):
    """Individual step inside an AgentPlan."""
    model_config = ConfigDict(extra="ignore")

    step_id: int
    action: str
    tool: Optional[str] = None
    expected_output: str


class AgentPlan(BaseModel):
    """Canonical AgentPlan schema."""
    model_config = ConfigDict(extra="ignore")

    task_id: str
    goal: str
    steps: List[PlanStep] = Field(default_factory=list)


class AgentStep(BaseModel):
    """Canonical AgentStep schema."""
    model_config = ConfigDict(extra="ignore")

    step_id: int
    action: str
    tool: Optional[str] = None
    status: StepStatus = "pending"
    started_at: str = Field(default_factory=get_utc_timestamp)
    finished_at: Optional[str] = None
    result: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None


class ModelSelection(BaseModel):
    """Canonical ModelSelection schema."""
    model_config = ConfigDict(extra="ignore")

    task_type: TaskType
    capability: CapabilityType
    model_id: str
    reason: str
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class ToolCall(BaseModel):
    """Canonical ToolCall schema."""
    model_config = ConfigDict(extra="ignore")

    call_id: str
    tool: str
    arguments: Dict[str, Any] = Field(default_factory=dict)
    status: ToolStatus = "completed"
    result: Dict[str, Any] = Field(default_factory=dict)
    duration_ms: int = 0


class Source(BaseModel):
    """Canonical Source metadata schema."""
    model_config = ConfigDict(extra="ignore")

    document_id: str
    filename: str
    page: Optional[int] = None
    section: Optional[str] = None
    chunk_id: str
    score: float = 0.0
    text: str


class Artifact(BaseModel):
    """Canonical Artifact schema."""
    model_config = ConfigDict(extra="ignore")

    artifact_id: str
    filename: str
    type: str
    path: str
    sha256: str
    verified: bool = False


class AuditEvent(BaseModel):
    """Canonical AuditEvent schema."""
    model_config = ConfigDict(extra="ignore")

    event_id: str
    timestamp: str = Field(default_factory=get_utc_timestamp)
    event_type: EventType
    actor: ActorType
    component: str
    status: EventStatus
    metadata: Dict[str, Any] = Field(default_factory=dict)


class VerificationResult(BaseModel):
    """Canonical VerificationResult schema."""
    model_config = ConfigDict(extra="ignore")

    verified: bool
    checks: Dict[str, bool] = Field(default_factory=dict)
    details: str = ""
    error: Optional[str] = None


# ==========================================
# MODEL ADAPTER SCHEMAS (MASTER/05)
# ==========================================

class ModelMessage(BaseModel):
    """Chat message for local model requests."""
    role: Literal["system", "user", "assistant"]
    content: str
    images: Optional[List[str]] = None  # Base64 encoded or file paths if supported locally


class ModelRequest(BaseModel):
    """Standard request to a ModelAdapter."""
    messages: List[ModelMessage]
    temperature: float = 0.1
    max_tokens: int = 2048
    system_prompt: Optional[str] = None
    model_id: Optional[str] = None


class ModelResponse(BaseModel):
    """Standard response from a ModelAdapter."""
    content: str
    model_id: str
    usage: Dict[str, int] = Field(default_factory=dict)
    finish_reason: str = "stop"
    latency_ms: int = 0


class HealthStatus(BaseModel):
    """Model health check response."""
    healthy: bool
    model_id: str
    backend: str
    latency_ms: float = 0.0
    error: Optional[str] = None


class ModelMetadata(BaseModel):
    """Metadata describing a model registered in ModelRegistry."""
    model_id: str
    capabilities: List[CapabilityType]
    context_limit: int = 8192
    vision_support: bool = False
    structured_output_support: bool = True
    available: bool = True
    health: Optional[HealthStatus] = None
