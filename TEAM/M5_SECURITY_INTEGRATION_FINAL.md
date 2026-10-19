# M5 SECURITY INTEGRATION FINAL
## FINAL CODING INSTRUCTION

M5 security/integration prompt: read AGENTS + MASTER; own security/tools/sandbox/infra/docker; implement ToolRegistry, path validation, sandbox with no network/restricted FS/timeout/non-root, default-deny/restricted egress, audit and network evidence, security status, Docker/local runtime; integrate in staged order; never weaken security; final owner of integration and E2E.

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
