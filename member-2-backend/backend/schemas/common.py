"""
Common schemas and error envelopes.
"""

from typing import Generic, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class ErrorDetail(BaseModel):
    code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Safe human-readable error message")
    request_id: str = Field(..., description="Request correlation identifier")


class ErrorEnvelope(BaseModel):
    error: ErrorDetail
