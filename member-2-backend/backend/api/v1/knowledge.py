"""
Knowledge indexing and search endpoints conforming to MASTER/03_API_CONTRACTS.md.
"""

from fastapi import APIRouter
from backend.services.knowledge_service import knowledge_service
from backend.schemas.knowledge import IndexRequest, IndexResponse, SearchRequest, SearchResponse

router = APIRouter(prefix="/knowledge", tags=["Knowledge"])


@router.post("/index", response_model=IndexResponse, status_code=200)
async def index_knowledge(payload: IndexRequest) -> IndexResponse:
    """
    Indexes a local file into the vector store.
    """
    return knowledge_service.index_document(file_id=payload.file_id)


@router.post("/search", response_model=SearchResponse, status_code=200)
async def search_knowledge(payload: SearchRequest) -> SearchResponse:
    """
    Searches local indexed knowledge and returns sources with page/section citations.
    """
    return knowledge_service.search(query=payload.query, top_k=payload.top_k)


@router.get("/search", response_model=SearchResponse, status_code=200)
async def search_knowledge_get(q: str = "") -> SearchResponse:
    """
    Searches local indexed knowledge via GET query param.
    """
    return knowledge_service.search(query=q, top_k=5)

