# MODULE CONTRACTS v2

## Ownership map

M1 — Frontend/Product
Owns: frontend/**

M2 — Backend/API
Owns: backend/api/**, backend/services/**, backend/schemas/**

M3 — Agent/Models
Owns: backend/agents/**, backend/models/**, prompts/agent/**, prompts/models/**

M4 — RAG/Multimodal
Owns: backend/rag/**, backend/vision/**, backend/ocr/**, prompts/rag/**

M5 — Security/Integration
Owns: backend/security/**, backend/tools/**, sandbox/**, infra/**, docker/**,
shared integration configuration and final integration branch.

## Cross-module rule
A member may READ another module but may not modify it.
If an interface is missing, request a contract change rather than editing another module.

## Shared directories
MASTER/** is protected.
tests/contracts/** may be modified by the relevant owner with integration approval.
schemas are contract-controlled.

## Definition of done for every module
- implementation compiles/runs
- contract tests pass
- no forbidden dependency
- no unauthorized filesystem/network access
- errors are structured
- changes are documented in commit
