"""
Health check schemas conforming to MASTER/03_API_CONTRACTS.md.
"""

from typing import Any, Literal
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: Literal["healthy", "degraded"] = Field(..., description="Overall system health")
    services: dict[str, Any] = Field(default_factory=dict, description="Subsystem health statuses")
