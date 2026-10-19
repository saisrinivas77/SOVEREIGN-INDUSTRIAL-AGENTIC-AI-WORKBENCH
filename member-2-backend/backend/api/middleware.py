"""
Middleware for request correlation, security tracing, and headers.
"""

import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class RequestCorrelationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        # Generate or retain incoming request correlation ID
        incoming_id = request.headers.get("X-Request-ID")
        if incoming_id and incoming_id.startswith("REQ-"):
            request_id = incoming_id
        else:
            request_id = f"REQ-{uuid.uuid4().hex[:8].upper()}"

        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
