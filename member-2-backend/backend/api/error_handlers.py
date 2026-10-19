"""
Global exception handlers enforcing the canonical error envelope from MASTER/03_API_CONTRACTS.md.
"""

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


def get_request_id(request: Request) -> str:
    return getattr(request.state, "request_id", "REQ-UNKNOWN")


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    request_id = get_request_id(request)
    code_map = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        405: "METHOD_NOT_ALLOWED",
        413: "PAYLOAD_TOO_LARGE",
        415: "UNSUPPORTED_MEDIA_TYPE",
        422: "VALIDATION_ERROR",
        500: "INTERNAL_SERVER_ERROR",
    }
    code = code_map.get(exc.status_code, "ERROR")
    message = str(exc.detail) if isinstance(exc.detail, str) else "An HTTP error occurred."

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "request_id": request_id,
            }
        },
        headers={"X-Request-ID": request_id},
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    request_id = get_request_id(request)
    # Build safe human-readable message from validation errors
    error_details = []
    for err in exc.errors():
        loc = " -> ".join(str(l) for l in err.get("loc", []))
        msg = err.get("msg", "Invalid value")
        error_details.append(f"{loc}: {msg}")
    
    clean_message = "; ".join(error_details) if error_details else "Invalid request payload."

    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": clean_message,
                "request_id": request_id,
            }
        },
        headers={"X-Request-ID": request_id},
    )


async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    request_id = get_request_id(request)
    msg = str(exc)
    
    # Check if this represents a 404 resource not found or 400 bad request
    if "not found" in msg.lower():
        status_code = 404
        code = "RESOURCE_NOT_FOUND"
    elif "forbidden" in msg.lower() or "traversal" in msg.lower() or "absolute" in msg.lower():
        status_code = 400
        code = "SECURITY_VIOLATION"
    elif "exceeds maximum" in msg.lower():
        status_code = 413
        code = "FILE_TOO_LARGE"
    elif "disallowed" in msg.lower():
        status_code = 400
        code = "INVALID_FILE_TYPE"
    else:
        status_code = 400
        code = "BAD_REQUEST"

    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": msg,
                "request_id": request_id,
            }
        },
        headers={"X-Request-ID": request_id},
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    request_id = get_request_id(request)
    # Never expose internal traceback or host paths
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An internal server error occurred. All operations remain strictly local.",
                "request_id": request_id,
            }
        },
        headers={"X-Request-ID": request_id},
    )
