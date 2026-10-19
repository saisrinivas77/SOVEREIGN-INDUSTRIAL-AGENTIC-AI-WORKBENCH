# M1 AI CODING PROMPT — FRONTEND / PRODUCT

Role: Senior Frontend Engineer.

Read AGENTS.md and MASTER contracts first.

Allowed:
- member-1-platform/frontend/**

Goal:
Build the Workbench UI around the fixed API contracts.

Required screens:
1. Chat/Task
2. Files
3. Agent timeline
4. Model routing trace
5. Artifacts
6. Security/Sovereignty center

Must display:
- task status
- agent steps
- selected model + reason
- RAG sources
- artifacts
- security counters

Do not implement backend business logic.
Do not call Ollama directly.
Use API contracts exactly.
Use mock adapters only until real endpoints exist, but keep interfaces identical.
