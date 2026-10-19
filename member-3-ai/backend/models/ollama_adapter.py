"""Local Ollama Model Adapter.

Conforms strictly to MASTER/05_MODEL_CONTRACT.md.
Connects strictly to local Ollama instance (127.0.0.1/localhost only).
Prohibits remote host endpoints.
"""

import time
from typing import Any, Dict, Iterator, List, Optional
import httpx

from .base import ModelAdapter
from .schemas import HealthStatus, ModelMessage, ModelRequest, ModelResponse


class OllamaAdapter(ModelAdapter):
    """Adapter for interacting with local Ollama runtime."""

    def __init__(
        self,
        model_id: str,
        base_url: str = "http://127.0.0.1:11434",
        timeout_seconds: float = 60.0
    ):
        super().__init__(model_id)
        # Security validation: strictly ensure host is local
        self._validate_local_endpoint(base_url)
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def _validate_local_endpoint(self, url: str) -> None:
        """Enforce that base_url is strictly a local address."""
        allowed_hosts = ["http://127.0.0.1", "http://localhost", "http://0.0.0.0"]
        if not any(url.startswith(h) for h in allowed_hosts):
            raise ValueError(
                f"SOVEREIGNTY VIOLATION: Endpoint '{url}' is not a permitted local runtime. "
                "Only local endpoints (127.0.0.1 / localhost) are allowed."
            )

    def generate(self, request: ModelRequest) -> ModelResponse:
        """Call local Ollama /api/chat endpoint."""
        start_time = time.time()
        endpoint = f"{self.base_url}/api/chat"

        messages = []
        for msg in request.messages:
            m_dict: Dict[str, Any] = {"role": msg.role, "content": msg.content}
            if msg.images:
                m_dict["images"] = msg.images
            messages.append(m_dict)

        payload = {
            "model": request.model_id or self.model_id,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": request.temperature,
                "num_predict": request.max_tokens,
            }
        }

        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                resp = client.post(endpoint, json=payload)
                resp.raise_for_status()
                data = resp.json()

            latency_ms = int((time.time() - start_time) * 1000)
            content = data.get("message", {}).get("content", "")
            usage = {
                "prompt_eval_count": data.get("prompt_eval_count", 0),
                "eval_count": data.get("eval_count", 0),
            }

            return ModelResponse(
                content=content,
                model_id=self.model_id,
                usage=usage,
                finish_reason="stop" if data.get("done") else "length",
                latency_ms=latency_ms
            )
        except Exception as e:
            raise RuntimeError(
                f"Local Ollama inference failed for model '{self.model_id}': {e}. "
                f"Ensure local Ollama service is running on {self.base_url}."
            ) from e

    def stream(self, request: ModelRequest) -> Iterator[str]:
        """Stream chunks from local Ollama /api/chat endpoint."""
        endpoint = f"{self.base_url}/api/chat"

        messages = []
        for msg in request.messages:
            m_dict: Dict[str, Any] = {"role": msg.role, "content": msg.content}
            if msg.images:
                m_dict["images"] = msg.images
            messages.append(m_dict)

        payload = {
            "model": request.model_id or self.model_id,
            "messages": messages,
            "stream": True,
            "options": {
                "temperature": request.temperature,
                "num_predict": request.max_tokens,
            }
        }

        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                with client.stream("POST", endpoint, json=payload) as response:
                    response.raise_for_status()
                    for line in response.iter_lines():
                        if line:
                            import json
                            data = json.loads(line)
                            delta = data.get("message", {}).get("content", "")
                            if delta:
                                yield delta
        except Exception as e:
            raise RuntimeError(f"Local Ollama streaming failed: {e}") from e

    def health_check(self) -> HealthStatus:
        """Verify local Ollama service availability."""
        start_time = time.time()
        endpoint = f"{self.base_url}/api/version"
        try:
            with httpx.Client(timeout=3.0) as client:
                resp = client.get(endpoint)
                latency_ms = (time.time() - start_time) * 1000.0
                if resp.status_code == 200:
                    return HealthStatus(
                        healthy=True,
                        model_id=self.model_id,
                        backend="ollama_local",
                        latency_ms=round(latency_ms, 2)
                    )
                else:
                    return HealthStatus(
                        healthy=False,
                        model_id=self.model_id,
                        backend="ollama_local",
                        latency_ms=round(latency_ms, 2),
                        error=f"HTTP {resp.status_code}"
                    )
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000.0
            return HealthStatus(
                healthy=False,
                model_id=self.model_id,
                backend="ollama_local",
                latency_ms=round(latency_ms, 2),
                error=f"Connection refused / offline: {e}"
            )
