"""
Non-Anonymous Document Chunker for SIH26117 Member 4.
Generates fully metadata-bound Chunk objects with SHA-256 content hashes.
"""

import hashlib
import re
from typing import List

try:
    from backend.rag.schemas import Chunk
    from backend.rag.parser import ParsedPage
except ImportError:
    from .schemas import Chunk
    from .parser import ParsedPage

class DocumentChunker:
    """
    Chunks parsed pages into bounded text segments while preserving full document metadata.
    Guarantees every chunk has document_id, filename, page, section, source_type, and content_hash.
    """

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_pages(self, pages: List[ParsedPage], filename: str, document_id: str = "DOC-001") -> List[Chunk]:
        chunks: List[Chunk] = []
        global_chunk_idx = 1

        for page in pages:
            text = page.text.strip()
            if not text:
                continue

            paragraphs = [p.strip() for p in re.split(r'\n\s*\n', text) if p.strip()]
            if not paragraphs:
                paragraphs = [text]

            current_chunk_text = ""
            page_chunk_idx = 1

            for para in paragraphs:
                if len(current_chunk_text) + len(para) <= self.chunk_size:
                    current_chunk_text = (current_chunk_text + "\n\n" + para).strip()
                else:
                    if current_chunk_text:
                        chunk_obj = self._create_chunk(
                            document_id=document_id,
                            filename=filename,
                            page=page.page_num,
                            section=page.section,
                            chunk_index=global_chunk_idx,
                            source_type=page.source_type,
                            text=current_chunk_text
                        )
                        chunks.append(chunk_obj)
                        global_chunk_idx += 1
                        page_chunk_idx += 1
                    
                    current_chunk_text = para

            if current_chunk_text:
                chunk_obj = self._create_chunk(
                    document_id=document_id,
                    filename=filename,
                    page=page.page_num,
                    section=page.section,
                    chunk_index=global_chunk_idx,
                    source_type=page.source_type,
                    text=current_chunk_text
                )
                chunks.append(chunk_obj)
                global_chunk_idx += 1

        return chunks

    def _create_chunk(
        self,
        document_id: str,
        filename: str,
        page: int,
        section: str,
        chunk_index: int,
        source_type: str,
        text: str
    ) -> Chunk:
        content_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
        chunk_id = f"{document_id}_p{page}_c{chunk_index}"

        return Chunk(
            document_id=document_id,
            filename=filename,
            page=page,
            section=section,
            chunk_id=chunk_id,
            source_type=source_type,
            content_hash=content_hash,
            text=text
        )
