"""
Health endpoint conforming to MASTER/03_API_CONTRACTS.md.
"""

from fastapi import APIRouter
from backend.services.health_service import health_service
from backend.schemas.health import HealthResponse

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("", response_model=HealthResponse, status_code=200)
async def get_health() -> HealthResponse:
    """
    Returns safe health status of all workbench subsystems.
    """
    return health_service.check_health()
