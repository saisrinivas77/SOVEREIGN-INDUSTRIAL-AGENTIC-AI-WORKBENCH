"""
Structured Vision Output Schemas for SIH26117 Member 4.
"""

from dataclasses import dataclass, asdict, field
from typing import List, Dict, Any

@dataclass
class VisionAnalysisOutput:
    """
    Structured Output contract for Local Vision Analysis.
    Never claims damage if visual evidence is insufficient.
    """
    observations: List[str]
    objects_components: List[str]
    visible_abnormalities: List[str]
    confidence: float
    evidence_references: List[str]
    uncertainties: List[str]
    has_sufficient_evidence: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
