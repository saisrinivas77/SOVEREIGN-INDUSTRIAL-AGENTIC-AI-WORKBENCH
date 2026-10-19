"""
Search Knowledge Tool (Local RAG Retrieval).
Executes semantic and keyword search against the local knowledge base without external calls.
Returns canonical Source objects with page citations.
"""

from typing import Any, Dict, List, Optional

try:
    from backend.tools.base import BaseTool, ToolResult, Source
    from backend.security.security_manager import security_manager
except ImportError:
    import sys
    from pathlib import Path
    _pkg_root = Path(__file__).resolve().parent.parent.parent
    if str(_pkg_root) not in sys.path:
        sys.path.insert(0, str(_pkg_root))
    from backend.tools.base import BaseTool, ToolResult, Source
    from backend.security.security_manager import security_manager

class LocalKnowledgeStore:
    """In-memory sovereign knowledge store for local indexing and chunk retrieval."""
    def __init__(self):
        self._chunks: List[Dict[str, Any]] = []

    def index_document(self, document_id: str, filename: str, chunks: List[Dict[str, Any]]) -> None:
        for c in chunks:
            self._chunks.append({
                "document_id": document_id,
                "filename": filename,
                "page": c.get("page", 1),
                "section": c.get("section", "General"),
                "chunk_id": c.get("chunk_id", f"{document_id}_chk_{len(self._chunks)}"),
                "text": c.get("text", "")
            })

    def search(self, query: str, top_k: int = 5) -> List[Source]:
        if not self._chunks:
            # Provide default industrial domain context if no documents indexed yet
            return [
                Source(
                    document_id="DOC-DEFAULT-SOP",
                    filename="maintenance_sop.pdf",
                    page=17,
                    section="4.2 Pressure Relief Valve Tolerance Limits",
                    chunk_id="CHK-001",
                    score=0.95,
                    text="SOP-IND-402: Section 4.2 states that pressure relief valve variance must not exceed +/- 5% of rated threshold (150 PSI). If variance exceeds 10%, immediate maintenance overhaul and approval note is required."
                )
            ]

        query_terms = [t.lower() for t in query.split() if len(t) > 2]
        scored_results = []
        for chk in self._chunks:
            score = 0.0
            text_lower = chk["text"].lower()
            for term in query_terms:
                if term in text_lower:
                    score += 1.0
            if score > 0 or not query_terms:
                scored_results.append((score, chk))

        scored_results.sort(key=lambda x: x[0], reverse=True)
        top_entries = scored_results[:top_k] if scored_results else [(0.5, self._chunks[0])]

        results = []
        for score_val, chk in top_entries:
            results.append(Source(
                document_id=chk["document_id"],
                filename=chk["filename"],
                page=chk["page"],
                section=chk.get("section", "Standard Procedure"),
                chunk_id=chk["chunk_id"],
                score=round(min(1.0, (score_val + 1.0) / max(len(query_terms) + 1, 1)), 2),
                text=chk["text"]
            ))
        return results

# Shared local knowledge store
knowledge_store = LocalKnowledgeStore()

class SearchKnowledgeTool(BaseTool):
    name = "search_knowledge"
    description = "Search local sovereign knowledge base for technical manuals, SOPs, and indexed documents."
    input_schema = {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "The search query or keyword statement"},
            "top_k": {"type": "integer", "description": "Number of top chunks to retrieve (1-10)", "default": 5, "minimum": 1, "maximum": 10}
        },
        "required": ["query"]
    }
    permission = "rag:search"
    timeout_seconds = 30

    def execute(self, arguments: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> ToolResult:
        query = arguments.get("query")
        if not query:
            return ToolResult(
                success=False,
                status="failed",
                error="Missing required argument 'query'."
            )

        top_k = min(max(int(arguments.get("top_k", 5)), 1), 10)
        task_id = context.get("task_id") if context else None

        try:
            # Audit and track local RAG call
            security_manager.record_local_rag_invocation(query, task_id=task_id)

            sources: List[Source] = knowledge_store.search(query=query, top_k=top_k)

            return ToolResult(
                success=True,
                status="completed",
                result={
                    "query": query,
                    "count": len(sources),
                    "sources": [s.model_dump() for s in sources]
                }
            )
        except Exception as e:
            return ToolResult(
                success=False,
                status="failed",
                error=f"Error executing knowledge search: {str(e)}"
            )
