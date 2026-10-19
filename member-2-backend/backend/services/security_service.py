"""
Security service conforming to MASTER/09_SECURITY_SOVEREIGNTY.md.
Tracks local sovereignty metrics, prevents path traversal, and logs security incidents.
"""

import urllib.parse
from typing import Any
from .database import db
from .audit_service import audit_service
from ..schemas.security import SecurityStatusResponse


class SecurityService:
    def __init__(self, database=db, audit=audit_service):
        self.db = database
        self.audit = audit

    def get_security_status(self) -> SecurityStatusResponse:
        metrics = self.db.get_security_metrics()
        return SecurityStatusResponse(
            network_mode=metrics.get("network_mode", "restricted"),
            external_calls=metrics.get("external_calls", 0),
            external_ai_calls=metrics.get("external_ai_calls", 0),
            blocked_attempts=metrics.get("blocked_attempts", 0),
            local_calls=metrics.get("local_calls", 0),
        )

    def record_local_call(self, component: str = "backend") -> None:
        self.db.increment_security_metric("local_calls", 1)

    def record_blocked_attempt(self, reason: str, metadata: dict[str, Any] | None = None) -> None:
        self.db.increment_security_metric("blocked_attempts", 1)
        meta = metadata.copy() if metadata else {}
        meta["reason"] = reason
        self.audit.log_event(
            event_type="security",
            actor="system",
            component="security_service",
            status="denied",
            metadata=meta,
        )

    def validate_safe_filename(self, filename: str) -> str:
        """
        Validates that a filename has no path traversal components (../, ..\\),
        absolute path indicators, URL-encoded bypasses, or dangerous characters.
        Returns the sanitized base filename or raises ValueError.
        """
        if not filename or not isinstance(filename, str):
            self.record_blocked_attempt("Empty or non-string filename provided")
            raise ValueError("Filename cannot be empty")

        # Decode URL-encoded sequences to catch %00, %2e%2e, etc.
        decoded = urllib.parse.unquote(filename)

        if "\x00" in filename or "\x00" in decoded or "%00" in filename.lower():
            self.record_blocked_attempt("Null byte injection detected in filename", {"raw_filename": filename})
            raise ValueError("Null bytes in filename are strictly forbidden")

        # Reject path separators and traversal patterns in raw and decoded strings
        for check_str in (filename, decoded):
            if "/" in check_str or "\\" in check_str or ".." in check_str:
                self.record_blocked_attempt("Path traversal sequence detected in filename", {"raw_filename": filename})
                raise ValueError("Path traversal sequences are strictly forbidden")

            # Check for absolute path markers (e.g. C:, /)
            if ":" in check_str or check_str.startswith("~"):
                self.record_blocked_attempt("Absolute path attempt detected in filename", {"raw_filename": filename})
                raise ValueError("Absolute paths are strictly forbidden")

        clean_name = filename.strip()
        if not clean_name:
            self.record_blocked_attempt("Blank filename provided after sanitization")
            raise ValueError("Invalid filename")

        return clean_name


security_service = SecurityService()
