"""Deterministic Sovereign Local Model Adapter (Mock & Engine).

Conforms strictly to MASTER/05_MODEL_CONTRACT.md.
Used for offline execution, airgap verification, test suites, and deterministic testing
without requiring an external GPU/Ollama runtime.
"""

import json
import time
from typing import Any, Callable, Dict, Iterator, List, Optional
from .base import ModelAdapter
from .schemas import HealthStatus, ModelRequest, ModelResponse


class LocalAdapter(ModelAdapter):
    """Deterministic local engine adapter for bounded testing and local execution."""

    def __init__(
        self,
        model_id: str,
        response_generator: Optional[Callable[[ModelRequest], str]] = None,
        is_healthy: bool = True
    ):
        super().__init__(model_id)
        self.response_generator = response_generator
        self._is_healthy = is_healthy
        self.call_history: List[ModelRequest] = []

    def set_healthy(self, healthy: bool) -> None:
        """Dynamically toggle health status for failover testing."""
        self._is_healthy = healthy

    def generate(self, request: ModelRequest) -> ModelResponse:
        """Generate response deterministically based on input or custom generator."""
        if not self._is_healthy:
            raise RuntimeError(f"Local model '{self.model_id}' is offline/unhealthy.")

        self.call_history.append(request)
        start_time = time.time()

        if self.response_generator:
            content = self.response_generator(request)
        else:
            content = self._default_deterministic_response(request)

        latency_ms = int((time.time() - start_time) * 1000)
        return ModelResponse(
            content=content,
            model_id=self.model_id,
            usage={"prompt_tokens": 120, "completion_tokens": 80, "total_tokens": 200},
            finish_reason="stop",
            latency_ms=latency_ms
        )

    def stream(self, request: ModelRequest) -> Iterator[str]:
        """Stream chunks from deterministic response."""
        response = self.generate(request)
        words = response.content.split(" ")
        for word in words:
            yield word + " "

    def health_check(self) -> HealthStatus:
        """Return local health status."""
        return HealthStatus(
            healthy=self._is_healthy,
            model_id=self.model_id,
            backend="local_engine",
            latency_ms=0.5,
            error=None if self._is_healthy else "Model offline or disabled."
        )

    def _default_deterministic_response(self, request: ModelRequest) -> str:
        """Provide context-aware fallback response matching canonical schemas."""
        last_message = request.messages[-1].content if request.messages else ""
        last_lower = last_message.lower()

        # 1. Planner request -> return valid JSON matching AgentPlan schema
        if "agentplan" in last_lower or "planner" in last_lower:
            return json.dumps({
                "task_id": "TASK-001",
                "goal": "Execute requested local industrial task",
                "steps": [
                    {
                        "step_id": 1,
                        "action": "Read inspection report and extract findings",
                        "tool": "read_file",
                        "expected_output": "Inspection report findings text"
                    },
                    {
                        "step_id": 2,
                        "action": "Retrieve relevant SOP guidelines",
                        "tool": "search_knowledge",
                        "expected_output": "Relevant SOP maintenance sections"
                    },
                    {
                        "step_id": 3,
                        "action": "Analyze inspection photograph for defects",
                        "tool": "analyze_image",
                        "expected_output": "Visual defect classification"
                    },
                    {
                        "step_id": 4,
                        "action": "Create industrial approval note document",
                        "tool": "create_docx",
                        "expected_output": "Verified approval_note.docx artifact"
                    }
                ]
            }, indent=2)

        # 2. Python Code Generation request -> return sandboxed Python code
        if "coding" in last_lower or "python" in last_lower or "equipment_data.csv" in last_lower:
            return """```python
import pandas as pd

# Load equipment data
df = pd.read_csv('equipment_data.csv')
summary = {
    'total_equipment': len(df),
    'critical_count': int((df['status'] == 'CRITICAL').sum()) if 'status' in df.columns else 0,
    'avg_vibration': float(df['vibration_mm_s'].mean()) if 'vibration_mm_s' in df.columns else 0.0
}
print("ANALYSIS_COMPLETE:", summary)
```"""

        # 3. Vision Analysis request -> return structured visual observations
        if "vision" in last_lower or "image" in last_lower or "photo" in last_lower:
            return json.dumps({
                "component": "High-Pressure Flange Seal",
                "visual_condition": "Localized pitting corrosion and gasket degradation observed at 4 o'clock position",
                "defect_type": "corrosion",
                "severity": "HIGH",
                "confidence": 0.94
            }, indent=2)

        # 4. Default reasoning synthesis
        return json.dumps({
            "summary": "Industrial analysis completed successfully using verified local evidence.",
            "status": "completed",
            "findings": [
                "Inspection report indicates wall thickness reduction exceeding 15%.",
                "Maintenance SOP Section 4.2 mandates immediate gasket replacement and hydrostatic test.",
                "Visual evidence corroborates localized pitting corrosion."
            ]
        }, indent=2)
