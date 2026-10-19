"""
Local Document Parser for SIH26117 Member 4.
Parses native PDFs, scanned PDFs (via OCR), raw text, and tabular files.
Preserves page numbers, section headers, and document metadata.
"""

import os
import io
import re
from typing import List, Dict, Any, Optional

try:
    from backend.ocr.engine import OCREngine
except (ImportError, ValueError):
    try:
        from ocr.engine import OCREngine
    except (ImportError, ValueError):
        # pyrefly: ignore [missing-import]
        from ..ocr.engine import OCREngine

class ParsedPage:
    def __init__(self, page_num: int, text: str, source_type: str, section: str = "General", tables: Optional[List[str]] = None):
        self.page_num = page_num
        self.text = text
        self.source_type = source_type
        self.section = section
        self.tables = tables or []

class DocumentParser:
    """
    Parses documents locally, extracting text, pages, sections, tables, and metadata.
    Automatically routes scanned pages to OCREngine.
    """

    def __init__(self, ocr_engine: Optional[OCREngine] = None):
        self.ocr_engine = ocr_engine or OCREngine()

    def parse(self, file_path_or_bytes: Any, filename: str, document_id: str = "DOC-001") -> List[ParsedPage]:
        ext = os.path.splitext(filename)[1].lower()

        if isinstance(file_path_or_bytes, str):
            if os.path.exists(file_path_or_bytes):
                with open(file_path_or_bytes, "rb") as f:
                    content = f.read()
            else:
                content = file_path_or_bytes.encode('utf-8')
        elif isinstance(file_path_or_bytes, bytes):
            content = file_path_or_bytes
        else:
            raise ValueError("Unsupported input format for document parser")

        if ext == ".pdf":
            return self._parse_pdf(content, filename, document_id)
        elif ext in [".txt", ".md", ".log"]:
            return self._parse_text(content, filename, document_id)
        elif ext in [".csv", ".tsv"]:
            return self._parse_tabular(content, filename, document_id)
        else:
            return self._parse_text(content, filename, document_id)

    def _parse_pdf(self, content: bytes, filename: str, document_id: str) -> List[ParsedPage]:
        if not content.startswith(b"%PDF"):
            return self._parse_text(content, filename, document_id)

        parsed_pages = []

        try:
            import pypdf
            reader = pypdf.PdfReader(io.BytesIO(content))
            for idx, page in enumerate(reader.pages):
                page_num = idx + 1
                native_text = page.extract_text() or ""
                
                if self.ocr_engine.detect_scanned_page(native_text, content):
                    ocr_res = self.ocr_engine.ocr_page(page_num, content, filename)
                    parsed_pages.append(ParsedPage(
                        page_num=page_num,
                        text=ocr_res.text,
                        source_type="scanned_pdf",
                        section=self._extract_section_header(ocr_res.text)
                    ))
                else:
                    section = self._extract_section_header(native_text)
                    parsed_pages.append(ParsedPage(
                        page_num=page_num,
                        text=native_text.strip(),
                        source_type="native_pdf",
                        section=section
                    ))
            if parsed_pages:
                return parsed_pages
        except Exception:
            pass

        text_pages = self._extract_raw_pdf_text_streams(content)
        if not text_pages:
            ocr_res = self.ocr_engine.ocr_page(1, content, filename)
            return [ParsedPage(page_num=1, text=ocr_res.text, source_type="scanned_pdf", section="1.0")]

        for idx, ptext in enumerate(text_pages):
            page_num = idx + 1
            if self.ocr_engine.detect_scanned_page(ptext):
                ocr_res = self.ocr_engine.ocr_page(page_num, content, filename)
                parsed_pages.append(ParsedPage(
                    page_num=page_num,
                    text=ocr_res.text,
                    source_type="scanned_pdf",
                    section=self._extract_section_header(ocr_res.text)
                ))
            else:
                section = self._extract_section_header(ptext)
                parsed_pages.append(ParsedPage(
                    page_num=page_num,
                    text=ptext,
                    source_type="native_pdf",
                    section=section
                ))

        return parsed_pages

    def _parse_text(self, content: bytes, filename: str, document_id: str) -> List[ParsedPage]:
        text = content.decode('utf-8', errors='ignore')
        raw_pages = text.split('\f') if '\f' in text else [text[i:i+2500] for i in range(0, len(text), 2500)]
        if not raw_pages:
            raw_pages = [text]

        parsed = []
        for idx, page_text in enumerate(raw_pages):
            if not page_text.strip():
                continue
            section = self._extract_section_header(page_text)
            parsed.append(ParsedPage(
                page_num=idx + 1,
                text=page_text.strip(),
                source_type="text",
                section=section
            ))
        return parsed

    def _parse_tabular(self, content: bytes, filename: str, document_id: str) -> List[ParsedPage]:
        text = content.decode('utf-8', errors='ignore')
        lines = text.strip().splitlines()
        header = lines[0] if lines else ""
        table_summary = f"Table File: {filename}\nHeader: {header}\nTotal Rows: {len(lines)-1}"
        
        return [ParsedPage(
            page_num=1,
            text=text,
            source_type="table",
            section="Data Table",
            tables=[table_summary]
        )]

    def _extract_section_header(self, text: str) -> str:
        match = re.search(r'^(?:[0-9]+\.[0-9]*\s+[A-Z][A-Za-z0-9\s]{2,30}|Section\s+[0-9\.]+|[A-Z\s]{4,25}:)', text, re.MULTILINE)
        if match:
            return match.group(0).strip()
        return "1.0 Main Section"

    def _extract_raw_pdf_text_streams(self, content: bytes) -> List[str]:
        stream_matches = re.findall(rb'BT\s*(.*?)\s*ET', content, re.DOTALL)
        if not stream_matches:
            extracted = re.findall(rb'\(([^\)]+)\)', content)
            txt = " ".join([e.decode('latin1', errors='ignore') for e in extracted if len(e) > 2])
            return [txt] if txt else []

        page_texts = []
        current_text = []
        for match in stream_matches:
            strings = re.findall(rb'\((.*?)\)', match)
            if strings:
                block = " ".join([s.decode('latin1', errors='ignore') for s in strings if s])
                current_text.append(block)
                if len(" ".join(current_text)) > 1500:
                    page_texts.append(" ".join(current_text))
                    current_text = []

        if current_text:
            page_texts.append(" ".join(current_text))

        return page_texts
