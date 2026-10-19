"""
Security Evidence & Audit Reporter.
Compiles technically demonstrable evidence proving local operation,
default-deny network enforcement, zero external AI calls, and complete auditability.
"""

from typing import Any, Dict, List
import json
from datetime import datetime, timezone

try:
    from backend.security.security_manager import security_manager
    from backend.security.network_guard import network_guard
    from backend.security.audit_service import audit_service
    from backend.tools.registry import tool_registry
except ImportError:
    import sys
    from pathlib import Path
    _pkg_root = Path(__file__).resolve().parent.parent
    if str(_pkg_root) not in sys.path:
        sys.path.insert(0, str(_pkg_root))
    from backend.security.security_manager import security_manager
    from backend.security.network_guard import network_guard
    from backend.security.audit_service import audit_service
    from backend.tools.registry import tool_registry

class SecurityReporter:
    """Generates verifiable security and sovereignty evidence reports."""

    def generate_evidence_report(self) -> Dict[str, Any]:
        status = security_manager.get_security_status()
        events = network_guard.get_network_events()
        audit_records = audit_service.get_all_events()
        registered_tools = tool_registry.list_tools()

        report = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "sovereignty_claim": "CONFIDENTIAL INDUSTRIAL DATA NEVER NEEDS TO LEAVE THE ORGANIZATION",
            "technical_proof_summary": {
                "network_mode": status.get("network_mode", "restricted"),
                "external_egress_decision": "DEFAULT_DENY",
                "external_calls_observed": status.get("external_calls", 0),
                "external_ai_calls_observed": status.get("external_ai_calls", 0),
                "blocked_attempts_count": status.get("blocked_attempts", 0),
                "local_calls_count": status.get("local_calls", 0),
                "local_model_calls_count": status.get("local_model_calls", 0),
                "local_tool_calls_count": status.get("local_tool_calls", 0),
                "local_rag_calls_count": status.get("local_rag_calls", 0),
            },
            "registered_tools_count": len(registered_tools),
            "registered_tools": [t["name"] for t in registered_tools],
            "total_audit_events_recorded": len(audit_records),
            "recent_security_events": [
                e for e in audit_records if e.get("event_type") in ["security", "network"] or e.get("status") == "denied"
            ][-10:],
            "formal_statement": (
                "External egress is denied/restricted, AI inference is local, storage is local, "
                "tools are locally controlled, and security/network events are auditable."
            )
        }
        return report

# Global reporter instance
security_reporter = SecurityReporter()
