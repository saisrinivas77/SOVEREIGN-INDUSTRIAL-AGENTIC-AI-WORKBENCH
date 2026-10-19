"""
Audit Service & Structured Audit Trail Engine.
Records and indexes immutable audit events across tasks, tool calls, model calls,
file accesses, network events, and security denials without exposing confidential payloads.
"""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

try:
    from infra.runtime_config import RuntimeConfig
except ImportError:
    import sys
    from pathlib import Path
    _pkg_root = Path(__file__).resolve().parent.parent.parent
    if str(_pkg_root) not in sys.path:
        sys.path.insert(0, str(_pkg_root))
    from infra.runtime_config import RuntimeConfig

EventType = Literal["task", "model_call", "tool_call", "file_access", "network", "security", "artifact"]
ActorType = Literal["user", "agent", "system"]
StatusType = Literal["success", "failure", "denied"]

class AuditEvent:
    """Canonical AuditEvent conforming to MASTER/04_DATA_SCHEMAS.md."""

    def __init__(
        self,
        event_id: str,
        timestamp: str,
        event_type: EventType,
        actor: ActorType,
        component: str,
        status: StatusType,
        metadata: Dict[str, Any]
    ):
        self.event_id = event_id
        self.timestamp = timestamp
        self.event_type = event_type
        self.actor = actor
        self.component = component
        self.status = status
        self.metadata = metadata

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp,
            "event_type": self.event_type,
            "actor": self.actor,
            "component": self.component,
            "status": self.status,
            "metadata": self.metadata
        }

class AuditService:
    """
    Central sovereign audit engine.
    Appends events to JSONL log file and maintains in-memory lookup indexes.
    """

    def __init__(self, log_dir: Optional[Path] = None):
        self.log_dir = (log_dir or RuntimeConfig.AUDIT_LOG_DIR).resolve()
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / "audit_events.jsonl"

        self._counter: int = 0
        self._events: List[AuditEvent] = []
        self._task_index: Dict[str, List[AuditEvent]] = {}

    def log_event(
        self,
        event_type: EventType,
        actor: ActorType,
        component: str,
        status: StatusType,
        metadata: Optional[Dict[str, Any]] = None,
        task_id: Optional[str] = None
    ) -> AuditEvent:
        """
        Record a new structured audit event.
        Ensures confidential payloads and secrets are sanitized before persisting.
        """
        self._counter += 1
        event_id = f"AUD-{self._counter:04d}"
        timestamp = datetime.now(timezone.utc).isoformat()

        meta = self._sanitize_metadata(metadata or {})
        if task_id and "task_id" not in meta:
            meta["task_id"] = task_id

        event = AuditEvent(
            event_id=event_id,
            timestamp=timestamp,
            event_type=event_type,
            actor=actor,
            component=component,
            status=status,
            metadata=meta
        )

        self._events.append(event)

        # Index by task_id if present
        tid = meta.get("task_id") or task_id
        if tid:
            if tid not in self._task_index:
                self._task_index[tid] = []
            self._task_index[tid].append(event)

        # Persist to disk (append-only JSONL)
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(event.to_dict()) + "\n")
        except Exception:
            pass

        return event

    def log_security_event(
        self,
        component: str,
        action: str,
        status: StatusType,
        reason: str,
        task_id: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None
    ) -> AuditEvent:
        """Convenience method for logging security/network events and denials."""
        meta = {
            "action": action,
            "reason": reason
        }
        if extra:
            meta.update(extra)
        return self.log_event(
            event_type="security",
            actor="system",
            component=component,
            status=status,
            metadata=meta,
            task_id=task_id
        )

    def get_events_by_task_id(self, task_id: str) -> List[Dict[str, Any]]:
        """Return all events associated with a task_id."""
        events = self._task_index.get(task_id, [])
        return [e.to_dict() for e in events]

    def get_events_by_type(self, event_type: EventType) -> List[Dict[str, Any]]:
        """Filter audit events by event_type."""
        return [e.to_dict() for e in self._events if e.event_type == event_type]

    def get_all_events(self) -> List[Dict[str, Any]]:
        """Return all recorded audit events."""
        return [e.to_dict() for e in self._events]

    def _sanitize_metadata(self, meta: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitizes metadata to prevent storing raw confidential document text,
        passwords, or secret tokens in audit trails.
        """
        sanitized = {}
        for k, v in meta.items():
            key_lower = k.lower()
            if any(secret_kw in key_lower for secret_kw in ["secret", "token", "password", "key", "credential"]):
                sanitized[k] = "[REDACTED_SECRET]"
            elif key_lower in ["payload", "file_content", "raw_content", "document_text", "code"] and isinstance(v, str) and len(v) > 200:
                # Truncate content preview to prevent full document storage in audit
                sanitized[k] = f"[CONTENT_REDACTED_LEN_{len(v)}]"
            elif isinstance(v, dict):
                sanitized[k] = self._sanitize_metadata(v)
            else:
                sanitized[k] = v
        return sanitized

# Global Singleton instance
audit_service = AuditService()
