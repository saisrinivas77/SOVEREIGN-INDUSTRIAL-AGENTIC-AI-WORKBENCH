"""
Run Python Tool (Sandboxed Execution).
Executes Python scripts in an isolated sandbox with no network access,
restricted files, strict timeouts, and automated output file extraction.
"""

from typing import Any, Dict, List, Optional
import uuid

try:
    from backend.tools.base import BaseTool, ToolResult, compute_file_sha256
    from backend.security.security_manager import security_manager
    from backend.security.path_validator import path_validator
    from sandbox.runner import sandbox_runner, SandboxResult
    from infra.runtime_config import RuntimeConfig
except ImportError:
    import sys
    from pathlib import Path
    _pkg_root = Path(__file__).resolve().parent.parent.parent
    if str(_pkg_root) not in sys.path:
        sys.path.insert(0, str(_pkg_root))
    from backend.tools.base import BaseTool, ToolResult, compute_file_sha256
    from backend.security.security_manager import security_manager
    from backend.security.path_validator import path_validator
    from sandbox.runner import sandbox_runner, SandboxResult
    from infra.runtime_config import RuntimeConfig

class RunPythonTool(BaseTool):
    name = "run_python"
    description = "Execute Python code in an isolated, network-disabled sandbox to analyze data, compute statistics, or generate output files."
    input_schema = {
        "type": "object",
        "properties": {
            "code": {"type": "string", "description": "The Python source code to execute"},
            "input_files": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Optional list of file IDs to stage into the sandbox workspace"
            }
        },
        "required": ["code"]
    }
    permission = "sandbox:execute"
    timeout_seconds = 30

    def execute(self, arguments: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> ToolResult:
        code = arguments.get("code")
        if not code or not isinstance(code, str):
            return ToolResult(
                success=False,
                status="failed",
                error="Missing or invalid required argument 'code'."
            )

        input_files = arguments.get("input_files") or []
        task_id = context.get("task_id") if context else None

        # Execute inside sandbox
        res: SandboxResult = sandbox_runner.run_code(
            code=code,
            input_files=input_files,
            task_id=task_id
        )

        if not res.success:
            return ToolResult(
                success=False,
                status="failed" if res.exit_code != -1 else "denied",
                error=res.error or res.stderr,
                result={
                    "stdout": res.stdout,
                    "stderr": res.stderr,
                    "exit_code": res.exit_code,
                    "execution_time_ms": res.execution_time_ms
                }
            )

        # Store generated output files into outputs directory and register as artifacts if appropriate
        generated_artifacts = []
        for filename, file_bytes in res.output_files.items():
            art_id = f"ART-{uuid.uuid4().hex[:6].upper()}"
            art_dir = RuntimeConfig.OUTPUTS_DIR / art_id
            art_dir.mkdir(parents=True, exist_ok=True)
            art_path = (art_dir / filename).resolve()
            with open(art_path, "wb") as f:
                f.write(file_bytes)

            file_hash = compute_file_sha256(art_path)
            security_manager.record_artifact_creation(
                artifact_id=art_id,
                filename=filename,
                path_str=str(art_path.relative_to(RuntimeConfig.BASE_DIR)),
                sha256=file_hash,
                verified=True,
                task_id=task_id
            )

            # Also register under file_id for subsequent tools if needed
            path_validator.register_file(art_id, filename, file_bytes)

            generated_artifacts.append({
                "artifact_id": art_id,
                "filename": filename,
                "path": str(art_path.relative_to(RuntimeConfig.BASE_DIR)),
                "sha256": file_hash,
                "verified": True
            })

        return ToolResult(
            success=True,
            status="completed",
            result={
                "stdout": res.stdout,
                "stderr": res.stderr,
                "exit_code": res.exit_code,
                "execution_time_ms": res.execution_time_ms,
                "output_artifacts": generated_artifacts
            }
        )
