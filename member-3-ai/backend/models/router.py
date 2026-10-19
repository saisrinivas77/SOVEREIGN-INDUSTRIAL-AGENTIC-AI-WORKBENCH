"""Model Router for Sovereign Industrial AI Workbench.

Conforms strictly to MASTER/05_MODEL_CONTRACT.md and MASTER/09_SECURITY_SOVEREIGNTY.md.
Implements deterministic capability selection, local model dispatch, local fallback,
and zero cloud egress enforcement.
"""

from typing import Any, Dict, List, Optional
from .base import ModelAdapter
from .registry import ModelRegistry
from .schemas import (
    CapabilityType,
    ModelRequest,
    ModelResponse,
    ModelSelection,
    Task,
    TaskType,
)

# Deterministic keyword and extension rules
VISION_INDICATORS = [
    "image", "photo", "p&id", "pid", "schematic", "visual", "picture", "diagram",
    "inspect photo", "gauge", "defect", "corrosion photo", "thermal image",
    ".jpg", ".jpeg", ".png", ".tiff", ".bmp", ".webp"
]

CODING_INDICATORS = [
    "code", "python", "script", "csv", "data analysis", "sandbox", "dataframe",
    "pandas", "numpy", "plot", "chart", "calculate statistics", "tabular data",
    ".py", ".csv", ".tsv", ".json", ".sql"
]

DOCUMENT_INDICATORS = [
    "report", "sop", "document", "approval", "maintenance", "inspection report",
    "standard operating procedure", "draft approval", "synthesize", "memo",
    ".pdf", ".docx", ".doc", ".txt", ".md"
]


class ModelRouter:
    """Deterministic Model Router that maps task requirements to sovereign local models."""

    def __init__(self, registry: Optional[ModelRegistry] = None):
        self.registry = registry or ModelRegistry()

    def determine_capability(
        self,
        instruction: str,
        file_ids: Optional[List[str]] = None,
        task_type: Optional[TaskType] = None
    ) -> tuple[CapabilityType, TaskType, str]:
        """Determine required capability and task type using deterministic policy."""
        inst_lower = (instruction or "").lower()
        files = [f.lower() for f in (file_ids or [])]
        combined = inst_lower + " " + " ".join(files)

        # 1. Vision Capability Check
        if any(ind in combined for ind in VISION_INDICATORS) or task_type == "vision":
            return "vision", "vision", "Task requires visual inspection / image analysis capability."

        # 2. Coding Capability Check
        if any(ind in combined for ind in CODING_INDICATORS) or task_type == "coding":
            return "coding", "coding", "Task requires Python coding / sandboxed data analysis capability."

        # 3. Document / Reasoning Capability Check
        if any(ind in combined for ind in DOCUMENT_INDICATORS) or task_type == "document":
            return "reasoning", "document", "Task requires industrial document analysis / evidence reasoning."

        # 4. General fallback
        return "reasoning", "general", "Task requires general local reasoning capability."

    def select_model(
        self,
        task: Optional[Task] = None,
        instruction: Optional[str] = None,
        file_ids: Optional[List[str]] = None,
        task_type: Optional[TaskType] = None,
        required_capability: Optional[CapabilityType] = None
    ) -> ModelSelection:
        """Produce canonical ModelSelection matching requirements to locally available models."""
        inst = task.instruction if task else (instruction or "")
        f_ids = task.file_ids if task else (file_ids or [])
        t_type = task.task_type if task else task_type

        if required_capability:
            cap = required_capability
            t_type = t_type or "general"
            reason = f"Explicitly requested capability '{cap}'."
        else:
            cap, t_type, reason = self.determine_capability(inst, f_ids, t_type)

        # Find primary default model for this capability if registered
        default_model_id = None
        try:
            default_model_id = self.registry.get_default_model_id(cap)
        except Exception:
            pass

        # Retrieve available models for this capability
        candidates = self.registry.list_models(cap)
        available_candidates = [m for m in candidates if m.available]

        if not available_candidates:
            # Check for approved local fallback: if vision or coding model is down,
            # check if general reasoning model can provide fallback or fail explicitly
            fallback_candidates = [m for m in self.registry.list_models("reasoning") if m.available]
            if cap != "vision" and fallback_candidates:
                selected_meta = fallback_candidates[0]
                reason += f" (Primary '{cap}' model unavailable; routed to approved local fallback '{selected_meta.model_id}')"
            else:
                raise RuntimeError(
                    f"LOCAL INFERENCE UNAVAILABLE: No local model available for capability '{cap}'. "
                    f"Cloud fallback is strictly forbidden by MASTER/05 and MASTER/09."
                )
        else:
            selected_meta = available_candidates[0]
            if default_model_id and selected_meta.model_id != default_model_id:
                reason += f" (Primary default model '{default_model_id}' unavailable; routed to approved local alternative/fallback '{selected_meta.model_id}')"

        return ModelSelection(
            task_type=t_type,
            capability=cap,
            model_id=selected_meta.model_id,
            reason=reason,
            confidence=0.95
        )

    def route_and_generate(
        self,
        request: ModelRequest,
        required_capability: CapabilityType = "reasoning"
    ) -> ModelResponse:
        """Route request to the appropriate local adapter and execute generation."""
        selection = self.select_model(required_capability=required_capability)
        adapter = self.registry.get_adapter(selection.model_id)
        return adapter.generate(request)

    def get_adapter_for_capability(self, capability: CapabilityType) -> ModelAdapter:
        """Retrieve the active ModelAdapter for a required capability."""
        selection = self.select_model(required_capability=capability)
        return self.registry.get_adapter(selection.model_id)
