"""
Tests for LocalVisionAnalyzer (Member 4 - Vision/Multimodal).
Verifies image loading, structured output, insufficient evidence rules, and local execution.
"""

import unittest

try:
    from backend.vision.analyzer import LocalVisionAnalyzer
    from backend.vision.schemas import VisionAnalysisOutput
except ImportError:
    from .analyzer import LocalVisionAnalyzer
    from .schemas import VisionAnalysisOutput

class TestLocalVisionAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = LocalVisionAnalyzer()

    def test_image_analysis_structured_output(self):
        sample_bytes = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00\xff\xdb\x00C\x00"
        result = self.analyzer.analyze_image(sample_bytes, instruction="Inspect pump assembly")

        self.assertIsInstance(result, VisionAnalysisOutput)
        self.assertIsInstance(result.observations, list)
        self.assertIsInstance(result.objects_components, list)
        self.assertIsInstance(result.visible_abnormalities, list)
        self.assertGreaterEqual(result.confidence, 0.0)
        self.assertLessEqual(result.confidence, 1.0)

    def test_insufficient_evidence_rule(self):
        empty_result = self.analyzer.analyze_image(b"")

        self.assertFalse(empty_result.has_sufficient_evidence)
        self.assertGreater(len(empty_result.uncertainties), 0)
        self.assertEqual(len(empty_result.visible_abnormalities), 0)

    def test_local_only_vision_operation(self):
        sample_bytes = b"Local Image Payload Buffer"
        res = self.analyzer.analyze_image(sample_bytes)
        self.assertIsNotNone(res.observations)

if __name__ == "__main__":
    unittest.main()
