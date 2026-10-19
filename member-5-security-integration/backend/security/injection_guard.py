"""
Injection Guard & Untrusted Content Sanitizer.
Ensures document contents and retrieved RAG chunks are treated strictly as data,
detects adversarial injection patterns, and protects agent execution boundaries.
"""

import re
from typing import List, Tuple, Dict, Any

class InjectionGuard:
    """
    Guards against indirect prompt injections from untrusted uploaded documents and user queries.
    """

    INJECTION_PATTERNS = [
        r"(?i)ignore\s+(all\s+)?(?:previous\s+|prior\s+|above\s+|system\s+)+instructions",
        r"(?i)disregard\s+(the\s+)?(?:above\s+|previous\s+|system\s+)+rules",
        r"(?i)system\s+override",
        r"(?i)you\s+are\s+now\s+in\s+developer\s+mode",
        r"(?i)send\s+.*to\s+https?://",
        r"(?i)exfiltrate\s+to\s+",
        r"(?i)call\s+(an?\s+)?external\s+api",
        r"(?i)execute\s+shell\s+command",
        r"(?i)curl\s+https?://",
        r"(?i)wget\s+https?://",
        r"(?i)download\s+from\s+https?://",
        r"(?i)print\s+(the\s+)?\.env",
        r"(?i)read\s+(the\s+)?(ssh|id_rsa|passwd)",
    ]

    def __init__(self):
        self._compiled_patterns = [re.compile(p) for p in self.INJECTION_PATTERNS]

    def scan_for_injection(self, text: str) -> Tuple[bool, List[str]]:
        """
        Scan text for prompt injection signatures.
        Returns (has_injection: bool, detected_signatures: List[str]).
        """
        if not text or not isinstance(text, str):
            return False, []

        detected = []
        for pattern in self._compiled_patterns:
            matches = pattern.findall(text)
            if matches:
                detected.append(pattern.pattern)

        return (len(detected) > 0), detected

    def wrap_untrusted_content(self, text: str, source_label: str = "UNTRUSTED_DOCUMENT") -> str:
        """
        Encloses untrusted text inside sovereign XML/markdown boundary blocks
        to prevent LLM role confusion.
        """
        clean_text = text.replace("```", "'''")  # Prevent block breakout
        return f"\n<{source_label}>\n{clean_text}\n</{source_label}>\n"

    def sanitize_untrusted_context(self, context_str: str) -> str:
        """
        Sanitizes retrieved text before feeding into prompts.
        """
        if not context_str:
            return ""
        # Strip potential system prompt impersonations
        sanitized = re.sub(r"(?i)<system>", "&lt;system&gt;", context_str)
        sanitized = re.sub(r"(?i)</system>", "&lt;/system&gt;", sanitized)
        sanitized = re.sub(r"(?i)### System Instructions:", "### Document Content:", sanitized)
        return sanitized

# Global Singleton instance
injection_guard = InjectionGuard()
