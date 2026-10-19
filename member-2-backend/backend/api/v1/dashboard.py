"""
Dashboard metrics endpoint for Sovereign AI Workbench.
"""

from fastapi import APIRouter
from backend.services.database import db
from backend.services.model_service import model_service
from backend.services.security_service import security_service

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/metrics", status_code=200)
async def get_dashboard_metrics():
    tasks = db.list_all_tasks()
    active_tasks = sum(1 for t in tasks if t["status"] in ("queued", "running"))
    completed_tasks = sum(1 for t in tasks if t["status"] == "completed")
    failed_tasks = sum(1 for t in tasks if t["status"] == "failed")
    
    docs = db.list_all_documents()
    models = model_service.list_models()
    artifacts = db.list_all_artifacts()
    events = db.list_all_audit_events()
    sec = security_service.get_security_status()

    return {
        "active_tasks": active_tasks,
        "completed_tasks": completed_tasks,
        "failed_tasks": failed_tasks,
        "indexed_documents": len(docs),
        "available_models": len(models.models),
        "generated_artifacts": len(artifacts),
        "security_events": len(events),
        "external_calls": sec.external_calls,
        "blocked_calls": sec.blocked_attempts,
    }
