"""
Audit service for recording and retrieving audit trails conforming to MASTER/04_DATA_SCHEMAS.md.
"""

import uuid
from datetime import datetime, timezone
from typing import Any
from .database import db
from ..schemas.audit import AuditEvent, AuditResponse, EventType, ActorType, StatusType


class AuditService:
    def __init__(self, database=db):
        self.db = database

    def log_event(
        self,
        event_type: EventType,
        actor: ActorType,
        component: str,
        status: StatusType,
        metadata: dict[str, Any] | None = None,
        task_id: str | None = None,
    ) -> AuditEvent:
        event_id = f"AUD-{uuid.uuid4().hex[:8].upper()}"
        timestamp = datetime.now(timezone.utc).isoformat()
        clean_metadata = metadata.copy() if metadata else {}
        
        # Ensure confidential bodies or sensitive paths are sanitized
        if "password" in clean_metadata:
            clean_metadata["password"] = "[REDACTED]"
        if "secret" in clean_metadata:
            clean_metadata["secret"] = "[REDACTED]"

        self.db.save_audit_event(
            event_id=event_id,
            task_id=task_id,
            timestamp=timestamp,
            event_type=event_type,
            actor=actor,
            component=component,
            status=status,
            metadata=clean_metadata,
        )

        return AuditEvent(
            event_id=event_id,
            timestamp=timestamp,
            event_type=event_type,
            actor=actor,
            component=component,
            status=status,
            metadata=clean_metadata,
        )

    def get_task_events(self, task_id: str) -> AuditResponse:
        records = self.db.get_audit_events_for_task(task_id)
        events = [
            AuditEvent(
                event_id=r["event_id"],
                timestamp=r["timestamp"],
                event_type=r["event_type"],
                actor=r["actor"],
                component=r["component"],
                status=r["status"],
                metadata=r["metadata"],
            )
            for r in records
        ]
        return AuditResponse(events=events)


audit_service = AuditService()
