"""Agent State Schema and Reducers.

Conforms strictly to MASTER/04_DATA_SCHEMAS.md and MASTER/06_AGENT_CONTRACT.md.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from ..models.schemas import (
    AgentPlan,
    AgentStep,
    Artifact,
    AuditEvent,
    ModelSelection,
    Source,
    TaskStatus,
    TaskType,
    ToolCall,
    VerificationResult,
    get_utc_timestamp,
)


class AgentState(BaseModel):
    """Complete canonical state representation for a running agent task."""
    model_config = ConfigDict(extra="ignore")

    task_id: str
    instruction: str
    file_ids: List[str] = Field(default_factory=list)
    task_type: TaskType = "general"
    status: TaskStatus = "queued"

    # Planning
    plan: Optional[AgentPlan] = None
    current_step_index: int = 0
    steps: List[AgentStep] = Field(default_factory=list)

    # Model Routing
    active_model_selection: Optional[ModelSelection] = None

    # Tool Execution & Observations
    tool_results: List[ToolCall] = Field(default_factory=list)
    sources: List[Source] = Field(default_factory=list)
    artifacts: List[Artifact] = Field(default_factory=list)
    verification_results: List[VerificationResult] = Field(default_factory=list)

    # Audit & Monitoring
    audit_events: List[AuditEvent] = Field(default_factory=list)
    execution_trace: List[str] = Field(default_factory=list)

    # Bounded Execution Tracking
    step_count: int = 0
    tool_retries: Dict[str, int] = Field(default_factory=dict)
    model_retries: Dict[str, int] = Field(default_factory=dict)
    error: Optional[str] = None

    # Timestamps
    created_at: str = Field(default_factory=get_utc_timestamp)
    updated_at: str = Field(default_factory=get_utc_timestamp)

    def log_trace(self, message: str) -> None:
        """Add entry to execution trace."""
        self.execution_trace.append(f"[{get_utc_timestamp()}] {message}")
        self.updated_at = get_utc_timestamp()

    def record_audit(
        self,
        event_type: str,
        actor: str,
        component: str,
        status: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AuditEvent:
        """Create and record canonical AuditEvent."""
        event_id = f"AUD-{len(self.audit_events) + 1:04d}"
        event = AuditEvent(
            event_id=event_id,
            timestamp=get_utc_timestamp(),
            event_type=event_type,  # type: ignore
            actor=actor,  # type: ignore
            component=component,
            status=status,  # type: ignore
            metadata=metadata or {}
        )
        self.audit_events.append(event)
        self.updated_at = get_utc_timestamp()
        return event
