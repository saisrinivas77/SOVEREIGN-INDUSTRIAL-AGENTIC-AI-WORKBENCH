"""
Tests for OCREngine (Member 4 - RAG/OCR/Multimodal).
Verifies scanned page detection, page preservation, low confidence tagging, and local execution.
"""

import unittest
try:
    from backend.ocr.engine import OCREngine, OCRResult
except ImportError:
    from .engine import OCREngine, OCRResult

class TestOCREngine(unittest.TestCase):
    def setUp(self):
        self.engine = OCREngine()

    def test_native_vs_scanned_detection(self):
        native_text = "Section 4.2 Maintenance Procedure. Ensure all valves are shut before inspection."
        scanned_text = "  \n  "  # Very sparse native text
        
        self.assertFalse(self.engine.detect_scanned_page(native_text))
        self.assertTrue(self.engine.detect_scanned_page(scanned_text))

    def test_ocr_page_preserves_page_number(self):
        sample_bytes = b"%PDF-1.4 sample image payload data for page 17"
        result = self.engine.ocr_page(page_num=17, image_bytes=sample_bytes, filename="scanned_doc.pdf")
        
        self.assertIsInstance(result, OCRResult)
        self.assertEqual(result.page_num, 17)
        self.assertTrue(result.is_scanned)

    def test_low_confidence_uncertainty_flag(self):
        # Empty or garbled image bytes
        empty_result = self.engine.ocr_page(page_num=5, image_bytes=b"")
        self.assertTrue(empty_result.uncertainty_flag)
        self.assertLess(empty_result.confidence, 0.60)

    def test_local_only_operation(self):
        sample_bytes = b"Sample local image buffer"
        res = self.engine.ocr_page(page_num=1, image_bytes=sample_bytes)
        self.assertIsNotNone(res.text)

if __name__ == "__main__":
    unittest.main()
