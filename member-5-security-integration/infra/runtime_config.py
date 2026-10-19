"""
Runtime Configuration for Sovereign AI Workbench.
Centralizes all directories, network policies, timeout bounds, and model endpoints.
"""

from pathlib import Path
import os
from typing import List, Set

class RuntimeConfig:
    # Base paths
    BASE_DIR: Path = Path(os.getenv("SOVEREIGN_BASE_DIR", Path(__cwd__ if "__cwd__" in dir() else os.getcwd()))).resolve()
    WORKSPACE_DIR: Path = BASE_DIR / "workspace"
    UPLOADS_DIR: Path = WORKSPACE_DIR / "uploads"
    SANDBOX_DIR: Path = WORKSPACE_DIR / "sandboxes"
    OUTPUTS_DIR: Path = BASE_DIR / "outputs"
    AUDIT_LOG_DIR: Path = BASE_DIR / "audit_logs"

    # Execution Bounds (Bounded Execution Policy)
    MAX_STEPS: int = int(os.getenv("MAX_STEPS", "12"))
    MAX_TOOL_RETRIES: int = int(os.getenv("MAX_TOOL_RETRIES", "2"))
    MAX_MODEL_RETRIES: int = int(os.getenv("MAX_MODEL_RETRIES", "2"))
    TASK_TIMEOUT_SECONDS: int = int(os.getenv("TASK_TIMEOUT_SECONDS", "600"))
    TOOL_TIMEOUT_SECONDS: int = int(os.getenv("TOOL_TIMEOUT_SECONDS", "60"))
    SANDBOX_TIMEOUT_SECONDS: int = int(os.getenv("SANDBOX_TIMEOUT_SECONDS", "30"))

    # Network Sovereignty Policy
    NETWORK_MODE: str = os.getenv("SOVEREIGN_NETWORK_MODE", "restricted")  # "restricted" | "isolated"
    ALLOW_EXTERNAL_NETWORK: bool = False  # NEVER True in sovereign mode

    # Approved Local Endpoints
    APPROVED_LOCAL_HOSTS: Set[str] = {
        "127.0.0.1",
        "localhost",
        "0.0.0.0",
        "::1",
        "host.docker.internal",
        "ollama",
        "chromadb",
        "backend",
        "frontend"
    }
    APPROVED_LOCAL_PORTS: Set[int] = {
        11434,  # Ollama
        8000,   # Backend API
        8001,   # ChromaDB / Vector DB
        3000,   # Next.js Frontend
        5000,   # Internal services
    }

    # Forbidden External AI Providers & Endpoints (Explicitly Blocked)
    FORBIDDEN_EXTERNAL_DOMAINS: Set[str] = {
        "api.openai.com",
        "api.anthropic.com",
        "generativelanguage.googleapis.com",
        "googleapis.com",
        "api-inference.huggingface.co",
        "huggingface.co",
        "api.cohere.ai",
        "api.mistral.ai",
        "api.together.xyz",
        "api.groq.com",
        "api.deepseek.com",
        "replicate.com"
    }

    @classmethod
    def ensure_directories(cls) -> None:
        """Ensure all required sovereign workspace directories exist."""
        cls.WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)
        cls.UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
        cls.SANDBOX_DIR.mkdir(parents=True, exist_ok=True)
        cls.OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
        cls.AUDIT_LOG_DIR.mkdir(parents=True, exist_ok=True)

# Auto-initialize directories on import
RuntimeConfig.ensure_directories()
