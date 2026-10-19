"""
Read File Tool.
Reads file content strictly from the controlled workspace registry.
Rejects path traversals and absolute host paths.
"""

from pathlib import Path
from typing import Any, Dict, Optional
import mimetypes

try:
    from backend.tools.base import BaseTool, ToolResult
    from backend.security.security_manager import security_manager
    from backend.security.path_validator import path_validator, SecurityPathViolationError
except ImportError:
    import sys
    from pathlib import Path
    _pkg_root = Path(__file__).resolve().parent.parent.parent
    if str(_pkg_root) not in sys.path:
        sys.path.insert(0, str(_pkg_root))
    from backend.tools.base import BaseTool, ToolResult
    from backend.security.security_manager import security_manager
    from backend.security.path_validator import path_validator, SecurityPathViolationError

class ReadFileTool(BaseTool):
    name = "read_file"
    description = "Read the contents of a registered workspace file by its canonical file_id."
    input_schema = {
        "type": "object",
        "properties": {
            "file_id": {"type": "string", "description": "The unique canonical file ID (e.g. FILE-001)"}
        },
        "required": ["file_id"]
    }
    permission = "file:read"
    timeout_seconds = 30

    def execute(self, arguments: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> ToolResult:
        file_id = arguments.get("file_id")
        if not file_id:
            return ToolResult(
                success=False,
                status="failed",
                error="Missing required argument 'file_id'."
            )

        task_id = context.get("task_id") if context else None

        try:
            # Validate security & resolve path
            resolved_path = security_manager.validate_file_access(
                file_id_or_path=file_id,
                action="read",
                task_id=task_id
            )

            filename = path_validator.get_filename(file_id)
            mime_type, _ = mimetypes.guess_type(resolved_path.name)
            mime_type = mime_type or "application/octet-stream"

            # Attempt text read first
            is_text = mime_type.startswith("text/") or resolved_path.suffix.lower() in [".txt", ".csv", ".json", ".md", ".py", ".html", ".xml", ".log", ".yaml", ".yml"]

            if is_text:
                with open(resolved_path, "r", encoding="utf-8", errors="replace") as f:
                    content_str = f.read()
            else:
                content_str = f"[Binary file: {filename}, size: {resolved_path.stat().st_size} bytes, type: {mime_type}]"

            return ToolResult(
                success=True,
                status="completed",
                result={
                    "file_id": file_id,
                    "filename": filename,
                    "mime_type": mime_type,
                    "size_bytes": resolved_path.stat().st_size,
                    "content": content_str
                }
            )

        except SecurityPathViolationError as e:
            return ToolResult(
                success=False,
                status="denied",
                error=f"Security denial: {str(e)}"
            )
        except FileNotFoundError as e:
            return ToolResult(
                success=False,
                status="failed",
                error=f"File not found: {str(e)}"
            )
        except Exception as e:
            return ToolResult(
                success=False,
                status="failed",
                error=f"Error reading file: {str(e)}"
            )
