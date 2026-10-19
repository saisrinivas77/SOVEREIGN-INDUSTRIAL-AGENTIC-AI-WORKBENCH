"""
Security status schemas conforming to MASTER/03_API_CONTRACTS.md and MASTER/09_SECURITY_SOVEREIGNTY.md.
"""

from typing import Literal
from pydantic import BaseModel, Field


class SecurityStatusResponse(BaseModel):
    network_mode: Literal["restricted", "isolated", "default_deny"] = Field(
        default="restricted",
        description="Active network isolation mode"
    )
    external_calls: int = Field(default=0, description="Count of external network calls attempted")
    external_ai_calls: int = Field(default=0, description="Count of external AI API calls attempted (must be 0)")
    blocked_attempts: int = Field(default=0, description="Count of security violations blocked")
    local_calls: int = Field(default=0, description="Count of local internal operations executed")
