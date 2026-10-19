"""
Model registry and routing schemas conforming to MASTER/04_DATA_SCHEMAS.md and MASTER/05_MODEL_CONTRACT.md.
"""

from typing import Literal
from pydantic import BaseModel, Field
from .task import TaskType


class ModelInfo(BaseModel):
    model_id: str = Field(..., description="Unique model identifier")
    capabilities: list[Literal["reasoning", "coding", "vision", "general"]] = Field(default_factory=list)
    context_limit: int = Field(default=4096, description="Context token window")
    vision_support: bool = Field(default=False)
    structured_output_support: bool = Field(default=True)
    available: bool = Field(default=True)
    health: str = Field(default="ready")


class ModelListResponse(BaseModel):
    models: list[ModelInfo] = Field(default_factory=list)


class ModelSelection(BaseModel):
    task_type: TaskType
    capability: Literal["reasoning", "coding", "vision"]
    model_id: str
    reason: str
    confidence: float = Field(ge=0.0, le=1.0)
