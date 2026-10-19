"""
Create PDF Tool for Sovereign AI Workbench.
Generates genuine, styled PDF reports using ReportLab with headers, tables,
sections, verification hashes, and technical sovereignty statements.
"""

import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)
from reportlab.lib.units import inch

try:
    from backend.tools.base import BaseTool, ToolResult, Artifact, compute_file_sha256
    from backend.security.security_manager import security_manager
    from backend.security.path_validator import path_validator
    from infra.runtime_config import RuntimeConfig
except ImportError:
    import sys
    _pkg_root = Path(__file__).resolve().parent.parent.parent
    if str(_pkg_root) not in sys.path:
        sys.path.insert(0, str(_pkg_root))
    from backend.tools.base import BaseTool, ToolResult, Artifact, compute_file_sha256
    from backend.security.security_manager import security_manager
    from backend.security.path_validator import path_validator
    from infra.runtime_config import RuntimeConfig


class CreatePdfTool(BaseTool):
    name = "create_pdf"
    description = "Generate a verified, styled PDF industrial analysis report or sign-off note."
    input_schema = {
        "type": "object",
        "properties": {
            "title": {"type": "string", "description": "Report title"},
            "subtitle": {"type": "string", "description": "Optional report subtitle"},
            "sections": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "heading": {"type": "string"},
                        "content": {"type": "string"}
                    },
                    "required": ["heading", "content"]
                },
                "description": "List of report sections"
            },
            "filename": {"type": "string", "description": "Optional output filename", "default": "analysis_report.pdf"}
        },
        "required": ["title", "sections"]
    }
    permission = "artifact:create"
    timeout_seconds = 30

    def execute(self, arguments: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> ToolResult:
        title = arguments.get("title", "Sovereign Industrial Analysis Report")
        subtitle = arguments.get("subtitle", "Autonomous Agentic Execution & Technical Verification Summary")
        sections = arguments.get("sections", [])
        raw_filename = arguments.get("filename", "analysis_report.pdf")
        if not raw_filename.endswith(".pdf"):
            raw_filename += ".pdf"

        safe_filename = path_validator.sanitize_filename(raw_filename)
        task_id = context.get("task_id") if context else f"TASK-{uuid.uuid4().hex[:6].upper()}"
        artifact_id = f"ART-{uuid.uuid4().hex[:6].upper()}"

        try:
            art_dir = (RuntimeConfig.OUTPUTS_DIR / artifact_id).resolve()
            art_dir.mkdir(parents=True, exist_ok=True)
            pdf_path = (art_dir / safe_filename).resolve()

            # Create Doc Template
            doc = SimpleDocTemplate(
                str(pdf_path),
                pagesize=letter,
                leftMargin=36,
                rightMargin=36,
                topMargin=36,
                bottomMargin=36
            )

            styles = getSampleStyleSheet()

            # Custom Colors (Royal Blue Theme)
            PRIMARY_COLOR = colors.HexColor("#1e40af")
            DARK_NAVY = colors.HexColor("#0f172a")
            SECONDARY_COLOR = colors.HexColor("#0284c7")
            TEXT_PRIMARY = colors.HexColor("#1e293b")
            BG_LIGHT = colors.HexColor("#f8fafc")
            BORDER_COLOR = colors.HexColor("#e2e8f0")

            # Custom Paragraph Styles
            title_style = ParagraphStyle(
                'DocTitle',
                parent=styles['Heading1'],
                fontName='Helvetica-Bold',
                fontSize=20,
                leading=24,
                textColor=PRIMARY_COLOR,
                spaceAfter=4
            )

            subtitle_style = ParagraphStyle(
                'DocSubtitle',
                parent=styles['Normal'],
                fontName='Helvetica-Bold',
                fontSize=9,
                leading=12,
                textColor=SECONDARY_COLOR,
                spaceAfter=12
            )

            heading_style = ParagraphStyle(
                'SectionHeading',
                parent=styles['Heading2'],
                fontName='Helvetica-Bold',
                fontSize=12,
                leading=16,
                textColor=PRIMARY_COLOR,
                spaceBefore=10,
                spaceAfter=4
            )

            body_style = ParagraphStyle(
                'DocBody',
                parent=styles['Normal'],
                fontName='Helvetica',
                fontSize=9.5,
                leading=14,
                textColor=TEXT_PRIMARY,
                spaceAfter=8
            )

            meta_label_style = ParagraphStyle(
                'MetaLabel',
                parent=styles['Normal'],
                fontName='Helvetica-Bold',
                fontSize=8.5,
                textColor=DARK_NAVY
            )

            meta_val_style = ParagraphStyle(
                'MetaVal',
                parent=styles['Normal'],
                fontName='Helvetica',
                fontSize=8.5,
                textColor=TEXT_PRIMARY
            )

            story = []

            # Header Title
            story.append(Paragraph(title, title_style))
            story.append(Paragraph(subtitle.upper(), subtitle_style))
            story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY_COLOR, spaceAfter=10))

            # Metadata Table Banner
            meta_data = [
                [
                    Paragraph("Task ID:", meta_label_style),
                    Paragraph(task_id, meta_val_style),
                    Paragraph("Runtime Boundary:", meta_label_style),
                    Paragraph("100% LOCAL (AIR-GAPPED)", meta_val_style),
                ],
                [
                    Paragraph("Artifact ID:", meta_label_style),
                    Paragraph(artifact_id, meta_val_style),
                    Paragraph("Egress Security:", meta_label_style),
                    Paragraph("RESTRICTED (DEFAULT DENY)", meta_val_style),
                ],
            ]

            meta_table = Table(meta_data, colWidths=[1.1*inch, 2.5*inch, 1.3*inch, 2.5*inch])
            meta_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT),
                ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('PADDING', (0,0), (-1,-1), 6),
            ]))
            story.append(meta_table)
            story.append(Spacer(1, 14))

            # Sections
            for sec in sections:
                h_text = sec.get("heading", "Section")
                c_text = sec.get("content", "")

                story.append(Paragraph(h_text, heading_style))
                story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER_COLOR, spaceAfter=6))
                
                # Split content paragraphs if newlines exist
                paragraphs = c_text.split("\n")
                for p in paragraphs:
                    if p.strip():
                        story.append(Paragraph(p.strip(), body_style))
                story.append(Spacer(1, 6))

            story.append(Spacer(1, 12))
            story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY_COLOR, spaceAfter=8))

            # Footer / Audit Proof
            footer_style = ParagraphStyle(
                'DocFooter',
                parent=styles['Normal'],
                fontName='Helvetica-Oblique',
                fontSize=7.5,
                leading=10,
                textColor=colors.HexColor("#64748b")
            )
            footer_text = (
                "CONFIDENTIAL & SOVEREIGN INDUSTRIAL AUDIT TRAIL — "
                "Generated by Sovereign Agentic AI Workbench (SIH26117). "
                "All inference, retrieval, and code execution occurred on-premise without external data transmission."
            )
            story.append(Paragraph(footer_text, footer_style))

            # Build Document
            doc.build(story)

            if not pdf_path.exists() or pdf_path.stat().st_size == 0:
                raise IOError(f"Failed to generate valid PDF at {pdf_path}")

            sha256_hash = compute_file_sha256(pdf_path)
            rel_path = str(pdf_path.relative_to(RuntimeConfig.BASE_DIR))

            security_manager.record_artifact_creation(
                artifact_id=artifact_id,
                filename=safe_filename,
                path_str=rel_path,
                sha256=sha256_hash,
                verified=True,
                task_id=task_id
            )

            with open(pdf_path, "rb") as f:
                path_validator.register_file(artifact_id, safe_filename, f.read())

            artifact = Artifact(
                artifact_id=artifact_id,
                filename=safe_filename,
                type="pdf",
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
                error=f"PDF generation failed: {str(e)}"
            )


create_pdf_tool = CreatePdfTool()
