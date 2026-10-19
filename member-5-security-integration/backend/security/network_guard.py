"""
Network Guard & Default-Deny Egress Enforcement.
Controls outbound network requests, detects and blocks forbidden external AI/telemetry endpoints,
intercepts runtime socket calls, and generates verifiable technical evidence.
"""

import socket
import urllib.parse
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set, Tuple, Any
import ipaddress

try:
    from infra.runtime_config import RuntimeConfig
except ImportError:
    import sys
    from pathlib import Path
    _pkg_root = Path(__file__).resolve().parent.parent.parent
    if str(_pkg_root) not in sys.path:
        sys.path.insert(0, str(_pkg_root))
    from infra.runtime_config import RuntimeConfig

class SecurityDenialError(PermissionError):
    """Raised when an action or network request violates sovereign security policy."""
    pass

class NetworkEvent:
    """Represents an auditable network decision event."""
    def __init__(
        self,
        destination: str,
        port: Optional[int],
        protocol: str,
        decision: str,  # "allowed" | "denied"
        component: str,
        reason: str,
        timestamp: Optional[str] = None
    ):
        self.timestamp = timestamp or datetime.now(timezone.utc).isoformat()
        self.destination = destination
        self.port = port
        self.protocol = protocol
        self.decision = decision
        self.component = component
        self.reason = reason

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "destination": self.destination,
            "port": self.port,
            "protocol": self.protocol,
            "decision": self.decision,
            "component": self.component,
            "reason": self.reason
        }

class NetworkGuard:
    """
    Sovereign Network Guard enforcing Default-Deny egress.
    Maintains real-time security telemetry and verifiable network event logs.
    """

    def __init__(self):
        self.network_mode: str = RuntimeConfig.NETWORK_MODE
        self.approved_hosts: Set[str] = set(RuntimeConfig.APPROVED_LOCAL_HOSTS)
        self.approved_ports: Set[int] = set(RuntimeConfig.APPROVED_LOCAL_PORTS)
        self.forbidden_domains: Set[str] = set(RuntimeConfig.FORBIDDEN_EXTERNAL_DOMAINS)

        # Real-time Telemetry Counters (Never Hardcoded)
        self._external_calls_attempted: int = 0
        self._external_calls_allowed: int = 0
        self._external_ai_calls_allowed: int = 0
        self._blocked_ai_attempts: int = 0
        self._blocked_attempts: int = 0
        self._local_calls: int = 0
        self._local_model_calls: int = 0
        self._local_tool_calls: int = 0
        self._local_rag_calls: int = 0

        # Event History
        self._events: List[NetworkEvent] = []
        self._socket_guard_installed: bool = False
        self._orig_socket_connect = None

    def is_local_ip(self, host: str) -> bool:
        """Check if a host string resolves to a loopback or link-local address."""
        try:
            ip = ipaddress.ip_address(host)
            return ip.is_loopback or ip.is_link_local or ip.is_private
        except ValueError:
            return False

    def evaluate_destination(
        self,
        destination: str,
        port: Optional[int] = None,
        protocol: str = "tcp",
        component: str = "system"
    ) -> Tuple[bool, str]:
        """
        Evaluate if a destination is permitted under the sovereign default-deny policy.
        Returns (is_allowed: bool, reason: str).
        """
        dest_clean = destination.strip().lower()

        # Check if destination is a full URL
        if "://" in dest_clean:
            parsed = urllib.parse.urlparse(dest_clean)
            dest_clean = parsed.hostname or dest_clean
            if parsed.port and port is None:
                port = parsed.port
            protocol = parsed.scheme or protocol

        # Strip trailing port if present
        if ":" in dest_clean and not dest_clean.startswith("["):
            parts = dest_clean.split(":")
            dest_clean = parts[0]
            if len(parts) > 1 and port is None:
                try:
                    port = int(parts[1])
                except ValueError:
                    pass

        # 1. Check Explicit Forbidden AI / Cloud Providers
        for forbidden in self.forbidden_domains:
            if dest_clean == forbidden or dest_clean.endswith("." + forbidden):
                self._external_calls_attempted += 1
                self._blocked_ai_attempts += 1
                self._blocked_attempts += 1
                reason = f"Forbidden external AI / cloud endpoint: '{dest_clean}'"
                self._record_event(dest_clean, port, protocol, "denied", component, reason)
                return False, reason

        # 2. Check Approved Local Hosts
        is_approved_host = (
            dest_clean in self.approved_hosts
            or self.is_local_ip(dest_clean)
        )

        if not is_approved_host:
            self._external_calls_attempted += 1
            self._blocked_attempts += 1
            reason = f"External network egress forbidden to unapproved host: '{dest_clean}'"
            self._record_event(dest_clean, port, protocol, "denied", component, reason)
            return False, reason

        # 3. Check Port (if specified)
        if port is not None and self.approved_ports and port not in self.approved_ports:
            # Check if it's standard local loopback port
            if not self.is_local_ip(dest_clean) or port > 65535 or port < 1:
                self._blocked_attempts += 1
                reason = f"Port {port} not in approved local ports for '{dest_clean}'"
                self._record_event(dest_clean, port, protocol, "denied", component, reason)
                return False, reason

        # Allowed Local Endpoint
        self._local_calls += 1
        reason = f"Approved sovereign local destination: '{dest_clean}'"
        self._record_event(dest_clean, port, protocol, "allowed", component, reason)
        return True, reason

    def check_and_enforce(
        self,
        destination: str,
        port: Optional[int] = None,
        protocol: str = "tcp",
        component: str = "system"
    ) -> None:
        """
        Evaluate destination and raise SecurityDenialError if denied.
        """
        allowed, reason = self.evaluate_destination(destination, port, protocol, component)
        if not allowed:
            raise SecurityDenialError(f"[SOVEREIGN SECURITY ENFORCEMENT] {reason}")

    def record_local_model_call(self, model_id: str, component: str = "model_router") -> None:
        """Track verified local model inference call."""
        self._local_model_calls += 1
        self._local_calls += 1
        self._record_event(
            destination=f"local_model:{model_id}",
            port=11434,
            protocol="internal",
            decision="allowed",
            component=component,
            reason=f"Local model inference executed for {model_id}"
        )

    def record_local_tool_call(self, tool_name: str, component: str = "tool_registry") -> None:
        """Track verified local tool execution."""
        self._local_tool_calls += 1
        self._local_calls += 1
        self._record_event(
            destination=f"local_tool:{tool_name}",
            port=None,
            protocol="internal",
            decision="allowed",
            component=component,
            reason=f"Local tool executed: {tool_name}"
        )

    def record_local_rag_call(self, query_summary: str, component: str = "rag") -> None:
        """Track verified local RAG retrieval."""
        self._local_rag_calls += 1
        self._local_calls += 1
        self._record_event(
            destination="local_chromadb",
            port=8001,
            protocol="internal",
            decision="allowed",
            component=component,
            reason=f"Local RAG vector search executed"
        )

    def _record_event(
        self,
        destination: str,
        port: Optional[int],
        protocol: str,
        decision: str,
        component: str,
        reason: str
    ) -> NetworkEvent:
        event = NetworkEvent(
            destination=destination,
            port=port,
            protocol=protocol,
            decision=decision,
            component=component,
            reason=reason
        )
        self._events.append(event)
        return event

    def get_security_status(self) -> Dict[str, Any]:
        """
        Exposes dynamic, verifiable security metrics matching API contract:
        GET /api/v1/security/status
        """
        return {
            "network_mode": self.network_mode,
            "external_calls": self._external_calls_allowed,
            "external_ai_calls": self._external_ai_calls_allowed,
            "blocked_attempts": self._blocked_attempts,
            "blocked_ai_attempts": self._blocked_ai_attempts,
            "local_calls": self._local_calls,
            # Additive detailed breakdown
            "local_model_calls": self._local_model_calls,
            "local_tool_calls": self._local_tool_calls,
            "local_rag_calls": self._local_rag_calls,
        }

    def get_network_events(self) -> List[Dict[str, Any]]:
        """Return full history of network events for auditing."""
        return [e.to_dict() for e in self._events]

    def install_socket_guard(self) -> None:
        """
        Active runtime protection: Intercepts low-level socket connections
        to enforce default-deny egress for any Python library.
        """
        if self._socket_guard_installed:
            return

        self._orig_socket_connect = socket.socket.connect
        guard = self

        def guarded_connect(sock_self, address):
            # address can be (host, port) tuple for AF_INET
            if isinstance(address, tuple) and len(address) >= 2:
                host, port = address[0], address[1]
                allowed, reason = guard.evaluate_destination(
                    destination=str(host),
                    port=int(port),
                    protocol="socket",
                    component="socket_interceptor"
                )
                if not allowed:
                    raise SecurityDenialError(f"Egress blocked by Sovereign Network Guard: {reason}")
            return guard._orig_socket_connect(sock_self, address)

        socket.socket.connect = guarded_connect
        self._socket_guard_installed = True

    def uninstall_socket_guard(self) -> None:
        """Restore original socket connect implementation."""
        if self._socket_guard_installed and self._orig_socket_connect:
            socket.socket.connect = self._orig_socket_connect
            self._socket_guard_installed = False

# Global Singleton instance
network_guard = NetworkGuard()
