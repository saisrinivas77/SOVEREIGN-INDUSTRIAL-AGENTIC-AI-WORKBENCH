# M1 FRONTEND FINAL
## FINAL CODING INSTRUCTION

M1 frontend prompt: read AGENTS + MASTER; own only member-1-platform/frontend; build Workbench, Documents, Tasks/Agent Trace, Artifacts, Security Center, Models; consume only /api/v1; typed client; no direct Ollama/ChromaDB/filesystem; render real backend state; test all task/security/artifact states; do not fake success.

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
