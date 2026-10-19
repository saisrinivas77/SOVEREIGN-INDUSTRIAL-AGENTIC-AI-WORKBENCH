"""Local Model Capability Registry for Sovereign Industrial AI Workbench.

Conforms strictly to MASTER/05_MODEL_CONTRACT.md and MASTER/09_SECURITY_SOVEREIGNTY.md.
Maintains available local models, capability declarations, and local health checks.
Strictly prohibits cloud models (OpenAI, Anthropic, Gemini, Copilot, Cohere, Voyage, etc.).

Primary Model Architecture:
1. Main Model (Reasoning/General/Planning): Qwen3 (configurable quantization/size: 3B/8B/14B/32B or Qwen2.5)
2. Vision Model (Multimodal/P&ID/Scanned docs): Qwen2.5-VL (3B/7B)
3. Coding Model (Sandboxed Code Generation): Qwen3-Coder (3B/8B/14B or Qwen2.5-Coder)
4. Embeddings (Local RAG Vector DB): Local only (nomic-embed-text, bge-m3, all-minilm-l6-v2)
"""

import os
from typing import Dict, List, Literal, Optional
from .base import ModelAdapter
from .schemas import CapabilityType, HealthStatus, ModelMetadata

# Forbidden remote patterns that must be rejected unconditionally
FORBIDDEN_MODEL_PATTERNS = [
    "gpt-", "openai", "claude", "anthropic", "gemini", "copilot",
    "huggingface.co", "api.together", "groq", "voyage", "cohere",
    "azure", "bedrock", "vertex", "text-embedding", "ada"
]

HardwareProfile = Literal["small", "medium", "large"]


class ModelRegistry:
    """Registry of approved local models and their capabilities."""

    def __init__(self, hardware_profile: Optional[HardwareProfile] = None):
        self._models: Dict[str, ModelMetadata] = {}
        self._adapters: Dict[str, ModelAdapter] = {}
        self._default_models: Dict[CapabilityType, str] = {}
        self._embedding_model: str = "nomic-embed-text"
        
        # Read profile from env or param (default: medium for venue workstations)
        env_profile = os.getenv("SOVEREIGN_HARDWARE_PROFILE", "medium").lower()
        active_profile: HardwareProfile = hardware_profile or (env_profile if env_profile in ["small", "medium", "large"] else "medium") # type: ignore
        
        self._initialize_default_registry(profile=active_profile)

    def _initialize_default_registry(self, profile: HardwareProfile = "medium") -> None:
        """Register approved sovereign local models with flexible sizing profiles."""
        
        # 1. Main Reasoning / Planning / General Models (Qwen3 / Qwen2.5 Family)
        self.register_model(
            metadata=ModelMetadata(
                model_id="qwen3:8b",
                capabilities=["reasoning"],
                context_limit=32768,
                vision_support=False,
                structured_output_support=True,
                available=True
            ),
            is_default_for=["reasoning"] if profile == "medium" else None
        )
        self.register_model(
            metadata=ModelMetadata(
                model_id="qwen3:3b",
                capabilities=["reasoning"],
                context_limit=32768,
                vision_support=False,
                structured_output_support=True,
                available=True
            ),
            is_default_for=["reasoning"] if profile == "small" else None
        )
        self.register_model(
            metadata=ModelMetadata(
                model_id="qwen3:14b",
                capabilities=["reasoning"],
                context_limit=32768,
                vision_support=False,
                structured_output_support=True,
                available=True
            ),
            is_default_for=["reasoning"] if profile == "large" else None
        )
        self.register_model(
            metadata=ModelMetadata(
                model_id="qwen2.5:7b",
                capabilities=["reasoning"],
                context_limit=32768,
                vision_support=False,
                structured_output_support=True,
                available=True
            ),
            is_default_for=["reasoning"]
        )
        self.register_model(
            metadata=ModelMetadata(
                model_id="qwen2.5:7b-instruct",
                capabilities=["reasoning"],
                context_limit=32768,
                vision_support=False,
                structured_output_support=True,
                available=True
            )
        )
        self.register_model(
            metadata=ModelMetadata(
                model_id="llama3.2-vision:11b",
                capabilities=["vision", "reasoning"],
                context_limit=16384,
                vision_support=True,
                structured_output_support=True,
                available=True
            )
        )

        # 2. Coding Models (Qwen3-Coder / Qwen2.5-Coder Family)
        self.register_model(
            metadata=ModelMetadata(
                model_id="qwen3-coder:8b",
                capabilities=["coding"],
                context_limit=32768,
                vision_support=False,
                structured_output_support=True,
                available=True
            ),
            is_default_for=["coding"] if profile == "medium" else None
        )
        self.register_model(
            metadata=ModelMetadata(
                model_id="qwen3-coder:3b",
                capabilities=["coding"],
                context_limit=32768,
                vision_support=False,
                structured_output_support=True,
                available=True
            ),
            is_default_for=["coding"] if profile == "small" else None
        )
        self.register_model(
            metadata=ModelMetadata(
                model_id="qwen3-coder:14b",
                capabilities=["coding"],
                context_limit=32768,
                vision_support=False,
                structured_output_support=True,
                available=True
            ),
            is_default_for=["coding"] if profile == "large" else None
        )
        self.register_model(
            metadata=ModelMetadata(
                model_id="qwen2.5-coder:7b",
                capabilities=["coding"],
                context_limit=32768,
                vision_support=False,
                structured_output_support=True,
                available=True
            )
        )

        # 3. Vision Models (Qwen2.5-VL Multimodal Family)
        self.register_model(
            metadata=ModelMetadata(
                model_id="qwen2.5-vl:7b",
                capabilities=["vision"],
                context_limit=8192,
                vision_support=True,
                structured_output_support=True,
                available=True
            ),
            is_default_for=["vision"] if profile in ["medium", "large"] else None
        )
        self.register_model(
            metadata=ModelMetadata(
                model_id="qwen2.5-vl:3b",
                capabilities=["vision"],
                context_limit=8192,
                vision_support=True,
                structured_output_support=True,
                available=True
            ),
            is_default_for=["vision"] if profile == "small" else None
        )
        self.register_model(
            metadata=ModelMetadata(
                model_id="llava:7b",
                capabilities=["vision"],
                context_limit=4096,
                vision_support=True,
                structured_output_support=True,
                available=True
            )
        )

        # 4. Fallback Reasoning Models
        self.register_model(
            metadata=ModelMetadata(
                model_id="mistral:7b-instruct",
                capabilities=["reasoning"],
                context_limit=8192,
                vision_support=False,
                structured_output_support=True,
                available=True
            )
        )

        # Environment variable overrides
        main_override = os.getenv("SOVEREIGN_MAIN_MODEL")
        if main_override and main_override in self._models:
            self._default_models["reasoning"] = main_override
        
        vision_override = os.getenv("SOVEREIGN_VISION_MODEL")
        if vision_override and vision_override in self._models:
            self._default_models["vision"] = vision_override

        coding_override = os.getenv("SOVEREIGN_CODING_MODEL")
        if coding_override and coding_override in self._models:
            self._default_models["coding"] = coding_override

        embed_override = os.getenv("SOVEREIGN_EMBED_MODEL")
        if embed_override:
            self.set_local_embedding_model(embed_override)

    def apply_hardware_profile(self, profile: HardwareProfile) -> None:
        """Dynamically switch default model sizes based on venue GPU capacity."""
        if profile == "small":
            self._default_models["reasoning"] = "qwen3:3b"
            self._default_models["coding"] = "qwen3-coder:3b"
            self._default_models["vision"] = "qwen2.5-vl:3b"
        elif profile == "large":
            self._default_models["reasoning"] = "qwen3:14b"
            self._default_models["coding"] = "qwen3-coder:14b"
            self._default_models["vision"] = "qwen2.5-vl:7b"
        else:  # medium
            self._default_models["reasoning"] = "qwen3:8b"
            self._default_models["coding"] = "qwen3-coder:8b"
            self._default_models["vision"] = "qwen2.5-vl:7b"

    def set_local_embedding_model(self, model_name: str) -> None:
        """Set the active local embedding model name, verifying no cloud embeddings."""
        name_lower = model_name.lower()
        for forbidden in FORBIDDEN_MODEL_PATTERNS:
            if forbidden in name_lower:
                raise ValueError(
                    f"SOVEREIGNTY VIOLATION: Cloud embedding model '{model_name}' is forbidden. "
                    "Only local embeddings (e.g. nomic-embed-text, bge-m3, all-minilm-l6-v2) are permitted."
                )
        self._embedding_model = model_name

    def get_local_embedding_model(self) -> str:
        """Get the declared local embedding model ID."""
        return self._embedding_model

    def register_model(
        self,
        metadata: ModelMetadata,
        adapter: Optional[ModelAdapter] = None,
        is_default_for: Optional[List[CapabilityType]] = None
    ) -> None:
        """Register a local model and validate that it is strictly sovereign."""
        # Security check: never allow cloud models
        model_lower = metadata.model_id.lower()
        for forbidden in FORBIDDEN_MODEL_PATTERNS:
            if forbidden in model_lower:
                raise ValueError(
                    f"SOVEREIGNTY VIOLATION: Remote/Cloud model '{metadata.model_id}' is forbidden."
                )

        self._models[metadata.model_id] = metadata
        if adapter:
            self._adapters[metadata.model_id] = adapter

        if is_default_for:
            for cap in is_default_for:
                self._default_models[cap] = metadata.model_id

    def set_adapter(self, model_id: str, adapter: ModelAdapter) -> None:
        """Attach an adapter instance to a registered model."""
        if model_id not in self._models:
            raise KeyError(f"Model '{model_id}' is not registered in ModelRegistry.")
        self._adapters[model_id] = adapter

    def get_adapter(self, model_id: str) -> ModelAdapter:
        """Get the adapter instance for a model."""
        if model_id not in self._adapters:
            raise KeyError(f"No adapter registered for model '{model_id}'.")
        return self._adapters[model_id]

    def get_metadata(self, model_id: str) -> Optional[ModelMetadata]:
        """Get metadata for a specific model."""
        return self._models.get(model_id)

    def list_models(self, capability: Optional[CapabilityType] = None) -> List[ModelMetadata]:
        """List registered local models, optionally filtered by capability."""
        if capability is None:
            return list(self._models.values())
        return [m for m in self._models.values() if capability in m.capabilities]

    def get_default_model_id(self, capability: CapabilityType) -> str:
        """Get the default model ID for a capability."""
        if capability in self._default_models:
            return self._default_models[capability]
        # Fallback to first available model with this capability
        candidates = self.list_models(capability)
        if candidates:
            return candidates[0].model_id
        raise ValueError(f"No local model available for capability '{capability}'.")

    def check_health(self, model_id: str) -> HealthStatus:
        """Perform health check on the specified model adapter."""
        adapter = self.get_adapter(model_id)
        status = adapter.health_check()
        if model_id in self._models:
            self._models[model_id].health = status
            self._models[model_id].available = status.healthy
        return status
