"""
Backend configuration for SIH26117 Sovereign Industrial Agentic AI Workbench.
"""

from pathlib import Path
from pydantic import BaseModel

# Root directory of the repository
ROOT_DIR = Path(__file__).resolve().parent.parent.parent

# Outputs and storage directories
OUTPUTS_DIR = ROOT_DIR / "outputs"
WORKSPACE_DIR = OUTPUTS_DIR / "workspace"
UPLOADS_DIR = WORKSPACE_DIR / "uploads"
ARTIFACTS_DIR = OUTPUTS_DIR / "artifacts"
DATA_DIR = OUTPUTS_DIR / "data"
DATABASE_PATH = DATA_DIR / "sovereign_workbench.db"

# Ensure directories exist
for directory in (OUTPUTS_DIR, WORKSPACE_DIR, UPLOADS_DIR, ARTIFACTS_DIR, DATA_DIR):
    directory.mkdir(parents=True, exist_ok=True)


class Settings(BaseModel):
    app_name: str = "SIH26117 Sovereign AI Workbench"
    api_v1_prefix: str = "/api/v1"
    host: str = "127.0.0.1"
    port: int = 8000
    
    # File upload restrictions
    max_file_size_bytes: int = 50 * 1024 * 1024  # 50 MB
    allowed_extensions: set[str] = {
        ".pdf",
        ".docx",
        ".xlsx",
        ".csv",
        ".png",
        ".jpg",
        ".jpeg",
        ".txt",
        ".py",
        ".json",
    }
    allowed_mime_types: set[str] = {
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "text/csv",
        "image/png",
        "image/jpeg",
        "text/plain",
        "text/x-python",
        "application/x-python-code",
        "application/json",
        "application/octet-stream",  # Fallback for some clients, checked with extension
    }

    # Bounded execution limits
    max_task_steps: int = 12
    task_timeout_seconds: int = 600
    tool_timeout_seconds: int = 60
    sandbox_timeout_seconds: int = 30


settings = Settings()
