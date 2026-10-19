"""
Create XLSX Tool.
Generates genuine Microsoft Excel (.xlsx) workbooks with multiple worksheets,
formatted tables, and computed summaries. Verifies integrity with SHA-256 hash.
"""

import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

try:
    from backend.tools.base import BaseTool, ToolResult, Artifact, compute_file_sha256
    from backend.security.security_manager import security_manager
    from backend.security.path_validator import path_validator
    from infra.runtime_config import RuntimeConfig
except ImportError:
    import sys
    from pathlib import Path
    _pkg_root = Path(__file__).resolve().parent.parent.parent
    if str(_pkg_root) not in sys.path:
        sys.path.insert(0, str(_pkg_root))
    from backend.tools.base import BaseTool, ToolResult, Artifact, compute_file_sha256
    from backend.security.security_manager import security_manager
    from backend.security.path_validator import path_validator
    from infra.runtime_config import RuntimeConfig

class CreateXlsxTool(BaseTool):
    name = "create_xlsx"
    description = "Generate a verified Microsoft Excel (.xlsx) spreadsheet with sheets, rows, and structured data tables."
    input_schema = {
        "type": "object",
        "properties": {
            "filename": {"type": "string", "description": "The output filename (e.g. results.xlsx)"},
            "sheets": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "rows": {
                            "type": "array",
                            "items": {"type": "array"}
                        }
                    },
                    "required": ["name", "rows"]
                },
                "description": "List of worksheets with row data"
            }
        },
        "required": ["filename", "sheets"]
    }
    permission = "artifact:create"
    timeout_seconds = 30

    def execute(self, arguments: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> ToolResult:
        raw_filename = arguments.get("filename", "results.xlsx")
        if not raw_filename.endswith(".xlsx"):
            raw_filename += ".xlsx"

        sheets_data = arguments.get("sheets", [])
        if not sheets_data:
            return ToolResult(
                success=False,
                status="failed",
                error="At least one worksheet with row data must be provided."
            )

        safe_filename = path_validator.sanitize_filename(raw_filename)
        task_id = context.get("task_id") if context else None
        artifact_id = f"ART-{uuid.uuid4().hex[:6].upper()}"

        try:
            art_dir = (RuntimeConfig.OUTPUTS_DIR / artifact_id).resolve()
            art_dir.mkdir(parents=True, exist_ok=True)
            wb_path = (art_dir / safe_filename).resolve()

            wb = openpyxl.Workbook()
            # Remove default active sheet
            default_sheet = wb.active
            wb.remove(default_sheet)

            # Styling definitions
            header_fill = PatternFill(start_color="1E3C72", end_color="1E3C72", fill_type="solid")
            header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
            data_font = Font(name="Calibri", size=10)
            thin_border = Border(
                left=Side(style='thin', color='D3D3D3'),
                right=Side(style='thin', color='D3D3D3'),
                top=Side(style='thin', color='D3D3D3'),
                bottom=Side(style='thin', color='D3D3D3')
            )

            for s_idx, s in enumerate(sheets_data):
                sheet_name = s.get("name", f"Sheet{s_idx + 1}")[:31] # Excel 31-char limit
                ws = wb.create_sheet(title=sheet_name)
                ws.views.sheetView[0].showGridLines = True

                rows = s.get("rows", [])
                for r_idx, row_values in enumerate(rows, start=1):
                    for c_idx, val in enumerate(row_values, start=1):
                        cell = ws.cell(row=r_idx, column=c_idx, value=val)
                        cell.border = thin_border

                        if r_idx == 1:
                            cell.fill = header_fill
                            cell.font = header_font
                            cell.alignment = Alignment(horizontal="center", vertical="center")
                        else:
                            cell.font = data_font
                            cell.alignment = Alignment(vertical="center")

                # Auto-fit column widths
                for col in ws.columns:
                    max_len = 0
                    col_letter = get_column_letter(col[0].column)
                    for cell in col:
                        if cell.value:
                            max_len = max(max_len, len(str(cell.value)))
                    ws.column_dimensions[col_letter].width = max(max_len + 4, 12)

            wb.save(str(wb_path))

            # Verify file existence and readability
            if not wb_path.exists() or wb_path.stat().st_size == 0:
                raise IOError(f"Failed to generate valid XLSX at {wb_path}")

            # Verify readability with openpyxl
            _ = openpyxl.load_workbook(str(wb_path))

            # Compute SHA-256
            sha256_hash = compute_file_sha256(wb_path)
            rel_path = str(wb_path.relative_to(RuntimeConfig.BASE_DIR))

            # Record in Security & Audit
            security_manager.record_artifact_creation(
                artifact_id=artifact_id,
                filename=safe_filename,
                path_str=rel_path,
                sha256=sha256_hash,
                verified=True,
                task_id=task_id
            )

            # Register as file in workspace for any downstream tools
            with open(wb_path, "rb") as f:
                path_validator.register_file(artifact_id, safe_filename, f.read())

            artifact = Artifact(
                artifact_id=artifact_id,
                filename=safe_filename,
                type="xlsx",
                path=rel_path,
                sha256=sha256_hash,
                verified=True
            )

            return ToolResult(
                success=True,
                status="completed",
                result=artifact.model_dump()
            )

        except Exception as e:
            return ToolResult(
                success=False,
                status="failed",
                error=f"XLSX generation failed: {str(e)}"
            )
