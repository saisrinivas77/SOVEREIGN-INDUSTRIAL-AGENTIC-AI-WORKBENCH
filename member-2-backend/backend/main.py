"""
Main FastAPI Application Entrypoint for SIH26117 Sovereign Industrial Agentic AI Workbench.
"""

import sys
from pathlib import Path

# Ensure package and workspace paths are initialized for direct script execution
_member_dir = str(Path(__file__).resolve().parent.parent)
if _member_dir not in sys.path:
    sys.path.insert(0, _member_dir)

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from backend.config import settings
from backend.api.v1.router import api_v1_router
from backend.api.middleware import RequestCorrelationMiddleware
from backend.api.error_handlers import (
    http_exception_handler,
    validation_exception_handler,
    value_error_handler,
    general_exception_handler,
)


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version="2.0.0",
        description="Canonical backend API for SIH26117 Sovereign Industrial Agentic AI Workbench",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Add request correlation middleware
    app.add_middleware(RequestCorrelationMiddleware)

    # Register global exception handlers for canonical error envelopes
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(ValueError, value_error_handler)
    app.add_exception_handler(Exception, general_exception_handler)

    # Mount canonical API v1 router
    app.include_router(api_v1_router, prefix=settings.api_v1_prefix)

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
    )
