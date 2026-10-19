"""
Audit trail schemas conforming to MASTER/04_DATA_SCHEMAS.md.
"""

from typing import Any, Literal
from pydantic import BaseModel, Field

EventType = Literal["task", "model_call", "tool_call", "file_access", "network", "security", "artifact"]
ActorType = Literal["user", "agent", "system"]
StatusType = Literal["success", "failure", "denied"]


class AuditEvent(BaseModel):
    event_id: str = Field(..., description="Canonical audit event ID e.g. AUD-001")
    timestamp: str = Field(..., description="ISO-8601 timestamp")
    event_type: EventType
    actor: ActorType
    component: str = Field(..., description="Subsystem component that emitted the event")
    status: StatusType
    metadata: dict[str, Any] = Field(default_factory=dict, description="Safe event metadata without secrets/payloads")


class AuditResponse(BaseModel):
    events: list[AuditEvent] = Field(default_factory=list)
