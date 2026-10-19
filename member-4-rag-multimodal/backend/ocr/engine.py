"""
Sovereign Local OCR Engine for SIH26117 Member 4 (RAG + Multimodal).
Operates 100% locally with zero cloud dependencies.
"""

import os
import io
import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class OCRResult:
    page_num: int
    text: str
    confidence: float
    is_scanned: bool
    uncertainty_flag: bool = False
    details: List[Dict[str, Any]] = field(default_factory=list)

class OCREngine:
    """
    Local OCR engine supporting native vs scanned PDF page detection,
    page preservation, confidence scoring, low-confidence uncertainty tagging,
    and fallback pure-python execution when Tesseract binary is unavailable.
    """

    def __init__(self, tesseract_cmd: Optional[str] = None):
        self.tesseract_cmd = tesseract_cmd
        self._pytesseract_available = False
        self._check_tesseract()

    def _check_tesseract(self):
        try:
            import pytesseract
            if self.tesseract_cmd:
                pytesseract.pytesseract.tesseract_cmd = self.tesseract_cmd
            self._pytesseract = pytesseract
            self._pytesseract_available = True
        except ImportError:
            self._pytesseract = None
            self._pytesseract_available = False

    def detect_scanned_page(self, page_text: str, image_bytes: Optional[bytes] = None) -> bool:
        """
        Detects if a PDF page is scanned based on extracted native text density.
        Pages with fewer than 30 readable non-whitespace characters are classified as scanned.
        """
        clean_text = re.sub(r'\s+', '', page_text or '')
        if len(clean_text) < 30:
            return True
        return False

    def ocr_page(self, page_num: int, image_bytes: bytes, filename: str = "") -> OCRResult:
        """
        Runs OCR on page image bytes. Returns structured OCRResult preserving page number.
        """
        if not image_bytes:
            return OCRResult(
                page_num=page_num,
                text="",
                confidence=0.0,
                is_scanned=True,
                uncertainty_flag=True,
                details=[{"error": "Empty image bytes"}]
            )

        # Attempt pytesseract if available
        if self._pytesseract_available:
            try:
                from PIL import Image
                img = Image.open(io.BytesIO(image_bytes))
                
                # Get detailed data including confidence
                data = self._pytesseract.image_to_data(img, output_type=self._pytesseract.Output.DICT)
                confidences = [float(c) for c in data.get('conf', []) if c != '-1' and c is not None]
                text_parts = [t for t in data.get('text', []) if t and t.strip()]
                
                extracted_text = " ".join(text_parts).strip()
                avg_confidence = (sum(confidences) / len(confidences) / 100.0) if confidences else 0.5
                
                uncertainty = avg_confidence < 0.60 or len(extracted_text) < 5
                final_text = extracted_text
                if uncertainty:
                    final_text = f"[LOW OCR CONFIDENCE (Page {page_num})] " + (extracted_text or "Unclear scanned content")

                return OCRResult(
                    page_num=page_num,
                    text=final_text,
                    confidence=round(avg_confidence, 2),
                    is_scanned=True,
                    uncertainty_flag=uncertainty,
                    details=[{"method": "pytesseract", "word_count": len(text_parts)}]
                )
            except Exception as e:
                # Fallback to local string extraction / deterministic fallback below
                pass

        # Pure-Python Local Fallback Engine (runs when pytesseract/Tesseract is unavailable)
        # Parses ASCII text strings embedded inside image payload or generates marked placeholder
        extracted_strings = re.findall(rb'[A-Za-z0-9\s.,;:\-\_\(\)]{4,}', image_bytes)
        fallback_text = " ".join([s.decode('ascii', errors='ignore').strip() for s in extracted_strings[:20]])
        fallback_text = re.sub(r'\s+', ' ', fallback_text).strip()

        if not fallback_text:
            fallback_text = f"[SCANNED PAGE {page_num}: OCR text extraction required]"
            avg_conf = 0.40
            uncertainty = True
        else:
            avg_conf = 0.55
            uncertainty = True
            fallback_text = f"[LOW OCR CONFIDENCE (Page {page_num})] {fallback_text}"

        return OCRResult(
            page_num=page_num,
            text=fallback_text,
            confidence=avg_conf,
            is_scanned=True,
            uncertainty_flag=uncertainty,
            details=[{"method": "local_fallback", "raw_strings_found": len(extracted_strings)}]
        )
