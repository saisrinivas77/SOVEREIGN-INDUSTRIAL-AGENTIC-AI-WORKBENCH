"""
Sovereign Tool Registry.
Enforces the mandatory execution pipeline:
Agent -> ToolRegistry -> Security Validation -> Tool -> Result.
Disallows arbitrary or unregistered tool execution; fails closed on unknown tools.
"""

import time
from typing import Any, Dict, List, Optional

try:
    from backend.tools.base import BaseTool, ToolResult
    from backend.tools.read_file import ReadFileTool
    from backend.tools.search_knowledge import SearchKnowledgeTool
    from backend.tools.analyze_image import AnalyzeImageTool
    from backend.tools.run_python import RunPythonTool
    from backend.tools.create_docx import CreateDocxTool
    from backend.tools.create_xlsx import CreateXlsxTool
    from backend.tools.create_pdf import CreatePdfTool
    from backend.tools.calculator import CalculatorTool
    from backend.security.security_manager import security_manager
    from backend.security.network_guard import SecurityDenialError
    from infra.runtime_config import RuntimeConfig
except ImportError:
    import sys
    from pathlib import Path
    _pkg_root = Path(__file__).resolve().parent.parent.parent
    if str(_pkg_root) not in sys.path:
        sys.path.insert(0, str(_pkg_root))
    from backend.tools.base import BaseTool, ToolResult
    from backend.tools.read_file import ReadFileTool
    from backend.tools.search_knowledge import SearchKnowledgeTool
    from backend.tools.analyze_image import AnalyzeImageTool
    from backend.tools.run_python import RunPythonTool
    from backend.tools.create_docx import CreateDocxTool
    from backend.tools.create_xlsx import CreateXlsxTool
    from backend.tools.create_pdf import CreatePdfTool
    from backend.tools.calculator import CalculatorTool
    from backend.security.security_manager import security_manager
    from backend.security.network_guard import SecurityDenialError
    from infra.runtime_config import RuntimeConfig

class ToolRegistry:
    """
    Central registry and dispatcher for all authorized workbench tools.
    """

    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        self._register_default_tools()

    def _register_default_tools(self) -> None:
        """Register default sovereign tools."""
        self.register_tool(ReadFileTool())
        self.register_tool(SearchKnowledgeTool())
        self.register_tool(AnalyzeImageTool())
        self.register_tool(RunPythonTool())
        self.register_tool(CreateDocxTool())
        self.register_tool(CreateXlsxTool())
        self.register_tool(CreatePdfTool())
        self.register_tool(CalculatorTool())


    def register_tool(self, tool: BaseTool) -> None:
        """Register a validated tool instance."""
        self._tools[tool.name] = tool

    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        """Retrieve tool instance if registered."""
        return self._tools.get(tool_name)

    def list_tools(self) -> List[Dict[str, Any]]:
        """Return descriptions and input schemas for all registered tools."""
        return [
            {
                "name": t.name,
                "description": t.description,
                "input_schema": t.input_schema,
                "permission": t.permission,
                "timeout_seconds": t.timeout_seconds
            }
            for t in self._tools.values()
        ]

    def execute_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> ToolResult:
        """
        Secure execution dispatch pipeline:
        1. Check registry allowlist -> DENY if unknown.
        2. Security validation.
        3. Execution with timeout & exception boundary.
        4. Audit and telemetry tracking.
        5. Return canonical ToolResult.
        """
        start_time = time.time()
        task_id = context.get("task_id") if context else None
        arguments = arguments or {}

        # 1. Registry Allowlist Check (Fail Closed)
        tool = self._tools.get(tool_name)
        if not tool:
            reason = f"Unknown or unauthorized tool '{tool_name}'. Tool is not registered in Sovereign ToolRegistry."
            security_manager.record_security_denial(
                component="tool_registry",
                action="tool_execution",
                reason=reason,
                task_id=task_id
            )
            return ToolResult(
                success=False,
                status="denied",
                error=reason
            )

        # 2. Security Validation
        try:
            security_manager.validate_tool_invocation(tool_name, arguments, task_id=task_id)
        except SecurityDenialError as e:
            return ToolResult(
                success=False,
                status="denied",
                error=str(e)
            )
        except Exception as e:
            return ToolResult(
                success=False,
                status="denied",
                error=f"Security policy violation: {str(e)}"
            )

        # 3. Tool Execution
        try:
            res: ToolResult = tool.execute(arguments, context=context)
            duration_ms = int((time.time() - start_time) * 1000)

            # 4. Audit & Telemetry Tracking
            if res.success:
                security_manager.record_local_tool_invocation(tool_name, task_id=task_id, duration_ms=duration_ms)
            else:
                security_manager.audit_service.log_event(
                    event_type="tool_call",
                    actor="agent",
                    component="tool_registry",
                    status="failure" if res.status != "denied" else "denied",
                    metadata={"tool": tool_name, "error": res.error, "duration_ms": duration_ms},
                    task_id=task_id
                )

            return res

        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            err_msg = f"Unexpected error during tool '{tool_name}' execution: {str(e)}"
            security_manager.audit_service.log_event(
                event_type="tool_call",
                actor="agent",
                component="tool_registry",
                status="failure",
                metadata={"tool": tool_name, "error": err_msg, "duration_ms": duration_ms},
                task_id=task_id
            )
            return ToolResult(
                success=False,
                status="failed",
                error=err_msg
            )

# Global ToolRegistry instance
tool_registry = ToolRegistry()
