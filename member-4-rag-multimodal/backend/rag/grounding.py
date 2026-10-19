"""
Grounding Engine & Prompt Injection Defense for SIH26117 Member 4.
Evaluates grounding state (SUPPORTED FACT vs INFERENCE vs INSUFFICIENT EVIDENCE).
Sanitizes untrusted document payloads against prompt injection attacks.
"""

import re
from typing import List, Dict, Any, Tuple

try:
    from backend.rag.schemas import Source, RetrievalResult
except ImportError:
    from .schemas import Source, RetrievalResult

class GroundingEngine:
    """
    Validates factual grounding and provides anti-prompt-injection sanitization for RAG context.
    """

    INJECTION_PATTERNS = [
        r"(?i)ignore\s+(all\s+)?(previous|system)\s+instructions?",
        r"(?i)disregard\s+(all\s+)?(prior|system)\s+rules?",
        r"(?i)you\s+are\s+now\s+a",
        r"(?i)system\s*:\s*",
        r"(?i)override\s+security",
        r"(?i)call_tool\(",
        r"(?i)execute_code\(",
    ]

    def sanitize_evidence_text(self, text: str) -> str:
        sanitized = text
        for pattern in self.INJECTION_PATTERNS:
            sanitized = re.sub(pattern, "[DOCUMENT CONTENT REMOVED UNTRUSTED COMMAND]", sanitized)
        return sanitized

    def evaluate_grounding(self, retrieval_result: RetrievalResult) -> Tuple[str, List[str]]:
        if not retrieval_result.has_evidence or not retrieval_result.sources:
            return "INSUFFICIENT EVIDENCE", []

        citations = []
        for src in retrieval_result.sources:
            cit = f"[{src.filename}, Page {src.page}, Section {src.section}]"
            if cit not in citations:
                citations.append(cit)

        top_score = retrieval_result.sources[0].score if retrieval_result.sources else 0.0
        if top_score >= 0.50:
            return "SUPPORTED FACT", citations
        elif top_score >= 0.20:
            return "INFERENCE", citations
        else:
            return "INSUFFICIENT EVIDENCE", []

    def format_source_preserving_context(self, retrieval_result: RetrievalResult) -> str:
        if not retrieval_result.has_evidence or not retrieval_result.sources:
            return "=== EVIDENCE CONTEXT ===\nStatus: INSUFFICIENT EVIDENCE\nNo relevant document evidence retrieved."

        lines = ["=== EVIDENCE CONTEXT ===", f"Grounding Status: {retrieval_result.grounding_status}\n"]

        for idx, src in enumerate(retrieval_result.sources, 1):
            safe_text = self.sanitize_evidence_text(src.text)
            lines.append(f"--- Evidence Source #{idx} ---")
            lines.append(f"Document ID : {src.document_id}")
            lines.append(f"Filename    : {src.filename}")
            lines.append(f"Page        : {src.page}")
            lines.append(f"Section     : {src.section}")
            lines.append(f"Chunk ID    : {src.chunk_id}")
            lines.append(f"Relevance   : {src.score:.2f}")
            lines.append(f"Text Content:\n{safe_text}\n")

        return "\n".join(lines)
