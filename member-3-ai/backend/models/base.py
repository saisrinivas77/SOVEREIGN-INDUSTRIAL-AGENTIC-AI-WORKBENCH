"""Base ModelAdapter Abstract Interface.

Conforms strictly to MASTER/05_MODEL_CONTRACT.md.
Every model adapter must implement generate, structured_generate, stream, and health_check.
"""

from abc import ABC, abstractmethod
import json
import re
from typing import Any, Dict, Iterator, Optional, Type, TypeVar
from pydantic import BaseModel, ValidationError

from .schemas import HealthStatus, ModelMessage, ModelRequest, ModelResponse

T = TypeVar("T", bound=BaseModel)


def extract_json_payload(raw_text: str) -> str:
    """Extract clean JSON substring from model output containing markdown or reasoning.
    
    Prevents fragile parsing while handling markdown code fences.
    """
    text = raw_text.strip()
    
    # 1. Match ```json ... ``` or ``` ... ``` code blocks
    json_block = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
    if json_block:
        candidate = json_block.group(1).strip()
        if (candidate.startswith("{") and candidate.endswith("}")) or (candidate.startswith("[") and candidate.endswith("]")):
            return candidate

    # 2. Match outermost JSON object { ... }
    brace_start = text.find("{")
    brace_end = text.rfind("}")
    if brace_start != -1 and brace_end != -1 and brace_end > brace_start:
        return text[brace_start : brace_end + 1]

    # 3. Match outermost JSON array [ ... ]
    bracket_start = text.find("[")
    bracket_end = text.rfind("]")
    if bracket_start != -1 and bracket_end != -1 and bracket_end > bracket_start:
        return text[bracket_start : bracket_end + 1]

    return text


class ModelAdapter(ABC):
    """Abstract Base Class for all Local Model Adapters."""

    def __init__(self, model_id: str):
        self.model_id = model_id

    @abstractmethod
    def generate(self, request: ModelRequest) -> ModelResponse:
        """Generate a complete text completion from the local model."""
        pass

    @abstractmethod
    def stream(self, request: ModelRequest) -> Iterator[str]:
        """Stream token chunks from the local model."""
        pass

    @abstractmethod
    def health_check(self) -> HealthStatus:
        """Perform a local health check to verify availability and latency."""
        pass

    def structured_generate(self, request: ModelRequest, schema: Type[T]) -> tuple[T, ModelResponse]:
        """Generate structured output and validate against a Pydantic schema.
        
        Extracts JSON safely and validates using Pydantic, avoiding fragile text heuristics.
        """
        # Append schema instruction to system prompt or user message
        schema_json = json.dumps(schema.model_json_schema(), indent=2)
        instruction = f"\nYou must respond with a single valid JSON object strictly matching this schema:\n{schema_json}\nReturn ONLY JSON."
        
        modified_req = request.model_copy(deep=True)
        if modified_req.messages:
            last_msg = modified_req.messages[-1]
            modified_req.messages[-1] = ModelMessage(
                role=last_msg.role,
                content=f"{last_msg.content}\n\n{instruction}",
                images=last_msg.images
            )
        else:
            modified_req.messages.append(ModelMessage(role="user", content=instruction))

        response = self.generate(modified_req)
        json_str = extract_json_payload(response.content)

        try:
            parsed_dict = json.loads(json_str)
            validated = schema.model_validate(parsed_dict)
            return validated, response
        except (json.JSONDecodeError, ValidationError) as e:
            # Bounded retry with explicit repair request
            repair_req = ModelRequest(
                model_id=self.model_id,
                messages=[
                    *request.messages,
                    ModelMessage(role="assistant", content=response.content),
                    ModelMessage(role="user", content=f"The response was not valid JSON matching the schema ({str(e)}). Fix it and return ONLY the corrected JSON object.")
                ],
                temperature=0.0
            )
            repair_resp = self.generate(repair_req)
            repaired_json_str = extract_json_payload(repair_resp.content)
            try:
                repaired_dict = json.loads(repaired_json_str)
                validated = schema.model_validate(repaired_dict)
                return validated, repair_resp
            except Exception as final_err:
                raise ValueError(
                    f"Failed to generate structured output for schema '{schema.__name__}'. "
                    f"Parse error: {final_err}. Raw model response: {response.content[:200]}"
                ) from final_err
