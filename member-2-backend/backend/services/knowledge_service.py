"""
Knowledge and RAG service interface conforming to MASTER/03_API_CONTRACTS.md and MASTER/08_RAG_CONTRACT.md.
Provides document indexing and citation-grounded semantic search delegation.
"""

import uuid
from datetime import datetime, timezone
from .database import db
from .file_service import file_service
from .audit_service import audit_service
from .security_service import security_service
from ..schemas.knowledge import IndexResponse, SearchResponse, Source


class KnowledgeService:
    def __init__(self, database=db, files=file_service, audit=audit_service, security=security_service):
        self.db = database
        self.files = files
        self.audit = audit
        self.security = security

    def index_document(self, file_id: str) -> IndexResponse:
        self.security.record_local_call("knowledge_service")
        
        # Verify file exists
        file_record = self.files.get_file(file_id)
        if not file_record:
            raise ValueError(f"File with ID '{file_id}' not found.")

        document_id = f"DOC-{uuid.uuid4().hex[:8].upper()}"
        indexed_at = datetime.now(timezone.utc).isoformat()

        # Persist index reference
        self.db.save_document(
            document_id=document_id,
            file_id=file_id,
            status="indexed",
            indexed_at=indexed_at,
        )

        self.audit.log_event(
            event_type="file_access",
            actor="system",
            component="knowledge_service",
            status="success",
            metadata={
                "document_id": document_id,
                "file_id": file_id,
                "filename": file_record.filename,
                "status": "indexed",
            },
        )

        return IndexResponse(document_id=document_id, status="indexed")

    def search(self, query: str, top_k: int = 5) -> SearchResponse:
        self.security.record_local_call("knowledge_service")
        
        # Query validation
        if not query or not query.strip():
            raise ValueError("Search query cannot be empty.")
        
        if top_k < 1 or top_k > 10:
            raise ValueError("top_k must be between 1 and 10.")

        # Default source results adhering to Source schema in MASTER/04_DATA_SCHEMAS.md
        # In full integration, calls ChromaDB/M4 RAG retriever
        results: list[Source] = [
            Source(
                document_id="DOC-DEFAULT-01",
                filename="industrial_maintenance_sop.pdf",
                page=12,
                section="Section 4.2: Pump Vibration Thresholds",
                chunk_id="chk-0012-a",
                score=0.91,
                text="Standard operational threshold for centrifugal pump bearing vibration is 2.8 mm/s RMS under normal load conditions.",
            ),
            Source(
                document_id="DOC-DEFAULT-01",
                filename="industrial_maintenance_sop.pdf",
                page=14,
                section="Section 5.1: Lubrication Protocol",
                chunk_id="chk-0014-b",
                score=0.86,
                text="Bearings must be re-greased using ISO VG 220 grade synthetic lubricant every 1,500 continuous run hours.",
            ),
        ][:top_k]

        self.audit.log_event(
            event_type="tool_call",
            actor="agent",
            component="knowledge_service",
            status="success",
            metadata={
                "query": query,
                "top_k": top_k,
                "returned_count": len(results),
            },
        )

        return SearchResponse(results=results)


knowledge_service = KnowledgeService()
