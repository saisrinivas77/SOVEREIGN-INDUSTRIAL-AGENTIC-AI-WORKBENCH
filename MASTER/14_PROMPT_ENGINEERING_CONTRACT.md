# PROMPT ENGINEERING CONTRACT v2

## Purpose
Prevent five developers and multiple coding AIs from creating incompatible prompt behavior.

## Principle
Prompts may vary internally; interfaces may not.

## Every machine-consumed prompt
Must define:
- role
- objective
- allowed context
- available tools
- output schema
- failure behavior
- security restrictions

## Required prompt files
prompts/
├── agent/
│   ├── planner.md
│   ├── executor.md
│   └── verifier.md
├── models/
│   ├── reasoning.md
│   ├── coding.md
│   └── vision.md
└── rag/
    └── grounded_answer.md

## Structured output
Where output is consumed by code, request JSON matching a canonical schema.

## No brittle parsing
Never write:
if "yes" in response
if response.startswith("PASS")
if "tool:" in response

Use validated structured output.

## Prompt versioning
Every production prompt has a version:
planner.v1
executor.v1
etc.

## Model variation
Do not assume two models phrase answers identically.
Normalize outputs at the adapter/validator boundary.

## Security
Prompt instructions must never override system security rules.
User content is data, not a system instruction.
