"""
End-to-End RAG + Multimodal Pipeline for SIH26117 Member 4.
Coordinates ingestion, OCR, parsing, chunking, local embedding, ChromaDB indexing,
source-preserving retrieval, grounding evaluation, and vision analysis.
"""

import os
from typing import List, Dict, Any, Optional

try:
    from backend.ocr.engine import OCREngine
    from backend.rag.parser import DocumentParser
    from backend.rag.chunker import DocumentChunker
    from backend.rag.embeddings import EmbeddingAdapter, LocalDeterministicEmbeddingAdapter
    from backend.rag.vector_store import LocalVectorStore
    from backend.rag.retriever import LocalRetriever
    from backend.rag.grounding import GroundingEngine
    from backend.vision.analyzer import LocalVisionAnalyzer
    from backend.rag.schemas import RetrievalResult
except (ImportError, ValueError):
    try:
        from ocr.engine import OCREngine
        from rag.parser import DocumentParser
        from rag.chunker import DocumentChunker
        from rag.embeddings import EmbeddingAdapter, LocalDeterministicEmbeddingAdapter
        from rag.vector_store import LocalVectorStore
        from rag.retriever import LocalRetriever
        from rag.grounding import GroundingEngine
        from vision.analyzer import LocalVisionAnalyzer
        from rag.schemas import RetrievalResult
    except (ImportError, ValueError):
        from ..ocr.engine import OCREngine
        from .parser import DocumentParser
        from .chunker import DocumentChunker
        from .embeddings import EmbeddingAdapter, LocalDeterministicEmbeddingAdapter
        from .vector_store import LocalVectorStore
        from .retriever import LocalRetriever
        from .grounding import GroundingEngine
        from ..vision.analyzer import LocalVisionAnalyzer
        from .schemas import RetrievalResult

class RAGMultimodalPipeline:
    """
    Main entry point for local document RAG and multimodal image analysis.
    Operates 100% locally with zero cloud dependencies.
    """

    def __init__(
        self,
        ocr_engine: Optional[OCREngine] = None,
        embedding_adapter: Optional[EmbeddingAdapter] = None,
        vector_store: Optional[LocalVectorStore] = None,
        vision_analyzer: Optional[LocalVisionAnalyzer] = None
    ):
        self.ocr_engine = ocr_engine or OCREngine()
        self.parser = DocumentParser(ocr_engine=self.ocr_engine)
        self.chunker = DocumentChunker()
        self.embedding_adapter = embedding_adapter or LocalDeterministicEmbeddingAdapter()
        self.vector_store = vector_store or LocalVectorStore()
        self.retriever = LocalRetriever(vector_store=self.vector_store, embedding_adapter=self.embedding_adapter)
        self.grounding_engine = GroundingEngine()
        self.vision_analyzer = vision_analyzer or LocalVisionAnalyzer()

    def ingest_document(self, file_path_or_bytes: Any, filename: str, document_id: str = "DOC-001") -> Dict[str, Any]:
        parsed_pages = self.parser.parse(file_path_or_bytes, filename, document_id)
        chunks = self.chunker.chunk_pages(parsed_pages, filename, document_id)
        chunk_texts = [c.text for c in chunks]
        embeddings = self.embedding_adapter.embed_texts(chunk_texts)
        self.vector_store.add_chunks(chunks, embeddings)

        return {
            "document_id": document_id,
            "filename": filename,
            "page_count": len(parsed_pages),
            "chunk_count": len(chunks),
            "status": "indexed_locally"
        }

    def query_knowledge(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        retrieval_res: RetrievalResult = self.retriever.retrieve(query, top_k=top_k)
        grounding_status, citations = self.grounding_engine.evaluate_grounding(retrieval_res)
        retrieval_res.grounding_status = grounding_status
        formatted_context = self.grounding_engine.format_source_preserving_context(retrieval_res)

        return {
            "query": query,
            "grounding_status": grounding_status,
            "has_evidence": retrieval_res.has_evidence,
            "citations": citations,
            "sources": [s.to_dict() for s in retrieval_res.sources],
            "formatted_context": formatted_context
        }

    def process_multimodal_demo(
        self,
        inspection_report_pdf: Any,
        inspection_photo_jpg: Any,
        maintenance_sop_pdf: Any
    ) -> Dict[str, Any]:
        ingest_res_sop = self.ingest_document(maintenance_sop_pdf, "maintenance_sop.pdf", "DOC-SOP-001")
        ingest_res_report = self.ingest_document(inspection_report_pdf, "inspection_report.pdf", "DOC-REP-001")

        image_analysis = self.vision_analyzer.analyze_image(
            inspection_photo_jpg,
            instruction="Identify visual abnormalities, component state, and compliance with SOP."
        )

        rag_evidence = self.query_knowledge(
            query="What are the required maintenance steps and safety SOP for inspection?",
            top_k=5
        )

        return {
            "ingested_sop": ingest_res_sop,
            "ingested_report": ingest_res_report,
            "image_observations": image_analysis.to_dict(),
            "rag_evidence": rag_evidence,
            "agent_context": {
                "text_evidence": rag_evidence["formatted_context"],
                "image_observations": image_analysis.observations,
                "visual_abnormalities": image_analysis.visible_abnormalities,
                "confidence": image_analysis.confidence,
                "uncertainties": image_analysis.uncertainties,
                "citations": rag_evidence["citations"]
            }
        }
