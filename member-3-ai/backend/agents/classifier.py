"""Deterministic Task Classifier.

Conforms strictly to MASTER/01_MASTER_ARCHITECTURE.md, MASTER/05_MODEL_CONTRACT.md,
and MASTER/06_AGENT_CONTRACT.md.
Classifies tasks deterministically before optional LLM refinement.
"""

from typing import List, Optional
from ..models.schemas import CapabilityType, Task, TaskType

# Deterministic File and Keyword Rules
VISION_PATTERNS = [
    ".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".webp",
    "photo", "image", "p&id", "pid", "schematic", "visual", "diagram",
    "corrosion photo", "gauge reading", "defect photo", "crack", "flange photo"
]

CODING_PATTERNS = [
    ".csv", ".tsv", ".py", ".sql", ".json",
    "code", "python", "script", "csv", "data analysis", "pandas", "numpy",
    "calculate statistics", "run script", "dataframe", "sandbox", "tabular data"
]

DOCUMENT_PATTERNS = [
    ".pdf", ".docx", ".doc", ".txt", ".md",
    "report", "sop", "document", "approval", "maintenance", "procedure",
    "inspection report", "draft memo", "synthesize", "work order", "specification"
]


class TaskClassifier:
    """Classifies user instructions and file context into canonical TaskType and Capability."""

    @classmethod
    def classify(
        cls,
        instruction: str,
        file_ids: Optional[List[str]] = None,
        task: Optional[Task] = None
    ) -> tuple[TaskType, CapabilityType, str]:
        """Deterministic intent and capability classification."""
        inst = (task.instruction if task else instruction) or ""
        files = (task.file_ids if task else (file_ids or []))
        
        combined_text = (inst + " " + " ".join(files)).lower()

        # 1. Vision Check
        if any(p in combined_text for p in VISION_PATTERNS):
            return "vision", "vision", "Task classified as VISION: visual indicators or image files detected."

        # 2. Coding Check
        if any(p in combined_text for p in CODING_PATTERNS):
            return "coding", "coding", "Task classified as CODING: data/script indicators or tabular files detected."

        # 3. Document / Industrial Reasoning Check
        if any(p in combined_text for p in DOCUMENT_PATTERNS):
            return "document", "reasoning", "Task classified as DOCUMENT: industrial document/SOP indicators detected."

        # 4. Fallback General
        return "general", "reasoning", "Task classified as GENERAL: standard reasoning task."
