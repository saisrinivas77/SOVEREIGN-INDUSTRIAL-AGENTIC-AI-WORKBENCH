"""
Audit trail endpoint conforming to MASTER/03_API_CONTRACTS.md.
"""

from fastapi import APIRouter
from backend.services.audit_service import audit_service
from backend.schemas.audit import AuditResponse

router = APIRouter(prefix="/audit", tags=["Audit"])


@router.get("/tasks/{task_id}", response_model=AuditResponse, status_code=200)
async def get_task_audit_trail(task_id: str) -> AuditResponse:
    """
    Returns complete chronological audit events for a specific task.
    """
    return audit_service.get_task_events(task_id=task_id)