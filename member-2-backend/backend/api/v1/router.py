"""
Aggregate v1 router for SIH26117 Sovereign AI Workbench.
"""

from fastapi import APIRouter
from backend.api.v1.tasks import router as tasks_router
from backend.api.v1.files import router as files_router
from backend.api.v1.knowledge import router as knowledge_router
from backend.api.v1.models import router as models_router
from backend.api.v1.health import router as health_router
from backend.api.v1.security import router as security_router
from backend.api.v1.audit import router as audit_router
from backend.api.v1.dashboard import router as dashboard_router
from backend.api.v1.documents import router as documents_router
from backend.api.v1.artifacts import router as artifacts_router
from backend.api.v1.reports import router as reports_router

api_v1_router = APIRouter()

api_v1_router.include_router(tasks_router)
api_v1_router.include_router(files_router)
api_v1_router.include_router(knowledge_router)
api_v1_router.include_router(models_router)
api_v1_router.include_router(health_router)
api_v1_router.include_router(security_router)
api_v1_router.include_router(audit_router)
api_v1_router.include_router(dashboard_router)
api_v1_router.include_router(documents_router)
api_v1_router.include_router(artifacts_router)
api_v1_router.include_router(reports_router)


