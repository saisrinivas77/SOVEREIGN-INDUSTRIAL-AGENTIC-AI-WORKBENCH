from typing import Any, Literal
from pydantic import BaseModel, Field

TaskType = Literal["document", "coding", "vision", "general"]

class ModelSelection(BaseModel):
    task_type: TaskType
    capability: Literal["reasoning", "coding", "vision"]
    model_id: str
    reason: str
    confidence: float = Field(ge=0, le=1)

class AgentStep(BaseModel):
    step_id: int
    action: str
    tool: str | None
    status: Literal["pending", "running", "completed", "failed"]
    result: dict[str, Any] | None = None
    error: str | None = None
