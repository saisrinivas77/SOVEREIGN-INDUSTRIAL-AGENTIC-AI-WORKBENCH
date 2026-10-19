# M3 AI FINAL
## FINAL CODING INSTRUCTION

M3 agent/model prompt: read AGENTS + MASTER; own only member-3-ai agent/model/prompt folders; implement LangGraph INTAKE→CLASSIFY→PLAN→ROUTE→EXECUTE→OBSERVE→VERIFY; deterministic routing first; ModelRouter→Adapter→local runtime; canonical structured outputs; MAX_STEPS=12, retries=2; registered tools only; no host shell, secrets, internet; golden inspection and CSV workflows; test malformed output and bounds.

### Mandatory procedure
1. Read `/AGENTS.md`.
2. Read every relevant `/MASTER/*.md`.
3. Inspect existing implementation before editing.
4. Work only inside your ownership directory.
5. Use canonical API/data/model/tool contracts exactly.
6. Do not create alternate schemas or duplicate services.
7. Do not add external AI, telemetry, storage, embeddings, OCR or vision.
8. Add tests for critical boundaries.
9. Run tests before reporting completion.
10. Report files changed, contracts consumed, tests, dependencies and blockers.

### Conflict rule
If a task conflicts with MASTER, stop. Name the exact file/section and request a contract change. Never improvise.

### Integration rule
Other members may implement different internals, but their modules must communicate only through the canonical contracts. Do not modify another member's code to make your module fit.
