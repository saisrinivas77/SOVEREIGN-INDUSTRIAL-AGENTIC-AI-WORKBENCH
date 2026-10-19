# TEAM AI CODING AGENTS

Each member receives:
- AGENTS.md
- the full MASTER/ directory
- exactly one member prompt

## Frozen integration boundaries
Frontend ↔ API
API ↔ Agent Service
Agent ↔ ModelRouter
Agent ↔ ToolRegistry
RAG ↔ local store
Tools ↔ local services
Security ↔ all sensitive execution/network boundaries

## Golden workflow
Inspection PDF + image + SOP
→ OCR
→ deterministic classification/routing
→ agent plan
→ local RAG
→ local vision
→ local reasoning
→ DOCX
→ verification
→ audit
→ sovereignty evidence

## Parallel-work rule
No member changes another member's implementation. If a contract is insufficient, create a change request.
