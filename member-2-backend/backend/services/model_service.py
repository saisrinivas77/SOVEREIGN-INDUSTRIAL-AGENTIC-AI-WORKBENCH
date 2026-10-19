"""
Model service interface conforming to MASTER/05_MODEL_CONTRACT.md.
Provides local model capability registry and deterministic router delegation.
"""

from .audit_service import audit_service
from .security_service import security_service
from ..schemas.model import ModelInfo, ModelListResponse, ModelSelection
from ..schemas.task import TaskType


class ModelService:
    def __init__(self, audit=audit_service, security=security_service):
        self.audit = audit
        self.security = security
        self._default_models: list[ModelInfo] = [
            ModelInfo(
                model_id="qwen2.5:7b",
                capabilities=["reasoning", "general"],
                context_limit=32768,
                vision_support=False,
                structured_output_support=True,
                available=True,
                health="ready",
            ),
            ModelInfo(
                model_id="qwen2.5-coder:7b",
                capabilities=["coding", "general"],
                context_limit=32768,
                vision_support=False,
                structured_output_support=True,
                available=True,
                health="ready",
            ),
            ModelInfo(
                model_id="llama3.2-vision:11b",
                capabilities=["vision", "reasoning", "general"],
                context_limit=16384,
                vision_support=True,
                structured_output_support=True,
                available=True,
                health="ready",
            ),
            ModelInfo(
                model_id="qwen2-vl:7b",
                capabilities=["vision", "general"],
                context_limit=16384,
                vision_support=True,
                structured_output_support=True,
                available=True,
                health="ready",
            ),
        ]



    def list_models(self) -> ModelListResponse:
        self.security.record_local_call("model_service")
        ollama_models: set[str] = set()
        try:
            import httpx
            resp = httpx.get("http://127.0.0.1:11434/api/tags", timeout=1.5)
            if resp.status_code == 200:
                data = resp.json()
                for m in data.get("models", []):
                    name = m.get("name", "")
                    if name:
                        ollama_models.add(name.lower())
        except Exception:
            pass

        result_models: list[ModelInfo] = []
        for m in self._default_models:
            model_copy = m.model_copy()
            if ollama_models:
                is_present = any(
                    m.model_id.lower() in om or om.startswith(m.model_id.lower())
                    for om in ollama_models
                )
                model_copy.available = True
                model_copy.health = "active (ollama_local)" if is_present else "ready"
            else:
                model_copy.available = True
                model_copy.health = "ready"
            result_models.append(model_copy)

        return ModelListResponse(models=result_models)


    def route_task(self, instruction: str, task_type: TaskType | None = None) -> ModelSelection:
        """
        Deterministic model routing policy conforming to MASTER/05_MODEL_CONTRACT.md.
        """
        self.security.record_local_call("model_service")
        lower = instruction.lower()

        # 1. Vision
        if any(term in lower for term in ["image", "photo", "p&id", "diagram", "visual", "picture", "schematic"]):
            selected = ModelSelection(
                task_type="vision",
                capability="vision",
                model_id="llama3.2-vision:11b",
                reason="Task requires visual inspection / image comprehension",
                confidence=0.95,
            )
        # 2. Coding / Data Analysis
        elif any(term in lower for term in ["code", "python", "script", "csv", "data analysis", "calculate", "pandas", "xlsx", "dataframe"]):
            selected = ModelSelection(
                task_type="coding",
                capability="coding",
                model_id="qwen2.5-coder:7b",
                reason="Task requires executable Python generation / data transformation",
                confidence=0.95,
            )
        # 3. Document / Reasoning / SOP
        elif any(term in lower for term in ["report", "sop", "document", "approval", "reasoning", "compliance", "policy", "maintenance"]):
            selected = ModelSelection(
                task_type="document",
                capability="reasoning",
                model_id="qwen2.5:7b",
                reason="Task requires multi-step industrial document analysis and reasoning",
                confidence=0.92,
            )
        # 4. General fallback
        else:
            selected = ModelSelection(
                task_type=task_type or "general",
                capability="reasoning",
                model_id="qwen2.5:7b",
                reason="Default deterministic routing to local general reasoning model",
                confidence=0.85,
            )

        self.audit.log_event(
            event_type="model_call",
            actor="system",
            component="model_service",
            status="success",
            metadata={
                "selected_model": selected.model_id,
                "capability": selected.capability,
                "task_type": selected.task_type,
                "confidence": selected.confidence,
            },
        )

        return selected


model_service = ModelService()
