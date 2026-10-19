"""
Security status endpoint conforming to MASTER/03_API_CONTRACTS.md and MASTER/09_SECURITY_SOVEREIGNTY.md.
"""

from fastapi import APIRouter
from backend.services.security_service import security_service
from backend.schemas.security import SecurityStatusResponse

router = APIRouter(prefix="/security", tags=["Security"])


@router.get("/status", response_model=SecurityStatusResponse, status_code=200)
async def get_security_status() -> SecurityStatusResponse:
    """
    Returns observable evidence of sovereign boundary enforcement and network restrictions.
    """
    return security_service.get_security_status()


@router.get("/telemetry", status_code=200)
async def get_security_telemetry():
    """
    Returns live sovereign telemetry breakdown.
    """
    status = security_service.get_security_status()
    from backend.services.database import db
    tasks = db.list_all_tasks()
    model_calls = sum(len(t.get("steps", [])) for t in tasks)
    tool_calls = sum(1 for t in tasks for s in t.get("steps", []) if s.get("tool"))
    rag_calls = sum(1 for t in tasks for s in t.get("steps", []) if s.get("tool") == "search_knowledge")
    
    return {
        "network_mode": status.network_mode.upper(),
        "external_ai_calls": status.external_ai_calls,
        "external_calls": status.external_calls,
        "blocked_attempts": status.blocked_attempts,
        "local_model_calls": model_calls,
        "local_tool_calls": tool_calls,
        "local_rag_calls": rag_calls,
    }


@router.get("/events", status_code=200)
async def get_security_events():
    """
    Returns audit events log.
    """
    from backend.services.database import db
    return {"events": db.list_all_audit_events()}

