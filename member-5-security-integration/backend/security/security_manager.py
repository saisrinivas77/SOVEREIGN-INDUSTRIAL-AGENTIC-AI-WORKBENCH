"""
Central Security Manager.
Coordinates Path Validation, Default-Deny Network Guard, Audit Logging,
Injection Protection, and Real-Time Security Telemetry for the Sovereign AI Workbench.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    from backend.security.path_validator import path_validator, PathValidator, SecurityPathViolationError
    from backend.security.network_guard import network_guard, NetworkGuard, SecurityDenialError
    from backend.security.audit_service import audit_service, AuditService, AuditEvent
    from backend.security.injection_guard import injection_guard, InjectionGuard
    from infra.runtime_config import RuntimeConfig
except ImportError:
    import sys
    from pathlib import Path
    _pkg_root = Path(__file__).resolve().parent.parent.parent
    if str(_pkg_root) not in sys.path:
        sys.path.insert(0, str(_pkg_root))
    from backend.security.path_validator import path_validator, PathValidator, SecurityPathViolationError
    from backend.security.network_guard import network_guard, NetworkGuard, SecurityDenialError
    from backend.security.audit_service import audit_service, AuditService, AuditEvent
    from backend.security.injection_guard import injection_guard, InjectionGuard
    from infra.runtime_config import RuntimeConfig

class SecurityManager:
    """
    Unified Security Manager orchestrating sovereign enforcement across all layers.
    """

    def __init__(
        self,
        validator: Optional[PathValidator] = None,
        net_guard: Optional[NetworkGuard] = None,
        auditor: Optional[AuditService] = None,
        inj_guard: Optional[InjectionGuard] = None,
    ):
        self.path_validator = validator or path_validator
        self.network_guard = net_guard or network_guard
        self.audit_service = auditor or audit_service
        self.injection_guard = inj_guard or injection_guard

    def validate_file_access(self, file_id_or_path: str, action: str = "read", task_id: Optional[str] = None) -> Path:
        """
        Validate file access, ensuring path confinement and traversal prevention.
        Records file access audit event.
        """
        try:
            # First check raw string for traversal or host root escapes
            self.path_validator.validate_raw_path_string(file_id_or_path)

            # Check if it is a canonical file_id or existing path inside workspace
            if file_id_or_path.startswith("FILE-") or not (os_path := Path(file_id_or_path)).is_absolute():
                resolved_path = self.path_validator.resolve_file_id(file_id_or_path)
            else:
                # Absolute path provided: must be within approved roots
                resolved_path = self.path_validator.validate_path_confinement(os_path)

            self.audit_service.log_event(
                event_type="file_access",
                actor="agent",
                component="path_validator",
                status="success",
                metadata={
                    "file_id_or_path": file_id_or_path,
                    "action": action,
                    "resolved_name": resolved_path.name
                },
                task_id=task_id
            )
            return resolved_path

        except (SecurityPathViolationError, FileNotFoundError, PermissionError) as e:
            reason = str(e)
            self.audit_service.log_security_event(
                component="path_validator",
                action=f"file_{action}_attempt",
                status="denied",
                reason=reason,
                task_id=task_id,
                extra={"target": file_id_or_path}
            )
            raise

    def validate_tool_invocation(self, tool_name: str, arguments: Dict[str, Any], task_id: Optional[str] = None) -> None:
        """
        Validate tool call before execution against security policies.
        """
        # 1. Reject forbidden dangerous arguments
        if "expression" in arguments and isinstance(arguments["expression"], str):
            expr = arguments["expression"]
            if any(forbidden in expr for forbidden in ["import", "__import__", "eval", "exec", "open", "os.", "sys.", "subprocess"]):
                reason = f"Dangerous expression detected in calculator tool: {expr}"
                self.record_security_denial(
                    component="tool_security",
                    action=f"tool_call_{tool_name}",
                    reason=reason,
                    task_id=task_id
                )
                raise SecurityDenialError(reason)

        # 2. Check path arguments
        if "file_id" in arguments and isinstance(arguments["file_id"], str):
            try:
                self.path_validator.validate_raw_path_string(arguments["file_id"])
            except SecurityPathViolationError as e:
                self.record_security_denial(
                    component="tool_security",
                    action=f"tool_call_{tool_name}",
                    reason=str(e),
                    task_id=task_id
                )
                raise

    def validate_model_endpoint(self, endpoint_or_host: str, model_id: str) -> None:
        """
        Ensure model requests route exclusively to local sovereign runtime.
        Blocks external AI endpoints.
        """
        allowed, reason = self.network_guard.evaluate_destination(
            destination=endpoint_or_host,
            component="model_router"
        )
        if not allowed:
            self.audit_service.log_security_event(
                component="model_router",
                action="model_inference_routing",
                status="denied",
                reason=f"Blocked external model endpoint: {endpoint_or_host} for model {model_id}"
            )
            raise SecurityDenialError(f"External model routing blocked: {reason}")

    def record_local_model_invocation(self, model_id: str, task_id: Optional[str] = None) -> None:
        """Track verified local model execution and log audit event."""
        self.network_guard.record_local_model_call(model_id, component="model_router")
        self.audit_service.log_event(
            event_type="model_call",
            actor="agent",
            component="model_adapter",
            status="success",
            metadata={"model_id": model_id, "runtime": "local_sovereign"},
            task_id=task_id
        )

    def record_local_tool_invocation(self, tool_name: str, task_id: Optional[str] = None, duration_ms: int = 0) -> None:
        """Track verified local tool execution and log audit event."""
        self.network_guard.record_local_tool_call(tool_name, component="tool_registry")
        self.audit_service.log_event(
            event_type="tool_call",
            actor="agent",
            component="tool_registry",
            status="success",
            metadata={"tool": tool_name, "duration_ms": duration_ms},
            task_id=task_id
        )

    def record_local_rag_invocation(self, query: str, task_id: Optional[str] = None) -> None:
        """Track verified local RAG retrieval."""
        self.network_guard.record_local_rag_call(query, component="rag")
        self.audit_service.log_event(
            event_type="tool_call",
            actor="agent",
            component="rag_retriever",
            status="success",
            metadata={"action": "local_vector_search", "query_len": len(query)},
            task_id=task_id
        )

    def record_artifact_creation(
        self,
        artifact_id: str,
        filename: str,
        path_str: str,
        sha256: str,
        verified: bool,
        task_id: Optional[str] = None
    ) -> None:
        """Track artifact generation and verification."""
        self.audit_service.log_event(
            event_type="artifact",
            actor="system",
            component="artifact_engine",
            status="success" if verified else "failure",
            metadata={
                "artifact_id": artifact_id,
                "filename": filename,
                "path": path_str,
                "sha256": sha256,
                "verified": verified
            },
            task_id=task_id
        )

    def record_security_denial(self, component: str, action: str, reason: str, task_id: Optional[str] = None) -> None:
        """Record and audit a security policy denial."""
        self.audit_service.log_security_event(
            component=component,
            action=action,
            status="denied",
            reason=reason,
            task_id=task_id
        )

    def get_security_status(self) -> Dict[str, Any]:
        """
        Expose live security status telemetry conforming to:
        GET /api/v1/security/status
        """
        return self.network_guard.get_security_status()

# Global Singleton instance
security_manager = SecurityManager()
