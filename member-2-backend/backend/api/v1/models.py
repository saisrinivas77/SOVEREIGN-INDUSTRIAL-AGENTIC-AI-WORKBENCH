"""
Model registry endpoint conforming to MASTER/03_API_CONTRACTS.md.
"""

from fastapi import APIRouter
from backend.services.model_service import model_service
from backend.schemas.model import ModelListResponse

router = APIRouter(prefix="/models", tags=["Models"])


@router.get("", response_model=ModelListResponse, status_code=200)
async def get_models() -> ModelListResponse:
    """
    Returns available local models and their capabilities.
    """
    return model_service.list_models()


@router.get("/routing/{task_id}", status_code=200)
async def get_model_routing(task_id: str):
    """
    Returns model routing decision for a given task.
    """
    from backend.services.database import db
    task = db.get_task(task_id)
    if not task:
        raise ValueError(f"Task '{task_id}' not found.")
    selection = model_service.route_task(task["instruction"])
    return selection.model_dump()

