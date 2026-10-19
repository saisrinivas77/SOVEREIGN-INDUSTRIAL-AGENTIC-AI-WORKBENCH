"""
Task and agent lifecycle schemas conforming to MASTER/04_DATA_SCHEMAS.md.
"""

from typing import Any, Literal
from pydantic import BaseModel, Field

TaskType = Literal["document", "coding", "vision", "general"]
TaskStatus = Literal["queued", "running", "completed", "failed"]
StepStatus = Literal["pending", "running", "completed", "failed"]


class TaskCreate(BaseModel):
    instruction: str = Field(..., min_length=1, max_length=5000, description="Task instruction from user")
    file_ids: list[str] = Field(default_factory=list, description="Associated file IDs")


class TaskCreateResponse(BaseModel):
    task_id: str
    status: Literal["queued"] = "queued"


class TaskRunResponse(BaseModel):
    task_id: str
    status: Literal["running"] = "running"


class AgentPlanStep(BaseModel):
    step_id: int
    action: str
    tool: str | None = None
    expected_output: str


class AgentPlan(BaseModel):
    task_id: str
    goal: str
    steps: list[AgentPlanStep] = Field(default_factory=list)


class AgentStep(BaseModel):
    step_id: int
    action: str
    tool: str | None = None
    status: StepStatus = "pending"
    started_at: str | None = None
    finished_at: str | None = None
    result: dict[str, Any] | None = None
    error: str | None = None


class Artifact(BaseModel):
    artifact_id: str
    filename: str
    type: str
    path: str
    sha256: str
    verified: bool = True


class TaskStatusResponse(BaseModel):
    task_id: str
    status: TaskStatus
    task_type: TaskType = "general"
    steps: list[AgentStep] = Field(default_factory=list)
    artifacts: list[Artifact] = Field(default_factory=list)
    error: str | None = None


class TaskRecord(BaseModel):
    task_id: str
    instruction: str
    file_ids: list[str] = Field(default_factory=list)
    task_type: TaskType = "general"
    status: TaskStatus = "queued"
    created_at: str
    updated_at: str
    plan: AgentPlan | None = None
    steps: list[AgentStep] = Field(default_factory=list)
    artifacts: list[Artifact] = Field(default_factory=list)
    error: str | None = None
