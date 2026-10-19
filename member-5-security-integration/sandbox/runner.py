"""
Isolated Python Sandbox Runner.
Executes code in a confined subprocess with zero network access, sanitized environment,
strict timeout bounds, and automated artifact extraction.
"""

import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from sandbox.policy import sandbox_policy, SandboxSecurityViolation
    from sandbox.environment import SandboxEnvironment
    from infra.runtime_config import RuntimeConfig
    from backend.security.audit_service import audit_service
except ImportError:
    import sys
    from pathlib import Path
    _pkg_root = Path(__file__).resolve().parent.parent
    if str(_pkg_root) not in sys.path:
        sys.path.insert(0, str(_pkg_root))
    from sandbox.policy import sandbox_policy, SandboxSecurityViolation
    from sandbox.environment import SandboxEnvironment
    from infra.runtime_config import RuntimeConfig
    from backend.security.audit_service import audit_service

class SandboxResult:
    """Represents the outcome of a sandboxed execution."""
    def __init__(
        self,
        success: bool,
        stdout: str,
        stderr: str,
        exit_code: int,
        output_files: Dict[str, bytes],
        execution_time_ms: int = 0,
        error: Optional[str] = None
    ):
        self.success = success
        self.stdout = stdout
        self.stderr = stderr
        self.exit_code = exit_code
        self.output_files = output_files
        self.execution_time_ms = execution_time_ms
        self.error = error

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "exit_code": self.exit_code,
            "output_files": list(self.output_files.keys()),
            "execution_time_ms": self.execution_time_ms,
            "error": self.error
        }

# Python runtime security preamble injected before execution to enforce network blocking at runtime
RUNTIME_PREAMBLE = """
# --- Sovereign Sandbox Security Guard Preamble ---
import sys

# Disallow network socket creation
def _block_socket(*args, **kwargs):
    raise PermissionError("[SOVEREIGN SANDBOX ERROR] Network access is strictly forbidden in the execution sandbox.")

try:
    import socket
    socket.socket = _block_socket
    socket.create_connection = _block_socket
    socket.getaddrinfo = _block_socket
except Exception:
    pass

# Strip sensitive environment variables inside child process
import os
for _k in list(os.environ.keys()):
    if any(_s in _k.upper() for _s in ["KEY", "SECRET", "TOKEN", "PASS", "AUTH", "CREDENTIAL", "SSH"]):
        del os.environ[_k]
# --- End Preamble ---
"""

class SandboxRunner:
    """
    Executes Python code in an isolated subprocess.
    """

    def __init__(self, timeout_seconds: Optional[int] = None):
        self.timeout = timeout_seconds or RuntimeConfig.SANDBOX_TIMEOUT_SECONDS

    def run_code(
        self,
        code: str,
        input_files: Optional[List[str]] = None,
        task_id: Optional[str] = None
    ) -> SandboxResult:
        """
        Executes code securely.
        1. Validates code against security policy.
        2. Sets up isolated ephemeral directory and copies input files.
        3. Runs Python subprocess with timeout and sanitized environment.
        4. Collects results and output files.
        """
        start_time = time.time()
        input_files = input_files or []

        # 1. Static Security Check
        try:
            sandbox_policy.validate_code_or_raise(code)
        except SandboxSecurityViolation as e:
            audit_service.log_security_event(
                component="sandbox",
                action="code_execution_blocked",
                status="denied",
                reason=str(e),
                task_id=task_id,
                extra={"code_len": len(code)}
            )
            return SandboxResult(
                success=False,
                stdout="",
                stderr=str(e),
                exit_code=-1,
                output_files={},
                execution_time_ms=int((time.time() - start_time) * 1000),
                error=str(e)
            )

        # 2. Ephemeral Sandbox Execution
        env_mgr = SandboxEnvironment()
        try:
            # Stage inputs
            env_mgr.stage_input_files(input_files)

            # Prepend security preamble to code
            full_code = RUNTIME_PREAMBLE + "\n" + code
            script_path = env_mgr.write_script(full_code)

            # Build clean environment with only essential system paths (no secrets or credentials)
            safe_env = {
                "PATH": os.environ.get("PATH", ""),
                "SYSTEMROOT": os.environ.get("SYSTEMROOT", "C:\\Windows"),
                "SYSTEMDRIVE": os.environ.get("SYSTEMDRIVE", "C:"),
                "WINDIR": os.environ.get("WINDIR", "C:\\Windows"),
                "TEMP": os.environ.get("TEMP", str(env_mgr.sandbox_dir)),
                "TMP": os.environ.get("TMP", str(env_mgr.sandbox_dir)),
                "PYTHONUNBUFFERED": "1",
                "PYTHONDONTWRITEBYTECODE": "1",
                "SOVEREIGN_SANDBOX": "1"
            }

            # 3. Launch Process
            cmd = [sys.executable, str(script_path)]
            try:
                proc = subprocess.run(
                    cmd,
                    cwd=str(env_mgr.sandbox_dir),
                    env=safe_env,
                    stdin=subprocess.DEVNULL,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout
                )
                duration_ms = int((time.time() - start_time) * 1000)
                output_files = env_mgr.collect_output_files()

                success = (proc.returncode == 0)
                error_msg = None if success else f"Process exited with return code {proc.returncode}"

                audit_service.log_event(
                    event_type="tool_call",
                    actor="agent",
                    component="sandbox_runner",
                    status="success" if success else "failure",
                    metadata={
                        "action": "run_python",
                        "exit_code": proc.returncode,
                        "duration_ms": duration_ms,
                        "output_files_count": len(output_files)
                    },
                    task_id=task_id
                )

                return SandboxResult(
                    success=success,
                    stdout=proc.stdout,
                    stderr=proc.stderr,
                    exit_code=proc.returncode,
                    output_files=output_files,
                    execution_time_ms=duration_ms,
                    error=error_msg
                )

            except subprocess.TimeoutExpired:
                duration_ms = int((time.time() - start_time) * 1000)
                err_msg = f"Sandbox execution timed out after {self.timeout} seconds."
                audit_service.log_event(
                    event_type="tool_call",
                    actor="agent",
                    component="sandbox_runner",
                    status="failure",
                    metadata={"action": "run_python", "error": "timeout", "duration_ms": duration_ms},
                    task_id=task_id
                )
                return SandboxResult(
                    success=False,
                    stdout="",
                    stderr=err_msg,
                    exit_code=-2,
                    output_files={},
                    execution_time_ms=duration_ms,
                    error=err_msg
                )

        finally:
            env_mgr.cleanup()

# Global Sandbox instance
sandbox_runner = SandboxRunner()
