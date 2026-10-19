# MODEL CONTRACT v2

## Goal
Make the agent model-agnostic.

## Approved local runtime
Ollama or another explicitly approved local runtime.

## Capability registry
Each model declares:
- model_id
- capabilities
- context_limit
- vision_support
- structured_output_support
- available
- health

## Common interface
ModelAdapter:
- generate(request)
- structured_generate(request, schema)
- stream(request)
- health_check()

## Router input
{
  "task_type":"document|coding|vision|general",
  "required_capabilities":["reasoning"],
  "complexity":"low|medium|high"
}

## Router output
ModelSelection schema.

## Deterministic routing policy
1. If task contains image/P&ID/photo/visual analysis → vision capability.
2. If task contains code/python/script/CSV analysis → coding capability.
3. If task contains report/SOP/document/approval/reasoning → reasoning capability.
4. Otherwise → general/reasoning capability.
5. Select only locally available models.
6. Never route externally.

The router may later use an LLM classifier, but the final selected model must still pass capability and availability checks.

## Prompt independence
Business logic must not parse free-form model prose.
Prefer structured JSON outputs validated against schemas.

## Failure
Unavailable model → approved local fallback → structured failure.
Never cloud fallback.
